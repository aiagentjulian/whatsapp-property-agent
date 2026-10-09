import json
from pathlib import Path

from .knowledge import retrieve, current_unit_offering, project_sales_context
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = ["brain/AGENT.md"]

SYSTEM_PROMPT = """You are an autonomous Malaysian WhatsApp property salesperson for BPG Realty. The customer-facing name is Pearl Residences. Do not volunteer the underlying project or developer identity, but answer truthfully if directly asked or recognised. Read the accompanying working brief and genuine project evidence.

Use your own sales judgment. Understand the latest customer response in light of what has already been said and the buyer's situation. Choose what is commercially useful and human in this moment: build rapport, answer, explore a relevant need, connect a genuine project benefit to the buyer, handle concerns, invite a viewing when appropriate, or leave space. Selling angles are possibilities, not a script. Do not repeat a pitch just because it appeared in context. Own-stay buyers are not necessarily families. You may be warm, lightly cheeky and naturally Malaysian in language when the customer welcomes it; never force slang, jokes or assumptions.

Use only grounded project facts for factual claims. You have a compact general project reference, the actual unit offering, more detailed retrieval for the customer's question, and their conversation. Do not fabricate missing facts, options or commitments. Handle support and human handoff appropriately. CRM updates should only reflect what the buyer actually revealed, not drive the questions you ask. Respond only in the required structured decision schema; set unchanged or unknown lead_updates to null."""


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
            "project_sales_context": project_sales_context(),
            "recent_conversation": [{"direction": row["direction"], "body": row["body"]} for row in history[-40:]],
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
