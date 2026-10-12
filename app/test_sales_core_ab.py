import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from simulator.runner.sales_core_ab import API, FakeOperations, run_conversation, report_metrics
from app.service import support_customer_reply
from app.provider import PROFILE_FIELDS


class EvalTests(unittest.TestCase):
    def test_support_adapter_reuses_pending_and_resolves_only_on_event(self):
        adapter = FakeOperations()
        request = {"support_type": "PRICING", "subject": "Type A", "requested_fact": "current price for three bedroom Type A unit"}
        first, created = adapter.accept_support(request)
        self.assertTrue(created)
        again, created = adapter.accept_support(request)
        self.assertFalse(created)
        self.assertEqual(first["request_id"], again["request_id"])
        self.assertEqual(adapter.context()[0]["status"], "OPEN")
        self.assertIsNone(adapter.context()[0]["support_result"])
        expanded = dict(request, requested_fact="current price for three bedroom Type A unit and cheaper option")
        expanded_request, expanded_created = adapter.accept_support(expanded)
        self.assertFalse(expanded_created)
        self.assertEqual(expanded_request["request_id"], first["request_id"])
        self.assertIn("current price", support_customer_reply(first, True))
        adapter.resolve(first["request_id"], "Synthetic fixture: verified price RM390k")
        self.assertEqual(adapter.context()[0]["status"], "RESOLVED")
        self.assertFalse(adapter.accept_handoff("APPOINTMENT_HANDOFF", "OPERATIONAL_BOOKING") is False)
        self.assertFalse(adapter.handoff["appointment_confirmed"])

    def test_fake_operator_pauses_without_forced_extra_turn(self):
        scenario = {"opening": "Hi", "persona": "ordinary browser", "facts": "no urgency", "motives": "understand project"}
        config = {"model": "gpt-6-luna", "reasoning": "high", "api_key": ""}
        with tempfile.TemporaryDirectory() as temp:
            result = run_conversation(scenario, "V3", API(config, dry=True), config, Path(temp) / "pair.json")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["customer_turns"], 2)
        self.assertEqual(result["customer_state_transitions"][0]["state"], "END")
        self.assertEqual(len(result["agent_actions"]), 1)
        self.assertEqual(result["deterministic_checks"]["duplicate_support_requests"], 0)

    def test_incomplete_usage_is_counted_but_not_success(self):
        rows = [{"role": "blind_judge", "transport": "responses_api", "outcome": "INCOMPLETE",
                 "latency_seconds": 1.0, "usage": {"input_tokens": 100, "cached_tokens": 0,
                                                     "output_tokens": 900, "total_tokens": 1000}}]
        metrics = report_metrics(rows)
        self.assertEqual(metrics["failed_or_incomplete_calls"], 1)
        self.assertEqual(metrics["tokens"]["total_tokens"], 1000)

    def test_formal_handoff_suppresses_draft_reply_as_runtime_does(self):
        class HandoffAPI(API):
            def fake(self, role, user):
                if role == "sales_v2":
                    return {"action": "APPOINTMENT_HANDOFF", "sales_move": "VIEWING", "buyer_signal": "POSITIVE",
                            "reply": "I will confirm Saturday", "lead_updates": {key: None for key in PROFILE_FIELDS},
                            "support_request": None, "handoff_reason": "OPERATIONAL_BOOKING", "handoff_details": "Buyer ready"}
                return super().fake(role, user)
        scenario = {"opening": "I want to view", "persona": "ready buyer", "facts": "ready", "motives": "see layout"}
        config = {"model": "gpt-6-luna", "reasoning": "high", "api_key": ""}
        with tempfile.TemporaryDirectory() as temp:
            result = run_conversation(scenario, "V2", HandoffAPI(config, dry=True), config, Path(temp) / "pair.json")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(len(result["transcript"]), 1)
        self.assertEqual(result["agent_actions"][0]["suppressed_draft"], "I will confirm Saturday")
        self.assertFalse(result["operations"]["handoff"]["appointment_confirmed"])

    def test_waiting_support_event_resumes_only_with_explicit_fixture(self):
        class EventAPI(API):
            def __init__(self, config):
                super().__init__(config, dry=True)
                self.sales_calls = 0
                self.customer_calls = 0
            def fake(self, role, user):
                if role == "sales_v2":
                    self.sales_calls += 1
                    answer = super().fake(role, user)
                    if self.sales_calls == 1:
                        answer.update(action="SUPPORT_REQUEST", reply="I can register a layout check.",
                            support_request={"support_type": "LAYOUT", "subject": "Type A",
                                "requested_fact": "approved floor plan and bedroom dimensions"})
                    else:
                        answer["reply"] = "The simulated result confirms three bedrooms."
                    return answer
                if role == "customer_simulator":
                    self.customer_calls += 1
                    return {"message": "Okay, thanks.", "state": "WAITING" if self.customer_calls == 1 else "END",
                            "reason": "waiting for result" if self.customer_calls == 1 else "answered",
                            "interest_change": "UNCHANGED"}
                return super().fake(role, user)
        scenario = {"opening": "Could you check the plan?", "persona": "buyer", "facts": "needs layout",
                    "motives": "room fit", "simulated_support_result": "Synthetic fixture: verified three bedrooms"}
        config = {"model": "gpt-6-luna", "reasoning": "high", "api_key": ""}
        with tempfile.TemporaryDirectory() as temp:
            result = run_conversation(scenario, "V2", EventAPI(config), config, Path(temp) / "pair.json")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["operations"]["requests"][0]["status"], "RESOLVED")
        self.assertTrue(any(s["state"] == "RESUMED" for s in result["customer_state_transitions"]))
        self.assertIn("Synthetic fixture", str(result["operations"]["requests"][0]["support_result"]))

if __name__ == "__main__": unittest.main()
