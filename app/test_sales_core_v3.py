import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .db import Store
from .provider import PROFILE_FIELDS
from .sales_core_v3 import SalesCoreV3, STRATEGY_SCHEMA, PROGRESS_FIELDS, ResponsesProvider, IncompleteResponse
from .service import Runtime


def progress():
    value = {key: [] for key in PROGRESS_FIELDS[:-1]}
    value.update(explicit_requirements=["four bedrooms requested"],
                 hypotheses=["privacy may motivate the room count"],
                 sales_attempts=["three-bedroom alternative: customer has not reacted yet; revise"],
                 next_opportunity={"action": "discover room use", "why": "fit uncertain",
                                   "feedback_to_watch": "whether all rooms must be separate"})
    return value


def decision():
    return {"action": "REPLY", "sales_move": "EXPLORE", "buyer_signal": "QUESTION",
            "reply": "Our verified standard unit has three bedrooms. What would the fourth room be used for?",
            "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
            "handoff_reason": None, "handoff_details": None}


class FakeProvider:
    def __init__(self, fail_strategy=False):
        self.calls = []
        self.fail_strategy = fail_strategy

    def request(self, name, schema, system, user, max_output_tokens):
        self.calls.append({"name": name, "schema": schema, "user": json.loads(user),
                           "max_output_tokens": max_output_tokens})
        if name == "sales_strategy_v3":
            if self.fail_strategy: raise RuntimeError("strategy unavailable")
            return ({"progress": progress(), "buyer_signal": "QUESTION", "reaction_to_previous_action": "unknown",
                     "immediate_objective": "Discover room use", "knowledge_query": "bedroom layout"},
                    {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}, 0.1)
        return decision(), {"input_tokens": 20, "output_tokens": 7, "total_tokens": 27}, 0.2


class SalesCoreV3Tests(unittest.TestCase):
    def test_progress_and_full_context_reach_both_stages(self):
        provider = FakeProvider()
        agent = SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, provider)
        history = [{"direction": "INBOUND" if i % 2 else "OUTBOUND", "body": "Earlier turn %d" % i}
                   for i in range(20)]
        prior = {"explicit_requirements": ["four rooms"], "next_opportunity": {"action": "clarify"}}
        result, usage = agent.decide("Do you have four rooms?", {"purchase_purpose": "OWN_STAY",
            "conversation_progress": prior, "next_objective": "old objective"}, history, [])
        self.assertEqual(provider.calls[0]["user"]["prior_progress"], prior)
        self.assertEqual(len(provider.calls[1]["user"]["recent_conversation"]), 20)
        self.assertIn("current_project_unit_offering", provider.calls[1]["user"])
        self.assertIn("brain_and_skills", provider.calls[1]["user"])
        self.assertIn("four bedrooms requested", result["_conversation_progress"]["explicit_requirements"])
        self.assertEqual(usage["total_tokens"], 42)
        self.assertEqual((provider.calls[0]["max_output_tokens"], provider.calls[1]["max_output_tokens"]), (3000, 6500))

    def test_strategy_failure_stops_without_fabricating_decision(self):
        provider = FakeProvider(fail_strategy=True)
        with self.assertRaisesRegex(RuntimeError, "strategy unavailable"):
            SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, provider).decide("Price?", {}, [], [])
        self.assertEqual(len(provider.calls), 1)

    def test_progress_persists_outside_crm_profile_and_usage_per_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp) / "test.sqlite3")
            lead, _, _ = store.ingest("Test Contact", "m1", "Need four bedrooms")
            observed = []
            agent = SalesCoreV3({"model": "gpt-6-luna", "reasoning": "high"}, FakeProvider(),
                usage_recorder=lambda lead_id, name, usage, status: observed.append((lead_id, name, status)))
            profile = dict(lead["profile"], conversation_progress=store.get_progress(lead["lead_id"]))
            result, usage = agent.decide("Need four bedrooms", profile, store.history(lead["lead_id"]), [])
            store.save_progress(lead["lead_id"], result.pop("_conversation_progress"))
            self.assertEqual(len(observed), 2)
            self.assertTrue(usage["recorded_stage_usage"])
            self.assertEqual(Store(store.path).get_progress(lead["lead_id"])["hypotheses"],
                             ["privacy may motivate the room count"])
            self.assertNotIn("conversation_progress", store.get(lead["lead_id"])["profile"])

    def test_incomplete_response_preserves_usage(self):
        fake_response = {"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"},
                         "usage": {"input_tokens": 100, "output_tokens": 900, "total_tokens": 1000}}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return json.dumps(fake_response).encode()
        with patch("app.sales_core_v3.urllib.request.urlopen", return_value=Response()):
            with self.assertRaises(IncompleteResponse) as caught:
                ResponsesProvider({"model": "gpt-6-luna", "reasoning": "high", "api_key": "fake"}).request(
                    "test", STRATEGY_SCHEMA, "system", "user", 3000)
        self.assertEqual(caught.exception.usage["total_tokens"], 1000)

    def test_v2_remains_default(self):
        with patch("app.service.SalesAgent") as v2:
            runtime = Runtime({"database": ":memory:", "sales_core": "v2"}, store=object())
        v2.assert_called_once()
        self.assertIs(runtime.agent, v2.return_value)

if __name__ == "__main__": unittest.main()
