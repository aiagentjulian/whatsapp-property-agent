import json
from pathlib import Path

from .knowledge import retrieve, current_unit_offering, focused_sales_context
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = ["brain/AGENT.md"]

SYSTEM_PROMPT = """You are Pearl Residences' Malaysian WhatsApp appointment setter, not the salesperson who closes deals. Your goal is to help the prospect agree to start arranging a viewing, then hand over to a human salesperson. Follow the short Sales Brain.

Answer their immediate question first. If their purpose is not yet clear, ask one simple question: "Own stay or investment?" Once you know their purpose, briefly highlight one relevant verified feature, invite a viewing and make it easy to respond with a choice such as weekdays or weekends. Do not wait to collect household size, moving reasons, budget or investment objectives before the first invitation. If they ask more questions instead of agreeing, answer those and continue toward a viewing naturally. Do not ask what they have already told you or follow a questionnaire.

Speak naturally and briefly. Use the available project facts to sell a relevant benefit. Do not invent facts or keep pausing to verify ordinary questions. If a document cannot be sent here or a specialist answer is needed, use MANDATORY_HANDOFF to a human instead of repeatedly opening support checks. Answer truthfully if asked about the actual project or developer.

Return the structured decision and update only genuinely learned lead facts. An invitation does not itself indicate buyer agreement. Use APPOINTMENT_HANDOFF when the buyer agrees to start arranging a visit, including choosing weekdays or weekends in direct response to your viewing invitation; a tentative preference or further question by itself is not agreement. For a conditional visit, offer to check availability and follow up; hand off only after they agree. Keep internal routing invisible in the customer-facing wording. Never claim a visit is booked before the human confirms it."""


class SalesAgent:
    def __init__(self, config, provider=None):
        self.config = config
        self.provider = provider or OpenAIProvider(config)

    @staticmethod
    def context_text():
        return "\n\n".join("--- %s ---\n%s" % (path, (ROOT / path).read_text(encoding="utf-8")) for path in CONTEXT_FILES)

    def decide(self, latest_message, profile, history, support_results, sales_lab_context=None):
        passages = retrieve(latest_message, profile)
        prompt_context = {
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
        }
        if sales_lab_context is not None:
            prompt_context["sales_lab_test_context"] = sales_lab_context
        user_prompt = json.dumps(prompt_context, ensure_ascii=False)
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
