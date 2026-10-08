import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(str(self.path), timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def initialize(self):
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id TEXT PRIMARY KEY, phone TEXT NOT NULL, project TEXT NOT NULL DEFAULT 'pearlmont',
                    lead_source TEXT NOT NULL DEFAULT 'INBOUND', owner TEXT NOT NULL DEFAULT 'AI',
                    ai_session_status TEXT NOT NULL DEFAULT 'ACTIVE', profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(phone, project)
                );
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY, lead_id TEXT NOT NULL REFERENCES leads(lead_id),
                    external_id TEXT UNIQUE, direction TEXT NOT NULL, body TEXT NOT NULL,
                    send_status TEXT NOT NULL DEFAULT 'received', created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS messages_lead_time ON messages(lead_id, created_at);
                CREATE TABLE IF NOT EXISTS support_requests (
                    request_id TEXT PRIMARY KEY, lead_id TEXT NOT NULL REFERENCES leads(lead_id),
                    status TEXT NOT NULL, support_type TEXT NOT NULL, requested_fact TEXT NOT NULL,
                    subject TEXT NOT NULL, customer_need TEXT NOT NULL, reason TEXT NOT NULL,
                    resume_stage TEXT NOT NULL, resume_objective TEXT NOT NULL,
                    signature TEXT NOT NULL, support_result TEXT, created_at TEXT NOT NULL, resolved_at TEXT
                );
                CREATE INDEX IF NOT EXISTS support_signature ON support_requests(lead_id, signature, status);
                CREATE TABLE IF NOT EXISTS handoffs (
                    handoff_id TEXT PRIMARY KEY, lead_id TEXT NOT NULL UNIQUE REFERENCES leads(lead_id),
                    handoff_type TEXT NOT NULL, reason TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS api_usage (
                    usage_id TEXT PRIMARY KEY, lead_id TEXT, model TEXT NOT NULL,
                    input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS adapter_state (
                    state_key TEXT PRIMARY KEY, state_value TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS prospects (
                    prospect_id TEXT PRIMARY KEY, phone TEXT NOT NULL, name TEXT NOT NULL DEFAULT '',
                    campaign TEXT NOT NULL DEFAULT '', source_detail TEXT NOT NULL DEFAULT '',
                    outbound_status TEXT NOT NULL DEFAULT 'NOT_SENT', sent_at TEXT, replied_at TEXT,
                    converted_lead_id TEXT, last_action TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(phone, campaign)
                );
                CREATE TABLE IF NOT EXISTS sheets_outbox (
                    entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'PENDING',
                    attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY(entity_type, entity_id)
                );
            """)
            # Additive migration: existing SQLite databases remain usable.
            columns = {row[1] for row in db.execute("PRAGMA table_info(leads)")}
            for name, declaration in (("source_detail", "TEXT NOT NULL DEFAULT ''"),
                                      ("campaign", "TEXT NOT NULL DEFAULT ''"),
                                      ("prospect_id", "TEXT")):
                if name not in columns:
                    db.execute("ALTER TABLE leads ADD COLUMN %s %s" % (name, declaration))

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def ingest(self, phone, external_id, body):
        """Atomically deduplicate inbound messages and reuse the one project Lead."""
        stamp = now()
        with self.transaction() as db:
            duplicate = db.execute("SELECT message_id, lead_id FROM messages WHERE external_id=?", (external_id,)).fetchone()
            if duplicate:
                return self.get_lead(duplicate["lead_id"], db), False, duplicate["message_id"]
            prospect = db.execute("SELECT * FROM prospects WHERE phone=? AND outbound_status IN ('SENT','REPLIED') ORDER BY updated_at DESC LIMIT 1", (phone,)).fetchone()
            lead = db.execute("SELECT * FROM leads WHERE phone=? AND project='pearlmont'", (phone,)).fetchone()
            if not lead:
                lead_id = str(uuid.uuid4())
                source = "OUTBOUND" if prospect else "INBOUND"
                profile = {"lead_id": lead_id, "phone": phone, "lead_source": source, "sales_stage": "UNDERSTAND",
                           "intent_level": "LOW", "appointment_readiness": "NOT_READY", "purchase_purpose": "UNKNOWN",
                           "owner": "AI", "ai_session_status": "ACTIVE", "next_objective": "Understand the enquiry and respond helpfully."}
                db.execute("INSERT INTO leads (lead_id,phone,project,lead_source,owner,ai_session_status,profile_json,created_at,updated_at,source_detail,campaign,prospect_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                           (lead_id, phone, "pearlmont", source, "AI", "ACTIVE", json.dumps(profile), stamp, stamp,
                            prospect["source_detail"] if prospect else "", prospect["campaign"] if prospect else "", prospect["prospect_id"] if prospect else None))
                self._queue(db, "LEAD", lead_id, stamp)
                if prospect:
                    db.execute("UPDATE prospects SET outbound_status='REPLIED',replied_at=COALESCE(replied_at,?),converted_lead_id=?,last_action='Customer replied; converted to Lead',updated_at=? WHERE prospect_id=?",
                               (stamp, lead_id, stamp, prospect["prospect_id"]))
                    self._queue(db, "PROSPECT", prospect["prospect_id"], stamp)
            else:
                lead_id = lead["lead_id"]
                db.execute("UPDATE leads SET updated_at=? WHERE lead_id=?", (stamp, lead_id))
                self._queue(db, "LEAD", lead_id, stamp)
            message_id = str(uuid.uuid4())
            db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?,?)",
                       (message_id, lead_id, external_id, "INBOUND", body, "received", stamp))
        return self.get(lead_id), True, message_id

    @staticmethod
    def get_lead(lead_id, db=None):
        own = db is None
        db = db or sqlite3.connect(":memory:")
        if own:
            raise RuntimeError("get_lead requires Store.get() when no transaction is supplied")
        row = db.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
        return Store.lead_dict(row) if row else None

    @staticmethod
    def lead_dict(row):
        if not row:
            return None
        data = dict(row)
        data["profile"] = json.loads(data.pop("profile_json"))
        return data

    def get(self, lead_id):
        with self.connect() as db:
            return self.lead_dict(db.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,)).fetchone())

    def by_phone(self, phone):
        with self.connect() as db:
            return self.lead_dict(db.execute("SELECT * FROM leads WHERE phone=? AND project='pearlmont'", (phone,)).fetchone())

    def leads(self):
        with self.connect() as db:
            return [self.lead_dict(r) for r in db.execute("SELECT * FROM leads ORDER BY updated_at DESC")]

    def history(self, lead_id):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM messages WHERE lead_id=? ORDER BY created_at", (lead_id,))]

    def add_message(self, lead_id, direction, body, status="sent"):
        msg_id = str(uuid.uuid4())
        with self.transaction() as db:
            db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?,?)", (msg_id, lead_id, None, direction, body, status, now()))
        return msg_id

    def update_send_status(self, message_id, status):
        with self.transaction() as db:
            db.execute("UPDATE messages SET send_status=? WHERE message_id=?", (status, message_id))

    def update_profile(self, lead_id, updates):
        with self.transaction() as db:
            row = db.execute("SELECT profile_json FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
            if not row:
                raise KeyError("Lead not found")
            profile = json.loads(row[0])
            profile.update(updates)
            profile["owner"] = db.execute("SELECT owner FROM leads WHERE lead_id=?", (lead_id,)).fetchone()[0]
            db.execute("UPDATE leads SET profile_json=?,updated_at=? WHERE lead_id=?", (json.dumps(profile, ensure_ascii=False), now(), lead_id))
            self._queue(db, "LEAD", lead_id, now())
        return self.get(lead_id)

    def create_support(self, lead_id, support):
        """Return (request, created); meaning signature prevents duplicate OPEN/RESOLVED requests."""
        signature = support["signature"]
        with self.connect() as db:
            existing = db.execute("SELECT * FROM support_requests WHERE lead_id=? AND signature=? AND status IN ('OPEN','RESOLVED') ORDER BY created_at DESC LIMIT 1", (lead_id, signature)).fetchone()
            if existing:
                return dict(existing), False
        request_id, stamp = str(uuid.uuid4()), now()
        with self.transaction() as db:
            db.execute("INSERT INTO support_requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (request_id, lead_id, "OPEN", support["support_type"], support["requested_fact"], support["subject"],
                        support["customer_need"], support["reason"], support["resume_stage"], support["resume_objective"], signature, None, stamp, None))
            row = db.execute("SELECT * FROM support_requests WHERE request_id=?", (request_id,)).fetchone()
            self._queue(db, "LEAD", lead_id, stamp)
        return dict(row), True

    def pending_support(self, lead_id=None):
        with self.connect() as db:
            sql = "SELECT * FROM support_requests WHERE status='OPEN'"
            args = ()
            if lead_id:
                sql += " AND lead_id=?"; args = (lead_id,)
            return [dict(r) for r in db.execute(sql + " ORDER BY created_at", args)]

    def support_context(self, lead_id):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM support_requests WHERE lead_id=? AND status IN ('OPEN','RESOLVED') ORDER BY COALESCE(resolved_at,created_at) DESC LIMIT 8", (lead_id,))]

    def resolve_support(self, request_id, result):
        with self.transaction() as db:
            row = db.execute("SELECT * FROM support_requests WHERE request_id=?", (request_id,)).fetchone()
            if not row:
                raise KeyError("Support Request not found")
            if row["status"] != "OPEN":
                raise ValueError("Only an OPEN Support Request can be resolved")
            db.execute("UPDATE support_requests SET status='RESOLVED',support_result=?,resolved_at=? WHERE request_id=?", (result, now(), request_id))
            self._queue(db, "LEAD", row["lead_id"], now())
            resolved = db.execute("SELECT * FROM support_requests WHERE request_id=?", (request_id,)).fetchone()
        return dict(resolved)

    def formal_handoff(self, lead_id, handoff_type, reason, details):
        if handoff_type not in ("APPOINTMENT_HANDOFF", "MANDATORY_OPERATIONAL_HANDOFF"):
            raise ValueError("Invalid formal handoff type")
        stamp = now()
        with self.transaction() as db:
            row = db.execute("SELECT owner,ai_session_status FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
            if not row or row["owner"] != "AI" or row["ai_session_status"] != "ACTIVE":
                return False
            if db.execute("SELECT 1 FROM handoffs WHERE lead_id=?", (lead_id,)).fetchone():
                return False
            hid = str(uuid.uuid4())
            db.execute("INSERT INTO handoffs VALUES(?,?,?,?,?,?)", (hid, lead_id, handoff_type, reason, details, stamp))
            profile = json.loads(db.execute("SELECT profile_json FROM leads WHERE lead_id=?", (lead_id,)).fetchone()[0])
            profile.update({"owner": "HUMAN", "ai_session_status": "ENDED", "handoff_status": "COMPLETED", "handoff_reason": reason})
            db.execute("UPDATE leads SET owner='HUMAN',ai_session_status='ENDED',profile_json=?,updated_at=? WHERE lead_id=?", (json.dumps(profile, ensure_ascii=False), stamp, lead_id))
            self._queue(db, "LEAD", lead_id, stamp)
        return True

    def handoffs(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM handoffs ORDER BY created_at DESC")]

    def record_usage(self, lead_id, model, usage):
        if not usage:
            return
        with self.transaction() as db:
            db.execute("INSERT INTO api_usage VALUES(?,?,?,?,?,?,?)", (str(uuid.uuid4()), lead_id, model, usage.get("input_tokens"), usage.get("output_tokens"), usage.get("total_tokens"), now()))

    def usage(self):
        with self.connect() as db:
            return dict(db.execute("SELECT COUNT(*) calls,COALESCE(SUM(input_tokens),0) input_tokens,COALESCE(SUM(output_tokens),0) output_tokens,COALESCE(SUM(total_tokens),0) total_tokens FROM api_usage").fetchone())

    def adapter_value(self, key):
        with self.connect() as db:
            row = db.execute("SELECT state_value FROM adapter_state WHERE state_key=?", (key,)).fetchone()
            return row[0] if row else None

    def set_adapter_value(self, key, value):
        with self.transaction() as db:
            db.execute("INSERT INTO adapter_state VALUES(?,?,?) ON CONFLICT(state_key) DO UPDATE SET state_value=excluded.state_value,updated_at=excluded.updated_at", (key, value, now()))

    @staticmethod
    def _queue(db, entity_type, entity_id, stamp=None):
        db.execute("INSERT INTO sheets_outbox(entity_type,entity_id,status,attempts,last_error,updated_at) VALUES(?,?,'PENDING',0,NULL,?) ON CONFLICT(entity_type,entity_id) DO UPDATE SET status='PENDING',last_error=NULL,updated_at=excluded.updated_at",
                   (entity_type, entity_id, stamp or now()))

    def create_prospect(self, phone, name="", campaign="", source_detail=""):
        stamp = now()
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM leads WHERE phone=? AND project='pearlmont'", (phone,)).fetchone():
                raise ValueError("This contact already has a Lead; refusing to create a duplicate Prospect.")
            existing = db.execute("SELECT * FROM prospects WHERE phone=? AND campaign=?", (phone, campaign)).fetchone()
            if existing:
                return dict(existing), False
            prospect_id = str(uuid.uuid4())
            db.execute("INSERT INTO prospects(prospect_id,phone,name,campaign,source_detail,outbound_status,last_action,created_at,updated_at) VALUES(?,?,?,?,?,'NOT_SENT','Prospect created',?,?)",
                       (prospect_id, phone, name, campaign, source_detail, stamp, stamp))
            self._queue(db, "PROSPECT", prospect_id, stamp)
            return dict(db.execute("SELECT * FROM prospects WHERE prospect_id=?", (prospect_id,)).fetchone()), True

    def get_prospect(self, prospect_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM prospects WHERE prospect_id=?", (prospect_id,)).fetchone()
            return dict(row) if row else None

    def prospects(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM prospects ORDER BY updated_at DESC")]

    def has_active_outbound_prospect(self, phone):
        with self.connect() as db:
            return bool(db.execute("SELECT 1 FROM prospects WHERE phone=? AND outbound_status IN ('SENT','REPLIED') LIMIT 1", (phone,)).fetchone())

    def mark_prospect_send(self, prospect_id, status, error=None):
        if status not in ("SENDING", "SENT", "UNCERTAIN"):
            raise ValueError("Invalid outbound status")
        stamp = now()
        with self.transaction() as db:
            row = db.execute("SELECT * FROM prospects WHERE prospect_id=?", (prospect_id,)).fetchone()
            if not row:
                raise KeyError("Prospect not found")
            allowed_previous = ("NOT_SENT",) if status == "SENDING" else ("SENDING",)
            if row["outbound_status"] not in allowed_previous:
                raise ValueError("Prospect is not eligible for a first send")
            action = {"SENDING": "Operator-approved send in progress", "SENT": "Opening message sent",
                      "UNCERTAIN": "Send status uncertain; operator review required"}[status]
            db.execute("UPDATE prospects SET outbound_status=?,sent_at=CASE WHEN ?='SENT' THEN ? ELSE sent_at END,last_action=?,updated_at=? WHERE prospect_id=?",
                       (status, status, stamp, action, stamp, prospect_id))
            self._queue(db, "PROSPECT", prospect_id, stamp)

    def outbox(self, limit=100):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM sheets_outbox WHERE status='PENDING' ORDER BY updated_at LIMIT ?", (limit,))]

    def outbox_result(self, entity_type, entity_id, error=None):
        with self.transaction() as db:
            if error is None:
                db.execute("UPDATE sheets_outbox SET status='SYNCED',attempts=attempts+1,last_error=NULL,updated_at=? WHERE entity_type=? AND entity_id=?", (now(), entity_type, entity_id))
            else:
                db.execute("UPDATE sheets_outbox SET status='PENDING',attempts=attempts+1,last_error=?,updated_at=? WHERE entity_type=? AND entity_id=?", (str(error)[:1000], now(), entity_type, entity_id))

    def crm_record(self, entity_type, entity_id):
        with self.connect() as db:
            if entity_type == "PROSPECT":
                row = db.execute("SELECT * FROM prospects WHERE prospect_id=?", (entity_id,)).fetchone()
                return dict(row) if row else None
            if entity_type == "LEAD":
                row = db.execute("SELECT * FROM leads WHERE lead_id=?", (entity_id,)).fetchone()
                if not row: return None
                lead = self.lead_dict(row)
                latest_support = db.execute("SELECT status FROM support_requests WHERE lead_id=? ORDER BY created_at DESC LIMIT 1", (entity_id,)).fetchone()
                lead["support_status"] = (latest_support[0] if latest_support else "NONE")
                lead["handoff_status"] = lead["profile"].get("handoff_status", "NONE")
                lead["handoff_reason"] = lead["profile"].get("handoff_reason", "")
                return lead
            raise ValueError("Unknown CRM entity type")
