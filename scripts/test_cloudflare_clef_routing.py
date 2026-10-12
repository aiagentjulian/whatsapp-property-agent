#!/usr/bin/env python3
"""Compare Cloudflare Clef decisions with isolated Sales Core V2 replays.

The script calls the Clef REST API directly and the existing Sales Core V2
agent in memory. It does not start WhatsApp, write the production database,
send messages, or change the production sales flow.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODEL_ID = "@cf/cloudflare/clef"
MODEL_SELECTOR = "clef"
CLEF_URL = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/clef"
PEA008_TRANSCRIPT = ROOT / "simulator/reports/RUN-V16-20261007T155329Z/PEA-008.transcript.json"
PEA008_SCENARIO = ROOT / "simulator/scenarios/pearlmont/PEA-008.json"

KNOWLEDGE_RESOURCES = (
    "knowledge/project/pearlmont/01_facts/overview.md",
    "knowledge/project/pearlmont/01_facts/location-and-connectivity.md",
    "knowledge/project/pearlmont/01_facts/school-access-and-family.md",
    "knowledge/project/pearlmont/01_facts/facilities-and-quality.md",
    "knowledge/project/pearlmont/01_facts/unit-and-layout.md",
    "knowledge/project/pearlmont/01_facts/orientation-and-view.md",
    "knowledge/project/pearlmont/02_commercial/pricing.md",
    "knowledge/project/pearlmont/02_commercial/sales-package.md",
    "knowledge/project/pearlmont/03_sales/unit-fit.md",
    "knowledge/project/pearlmont/03_sales/sales-judgment.md",
    "knowledge/project/pearlmont/03_sales/viewing-close.md",
)
SKILL_RESOURCES = (
    "skills/decide-next-action.md",
    "skills/retrieve-project-knowledge.md",
    "skills/update-lead-profile.md",
    "skills/request-human-support.md",
    "skills/handoff-to-human.md",
    "skills/sync-google-sheet.md",
)

CHOICE_QUESTIONS: dict[str, dict[str, str]] = {
    "purchase_purpose": {
        "OWN_STAY": "The customer is considering the property for their own residence.",
        "INVESTMENT": "The customer is considering the property primarily as an investment.",
        "BOTH": "The customer has expressed both own-residence and investment purposes.",
        "EXPLORING": "The customer is exploring options without a clear purchase purpose.",
        "UNKNOWN": "The conversation does not establish a purchase purpose.",
    },
    "household_composition": {
        "INDIVIDUAL_OR_COUPLE": "The stated household is an individual or couple.",
        "FAMILY": "The stated household includes a family group.",
        "OTHER_GROUP": "The stated household is another group arrangement.",
        "UNKNOWN": "The conversation does not establish household composition.",
    },
    "household_size": {
        "ONE": "One person.",
        "TWO": "Two people.",
        "THREE": "Three people.",
        "FOUR": "Four people.",
        "FIVE_OR_MORE": "Five or more people.",
        "UNKNOWN": "No household size is established.",
    },
    "buyer_signal": {
        "QUESTION": "The customer is asking for information or clarification.",
        "POSITIVE": "The customer expresses a clear positive buying signal.",
        "NEUTRAL": "The customer gives a neutral acknowledgement or response.",
        "OBJECTION": "The customer raises a concern, blocker, or disagreement.",
        "DISENGAGED": "The customer signals they want to stop or disengage.",
        "UNKNOWN": "The customer signal is unclear.",
    },
    "response_stance": {
        "CLEAR_AFFIRMATIVE": "The latest message clearly agrees or opts in.",
        "TENTATIVE_AFFIRMATIVE": "The latest message agrees tentatively or with uncertainty.",
        "NEUTRAL_ACKNOWLEDGEMENT": "The latest message acknowledges information without a clear new commitment.",
        "NEGATIVE_OR_DECLINING": "The latest message declines or rejects the suggestion.",
        "REQUESTING_INFORMATION": "The latest message asks for information or clarification.",
        "OVERWHELMED": "The latest message says the customer is overloaded or needs time.",
        "UNCLEAR": "The latest message does not establish a clear stance.",
    },
    "intent_level": {
        "LOW": "Limited evidence of active purchase consideration.",
        "MEDIUM": "A genuine need or preference is present, without clear movement toward action.",
        "HIGH": "The customer is seriously evaluating whether or how to proceed.",
        "READY_FOR_APPOINTMENT": "A viewing, call, or appointment is now the useful next step.",
    },
    "sales_move": {
        "ANSWER": "Answer a direct customer question with supported information.",
        "EXPLORE": "Ask one useful question to understand an unresolved customer need.",
        "POSITION": "Connect a relevant verified benefit to the customer's needs.",
        "HANDLE": "Address a concern, objection, or uncertainty.",
        "VIEWING": "Discuss a viewing when the conversation supports that move.",
        "GIVE_SPACE": "Acknowledge the customer and allow space without another pitch or question.",
    },
    "next_action": {
        "ASK": "Ask one useful question to clarify an unresolved need.",
        "ANSWER": "Answer the current question with supported information.",
        "POSITION": "Connect a relevant verified benefit to the customer's needs.",
        "HANDLE_OBJECTION": "Address a concern, objection, or uncertainty.",
        "NARROW_UNIT": "Narrow suitable unit categories using established priorities.",
        "REQUEST_SUPPORT": "Request human verification for material information that is unavailable.",
        "CLOSE_VIEWING": "Explore a viewing after the customer shows sufficient interest.",
        "APPOINTMENT_HANDOFF": "Hand off an appointment request to the scheduling owner.",
        "MANDATORY_HANDOFF": "Hand off a case that requires human ownership.",
        "ACKNOWLEDGE_MAINTAIN": "Acknowledge the message and maintain the conversation without advancing it.",
    },
    "runtime_action": {
        "REPLY": "Continue with a normal customer-facing response.",
        "SUPPORT_REQUEST": "Request verification for a material fact that is not currently verified.",
        "APPOINTMENT_HANDOFF": "Pass an appointment request to the scheduling owner.",
        "MANDATORY_HANDOFF": "Transfer the conversation to a human owner when required.",
    },
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            item = line.strip()
            if not item or item.startswith("#"):
                continue
            if item.startswith("export "):
                item = item[7:].lstrip()
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    for key in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "OPENAI_API_KEY"):
        if os.environ.get(key):
            values.setdefault(key, os.environ[key])
    return values


def redact(value: Any, secrets: tuple[str, ...]) -> str:
    result = str(value)
    for secret in secrets:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result[:600]


def cloudflare_request(
    url: str,
    token: str,
    secrets: tuple[str, ...],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method="POST" if payload is not None else "GET",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = response.status
            body = json.loads(response.read())
    except urllib.error.HTTPError as error:
        status = error.code
        try:
            body = json.loads(error.read())
        except (ValueError, OSError):
            body = {}
    except (TimeoutError, urllib.error.URLError, OSError) as error:
        return {
            "http_status": None,
            "latency_ms": round((time.perf_counter() - started) * 1000),
            "answers": {},
            "usage": {},
            "errors": [{"type": type(error).__name__, "message": redact(error, secrets)}],
        }
    result = body.get("result") or {}
    errors = [
        {
            "code": error.get("code"),
            "message": redact(error.get("message", ""), secrets),
        }
        for error in body.get("errors", [])
    ]
    if not body.get("success") and not errors:
        errors = [{"code": None, "message": "Cloudflare returned success=false without error details."}]
    return {
        "http_status": status,
        "success": status == 200 and body.get("success") is True,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "token_status": result.get("status") if url.endswith("/user/tokens/verify") else None,
        "response_model": result.get("model"),
        "answers": result.get("answers") or {},
        "usage": result.get("usage") or {},
        "errors": errors,
    }


def clef_questions() -> tuple[dict[str, dict[str, Any]], dict[str, tuple[str, str]]]:
    questions: dict[str, dict[str, Any]] = {}
    route_question_map: dict[str, tuple[str, str]] = {}
    for question_id, criteria in CHOICE_QUESTIONS.items():
        instructions = {
            "purchase_purpose": "Which purchase purpose is best supported by the conversation?",
            "household_composition": "Which household composition is established by the conversation?",
            "household_size": "Which household-size category is established by the conversation?",
            "buyer_signal": "What buyer signal does the latest customer message convey in context?",
            "response_stance": "What stance does the latest customer message express in context?",
            "intent_level": "Which intent level is best supported by the full conversation?",
            "sales_move": "Which primary sales move best fits the current turn?",
            "next_action": "Which next action is most appropriate for the current turn?",
            "runtime_action": "Which runtime action best fits the current turn?",
        }[question_id]
        questions[question_id] = {
            "type": "choice",
            "instructions": instructions,
            "criteria": criteria,
        }
    questions["should_give_space"] = {
        "type": "noul",
        "instructions": "Should the next response give the customer space without another sales question or pitch?",
    }
    for category, resources in (("knowledge", KNOWLEDGE_RESOURCES), ("skill", SKILL_RESOURCES)):
        for resource in resources:
            question_id = category + "_" + re.sub(r"[^a-zA-Z0-9]+", "_", resource).strip("_")
            questions[question_id] = {
                "type": "noul",
                "instructions": f"Is {resource} relevant to handling the current customer turn?",
            }
            route_question_map[question_id] = (category, resource)
    return questions, route_question_map


def purpose_summary(relative_path: str) -> str:
    text = (ROOT / relative_path).read_text(encoding="utf-8")
    section = text.split("## Purpose", 1)[1].split("\n## ", 1)[0] if "## Purpose" in text else text
    lines = [re.sub(r"\s+", " ", line.strip(" #\t")) for line in section.splitlines()]
    summary = " ".join(line for line in lines if line and not line.startswith("```"))
    return summary[:420]


def resource_catalog() -> dict[str, dict[str, str]]:
    return {
        "knowledge": {path: purpose_summary(path) for path in KNOWLEDGE_RESOURCES},
        "skills": {path: purpose_summary(path) for path in SKILL_RESOURCES},
    }


def api_result(state: dict[str, Any], questions: dict[str, dict[str, Any]], account: str, token: str, secrets: tuple[str, ...]) -> dict[str, Any]:
    result = cloudflare_request(
        CLEF_URL.format(account=account),
        token,
        secrets,
        {"model": MODEL_SELECTOR, "state": state, "questions": questions},
    )
    result["endpoint_model_id"] = MODEL_ID
    if result.get("response_model") in ("clef", MODEL_ID):
        result["actual_model_id"] = MODEL_ID
    return result


def choice(result: dict[str, Any], question_id: str) -> Any:
    answer = (result.get("answers") or {}).get(question_id)
    if isinstance(answer, dict):
        return answer.get("choice", answer.get("answer", answer.get("value")))
    return answer


def customer_transcript_from_pea008() -> tuple[list[dict[str, str]], str | None]:
    transcript = json.loads(PEA008_TRANSCRIPT.read_text(encoding="utf-8"))
    messages = [
        {"speaker": item.get("speaker", "customer"), "text": item.get("message", "")}
        for item in transcript.get("transcript", [])
        if item.get("speaker") == "customer" and item.get("message")
    ]
    scenario = json.loads(PEA008_SCENARIO.read_text(encoding="utf-8"))
    reference = str((scenario.get("buyer") or {}).get("initial_intent", "")).upper() or None
    return messages, reference


def run_sales_core_v2_family(secrets: tuple[str, ...]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from app.agent import SalesAgent
    from app.config import get_config
    from app.eval_sales import SCENARIOS
    from app.provider import PROFILE_FIELDS
    from app.knowledge import retrieve

    config = get_config()
    agent = SalesAgent(config)
    messages = SCENARIOS["family"]
    profile: dict[str, Any] = {"purchase_purpose": "UNKNOWN"}
    history: list[dict[str, str]] = []
    turn_results: list[dict[str, Any]] = []
    v2_info = {"model": config["model"], "reasoning": config["reasoning"], "provider": config["provider"]}
    for index, customer_message in enumerate(messages, start=1):
        history.append({"direction": "INBOUND", "body": customer_message})
        turn_context = [
            {"speaker": "customer" if item["direction"] == "INBOUND" else "assistant", "text": item["body"]}
            for item in history
        ]
        retrieved = retrieve(customer_message, profile)
        started = time.perf_counter()
        entry: dict[str, Any] = {
            "turn": index,
            "customer_message": customer_message,
            "transcript_before_decision": turn_context,
            "knowledge_routes": [item.get("path") for item in retrieved if isinstance(item, dict)],
            "probabilities": None,
            "errors": [],
        }
        try:
            decision, usage = agent.decide(customer_message, profile, history, [])
            entry.update({
                "latency_ms": round((time.perf_counter() - started) * 1000),
                "buyer_signal": decision.get("buyer_signal"),
                "sales_move": decision.get("sales_move"),
                "action": decision.get("action"),
                "reply": decision.get("reply"),
                "lead_updates": decision.get("lead_updates", {}),
                "usage": usage,
            })
            updates = {
                key: value for key, value in decision.get("lead_updates", {}).items()
                if key in PROFILE_FIELDS and value is not None
            }
            profile.update(updates)
            if decision.get("reply"):
                history.append({"direction": "OUTBOUND", "body": decision["reply"]})
            entry["lead_profile_after"] = profile.copy()
        except Exception as error:  # preserve per-turn failures for the comparison report
            entry.update({
                "latency_ms": round((time.perf_counter() - started) * 1000),
                "errors": [{"type": type(error).__name__, "message": redact(error, secrets)}],
            })
            entry["lead_profile_after"] = profile.copy()
        turn_results.append(entry)
    return v2_info, turn_results


def state_for_transcript(transcript: list[dict[str, str]], catalog: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {"conversation": transcript, "available_resources": catalog}


def run_clef_turn(
    transcript: list[dict[str, str]],
    catalog: dict[str, dict[str, str]],
    questions: dict[str, dict[str, Any]],
    route_question_map: dict[str, tuple[str, str]],
    account: str,
    token: str,
    secrets: tuple[str, ...],
) -> dict[str, Any]:
    result = api_result(state_for_transcript(transcript, catalog), questions, account, token, secrets)
    routed: dict[str, list[dict[str, Any]]] = {"knowledge": [], "skills": []}
    answers = result.get("answers") or {}
    for question_id, (category, resource) in route_question_map.items():
        answer = answers.get(question_id)
        if isinstance(answer, dict):
            yes_probability = answer.get("noul", answer.get("probability_yes"))
        else:
            yes_probability = answer
        routed["knowledge" if category == "knowledge" else "skills"].append({
            "path": resource,
            "probability_relevant": yes_probability,
        })
    result["routes"] = routed
    result["top_choices"] = {
        key: choice(result, key)
        for key in CHOICE_QUESTIONS
    }
    return result


def v2_comparison(clef: dict[str, Any], v2: dict[str, Any]) -> dict[str, Any]:
    updates = v2.get("lead_updates") or {}
    profile = v2.get("lead_profile_after") or {}
    return {
        "purchase_purpose": {"clef": clef.get("top_choices", {}).get("purchase_purpose"), "sales_core_v2": profile.get("purchase_purpose") or updates.get("purchase_purpose")},
        "buyer_signal": {"clef": clef.get("top_choices", {}).get("buyer_signal"), "sales_core_v2": v2.get("buyer_signal")},
        "intent_level": {"clef": clef.get("top_choices", {}).get("intent_level"), "sales_core_v2": profile.get("intent_level") or updates.get("intent_level")},
        "sales_move": {"clef": clef.get("top_choices", {}).get("sales_move"), "sales_core_v2": v2.get("sales_move")},
        "runtime_action": {"clef": clef.get("top_choices", {}).get("runtime_action"), "sales_core_v2": v2.get("action")},
        "knowledge_routes": {"clef": clef.get("routes", {}).get("knowledge"), "sales_core_v2": v2.get("knowledge_routes")},
        "skill_routes": {"clef": clef.get("routes", {}).get("skills"), "sales_core_v2": "Sales Core V2 applies its agent/skill context through the runtime prompt."},
    }


def main() -> int:
    credentials = load_env(ROOT / ".env")
    account = credentials.get("CLOUDFLARE_ACCOUNT_ID", "")
    token = credentials.get("CLOUDFLARE_API_TOKEN", "")
    openai_key = credentials.get("OPENAI_API_KEY", "")
    secrets = (token, openai_key)
    report: dict[str, Any] = {
        "requested_model_id": MODEL_ID,
        "model_selector": MODEL_SELECTOR,
        "connectivity": {},
        "sales_core_v2": {},
        "clef_decisions": {},
    }
    if not re.fullmatch(r"[0-9a-fA-F]{32}", account) or not token:
        report["connectivity"] = {"success": False, "errors": [{"message": "Missing or invalid Cloudflare credentials in the local .env."}]}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    verify = cloudflare_request(
        "https://api.cloudflare.com/client/v4/user/tokens/verify", token, secrets
    )
    active = (
        verify.get("success")
        and verify.get("token_status") == "active"
    )
    verify_result = verify
    verify_result["active"] = bool(active)
    if not active:
        report["connectivity"] = {"token_verification": verify_result, "success": False}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    probe_questions = {
        "probe_state": {
            "type": "choice",
            "instructions": "Which status description best fits the supplied record?",
            "criteria": {
                "responding": "The record contains a successful service response.",
                "unavailable": "The record contains a service failure.",
            },
        }
    }
    probe = api_result(
        {"record": "Cloudflare Workers AI Clef connectivity probe; request accepted."},
        probe_questions,
        account,
        token,
        secrets,
    )
    probe["success"] = bool(
        probe.get("success") and probe.get("response_model") in ("clef", MODEL_ID)
    )
    report["connectivity"] = {"token_verification": verify_result, "clef_probe": probe, "success": probe["success"]}
    if not probe["success"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    catalog = resource_catalog()
    questions, route_question_map = clef_questions()
    v2_info: dict[str, Any] = {}
    v2_turns: list[dict[str, Any]] = []
    try:
        v2_info, v2_turns = run_sales_core_v2_family(secrets)
    except Exception as error:
        v2_info = {"errors": [{"type": type(error).__name__, "message": redact(error, secrets)}]}
    report["sales_core_v2"] = {"config": v2_info, "turns": v2_turns}

    clef_scenarios: list[dict[str, Any]] = []
    pea_messages, pea_reference_intent = customer_transcript_from_pea008()
    pea_state = [{"speaker": item["speaker"], "text": item["text"]} for item in pea_messages]
    pea_result = run_clef_turn(pea_state, catalog, questions, route_question_map, account, token, secrets)
    clef_scenarios.append({
        "scenario": "PEA-008 single-turn historical simulator failure",
        "historical_failure": "The saved simulator report ended before an AI reply after HTTP 429.",
        "reference_initial_intent_not_sent_to_clef": pea_reference_intent,
        "turns": [{"turn": 1, "transcript": pea_state, "decision": pea_result}],
    })

    family_turns: list[dict[str, Any]] = []
    for v2_turn in v2_turns:
        transcript = v2_turn.get("transcript_before_decision", [])
        decision = run_clef_turn(transcript, catalog, questions, route_question_map, account, token, secrets)
        family_turns.append({
            "turn": v2_turn["turn"],
            "customer_message": v2_turn["customer_message"],
            "clef_decision": decision,
            "sales_core_v2": v2_turn,
            "comparison": v2_comparison(decision, v2_turn),
        })
    clef_scenarios.append({
        "scenario": "Sales Core V2 family multi-turn evaluation",
        "source": "app/eval_sales.py SCENARIOS['family']",
        "turns": family_turns,
    })
    report["clef_decisions"] = {
        "questions_per_decision": len(questions),
        "resource_route_questions": len(route_question_map),
        "scenarios": clef_scenarios,
    }
    api_calls_succeeded = all(
        turn.get("decision", turn.get("clef_decision", {})).get("success") is True
        for scenario in clef_scenarios
        for turn in scenario.get("turns", [])
    )
    report["api_decision_calls_succeeded"] = api_calls_succeeded
    # API success is transport evidence, not evidence that the classifications are good.
    # Leave quality as reviewable output rather than silently treating V2 as ground truth.
    report["decision_quality_status"] = "REQUIRES_REVIEW" if api_calls_succeeded else "NOT_EVALUABLE_API_ERRORS"
    report["decision_quality_passed"] = None
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if api_calls_succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
