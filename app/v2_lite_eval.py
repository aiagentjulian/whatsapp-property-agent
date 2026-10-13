"""Mission-led paired evaluation of the main V2 and experimental V2 Lite runtimes."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import random
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import get_config
from .provider import PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "778104a3c14b2cc3a870206d83934039b898819b"
LITE_SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
MAIN_ROOT = Path(os.environ.get("V2_MAIN_WORKTREE", ROOT.parent / "whatsapp-property-agent-main-v2-eval-20261013")).resolve()
SCENARIO_IDS = (
    "P3-family-four-bedroom-budget", "E05-layout-four-bedrooms", "P3-too-expensive-ambiguous",
    "E02-first-home-unsure", "P3-short-oh-okay", "P3-pricing-rebates-maintenance",
    "E30-ready-but-no-pressure", "P3-explicit-no-contact",
)
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
    "factual_accuracy": "Answers from supplied Knowledge, acknowledges unknowns, and does not invent facts or commitments.",
    "appropriate_pacing": "Shows a reasonable sales initiative when it helps, respects uncertainty, and stops contact when asked.",
}
INPUT_USD_PER_M = 0.10
OUTPUT_USD_PER_M = 0.50
MAX_CUSTOMER_TURNS = 12


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def load_runtime(root: Path, package_name: str) -> Any:
    """Import an isolated complete app package from the requested worktree."""
    init = root / "app" / "__init__.py"
    spec = importlib.util.spec_from_file_location(package_name, init,
        submodule_search_locations=[str(root / "app")])
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load runtime package at {root}")
    package = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[package_name] = package
    spec.loader.exec_module(package)
    return importlib.import_module(f"{package_name}.agent")


def load_runtimes() -> dict[str, Any]:
    if not MAIN_ROOT.is_dir():
        raise RuntimeError(f"The isolated main V2 worktree is missing: {MAIN_ROOT}")
    return {"A_V2": load_runtime(MAIN_ROOT, "phase3_main_app"),
            "B_V2_LITE": load_runtime(ROOT, "phase3_lite_app")}


def runtime_evidence(runtimes: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    brains, manifests = {}, {}
    for arm, module in runtimes.items():
        root = Path(module.ROOT)
        brains[arm] = module.SalesAgent.context_text()
        package = importlib.import_module(module.__package__ + ".knowledge")
        knowledge = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
                     for p in sorted(package.KNOWLEDGE.rglob("*.md"))}
        manifests[arm] = {
            "root": str(root), "system_prompt_sha256": hashlib.sha256(module.SYSTEM_PROMPT.encode()).hexdigest(),
            "brain_sha256": hashlib.sha256(brains[arm].encode()).hexdigest(),
            "knowledge_files_sha256": {path: hashlib.sha256(text.encode()).hexdigest() for path, text in knowledge.items()},
            "agent_py_sha256": hashlib.sha256((root / "app/agent.py").read_bytes()).hexdigest(),
            "knowledge_py_sha256": hashlib.sha256((root / "app/knowledge.py").read_bytes()).hexdigest(),
            "runtime_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        }
        manifests[arm]["knowledge"] = knowledge
    changed = subprocess.check_output(["git", "diff", "--name-only", f"{BASE_SHA}...{LITE_SHA}"], cwd=ROOT, text=True).splitlines()
    if brains["A_V2"] == brains["B_V2_LITE"]:
        raise RuntimeError("Expected distinct V2 and V2 Lite Sales Brain prompts.")
    manifests["changed_paths_between_commits"] = changed
    return brains, manifests


class Usage:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.calls: dict[str, dict[str, Any]] = {}
        self.request_attempts: dict[str, int] = {}
        self.failed_calls: dict[str, int] = {}

    def start(self, role: str) -> None:
        self.request_attempts[role] = self.request_attempts.get(role, 0) + 1

    def add(self, role: str, usage: dict[str, Any], elapsed_ms: int) -> None:
        row = self.calls.setdefault(role, {"calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
                                           "cache_write_input_tokens": 0, "output_tokens": 0, "latency_ms": []})
        row["calls"] += 1
        row["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
        details = usage.get("input_tokens_details") or {}
        row["cached_input_tokens"] += int(details.get("cached_tokens", 0) or 0)
        row["cache_write_input_tokens"] += int(details.get("cache_write_tokens", 0) or 0)
        row["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
        row["latency_ms"].append(elapsed_ms)

    def fail(self, role: str) -> None:
        self.failed_calls[role] = self.failed_calls.get(role, 0) + 1

    def restore(self, summary: dict[str, Any]) -> None:
        for role, row in summary.get("by_role", {}).items():
            latencies = row.get("latency_samples_ms")
            if not isinstance(latencies, list):
                # Earlier checkpoint format retained only a mean and median.
                latencies = [row["latency_ms_mean"]] * int(row.get("calls", 0)) if row.get("latency_ms_mean") else []
            self.calls[role] = {"calls": int(row.get("calls", 0)), "input_tokens": int(row.get("input_tokens", 0)),
                                "cached_input_tokens": int(row.get("cached_input_tokens", 0)),
                                "cache_write_input_tokens": int(row.get("cache_write_input_tokens", 0)),
                                "output_tokens": int(row.get("output_tokens", 0)), "latency_ms": latencies}
        self.request_attempts.update(summary.get("attempts_by_role", {}))
        self.failed_calls.update(summary.get("failed_calls_by_role", {}))

    def summary(self) -> dict[str, Any]:
        roles = {}
        in_total = cached_total = cache_write_total = out_total = calls = 0
        for role, row in self.calls.items():
            in_total += row["input_tokens"]
            cached_total += row["cached_input_tokens"]
            cache_write_total += row["cache_write_input_tokens"]
            out_total += row["output_tokens"]
            calls += row["calls"]
            roles[role] = {**{k: row[k] for k in ("calls", "input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens")},
                           "latency_ms_mean": round(statistics.mean(row["latency_ms"])) if row["latency_ms"] else None,
                           "latency_ms_median": round(statistics.median(row["latency_ms"])) if row["latency_ms"] else None,
                           "latency_samples_ms": row["latency_ms"]}
        regular_input = max(0, in_total - cached_total - cache_write_total)
        cost = (regular_input * INPUT_USD_PER_M + cached_total * 0.01 + cache_write_total * 0.125 +
                out_total * OUTPUT_USD_PER_M) / 1_000_000
        latencies = [lat for row in self.calls.values() for lat in row["latency_ms"]]
        return {"provider": "OpenAI Responses API", "model": "gpt-6-luna", "request_attempts": sum(self.request_attempts.values()),
                "attempts_by_role": self.request_attempts, "failed_calls_by_role": self.failed_calls, "successful_calls": calls,
                "input_tokens": in_total, "cached_input_tokens": cached_total,
                "cache_write_input_tokens": cache_write_total, "output_tokens": out_total,
                "estimated_cost_usd": round(cost, 6),
                "pricing_usd_per_million_tokens": {"input": INPUT_USD_PER_M, "cached_input": 0.01,
                                                   "cache_write": 0.125, "output": OUTPUT_USD_PER_M},
                "latency_ms_mean": round(statistics.mean(latencies)) if latencies else None,
                "latency_ms_median": round(statistics.median(latencies)) if latencies else None,
                "by_role": roles}


def request_json(usage: Usage, system: str, user: dict[str, Any], role: str, reasoning: str,
                 max_output: int, mock: bool = False, mock_response: dict[str, Any] | None = None):
    if mock:
        return mock_response or {}, {"input_tokens": 0, "output_tokens": 0}, 0
    payload = {"model": "gpt-6-luna", "reasoning": {"effort": reasoning},
               "input": [{"role": "system", "content": [{"type": "input_text", "text": system}]},
                         {"role": "user", "content": [{"type": "input_text", "text": compact(user)}]}],
               "text": {"format": {"type": "json_object"}}, "max_output_tokens": max_output, "store": False}
    body = compact(payload).encode()
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=body,
                                 headers={"Authorization": "Bearer " + usage.api_key,
                                          "Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    usage.start(role)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        usage.fail(role)
        detail = exc.read().decode("utf-8", "replace")[:1000]
        raise RuntimeError(f"OpenAI request for {role} failed (HTTP {exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        usage.fail(role)
        raise RuntimeError(f"OpenAI request for {role} could not complete: {exc}") from exc
    elapsed = round((time.perf_counter() - started) * 1000)
    response_usage = result.get("usage") or {}
    if result.get("status") not in (None, "completed"):
        if "input_tokens" in response_usage and "output_tokens" in response_usage:
            usage.add(role, response_usage, elapsed)
        usage.fail(role)
        raise RuntimeError(f"OpenAI {role} response status: {result.get('status')}; incomplete_details={result.get('incomplete_details')}")
    raw = result.get("output_text") or next((part.get("text") for item in result.get("output", [])
        for part in item.get("content", []) if part.get("type") == "output_text"), None)
    if not raw:
        usage.fail(role)
        raise RuntimeError(f"OpenAI returned no output for {role}.")
    if "input_tokens" not in response_usage or "output_tokens" not in response_usage:
        usage.fail(role)
        raise RuntimeError(f"OpenAI omitted token usage for {role}; stop to avoid unmetered calls.")
    usage.add(role, response_usage, elapsed)
    return json.loads(raw), response_usage, elapsed


class FakeSalesProvider:
    """Dry-run provider verifies the assigned runtime prompt and captures full evidence."""
    def __init__(self, brain: str, arm: str, system: str, prompt_seen: list[dict[str, str]], captures: list[dict[str, Any]]):
        self.brain, self.arm, self.system, self.prompt_seen, self.captures = brain, arm, system, prompt_seen, captures

    def decide(self, system_prompt: str, user_prompt: str):
        context = json.loads(user_prompt)
        brief = context["brain_and_skills"]
        if brief != self.brain or system_prompt != self.system:
            raise AssertionError("V2 agent did not load the assigned prompt for this arm.")
        self.prompt_seen.append({"arm": self.arm, "sha256": hashlib.sha256(brief.encode()).hexdigest()})
        self.captures.append({"arm": self.arm, "system_prompt": system_prompt, "available_context": context})
        reply = "For a family home, we can start with the layout and daily routine that matter most to you. What would you like to check first?"
        decision = {"action": "REPLY", "sales_move": "EXPLORE", "buyer_signal": "QUESTION", "reply": reply,
                    "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                    "handoff_reason": None, "handoff_details": None}
        return decision, {"input_tokens": 0, "output_tokens": 0}


class SalesAgentProvider:
    """Metered copy of the existing V2 Responses request and structured schema."""
    def __init__(self, config: dict[str, Any], usage: Usage, schema: dict[str, Any], arm: str,
                 captures: list[dict[str, Any]]):
        self.config, self.usage, self.schema, self.arm, self.captures = config, usage, schema, arm, captures

    def decide(self, system_prompt: str, user_prompt: str):
        payload = {"model": self.config["model"], "reasoning": {"effort": self.config["reasoning"]},
                   "input": [{"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                             {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]}],
                   "text": {"format": {"type": "json_schema", "name": "property_agent_decision", "strict": True,
                                        "schema": self.schema}}, "max_output_tokens": 4500, "store": False}
        context = json.loads(user_prompt)
        self.captures.append({"arm": self.arm, "system_prompt": system_prompt, "available_context": context})
        request = urllib.request.Request("https://api.openai.com/v1/responses", data=compact(payload).encode(),
            headers={"Authorization": "Bearer " + self.config["api_key"], "Content-Type": "application/json"}, method="POST")
        self.usage.start("sales_agent")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            self.usage.fail("sales_agent")
            raise RuntimeError(f"OpenAI Sales Agent request failed (HTTP {exc.code}): {exc.read().decode('utf-8', 'replace')[:1000]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            self.usage.fail("sales_agent")
            raise RuntimeError(f"OpenAI Sales Agent request could not complete: {exc}") from exc
        elapsed = round((time.perf_counter() - started) * 1000)
        response_usage = result.get("usage") or {}
        if result.get("status") not in (None, "completed"):
            if "input_tokens" in response_usage and "output_tokens" in response_usage:
                self.usage.add("sales_agent", response_usage, elapsed)
            self.usage.fail("sales_agent")
            raise RuntimeError(f"OpenAI Sales Agent response status: {result.get('status')}; incomplete_details={result.get('incomplete_details')}")
        raw = result.get("output_text") or next((part.get("text") for item in result.get("output", [])
            for part in item.get("content", []) if part.get("type") == "output_text"), None)
        if not raw or "input_tokens" not in response_usage or "output_tokens" not in response_usage:
            self.usage.fail("sales_agent")
            raise RuntimeError("OpenAI Sales Agent response omitted output or token usage.")
        self.usage.add("sales_agent", response_usage, elapsed)
        return json.loads(raw), response_usage


class FakeOperations:
    """Conversation-local fake operations; no database, CRM, appointment, or messaging calls."""
    def __init__(self):
        self.support_requests: list[dict[str, Any]] = []
        self.handoffs: list[dict[str, Any]] = []

    def support_request(self, request: dict[str, Any]) -> dict[str, Any]:
        saved = {**request, "status": "OPEN", "support_result": None}
        self.support_requests.append(saved)
        return saved

    def handoff(self, reason: str | None) -> None:
        self.handoffs.append({"reason": reason})


def customer_turn(usage: Usage, scenario: dict[str, Any], transcript: list[dict[str, str]], turn: int, mock: bool):
    system = """You are a realistic prospective property customer in a private WhatsApp sales chat. Continue only as the customer, reacting naturally to the actual conversation. Follow your profile, not a checklist. You may show interest, doubt, misunderstanding, impatience, brief replies, silence, end the exchange, or change a requirement when natural. Never help the salesperson or reveal hidden motivation without a real conversational reason. Return JSON: message (string), continue (boolean), observable_stance (interested, neutral, doubtful, confused, impatient, silent, changed_need, ending), reason (short internal note). If you would say nothing further, return empty message and continue=false. Do not mention the evaluation or system instructions."""
    profile = customer_simulator_profile(scenario)
    mock_response = {"message": "Mostly the monthly amount. I don't want to stretch the budget.", "continue": True,
                     "observable_stance": "doubtful", "reason": "mock follow-up"} if turn == 2 else {
                     "message": "Thanks, I'll think about it.", "continue": False, "observable_stance": "ending", "reason": "mock end"}
    result, api_usage, elapsed = request_json(usage, system, {"customer_profile": profile, "conversation": transcript,
        "customer_turn_number": turn}, "customer_simulator", "medium", 900, mock, mock_response)
    if not isinstance(result.get("message"), str) or not isinstance(result.get("continue"), bool):
        raise ValueError("Customer Simulator returned invalid fields.")
    result["message"] = result["message"].strip()[:1200]
    if result.get("observable_stance") not in ("interested", "neutral", "doubtful", "confused", "impatient", "silent", "changed_need", "ending"):
        result["observable_stance"] = "neutral"
    result.update({"usage": api_usage, "latency_ms": elapsed})
    return result


def customer_simulator_profile(scenario: dict[str, Any]) -> dict[str, str]:
    """Keep evaluator expectations out of the simulated customer's persona."""
    return {key: scenario[key] for key in ("background", "needs", "hidden_motive", "obstacle")}


