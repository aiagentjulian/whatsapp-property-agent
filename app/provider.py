import json
import urllib.error
import urllib.request


PROFILE_FIELDS = [
    "name", "preferred_language", "purchase_purpose", "purchase_reason", "preferred_location",
    "preferred_property_type", "size_or_layout_preference", "budget_range", "financing_context",
    "purchase_timeline", "viewing_interest", "appointment_readiness", "intent_level", "sales_stage",
    "important_features", "primary_motivations", "decision_factors", "active_concerns", "resolved_concerns",
    "fit_assessment", "next_objective", "last_progress", "next_action", "conversation_summary",
]
ARRAY_FIELDS = {"important_features", "primary_motivations", "decision_factors", "active_concerns", "resolved_concerns"}
ENUM_FIELDS = {
    "purchase_purpose": ["OWN_STAY", "INVESTMENT", "BOTH", "EXPLORING", "UNKNOWN"],
    "appointment_readiness": ["NOT_READY", "EMERGING", "READY_FOR_APPOINTMENT", "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED"],
    "intent_level": ["LOW", "MEDIUM", "HIGH", "READY_FOR_APPOINTMENT"],
    "sales_stage": ["UNDERSTAND", "QUALIFY", "POSITION", "HANDLE", "INTENT", "CLOSE"],
}
STRING = {"type": ["string", "null"]}


def agent_schema():
    updates = {}
    for key in PROFILE_FIELDS:
        if key in ARRAY_FIELDS:
            updates[key] = {"type": ["array", "null"], "items": {"type": "string"}}
        elif key in ENUM_FIELDS:
            updates[key] = {"type": ["string", "null"], "enum": ENUM_FIELDS[key] + [None]}
        else:
            updates[key] = STRING
    support = {key: {"type": "string"} for key in (
        "support_type", "requested_fact", "subject", "customer_need", "reason", "resume_stage", "resume_objective")}
    support["support_type"]["enum"] = ["AVAILABILITY", "PRICING", "PACKAGE", "FINANCING", "LAYOUT", "TECHNICAL", "OTHER"]
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "action": {"type": "string", "enum": ["REPLY", "SUPPORT_REQUEST", "APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"]},
            "sales_move": {"type": "string", "enum": ["ANSWER", "EXPLORE", "POSITION", "HANDLE", "VIEWING", "GIVE_SPACE"]},
            "buyer_signal": {"type": "string", "enum": ["QUESTION", "POSITIVE", "NEUTRAL", "OBJECTION", "DISENGAGED", "UNKNOWN"]},
            "reply": {"type": "string"},
            "lead_updates": {"type": "object", "properties": updates, "required": PROFILE_FIELDS, "additionalProperties": False},
            "support_request": {"type": ["object", "null"], "properties": support, "required": list(support), "additionalProperties": False},
            "handoff_reason": {"type": ["string", "null"], "enum": ["OPERATIONAL_BOOKING", "SALES_OWNERSHIP_CONFLICT", "EXPLICIT_HUMAN_REQUEST", "COMPLAINT_OR_DISPUTE", "HIGH_RISK_FACTUAL_UNCERTAINTY", "OTHER", None]},
            "handoff_details": {"type": ["string", "null"]},
        },
        "required": ["action", "sales_move", "buyer_signal", "reply", "lead_updates", "support_request", "handoff_reason", "handoff_details"],
    }


class OpenAIProvider:
    def __init__(self, config):
        self.config = config
        if not config["api_key"]:
            raise RuntimeError("OPENAI_API_KEY is required for the OpenAI API provider.")

    def decide(self, system_prompt, user_prompt):
        payload = {
            "model": self.config["model"],
            "reasoning": {"effort": self.config["reasoning"]},
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
            "text": {"format": {"type": "json_schema", "name": "property_agent_decision", "strict": True, "schema": agent_schema()}},
            "max_output_tokens": 4500,
            "store": False,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses", data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.config["api_key"], "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            if exc.code in (400, 404, 422):
                raise RuntimeError("GPT-6 Luna API unavailable or request unsupported; no fallback model was used. " + detail[:800])
            raise RuntimeError("OpenAI API request failed (HTTP %s): %s" % (exc.code, detail[:800]))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("OpenAI API request could not complete: %s" % exc)
        if result.get("status") not in (None, "completed"):
            raise RuntimeError("OpenAI API did not complete the structured response: %s" % result.get("status"))
        text = result.get("output_text")
        if not text:
            for item in result.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text = content.get("text")
                        break
        if not text:
            raise RuntimeError("OpenAI API returned no structured decision text.")
        decision = json.loads(text)
        return decision, result.get("usage") or {}
