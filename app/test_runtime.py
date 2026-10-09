import tempfile
import unittest
from pathlib import Path

from .db import Store
from .agent import SalesAgent
from .knowledge import retrieve
from .provider import PROFILE_FIELDS, agent_schema
from .service import Runtime, support_signature
from .contacts import is_allowlisted


def decision(action="REPLY", reply="Thanks, I’ll check that for you.", **kwargs):
    value = {"action": action, "reply": reply, "lead_updates": {key: None for key in PROFILE_FIELDS},
             "support_request": None, "handoff_reason": None, "handoff_details": None}
    value.update(kwargs)
    return value


class FakeAgent:
    def __init__(self, *decisions):
        self.decisions = list(decisions)
        self.support_contexts = []

    def decide(self, message, profile, history, supports):
        self.support_contexts.append(supports)
        if not self.decisions:
            return decision(), {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
        return self.decisions.pop(0), {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "agent.sqlite3"
        self.config = {"database": self.path, "model": "gpt-6-luna", "allowlist": ["Alice Example", "+60123456789"]}

    def tearDown(self):
        self.temp.cleanup()

    def support(self, requested="Check Type B availability"):
        return {"support_type": "AVAILABILITY", "requested_fact": requested, "subject": "Type B",
                "customer_need": "Decide whether to view Type B", "reason": "Live availability is not in static Knowledge",
                "resume_stage": "HANDLE", "resume_objective": "Continue the buyer discussion and move toward viewing"}

    def test_allowlist_enforced_and_contact_matching(self):
        self.assertTrue(is_allowlisted("Alice Example", self.config["allowlist"]))
        self.assertTrue(is_allowlisted("+60123456789", self.config["allowlist"]))
        self.assertFalse(is_allowlisted("123456789", self.config["allowlist"]))
        self.assertFalse(is_allowlisted("Unrelated Person", self.config["allowlist"]))
        runtime = Runtime(self.config, Store(self.path), FakeAgent())
        self.assertEqual(runtime.process_inbound("Unrelated Person", "x", "hello")["status"], "blocked")

    def test_lead_reuse_dedup_and_restart_persistence(self):
        store = Store(self.path)
        lead, inserted, _ = store.ingest("Alice Example", "m1", "Hi")
        same, inserted_again, _ = store.ingest("Alice Example", "m2", "Price?")
        duplicate, was_inserted, _ = store.ingest("Alice Example", "m2", "Price?")
        self.assertTrue(inserted); self.assertTrue(inserted_again); self.assertFalse(was_inserted)
        self.assertEqual(lead["lead_id"], same["lead_id"])
        self.assertEqual(same["lead_id"], duplicate["lead_id"])
        restarted = Store(self.path)
        self.assertEqual(len(restarted.leads()), 1)
        self.assertEqual(len(restarted.history(lead["lead_id"])), 2)
        self.assertEqual(restarted.get(lead["lead_id"])["lead_source"], "INBOUND")

    def test_support_create_resolve_resume_and_duplicate_equivalence(self):
        request = self.support()
        equivalent = self.support("Can you confirm Type B is still available?")
        self.assertEqual(support_signature(request), support_signature(equivalent))
        first = decision("SUPPORT_REQUEST", support_request=request)
        second = decision("SUPPORT_REQUEST", support_request=equivalent)
        agent = FakeAgent(first, second, decision(reply="The verified result confirms it is available."))
        runtime = Runtime(self.config, Store(self.path), agent)
        r1 = runtime.process_inbound("Alice Example", "s1", "Is Type B available?")
        r2 = runtime.process_inbound("Alice Example", "s2", "Any update on Type B?")
        self.assertEqual(r1["status"], "support_requested")
        self.assertEqual(r2["status"], "support_reused")
        store = runtime.store
        pending = store.pending_support()
        self.assertEqual(len(pending), 1)
        self.assertEqual(store.get(pending[0]["lead_id"])["owner"], "AI")
        resolved = store.resolve_support(pending[0]["request_id"], "Verified: one Type B unit is currently available.")
        self.assertEqual(resolved["status"], "RESOLVED")
        resumed = runtime.process_inbound("Alice Example", "s3", "Thanks, what does that mean for viewing?")
        self.assertEqual(resumed["status"], "reply_ready")
        self.assertTrue(agent.support_contexts[-1])
        self.assertIn("Verified: one Type B unit is currently available.", agent.support_contexts[-1][0]["support_result"])
        self.assertEqual(store.usage()["calls"], 3)

    def test_formal_handoff_is_one_way_and_blocks_later_ai(self):
        ready = decision("APPOINTMENT_HANDOFF", "I can arrange the viewing.", handoff_reason="OPERATIONAL_BOOKING",
                         handoff_details="Buyer requested a Saturday viewing", lead_updates={**{k: None for k in PROFILE_FIELDS},
                         "appointment_readiness": "READY_FOR_APPOINTMENT"})
        agent = FakeAgent(ready, decision(reply="should never be called"))
        runtime = Runtime(self.config, Store(self.path), agent)
        result = runtime.process_inbound("Alice Example", "h1", "I want to view this Saturday.")
        self.assertEqual(result["status"], "handed_off")
        lead = runtime.store.get(result["lead_id"])
        self.assertEqual(lead["owner"], "HUMAN")
        self.assertEqual(lead["ai_session_status"], "ENDED")
        self.assertEqual(runtime.process_inbound("Alice Example", "h2", "Can I change the time?")["status"], "suppressed")
        self.assertEqual(len(runtime.store.handoffs()), 1)
        self.assertEqual(len(agent.decisions), 1)
        self.assertFalse(runtime.store.formal_handoff(lead["lead_id"], "APPOINTMENT_HANDOFF", "OTHER", "again"))

    def test_appointment_handoff_requires_ready_state(self):
        malformed = decision("APPOINTMENT_HANDOFF", handoff_reason="OPERATIONAL_BOOKING")
        runtime = Runtime(self.config, Store(self.path), FakeAgent(malformed))
        with self.assertRaisesRegex(ValueError, "appointment-ready"):
            runtime.process_inbound("Alice Example", "a1", "Maybe I will view sometime.")

    def test_send_uncertainty_is_not_retried_or_reported_sent(self):
        runtime = Runtime(self.config, Store(self.path), FakeAgent(decision(reply="Here are the details.")))
        result = runtime.process_inbound("Alice Example", "u1", "Tell me about it", True,
                                         lambda contact, text: (_ for _ in ()).throw(RuntimeError("timeout")))
        self.assertEqual(result["send_status"], "uncertain")
        self.assertTrue(result["operator_review_required"])
        self.assertEqual(runtime.store.history(result["lead_id"])[-1]["send_status"], "uncertain")

    def test_knowledge_retrieval_and_internal_boundary(self):
        pricing = retrieve("What is the current price and package for this unit?")
        self.assertTrue(any("pricing.md" in row["path"] or "sales-package.md" in row["path"] for row in pricing))
        self.assertFalse(any(row["path"].startswith("04_internal/") for row in pricing))
        ownership = retrieve("I already registered with another agent; who owns this lead?")
        self.assertTrue(any(row["path"].startswith("04_internal/") and "INTERNAL ONLY" in row["content"] for row in ownership))
        ordinary_ownership = retrieve("Monthly home ownership costs are important to us.",
                                      {"active_concerns": ["monthly home ownership costs"]})
        self.assertFalse(any(row["path"].startswith("04_internal/") for row in ordinary_ownership))
        self.assertTrue(any("maintenance-and-management.md" in row["path"] and "RM0.18" in row["content"]
                            for row in ordinary_ownership))
        layout = retrieve("Layout?")
        self.assertEqual(len(layout), 1)
        self.assertEqual(layout[0]["heading"], "Layout and room arrangement")
        self.assertFalse(retrieve("Own stay."))
        intro = retrieve("Hi there, may I know more about this project?")
        self.assertEqual(len(intro), 1)
        self.assertEqual(intro[0]["heading"], "General property facts")
        self.assertIn("Freehold", intro[0]["content"])
        self.assertNotIn("SkyWorld", str(intro))
        self.assertNotIn("Pearlmont", str(intro))
        other_intro = retrieve("Can you share some project details?")
        self.assertNotIn("SkyWorld Pearlmont", str(other_intro))
        # Identity questions must still have access to the real project facts.
        identified = retrieve("Is this SkyWorld Pearlmont?")
        self.assertTrue(any("SkyWorld Pearlmont" in row["content"] for row in identified))
        natural_layout = retrieve("900 sq ft sounds tight—how are the rooms laid out?")
        self.assertTrue(any("unit-and-layout.md" in row["path"] for row in natural_layout))
        pool_details = retrieve("Could you give me a fuller explanation of the main pool and kids’ pool, including their approximate lengths and depths?")
        self.assertTrue(any("55m" in row["content"] or "55 m" in row["content"] for row in pool_details))

    def test_history_order_is_stable_for_equal_timestamps(self):
        store = Store(self.path)
        lead, _, _ = store.ingest("Alice Example", "h1", "first")
        store.add_message(lead["lead_id"], "OUTBOUND", "reply")
        store.ingest("Alice Example", "h2", "second")
        with store.connect() as db:
            db.execute("UPDATE messages SET created_at='2026-01-01T00:00:00+00:00' WHERE lead_id=?", (lead["lead_id"],))
        self.assertEqual([row["body"] for row in store.history(lead["lead_id"])], ["first", "reply", "second"])

    def test_sales_agent_receives_extended_bidirectional_history(self):
        import json
        class CapturingProvider:
            def __init__(self):
                self.payload = None
            def decide(self, system, user):
                self.payload = json.loads(user)
                return decision(reply="Okay."), {}

        provider = CapturingProvider()
        rows = [{"direction": "INBOUND" if i % 2 == 0 else "OUTBOUND",
                 "body": "message %s" % i} for i in range(50)]
        SalesAgent(self.config, provider).decide("latest", {}, rows, [])
        recent = provider.payload["recent_conversation"]
        offering = provider.payload["current_project_unit_offering"]
        self.assertIn("All Phase 1 residential units use the same main unit type", offering)
        self.assertIn("- Built-up: 900 sq.ft.", offering)
        self.assertIn("- 3 bedrooms", offering)
        self.assertIn("- 2 bathrooms", offering)
        self.assertEqual(len(recent), 40)
        self.assertEqual(recent[0]["body"], "message 10")
        self.assertEqual(recent[-1]["body"], "message 49")
        self.assertEqual(recent[0]["direction"], "INBOUND")
        self.assertEqual(recent[-1]["direction"], "OUTBOUND")

    def test_sales_evidence_uses_recent_buyer_context_across_profiles(self):
        from .knowledge import buyer_sales_evidence
        family_messages = [
            {"direction": "INBOUND", "body": "own stay"},
            {"direction": "OUTBOUND", "body": "Would the 3-bedroom layout work?"},
            {"direction": "INBOUND", "body": "We have two children and practical family spaces matter."},
            {"direction": "OUTBOUND", "body": "That layout may suit you."},
            {"direction": "INBOUND", "body": "I think the layout could work."},
        ]
        evidence = buyer_sales_evidence({
            "purchase_purpose": "OWN_STAY",
            "important_features": ["Practical layout for a family with two children", "Family-friendly spaces"],
            "conversation_summary": "Own-stay buyer with two children who is assessing family layout fit.",
        }, family_messages)
        self.assertLessEqual(len(evidence), 1)
        self.assertTrue(any(item["heading"] in ("2. Family Practicality Angle", "9. Efficient 900 sqft Layout") for item in evidence))
        own_stay_messages = [
            {"direction": "INBOUND", "body": "My partner and I want an own-stay home; monthly ownership costs matter."},
            {"direction": "OUTBOUND", "body": "Would maintenance or mortgage matter more?"},
            {"direction": "INBOUND", "body": "That seems reasonable."},
        ]
        own_stay_evidence = buyer_sales_evidence({
            "purchase_purpose": "OWN_STAY",
            "important_features": ["Monthly ownership costs"],
            "conversation_summary": "Couple considering own stay and watching monthly ownership costs.",
        }, own_stay_messages)
        self.assertTrue(any(item["heading"] == "4. Low-Holding-Cost Angle" for item in own_stay_evidence))
        self.assertNotIn("Family Practicality Angle", " ".join(item["heading"] for item in own_stay_evidence))
        investor_messages = [
            {"direction": "INBOUND", "body": "I am considering a rental investment; monthly holding costs matter."},
            {"direction": "OUTBOUND", "body": "The stated maintenance charge is RM0.18 psf."},
            {"direction": "INBOUND", "body": "That sounds manageable."},
        ]
        investor_evidence = buyer_sales_evidence({
            "purchase_purpose": "INVESTMENT",
            "important_features": ["Rental income", "Manageable ownership costs"],
            "conversation_summary": "Buyer is considering rental investment and holding costs.",
        }, investor_messages)
        self.assertTrue(any(item["heading"] == "4. Low-Holding-Cost Angle" for item in investor_evidence))
        self.assertNotIn("Family Practicality Angle", " ".join(item["heading"] for item in investor_evidence))
        self.assertFalse(buyer_sales_evidence({}, [{"direction": "INBOUND", "body": "Price?"}]))

    def test_sales_brain_keeps_identity_private_and_conversation_unscripted(self):
        from .agent import CONTEXT_FILES, SYSTEM_PROMPT
        context = SalesAgent.context_text()
        self.assertIn("BPG", context)
        self.assertIn("Pearl Residences", SYSTEM_PROMPT)
        self.assertIn("Pearl Residences", context)
        self.assertIn("own stay or investment", SYSTEM_PROMPT)
        self.assertIn("never give more than three", SYSTEM_PROMPT)
        self.assertIn("shift from repeated qualification to relevant positioning", SYSTEM_PROMPT)
        self.assertIn("do not ask open-ended bedroom-count preferences", SYSTEM_PROMPT)
        self.assertIn("four bedrooms are essential", context)
        self.assertIn("If a customer directly asks", SYSTEM_PROMPT)
        self.assertIn("answer truthfully", SYSTEM_PROMPT)
        self.assertIn("brain/AGENT.md", CONTEXT_FILES)
        self.assertNotIn("brain/RESPONSE_RULES.md", CONTEXT_FILES)
        self.assertFalse(any(path.startswith("skills/") for path in CONTEXT_FILES))

    def test_structured_agent_output_schema_and_validation(self):
        class Provider:
            def decide(self, system, user):
                return decision(reply="The project is in Pearlmont."), {"input_tokens": 10, "output_tokens": 3, "total_tokens": 13}
        output, usage = SalesAgent({"model": "gpt-6-luna", "reasoning": "medium"}, Provider()).decide(
            "Where is it?", {"lead_source": "INBOUND"}, [], [])
        self.assertEqual(output["action"], "REPLY")
        self.assertEqual(usage["total_tokens"], 13)
        schema = agent_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("owner", schema["properties"]["lead_updates"]["properties"])
        class InvalidProvider:
            def decide(self, system, user):
                invalid = decision()
                invalid["lead_updates"]["owner"] = "HUMAN"
                return invalid, {}
        with self.assertRaisesRegex(ValueError, "system-controlled"):
            SalesAgent({"model": "gpt-6-luna", "reasoning": "medium"}, InvalidProvider()).decide("Hi", {}, [], [])



if __name__ == "__main__":
    unittest.main()
