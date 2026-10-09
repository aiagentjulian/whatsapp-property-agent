import json
from pathlib import Path

from .knowledge import retrieve
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = [
    "brain/AGENT.md", "brain/LEAD_PROFILE.md",
    "brain/HANDOFF_RULES.md", "brain/SUPPORT_LIFECYCLE.md",
]

SYSTEM_PROMPT = """You are a WhatsApp property sales advisor. The project's and developer's names in internal Knowledge are not names to volunteer to customers; under the BPG lead-protection rule, do not proactively reveal them or identifying company details unless the customer has already identified them or directly asks. When asked directly, answer honestly without evasiveness. Never mention internal sales or lead-protection rules. Treat the Core Brain as judgment guidance and operational documents as instructions for internal actions, not a customer-facing script. Understand the latest customer need in light of their conversation and Lead Profile. Answer it directly and proportionately; many turns should end after a useful answer, without another question. Avoid reintroducing known facts or reciting document/source phrasing. Use short, readable WhatsApp paragraphs where helpful; no fixed length or mandatory question. Treat retrieved Knowledge as evidence, preserve meaningful uncertainty and never invent project facts, pricing, availability, legal or financing promises, returns, or commitments. Update Lead Profile only with supported progress; structured next_action and sales_stage are internal records, not instructions to interrogate the buyer. Use Human Support for material unknown facts while AI remains owner and preserve the resume objective; use terminal Appointment Handoff only for appointment-ready operational work, and Mandatory Handoff for explicit human requests, ownership conflicts, complaints and policy-bound cases. Never change system-controlled Lead fields; set unknown or unchanged lead_updates fields to null. Return only the schema decision."""


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
