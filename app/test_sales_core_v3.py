import json
import unittest
from unittest.mock import patch

from .agent import SalesAgent
from .sales_core_v3 import SalesCoreV3, STRATEGY_SCHEMA


def decision():
    return {
        "action": "REPLY", "sales_move": "ANSWER", "buyer_signal": "QUESTION",
        "reply": "I can check the latest unit price with the team; it is not in the verified information I have here.",
        "lead_updates": {key: None for key in __import__("app.provider", fromlist=["PROFILE_FIELDS"]).PROFILE_FIELDS},
        "support_request": None, "handoff_reason": None, "handoff_details": None,
    }


class FakeProvider:
    def __init__(self, strategy=None, final=None, fail_strategy=False):
        self.calls = []
        self.strategy = strategy or {
            "customer_intent": "The buyer is returning to an earlier layout question.",
            "known_customer_context": ["Own-stay buyer with two children"],
            "unresolved_items": ["Bedroom layout dimensions remain unanswered"],
            "buyer_signal": "QUESTION", "immediate_objective": "Answer the earlier room-layout request.",
            "knowledge_query": "family two children bedroom layout dimensions",
        }
        self.final = final or decision()
        self.fail_strategy = fail_strategy

    def request(self, name, schema, system, user, max_output_tokens):
        self.calls.append({"name": name, "schema": schema, "system": system, "user": json.loads(user),
                           "max_output_tokens": max_output_tokens})
        if name == "sales_strategy_v3":
            if self.fail_strategy:
                raise RuntimeError("strategy unavailable")
            return self.strategy, {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}, 0.1
        return self.final, {"input_tokens": 20, "output_tokens": 7, "total_tokens": 27}, 0.2


class SalesCoreV3Tests(unittest.TestCase):
    def test_strategy_uses_unresolved_context_to_select_knowledge(self):
        provider = FakeProvider()
        agent = SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, provider)
        history = [
            {"direction": "INBOUND", "body": "We need 3 bedrooms for own stay with two kids."},
            {"direction": "OUTBOUND", "body": "The unit is 900 sqft and has three bedrooms."},
            {"direction": "INBOUND", "body": "Can you tell me the room layout?"},
            {"direction": "OUTBOUND", "body": "I'll check the plan."},
            {"direction": "INBOUND", "body": "Also what is the current price?"},
        ]
        result, usage = agent.decide("Also what is the current price?", {"purchase_purpose": "OWN_STAY"}, history, [])
        self.assertEqual([call["name"] for call in provider.calls], ["sales_strategy_v3", "property_agent_decision_v3"])
        payload = provider.calls[1]["user"]
        self.assertEqual(payload["sales_strategy"]["unresolved_items"], ["Bedroom layout dimensions remain unanswered"])
        self.assertTrue(any("layout" in item["content"].lower() for item in payload["relevant_project_knowledge"]))
        self.assertEqual(usage["total_tokens"], 42)
        self.assertEqual(result["action"], "REPLY")

    def test_strategy_failure_stops_without_fabricating_a_decision(self):
        provider = FakeProvider(fail_strategy=True)
        agent = SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, provider)
        with self.assertRaisesRegex(RuntimeError, "strategy unavailable"):
            agent.decide("How much?", {}, [], [])
        self.assertEqual(len(provider.calls), 1)

    def test_strategy_schema_is_compact_and_does_not_contain_reply_field(self):
        self.assertEqual(set(STRATEGY_SCHEMA["required"]), set(STRATEGY_SCHEMA["properties"]))
        self.assertNotIn("reply", STRATEGY_SCHEMA["properties"])

    def test_strategy_and_conversation_usage_are_combined_without_losing_stage_usage(self):
        provider = FakeProvider()
        agent = SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, provider)
        _, usage = agent.decide("How much?", {}, [{"direction": "INBOUND", "body": "How much?"}], [])
        self.assertEqual(usage["input_tokens"], 30)
        self.assertEqual(usage["output_tokens"], 12)
        self.assertEqual(usage["stages"]["strategy"]["total_tokens"], 15)

    def test_v2_agent_and_prompt_remain_the_existing_default(self):
        from .service import Runtime
        with patch("app.service.SalesAgent") as v2:
            runtime = Runtime({"database": ":memory:", "sales_core": "v2"}, store=object(), agent=None)
        v2.assert_called_once()
        self.assertIs(runtime.agent, v2.return_value)


if __name__ == "__main__":
    unittest.main()
