"""Experimental two-pass sales cycle. V2 remains the default runtime."""
import json
import time
import urllib.error
import urllib.request

from .agent import SalesAgent, SYSTEM_PROMPT
from .knowledge import current_unit_offering, focused_sales_context, retrieve
from .provider import agent_schema

PROGRESS_FIELDS = ("explicit_requirements", "confirmed_motivations", "hypotheses", "tradeoffs",
                   "objections", "communicated_facts", "sales_attempts", "open_questions",
                   "commitments", "next_opportunity")
PROGRESS_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    **{key: {"type": "array", "items": {"type": "string"}} for key in PROGRESS_FIELDS[:-1]},
    "next_opportunity": {"type": "object", "additionalProperties": False, "properties": {
        "action": {"type": "string"}, "why": {"type": "string"}, "feedback_to_watch": {"type": "string"}},
        "required": ["action", "why", "feedback_to_watch"]}}, "required": list(PROGRESS_FIELDS)}
STRATEGY_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "progress": PROGRESS_SCHEMA,
    "buyer_signal": {"type": "string", "enum": ["QUESTION", "POSITIVE", "NEUTRAL", "OBJECTION", "DISENGAGED", "UNKNOWN"]},
    "reaction_to_previous_action": {"type": "string"},
    "immediate_objective": {"type": "string"},
    "knowledge_query": {"type": ["string", "null"]}},
    "required": ["progress", "buyer_signal", "reaction_to_previous_action", "immediate_objective", "knowledge_query"]}
STRATEGY_PROMPT = """You analyze a Malaysian property buyer conversation for the next useful sales action. Update the compact progress from the full message history and prior progress. Full messages override a stale summary. Explicit requirements and confirmed motivations must be supported by customer words; put interpretations only in hypotheses. Record prior sales angles and the buyer's actual reaction in sales_attempts as concise strings; mark continue, revise or abandon. Distinguish politeness from genuine interest. Keep open questions, promises and support status accurate. A pending support request is awaiting external action, not a reason to promise the same check again. A hard mismatch is only established after the underlying requirement is clear. Set one commercially useful immediate objective, without forcing a stage. Keep arrays compact and remove stale items. Do not write a customer reply."""
CONVERSATION_PROMPT = SYSTEM_PROMPT + """\n\nUse the private progress and objective as evidence, not an order. Correct them when customer intent or verified facts conflict. Discover why a stated requirement matters when there is a plausible fit, then test at most one truthful alternative; respect a definitive mismatch. Observe whether prior angles helped before repeating one. Pending support means no verified result yet: never repeat a promise to check, claim a team was contacted, or promise a scheduled future reply. A support request is only registered after the runtime accepts it. Never claim an appointment is confirmed by a handoff. Answer direct questions first and speak naturally."""


class IncompleteResponse(RuntimeError):
    def __init__(self, status, details, usage):
        super().__init__("Sales Core V3 response %s: %s" % (status, details))
        self.usage = usage
        self.status = status
        self.details = details


class ResponsesProvider:
    def __init__(self, config):
        self.config = config

    def request(self, name, schema, system, user, max_output_tokens):
        payload = {"model": self.config["model"], "reasoning": {"effort": self.config["reasoning"]},
                   "input": [{"role": "system", "content": [{"type": "input_text", "text": system}]},
                             {"role": "user", "content": [{"type": "input_text", "text": user}]}],
                   "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
                   "max_output_tokens": max_output_tokens, "store": False}
        request = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(payload).encode(),
                headers={"Authorization": "Bearer " + self.config["api_key"], "Content-Type": "application/json"}, method="POST")
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise RuntimeError("Sales Core V3 API HTTP %s: %s" % (exc.code, detail[:800]))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("Sales Core V3 API transport: %s" % exc)
        usage = result.get("usage") or {}
        if result.get("status") != "completed":
            raise IncompleteResponse(result.get("status"), result.get("incomplete_details"), usage)
        output = result.get("output_text") or next((item.get("text") for row in result.get("output", [])
            for item in row.get("content", []) if item.get("type") == "output_text"), None)
        if not output:
            raise IncompleteResponse("no_output", result.get("incomplete_details"), usage)
        return json.loads(output), usage, round(time.monotonic() - started, 3)


