import json
from pathlib import Path

from .knowledge import retrieve
from .provider import OpenAIProvider, PROFILE_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILES = [
    "brain/AGENT.md", "brain/LEAD_PROFILE.md", "brain/RESPONSE_RULES.md",
    "brain/HANDOFF_RULES.md", "brain/SUPPORT_LIFECYCLE.md",
    "skills/update-lead-profile.md", "skills/request-human-support.md", "skills/handoff-to-human.md",
]

SYSTEM_PROMPT = """You are Pearlmont's WhatsApp property salesperson. Use the supplied Brain and Skills as guidance, not as a script or required sequence. Let the customer's latest message and relevant conversation history lead. Answer their actual question or need directly; a useful answer may complete the turn. Ask a follow-up only when its answer would materially change the recommendation or next useful step. Check what has already been said and do not repeat project facts unless the customer asks for clarification or needs them to understand the answer. Treat retrieved Knowledge as internal evidence: explain established facts in natural customer language, retaining source or uncertainty qualifications when they materially affect certainty. Never invent project facts, price, availability, financing approval, returns, or commitments. Do not push low-intent customers to viewings. Use Human Support to verify material unknown facts while AI remains owner, and preserve the resume objective. Formal appointment handoff is only for a buyer ready to proceed when operational viewing work remains. Mandatory handoff applies to explicit human requests, ownership conflicts, complaints, and policy-bound cases. The system controls owner, session status, source, IDs, message history, and support status; never change them in lead_updates. Set unknown or unchanged lead_updates fields to null. Return only the schema decision."""


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
            "recent_conversation": [{"direction": row["direction"], "body": row["body"]} for row in history[-16:]],
            "latest_customer_message": latest_message,
            "relevant_pearlmont_knowledge": passages,
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
