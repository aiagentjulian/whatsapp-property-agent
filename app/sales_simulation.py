"""Bounded, offline-from-WhatsApp closed-loop sales simulation.

The seller is the production SalesAgent. Synthetic buyers react to the seller's
actual prior reply. All transcripts and the durable API-call ledger stay under
the ignored sales_lab/reports directory; this module never imports Runtime,
Meta, Sheets, or the production database.
"""
import argparse
import json
import os
import urllib.request
from pathlib import Path
from unittest.mock import patch

from .agent import SalesAgent
from .config import get_config, load_env_file
from .knowledge import retrieve
from .provider import PROFILE_FIELDS
from .sales_workflow import plan_sales_turn

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "sales_lab" / "reports" / "2026-10-22" / "closed-loop-v1"
GOLDEN_RUN = ROOT / "sales_lab" / "reports" / "golden-loop-v1"
MAX_CALLS = 40
BUYER_MODEL = "gpt-6-luna"

# Personas are fictional and their private motivations are sent only to the
# buyer actor, never to the selling agent.
PERSONAS = {
    "couple-own-stay": {
        "route": "OWN_STAY",
        "opening": "Hi, saw the Pearl Residences ad. My wife and I are looking around Seberang Jaya. Can share a bit more?",
        "private": "A married couple, no children. They want a practical first home near the wife's workplace. Comfortable total budget is about RM380k; they are cautious about monthly costs and do not want a hard sell. They may view if a benefit connects to commute or daily life and price is handled honestly.",
    },
    "small-family-own-stay": {
        "route": "OWN_STAY",
        "opening": "We're a family with two young kids, considering a move. How does this place work for a family, and is there a viewing this weekend?",
        "private": "A family of four, currently renting nearby. They value child-friendly outdoor space and school access, have a strict budget around RM400k, and worry that a new condo may add too many monthly costs. They are already open to viewing if the agent answers directly and does not promise unconfirmed arrangements.",
    },
    "rental-income-investor": {
        "route": "INVESTMENT",
        "opening": "Hi, I'm looking at Pearl Residences as an investment. Is it worth considering for rental income?",
        "private": "A cautious investor with one existing property. The main goal is long-term rental income, with a budget around RM350k. They worry about vacancy and will not accept invented rent or yield claims. They would consider viewing after a grounded explanation of ownership cost and location, but do not ask them to book unless interest develops.",
    },
    "capital-gain-investor": {
        "route": "INVESTMENT",
        "opening": "I'm comparing a few freehold projects for longer-term capital appreciation. What stands out here?",
        "private": "An experienced investor, 7-10 year horizon, budget up to RM420k. They prioritize tenure, location development and total holding cost, and are skeptical of guaranteed gains. A viewing is reasonable after a useful comparison point, not after generic claims.",
    },
    "holdout-commuter-couple": {
        "route": "OWN_STAY",
        "opening": "My partner and I commute to Perai and are thinking of buying our own place. Could you explain the monthly costs first?",
        "private": "A different holdout combination: couple buying for own stay, both commute to Perai, monthly cost is the main concern, combined budget around RM360k. They want maintenance charges explained as one component, not presented as their full monthly payment. They may view after the agent answers and connects a relevant verified benefit.",
    },
    "holdout-weekend-couple": {
        "route": "OWN_STAY",
        "seller_turns": 3,
        "opening": "Hi, my wife and I are considering Pearl Residences for own stay. We work around Seberang Jaya and are watching monthly costs. Can share what matters to a couple?",
        "private": "An unseen couple persona, no children, budget around RM390k, wife works around Seberang Jaya, cautious about monthly outgoings. If the seller connects a verified benefit and asks or answers usefully, explain that they would want to compare the monthly charges and general price. If the seller offers a weekend viewing after that, Saturday would suit if a slot is available. If the seller ignores the need or pushes without answering costs, remain tentative and do not volunteer a viewing request. Never disclose this hidden plan or facts unrelated to the actual reply.",
    },
}

