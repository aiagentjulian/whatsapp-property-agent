"""Offline-from-WhatsApp, real-model sales conversation evaluation.

Runs against the OpenAI API with an in-memory customer profile and messages.
Never sends WhatsApp messages, writes production SQLite or touches Google Sheets.
This is a qualitative test harness, not an automatic proof of sales quality.
"""
import argparse
import json

from .agent import SalesAgent
from .config import get_config
from .provider import PROFILE_FIELDS


SCENARIOS = {
    "family": [
        "Hi, may I have more info about this project?",
        "own stay",
        "with family",
        "4 in total",
        "yes guess so",
        "oh ok",
    ],
    "overload": [
        "Hi may I have more info about this Project",
        "Too much information. I need some time to digest all that.",
    ],
    "commercial": [
        "Can you tell me the maintenance fee, and what is included?",
        "What is the price after rebate?",
    ],
    "hard_mismatch": [
        "We need a four-bedroom unit. Must have 4 bedrooms.",
        "Three bedrooms definitely cannot work for us.",
    ],
    "viewing": [
        "I am buying for own stay. Can I visit the show unit this Saturday?",
        "Can you confirm the viewing?",
    ],
    "returning": [
        "Hi, could you tell me about the 3-bedroom layout?",
        "Thanks, I will check with my wife first.",
        "I'm back. About the room size we discussed, could you explain that again?",
    ],
}
QUALITY_CRITERIA = (
    "answers the latest request instead of following a checklist",
    "avoids a brochure-style information dump on general enquiry",
    "distinguishes neutral acknowledgement from a strong buying signal",
    "does not repeat previously pitched benefits without reason",
    "does not claim nonexistent four-bedroom units or invented facts",
    "acknowledges overload and gives the customer room",
    "responds to viewing interest without promising an unverified booking",
    "maintains a natural, commercially helpful Malaysian WhatsApp conversation",
)


def run_scenario(agent, name):
    history = []
    profile = {"purchase_purpose": "UNKNOWN"}
    turns = []
    for customer in SCENARIOS[name]:
        history.append({"direction": "INBOUND", "body": customer})
        decision, usage = agent.decide(customer, profile, history, [])
        turns.append({"customer": customer, "buyer_signal": decision["buyer_signal"],
                      "sales_move": decision["sales_move"], "action": decision["action"],
                      "reply": decision["reply"], "usage": usage})
        updates = {key: value for key, value in decision["lead_updates"].items()
                   if key in PROFILE_FIELDS and value is not None}
        profile.update(updates)
        if decision["reply"]:
            history.append({"direction": "OUTBOUND", "body": decision["reply"]})
        if decision["action"] in ("MANDATORY_HANDOFF", "APPOINTMENT_HANDOFF"):
            break
    return {"scenario": name, "turns": turns}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run real-Luna sales dialogue eval without WhatsApp or CRM")
    parser.add_argument("--scenario", choices=("all", *SCENARIOS), default="all")
    args = parser.parse_args(argv)
    config = get_config()
    if not config["api_key"]:
        parser.error("OPENAI_API_KEY is required for real-model validation; no mock fallback")
    agent = SalesAgent(config)
    names = SCENARIOS if args.scenario == "all" else (args.scenario,)
    report = {"model": config["model"], "reasoning": config["reasoning"],
              "quality_review_criteria": QUALITY_CRITERIA, "results": []}
    for name in names:
        report["results"].append(run_scenario(agent, name))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
