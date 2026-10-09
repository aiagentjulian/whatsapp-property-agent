import hashlib
import logging
import re

from .agent import SalesAgent
from .db import Store
from .provider import PROFILE_FIELDS

logger = logging.getLogger(__name__)


def normalize(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def support_signature(support):
    tokens = set((normalize(support.get("subject", "")) + " " + normalize(support.get("requested_fact", ""))).split())
    synonyms = {"available": "availability", "confirm": "verify", "check": "verify", "checked": "verify", "prices": "price", "pricing": "price"}
    ignored = {"can", "you", "please", "the", "is", "still", "for", "of", "to", "a", "an", "unit", "confirm", "check", "whether", "if"}
    tokens = {synonyms.get(token, token) for token in tokens if token not in ignored}
    return "%s|%s" % (support.get("support_type", "OTHER"), " ".join(sorted(tokens)))


class Runtime:
    def __init__(self, config, store=None, agent=None):
        self.config = config
        self.store = store or Store(config["database"])
        self.agent = agent or SalesAgent(config)
        self._sheets_client = None
        self._sheets_checked = False

    def sync_crm(self):
        from .sheets import SheetsCRM, sync_pending
        if not self._sheets_checked:
            try:
                self._sheets_client = SheetsCRM.from_token(self.config)
            except Exception as exc:
                self._sheets_checked = True
                return {"status": "PENDING", "error": str(exc), "pending": len(self.store.outbox())}
            self._sheets_checked = True
        if self._sheets_client is None:
            return {"status": "AUTH_REQUIRED", "pending": len(self.store.outbox())}
        results = sync_pending(self.store, self._sheets_client)
        return {"status": "SYNCED" if all(x["status"] == "SYNCED" for x in results) else "PENDING", "results": results}

    def process_inbound(self, contact, external_id, body, send_reply=False, sender=None, diagnostic_id=None):
        message_ref = hashlib.sha256(str(external_id).encode("utf-8")).hexdigest()[:12] if external_id else "missing"
        allowed = self.allowed(contact)
        if diagnostic_id:
            logger.info("meta_webhook request_id=%s message_ref=%s stage=allowlist decision=%s",
                        diagnostic_id, message_ref, "allow" if allowed else "deny")
        if not allowed:
            return {"status": "blocked", "reason": "contact_not_allowlisted"}
        try:
            lead, inserted, message_id = self.store.ingest(contact, external_id, body)
        except Exception as exc:
            if diagnostic_id:
                logger.error("meta_webhook request_id=%s message_ref=%s stage=sqlite_ingestion outcome=error error_type=%s",
                             diagnostic_id, message_ref, type(exc).__name__)
            raise
        if diagnostic_id:
            logger.info("meta_webhook request_id=%s message_ref=%s stage=sqlite_ingestion outcome=%s",
                        diagnostic_id, message_ref, "inserted" if inserted else "duplicate")
        if not inserted:
            return {"status": "duplicate", "lead_id": lead["lead_id"]}
        if lead["owner"] != "AI" or lead["ai_session_status"] != "ACTIVE":
            return {"status": "suppressed", "reason": "ai_session_ended", "lead_id": lead["lead_id"]}
        profile = lead["profile"]
        history = self.store.history(lead["lead_id"])
        supports = self.store.support_context(lead["lead_id"])
        if diagnostic_id:
            logger.info("meta_webhook request_id=%s message_ref=%s stage=gpt_call outcome=started",
                        diagnostic_id, message_ref)
        try:
            decision, usage = self.agent.decide(body, profile, history, supports)
        except Exception as exc:
            if diagnostic_id:
                logger.error("meta_webhook request_id=%s message_ref=%s stage=gpt_call outcome=error error_type=%s",
                             diagnostic_id, message_ref, type(exc).__name__)
            raise
        if diagnostic_id:
            logger.info("meta_webhook request_id=%s message_ref=%s stage=gpt_call outcome=complete",
                        diagnostic_id, message_ref)
        self.store.record_usage(lead["lead_id"], self.config["model"], usage)
        updates = {key: value for key, value in decision["lead_updates"].items() if key in PROFILE_FIELDS and value is not None}
        if decision["action"] == "APPOINTMENT_HANDOFF":
            readiness = updates.get("appointment_readiness") or profile.get("appointment_readiness")
            if readiness not in ("READY_FOR_APPOINTMENT", "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED"):
                raise ValueError("Appointment handoff is blocked until the persisted readiness state is appointment-ready")
        # System fields are restored from persisted authority after every model update.
        updates.update({"lead_id": lead["lead_id"], "phone": lead["phone"], "lead_source": lead["lead_source"], "owner": lead["owner"], "ai_session_status": lead["ai_session_status"]})
        self.store.update_profile(lead["lead_id"], updates)
        action = decision["action"]
        if action == "SUPPORT_REQUEST":
            request = dict(decision["support_request"])
            request["signature"] = support_signature(request)
            support, created = self.store.create_support(lead["lead_id"], request)
            result = {"status": "support_requested" if created else "support_reused", "support_request_id": support["request_id"], "lead_id": lead["lead_id"]}
        elif action in ("APPOINTMENT_HANDOFF", "MANDATORY_HANDOFF"):
            formal_type = "APPOINTMENT_HANDOFF" if action == "APPOINTMENT_HANDOFF" else "MANDATORY_OPERATIONAL_HANDOFF"
            success = self.store.formal_handoff(lead["lead_id"], formal_type, decision["handoff_reason"], decision.get("handoff_details") or body)
            return {"status": "handed_off" if success else "handoff_suppressed", "lead_id": lead["lead_id"], "reply": None}
        else:
            result = {"status": "reply_ready", "lead_id": lead["lead_id"]}
        reply = decision["reply"].strip()
        if reply:
            # Recheck persisted authority immediately before creating/sending an outbound message.
            current = self.store.get(lead["lead_id"])
            if current["owner"] != "AI" or current["ai_session_status"] != "ACTIVE":
                return {"status": "suppressed", "reason": "ownership_changed_before_send", "lead_id": lead["lead_id"]}
            out_id = self.store.add_message(lead["lead_id"], "OUTBOUND", reply, "pending_send" if send_reply else "not_sent")
            if send_reply:
                if diagnostic_id:
                    logger.info("meta_webhook request_id=%s message_ref=%s stage=meta_send outcome=started",
                                diagnostic_id, message_ref)
                try:
                    send_result = sender(contact, reply)
                except Exception as exc:
                    self.store.update_send_status(out_id, "uncertain")
                    if diagnostic_id:
                        logger.error("meta_webhook request_id=%s message_ref=%s stage=meta_send outcome=uncertain error_type=%s",
                                     diagnostic_id, message_ref, type(exc).__name__)
                    return dict(result, reply=None, send_status="uncertain", error=str(exc), operator_review_required=True)
                external_id = send_result.get("message_id") if isinstance(send_result, dict) else None
                self.store.update_send_status(out_id, "sent", external_id)
                if diagnostic_id:
                    logger.info("meta_webhook request_id=%s message_ref=%s stage=meta_send outcome=accepted",
                                diagnostic_id, message_ref)
                result["send_status"] = "sent"
            result["reply"] = reply
        return result

    def allowed(self, contact):
        target = normalize(contact)
        inbound = any(target == normalize(value) for value in self.config["allowlist"])
        outbound = any(target == normalize(value) for value in self.config.get("outbound_allowlist", []))
        return bool(target) and (inbound or (outbound and self.store.has_active_outbound_prospect(contact)))
