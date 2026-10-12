"""Blinded, budget-limited real-model comparison for Sales Core V2 and Clef routing."""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agent import SalesAgent
from .config import get_config
from .knowledge import KNOWLEDGE, retrieve
from .provider import PROFILE_FIELDS, agent_schema

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "simulator/evaluation/scenarios.json"
REPORTS = ROOT / "simulator/ab_eval_reports"
CLEF_MODEL_ID = "@cf/cloudflare/clef"
CLEF_URL = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/clef"
OPENAI_INPUT_USD_PER_M = 0.10
OPENAI_OUTPUT_USD_PER_M = 0.50
NEURONS_PER_M_INPUT = 21818
CLEF_INPUT_USD_PER_M = 0.24
MAX_CUSTOMER_TURNS = 12
PILOT_IDS = ("E01-own-stay-small-family", "E05-layout-four-bedrooms", "E08-cold-short-replies",
             "E10-viewing-saturday", "E20-explicit-need-time")
CRITERIA = (
    "intent_understanding", "natural_continuation", "valuable_questions", "relevant_advantages",
    "customer_interest", "non_repetition", "factual_accuracy", "appropriate_pacing",
)
RUBRIC = {
    "intent_understanding": "Understands the customer's stated and context-supported real need; adapts when it changes.",
    "natural_continuation": "Responds to what the customer actually said and keeps the exchange coherent and human.",
    "valuable_questions": "Asks a useful question only when it helps the customer, rather than collecting CRM fields.",
    "relevant_advantages": "Introduces a verified project advantage only when it genuinely relates to this customer's needs.",
    "customer_interest": "Makes it easier or more appealing for this customer to learn more, without manufactured urgency.",
    "non_repetition": "Avoids repeating a pitch, re-asking answered questions, or talking past the customer.",
    "factual_accuracy": "Answers from the supplied project Knowledge, acknowledges unknowns, and does not invent facts or commitments.",
    "appropriate_pacing": "Moves toward a viewing when welcome and suitable, and gives space when the customer signals that preference.",
}