def run_dialogue(arm: str, runtime: Any, brain: str, scenario: dict[str, Any], config: dict[str, Any], usage: Usage,
                 prompt_seen: list[dict[str, str]], captures: list[dict[str, Any]], mock: bool):
    profile: dict[str, Any] = {"purchase_purpose": "UNKNOWN"}
    history = list(scenario.get("seeded_history", []))
    transcript = [{"speaker": "customer" if row["direction"] == "INBOUND" else "agent", "text": row["body"]}
                  for row in history]
    turns: list[dict[str, Any]] = []
    operations = FakeOperations()
    agent_provider = (FakeSalesProvider(brain, arm, runtime.SYSTEM_PROMPT, prompt_seen, captures) if mock else
                      SalesAgentProvider(config, usage, importlib.import_module(runtime.__package__ + ".provider").agent_schema(), arm, captures))
    agent = runtime.SalesAgent(config, provider=agent_provider)
    customer = {"message": scenario["opening_message"], "continue": True, "observable_stance": "neutral", "simulator_note": "opening"}
    end_reason = "customer_turn_limit"
    for turn in range(1, MAX_CUSTOMER_TURNS + 1):
        if not customer["message"]:
            end_reason = "customer_silence"
            break
        history.append({"direction": "INBOUND", "body": customer["message"]})
        transcript.append({"speaker": "customer", "text": customer["message"]})
        started = time.perf_counter()
        try:
            if mock:
                decision, agent_usage = agent.decide(customer["message"], profile, history,
                    operations.support_requests)
            else:
                decision, agent_usage = agent.decide(customer["message"], profile, history,
                    operations.support_requests)
        except Exception as exc:
            turns.append({"turn": turn, "customer": customer["message"], "error": {"type": type(exc).__name__, "message": str(exc)[:1000]}})
            return {"arm": arm, "scenario_id": scenario["id"], "transcript": transcript, "turns": turns,
                    "customer_turn_count": len(turns) + 1,
                    "end_reason": "agent_error", "operations": operations.__dict__}
        updates = decision.get("lead_updates") or {}
        profile.update({k: v for k, v in updates.items() if k in PROFILE_FIELDS and v is not None})
        action = decision.get("action")
        if action == "APPOINTMENT_HANDOFF" and profile.get("appointment_readiness") not in (
                "READY_FOR_APPOINTMENT", "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED"):
            turns.append({"turn": turn, "customer": customer["message"], "action": action,
                          "system_gate": "appointment readiness not persisted", "agent_reply": ""})
            end_reason = "appointment_readiness_gate_blocked"
            break
        if action in ("MANDATORY_HANDOFF", "APPOINTMENT_HANDOFF"):
            operations.handoff(decision.get("handoff_reason"))
            turns.append({"turn": turn, "customer": customer["message"], "action": action,
                          "handoff_reason": decision.get("handoff_reason")})
            end_reason = "formal_handoff"
            break
        reply = decision.get("reply", "")
        transcript.append({"speaker": "agent", "text": reply})
        if reply:
            history.append({"direction": "OUTBOUND", "body": reply})
        evidence = captures[-1]["available_context"]
        entry = {"turn": turn, "customer": customer["message"], "customer_stance": customer.get("observable_stance"),
                 "agent_reply": reply, "action": action, "sales_move": decision.get("sales_move"),
                 "buyer_signal": decision.get("buyer_signal"), "openai_usage": agent_usage,
                 "agent_latency_ms": round((time.perf_counter() - started) * 1000),
                 "system_prompt": captures[-1]["system_prompt"], "available_to_sales_agent": evidence,
                 "retrieved_knowledge_paths": [x.get("path") for x in evidence.get("relevant_project_knowledge", [])],
                 "retrieved_knowledge_passages": evidence.get("relevant_project_knowledge", []),
                 "separately_supplied_facts": {key: evidence.get(key) for key in
                    ("current_project_unit_offering", "focused_sales_evidence", "verified_support_results")}}
        if action == "SUPPORT_REQUEST":
            entry["support_request"] = operations.support_request(decision["support_request"])
        if turn == MAX_CUSTOMER_TURNS:
            turns.append(entry)
            end_reason = "customer_turn_limit"
            break
        try:
            customer = customer_turn(usage, scenario, transcript, turn + 1, mock)
        except Exception as exc:
            entry["customer_simulator_error"] = {"type": type(exc).__name__, "message": str(exc)[:1000]}
            turns.append(entry)
            end_reason = "customer_simulator_error"
            break
        entry["customer_next_stance"] = customer["observable_stance"]
        entry["customer_simulator_usage"] = customer["usage"]
        entry["customer_simulator_latency_ms"] = customer["latency_ms"]
        turns.append(entry)
        if not customer["continue"]:
            end_reason = "customer_ended"
            break
    return {"arm": arm, "scenario_id": scenario["id"], "transcript": transcript, "turns": turns,
            "customer_turn_count": len(turns),
            "end_reason": end_reason, "operations": operations.__dict__,
            "customer_profile_for_blind_judge": {k: scenario[k] for k in ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior")}}


def judge(usage: Usage, dialogue: dict[str, Any], knowledge: dict[str, str], mock: bool):
    system = """You are an independent blind evaluator of a complete property-sales conversation. Judge only the customer-facing interaction; ignore arm identity and internal actions. Assess actual judgment, naturalness, listening, useful initiative, repetition, verified facts, and respect for explicit no-contact requests. Do not reward length, early termination, or viewing requests by themselves. For factual review, compare each turn's available_to_sales_agent information with the broader project Knowledge: distinguish a retrieval omission from a response omission and a genuine Knowledge gap. 'Pearl Residences' is the authorized customer-facing name for the project whose formal identity is SkyWorld Pearlmont; do not mark that alias inaccurate. Score criteria from 1 to 5 and provide specific turn-level evidence. Return JSON: scores, evidence (criterion to short quote/reason), factual_issues (array with cause where possible), overall_note (string)."""
    trusted = {p: t[:12000] for p, t in knowledge.items() if "/01_facts/" in p or "/02_commercial/" in p}
    user = {"customer_context": dialogue["customer_profile_for_blind_judge"], "transcript": dialogue["transcript"],
            "turn_level_information_available_to_sales_agent": [
                {"turn": t.get("turn"), "available": t.get("available_to_sales_agent"), "reply": t.get("agent_reply")}
                for t in dialogue.get("turns", [])],
            "project_knowledge_for_fact_check": trusted, "criteria": RUBRIC}
    fake = {"scores": {k: 3 for k in CRITERIA},
            "evidence": {k: "Mock dry-run: criterion included in blind judging request." for k in CRITERIA},
            "factual_issues": [], "overall_note": "Mock dry run only."}
    result, api_usage, elapsed = request_json(usage, system, user, "blind_evaluator", "xhigh", 12000, mock, fake)
    scores = result.get("scores") or {}
    normalized = {}
    for key in CRITERIA:
        score = scores.get(key)
        if not isinstance(score, (int, float)) or not 1 <= score <= 5:
            raise ValueError(f"Blind evaluator returned invalid {key} score.")
        normalized[key] = int(score)
    return {"scores": normalized, "evidence": result.get("evidence", {}), "factual_issues": result.get("factual_issues", []),
            "overall_note": result.get("overall_note", ""), "usage": api_usage, "latency_ms": elapsed}


def composite(judgment: dict[str, Any]) -> float:
    return sum(judgment["scores"][k] for k in CRITERIA) / len(CRITERIA)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mission-led main V2 versus V2 Lite evaluation")
    parser.add_argument("--mock", action="store_true", help="Run local full-path fake-provider test; no network calls")
    parser.add_argument("--output", type=Path, help="Output JSON path; real run defaults to a timestamped report")
    parser.add_argument("--resume", type=Path, help="Resume an incomplete saved real run without repeating completed dialogues")
    parser.add_argument("--seed", type=int, default=20261013)
    args = parser.parse_args(argv)
    try:
        runtimes = load_runtimes()
        brains, runtime_manifest = runtime_evidence(runtimes)
        if runtime_manifest["A_V2"]["runtime_commit"] != BASE_SHA:
            raise RuntimeError("The baseline worktree does not match the recorded main commit.")
        knowledge_by_arm = {arm: runtime_manifest[arm].pop("knowledge") for arm in runtimes}
        config = get_config()
        if config["model"] != "gpt-6-luna" or config["reasoning"] != "high":
            raise RuntimeError("Sales Agent must use gpt-6-luna/high.")
        if not args.mock and not config["api_key"]:
            raise RuntimeError("OPENAI_API_KEY is required for the paid evaluation.")
        usage = Usage(config["api_key"])
        rows = json.loads((ROOT / "simulator/evaluation/scenarios.json").read_text(encoding="utf-8"))
        by_id = {row["id"]: row for row in rows}
        scenarios = [by_id[item] for item in SCENARIO_IDS]
        rng = random.Random(args.seed)
        prompt_seen: list[dict[str, str]] = []
        captures: list[dict[str, Any]] = []
        if args.resume:
            report = json.loads(args.resume.read_text(encoding="utf-8"))
            if report.get("git", {}).get("lite_commit") != LITE_SHA:
                raise RuntimeError("Resume report was created for a different V2 Lite commit.")
            usage.restore(report.get("usage", {}))
            # Bring earlier checkpoints into the current request-attempt accounting.
            for role, count in usage.calls.items():
                usage.request_attempts[role] = max(usage.request_attempts.get(role, 0), count["calls"])
            if any(row.get("end_reason") == "evaluation_error" for row in report.get("dialogues", [])):
                usage.failed_calls["blind_evaluator"] = max(usage.failed_calls.get("blind_evaluator", 0), 1)
            prompt_seen = list(report.get("prompt_load_checks", []))
        else:
            report = {
            "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), "status": "running",
            "git": {"main_base": BASE_SHA, "lite_commit": LITE_SHA,
                    "runtime_comparison": runtime_manifest},
            "model_configuration": {"sales_agent": "gpt-6-luna/high", "customer_simulator": "gpt-6-luna/medium",
                                    "blind_judge": "gpt-6-luna/xhigh"},
            "protocol": {"paired_scenarios": list(SCENARIO_IDS), "max_customer_turns": MAX_CUSTOMER_TURNS,
                         "minimum_customer_turns": 0, "blind_judge_receives_arm_identity": False,
                         "production_side_effects": False, "operations_adapter": "conversation-local in-memory fake",
                         "customer_messages_fixed": False, "each_arm_uses_its_own_runtime": True},
            "dialogues": [], "pairs": [], "usage": {},
            }
            prompt_seen: list[dict[str, str]] = []
        saved = {(row.get("scenario_id"), row.get("arm")): row for row in report.get("dialogues", [])}
        for scenario in scenarios:
            arms = ["A_V2", "B_V2_LITE"]
            rng.shuffle(arms)
            pair = {"scenario_id": scenario["id"], "execution_order": arms}
            for arm in arms:
                row = saved.get((scenario["id"], arm))
                if row and row.get("blind_judgment") == "complete":
                    pair["A_score" if arm == "A_V2" else "B_score"] = row.get("composite_score_1_to_5")
                    continue
                if row and row.get("end_reason") == "evaluation_error":
                    row["end_reason"] = "customer_ended" if row.get("customer_turn_count", 0) < MAX_CUSTOMER_TURNS else "customer_turn_limit"
                if row and "customer_profile_for_blind_judge" not in row:
                    row["customer_profile_for_blind_judge"] = {k: scenario[k] for k in
                        ("background", "needs", "hidden_motive", "obstacle", "acceptable_behavior")}
                try:
                    if row is None:
                        row = run_dialogue(arm, runtimes[arm], brains[arm], scenario, config, usage,
                                           prompt_seen, captures, args.mock)
                        report["dialogues"].append(row)
                        saved[(scenario["id"], arm)] = row
                    row["judgment"] = judge(usage, row, knowledge_by_arm[arm], args.mock)
                    row["composite_score_1_to_5"] = round(composite(row["judgment"]), 3)
                    row["blind_judgment"] = "complete"
                    row.pop("error", None)
                except Exception as exc:
                    row["judgment_error" if row.get("transcript") else "error"] = {"type": type(exc).__name__, "message": str(exc)[:1000]}
                    row["blind_judgment"] = "failed"
                    if row.get("end_reason") not in ("agent_error", "customer_simulator_error"):
                        row["end_reason"] = "customer_ended" if row.get("customer_turn_count", 0) < MAX_CUSTOMER_TURNS else "customer_turn_limit"
                    report["usage"] = usage.summary()
                    report["prompt_load_checks"] = list(prompt_seen)
                    report["status"] = "incomplete"
                    report["stop_reason"] = row.get("judgment_error") or row.get("error")
                    target = args.output or (args.resume if args.resume else ROOT / "simulator/v2_lite_eval_reports" / report["run_id"] / "report.json")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps({"status": "incomplete", "output": str(target), "dialogues": len(report["dialogues"]),
                                      "usage": report["usage"], "stop_reason": report["stop_reason"]}, ensure_ascii=False, indent=2))
                    return 1
                pair["A_score" if arm == "A_V2" else "B_score"] = row.get("composite_score_1_to_5")
                report["usage"] = usage.summary()
                report["prompt_load_checks"] = list(prompt_seen)
                target = args.output or (args.resume if args.resume else ROOT / "simulator/v2_lite_eval_reports" / report["run_id"] / "report.json")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                # Flush after every completed dialogue so provider/balance failures preserve prior work.
                if row.get("end_reason") in ("agent_error", "customer_simulator_error"):
                    report["status"] = "incomplete"
                    report["stop_reason"] = row.get("error") or row.get("end_reason")
                    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps({"status": "incomplete", "output": str(target), "dialogues": len(report["dialogues"]),
                                      "usage": report["usage"], "stop_reason": report["stop_reason"]}, ensure_ascii=False, indent=2))
                    return 1
            if not any(p.get("scenario_id") == scenario["id"] for p in report.get("pairs", [])):
                report["pairs"].append(pair)
        report["usage"] = usage.summary()
        report["prompt_load_checks"] = list(prompt_seen)
        report["status"] = "complete" if len(report["dialogues"]) == 16 and all(r.get("blind_judgment") == "complete" for r in report["dialogues"]) else "incomplete"
        report["summary"] = summarize(report["dialogues"])
        report["recommendation"] = recommendation(report)
        target = args.output or (ROOT / "simulator/v2_lite_eval_reports" / report["run_id"] / "report.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "output": str(target), "dialogues": len(report["dialogues"]),
                          "usage": report["usage"], "summary": report.get("summary"), "recommendation": report.get("recommendation")},
                         ensure_ascii=False, indent=2))
        return 0 if report["status"] == "complete" else 1
    except Exception as exc:
        print(json.dumps({"status": "failed_preflight", "error": {"type": type(exc).__name__, "message": str(exc)[:1000]}}, ensure_ascii=False))
        return 1


