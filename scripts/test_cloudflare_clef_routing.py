#!/usr/bin/env python3
"""Small real-Clef routing retest against recorded normal V2 conversations."""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "@cf/cloudflare/clef"
MODEL_SELECTOR = "clef"
KNOWLEDGE_RESOURCES = (
    "knowledge/project/pearlmont/01_facts/building-and-access.md",
    "knowledge/project/pearlmont/01_facts/carpark-and-utility-room.md",
    "knowledge/project/pearlmont/01_facts/clubhouse-and-pay-per-use.md",
    "knowledge/project/pearlmont/01_facts/commercial-component.md",
    "knowledge/project/pearlmont/01_facts/developer-and-track-record.md",
    "knowledge/project/pearlmont/01_facts/facilities-and-quality.md",
    "knowledge/project/pearlmont/01_facts/green-building-and-sustainability.md",
    "knowledge/project/pearlmont/01_facts/location-and-connectivity.md",
    "knowledge/project/pearlmont/01_facts/maintenance-and-management.md",
    "knowledge/project/pearlmont/01_facts/orientation-and-view.md",
    "knowledge/project/pearlmont/01_facts/overview.md",
    "knowledge/project/pearlmont/01_facts/parking-access-and-security.md",
    "knowledge/project/pearlmont/01_facts/project-timeline-and-completion.md",
    "knowledge/project/pearlmont/01_facts/risks-and-sensitive-faq.md",
    "knowledge/project/pearlmont/01_facts/school-access-and-family.md",
    "knowledge/project/pearlmont/01_facts/specifications-and-finishes.md",
    "knowledge/project/pearlmont/01_facts/unit-and-layout.md",
    "knowledge/project/pearlmont/01_facts/vertical-school-and-commercial.md",
    "knowledge/project/pearlmont/02_commercial/financing-and-booking.md",
    "knowledge/project/pearlmont/02_commercial/lppsa.md",
    "knowledge/project/pearlmont/02_commercial/panel-financiers-and-legal.md",
    "knowledge/project/pearlmont/02_commercial/pricing.md",
    "knowledge/project/pearlmont/02_commercial/sales-package.md",
    "knowledge/project/pearlmont/03_sales/usp-map.md",
)
CHOICES = {
    "buyer_signal": {
        "QUESTION": "The customer asks for information or clarification.",
        "POSITIVE": "The customer expresses a clear positive buying signal.",
        "NEUTRAL": "The customer gives a neutral acknowledgement.",
        "OBJECTION": "The customer raises a concern or blocker.",
        "DISENGAGED": "The customer signals they want to stop or disengage.",
        "UNKNOWN": "The signal is unclear.",
    },
    "purchase_intent": {
        "OWN_STAY": "The customer is considering the property for their own residence.",
        "INVESTMENT": "The customer is considering it primarily as an investment.",
        "BOTH": "The customer has expressed both purposes.",
        "EXPLORING": "The customer is exploring without a clear purchase purpose.",
        "UNKNOWN": "The conversation does not establish a purpose.",
    },
    "sales_move": {
        "ANSWER": "Answer a direct question with supported information.",
        "EXPLORE": "Ask one useful question about an unresolved need.",
        "POSITION": "Connect a verified benefit to the customer's needs.",
        "HANDLE": "Address a concern or uncertainty.",
        "VIEWING": "Discuss viewing when the conversation supports it.",
        "GIVE_SPACE": "Allow space without another pitch or question.",
    },
    "runtime_action": {
        "REPLY": "Continue with a normal customer-facing response.",
        "SUPPORT_REQUEST": "Request verification for a material unavailable fact.",
        "APPOINTMENT_HANDOFF": "Pass an appointment request to the scheduling owner.",
        "MANDATORY_HANDOFF": "Transfer the conversation to a human owner when required.",
    },
}
INSTRUCTIONS = {
    "buyer_signal": "What buyer signal does the latest customer message convey in context?",
    "purchase_intent": "Which purchase purpose is supported by the conversation so far?",
    "sales_move": "Which primary sales move best fits this turn?",
    "runtime_action": "Which runtime action best fits this turn?",
}