class SalesCoreV3:
    def __init__(self, config, provider=None, usage_recorder=None):
        self.config = config
        self.provider = provider or ResponsesProvider(config)
        self.usage_recorder = usage_recorder

    def decide(self, latest_message, profile, history, support_results):
        history_context = [{"direction": row.get("direction"), "body": row.get("body", "")[:1600]}
                           for row in history[-28:]]
        previous = profile.get("conversation_progress") or {}
        profile_context = {key: value for key, value in profile.items()
                           if key not in ("lead_id", "phone", "owner", "ai_session_status", "conversation_progress")
                           and value not in (None, "", [], "UNKNOWN")}
        strategy, strategy_usage, strategy_latency = self._request("sales_strategy_v3", STRATEGY_SCHEMA,
            STRATEGY_PROMPT, {"lead_profile": profile_context, "prior_progress": previous,
                              "conversation": history_context, "latest_customer_message": latest_message,
                              "support_and_handoff_status": support_results}, 3000, profile)
        if not isinstance(strategy, dict) or set(strategy) != set(STRATEGY_SCHEMA["required"]):
            raise ValueError("Sales Core V3 strategy response is incomplete")
        progress = strategy["progress"]
        if not isinstance(progress, dict) or set(progress) != set(PROGRESS_FIELDS):
            raise ValueError("Sales Core V3 progress is incomplete")
        query = " ".join(str(x) for x in (latest_message, strategy["immediate_objective"],
                         strategy["knowledge_query"] or "", *progress["explicit_requirements"],
                         *progress["objections"], *progress["open_questions"]))
        passages = retrieve(query, profile, limit=3)
        conversation_input = {"brain_and_skills": SalesAgent.context_text(),
            "lead_profile": profile_context, "conversation_progress": progress,
            "recent_conversation": history_context, "latest_customer_message": latest_message,
            "sales_strategy": {key: value for key, value in strategy.items() if key != "progress"},
            "current_project_unit_offering": current_unit_offering(),
            "relevant_project_knowledge": passages,
            "focused_sales_evidence": focused_sales_context(query, profile, history),
            "support_and_handoff_status": support_results}
        decision, conversation_usage, conversation_latency = self._request("property_agent_decision_v3",
            agent_schema(), CONVERSATION_PROMPT, conversation_input, 6500, profile)
        SalesAgent.validate(decision)
        decision["_conversation_progress"] = progress
        usage = {"input_tokens": _sum_usage(strategy_usage, conversation_usage, key="input_tokens"),
                 "output_tokens": _sum_usage(strategy_usage, conversation_usage, key="output_tokens"),
                 "total_tokens": _sum_usage(strategy_usage, conversation_usage, key="total_tokens"),
                 "stages": {"strategy": strategy_usage, "conversation": conversation_usage},
                 "latency_seconds": {"strategy": strategy_latency, "conversation": conversation_latency},
                 "recorded_stage_usage": bool(self.usage_recorder)}
        return decision, usage

    def _request(self, name, schema, system, data, budget, profile):
        try:
            result = self.provider.request(name, schema, system, json.dumps(data, ensure_ascii=False), budget)
        except IncompleteResponse as exc:
            if self.usage_recorder:
                self.usage_recorder(profile.get("lead_id"), name, exc.usage, exc.status)
            raise
        if self.usage_recorder:
            self.usage_recorder(profile.get("lead_id"), name, result[1], "COMPLETED")
        return result


def _sum_usage(*records, key):
    values = [record.get(key) for record in records if isinstance(record.get(key), int)]
    return sum(values) if values else None