def _request(model, reasoning, system, prompt, max_output_tokens=1400):
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for a live phase")
    payload = {
        "model": model,
        "reasoning": {"effort": reasoning},
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system}]},
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
        "text": {"format": {"type": "json_object"}},
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses", data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as response:
        result = json.loads(response.read().decode())
    if result.get("status") not in (None, "completed"):
        raise RuntimeError("Model response did not complete")
    text = result.get("output_text")
    if not text:
        text = next((block.get("text") for item in result.get("output", [])
                     for block in item.get("content", []) if block.get("type") == "output_text"), None)
    if not text:
        raise RuntimeError("Model response contained no output text")
    return json.loads(text), result.get("usage") or {}


def _save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _load_ledger(path, resume_after_judge_failure=False):
    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if ledger.get("max_calls") != MAX_CALLS:
            raise RuntimeError("The existing ledger has a different call cap")
        if ledger.get("stopped"):
            last = ledger["calls"][-1] if ledger.get("calls") else {}
            if not (resume_after_judge_failure and last.get("status") == "failed"
                    and str(last.get("purpose", "")).startswith("judge:")):
                raise RuntimeError("Experiment is stopped after an API failure; inspect ledger")
            # A failed independent judge is not retried. The caller may continue
            # seller/buyer simulation only, with the failed attempt still charged.
            ledger["stopped"] = False
            _save(path, ledger)
        return ledger
    return {"max_calls": MAX_CALLS, "calls": [], "usage": {"input_tokens": 0, "output_tokens": 0}, "stopped": False}


def _live_call(ledger_path, ledger, purpose, operation):
    if len(ledger["calls"]) >= MAX_CALLS:
        raise RuntimeError("40-call experiment budget exhausted")
    item = {"number": len(ledger["calls"]) + 1, "purpose": purpose, "status": "started"}
    ledger["calls"].append(item)
    ledger["stopped"] = True
    _save(ledger_path, ledger)  # Reserve before transport; failures consume budget.
    try:
        result, usage = operation()
    except Exception as exc:
        item.update(status="failed", error_type=type(exc).__name__)
        _save(ledger_path, ledger)
        raise RuntimeError("Call failed and is recorded; experiment stopped without retry") from None
    item.update(status="completed", usage=usage)
    for key in ("input_tokens", "output_tokens"):
        ledger["usage"][key] += int(usage.get(key, 0) or 0)
    ledger["stopped"] = False
    _save(ledger_path, ledger)
    return result, usage


def _buyer_reply(ledger_path, ledger, name, transcript, interest):
    persona = PERSONAS[name]
    system = (
        "You are role-playing one ordinary synthetic Malaysian property buyer in a private research simulation. "
        "Reply only as that buyer, briefly and naturally. Read and react specifically to the salesperson's latest actual reply. "
        "Remember prior turns. Do not repeat questions already answered. Reveal only relevant private motivations naturally; "
        "do not coach the salesperson, invent facts, or request viewing merely to help the test pass. A weak or irrelevant reply "
        "can leave you hesitant. A useful, credible personal connection may increase interest. Return JSON with customer_message "
        "(string), interest (integer 1-5), and private_note (string). The private_note is not customer-facing."
    )
    prompt = json.dumps({"private_buyer_profile": persona["private"], "interest_before": interest,
                         "conversation": transcript, "task": "Respond to the salesperson's last reply."}, ensure_ascii=False)
    return _live_call(ledger_path, ledger, "buyer:" + name,
                      lambda: _request(BUYER_MODEL, "medium", system, prompt, 700))


def _seller_turn(agent, latest, profile, history, ledger_path, ledger, label):
    workflow_before = plan_sales_turn(latest, profile, history)
    def call():
        return agent.decide(latest, profile, history, [] )
    decision, usage = _live_call(ledger_path, ledger, label, call)
    profile.update({key: value for key, value in decision["lead_updates"].items()
                    if key in PROFILE_FIELDS and value is not None})
    history.extend(({"direction": "INBOUND", "body": latest},
                    {"direction": "OUTBOUND", "body": decision["reply"]}))
    return {"customer": latest, "workflow": workflow_before,
            "decision": decision, "usage": usage}


