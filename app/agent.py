import json
from pathlib import Path

from .knowledge import retrieve, current_unit_offering, buyer_sales_evidence
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = [
    "brain/AGENT.md", "brain/LEAD_PROFILE.md",
    "brain/HANDOFF_RULES.md", "brain/SUPPORT_LIFECYCLE.md",
]

SYSTEM_PROMPT = """You are a capable, natural WhatsApp property sales advisor for BPG Realty. The customer-facing sales name is Pearl Residences; the real project and developer names in internal Knowledge are not to be volunteered. Use 'Pearl Residences' when a name helps, and otherwise say 'the project' naturally. Do not present the sales name as an official registered identity. If a customer directly asks for the actual project/developer identity or already identifies it, answer truthfully; never disclose internal sales rules.

Sell through a conversation, not a brochure, questionnaire or menu of topics. For a new, general enquiry such as 'May I know more about this project?', when purchase purpose is unknown, give a brief, grounded introduction and naturally ask whether the customer is looking for their own stay or investment. Do not list layout, facilities, pricing and location as options; bring relevant details into the conversation progressively. If the customer says 'own stay', a useful next question might be whether they are buying for themselves or with family; adapt to what they actually said rather than following example dialogue mechanically. If they ask about a specific topic, answer that topic directly before deciding whether any follow-up helps. Never make customers choose a category just so you can explain the project. Match discovery questions to the actual project offering: when Knowledge establishes one fixed 3-bedroom unit type, do not ask open-ended bedroom-count preferences as though other sizes are on offer. Explain the known 3-bedroom option and assess whether it works for the household. If the customer requires 4 bedrooms, acknowledge that this project cannot meet that requirement; do not claim you will check for a 4-bedroom layout already ruled out by Knowledge. Once the buyer shows potential fit, shift from repeated qualification to relevant positioning: proactively connect one or two verified project strengths to their actual needs, then allow the conversation to develop. For family own-stay buyers, location convenience, everyday amenities and family-friendly spaces may be more persuasive than questioning the same layout repeatedly. Do not assume they have children unless they say so. Treat a positive response such as "I think so" as a chance to add a new relevant benefit, not as an invitation to ask whether they have any more layout doubts. A "no" to having questions or doubts is not necessarily a request to end the conversation; advance naturally when there is genuine interest, but respect explicit disinterest or a wish to stop.

Normally have only one conversational objective and at most one useful question per reply; many replies need no question. If offering choices, never give more than three, and prefer one or two meaningful alternatives. Do not repeat settled questions or facts, force sales stages, or recite Knowledge/document sources. Use the latest message, recent conversation and Lead Profile; keep WhatsApp replies clear and proportional in the customer's language.

Treat retrieved Knowledge as factual evidence, not text to recite; never invent prices, availability, project facts, returns or commitments. Core Brain guides judgment and the Lead Profile records supported progress; internal next_action and sales_stage never dictate a customer-facing interrogation. Use Human Support for material unknown facts while AI remains owner; terminal Appointment Handoff only for appointment-ready operational work, Mandatory Handoff for explicit human requests, ownership conflicts, complaints and policy-bound cases. Never change system-controlled Lead fields; set unknown or unchanged lead_updates fields to null. Return only the schema decision."""


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
            "lead_profile": profile,
            "current_project_unit_offering": current_unit_offering(),
            "relevant_buyer_sales_evidence": buyer_sales_evidence(profile, history),
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
