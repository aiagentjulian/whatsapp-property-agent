import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .cli import main
from .db import Store
from .provider import PROFILE_FIELDS
from .service import Runtime
from .sheets import LEAD_HEADERS, PROSPECT_HEADERS, SheetsCRM, lead_values, prospect_values, sync_pending
from .whatsapp import is_allowlisted


class FakeAgent:
    def decide(self, *_args):
        return ({"action": "REPLY", "reply": "Thanks, I can help.",
                 "lead_updates": {key: None for key in PROFILE_FIELDS}, "support_request": None,
                 "handoff_reason": None, "handoff_details": None}, {})


class FakeValues:
    def __init__(self, tabs): self.tabs = tabs
    def get(self, spreadsheetId, range):
        tab, cell_range = range.split("!", 1)
        tab = tab.strip("'")
        if cell_range == "1:1": value = [self.tabs[tab]["headers"]]
        elif cell_range == "A2:A": value = [[row[0]] for row in self.tabs[tab]["rows"]]
        else: value = []
        return FakeRequest(lambda: {"values": value})
    def update(self, spreadsheetId, range, valueInputOption, body):
        tab, row_spec = range.split("!", 1); tab = tab.strip("'")
        row_index = int(row_spec.split(":")[0][1:]) - 2
        return FakeRequest(lambda: self.tabs[tab]["rows"].__setitem__(row_index, body["values"][0]) or {})
    def append(self, spreadsheetId, range, valueInputOption, insertDataOption, body):
        tab = range.split("!")[0].strip("'")
        return FakeRequest(lambda: self.tabs[tab]["rows"].extend(body["values"]) or {})


class FakeRequest:
    def __init__(self, callback): self.callback = callback
    def execute(self): return self.callback()


class FakeService:
    def __init__(self):
        self.tabs = {"Leads": {"headers": LEAD_HEADERS, "rows": []},
                     "Prospects": {"headers": PROSPECT_HEADERS, "rows": []}}
    def spreadsheets(self): return self
    def values(self): return FakeValues(self.tabs)


class CRMTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "agent.sqlite3"
        self.store = Store(self.path)
        self.config = {"database": self.path, "model": "gpt-6-luna", "allowlist": ["Inbound Test Contact"],
                       "outbound_allowlist": ["Outbound Test Contact"]}

    def tearDown(self): self.temp.cleanup()

    def test_field_mappings_follow_existing_headers(self):
        lead, _, _ = self.store.ingest("Inbound Test Contact", "in-1", "Hi")
        mapped = lead_values(self.store.crm_record("LEAD", lead["lead_id"]))
        self.assertEqual(len(mapped), len(LEAD_HEADERS))
        self.assertEqual(mapped[:4], [lead["lead_id"], "Inbound Test Contact", "", "INBOUND"])
        prospect, _ = self.store.create_prospect("Outbound Test Contact", campaign="Oct test", source_detail="Approved test")
        self.assertEqual(len(prospect_values(prospect)), len(PROSPECT_HEADERS))
        self.assertEqual(prospect_values(prospect)[5], "NOT_SENT")
        self.assertEqual(len(self.store.leads()), 1)

    def test_outbound_reply_converts_once_and_updates_same_lead(self):
        prospect, created = self.store.create_prospect("Outbound Test Contact", campaign="Oct test", source_detail="Referral")
        self.assertTrue(created)
        self.store.mark_prospect_send(prospect["prospect_id"], "SENDING")
        self.store.mark_prospect_send(prospect["prospect_id"], "SENT")
        runtime = Runtime(self.config, self.store, FakeAgent())
        result = runtime.process_inbound("Outbound Test Contact", "reply-1", "Interested")
        self.assertEqual(result["status"], "reply_ready")
        converted = self.store.get_prospect(prospect["prospect_id"])
        self.assertEqual(converted["outbound_status"], "REPLIED")
        lead = self.store.get(converted["converted_lead_id"])
        self.assertEqual(lead["lead_source"], "OUTBOUND")
        self.assertEqual(lead["prospect_id"], prospect["prospect_id"])
        self.assertEqual(lead["campaign"], "Oct test")
        runtime.process_inbound("Outbound Test Contact", "reply-2", "More details?")
        self.assertEqual(len(self.store.leads()), 1)
        self.assertEqual(self.store.get_prospect(prospect["prospect_id"])["converted_lead_id"], lead["lead_id"])

    def test_outbox_upserts_by_id_and_retries_without_losing_sqlite(self):
        lead, _, _ = self.store.ingest("Inbound Test Contact", "in-1", "Hi")
        client = type("Client", (), {"sync_one": lambda _self, store, entity, identifier: None})()
        results = sync_pending(self.store, client)
        self.assertTrue(results)
        self.assertEqual(self.store.get(lead["lead_id"])["phone"], "Inbound Test Contact")
        self.assertEqual(self.store.outbox(), [])
        self.store.update_profile(lead["lead_id"], {"name": "Test"})
        failing = type("Client", (), {"sync_one": lambda *_args: (_ for _ in ()).throw(RuntimeError("offline"))})()
        result = sync_pending(self.store, failing)
        self.assertEqual(result[0]["status"], "PENDING")
        self.assertIn("offline", self.store.outbox()[0]["last_error"])
        self.assertEqual(self.store.get(lead["lead_id"])["profile"]["name"], "Test")

    def test_rows_append_then_update_same_stable_id(self):
        lead, _, _ = self.store.ingest("Inbound Test Contact", "in-1", "Hi")
        prospect, _ = self.store.create_prospect("Outbound Test Contact", campaign="Oct")
        service = FakeService()
        client = SheetsCRM(service)
        client.sync_one(self.store, "LEAD", lead["lead_id"])
        client.sync_one(self.store, "LEAD", lead["lead_id"])
        client.sync_one(self.store, "PROSPECT", prospect["prospect_id"])
        self.assertEqual(len(service.tabs["Leads"]["rows"]), 1)
        self.assertEqual(len(service.tabs["Prospects"]["rows"]), 1)

    def test_support_handoff_and_one_way_states_are_queued(self):
        lead, _, _ = self.store.ingest("Inbound Test Contact", "in-1", "Hi")
        support = {"support_type": "PRICING", "requested_fact": "price", "subject": "unit", "customer_need": "decide",
                   "reason": "unknown", "resume_stage": "HANDLE", "resume_objective": "continue", "signature": "x"}
        req, _ = self.store.create_support(lead["lead_id"], support)
        self.assertEqual(self.store.crm_record("LEAD", lead["lead_id"])["support_status"], "OPEN")
        self.store.resolve_support(req["request_id"], "verified result")
        self.assertEqual(self.store.crm_record("LEAD", lead["lead_id"])["support_status"], "RESOLVED")
        self.assertTrue(self.store.formal_handoff(lead["lead_id"], "MANDATORY_OPERATIONAL_HANDOFF", "EXPLICIT_HUMAN_REQUEST", "requested"))
        self.assertFalse(self.store.formal_handoff(lead["lead_id"], "MANDATORY_OPERATIONAL_HANDOFF", "OTHER", "again"))
        record = self.store.crm_record("LEAD", lead["lead_id"])
        self.assertEqual((record["owner"], record["ai_session_status"], record["handoff_status"]), ("HUMAN", "ENDED", "COMPLETED"))

    def test_contact_gate_and_outbound_send_requires_interactive_confirmation(self):
        self.assertTrue(is_allowlisted("Outbound Test Contact", self.config["outbound_allowlist"]))
        self.assertFalse(is_allowlisted("Other Test Contact", self.config["outbound_allowlist"]))
        prospect, _ = self.store.create_prospect("Outbound Test Contact")
        import os
        old_db = os.environ.get("DATABASE_PATH")
        old_allow = os.environ.get("WHATSAPP_OUTBOUND_ALLOWLIST")
        old_copy = os.environ.get("OUTBOUND_OPENING_MESSAGE")
        os.environ["DATABASE_PATH"] = str(self.path)
        os.environ["WHATSAPP_OUTBOUND_ALLOWLIST"] = "Outbound Test Contact"
        os.environ["OUTBOUND_OPENING_MESSAGE"] = "Approved test copy"
        try:
            with patch("builtins.input", return_value="NO"), patch("app.cli.WhatsAppWeb.send_outbound") as send:
                with self.assertRaises(SystemExit): main(["send-outbound", prospect["prospect_id"]])
                send.assert_not_called()
            self.assertEqual(self.store.get_prospect(prospect["prospect_id"])["outbound_status"], "NOT_SENT")
            with patch("builtins.input", return_value="SEND"), patch("app.cli.WhatsAppWeb.send_outbound") as send:
                main(["send-outbound", prospect["prospect_id"]])
                send.assert_called_once_with("Outbound Test Contact", "Approved test copy")
            self.assertEqual(self.store.get_prospect(prospect["prospect_id"])["outbound_status"], "SENT")
        finally:
            for key, old in (("DATABASE_PATH", old_db), ("WHATSAPP_OUTBOUND_ALLOWLIST", old_allow), ("OUTBOUND_OPENING_MESSAGE", old_copy)):
                if old is None: os.environ.pop(key, None)
                else: os.environ[key] = old

    def test_uncertain_send_state_cannot_be_retried(self):
        prospect, _ = self.store.create_prospect("Outbound Test Contact")
        self.store.mark_prospect_send(prospect["prospect_id"], "SENDING")
        self.store.mark_prospect_send(prospect["prospect_id"], "UNCERTAIN")
        with self.assertRaisesRegex(ValueError, "not eligible"):
            self.store.mark_prospect_send(prospect["prospect_id"], "SENDING")


if __name__ == "__main__": unittest.main()