def run_case(name, phase, run_dir, ledger_path, ledger):
    persona = PERSONAS[name]
    config = get_config()
    if config["model"] != "gpt-6-luna" or config["reasoning"] != "high":
        raise RuntimeError("Seller must use GPT-6 Luna / High")
    if phase.startswith("golden_") and config.get("golden_guidance_mode") != "on":
        raise RuntimeError("Golden Loop requires GOLDEN_GUIDANCE_MODE=on")
    agent = SalesAgent(config)
    profile = {"purchase_purpose": "UNKNOWN"}
    history = []
    transcript = []
    artifact_path = run_dir / phase / (name + ".json")
    initial_interest = current_interest = 2
    latest_customer = persona["opening"]
    seller_turns = persona.get("seller_turns", 2)
    terminal_action = None
    for turn_number in range(1, seller_turns + 1):
        seller = _seller_turn(agent, latest_customer, profile, history, ledger_path, ledger,
                              "seller:%s:%s:%d" % (phase, name, turn_number))
        transcript.append(seller)
        if seller["decision"]["action"] in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
            terminal_action = seller["decision"]["action"]
            break  # The real runtime ends AI service after a formal handoff.
        partial = {"phase": phase, "persona": name, "route": persona["route"], "model": config["model"],
                   "reasoning": config["reasoning"], "transcript": transcript,
                   "buyer_interest_before": initial_interest, "buyer_interest_after": current_interest,
                   "status": "in_progress"}
        _save(artifact_path, partial)
        if turn_number == seller_turns:
            break
        buyer, buyer_usage = _buyer_reply(ledger_path, ledger, name, transcript, current_interest)
        latest_customer = buyer.get("customer_message", "").strip()
        if not latest_customer or len(latest_customer) > 700:
            raise RuntimeError("Buyer simulator returned an invalid customer message")
        current_interest = buyer.get("interest", current_interest)
        transcript.append({"buyer_reaction": latest_customer, "buyer_interest": current_interest,
                           "buyer_private_note": buyer.get("private_note"), "usage": buyer_usage})
        partial.update(transcript=transcript, buyer_interest_after=current_interest)
        _save(artifact_path, partial)
    interest_after = current_interest
    artifact = {"phase": phase, "persona": name, "route": persona["route"], "model": config["model"],
                "reasoning": config["reasoning"], "transcript": transcript,
                "evaluation": {"status": "pending transcript review"},
                "buyer_interest_before": initial_interest, "buyer_interest_after": interest_after,
                "status": "complete", "terminal_action": terminal_action}
    _save(artifact_path, artifact)
    return artifact


