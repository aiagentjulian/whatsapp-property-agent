#!/usr/bin/env python3
"""Replay the failed PEA-008 message against Cloudflare Workers AI.

This is an isolated API smoke test. It does not start the WhatsApp runtime or
change the production sales flow. It classifies one message and proposes local
knowledge files; it never sends a customer reply.
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


ROOT = Path(__file__).resolve().parents[1]
MODEL = "@cf/meta/llama-3.1-8b-instruct"
FIXTURE = ROOT / "simulator/reports/RUN-V16-20261007T155329Z/PEA-008.transcript.json"
SCENARIO = ROOT / "simulator/scenarios/pearlmont/PEA-008.json"
ALLOWED_INTENTS = {"LOW", "MEDIUM", "HIGH", "READY_FOR_APPOINTMENT"}
ROUTE_CATALOG = {
    "knowledge/project/pearlmont/01_facts/unit-and-layout.md": (
        "Unit configuration and layout; includes block/floor facing references, "
        "but exact available units must be checked against the current schedule."
    ),
    "knowledge/project/pearlmont/01_facts/orientation-and-view.md": (
        "Tower orientation, sea-facing stacks, view and floor bands; warns that "
        "a broad view category does not confirm a specific available unit."
    ),
    "knowledge/project/pearlmont/02_commercial/pricing.md": (
        "Original/base price structure only; not the current post-rebate customer price."
    ),
    "knowledge/project/pearlmont/02_commercial/sales-package.md": (
        "Current effective price, rebates and package applicability by unit category, "
        "floor band and car-park allocation. Use for budget and current-package questions."
    ),
    "knowledge/project/pearlmont/03_sales/unit-fit.md": (
        "Sales judgment for matching buyer priorities (view, floor, budget) to unit categories; "
        "requires verification of exact availability and current price."
    ),
}
REQUIRED_ROUTES = {
    "knowledge/project/pearlmont/01_facts/orientation-and-view.md",
    "knowledge/project/pearlmont/02_commercial/sales-package.md",
    "knowledge/project/pearlmont/03_sales/unit-fit.md",
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
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
    values.update({key: val for key, val in os.environ.items() if key in {
        "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"
    }})
    return values


def api_request(url: str, token: str, payload: dict | None = None) -> tuple[int, dict, int]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method="POST" if payload is not None else "GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status = response.status
            body = json.loads(response.read())
    except urllib.error.HTTPError as error:
        status = error.code
        try:
            body = json.loads(error.read())
        except (ValueError, OSError):
            body = {}
    except (TimeoutError, urllib.error.URLError) as error:
        print(f"API request failed: {type(error).__name__}", file=sys.stderr)
        raise SystemExit(2) from None
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    return status, body, elapsed_ms


def fixture_data() -> tuple[str, str]:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    messages = [
        item.get("message", "").strip()
        for item in fixture.get("transcript", [])
        if item.get("speaker") == "customer" and item.get("message", "").strip()
    ]
    if not messages:
        raise ValueError("PEA-008 fixture has no customer message")
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    expected = str((scenario.get("buyer") or {}).get("initial_intent", "")).upper()
    if expected not in ALLOWED_INTENTS:
        raise ValueError("PEA-008 fixture has no valid initial_intent")
    return "\n".join(messages), expected


def parse_result(value: object) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        match = re.search(r"\{.*\}", value, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
    raise ValueError("Workers AI returned no JSON classification")


def main() -> int:
    credentials = load_env(ROOT / ".env")
    account = credentials.get("CLOUDFLARE_ACCOUNT_ID", "")
    token = credentials.get("CLOUDFLARE_API_TOKEN", "")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", account):
        print("CLOUDFLARE_ACCOUNT_ID must be exactly 32 hexadecimal characters.", file=sys.stderr)
        return 2
    if not token:
        print("CLOUDFLARE_API_TOKEN is missing.", file=sys.stderr)
        return 2

    base = "https://api.cloudflare.com/client/v4"
    status, verification, _ = api_request(f"{base}/user/tokens/verify", token)
    active = (
        status == 200
        and verification.get("success")
        and (verification.get("result") or {}).get("status") == "active"
    )
    print(f"Token verification: {'active' if active else 'failed'} (HTTP {status})")
    if not active:
        codes = [str(error.get("code", "")) for error in verification.get("errors", [])]
        print("Cloudflare error codes:", ",".join(codes) or "none")
        return 1

    message, expected_intent = fixture_data()
    catalog = "\n".join(f"- {path}: {description}" for path, description in ROUTE_CATALOG.items())
    system = (
        "You are running an isolated intent and knowledge-routing test for a property-sales assistant. "
        "Follow brain/INTENT_MODEL.md: HIGH includes specific unit evaluation and questions about unit "
        "availability; READY_FOR_APPOINTMENT is for a viewing/call request, offering availability, asking "
        "how to proceed, or accumulated evidence that an appointment is the useful next step. A question "
        "asking which unit to choose is serious evaluation, but by itself is not an appointment request. "
        "Use only the supplied conversation; do not infer missing turns.\n\n"
        "Choose only relevant local knowledge paths from this catalog:\n"
        f"{catalog}\n\n"
        "For a budget constraint, include sales-package.md because it is the source for current effective "
        "price and rebates. pricing.md is supplemental base-price context, not a substitute. For a desired "
        "view/floor and unit recommendation, route to unit-fit.md, orientation-and-view.md, and "
        "unit-and-layout.md. "
        "Exact inventory is not in these files: set inventory_check_required true and do not assert availability.\n"
        "Return a JSON object only. intent must be exactly one of LOW, MEDIUM, HIGH, "
        "READY_FOR_APPOINTMENT. Include confidence (LOW/MEDIUM/HIGH), knowledge_routes "
        "(exact paths from catalog), inventory_check_required (boolean), and rationale (one sentence)."
    )
    model_path = urllib.parse.quote(MODEL, safe="@/")
    url = f"{base}/accounts/{account}/ai/run/{model_path}"
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "max_tokens": 220,
        "temperature": 0,
    }
    status, response, latency_ms = api_request(url, token, payload)
    print(f"Workers AI inference: HTTP {status}; latency_ms={latency_ms}")
    if status != 200 or not response.get("success"):
        codes = [str(error.get("code", "")) for error in response.get("errors", [])]
        print("Cloudflare error codes:", ",".join(codes) or "none")
        return 1

    try:
        result = parse_result((response.get("result") or {}).get("response"))
    except (ValueError, json.JSONDecodeError) as error:
        print(f"Classification parse failed: {error}")
        return 1
    intent = result.get("intent")
    routes = result.get("knowledge_routes") or []
    if intent not in ALLOWED_INTENTS or not isinstance(routes, list):
        print(
            "Classification failed schema validation:",
            "intent=", intent,
            "knowledge_routes_type=", type(routes).__name__,
            "fields=", json.dumps(sorted(result.keys())),
        )
        return 1
    selected = {route for route in routes if route in ROUTE_CATALOG}
    missing = sorted(REQUIRED_ROUTES - selected)
    valid = len(selected) == len(routes)
    intent_match = intent == expected_intent
    inventory_safe = result.get("inventory_check_required") is True
    print("Intent:", intent, "(fixture initial intent:", expected_intent + ")")
    print("Confidence:", result.get("confidence", "unspecified"))
    print("Knowledge routes:", json.dumps(sorted(selected)))
    print("Required routes covered:", f"{len(REQUIRED_ROUTES - set(missing))}/{len(REQUIRED_ROUTES)}")
    print("Missing required routes:", json.dumps(missing))
    print("Inventory check required:", inventory_safe)
    print("Rationale:", str(result.get("rationale", ""))[:240])
    quality_ok = intent_match and valid and not missing and inventory_safe
    print("Fixture quality check:", "pass" if quality_ok else "needs review")
    return 0 if quality_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
