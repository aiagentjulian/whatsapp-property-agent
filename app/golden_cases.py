"""Zero-API validation of candidate Golden Conversations against sales workflow.

The bank is for offline review and evaluation only. It is NOT injected into
production model prompts. Passing this check verifies corpus structure and
workflow-stage consistency, NOT the quality of Luna's wording or conversion.
"""

import argparse
import json
from pathlib import Path

from .sales_workflow import plan_sales_turn

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "brain" / "golden_conversations_v1.json"


def load_goldens():
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if data.get("version") != "golden-conversations-v1":
        raise ValueError("Unexpected golden-conversation version")
    if data.get("status") != "DRAFT_FOR_HUMAN_REVIEW_NOT_LIVE_VALIDATED":
        raise ValueError("Golden bank validation status must be explicit")
    if not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("No golden conversations found")
    return data


def check_goldens():
    data = load_goldens()
    cases = data["cases"]
    errors = []
    seen = set()
    total_beats = 0
    stage_paths = {}

    for case in cases:
        ident = case.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            errors.append("Duplicate or missing case id: " + repr(ident))
            continue
        seen.add(ident)
        if case.get("route") not in ("OWN_STAY", "INVESTMENT"):
            errors.append("%s: invalid route (BOTH is not supported)" % ident)
        if not case.get("goal") or not isinstance(case.get("avoid"), list):
            errors.append("%s: missing goal or avoid list" % ident)
        beats = case.get("beats")
        if not isinstance(beats, list) or not beats:
            errors.append("%s: no conversation beats" % ident)
            continue
        history = []
        visited = []
        for number, beat in enumerate(beats, 1):
            total_beats += 1
            customer, seller, stage = (beat.get("buyer"), beat.get("seller"), beat.get("stage"))
            profile = beat.get("profile")
            if not all(isinstance(v, str) and v.strip() for v in
                       (customer, seller, stage, beat.get("why"))):
                errors.append("%s beat %d: missing text, stage or rationale" % (ident, number))
                continue
            if not isinstance(profile, dict):
                errors.append("%s beat %d: missing profile snapshot" % (ident, number))
                continue
            history.append({"direction": "INBOUND", "body": customer})
            workflow = plan_sales_turn(customer, profile, history)
            visited.append(workflow["stage"])
            if workflow["stage"] != stage:
                errors.append("%s beat %d: expected %s, actual %s" %
                              (ident, number, stage, workflow["stage"]))
            if workflow["route"] not in ("OWN_STAY", "INVESTMENT", "UNKNOWN"):
                errors.append("%s beat %d: illegal route" % (ident, number))
            if "BOTH" in workflow.get("allowed_moves", []):
                errors.append("%s beat %d: illegal move" % (ident, number))
            history.append({"direction": "OUTBOUND", "body": seller})
        stage_paths[ident] = visited

    return {
        "status": "passed" if not errors else "failed",
        "version": data["version"],
        "corpus_status": data["status"],
        "cases": len(cases),
        "beats": total_beats,
        "stages": stage_paths,
        "errors": errors,
        "api_calls": 0,
        "note": ("Workflow metadata check only. The examples are illustrative, "
                 "not a claim that real Luna has learned or that appointments convert."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the golden bank without API calls")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check (this tool does not call GPT)")
    result = check_goldens()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