def summarize(dialogues: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in dialogues if row.get("judgment")]
    means = {}
    for arm in ("A_V2", "B_V2_LITE"):
        selected = [r for r in valid if r["arm"] == arm]
        means[arm] = {"n": len(selected), "composite_mean": round(statistics.mean(r["composite_score_1_to_5"] for r in selected), 3) if selected else None,
                      "mean_customer_turns": round(statistics.mean(r["customer_turn_count"] for r in selected), 2) if selected else None,
                      "criterion_means": {k: round(statistics.mean(r["judgment"]["scores"][k] for r in selected), 3) for k in CRITERIA} if selected else {}}
    pairs = {}
    for row in valid:
        pairs.setdefault(row["scenario_id"], {})[row["arm"]] = row["composite_score_1_to_5"]
    pairs_out = {key: {**value, "B_minus_A": round(value["B_V2_LITE"] - value["A_V2"], 3)}
                 for key, value in pairs.items() if "A_V2" in value and "B_V2_LITE" in value}
    return {"arms": means, "paired_scenarios": pairs_out,
            "paired_mean_B_minus_A": round(statistics.mean(p["B_minus_A"] for p in pairs_out.values()), 3) if pairs_out else None}


def recommendation(report: dict[str, Any]) -> str:
    if report.get("status") != "complete":
        return "Keep V2 pending a complete paired evaluation."
    return "Pending transcript and turn-level evidence review; do not decide from the score average alone."


if __name__ == "__main__":
    raise SystemExit(main())
