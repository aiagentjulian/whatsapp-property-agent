import tempfile
import json
import threading
import unittest
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

from .db import Store
from .agent import SalesAgent
from .provider import PROFILE_FIELDS
from .service import Runtime
from .webhook import WebhookApp, make_handler


class FakeAgent:
    def __init__(self):
        self.calls = 0

    def decide(self, *_args):
        self.calls += 1
        return ({"action": "REPLY", "reply": "I can help with that.",
                 "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                 "handoff_reason": None, "handoff_details": None}, {})


class FailingAgent:
    def decide(self, *_args):
        raise RuntimeError("private message and provider details must not be logged")


class FakeMeta:
    def __init__(self):
        self.sends = []

    def send_text(self, to, body):
        self.sends.append((to, body))
        return {"message_id": "wamid.outbound-test", "status": "accepted"}


class FakeProvider:
    def __init__(self):
        self.calls = 0

    def decide(self, _system, _user):
        self.calls += 1
        return ({"action": "REPLY", "reply": "The project offers several home layouts. What size are you considering?",
                 "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                 "handoff_reason": None, "handoff_details": None},
                {"input_tokens": 10, "output_tokens": 12, "total_tokens": 22})


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = {"database": Path(self.temp.name) / "agent.sqlite3", "model": "gpt-6-luna",
                       "allowlist": ["+60184005448", "+60123456789"], "outbound_allowlist": [],
                       "meta_access_token": "test", "meta_phone_number_id": "phone-id",
                       "meta_webhook_verify_token": "verify-test", "meta_graph_api_version": "v25.0"}
        self.store = Store(self.config["database"])
        self.agent = FakeAgent()
        self.runtime = Runtime(self.config, self.store, self.agent)
        self.crm_syncs = []
        self.runtime.sync_crm = lambda: self.crm_syncs.append(True) or {"status": "SYNCED"}
        self.meta = FakeMeta()
        self.app = WebhookApp(self.config, self.runtime, self.meta)

    def tearDown(self):
        self.temp.cleanup()

    def payload(self, message_id="wamid.inbound-test", sender="60184005448", body="Tell me about the project"):
        return {"object": "whatsapp_business_account", "entry": [{"changes": [{"field": "messages", "value": {
            "messaging_product": "whatsapp",
            "metadata": {"display_phone_number": "+1 555 640 9035", "phone_number_id": "phone-id"},
            "contacts": [{"profile": {"name": "Test Contact"}, "wa_id": sender}],
            "messages": [{"id": message_id, "from": sender, "type": "text", "text": {"body": body}}]}}]}]}

    def test_verify_token_matches_without_revealing_it(self):
        self.assertEqual(self.app.verify("hub.mode=subscribe&hub.verify_token=verify-test&hub.challenge=123"), "123")
        self.assertIsNone(self.app.verify("hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=123"))

    def test_inbound_calls_existing_runtime_once_and_persists_meta_message_id(self):
        result = self.app.handle_payload(self.payload())
        self.assertEqual(result["handled"], 1)
        self.assertEqual(self.agent.calls, 1)
        self.assertEqual(self.meta.sends, [("60184005448", "I can help with that.")])
        self.assertEqual(len(self.store.leads()), 1)
        lead = self.store.leads()[0]
        history = self.store.history(lead["lead_id"])
        self.assertEqual([row["external_id"] for row in history], ["wamid.inbound-test", "wamid.outbound-test"])
        self.assertEqual([row["send_status"] for row in history], ["received", "sent"])
        self.assertEqual(len(self.crm_syncs), 1)

    def test_duplicate_delivery_does_not_call_agent_or_send_twice(self):
        self.app.handle_payload(self.payload())
        self.app.handle_payload(self.payload())
        self.assertEqual(self.agent.calls, 1)
        self.assertEqual(len(self.meta.sends), 1)
        self.assertEqual(len(self.store.leads()), 1)

    def test_unsupported_sender_and_unrelated_events_are_ignored(self):
        self.app.handle_payload(self.payload(sender="60999999999"))
        result = self.app.handle_payload({"object": "whatsapp_business_account", "entry": [{"changes": [{"field": "account_update", "value": {}}]}]})
        self.assertEqual(result["handled"], 0)
        self.assertEqual(self.agent.calls, 0)
        self.assertEqual(self.meta.sends, [])
        self.assertEqual(self.store.leads(), [])

    def test_delivery_status_updates_outbound_message(self):
        lead, _, _ = self.store.ingest("60184005448", "in-1", "Hello")
        outbound_id = self.store.add_message(lead["lead_id"], "OUTBOUND", "Reply", "sent")
        self.store.update_send_status(outbound_id, "sent", "wamid.outbound-test")
        event = {"object": "whatsapp_business_account", "entry": [{"changes": [{"field": "messages", "value": {
            "metadata": {"phone_number_id": "phone-id"}, "statuses": [{"id": "wamid.outbound-test", "status": "delivered"}]}}]}]}
        self.app.handle_payload(event)
        self.assertEqual(self.store.history(lead["lead_id"])[-1]["send_status"], "delivered")

    def test_http_operator_entrypoint_dry_run_with_fake_provider_and_meta_transport(self):
        provider = FakeProvider()
        agent = SalesAgent(self.config, provider=provider)
        runtime = Runtime(self.config, self.store, agent)
        crm_syncs = []
        runtime.sync_crm = lambda: crm_syncs.append(True) or {"status": "SYNCED"}
        meta = FakeMeta()
        app = WebhookApp(self.config, runtime, meta)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = "http://127.0.0.1:%s" % server.server_address[1]
        try:
            verify = urllib.request.urlopen(origin + "/webhook?hub.mode=subscribe&hub.verify_token=verify-test&hub.challenge=dryrun", timeout=3)
            self.assertEqual(verify.read().decode(), "dryrun")
            data = json.dumps(self.payload()).encode()
            request = urllib.request.Request(origin + "/webhook", data=data, headers={"Content-Type": "application/json"})
            with self.assertLogs(level="INFO") as captured:
                first = json.loads(urllib.request.urlopen(request, timeout=3).read())
            second = json.loads(urllib.request.urlopen(request, timeout=3).read())
            self.assertEqual(first["handled"], 1)
            self.assertEqual(second["handled"], 1)
            self.assertEqual(provider.calls, 1)
            self.assertEqual(len(meta.sends), 1)
            self.assertEqual(len(self.store.leads()), 1)
            self.assertEqual(len(crm_syncs), 1)
            diagnostics = "\n".join(captured.output)
            for stage in ("request_arrived", "json_parsed", "payload_parsed", "message_parsed",
                          "allowlist decision=allow", "sqlite_ingestion outcome=inserted", "gpt_call outcome=complete",
                          "meta_send outcome=accepted", "response http_status=200"):
                self.assertIn(stage, diagnostics)
            for sensitive in ("Tell me about the project", "60184005448", "wamid.inbound-test", "phone-id"):
                self.assertNotIn(sensitive, diagnostics)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_processing_exception_is_logged_without_sensitive_data_after_http_ack(self):
        runtime = Runtime(self.config, self.store, FailingAgent())
        app = WebhookApp(self.config, runtime, self.meta)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = "http://127.0.0.1:%s" % server.server_address[1]
        secret_body = "private-message-body-unique"
        message_id = "wamid.private-test-id"
        try:
            data = json.dumps(self.payload(message_id=message_id, body=secret_body)).encode()
            request = urllib.request.Request(origin + "/webhook", data=data, headers={"Content-Type": "application/json"})
            with self.assertLogs(level="INFO") as captured:
                response = urllib.request.urlopen(request, timeout=3)
                self.assertEqual(response.status, 200)
                self.assertEqual(response.read(), b"")
            diagnostics = "\n".join(captured.output)
            self.assertIn("stage=gpt_call outcome=error error_type=RuntimeError", diagnostics)
            self.assertIn("outcome=processing_error_acknowledged", diagnostics)
            for sensitive in (secret_body, message_id, "60184005448", "private message and provider details"):
                self.assertNotIn(sensitive, diagnostics)
            self.assertEqual(len(self.store.leads()), 1)
            self.assertEqual([row["external_id"] for row in self.store.history(self.store.leads()[0]["lead_id"])],
                             [message_id])
            self.assertEqual(self.meta.sends, [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
