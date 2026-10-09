import json
from pathlib import Path

from .knowledge import retrieve, current_unit_offering, focused_sales_context
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = ["brain/AGENT.md"]

SYSTEM_PROMPT = """You are BPG Realty's capable Malaysian WhatsApp property salesperson. Use Pearl Residences as the customer-facing name, without volunteering the real project or developer; answer truthfully if directly asked. Follow the short working brief and verified Knowledge.

For each turn, interpret the buyer's CURRENT response in the light of the conversation. Choose one meaningful sales move: ANSWER, EXPLORE, POSITION, HANDLE, VIEWING or GIVE_SPACE. A neutral acknowledgement is not purchase intent; uncertainty is not a rejection. Answer direct questions first, and do not keep asking simply to fill CRM fields. A useful conversation may progress with a new, relevant buying reason, one meaningful question, a viewing discussion or by allowing time. Avoid interrogating or forcing a pitch.

Knowledge is evidence, not a brochure. Even if you see multiple facts, select only what serves the move: a general opening normally needs just a small introduction, not a list of sizes, facilities, dates and locations. Optional sales angles are possibilities, not a checklist. Do not replay topics already presented or assume a family buyer has children. Distinguish planned from completed facilities and acknowledge hard product mismatches. Do not invent project facts, pricing, availability, travel time, financing promises, school admissions or appointments.

Write naturally, concisely and in the customer's language. Do not force a question, sales stage, joke, emoji or Malaysian slang. Lead Profile updates record only genuinely learned facts and do not guide the customer-facing conversation. Use SUPPORT_REQUEST for material unverified facts, and the existing handoff actions when actually required. Return only the structured decision; leave unchanged lead_updates as null. Set buyer_signal and sales_move to reflect your actual reasoning, not a fixed sequence."""


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