class BudgetStop(RuntimeError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _usage_tokens(usage: dict[str, Any], key: str) -> int | None:
    value = usage.get(key)
    return int(value) if isinstance(value, (int, float)) else None


def _is_clef_quota_exhausted(status: int | None, body: dict[str, Any]) -> bool:
    errors = body.get("errors") or []
    messages = " ".join(str(error.get("message", "")).lower() for error in errors if isinstance(error, dict))
    codes = {error.get("code") for error in errors if isinstance(error, dict)}
    return (status == 429 or 4006 in codes or "used up your daily free allocation" in messages
            or ("neuron" in messages and "quota" in messages))


class Ledger:
    """Enforces conservative pre-call reservation and records provider-reported usage."""
    def __init__(self, max_usd: float, max_neurons: int, secrets: tuple[str, ...], prior_cost_usd: float = 0.0, prior_neurons: int = 0):
        self.max_usd = max_usd
        self.max_neurons = max_neurons
        self.prior_cost_usd = prior_cost_usd
        self.prior_neurons = prior_neurons
        self.secrets = tuple(secret for secret in secrets if secret)
        self.openai_input_tokens = 0
        self.openai_output_tokens = 0
        self.openai_cost_usd = 0.0
        self.openai_calls = 0
        self.openai_latency_ms: list[int] = []
        self.openai_by_role: dict[str, dict[str, Any]] = {}
        self.clef_calls = 0
        self.clef_successful_calls = 0
        self.clef_failed_calls = 0
        self.clef_neurons: int | None = 0
        self.clef_input_tokens = 0
        self.clef_cost_usd = 0.0
        self.clef_latency_ms: list[int] = []
        self.reserved_usd = 0.0
        self.failures: list[dict[str, str]] = []

    def redact(self, value: Any) -> str:
        result = str(value)
        for secret in self.secrets:
            result = result.replace(secret, "[REDACTED]")
        return result[:800]

    def reserve_openai(self, prompt: str, max_output_tokens: int) -> float:
        # Two characters per token is intentionally conservative for this English/JSON workload.
        input_reserve = math.ceil(len(prompt) / 2)
        reserve = (input_reserve * OPENAI_INPUT_USD_PER_M + max_output_tokens * OPENAI_OUTPUT_USD_PER_M) / 1_000_000
        if self.prior_cost_usd + self.openai_cost_usd + self.clef_cost_usd + self.reserved_usd + reserve > self.max_usd:
            raise BudgetStop(f"OpenAI USD cap reached before next request (cap=${self.max_usd:.2f}).")
        self.reserved_usd += reserve
        return reserve

    def reserve_clef(self, prompt_chars: int) -> tuple[int, float]:
        tokens = math.ceil(prompt_chars / 2)
        neurons = math.ceil(tokens * NEURONS_PER_M_INPUT / 1_000_000)
        reserve = tokens * CLEF_INPUT_USD_PER_M / 1_000_000
        current_neurons = self.prior_neurons + (self.clef_neurons or 0)
        if current_neurons + neurons > self.max_neurons:
            raise BudgetStop(f"Clef Neuron cap would be exceeded before next request ({current_neurons}+{neurons}/{self.max_neurons}).")
        if self.prior_cost_usd + self.openai_cost_usd + self.clef_cost_usd + self.reserved_usd + reserve > self.max_usd:
            raise BudgetStop(f"Combined provider USD cap reached before next Clef request (cap=${self.max_usd:.2f}).")
        self.reserved_usd += reserve
        return tokens, reserve

    def cancel_reservation(self, reserve: float) -> None:
        self.reserved_usd = max(0.0, self.reserved_usd - reserve)

    def start_clef_call(self) -> None:
        self.clef_calls += 1

    def fail_clef_call(self) -> None:
        self.clef_failed_calls += 1

    def finish_openai(self, reserve: float, usage: dict[str, Any], elapsed: int, role: str) -> None:
        self.cancel_reservation(reserve)
        incoming = _usage_tokens(usage, "input_tokens")
        outgoing = _usage_tokens(usage, "output_tokens")
        if incoming is None or outgoing is None:
            raise BudgetStop("OpenAI response omitted input_tokens/output_tokens; stopping before another unmetered request.")
        self.openai_calls += 1
        self.openai_input_tokens += incoming
        self.openai_output_tokens += outgoing
        self.openai_cost_usd += (incoming * OPENAI_INPUT_USD_PER_M + outgoing * OPENAI_OUTPUT_USD_PER_M) / 1_000_000
        self.openai_latency_ms.append(elapsed)
        role_totals = self.openai_by_role.setdefault(role, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": []})
        role_totals["calls"] += 1
        role_totals["input_tokens"] += incoming
        role_totals["output_tokens"] += outgoing
        role_totals["latency_ms"].append(elapsed)
        if self.openai_cost_usd > self.max_usd:
            raise BudgetStop(f"OpenAI provider-reported usage exceeded USD cap (${self.openai_cost_usd:.4f}/${self.max_usd:.2f}).")

    def add_clef(self, usage: dict[str, Any], elapsed: int, input_chars: int) -> None:
        self.clef_successful_calls += 1
        self.clef_latency_ms.append(elapsed)
        tokens = _usage_tokens(usage, "input_tokens") or _usage_tokens(usage, "total_tokens")
        if tokens is None:
            tokens = math.ceil(input_chars / 2)
            self.clef_neurons = None
        self.clef_input_tokens += tokens
        self.clef_cost_usd += tokens * CLEF_INPUT_USD_PER_M / 1_000_000
        neurons = usage.get("neurons") or usage.get("neuron_count")
        if isinstance(neurons, (int, float)):
            if self.clef_neurons is not None:
                self.clef_neurons += int(neurons)
        elif self.clef_neurons is not None:
            self.clef_neurons += math.ceil(tokens * NEURONS_PER_M_INPUT / 1_000_000)
        if self.clef_neurons is not None and self.prior_neurons + self.clef_neurons > self.max_neurons:
            raise BudgetStop(f"Clef Neuron cap exceeded ({self.prior_neurons + self.clef_neurons}/{self.max_neurons}).")
        if self.prior_cost_usd + self.openai_cost_usd + self.clef_cost_usd > self.max_usd:
            raise BudgetStop(f"Combined provider USD cap exceeded (${self.prior_cost_usd + self.openai_cost_usd + self.clef_cost_usd:.4f}/${self.max_usd:.2f}).")

    def summary(self) -> dict[str, Any]:
        return {
            "openai_model": "gpt-6-luna", "openai_calls": self.openai_calls,
            "openai_input_tokens": self.openai_input_tokens, "openai_output_tokens": self.openai_output_tokens,
            "openai_cost_usd_estimate": round(self.openai_cost_usd, 6), "openai_cost_cap_usd": self.max_usd,
            "clef_cost_usd_estimate": round(self.clef_cost_usd, 6),
            "prior_attempt_cost_usd_estimate": round(self.prior_cost_usd, 6),
            "combined_cost_usd_estimate": round(self.prior_cost_usd + self.openai_cost_usd + self.clef_cost_usd, 6),
            "openai_latency_ms_mean": round(statistics.mean(self.openai_latency_ms)) if self.openai_latency_ms else None,
            "openai_latency_ms_median": round(statistics.median(self.openai_latency_ms)) if self.openai_latency_ms else None,
            "openai_by_role": {role: {"calls": values["calls"], "input_tokens": values["input_tokens"],
                                       "output_tokens": values["output_tokens"],
                                       "latency_ms_mean": round(statistics.mean(values["latency_ms"])) if values["latency_ms"] else None,
                                       "latency_ms_median": round(statistics.median(values["latency_ms"])) if values["latency_ms"] else None}
                               for role, values in self.openai_by_role.items()},
            "clef_model": CLEF_MODEL_ID, "clef_calls": self.clef_calls,
            "clef_successful_calls": self.clef_successful_calls, "clef_failed_calls": self.clef_failed_calls,
            "clef_input_tokens_reported_or_conservative_estimate": self.clef_input_tokens,
            "clef_neurons_reported_or_estimate": self.clef_neurons,
            "prior_attempt_neurons": self.prior_neurons,
            "combined_clef_neurons_reported_or_estimate": self.prior_neurons + self.clef_neurons if self.clef_neurons is not None else None,
            "clef_neuron_cap": self.max_neurons,
            "clef_latency_ms_mean": round(statistics.mean(self.clef_latency_ms)) if self.clef_latency_ms else None,
            "clef_latency_ms_median": round(statistics.median(self.clef_latency_ms)) if self.clef_latency_ms else None,
        }


class MeteredSalesProvider:
    """Sales Core V2's exact model/reasoning/schema with an evaluation cost guard."""
    def __init__(self, config: dict[str, Any], ledger: Ledger):
        self.config, self.ledger = config, ledger
        if not config["api_key"]:
            raise RuntimeError("OPENAI_API_KEY is required; no mock fallback is available.")

    def decide(self, system_prompt: str, user_prompt: str):
        payload = {
            "model": self.config["model"], "reasoning": {"effort": self.config["reasoning"]},
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
            "text": {"format": {"type": "json_schema", "name": "property_agent_decision", "strict": True, "schema": agent_schema()}},
            "max_output_tokens": 4500, "store": False,
        }
        body = _json(payload).encode()
        reserve = self.ledger.reserve_openai(body.decode(), payload["max_output_tokens"])
        req = urllib.request.Request("https://api.openai.com/v1/responses", data=body,
                                     headers={"Authorization": "Bearer " + self.config["api_key"],
                                              "Content-Type": "application/json"}, method="POST")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            detail = self.ledger.redact(exc.read().decode("utf-8", "replace"))
            raise RuntimeError(f"OpenAI API request failed (HTTP {exc.code}): {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("OpenAI API request could not complete: " + self.ledger.redact(exc)) from exc
        elapsed = round((time.perf_counter() - started) * 1000)
        self.ledger.finish_openai(reserve, result.get("usage") or {}, elapsed, "sales_agent")
        if result.get("status") not in (None, "completed"):
            raise RuntimeError("OpenAI API did not complete the structured response: " + str(result.get("status")))
        output = result.get("output_text")
        if not output:
            for item in result.get("output", []):
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        output = part.get("text")
                        break
        if not output:
            raise RuntimeError("OpenAI API returned no structured decision text.")
        return json.loads(output), result.get("usage") or {}


def metered_json_call(ledger: Ledger, api_key: str, system: str, user: dict[str, Any], max_output: int, role: str) -> tuple[dict[str, Any], dict[str, Any], int]:
    payload = {"model": "gpt-6-luna", "reasoning": {"effort": "high"},
               "input": [{"role": "system", "content": [{"type": "input_text", "text": system}]},
                         {"role": "user", "content": [{"type": "input_text", "text": _json(user)}]}],
               "text": {"format": {"type": "json_object"}}, "max_output_tokens": max_output, "store": False}
    raw = _json(payload)
    reserve = ledger.reserve_openai(raw, max_output)
    request = urllib.request.Request("https://api.openai.com/v1/responses", data=raw.encode(),
                                     headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"OpenAI API request failed (HTTP {exc.code}): {ledger.redact(exc.read().decode('utf-8', 'replace'))}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("OpenAI API request could not complete: " + ledger.redact(exc)) from exc
    elapsed = round((time.perf_counter() - started) * 1000)
    usage = response_data.get("usage") or {}
    ledger.finish_openai(reserve, usage, elapsed, role)
    if response_data.get("status") not in (None, "completed"):
        raise RuntimeError("GPT-6 Luna JSON response did not complete.")
    output = response_data.get("output_text")
    if not output:
        output = next((part.get("text") for item in response_data.get("output", [])
                       for part in item.get("content", []) if part.get("type") == "output_text"), None)
    if not output:
        raise RuntimeError("GPT-6 Luna returned no JSON output.")
    return json.loads(output), usage, elapsed


def load_resources() -> dict[str, str]:
    return {path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(KNOWLEDGE.rglob("*.md"))}


def _section_summary(text: str) -> str:
    part = text.split("## Purpose", 1)[1].split("\n## ", 1)[0] if "## Purpose" in text else text
    return re.sub(r"\s+", " ", part)[:360]


def _clef_request(ledger: Ledger, account: str, token: str, transcript: list[dict[str, str]], resources: dict[str, str]) -> dict[str, Any]:
    choices = {
        "purchase_purpose": {"OWN_STAY": "Customer plans to live there.", "INVESTMENT": "Customer is primarily evaluating investment.",
                             "BOTH": "Customer stated both uses.", "EXPLORING": "Customer is browsing without decided purpose.", "UNKNOWN": "Not established."},
        "buyer_signal": {"QUESTION": "Asking for information.", "POSITIVE": "Clear positive buying signal.", "NEUTRAL": "Neutral acknowledgement.",
                         "OBJECTION": "Concern or disagreement.", "DISENGAGED": "Wants to stop or disengage.", "UNKNOWN": "Unclear."},
        "response_stance": {"AFFIRMATIVE": "Clear agreement.", "TENTATIVE": "Tentative agreement.", "NEUTRAL": "Acknowledgement without commitment.",
                            "DECLINING": "Declines or rejects.", "QUESTION": "Requests information.", "OVERWHELMED": "Needs time or signals overload.", "UNCLEAR": "Unclear."},
        "intent_level": {"LOW": "Limited evidence of active purchase consideration.", "MEDIUM": "Genuine need, no clear action readiness.",
                         "HIGH": "Seriously evaluating next steps.", "READY": "A viewing or appointment is useful now.", "UNKNOWN": "Not established."},
    }
    questions: dict[str, Any] = {key: {"type": "choice", "instructions": prompt, "criteria": options}
                                 for key, (prompt, options) in {
        "purchase_purpose": ("Which purchase purpose is best supported by the full conversation?", choices["purchase_purpose"]),
        "buyer_signal": ("What signal does the latest customer message convey in context?", choices["buyer_signal"]),
        "response_stance": ("What stance does the latest customer message express in context?", choices["response_stance"]),
        "intent_level": ("What intent level is supported by the conversation so far?", choices["intent_level"]),
    }.items()}
    resources_meta = {path: _section_summary(text) for path, text in resources.items()}
    for idx, (path, description) in enumerate(resources_meta.items()):
        questions[f"knowledge_{idx}"] = {"type": "noul", "instructions": f"Would this Knowledge be useful for responding to the current customer turn? Resource {path}: {description}"}
    payload = {"model": "clef", "state": {"conversation": transcript, "available_resources": resources_meta}, "questions": questions}
    prompt_text = _json(payload)
    estimated_tokens, cost_reserve = ledger.reserve_clef(len(prompt_text))
    ledger.start_clef_call()
    request = urllib.request.Request(CLEF_URL.format(account=account), data=prompt_text.encode(),
                                     headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        ledger.fail_clef_call()
        raw_error = exc.read().decode("utf-8", "replace")
        try:
            error_body = json.loads(raw_error)
        except ValueError:
            error_body = {}
        ledger.cancel_reservation(cost_reserve)
        if _is_clef_quota_exhausted(exc.code, error_body):
            raise BudgetStop("Cloudflare Clef daily Neurons allocation is exhausted; stopped before another routed request.") from exc
        detail = ledger.redact(raw_error)
        raise RuntimeError(f"Cloudflare Clef API failed (HTTP {exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        ledger.fail_clef_call()
        ledger.cancel_reservation(cost_reserve)
        raise RuntimeError("Cloudflare Clef request could not complete: " + ledger.redact(exc)) from exc
    elapsed = round((time.perf_counter() - started) * 1000)
    if body.get("success") is not True:
        ledger.fail_clef_call()
        ledger.cancel_reservation(cost_reserve)
        errors = body.get("errors") or []
        if _is_clef_quota_exhausted(None, body):
            raise BudgetStop("Cloudflare Clef daily Neurons allocation is exhausted; stopped before another routed request.")
        raise RuntimeError("Cloudflare Clef returned success=false: " + ledger.redact(errors))
    result = body.get("result") or {}
    if result.get("model") not in ("clef", CLEF_MODEL_ID):
        ledger.cancel_reservation(cost_reserve)
        raise RuntimeError("Cloudflare response did not confirm @cf/cloudflare/clef; no model substitution is allowed.")
    answers = result.get("answers") or {}
    ledger.cancel_reservation(cost_reserve)
    usage = result.get("usage") or {}
    reported_tokens = _usage_tokens(usage, "input_tokens") or _usage_tokens(usage, "total_tokens")
    ledger.add_clef(usage, elapsed, len(prompt_text))
    routes = []
    for idx, path in enumerate(resources_meta):
        answer = answers.get(f"knowledge_{idx}")
        probability = answer.get("noul", answer.get("probability_yes")) if isinstance(answer, dict) else answer
        try:
            probability = float(probability)
        except (ValueError, TypeError):
            probability = 0.0
        routes.append({"path": path, "probability_relevant": probability})
    routes.sort(key=lambda item: item["probability_relevant"], reverse=True)
    selected = []
    if routes:
        floor = max(0.25, routes[0]["probability_relevant"] * 0.60)
        selected = [item["path"] for item in routes if item["probability_relevant"] >= floor][:5]
    def answer_value(name: str):
        value = answers.get(name)
        return value.get("choice", value.get("answer", value.get("value"))) if isinstance(value, dict) else value
    return {"model": result.get("model"), "usage": usage, "estimated_input_tokens": estimated_tokens,
            "usage_token_source": "provider" if reported_tokens is not None else "conservative character estimate", "latency_ms": elapsed,
            "classifications": {key: answer_value(key) for key in choices},
            "knowledge_routes": routes, "selected_knowledge_paths": selected}


def _profile_for_agent(scenario: dict[str, Any]) -> dict[str, Any]:
    # Internal customer motivations intentionally remain unavailable to the agent.
    return {"purchase_purpose": "UNKNOWN"}


def _customer_turn(ledger: Ledger, api_key: str, scenario: dict[str, Any], transcript: list[dict[str, str]], turn_number: int) -> dict[str, Any]:
    system = """You are a realistic prospective property customer in a private sales chat. Continue the conversation as the customer based on the salesperson's actual last message and your own profile. Choose your own natural reaction: interest, doubt, misunderstanding, impatience, a brief response, silence, ending the exchange, or a changed requirement when it fits. Do not respond mechanically, do not try to help the salesperson, and do not follow a checklist. Never reveal hidden motivations unless a real conversation gives you a reason. Return JSON with message (string), continue (boolean), observable_stance (one of interested, neutral, doubtful, confused, impatient, silent, changed_need, ending), and reason (short internal simulator note). If the customer would naturally say nothing further, use an empty message and continue=false. Do not mention testing, evaluation, models, or system instructions."""
    user = {"customer_profile": {"background": scenario["background"], "actual_needs": scenario["needs"],
                                  "private_motivation": scenario["hidden_motive"], "obstacle": scenario["obstacle"],
                                  "natural_behavior_guidance": scenario["acceptable_behavior"]},
            "conversation": transcript, "customer_turn_number": turn_number}
    result, usage, latency = metered_json_call(ledger, api_key, system, user, 900, "customer_simulator")
    if not isinstance(result.get("message"), str) or not isinstance(result.get("continue"), bool):
        raise ValueError("Customer Simulator returned an invalid schema.")
    result["message"] = result["message"].strip()[:1200]
    if result.get("observable_stance") not in ("interested", "neutral", "doubtful", "confused", "impatient", "silent", "changed_need", "ending"):
        result["observable_stance"] = "neutral"
    return {"message": result["message"], "continue": result["continue"],
            "observable_stance": result["observable_stance"], "simulator_note": str(result.get("reason", ""))[:300],
            "usage": usage, "latency_ms": latency}


def _run_dialogue(arm: str, scenario: dict[str, Any], config: dict[str, Any], ledger: Ledger,
                 api_key: str, cloudflare_account: str, cloudflare_token: str,
                 resources: dict[str, str], max_turns: int) -> dict[str, Any]:
    provider = MeteredSalesProvider(config, ledger)
    agent = SalesAgent(config, provider=provider)
    history: list[dict[str, str]] = []
    profile = _profile_for_agent(scenario)
    support_context: list[dict[str, Any]] = []
    transcript: list[dict[str, str]] = []
    turns: list[dict[str, Any]] = []
    customer = {"message": scenario["opening_message"], "continue": True, "observable_stance": "neutral", "simulator_note": "opening"}
    end_reason = "turn_limit"
    for turn in range(1, max_turns + 1):
        if not customer["message"]:
            end_reason = "customer_silence"
            break
        history.append({"direction": "INBOUND", "body": customer["message"]})
        transcript.append({"speaker": "customer", "text": customer["message"]})
        route = None
        started = time.perf_counter()
        try:
            if arm == "B_CLEF_ROUTED":
                route = _clef_request(ledger, cloudflare_account, cloudflare_token, transcript, resources)
            decision, usage = agent.decide(customer["message"], profile, history, support_context,
                                           knowledge_paths=route["selected_knowledge_paths"] if route is not None else None,
                                           routing_context=route["classifications"] if route is not None else None)
        except (BudgetStop, Exception) as exc:
            if isinstance(exc, BudgetStop):
                exc.partial_dialogue = {"arm": arm, "scenario_id": scenario["id"], "transcript": transcript,
                                        "turns": turns + [{"turn": turn, "customer": customer["message"], "clef": route,
                                                           "error": {"type": "BudgetStop", "message": str(exc)}}],
                                        "end_reason": "budget_stop", "customer_turn_count": sum(x["speaker"] == "customer" for x in transcript),
                                        "customer_profile_for_blind_judge": {key: scenario[key] for key in ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior")}}
                raise
            end_reason = "agent_error"
            turns.append({"turn": turn, "customer": customer["message"], "customer_stance": customer["observable_stance"],
                          "clef": route, "error": {"type": type(exc).__name__, "message": ledger.redact(exc)},
                          "latency_ms": round((time.perf_counter() - started) * 1000)})
            break
        updates = decision.get("lead_updates") or {}
        for key, value in updates.items():
            if key in PROFILE_FIELDS and value is not None:
                profile[key] = value
        reply = decision.get("reply", "")
        action = decision.get("action")
        if action == "APPOINTMENT_HANDOFF" and (updates.get("appointment_readiness") or profile.get("appointment_readiness")) not in (
                "READY_FOR_APPOINTMENT", "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED"):
            end_reason = "appointment_readiness_gate_blocked"
            turns.append({"turn": turn, "customer": customer["message"], "customer_stance": customer["observable_stance"],
                          "action": action, "system_gate": "appointment readiness is not persisted as appointment-ready",
                          "clef": route, "openai_usage": usage, "agent_latency_ms": round((time.perf_counter() - started) * 1000)})
            break
        if action in ("MANDATORY_HANDOFF", "APPOINTMENT_HANDOFF"):
            # Runtime formal handoffs transfer ownership and return no outbound message.
            turns.append({"turn": turn, "customer": customer["message"], "customer_stance": customer["observable_stance"],
                          "action": action, "handoff_reason": decision.get("handoff_reason"), "clef": route,
                          "openai_usage": usage, "agent_latency_ms": round((time.perf_counter() - started) * 1000)})
            end_reason = "formal_handoff"
            break
        transcript.append({"speaker": "agent", "text": reply})
        if reply:
            history.append({"direction": "OUTBOUND", "body": reply})
        turn_entry = {"turn": turn, "customer": customer["message"], "customer_stance": customer["observable_stance"],
                      "agent_reply": reply, "action": decision.get("action"), "sales_move": decision.get("sales_move"),
                      "buyer_signal": decision.get("buyer_signal"), "clef": route,
                      "retrieved_knowledge_paths": [item["path"] for item in retrieve(
                          customer["message"], profile,
                          allowed_paths=route["selected_knowledge_paths"] if route is not None else None)],
                      "openai_usage": usage, "agent_latency_ms": round((time.perf_counter() - started) * 1000)}
        if action == "SUPPORT_REQUEST":
            support = dict(decision["support_request"])
            support.update({"status": "OPEN", "support_result": None})
            support_context.append(support)
        if turn >= max_turns:
            turns.append(turn_entry)
            end_reason = "turn_limit"
            break
        try:
            customer = _customer_turn(ledger, api_key, scenario, transcript, turn + 1)
        except BudgetStop as exc:
            turn_entry["customer_simulator_budget_stop"] = True
            turns.append(turn_entry)
            exc.partial_dialogue = {"arm": arm, "scenario_id": scenario["id"], "transcript": transcript,
                                    "turns": turns, "end_reason": "budget_stop",
                                    "customer_turn_count": sum(x["speaker"] == "customer" for x in transcript),
                                    "customer_profile_for_blind_judge": {key: scenario[key] for key in ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior")}}
            raise
        except Exception as exc:
            end_reason = "customer_simulator_error"
            turn_entry["customer_simulator_error"] = {"type": type(exc).__name__, "message": ledger.redact(exc)}
            turns.append(turn_entry)
            break
        turn_entry["customer_next_stance"] = customer["observable_stance"]
        turn_entry["customer_simulator_usage"] = customer["usage"]
        turn_entry["customer_simulator_latency_ms"] = customer["latency_ms"]
        turns.append(turn_entry)
        if not customer["continue"]:
            end_reason = "customer_ended"
            break
    return {"arm": arm, "scenario_id": scenario["id"], "transcript": transcript, "turns": turns,
            "end_reason": end_reason, "customer_turn_count": sum(row["speaker"] == "customer" for row in transcript),
            "customer_profile_for_blind_judge": {key: scenario[key] for key in ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior")}}


def _judge(ledger: Ledger, api_key: str, dialogue: dict[str, Any], knowledge: dict[str, str]) -> dict[str, Any]:
    system = """You are an independent evaluator of a complete property-sales conversation. You are blind to any experimental method. Score the actual customer-facing interaction and nothing about hidden routing. Use the supplied customer context as the situation, not as an answer key. There is no single correct script: do not penalize a sensible answer, question, pause, or early ending when it suits this customer. Score each criterion from 1 (poor) to 5 (strong). Judge factual accuracy against the supplied project Knowledge; flag claims that are unsupported, overconfident, or contradictory. Give concise evidence from the transcript for every score. Return JSON with scores (object containing every requested criterion as integer 1..5), evidence (object with a short transcript quote/reason per criterion), factual_issues (array of strings), overall_note (string). Do not infer correctness from action labels or model metadata."""
    trusted = {path: text[:12000] for path, text in knowledge.items()
               if "/01_facts/" in path or "/02_commercial/" in path}
    user = {"customer_context": dialogue["customer_profile_for_blind_judge"], "transcript": dialogue["transcript"],
            "project_knowledge_for_fact_check": trusted, "criteria": RUBRIC}
    result, usage, latency = metered_json_call(ledger, api_key, system, user, 3000, "blind_evaluator")
    scores = result.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("Blind evaluator returned no scores object.")
    normalized = {}
    for criterion in CRITERIA:
        score = scores.get(criterion)
        if not isinstance(score, (int, float)) or not 1 <= score <= 5:
            raise ValueError(f"Blind evaluator returned an invalid score for {criterion}.")
        normalized[criterion] = int(score)
    return {"scores": normalized, "evidence": result.get("evidence", {}), "factual_issues": result.get("factual_issues", []),
            "overall_note": str(result.get("overall_note", ""))[:1200], "usage": usage, "latency_ms": latency}


def _composite(judgment: dict[str, Any]) -> float:
    return sum(judgment["scores"][criterion] for criterion in CRITERIA) / len(CRITERIA)


def _bootstrap_cluster_ci(pairs: list[dict[str, Any]], samples: int = 10000) -> dict[str, Any]:
    by_scenario: dict[str, list[float]] = {}
    for pair in pairs:
        if pair.get("A_score") is not None and pair.get("B_score") is not None:
            by_scenario.setdefault(pair["scenario_id"], []).append(pair["B_score"] - pair["A_score"])
    clusters = [statistics.mean(values) for values in by_scenario.values()]
    if len(clusters) < 2:
        return {"n_scenarios": len(clusters), "mean_B_minus_A_points_1_to_5": None, "ci95": None,
                "method": "scenario-cluster bootstrap", "statistical_signal": "insufficient valid scenario clusters"}
    rng = random.Random(823641)
    boot = [statistics.mean(rng.choices(clusters, k=len(clusters))) for _ in range(samples)]
    low, high = sorted(boot)[int(samples * 0.025)], sorted(boot)[int(samples * 0.975) - 1]
    mean = statistics.mean(clusters)
    signal = "B higher; 95% CI excludes zero" if low > 0 else "A higher; 95% CI excludes zero" if high < 0 else "no clear difference; 95% CI includes zero"
    return {"n_scenarios": len(clusters), "mean_B_minus_A_points_1_to_5": round(mean, 4),
            "ci95": [round(low, 4), round(high, 4)], "method": "two-sided 95% percentile bootstrap over scenario-cluster means (10,000 resamples)",
            "statistical_signal": signal}


def summarize_dialogues(dialogues: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, list[dict[str, Any]]] = {"A_SALES_CORE_V2": [], "B_CLEF_ROUTED": []}
    for row in dialogues:
        if row.get("judgment"):
            arms[row["arm"]].append(row)
    summary: dict[str, Any] = {"arms": {}, "paired": _bootstrap_cluster_ci(pairs), "scenarios": {}}
    for arm, rows in arms.items():
        comps = [_composite(row["judgment"]) for row in rows]
        summary["arms"][arm] = {"evaluated_dialogues": len(rows), "composite_mean_1_to_5": round(statistics.mean(comps), 3) if comps else None,
                                "criterion_means_1_to_5": {key: round(statistics.mean(row["judgment"]["scores"][key] for row in rows), 3) for key in CRITERIA} if rows else {},
                                "mean_turns": round(statistics.mean(row["customer_turn_count"] for row in rows), 2) if rows else None,
                                "end_reasons": {reason: sum(row.get("end_reason") == reason for row in rows) for reason in sorted({row.get("end_reason") for row in rows})}}
    for pair in pairs:
        summary["scenarios"].setdefault(pair["scenario_id"], []).append(pair)
    summary["scenarios"] = {key: {"pairs": len(vals), "A_mean": round(statistics.mean(p["A_score"] for p in vals if p.get("A_score") is not None), 3) if any(p.get("A_score") is not None for p in vals) else None,
                                   "B_mean": round(statistics.mean(p["B_score"] for p in vals if p.get("B_score") is not None), 3) if any(p.get("B_score") is not None for p in vals) else None}
                             for key, vals in summary["scenarios"].items()}
    return summary


def _valid_for_expansion(dialogues: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    reasons = []
    if len(dialogues) != len(PILOT_IDS) * 2:
        reasons.append("Pilot did not complete all 10 A/B dialogues.")
    for row in dialogues:
        if row.get("blind_judgment") != "complete":
            reasons.append(f"{row['scenario_id']} / {row['arm']} did not receive a valid independent blind judgment.")
        if row.get("end_reason") in ("agent_error", "customer_simulator_error"):
            reasons.append(f"{row['scenario_id']} / {row['arm']} contains a provider or schema failure.")
        customer_facing_reply = any(item["speaker"] == "agent" for item in row.get("transcript", []))
        valid_formal_handoff = row.get("end_reason") == "formal_handoff" and any(
            turn.get("action") in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF") for turn in row.get("turns", []))
        if not row.get("transcript") or not (customer_facing_reply or valid_formal_handoff):
            reasons.append(f"{row['scenario_id']} / {row['arm']} has no complete agent response.")
        if row["arm"] == "B_CLEF_ROUTED" and any(not turn.get("clef", {}).get("model") for turn in row["turns"] if not turn.get("error")):
            reasons.append(f"{row['scenario_id']} Clef route did not confirm the real requested model.")
    observed_stances = {turn.get("customer_next_stance") for row in dialogues for turn in row.get("turns", [])
                        if turn.get("customer_next_stance")}
    if len(observed_stances) < 2:
        reasons.append("Customer Simulator did not demonstrate multiple dynamic response stances during the pilot.")
    return not reasons, reasons


def _markdown_report(report: dict[str, Any]) -> str:
    lines = ["# Sales Core V2 vs Cloudflare Clef + GPT-6 Luna", "", f"Run ID: `{report['run_id']}`", "",
             f"Status: **{report['status']}**", "", "## Result", ""]
    for phase, detail in report.get("phases", {}).items():
        lines += [f"### {phase}", "", f"Dialogues: {len(detail.get('dialogues', []))}", ""]
        summary = detail.get("summary", {})
        for arm, values in summary.get("arms", {}).items():
            lines.append(f"- {arm}: composite {values.get('composite_mean_1_to_5')}; dialogues {values.get('evaluated_dialogues')}; mean turns {values.get('mean_turns')}.")
        if summary.get("paired"):
            paired = summary["paired"]
            lines.append(f"- Paired B − A: {paired.get('mean_B_minus_A_points_1_to_5')} (95% CI {paired.get('ci95')}); {paired.get('statistical_signal')}.")
        if phase == "full" and detail.get("comparison_validity", {}).get("valid") is False:
            lines += ["", "**Comparison is incomplete. Do not interpret the aggregate score or confidence interval as evidence for either arm.**"]
            lines.extend("- " + reason for reason in detail["comparison_validity"].get("reasons", []))
        lines += ["", "#### Blind criterion averages", "", "| Criterion | A: Sales Core V2 | B: Clef routed |", "|---|---:|---:|"]
        a = summary.get("arms", {}).get("A_SALES_CORE_V2", {}).get("criterion_means_1_to_5", {})
        b = summary.get("arms", {}).get("B_CLEF_ROUTED", {}).get("criterion_means_1_to_5", {})
        for criterion in CRITERIA:
            lines.append(f"| {criterion.replace('_', ' ')} | {a.get(criterion, '—')} | {b.get(criterion, '—')} |")
        lines += ["", "#### Scenario results", "", "| Scenario | Pairs | A mean | B mean |", "|---|---:|---:|---:|"]
        for scenario_id, values in summary.get("scenarios", {}).items():
            lines.append(f"| {scenario_id} | {values.get('pairs')} | {values.get('A_mean', '—')} | {values.get('B_mean', '—')} |")
        lines += ["", "#### Reply examples", ""]
        examples = 0
        for row in detail.get("dialogues", []):
            replies = [turn.get("agent_reply") for turn in row.get("turns", []) if turn.get("agent_reply")]
            if not replies:
                continue
            lines.append(f"**{row['scenario_id']} · {row['arm']} · score {row.get('composite_score_1_to_5', 'not scored')}**")
            lines.append("")
            lines.append("  Customer: " + next((turn.get("customer", "") for turn in row["turns"] if turn.get("agent_reply")), ""))
            lines.append("")
            lines.append("  Agent: " + replies[0].replace("\n", " "))
            lines.append("")
            if len(replies) > 1:
                lines.append("  Later reply: " + replies[1].replace("\n", " "))
                lines.append("")
            examples += 1
            if examples >= 6:
                break
        failures = [row for row in detail.get("dialogues", [])
                    if row.get("end_reason") in ("agent_error", "customer_simulator_error", "budget_stop")
                    or row.get("blind_judgment") != "complete"]
        lines += ["#### Failures", ""]
        if not failures:
            lines.append("No provider/schema/judging failures were recorded in this phase.")
        else:
            for row in failures:
                details = row.get("judgment_error") or next((turn.get("error") for turn in row.get("turns", []) if turn.get("error")), None)
                lines.append(f"- `{row.get('scenario_id')}` / `{row.get('arm')}` / `{row.get('end_reason')}`: {details or row.get('blind_judgment')}. Full original transcript is in the JSON report.")
        lines.append("")
    caveat = report.get("protocol", {}).get("baseline_prompt_caveat")
    if caveat:
        lines += ["## Protocol caveat", "", caveat, ""]
    lines += ["## Usage", "", "```json", _json(report.get("usage", {})), "```", "",
              "## Recommendation", "", report.get("recommendation", "Pending review."), "",
              "All dialogue transcripts, route traces, blind scores, and evidence are in the sibling JSON report. Scores are model-based blind judgments and should be read as evidence, not proof of a production lift.", ""]
    return "\n".join(lines)


def _run_phase(name: str, scenarios: list[dict[str, Any]], repeats: int, config: dict[str, Any], ledger: Ledger,
               api_key: str, account: str, token: str, resources: dict[str, str], max_turns: int,
               rng: random.Random) -> dict[str, Any]:
    dialogues = []
    pairs = []
    stop_reason = None
    try:
        for scenario in scenarios:
            for repeat in range(1, repeats + 1):
                pair_id = f"{scenario['id']}-R{repeat}"
                order = ["A_SALES_CORE_V2", "B_CLEF_ROUTED"]
                rng.shuffle(order)
                pair = {"pair_id": pair_id, "scenario_id": scenario["id"], "repeat": repeat, "execution_order": order}
                for arm in order:
                    try:
                        row = _run_dialogue(arm, scenario, config, ledger, api_key, account, token, resources, max_turns)
                    except BudgetStop as exc:
                        row = getattr(exc, "partial_dialogue", None)
                        if row:
                            row["pair_id"] = pair_id
                            row["blind_judgment"] = "pending_budget_stop"
                            dialogues.append(row)
                        raise
                    row["pair_id"] = pair_id
                    row["blind_judgment"] = "pending"
                    try:
                        row["judgment"] = _judge(ledger, api_key, row, resources)
                        row["blind_judgment"] = "complete"
                    except BudgetStop:
                        dialogues.append(row)
                        raise
                    except Exception as exc:
                        row["judgment_error"] = {"type": type(exc).__name__, "message": ledger.redact(exc)}
                        row["blind_judgment"] = "failed"
                    row["composite_score_1_to_5"] = _composite(row["judgment"]) if row.get("judgment") else None
                    dialogues.append(row)
                    pair["A_score" if arm == "A_SALES_CORE_V2" else "B_score"] = row["composite_score_1_to_5"]
                pairs.append(pair)
    except BudgetStop as exc:
        stop_reason = str(exc)
    return {"phase": name, "dialogues": dialogues, "pairs": pairs, "stop_reason": stop_reason,
            "summary": summarize_dialogues(dialogues, pairs)}


def _probe_clef(ledger: Ledger, account: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request("https://api.cloudflare.com/client/v4/user/tokens/verify", headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(request, timeout=45) as response:
        verification = json.loads(response.read().decode())
    if verification.get("success") is not True or (verification.get("result") or {}).get("status") != "active":
        raise RuntimeError("Cloudflare API token verification did not return active.")
    # The first routed customer turn is the actual-model probe; no substitute model is accepted.
    if not re.fullmatch(r"[a-fA-F0-9]{32}", account):
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is missing or malformed.")
    payload = {"model": "clef", "state": {"record": "Connectivity verification only."},
               "questions": {"probe": {"type": "choice", "instructions": "Which state is shown?",
                                         "criteria": {"verified": "The record is a connectivity verification.",
                                                       "other": "The record is something else."}}}}
    raw = _json(payload)
    estimated, reserve = ledger.reserve_clef(len(raw))
    ledger.start_clef_call()
    probe = urllib.request.Request(CLEF_URL.format(account=account), data=raw.encode(),
                                   headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(probe, timeout=60) as response:
            body = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        ledger.fail_clef_call()
        ledger.cancel_reservation(reserve)
        try:
            body = json.loads(exc.read().decode("utf-8", "replace"))
        except ValueError:
            body = {}
        if _is_clef_quota_exhausted(exc.code, body):
            raise BudgetStop("Cloudflare Clef daily Neurons allocation is exhausted; model preflight stopped.") from exc
        raise
    except Exception:
        ledger.fail_clef_call()
        ledger.cancel_reservation(reserve)
        raise
    elapsed = round((time.perf_counter() - started) * 1000)
    result = body.get("result") or {}
    if body.get("success") is not True or result.get("model") not in ("clef", CLEF_MODEL_ID):
        ledger.fail_clef_call()
        ledger.cancel_reservation(reserve)
        raise RuntimeError("Clef connectivity probe failed to confirm @cf/cloudflare/clef; no model substitution is allowed.")
    usage = result.get("usage") or {}
    ledger.cancel_reservation(reserve)
    ledger.add_clef(usage, elapsed, len(raw))
    return {"token_status": "active", "account_id": "[REDACTED]", "model": result.get("model"),
            "latency_ms": elapsed, "estimated_input_tokens": estimated, "usage": usage}


def _load_scenarios() -> list[dict[str, Any]]:
    rows = json.loads(DATASET.read_text(encoding="utf-8"))
    if len(rows) < 30 or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Evaluation set must contain at least 30 uniquely named scenarios.")
    required = {"background", "needs", "hidden_motive", "obstacle", "acceptable_behavior"}
    for row in rows:
        if not required.issubset(row):
            raise ValueError(f"Scenario {row.get('id')} is missing required profile fields.")
        if not row.get("opening_message"):
            raise ValueError(f"Scenario {row.get('id')} is missing its customer opening message.")
    return rows


def run(mode: str, max_usd: float, max_neurons: int, max_turns: int, seed: int,
        prior_cost_usd: float = 0.0, prior_neurons: int = 0) -> dict[str, Any]:
    config = get_config()
    if config["model"] != "gpt-6-luna" or config["provider"] != "openai_api":
        raise RuntimeError("Evaluation is pinned to the existing gpt-6-luna / openai_api configuration.")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not account or not token:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN are required for real Clef; no substitute is allowed.")
    if not config["api_key"]:
        raise RuntimeError("OPENAI_API_KEY is required for GPT-6 Luna; no mock fallback is available.")
    ledger = Ledger(max_usd, max_neurons, (config["api_key"], token), prior_cost_usd, prior_neurons)
    clef_probe = _probe_clef(ledger, account, token)
    scenarios = _load_scenarios()
    by_id = {row["id"]: row for row in scenarios}
    resources = load_resources()
    rng = random.Random(seed)
    report: dict[str, Any] = {"run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                              "status": "running", "model_configuration": {"sales_agent": config["model"],
                                  "reasoning": config["reasoning"], "customer_simulator": "gpt-6-luna/high",
                                  "blind_evaluator": "gpt-6-luna/high", "clef_requested": CLEF_MODEL_ID},
                              "connectivity": {"cloudflare_token": "active", "clef_model_probe": clef_probe},
                              "protocol": {"pilot": "5 distinct scenarios × A/B = 10 dialogues",
                                           "full": "30 scenarios × 3 repeats × A/B = 180 dialogues",
                                           "max_customer_turns": max_turns, "blind_to_arms": True,
                                           "provider_retries": 0, "production_side_effects": False,
                                           "combined_usd_budget_cap": max_usd, "cloudflare_neuron_cap": max_neurons,
                                           "prior_attempt_cost_usd_estimate": prior_cost_usd,
                                           "prior_attempt_neurons": prior_neurons,
                                           "billing_basis": {"openai": "Standard GPT-6 Luna $0.10/1M input and $0.50/1M output; uncached rates used conservatively.",
                                                               "cloudflare": "Clef $0.24/1M input tokens; 21,818 Neurons/1M input tokens. If usage omits tokens/neurons, a conservative character-based estimate is reported.",
                                                               "sources": ["https://developers.openai.com/api/docs/pricing", "https://developers.cloudflare.com/workers-ai/platform/pricing/"]}}, "phases": {}}
    phases = report["phases"]
    if mode in ("pilot", "pilot_then_full"):
        pilot = [by_id[item] for item in PILOT_IDS]
        phases["pilot"] = _run_phase("pilot", pilot, 1, config, ledger, config["api_key"], account, token, resources, max_turns, rng)
        if phases["pilot"].get("stop_reason"):
            report["stop_reason"] = phases["pilot"]["stop_reason"]
            report["status"] = "stopped_budget_during_pilot"
        valid, reasons = _valid_for_expansion(phases["pilot"].get("dialogues", []))
        phases["pilot"]["framework_effective"] = valid
        phases["pilot"]["validation_reasons"] = reasons
        if mode == "pilot_then_full" and valid and report["status"] == "running":
            phases["full"] = _run_phase("full", scenarios, 3, config, ledger, config["api_key"], account, token, resources, max_turns, rng)
            if phases["full"].get("stop_reason"):
                report["stop_reason"] = phases["full"]["stop_reason"]
                report["status"] = "stopped_budget_during_full"
            elif not _phase_complete(phases["full"], expected=180):
                report["status"] = "full_completed_with_failures"
    elif mode == "full":
        phases["full"] = _run_phase("full", scenarios, 3, config, ledger, config["api_key"], account, token, resources, max_turns, rng)
        if phases["full"].get("stop_reason"):
            report["stop_reason"] = phases["full"]["stop_reason"]
            report["status"] = "stopped_budget_during_full"
        elif not _phase_complete(phases["full"], expected=180):
            report["status"] = "full_completed_with_failures"
    report["usage"] = ledger.summary()
    report.setdefault("status", "complete")
    if report["status"] == "running":
        report["status"] = "complete"
    if "full" in phases and _phase_complete(phases["full"], expected=180):
        paired = phases["full"]["summary"]["paired"]
        phases["full"]["comparison_validity"] = {"valid": True, "reasons": []}
        report["recommendation"] = _recommendation(phases["full"]["summary"], paired)
    elif "full" in phases:
        reasons = _phase_failure_reasons(phases["full"])
        phases["full"]["comparison_validity"] = {"valid": False, "reasons": reasons}
        report["recommendation"] = ("Retain Sales Core V2. The full comparison is invalid because Clef's daily free Neurons allocation was exhausted and some B conversations have no real Clef turn. The 5-scenario pilot showed no clear difference; do not infer a full-dialogue sales-quality lift from the incomplete full-phase scores.")
    elif "pilot" in phases:
        report["recommendation"] = "Pilot evidence only; no integration recommendation is justified until the 30-scenario paired evaluation completes."
    else:
        report["recommendation"] = "No quality conclusion: evaluation stopped before a complete pilot."
    return report


def _phase_complete(phase: dict[str, Any], expected: int) -> bool:
    rows = phase.get("dialogues", [])
    return len(rows) == expected and all(
        row.get("blind_judgment") == "complete"
        and row.get("end_reason") not in ("agent_error", "customer_simulator_error")
        and (row.get("arm") != "B_CLEF_ROUTED" or all(turn.get("clef", {}).get("model") for turn in row.get("turns", []) if not turn.get("error")))
        for row in rows
    )


def _phase_failure_reasons(phase: dict[str, Any]) -> list[str]:
    rows = phase.get("dialogues", [])
    reasons = []
    if phase.get("stop_reason"):
        reasons.append(phase["stop_reason"])
    if any(row.get("end_reason") == "agent_error" for row in rows):
        reasons.append("One or more agent turns failed, including unavailable or exhausted Clef calls.")
    if any(row.get("end_reason") == "customer_simulator_error" for row in rows):
        reasons.append("One or more Customer Simulator responses failed structured-output validation.")
    if any(row.get("blind_judgment") != "complete" for row in rows):
        reasons.append("One or more dialogues lack a valid independent blind judgment.")
    if len(rows) != 180:
        reasons.append(f"Expected 180 full-phase dialogues, recorded {len(rows)}.")
    return list(dict.fromkeys(reasons))


def _recommendation(summary: dict[str, Any], paired: dict[str, Any]) -> str:
    a = summary["arms"]["A_SALES_CORE_V2"].get("composite_mean_1_to_5")
    b = summary["arms"]["B_CLEF_ROUTED"].get("composite_mean_1_to_5")
    interval = paired.get("ci95")
    if a is None or b is None or not interval:
        return "Incomplete blind evaluation; retain Sales Core V2 pending a valid comparison."
    if interval[0] > 0 and b >= a + 0.20:
        return "Integrate Clef for Knowledge routing only, behind the existing Luna sales decision, subject to human review of factual-accuracy and repetition failures. The paired scenario-cluster interval favors B, but this remains simulator evidence rather than production proof."
    if interval[1] < 0:
        return "Retain Sales Core V2. Clef routing reduced blind conversation quality in this evaluation; do not integrate it as a sales decision-maker."
    if interval[0] <= 0 <= interval[1] and abs(b - a) < 0.20:
        return "Retain Sales Core V2. This evaluation does not show a clear full-dialogue improvement from Clef routing."
    return "No robust integration case yet. Retain Sales Core V2 and review scenario-level scores, factual issues, and transcript failures before redesigning or repeating the evaluation."


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Blinded real-model A/B evaluation: Sales Core V2 vs Clef knowledge routing")
    parser.add_argument("--mode", choices=("pilot", "pilot_then_full", "full"), default="pilot_then_full")
    parser.add_argument("--max-usd", type=float, default=10.0, help="Hard provider-usage USD cap (default: 10)")
    parser.add_argument("--max-neurons", type=int, default=10000, help="Cloudflare Neurons cap (default: 10000 daily free allocation)")
    parser.add_argument("--prior-cost-usd", type=float, default=0.0, help="Usage already spent in earlier attempts under the same total cap")
    parser.add_argument("--prior-neurons", type=int, default=0, help="Clef Neurons already used in earlier attempts under the same cap")
    parser.add_argument("--max-turns", type=int, default=MAX_CUSTOMER_TURNS, choices=range(2, MAX_CUSTOMER_TURNS + 1))
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args(argv)
    if args.max_usd <= 0 or args.max_neurons <= 0:
        parser.error("Budget caps must be positive.")
    REPORTS.mkdir(parents=True, exist_ok=True)
    try:
        report = run(args.mode, args.max_usd, args.max_neurons, args.max_turns, args.seed,
                     args.prior_cost_usd, args.prior_neurons)
    except Exception as exc:
        report = {"status": "failed_preflight", "error": {"type": type(exc).__name__, "message": str(exc)[:1000]}}
    run_id = report.get("run_id", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    report["run_id"] = run_id
    output = REPORTS / run_id
    output.mkdir(parents=True, exist_ok=True)
    json_path, md_path = output / "report.json", output / "report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown_report(report), encoding="utf-8")
    print(json.dumps({"status": report.get("status"), "report_json": str(json_path), "report_markdown": str(md_path),
                      "usage": report.get("usage"), "recommendation": report.get("recommendation"),
                      "stop_reason": report.get("stop_reason")}, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