def read_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#") or "=" not in item:
            continue
        key, value = item.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def resource_catalog() -> dict[str, str]:
    catalog = {}
    for relative in KNOWLEDGE_RESOURCES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Current Knowledge resource is missing: {relative}")
        text = path.read_text(encoding="utf-8")
        purpose = text.split("## Purpose", 1)[-1].split("\n## ", 1)[0]
        summary = " ".join(re.sub(r"\s+", " ", line.strip(" #\t")) for line in purpose.splitlines())
        catalog[relative] = summary[:420]
    return catalog


def question_catalog(resources: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    questions = {
        key: {"type": "choice", "instructions": INSTRUCTIONS[key], "criteria": criteria}
        for key, criteria in CHOICES.items()
    }
    questions["should_give_space"] = {
        "type": "noul",
        "instructions": "Should the next response give the customer space without another pitch or question?",
    }
    route_map = {}
    for path in resources:
        key = "knowledge_" + re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_")
        questions[key] = {
            "type": "noul",
            "instructions": f"Is the customer-facing Knowledge file {path} relevant to the current turn?",
        }
        route_map[key] = path
    return questions, route_map


def request_clef(account: str, token: str, state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL_ID}"
    payload = json.dumps({"model": MODEL_SELECTOR, "state": state, "questions": questions}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            status, body = response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except (ValueError, OSError):
            body = {}
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"http_status": None, "latency_ms": round((time.perf_counter() - started) * 1000),
                "success": False, "error": {"type": type(exc).__name__, "message": str(exc)[:500]}}
    result = body.get("result") or {}
    return {
        "http_status": status,
        "success": status == 200 and body.get("success") is True,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "endpoint_model_id": MODEL_ID,
        "model_selector": MODEL_SELECTOR,
        "response_model": result.get("model"),
        "answers": result.get("answers") or {},
        "usage": result.get("usage") or {},
        "errors": body.get("errors") or [],
    }


def before_customer_turn(transcript: list[dict[str, str]], message: str) -> list[dict[str, str]]:
    for index, entry in enumerate(transcript):
        if entry.get("speaker") == "customer" and entry.get("text") == message:
            return transcript[: index + 1]
    raise ValueError("Could not match a recorded customer message in its transcript.")


def get_choice(answers: dict[str, Any], key: str) -> Any:
    value = answers.get(key)
    return value.get("choice", value.get("answer")) if isinstance(value, dict) else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="Completed normal V2/V2 Lite A/B report JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output path for the Clef comparison JSON")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--dashboard-neurons-before", type=float)
    parser.add_argument("--dashboard-neurons-after", type=float)
    parser.add_argument("--quota-checked-at-utc")
    args = parser.parse_args()
    read_env(args.env_file)
    account, token = os.getenv("CLOUDFLARE_ACCOUNT_ID", ""), os.getenv("CLOUDFLARE_API_TOKEN", "")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", account) or not token:
        raise SystemExit("Missing or invalid Cloudflare credentials; no inference request made.")

    source = json.loads(args.report.read_text(encoding="utf-8"))
    if source.get("status") != "complete":
        raise SystemExit("The paired sales evaluation must be complete before Clef comparison.")
    resources = resource_catalog()
    questions, route_map = question_catalog(resources)
    by_case = {(row.get("scenario_id"), row.get("arm")): row for row in source.get("dialogues", [])}
    cases = (
        ("E14-price-after-rebate", "价格询问"),
        ("E13-maintenance-fee", "管理费询问"),
        ("E15-facility-overload", "家庭设施询问"),
    )
    report: dict[str, Any] = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_model_id": MODEL_ID,
        "model_selector": MODEL_SELECTOR,
        "source_run_id": source.get("run_id"),
        "source_luna_arm": "A_V2",
        "resource_catalog": resources,
        "questions_per_decision": len(questions),
        "quota_preflight": {
            "dashboard_neurons_used_today": args.dashboard_neurons_before,
            "daily_free_limit": 10000,
            "dashboard_observed_at_utc": args.quota_checked_at_utc,
        },
        "cases": [],
    }
    secrets = (token, os.getenv("OPENAI_API_KEY", ""))
    for scenario_id, label in cases:
        luna_row = by_case.get((scenario_id, "A_V2"))
        if not luna_row or not luna_row.get("turns"):
            raise SystemExit(f"Missing recorded V2 decision for {scenario_id}; no Clef request made.")
        luna = luna_row["turns"][0]
        transcript = before_customer_turn(luna_row["transcript"], luna["customer"])
        state = {"conversation": transcript, "available_resources": resources}
        decision = request_clef(account, token, state, questions)
        # Scrub any credential accidentally echoed by provider error text.
        for error in decision.get("errors", []):
            for secret in secrets:
                if secret and isinstance(error, dict) and isinstance(error.get("message"), str):
                    error["message"] = error["message"].replace(secret, "[REDACTED]")
        answers = decision.get("answers", {})
        routes = []
        for key, path in route_map.items():
            value = answers.get(key)
            probability = value.get("noul", value.get("probability_yes")) if isinstance(value, dict) else value
            routes.append({"path": path, "probability_relevant": probability})
        routes.sort(key=lambda row: row.get("probability_relevant") or 0, reverse=True)
        decision["top_choices"] = {key: get_choice(answers, key) for key in CHOICES}
        decision["knowledge_routes_ranked"] = routes
        luna_decision = {key: luna.get(key) for key in
                         ("buyer_signal", "sales_move", "action", "retrieved_knowledge_paths")}
        decision["luna_comparison"] = {
            "luna": luna_decision,
            "clef": {"buyer_signal": decision["top_choices"].get("buyer_signal"),
                     "sales_move": decision["top_choices"].get("sales_move"),
                     "action": decision["top_choices"].get("runtime_action")},
        }
        report["cases"].append({"scenario_id": scenario_id, "label": label, "context": transcript,
                                "luna_reply": luna.get("agent_reply"), "luna": luna_decision,
                                "clef": decision})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not decision.get("success") or decision.get("response_model") not in ("clef", MODEL_ID):
            report["status"] = "incomplete_no_retry"
            report["stop_reason"] = "Clef call failed or returned an unexpected model; further calls stopped."
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 1
    report["status"] = "complete"
    usages = [case["clef"].get("usage", {}) for case in report["cases"]]
    report["usage_summary"] = {
        "calls": len(usages),
        "neurons_reported_by_api": (
            sum(float(row.get("neurons", 0) or 0) for row in usages)
            if all("neurons" in row for row in usages) else None
        ),
        "input_tokens": sum(int(row.get("input_tokens", 0) or 0) for row in usages),
        "output_tokens": sum(int(row.get("output_tokens", 0) or 0) for row in usages),
        "mean_latency_ms": round(sum(case["clef"]["latency_ms"] for case in report["cases"]) / len(report["cases"])),
    }
    report["dashboard_neurons_after_run"] = args.dashboard_neurons_after
    if args.dashboard_neurons_before is not None and args.dashboard_neurons_after is not None:
        report["dashboard_neurons_consumed_by_run"] = max(
            0.0, args.dashboard_neurons_after - args.dashboard_neurons_before
        )
        report["estimated_cost_usd"] = round(
            max(0.0, args.dashboard_neurons_after - 10000) * 0.011 / 1000, 8
        )
    else:
        report["estimated_cost_usd"] = None
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(args.output),
                      "actual_model_ids": [case["clef"].get("response_model") for case in report["cases"]],
                      "usage": report["usage_summary"], "estimated_cost_usd": report["estimated_cost_usd"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
