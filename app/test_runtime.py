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
        sends = []
        result = runtime.process_inbound("Alice Example", "h1", "I want to view this Saturday.", True,
                                         lambda contact, text: sends.append((contact, text)) or {"message_id": "out-h1"})
        self.assertEqual(result["status"], "handed_off")
        self.assertIn("follow up to confirm availability", result["reply"])
        self.assertNotIn("confirmed", result["reply"].lower())
        self.assertEqual(result["send_status"], "sent")
        self.assertEqual(sends, [("Alice Example", result["reply"])])
        self.assertEqual(runtime.process_inbound("Alice Example", "h1", "I want to view this Saturday.", True,
                                                  lambda contact, text: self.fail("duplicate must not send"))["status"],
                         "duplicate")
        lead = runtime.store.get(result["lead_id"])
        self.assertEqual(lead["owner"], "HUMAN")
        self.assertEqual(lead["ai_session_status"], "ENDED")
        self.assertEqual(runtime.process_inbound("Alice Example", "h2", "Can I change the time?")["status"], "suppressed")
        self.assertEqual(len(runtime.store.handoffs()), 1)
        self.assertEqual(len(agent.decisions), 1)
        self.assertFalse(runtime.store.formal_handoff(lead["lead_id"], "APPOINTMENT_HANDOFF", "OTHER", "again"))

    def test_mandatory_handoff_sends_acknowledgment_after_owner_transfer(self):
        mandatory = decision("MANDATORY_HANDOFF", "Use this LLM reply only.", handoff_reason="EXPLICIT_HUMAN_REQUEST",
                             handoff_details="Buyer requested a human agent")
        runtime = Runtime(self.config, Store(self.path), FakeAgent(mandatory))
        sends = []
        result = runtime.process_inbound("Alice Example", "mh1", "Can a person help me?", True,
                                         lambda contact, text: sends.append((contact, text)) or {"message_id": "out-mh1"})
        self.assertEqual(result["status"], "handed_off")
        self.assertEqual(result["send_status"], "sent")
        self.assertEqual(result["reply"], "I’ve passed this to our team, and someone will follow up with you.")
        self.assertEqual(sends, [("Alice Example", result["reply"])])
        lead = runtime.store.get(result["lead_id"])
        self.assertEqual((lead["owner"], lead["ai_session_status"]), ("HUMAN", "ENDED"))
        self.assertEqual(len(runtime.store.handoffs()), 1)

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
        ad_intro = retrieve("Hi, I saw your property ad. Can share more details?")
        self.assertEqual(len(ad_intro), 1)
        self.assertEqual(ad_intro[0]["heading"], "General property facts")
        self.assertIn("Seberang Jaya", ad_intro[0]["content"])
        self.assertIn("Freehold", ad_intro[0]["content"])
        self.assertNotIn("SkyWorld", str(ad_intro))
        self.assertNotIn("open-plan", str(ad_intro))
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

    def test_relevant_golden_examples_reach_agent_without_script_dump(self):
        import json
        from .golden_guidance import select_golden_guidance
        from .sales_workflow import plan_sales_turn

        def select(message, purpose, history=None):
            history = history or [{"direction": "INBOUND", "body": message}]
            profile = {"purchase_purpose": purpose}
            workflow = plan_sales_turn(message, profile, history)
            return workflow, select_golden_guidance(message, profile, history, workflow)

        workflow, guides = select("own stay", "OWN_STAY")
        self.assertEqual(workflow["stage"], "HOUSEHOLD")
        self.assertEqual(guides["examples"][0]["case_id"], "G01_ad_to_own_stay")
        self.assertLessEqual(len(guides["examples"]), 2)

        workflow, guides = select("just me and my wife", "OWN_STAY")
        self.assertEqual(workflow["stage"], "PRESENT_VALUE")
        self.assertEqual(guides["examples"][0]["case_id"], "G01_ad_to_own_stay")

        workflow, guides = select("Rental income, worried about vacancy", "INVESTMENT")
        self.assertEqual(workflow["stage"], "OBJECTION")
        self.assertEqual(guides["examples"][0]["case_id"], "G05_investment_rental")

        workflow, guides = select("What is the maintenance fee?", "OWN_STAY")
        self.assertEqual(workflow["stage"], "BUYING_CONSIDERATION")
        self.assertEqual(guides["examples"][0]["case_id"], "G02_couple_warm_to_viewing")

        history = [
            {"direction": "INBOUND", "body": "Own stay with my wife"},
            {"direction": "OUTBOUND", "body": "Would a weekend viewing suit you?"},
            {"direction": "INBOUND", "body": "Saturday works for us"},
        ]
        workflow, guides = select("Saturday works for us", "OWN_STAY", history)
        self.assertEqual(workflow["stage"], "VIEWING")
        self.assertEqual(guides["examples"][0]["case_id"], "G02_couple_warm_to_viewing")
        self.assertIn("not fixed scripts", guides["policy"])

        class CaptureProvider:
            def __init__(self):
                self.payload = None
                self.system = None
            def decide(self, system, user):
                self.system = system
                self.payload = json.loads(user)
                return decision(reply="Testing only."), {}

        capture = CaptureProvider()
        config = dict(self.config, golden_guidance_mode="on")
        SalesAgent(config, capture).decide("own stay", {"purchase_purpose": "OWN_STAY"}, [], [])
        self.assertIn("golden_sales_examples", capture.payload)
        self.assertEqual(capture.payload["golden_sales_examples"]["examples"][0]["stage"], "HOUSEHOLD")
        self.assertIn("not its literal language", capture.system)
        self.assertNotIn("golden_conversations_v1.json", capture.system)

        capture_off = CaptureProvider()
        SalesAgent(dict(self.config, golden_guidance_mode="off"), capture_off).decide(
            "own stay", {"purchase_purpose": "OWN_STAY"}, [], [])
        self.assertIsNone(capture_off.payload["golden_sales_examples"])

    def test_golden_simulation_dry_run_has_isolated_call_budget(self):
        from .sales_simulation import dry_run, GOLDEN_RUN, DEFAULT_RUN
        self.assertNotEqual(GOLDEN_RUN, DEFAULT_RUN)
        report = dry_run()
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["api_calls"], 0)
        self.assertEqual(report["phase_call_upper_bound"]["golden_initial"], 12)
        self.assertEqual(report["phase_call_upper_bound"]["golden_retest"], 12)
        self.assertEqual(report["phase_call_upper_bound"]["golden_holdout"], 8)
        self.assertEqual(report["hard_call_cap"], 40)

    def test_golden_conversation_bank_matches_workflow_without_model_calls(self):
        from .golden_cases import load_goldens, check_goldens
        corpus = load_goldens()
        self.assertEqual(len(corpus["cases"]), 9)
        self.assertEqual(corpus["status"], "DRAFT_FOR_HUMAN_REVIEW_NOT_LIVE_VALIDATED")
        ids = {item["id"] for item in corpus["cases"]}
        self.assertIn("G01_ad_to_own_stay", ids)
        self.assertIn("G02_couple_warm_to_viewing", ids)
        self.assertIn("G05_investment_rental", ids)
        self.assertIn("G06_investment_capital_gain", ids)
        self.assertIn("G08_nonfit_four_bedrooms", ids)
        self.assertTrue(all(case["route"] in ("OWN_STAY", "INVESTMENT")
                            for case in corpus["cases"]))
        report = check_goldens()
        self.assertEqual(report["status"], "passed", report["errors"])
        self.assertEqual(report["api_calls"], 0)
        self.assertEqual(report["beats"], 19)
        self.assertEqual(report["stages"]["G01_ad_to_own_stay"],
                         ["PURPOSE", "HOUSEHOLD", "PRESENT_VALUE"])
        self.assertEqual(report["stages"]["G02_couple_warm_to_viewing"],
                         ["BUYING_CONSIDERATION", "WARM_INTEREST", "VIEWING"])

    def test_two_route_sales_workflow_prioritizes_sales_progress(self):
        from .sales_workflow import plan_sales_turn

        def plan(text, purpose=None, older=()):
            profile = {"purchase_purpose": purpose} if purpose else {}
            history = [{"direction": "INBOUND", "body": msg} for msg in older]
            return plan_sales_turn(text, profile, history)

        opening = plan("Hi, I saw your property ad. Can share more details?")
        self.assertEqual((opening["route"], opening["stage"]), ("UNKNOWN", "PURPOSE"))
        self.assertIn("EXPLORE", opening["allowed_moves"])

        own_stay = plan("own stay")
        self.assertEqual((own_stay["route"], own_stay["stage"]), ("OWN_STAY", "HOUSEHOLD"))
        self.assertIn("who would actually live", own_stay["objective"])
        self.assertIn("NOT ask first home versus upgrade", own_stay["objective"])

        with_spouse = plan("just me and my wife", "OWN_STAY", ("own stay",))
        self.assertEqual(with_spouse["stage"], "PRESENT_VALUE")
        self.assertNotIn("EXPLORE", with_spouse["allowed_moves"])
        self.assertIn("POSITION", with_spouse["allowed_moves"])

        # The real failed conversation must not trigger another broad quiz.
        upgrade = plan("upgrade", "OWN_STAY", ("own stay",))
        self.assertEqual(upgrade["stage"], "PRESENT_VALUE")
        self.assertNotIn("EXPLORE", upgrade["allowed_moves"])

        # Disclosure of household or upgrade is not yet an appointment signal.
        self.assertNotIn("VIEWING", with_spouse["allowed_moves"])
        self.assertNotIn("VIEWING", upgrade["allowed_moves"])
        warmed = plan("I like what you're describing", "OWN_STAY", ("own stay", "just me and my wife"))
        self.assertEqual(warmed["stage"], "WARM_INTEREST")
        self.assertIn("VIEWING", warmed["allowed_moves"])
        self.assertIn("not an assumed booking", warmed["objective"])

        investment = plan("investment")
        self.assertEqual((investment["route"], investment["stage"]),
                         ("INVESTMENT", "INVESTMENT_OBJECTIVE"))
        self.assertIn("rental income or capital gain", investment["objective"])
        rental = plan("mainly rental income", "INVESTMENT", ("investment",))
        self.assertEqual(rental["stage"], "PRESENT_VALUE")
        self.assertNotIn("EXPLORE", rental["allowed_moves"])
        cap_gain = plan("capital gain", "INVESTMENT", ("investment",))
        self.assertEqual(cap_gain["stage"], "PRESENT_VALUE")

        legacy_both = plan("both", "BOTH")
        self.assertEqual((legacy_both["route"], legacy_both["stage"]), ("UNKNOWN", "PURPOSE"))
        known_primary = plan("own stay", "BOTH")
        self.assertEqual(known_primary["route"], "OWN_STAY")

        location = plan("Where is the location?", "OWN_STAY", ("own stay",))
        self.assertEqual(location["stage"], "DIRECT_QUESTION")
        self.assertIn("ANSWER", location["allowed_moves"])
        objection = plan("Seems too small", "OWN_STAY", ("own stay",))
        self.assertEqual(objection["stage"], "OBJECTION")
        self.assertIn("HANDLE", objection["allowed_moves"])
        switched = plan("Actually this is for investment", "OWN_STAY", ("own stay",))
        self.assertEqual(switched["route"], "INVESTMENT")
        self.assertEqual(switched["stage"], "INVESTMENT_OBJECTIVE")

        financing = plan("What is the monthly instalment?", "OWN_STAY", ("own stay",))
        self.assertEqual(financing["stage"], "BUYING_CONSIDERATION")
        self.assertIn("financing or first-time buyer", financing["objective"])
        self.assertNotIn("EXPLORE", financing["allowed_moves"])

        view = plan("Can I arrange a viewing?", "OWN_STAY", ("own stay",))
        self.assertEqual(view["stage"], "VIEWING")
        self.assertIn("VIEWING", view["allowed_moves"])
        accepted = plan_sales_turn("Yes, sounds good", {"purchase_purpose": "OWN_STAY"}, [
            {"direction": "OUTBOUND", "body": "Would you like to arrange a viewing?"},
            {"direction": "INBOUND", "body": "Yes, sounds good"},
        ])
        self.assertEqual(accepted["stage"], "VIEWING")
        date_choice = plan_sales_turn(
            "Saturday would suit us if a slot is confirmed. Could you also share the price?",
            {"purchase_purpose": "OWN_STAY"}, [
                {"direction": "OUTBOUND", "body": "I'll check whether there's a viewing slot this weekend. Would Saturday or Sunday suit you?"},
                {"direction": "INBOUND", "body": "Saturday would suit us if a slot is confirmed. Could you also share the price?"},
            ])
        self.assertEqual(date_choice["stage"], "VIEWING")
        self.assertIn("ANSWER", date_choice["allowed_moves"])
        declined_date = plan_sales_turn(
            "Saturday doesn't work for us, unfortunately.",
            {"purchase_purpose": "OWN_STAY"}, [
                {"direction": "OUTBOUND", "body": "Would you like to arrange a viewing? Would Saturday suit you?"},
                {"direction": "INBOUND", "body": "Saturday doesn't work for us, unfortunately."},
            ])
        self.assertNotEqual(declined_date["stage"], "VIEWING")

    def test_workflow_restricts_structured_move_options(self):
        from .provider import agent_schema
        schema = agent_schema(["ANSWER", "EXPLORE"])
        self.assertEqual(schema["properties"]["sales_move"]["enum"], ["ANSWER", "EXPLORE"])
        self.assertNotIn("BOTH", schema["properties"]["lead_updates"]
                         ["properties"]["purchase_purpose"]["enum"])
        with self.assertRaisesRegex(ValueError, "Invalid sales workflow move"):
            agent_schema(["ANSWER", "HALLUCINATE"])

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
        self.assertIn("sales_workflow", provider.payload)
        self.assertEqual(provider.payload["sales_workflow"]["route"], "OWN_STAY")
        self.assertIn("allowed_moves", provider.payload["sales_workflow"])
        self.assertNotIn("project_sales_context", provider.payload)
        recent = provider.payload["recent_conversation"]
        offering = provider.payload["current_project_unit_offering"]
        self.assertIn("All Phase 1 residential units use the same main unit type", offering)
        self.assertIn("- Built-up: 900 sq.ft.", offering)
        self.assertIn("- 3 bedrooms", offering)
        self.assertIn("- 2 bathrooms", offering)
        reference = provider.payload["verified_project_reference"]
        by_topic = {item["topic"]: item["verified_evidence"] for item in reference}
        self.assertIn("Seberang Jaya", by_topic["Project identity"])
        self.assertIn("Freehold", by_topic["Project identity"])
        self.assertIn("10-acre", by_topic["Major development components"])
        self.assertIn("RM0.18", by_topic["Maintenance"])
        self.assertIn("Q4 2029", by_topic["Completion"])
        self.assertNotIn("SkyWorld", str(reference))
        self.assertNotIn("Pearlmont", str(reference))
        # The exact failed customer journey supplies no layout keywords, but
        # must still give Luna alternative verified project benefits.
        conversation = [
            {"direction": "INBOUND", "body": "Hi, I saw your property ad. Can share more details?"},
            {"direction": "OUTBOUND", "body": "Would this be for own stay or investment?"},
            {"direction": "INBOUND", "body": "own stay"},
            {"direction": "OUTBOUND", "body": "First home or an upgrade?"},
            {"direction": "INBOUND", "body": "upgrade"},
        ]
        SalesAgent(self.config, provider).decide("upgrade", {
            "purchase_purpose": "OWN_STAY", "purchase_reason": "upgrade",
        }, conversation, [])
        self.assertEqual(provider.payload["focused_sales_evidence"]["optional_sales_angles"], [])
        self.assertIn("Freehold", str(provider.payload["verified_project_reference"]))
        self.assertIn("10-acre", str(provider.payload["verified_project_reference"]))
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
        self.assertIn("Guided selling judgment", context)
        self.assertIn("Buyer discovery compass (not a questionnaire)", context)
        self.assertIn("Own stay:", context)
        self.assertIn("Wanting to live there does not by itself establish", context)
        self.assertIn("First discover whether this is for the customer alone", context)
        self.assertIn("Investment:", context)
        self.assertIn("Undecided:", context)
        self.assertNotIn("**Both or undecided:**", context)
        self.assertIn("Do not proactively ask whether this is a first home, upgrade or relocation", context)
        self.assertIn("Workflow discipline", context)
        self.assertIn("rental income, capital appreciation, or a mix", context)
        self.assertIn("what you would do differently with the answer", context)
        self.assertIn("sell the connection to the property before digging deeper", context)
        self.assertIn("connect it to real features of this particular project", context)
        self.assertIn("deepen buying interest", context)
        self.assertIn("not a prescribed sequence or dialogue script", context)
        self.assertIn("would materially improve your pitch", context)
        self.assertIn("An answered discovery question is not an invitation to keep interviewing", context)
        self.assertIn('If the buyer says "upgrade"', context)
        self.assertIn("A short answer to your own discovery question is progress", SYSTEM_PROMPT)
        self.assertIn("Build desire for this particular home, not just a list of facts", context)
        self.assertIn("First judge whether the buyer has actually revealed a need", context)
        self.assertIn("There is no fixed opening formula", context)
        self.assertIn("which brochure category they want to hear about", context)
        self.assertIn("scattered facility highlights", SYSTEM_PROMPT)
        self.assertIn("creatively connect that desire to this property", context)
        self.assertNotIn("including plausible ways they *could* use its spaces or amenities", context)
        self.assertIn("Malaysian", SYSTEM_PROMPT)
        self.assertIn("answer truthfully", SYSTEM_PROMPT.lower())
        self.assertIn("connect it back to the home instead of pursuing unrelated lifestyle details", SYSTEM_PROMPT)
        self.assertIn("not a fixed questionnaire or script", SYSTEM_PROMPT)
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
        self.assertEqual(family["optional_sales_angles"], [])
        # An actual expressed preference can still trigger a relevant angle.
        kids = focused_sales_context("We want somewhere with space for kids to play",
                                     {"purchase_purpose": "OWN_STAY"}, messages)
        self.assertTrue(any("SkyPark" in x["angle"] for x in kids["optional_sales_angles"]))
        messages += [
            {"direction": "OUTBOUND", "body": "There's a 10-acre SkyPark and Sunway Carnival Mall in the wider area."},
            {"direction": "INBOUND", "body": "oh ok"},
        ]
        cool = focused_sales_context("oh ok", {"purchase_purpose": "OWN_STAY"}, messages)
        self.assertFalse(any("SkyPark" in x["angle"] or "Mature Seberang" in x["angle"]
                             for x in cool["optional_sales_angles"]))
        self.assertTrue(any("SkyPark" in title for title in cool["already_presented"]))

    def test_own_stay_context_is_human_readable_and_does_not_keep_reappearing(self):
        from .knowledge import focused_sales_context
        history = [
            {"direction": "INBOUND", "body": "Hi, I saw your property ad. Can share more details?"},
            {"direction": "OUTBOUND", "body": "900 sq. ft., 3 bedrooms, 2 bathrooms, balcony. Own stay or investment?"},
            {"direction": "INBOUND", "body": "own stay"},
        ]
        own_stay = focused_sales_context("own stay", {"purchase_purpose": "OWN_STAY"}, history)
        self.assertEqual(own_stay["optional_sales_angles"], [])
        for buyer_reply in ("just me and wife", "a couple", "with family"):
            result = focused_sales_context(buyer_reply, {"purchase_purpose": "OWN_STAY"}, history)
            self.assertFalse(any("Efficient 900 sqft Layout" in row["angle"]
                                 for row in result["optional_sales_angles"]))

        # Explicit interest in room arrangement still retrieves the layout.
        layout_request = focused_sales_context(
            "Can you show how the bedrooms are laid out?",
            {"purchase_purpose": "OWN_STAY"}, history)
        layout = [row for row in layout_request["optional_sales_angles"]
                  if "Efficient 900 sqft Layout" in row["angle"]]
        self.assertTrue(layout)
        self.assertIn("open-plan", layout[0]["verified_evidence"].lower())
        self.assertNotIn("404.7", layout[0]["verified_evidence"])

        history += [
            {"direction": "OUTBOUND", "body": "There's an open-plan living, dining and kitchen space."},
            {"direction": "INBOUND", "body": "I guess so"},
        ]
        tentative = focused_sales_context("I guess so", {"purchase_purpose": "OWN_STAY"}, history)
        self.assertEqual(tentative["optional_sales_angles"], [])
        history.append({"direction": "INBOUND", "body": "Two people and three cats"})
        pets = focused_sales_context("Two people and three cats", {"purchase_purpose": "OWN_STAY"}, history)
        self.assertFalse(any("Efficient 900 sqft Layout" in row["angle"]
                             for row in pets["optional_sales_angles"]))

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
        with patch("app.config.load_env_file"), patch.dict("os.environ", {}, clear=True):
            self.assertEqual(get_config()["reasoning"], "high")
        with patch("app.config.load_env_file"), patch.dict("os.environ", {"RUNTIME_REASONING": "medium"}, clear=True):
            self.assertEqual(get_config()["reasoning"], "medium")
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
        self.assertIn("sales_move", schema["required"])
        self.assertIn("buyer_signal", schema["required"])
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
