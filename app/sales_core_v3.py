"""Experimental two-pass sales pipeline. The existing SalesAgent remains V2."""
import json
import time
import urllib.error
import urllib.request

from .agent import SalesAgent, SYSTEM_PROMPT
from .knowledge import focused_sales_context, retrieve
from .provider import agent_schema


STRATEGY_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "customer_intent": {"type": "string"},
        "known_customer_context": {"type": "array", "items": {"type": "string"}},
        "unresolved_items": {"type": "array", "items": {"type": "string"}},
        "buyer_signal": {"type": "string", "enum": ["QUESTION", "POSITIVE", "NEUTRAL", "OBJECTION", "DISENGAGED", "UNKNOWN"]},
        "immediate_objective": {"type": "string"},
        "knowledge_query": {"type": ["string", "null"]},
    },
    "required": ["customer_intent", "known_customer_context", "unresolved_items", "buyer_signal", "immediate_objective", "knowledge_query"],
}

STRATEGY_PROMPT = """You are the private sales-strategy analyst for a Malaysian property salesperson. Assess this customer turn using the supplied profile and conversation, including earlier unresolved requests. Be concise and factual. Do not draft a customer-facing reply. Do not impose a linear sales stage or ask for profile details without a reason. Distinguish a weak acknowledgement from buying interest. Identify what matters now, what remains unresolved, and whether project evidence is needed for the immediate objective. Never infer facts not supported by the conversation."""

CONVERSATION_PROMPT = SYSTEM_PROMPT + """

You are now given a private strategy assessment. Use it as a helpful reading of context, not a required action. Make your own judgment and correct it when it conflicts with the customer or evidence. Relevant knowledge may be empty; do not fill gaps with assumptions. Answer the customer's direct question first. Keep WhatsApp replies concise and natural. Return the same structured decision format required by the runtime."""


class ResponsesProvider:
    """Small structured-output transport, injectable for offline tests."""
    def __init__(self, config):
        self.config = config

    def request(self, name, schema, system, user, max_output_tokens):
        payload = {
            "model": self.config["model"],
            "reasoning": {"effort": self.config["reasoning"]},
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": user}]},
            ],
            "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
            "max_output_tokens": max_output_tokens,
            "store": False,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses", data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.config["api_key"], "Content-Type": "application/json"}, method="POST")
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise RuntimeError("Sales Core V3 API request failed (HTTP %s): %s" % (exc.code, detail[:800]))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("Sales Core V3 API request could not complete: %s" % exc)
        if result.get("status") not in (None, "completed"):
            raise RuntimeError("Sales Core V3 structured response incomplete: %s" % result.get("status"))
        output = result.get("output_text")
        if not output:
            output = next((item.get("text") for row in result.get("output", []) for item in row.get("content", [])
                           if item.get("type") == "output_text"), None)
        if not output:
            raise RuntimeError("Sales Core V3 API returned no structured response")
        return json.loads(output), result.get("usage") or {}, round(time.monotonic() - started, 3)


class SalesCoreV3:
    def __init__(self, config, provider=None):
        self.config = config
        self.provider = provider or ResponsesProvider(config)

    def decide(self, latest_message, profile, history, support_results):
        strategy_history = [
            {"direction": row.get("direction"), "body": row.get("body", "")[:1200]}
            for row in history[-28:]
        ]
        profile_context = {key: value for key, value in profile.items()
                           if key not in ("lead_id", "phone", "owner", "ai_session_status", "next_action", "next_objective", "sales_stage", "last_progress")
                           and value not in (None, "", [], "UNKNOWN")}
        strategy, strategy_usage, strategy_latency = self.provider.request(
            "sales_strategy_v3", STRATEGY_SCHEMA, STRATEGY_PROMPT,
            json.dumps({"lead_profile": profile_context, "recent_conversation": strategy_history,
                        "latest_customer_message": latest_message}, ensure_ascii=False), 900)
        if not isinstance(strategy, dict) or set(strategy) != set(STRATEGY_SCHEMA["required"]):
            raise ValueError("Sales Core V3 strategy response is incomplete")
        query_parts = [latest_message, strategy["customer_intent"], strategy["immediate_objective"]]
        if strategy["knowledge_query"]:
            query_parts.append(strategy["knowledge_query"])
        query_parts.extend(strategy["known_customer_context"])
        query_parts.extend(strategy["unresolved_items"])
        query = " ".join(part for part in query_parts if isinstance(part, str))
        passages = retrieve(query, profile, limit=3)
        focused = focused_sales_context(query, profile, history)
        compact_history = strategy_history[-8:]
        conversation_input = {
            "lead_profile": profile_context,
            "recent_conversation": compact_history,
            "latest_customer_message": latest_message,
            "sales_strategy": strategy,
            "relevant_project_knowledge": passages,
            "focused_sales_evidence": focused,
            "verified_support_results": support_results,
        }
        decision, conversation_usage, conversation_latency = self.provider.request(
            "property_agent_decision_v3", agent_schema(), CONVERSATION_PROMPT,
            json.dumps(conversation_input, ensure_ascii=False), 8000)
        SalesAgent.validate(decision)
        # Keep db usage accounting compatible and expose stage-level usage to the evaluator.
        usage = {
            "input_tokens": _sum_usage(strategy_usage, conversation_usage, key="input_tokens"),
            "output_tokens": _sum_usage(strategy_usage, conversation_usage, key="output_tokens"),
            "total_tokens": _sum_usage(strategy_usage, conversation_usage, key="total_tokens"),
            "stages": {"strategy": strategy_usage, "conversation": conversation_usage},
            "latency_seconds": {"strategy": strategy_latency, "conversation": conversation_latency},
        }
        return decision, usage


def _sum_usage(*records, key):
    values = [record.get(key) for record in records if isinstance(record.get(key), int)]
    return sum(values) if values else None
