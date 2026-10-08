import tempfile
import unittest
from pathlib import Path

from .db import Store
from .agent import SalesAgent
from .knowledge import retrieve
from .provider import PROFILE_FIELDS, agent_schema
from .service import Runtime, support_signature
from .whatsapp import WhatsAppWeb, is_allowlisted


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

    def test_whatsapp_adapter_reads_only_incoming_message_nodes(self):
        class Message:
            def __init__(self, external_id, body, classes="", testid=""):
                self.external_id = external_id
                self.body = body
                self.classes = classes
                self.testid = testid
            def get_attribute(self, key):
                return {"data-id": self.external_id, "class": self.classes, "data-testid": self.testid}.get(key)
            def locator(self, selector):
                return BodyLocator(self.body)
        class BodyLocator:
            def __init__(self, body): self.body = body
            @property
            def first(self): return self
            def count(self): return int(bool(self.body))
            def inner_text(self): return self.body
        class Messages:
            def all(self):
                return [Message("legacy-1", "hello", classes="message-in"),
                        Message("false_chat_2", "current inbound", testid="conv-msg-2"),
                        Message("true_chat_3", "outbound", testid="conv-msg-3"),
                        Message(None, "missing id"), Message("false_chat_4", "  ", testid="conv-msg-4")]
        class Page:
            def locator(self, selector):
                self.selector = selector
                return Messages()
        page = Page()
        self.assertEqual(WhatsAppWeb._incoming(page), [("legacy-1", "hello"), ("false_chat_2", "current inbound")])
        self.assertEqual(page.selector, '.message-in, [data-testid^="conv-msg-"]')

    def test_whatsapp_startup_waits_for_initial_message_download(self):
        class Locator:
            def __init__(self, visible): self.visible = visible
            @property
            def first(self): return self
            def count(self): return 1
            def is_visible(self): return self.visible
            def all(self): return [self]
        class Page:
            def __init__(self): self.loading = True; self.waits = 0
            def locator(self, selector): return Locator(False if "canvas" in selector or "data-ref" in selector else True)
            def get_by_text(self, text, exact=False): return Locator(self.loading)
            def wait_for_timeout(self, milliseconds): self.waits += 1; self.loading = False
        page = Page()
        adapter = WhatsAppWeb({}, None)
        self.assertTrue(adapter._wait_authenticated(page, timeout=1))
        self.assertEqual(page.waits, 1)

    def test_whatsapp_phone_chat_uses_exact_route_once(self):
        class Locator:
            @property
            def first(self): return self
            @property
            def last(self): return self
            def count(self): return 1
            def is_visible(self): return True
            def wait_for(self, state, timeout): return None
            def inner_text(self, timeout=None): return "+60 18-400 5448"
            def click(self, timeout=None): return None
        class Page:
            class Keyboard:
                def press(self, key): return None
            def __init__(self): self.urls = []; self.keyboard = self.Keyboard()
            def goto(self, url, wait_until): self.urls.append(url)
            def locator(self, selector): return Locator()
            def get_by_role(self, role, name): return Locator()
        page = Page()
        adapter = WhatsAppWeb({}, None)
        self.assertTrue(adapter._open_contact(page, "+60 18-400 5448"))
        self.assertEqual(page.urls, ["https://web.whatsapp.com/send?phone=60184005448"])

    def test_whatsapp_poll_continues_when_one_chat_is_not_ready(self):
        class Adapter(WhatsAppWeb):
            @staticmethod
            def _qr_visible(page): return False
            @staticmethod
            def _wait_for_composer(page, timeout=20000):
                if page == "stalled": raise RuntimeError("chat composer did not become visible")
            @staticmethod
            def _verify_phone_identity(page, contact): return None
            @staticmethod
            def _incoming(page): return [("message-2", "visible inbound")]
        adapter = Adapter({}, None)
        verified = {"60184005448", "60124696398"}
        results = adapter._poll_contact_pages(
            [("60184005448", "stalled"), ("60124696398", "ready")], verified)
        self.assertIn("chat composer did not become visible", results[0][4])
        self.assertEqual(results[0][3], [])
        self.assertIsNone(results[1][4])
        self.assertEqual(results[1][3], [("message-2", "visible inbound")])

    def test_whatsapp_phone_identity_mismatch_fails_closed(self):
        class Locator:
            @property
            def first(self): return self
            def count(self): return 1
            def is_visible(self): return True
            def click(self, timeout=None): return None
            def wait_for(self, state, timeout): return None
            def inner_text(self, timeout=None): return "+60 12-469 6398"
        class Keyboard:
            def press(self, key): return None
        class Page:
            keyboard = Keyboard()
            def get_by_role(self, role, name): return Locator()
            def locator(self, selector): return Locator()
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            WhatsAppWeb._verify_phone_identity(Page(), "60184005448")

    def test_whatsapp_send_confirmation_supports_current_outgoing_dom(self):
        class Locator:
            @property
            def first(self): return self
            def count(self): return 1
            def is_visible(self): return True
            def fill(self, body): self.body = body
            def press(self, key): self.key = key
        class Page:
            def __init__(self): self.selectors = []; self.wait_args = None
            def locator(self, selector):
                self.selectors.append(selector)
                return Locator()
            def wait_for_function(self, script, arg, timeout):
                self.wait_args = (script, arg, timeout)
        page = Page()
        WhatsAppWeb({}, None)._send(page, "Approved reply")
        self.assertEqual(page.selectors[0], WhatsAppWeb.OUTGOING_MESSAGES)
        self.assertEqual(page.wait_args[1]["selector"], WhatsAppWeb.OUTGOING_MESSAGES)


if __name__ == "__main__":
    unittest.main()
