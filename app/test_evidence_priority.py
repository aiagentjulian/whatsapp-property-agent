"""No-API regression tests for sales evidence precedence."""
import json
import unittest

from .agent import SalesAgent
from .evidence_priority import resolved_price_quote
from .provider import agent_schema, PROFILE_FIELDS
from .sales_simulation import simulated_resolved_support


class Capture:
    def __init__(self):
        self.context = None

    def decide(self, system, user):
        self.context = json.loads(user)
        return {
            "action": "REPLY", "sales_move": "ANSWER",
            "buyer_signal": "UNKNOWN", "reply": "Test reply.",
            "lead_updates": {k: None for k in PROFILE_FIELDS},
            "support_request": None, "handoff_reason": None,
            "handoff_details": None,
        }, {}


class EvidencePriorityTests(unittest.TestCase):
    def context(self, latest, support=None, profile=None, history=None):
        capture = Capture()
        SalesAgent({"model": "gpt-6-luna", "golden_guidance_mode": "on"},
                   capture).decide(latest, profile or {"purchase_purpose": "OWN_STAY"},
                                   history or [{"direction": "INBOUND", "body": latest}],
                                   support or [])
        return capture.context

    def test_resolved_quote_overrides_old_package_context(self):
        support = simulated_resolved_support()
        self.assertIsNotNone(resolved_price_quote(support))
        data = self.context("How much after rebate?", support)
        self.assertEqual(data["sales_workflow"]["commercial_evidence_state"], "PRICE_CONFIRMED")
        self.assertIsNone(data["dated_commercial_context"])
        self.assertFalse(any(x["path"].startswith("02_commercial/")
                             for x in data["relevant_project_knowledge"]))
        self.assertIn("RM330,000 NET", data["verified_support_results"][0]["support_result"])
        workflow = data["sales_workflow"]
        self.assertEqual(workflow["blocked_support_types"], ["PRICING", "PACKAGE"])
        schema = agent_schema(workflow["allowed_moves"], workflow["blocked_support_types"])
        options = schema["properties"]["support_request"]["properties"]["support_type"]["enum"]
        self.assertNotIn("PRICING", options)
        self.assertNotIn("PACKAGE", options)
        self.assertIn("AVAILABILITY", options)

    def test_unverified_old_price_does_not_override(self):
        bad = [
            {"status": "OPEN", "support_type": "PRICING", "support_result": "Confirmed RM330,000"},
            {"status": "RESOLVED", "support_type": "PRICING",
             "support_result": "The current price RM330,000 is not confirmed."},
            {"status": "RESOLVED", "support_type": "PACKAGE",
             "support_result": "Cannot confirm the package price RM330,000."},
            {"status": "RESOLVED", "support_type": "PRICING",
             "support_result": "Historical price RM330,000; current net quote pending."},
        ]
        for item in bad:
            self.assertIsNone(resolved_price_quote([item]), item)
        old_confirmed = simulated_resolved_support()[0]
        # The store supplies most recently updated support first.
        self.assertIsNone(resolved_price_quote([bad[0], old_confirmed]))
        self.assertIsNone(resolved_price_quote([bad[1], old_confirmed]))
        self.assertIsNotNone(resolved_price_quote([old_confirmed, bad[0]]))
        data = self.context("Price?", [])
        self.assertIsNotNone(data["dated_commercial_context"])
        self.assertNotIn("commercial_evidence_state", data["sales_workflow"])
        pending = self.context("Price?", [bad[0]])
        self.assertEqual(pending["sales_workflow"]["commercial_evidence_state"], "PRICE_CHECK_PENDING")
        self.assertEqual(pending["sales_workflow"]["blocked_support_types"], ["PRICING", "PACKAGE"])
        self.assertIsNotNone(pending["dated_commercial_context"])

    def test_commute_uses_known_location_not_repeated_check(self):
        data = self.context("How long to drive to Perai for work?", [], history=[
            {"direction": "INBOUND", "body": "My wife and I are looking for own stay."},
            {"direction": "OUTBOUND", "body": "It is in Seberang Jaya."},
            {"direction": "INBOUND", "body": "How long to drive to Perai for work?"},
        ])
        flow = data["sales_workflow"]
        self.assertEqual(flow["stage"], "DIRECT_QUESTION")
        self.assertIn("Do not invent drive times", flow["commute_answer_objective"])
        self.assertNotIn("VIEWING", flow["allowed_moves"])

    def test_no_simulation_price_in_unrelated_live_context(self):
        data = self.context("Can you tell me about the landscaped deck?")
        self.assertNotIn("RM330,000 NET", json.dumps(data))
        self.assertNotIn("simulation_only", json.dumps(data))


if __name__ == "__main__":
    unittest.main()