def dry_run():
    checks = []
    cases = ("couple-own-stay", "small-family-own-stay", "rental-income-investor", "capital-gain-investor")
    assert len(set(PERSONAS)) == len(PERSONAS)
    assert {PERSONAS[name]["route"] for name in cases} == {"OWN_STAY", "INVESTMENT"}
    checks.append("synthetic buyer set covers couples, family, rental income, capital gain and both supported routes")
    assert all("BOTH" not in persona["route"] for persona in PERSONAS.values())
    checks.append("no BOTH route is defined")
    for message, expected in (("Hi, saw the property ad. Can share more details?", "PURPOSE"),
                              ("Own stay.", "HOUSEHOLD"), ("Investment.", "INVESTMENT_OBJECTIVE"),
                              ("I want to visit the show unit this Saturday.", "VIEWING")):
        history = [{"direction": "INBOUND", "body": message}]
        plan = plan_sales_turn(message, {"purchase_purpose": "UNKNOWN"}, history)
        assert plan["stage"] == expected, (message, plan["stage"], expected)
    checks.append("workflow stage progression covers purpose, household, investment goal and explicit viewing signal")
    query = retrieve("Our family has two kids and wants a nearby school and outdoor space.")
    assert query
    checks.append("family evidence lookup returns project knowledge")
    captured = {}

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data.decode())
        assert payload["model"] == "gpt-6-luna"
        assert payload["reasoning"]["effort"] == "high"
        user_context = json.loads(payload["input"][1]["content"][0]["text"])
        assert user_context["sales_workflow"]["stage"] == "PURPOSE"
        assert "lead_profile" in user_context and "relevant_project_knowledge" in user_context
        assert user_context["golden_sales_examples"]["examples"]
        assert len(user_context["golden_sales_examples"]["examples"]) <= 2
        captured["payload"] = payload
        response = {"status": "completed", "output_text": json.dumps({
            "action": "REPLY", "sales_move": "ANSWER", "buyer_signal": "QUESTION",
            "reply": "Fake transport validation only.",
            "lead_updates": {key: None for key in PROFILE_FIELDS},
            "support_request": None, "handoff_reason": None, "handoff_details": None,
        }), "usage": {}}

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *exc): return False
            def read(self): return json.dumps(response).encode()
        return FakeResponse()

    fake_config = {"model": "gpt-6-luna", "reasoning": "high", "api_key": "fake"}
    with patch("app.provider.urllib.request.urlopen", fake_urlopen):
        decision, _ = SalesAgent(fake_config).decide(
            "Hi, saw the property ad. Can share more details?", {"purchase_purpose": "UNKNOWN"},
            [{"direction": "INBOUND", "body": "Hi, saw the property ad. Can share more details?"}], [])
    assert decision["reply"] == "Fake transport validation only." and captured
    checks.append("real SalesAgent entrypoint accepts a fake HTTP response; no network call was made")
    from .golden_cases import check_goldens
    golden_result = check_goldens()
    assert golden_result["status"] == "passed", golden_result["errors"]
    assert captured["payload"]["input"][1]["content"][0]["text"]
    checks.append("golden bank has matching workflow stages and passes zero-API validation")
    return {"status": "passed", "api_calls": 0, "checks": checks,
            "phase_call_upper_bound": {"baseline": 12, "candidate": 12, "holdout": 5,
                                       "golden_initial": 12, "golden_retest": 12,
                                       "golden_holdout": 8},
            "hard_call_cap": MAX_CALLS, "whatsapp": "not used", "crm_sheets_database": "not used"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--phase", choices=(
        "baseline", "candidate", "holdout",
        "golden_initial", "golden_retest", "golden_holdout"))
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--continue-after-judge-failure", action="store_true",
                        help="continue other cases after a failed judge call without retrying that call")
    args = parser.parse_args(argv)
    if args.dry_run:
        if args.phase:
            parser.error("--dry-run and --phase cannot be combined")
        print(json.dumps(dry_run(), ensure_ascii=False, indent=2))
        return
    if not args.phase:
        parser.error("choose --dry-run or one explicit --phase")
    if args.env_file:
        load_env_file(args.env_file)
    if args.phase.startswith("golden_") and args.run_dir == DEFAULT_RUN:
        args.run_dir = GOLDEN_RUN
    ledger_path = args.run_dir / "api-ledger.json"
    ledger = _load_ledger(ledger_path, args.continue_after_judge_failure)
    selected = {
        "baseline": ("couple-own-stay", "small-family-own-stay", "rental-income-investor", "capital-gain-investor"),
        "candidate": ("couple-own-stay", "small-family-own-stay", "rental-income-investor", "capital-gain-investor"),
        "holdout": ("holdout-weekend-couple",),
        # Golden Loop V1: no separate old-model A/B replay. The previous
        # evaluation is the historical reference. Compare only targeted fixes
        # against initial Golden-guided cases, then unseen holdouts.
        "golden_initial": ("couple-own-stay", "small-family-own-stay",
                           "rental-income-investor", "capital-gain-investor"),
        "golden_retest": ("couple-own-stay", "small-family-own-stay",
                          "rental-income-investor", "capital-gain-investor"),
        "golden_holdout": ("holdout-weekend-couple", "holdout-commuter-couple"),
    }[args.phase]
    outputs = []
    for name in selected:
        outputs.append(run_case(name, args.phase, args.run_dir, ledger_path, ledger))
    print(json.dumps({"phase": args.phase, "cases": len(outputs), "api_calls_used": len(ledger["calls"]),
                      "api_calls_remaining": MAX_CALLS - len(ledger["calls"]), "usage": ledger["usage"],
                      "results": [{"persona": x["persona"], "buyer_interest_before": x["buyer_interest_before"],
                                  "buyer_interest_after": x["buyer_interest_after"],
                                  "status": x["status"]} for x in outputs]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
