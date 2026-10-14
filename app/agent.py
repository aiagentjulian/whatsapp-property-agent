import json
from pathlib import Path

from .knowledge import retrieve, current_unit_offering, focused_sales_context
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = ["brain/AGENT.md"]

SYSTEM_PROMPT = """You are BPG Realty's Malaysian WhatsApp property salesperson for Pearl Residences. Follow the accompanying Sales Brain: understand what the buyer wants, connect that need to verified advantages of this specific property, and help the buyer picture the personal benefit so genuine purchase interest can grow. Answer truthfully if asked about the actual project or developer; do not volunteer those identities unprompted.

An inbound enquiry usually carries some interest in the advertised home, but you do not know exactly what ad the buyer saw. Use the conversation and Knowledge to decide the best sales move, not a fixed questionnaire or script. Ask a question only when the answer will help you sell more relevantly, address a concern or move toward a meaningful next step. Once a useful need is known, connect it back to the home instead of pursuing unrelated lifestyle details. Do not turn each reply into a question or a parade of room measurements. Be natural, proactive and responsive; avoid hard selling when interest is not there.

Return one valid structured decision with an honest buyer_signal, sales_move and lead_updates based only on what was learned. Use verified Knowledge for claims, SUPPORT_REQUEST for missing material facts and formal handoff actions when required. Do not invent facts or actions, repeat pending checks or claim an unconfirmed booking."""


class SalesAgent:
    def __init__(self, config, provider=None):
        self.config = config
        self.provider = provider or OpenAIProvider(config)

    @staticmethod
    def context_text():
        return "\n\n".join("--- %s ---\n%s" % (path, (ROOT / path).read_text(encoding="utf-8")) for path in CONTEXT_FILES)

    def decide(self, latest_message, profile, history, support_results):
        passages = retrieve(latest_message, profile)
        user_prompt = json.dumps({
            "brain_and_skills": self.context_text(),
            "lead_profile": {key: value for key, value in profile.items()
                             if key not in ("lead_id", "phone", "owner", "ai_session_status",
                                            "next_action", "next_objective", "sales_stage", "last_progress")
                             and value not in (None, "", [], "UNKNOWN")},
            "current_project_unit_offering": current_unit_offering(),
            "focused_sales_evidence": focused_sales_context(latest_message, profile, history),
            "recent_conversation": [{"direction": row["direction"], "body": row["body"]} for row in history[-28:]],
            "latest_customer_message": latest_message,
            "relevant_project_knowledge": passages,
            "verified_support_results": support_results,
        }, ensure_ascii=False)
        decision, usage = self.provider.decide(SYSTEM_PROMPT, user_prompt)
        self.validate(decision)
        return decision, usage

    @staticmethod
    def validate(decision):
        if not isinstance(decision, dict):
            raise ValueError("Agent decision must be an object")
        action = decision.get("action")
        if action not in ("REPLY", "SUPPORT_REQUEST", "APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
            raise ValueError("Agent returned an unsupported action")
        if decision.get("sales_move") not in ("ANSWER", "EXPLORE", "POSITION", "HANDLE", "VIEWING", "GIVE_SPACE"):
            raise ValueError("Agent returned an invalid sales move")
        if decision.get("buyer_signal") not in ("QUESTION", "POSITIVE", "NEUTRAL", "OBJECTION", "DISENGAGED", "UNKNOWN"):
            raise ValueError("Agent returned an invalid buyer signal")
        if not isinstance(decision.get("reply"), str) or len(decision["reply"]) > 3000:
            raise ValueError("Agent reply is missing or exceeds 3000 characters")
        updates = decision.get("lead_updates")
        if not isinstance(updates, dict):
            raise ValueError("Agent lead_updates must be an object")
        illegal = set(updates) - set(PROFILE_FIELDS)
        if illegal:
            raise ValueError("Agent attempted to modify system-controlled or unknown fields: " + ", ".join(sorted(illegal)))
        if action == "SUPPORT_REQUEST" and not isinstance(decision.get("support_request"), dict):
            raise ValueError("SUPPORT_REQUEST requires a complete support_request")
        if action in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF") and decision.get("handoff_reason") is None:
            raise ValueError("Formal handoff requires a reason")
