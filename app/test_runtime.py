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
    value = {"action": action, "sales_move": "ANSWER", "buyer_signal": "UNKNOWN", "reply": reply, "lead_updates": {key: None for key in PROFILE_FIELDS},
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
        SalesAgent(self.config, provider).decide("latest", {
            "purchase_purpose": "OWN_STAY", "next_action": "ASK_BUDGET",
            "sales_stage": "QUALIFY", "active_concerns": [], "phone": "private",
        }, rows, [])
        self.assertEqual(provider.payload["lead_profile"], {"purchase_purpose": "OWN_STAY"})
        self.assertIn("optional_sales_angles", provider.payload["focused_sales_evidence"])
        self.assertNotIn("project_sales_context", provider.payload)
        recent = provider.payload["recent_conversation"]
        offering = provider.payload["current_project_unit_offering"]
        self.assertIn("All Phase 1 residential units use the same main unit type", offering)
        self.assertIn("- Built-up: 900 sq.ft.", offering)
        self.assertIn("- 3 bedrooms", offering)
        self.assertIn("- 2 bathrooms", offering)
        self.assertEqual(len(recent), 28)
        self.assertEqual(recent[0]["body"], "message 22")
        self.assertEqual(recent[-1]["body"], "message 49")
        self.assertEqual(recent[0]["direction"], "INBOUND")
        self.assertEqual(recent[-1]["direction"], "OUTBOUND")

    def test_project_sales_context_offers_broad_evidence_not_a_family_script(self):
        from .knowledge import project_sales_context
        context = project_sales_context()
        facts = " ".join(item["content"] for item in context["facts"])
        angles = context["selling_possibilities"]
        self.assertIn("Sunway Carnival Mall", facts)
        self.assertIn("Children's playground", facts)
        self.assertIn("RM0.18", facts)
        self.assertTrue(any("Mature Seberang Jaya" in item["topic"] for item in angles))
        self.assertTrue(any("Freehold" in item["topic"] for item in angles))
        self.assertTrue(any("SkyPark" in item["topic"] for item in angles))
        self.assertGreaterEqual(len(angles), 8)
        self.assertNotIn("Project name: SkyWorld Pearlmont", facts)
        # The runtime does not choose a "family" or "single" angle in advance.
        self.assertEqual(context, project_sales_context())

    def test_sales_brain_keeps_identity_private_and_conversation_unscripted(self):
        from .agent import CONTEXT_FILES, SYSTEM_PROMPT
        context = SalesAgent.context_text()
        self.assertEqual(CONTEXT_FILES, ["brain/AGENT.md"])
        self.assertIn("BPG", context)
        self.assertIn("Pearl Residences", SYSTEM_PROMPT)
        self.assertIn("Pearl Residences", context)
        self.assertIn("independent sales judgment", context.lower())
        self.assertIn("Malaysian", SYSTEM_PROMPT)
        self.assertIn("Never force jokes", context)
        self.assertIn("answer truthfully", SYSTEM_PROMPT)
        self.assertNotIn("if the customer says 'own stay'", SYSTEM_PROMPT.lower())
        self.assertNotIn("oh ok", SYSTEM_PROMPT.lower())

    def test_focused_sales_context_provides_evidence_without_brochure_dump(self):
        from .knowledge import focused_sales_context
        intro = [{"direction": "INBOUND", "body": "Hi, may I know more about this project?"}]
        start = focused_sales_context(intro[-1]["body"], {}, intro)
        self.assertEqual(start["optional_sales_angles"], [])
        messages = intro + [
            {"direction": "OUTBOUND", "body": "The project is in Seberang Jaya. Own stay or investment?"},
            {"direction": "INBOUND", "body": "own stay"},
            {"direction": "OUTBOUND", "body": "Are you looking with family?"},
            {"direction": "INBOUND", "body": "with family"},
        ]
        family = focused_sales_context("with family", {"purchase_purpose": "OWN_STAY"}, messages)
        self.assertLessEqual(len(family["optional_sales_angles"]), 2)
        self.assertGreater(len(family["optional_sales_angles"]), 0)
        self.assertFalse(any("Vertical School" in x["angle"] for x in family["optional_sales_angles"]))
        messages += [
            {"direction": "OUTBOUND", "body": "There's a 10-acre SkyPark and Sunway Carnival Mall in the wider area."},
            {"direction": "INBOUND", "body": "oh ok"},
        ]
        cool = focused_sales_context("oh ok", {"purchase_purpose": "OWN_STAY"}, messages)
        self.assertFalse(any("SkyPark" in x["angle"] or "Mature Seberang" in x["angle"]
                             for x in cool["optional_sales_angles"]))
        self.assertTrue(any("SkyPark" in title for title in cool["already_presented"]))

    def test_reset_test_lead_isolated_and_restores_new_conversation_state(self):
        store = Store(self.path)
        initial, _, _ = store.ingest("+60123456789", "m-test-1", "I'm looking with family")
        other, _, _ = store.ingest("Real Buyer", "m-real-1", "Need 4 rooms")
        store.update_profile(initial["lead_id"], {"purchase_purpose": "OWN_STAY", "active_concerns": ["budget"]})
        store.add_message(initial["lead_id"], "OUTBOUND", "Here are our facilities")
        store.record_usage(initial["lead_id"], "gpt-6-luna", {"input_tokens": 10})
        self.assertTrue(store.formal_handoff(initial["lead_id"], "MANDATORY_OPERATIONAL_HANDOFF",
                                             "EXPLICIT_HUMAN_REQUEST", "buyer requested"))
        with self.assertRaisesRegex(ValueError, "WHATSAPP_TEST_CONTACTS"):
            store.reset_test_lead("Real Buyer", ["+60123456789"])
        result = store.reset_test_lead("+60123456789", ["+60123456789"])
        self.assertEqual(result["status"], "reset")
        fresh = store.by_phone("+60123456789")
        self.assertEqual(fresh["lead_id"], initial["lead_id"])
        self.assertEqual(fresh["profile"], store._initial_profile(initial["lead_id"], "+60123456789"))
        self.assertEqual(store.history(initial["lead_id"]), [])
        self.assertEqual(store.pending_support(initial["lead_id"]), [])
        self.assertFalse(any(x["lead_id"] == initial["lead_id"] for x in store.handoffs()))
        self.assertEqual(store.usage()["calls"], 0)
        self.assertEqual(store.get(other["lead_id"])["profile"]["purchase_purpose"], "UNKNOWN")
        self.assertEqual(len(store.history(other["lead_id"])), 1)
        self.assertTrue(any(row["entity_id"] == initial["lead_id"] and row["entity_type"] == "LEAD"
                            for row in store.outbox()))
        new, inserted, _ = store.ingest("+60123456789", "m-test-2", "Hi, what is this project?")
        self.assertTrue(inserted)
        self.assertEqual(new["lead_id"], initial["lead_id"])
        self.assertEqual(len(store.history(initial["lead_id"])), 1)
        self.assertEqual(store.history(initial["lead_id"])[0]["body"], "Hi, what is this project?")

    def test_high_reasoning_is_default_unless_explicitly_overridden(self):
        from .config import get_config
        from unittest.mock import patch
        with patch.dict("os.environ", {"RUNTIME_REASONING": "high", "RUNTIME_MODEL": "gpt-6-luna"}):
            self.assertEqual(get_config()["reasoning"], "high")
        self.assertIn('"effort": self.config["reasoning"]', __import__(
            "inspect").getsource(__import__("app.provider", fromlist=["OpenAIProvider"]).OpenAIProvider.decide))

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
