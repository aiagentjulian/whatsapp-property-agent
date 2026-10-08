"""Google Sheets CRM adapter. SQLite remains canonical; writes are idempotent by stable IDs."""
from pathlib import Path

from .config import ROOT

SPREADSHEET_ID = "1yCKtoHYkwXzFj_TJCSCQBodX_2s58Qnc8cweleY7iFw"
LEAD_HEADERS = ["Lead ID", "Phone", "Name", "Source", "Source Detail", "Campaign", "Purpose", "Budget", "Financing", "Preferred Location", "Property Preference", "Timeline", "Motivation", "Concern", "Sales Stage", "Intent", "Appointment Readiness", "Fit", "Last Progress", "Next Action", "Owner", "AI Session Status", "Support Status", "Handoff Status", "Handoff Reason", "Updated At"]
PROSPECT_HEADERS = ["Prospect ID", "Phone", "Name", "Campaign", "Source Detail", "Outbound Status", "Sent At", "Replied At", "Converted Lead ID", "Last Action", "Updated At"]


def lead_values(record):
    p = record["profile"]
    def joined(key):
        value = p.get(key)
        return ", ".join(value) if isinstance(value, list) else (value or "")
    return [record["lead_id"], record["phone"], p.get("name", ""), record["lead_source"], record.get("source_detail", ""), record.get("campaign", ""),
            p.get("purchase_purpose", ""), p.get("budget_range", ""), p.get("financing_context", ""), p.get("preferred_location", ""),
            p.get("preferred_property_type", "") or p.get("size_or_layout_preference", ""), p.get("purchase_timeline", ""),
            joined("primary_motivations"), joined("active_concerns"), p.get("sales_stage", ""), p.get("intent_level", ""),
            p.get("appointment_readiness", ""), p.get("fit_assessment", ""), p.get("last_progress", ""), p.get("next_action", ""),
            record["owner"], record["ai_session_status"], record.get("support_status", "NONE"), record.get("handoff_status", "NONE"),
            record.get("handoff_reason", ""), record["updated_at"]]


def prospect_values(record):
    return [record["prospect_id"], record["phone"], record["name"], record["campaign"], record["source_detail"],
            record["outbound_status"], record["sent_at"] or "", record["replied_at"] or "", record["converted_lead_id"] or "",
            record["last_action"], record["updated_at"]]


class SheetsCRM:
    def __init__(self, service):
        self.service = service

    @classmethod
    def from_token(cls, config):
        token_path = config["google_token_path"]
        if not token_path.is_absolute():
            token_path = ROOT / token_path
        client_path = config["google_oauth_client_path"]
        if not client_path.is_absolute():
            client_path = ROOT / client_path
        if not token_path.is_file() or not client_path.is_file():
            return None
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError("Install Google Sheets dependencies from requirements.txt") from exc
        creds = Credentials.from_authorized_user_file(str(token_path), ["https://www.googleapis.com/auth/spreadsheets"])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
            token_path.chmod(0o600)
        if not creds.valid:
            return None
        return cls(build("sheets", "v4", credentials=creds, cache_discovery=False))

    def _values(self):
        return self.service.spreadsheets().values()

    def upsert(self, tab, headers, identifier, values):
        sheet_range = "'" + tab.replace("'", "''") + "'"
        existing_headers = self._values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_range + "!1:1").execute().get("values", [[]])[0]
        if existing_headers != headers:
            raise RuntimeError("Existing %s headers differ from the expected CRM schema; refusing to modify the sheet." % tab)
        ids = self._values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_range + "!A2:A").execute().get("values", [])
        matches = [index + 2 for index, row in enumerate(ids) if row and row[0] == identifier]
        if len(matches) > 1:
            raise RuntimeError("Duplicate CRM identifier %s in %s; refusing ambiguous update." % (identifier, tab))
        if matches:
            self._values().update(spreadsheetId=SPREADSHEET_ID, range="%s!A%d:%s%d" % (sheet_range, matches[0], chr(64 + len(headers)), matches[0]),
                                  valueInputOption="RAW", body={"values": [values]}).execute()
        else:
            self._values().append(spreadsheetId=SPREADSHEET_ID, range=sheet_range + "!A1", valueInputOption="RAW", insertDataOption="INSERT_ROWS",
                                  body={"values": [values]}).execute()

    def sync_one(self, store, entity_type, entity_id):
        record = store.crm_record(entity_type, entity_id)
        if record is None:
            raise RuntimeError("SQLite CRM record disappeared: %s %s" % (entity_type, entity_id))
        if entity_type == "LEAD":
            self.upsert("Leads", LEAD_HEADERS, entity_id, lead_values(record))
        elif entity_type == "PROSPECT":
            self.upsert("Prospects", PROSPECT_HEADERS, entity_id, prospect_values(record))
        else:
            raise ValueError("Unknown CRM entity type")


def sync_pending(store, client):
    results = []
    for item in store.outbox():
        try:
            client.sync_one(store, item["entity_type"], item["entity_id"])
        except Exception as exc:
            store.outbox_result(item["entity_type"], item["entity_id"], exc)
            results.append({"entity_type": item["entity_type"], "entity_id": item["entity_id"], "status": "PENDING", "error": str(exc)})
        else:
            store.outbox_result(item["entity_type"], item["entity_id"])
            results.append({"entity_type": item["entity_type"], "entity_id": item["entity_id"], "status": "SYNCED"})
    return results


def authorize(config):
    client_path = config["google_oauth_client_path"]
    token_path = config["google_token_path"]
    if not client_path.is_absolute(): client_path = ROOT / client_path
    if not token_path.is_absolute(): token_path = ROOT / token_path
    if not client_path.is_file():
        raise RuntimeError("Place your Google OAuth Desktop client JSON at %s, then run sheets-auth again." % client_path)
    client_path.chmod(0o600)
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise RuntimeError("Install Google Sheets dependencies from requirements.txt") from exc
    flow = InstalledAppFlow.from_client_secrets_file(str(client_path), ["https://www.googleapis.com/auth/spreadsheets"])
    creds = flow.run_local_server(port=0, open_browser=True, prompt="consent")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    token_path.chmod(0o600)
    return token_path
