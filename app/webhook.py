"""Local HTTP endpoints for Meta WhatsApp Cloud API webhooks."""
import hmac
import hashlib
import json
import logging
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .config import get_config
from .meta import MetaCloudAPI
from .service import Runtime

logger = logging.getLogger(__name__)


def _message_ref(external_id):
    """Return a stable, non-reversible log reference for a Meta message ID."""
    return hashlib.sha256(str(external_id).encode("utf-8")).hexdigest()[:12]


class WebhookApp:
    def __init__(self, config, runtime=None, meta=None):
        self.config = config
        self.runtime = runtime or Runtime(config)
        self.meta = meta or MetaCloudAPI(config)

    def verify(self, query):
        values = parse_qs(query)
        mode = (values.get("hub.mode") or [""])[0]
        supplied = (values.get("hub.verify_token") or [""])[0]
        challenge = (values.get("hub.challenge") or [""])[0]
        expected = self.config["meta_webhook_verify_token"]
        if mode == "subscribe" and expected and hmac.compare_digest(supplied, expected):
            return challenge
        return None

    def handle_payload(self, payload, request_id=None):
        handled = 0
        ignored = 0
        entries = payload.get("entry", []) if isinstance(payload, dict) and payload.get("object") == "whatsapp_business_account" else []
        logger.info("meta_webhook request_id=%s stage=payload_parsed object=%s entries=%d",
                    request_id, payload.get("object") if isinstance(payload, dict) else "invalid", len(entries))
        for entry in entries:
            for change in entry.get("changes", []):
                if change.get("field") != "messages":
                    ignored += 1
                    logger.info("meta_webhook request_id=%s stage=event_ignored reason=unsupported_field", request_id)
                    continue
                value = change.get("value") or {}
                metadata = value.get("metadata") or {}
                if metadata.get("phone_number_id") != self.config["meta_phone_number_id"]:
                    ignored += 1
                    logger.info("meta_webhook request_id=%s stage=event_ignored reason=phone_number_id_mismatch", request_id)
                    continue
                for status in value.get("statuses", []) or []:
                    mapped = {"sent": "sent", "delivered": "delivered", "read": "read", "failed": "failed"}.get(status.get("status"))
                    if mapped and status.get("id"):
                        self.runtime.store.update_status_by_external_id(status["id"], mapped)
                contacts = {item.get("wa_id"): item for item in (value.get("contacts") or []) if item.get("wa_id")}
                for message in value.get("messages", []) or []:
                    text = message.get("text", {}).get("body") if message.get("type") == "text" else None
                    sender = message.get("from")
                    external_id = message.get("id")
                    message_ref = _message_ref(external_id) if external_id else "missing"
                    logger.info("meta_webhook request_id=%s message_ref=%s stage=message_parsed type=%s",
                                request_id, message_ref, message.get("type", "unknown"))
                    if not text or not sender or not external_id:
                        ignored += 1
                        logger.info("meta_webhook request_id=%s message_ref=%s stage=message_ignored reason=unsupported_or_incomplete",
                                    request_id, message_ref)
                        continue
                    outcome = self.runtime.process_inbound(sender, external_id, text, send_reply=True,
                                                           sender=self.meta.send_text, diagnostic_id=request_id)
                    handled += 1
                    logger.info("meta_webhook request_id=%s message_ref=%s stage=message_complete outcome=%s",
                                request_id, message_ref, outcome.get("status", "unknown"))
                    if outcome.get("status") != "duplicate" and outcome.get("lead_id"):
                        # SQLite is canonical; the existing outbox retries a failed CRM sync later.
                        try:
                            crm_result = self.runtime.sync_crm()
                            logger.info("meta_webhook request_id=%s message_ref=%s stage=crm_sync outcome=%s",
                                        request_id, message_ref, crm_result.get("status", "unknown"))
                        except Exception as exc:
                            logger.error("meta_webhook request_id=%s message_ref=%s stage=crm_sync outcome=error error_type=%s",
                                         request_id, message_ref, type(exc).__name__)
                            raise
        return {"handled": handled, "ignored": ignored}


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format, *_args):
            # Request-scoped diagnostics below deliberately exclude request bodies and URLs.
            return

        def respond(self, request_id, status, body=b"", content_type=None, outcome="complete"):
            self.send_response(status)
            if content_type:
                self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)
            logger.info("meta_webhook request_id=%s stage=response http_status=%d outcome=%s",
                        request_id, status, outcome)

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path != "/webhook":
                self.send_error(404)
                return
            challenge = app.verify(parsed.query)
            if challenge is None:
                self.send_error(403)
                return
            body = challenge.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            request_id = uuid.uuid4().hex[:12]
            parsed = urlsplit(self.path)
            length_header = self.headers.get("Content-Length", "0")
            logger.info("meta_webhook request_id=%s stage=request_arrived method=POST path=%s content_length=%s",
                        request_id, parsed.path, length_header)
            if parsed.path != "/webhook":
                self.respond(request_id, 404, outcome="not_found")
                return
            try:
                length = int(length_header)
                if length < 1 or length > 1_000_000:
                    self.respond(request_id, 413, outcome="invalid_content_length")
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    self.respond(request_id, 400, outcome="invalid_payload_type")
                    return
                logger.info("meta_webhook request_id=%s stage=json_parsed", request_id)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                logger.warning("meta_webhook request_id=%s stage=json_parse outcome=error error_type=%s",
                               request_id, type(exc).__name__)
                self.respond(request_id, 400, outcome="invalid_json")
                return
            try:
                outcome = app.handle_payload(payload, request_id=request_id)
            except Exception as exc:
                # Meta retries non-2xx deliveries. Inbound IDs are persisted/deduplicated before
                # AI processing, so returning 2xx avoids duplicate sends after uncertain outcomes.
                logger.error("meta_webhook request_id=%s stage=payload_processing outcome=error error_type=%s",
                             request_id, type(exc).__name__)
                self.respond(request_id, 200, outcome="processing_error_acknowledged")
                return
            body = json.dumps(outcome).encode("utf-8")
            self.respond(request_id, 200, body, "application/json", outcome="processed")

    return Handler


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = get_config()
    if not config["meta_webhook_verify_token"]:
        raise SystemExit("META_WEBHOOK_VERIFY_TOKEN is required")
    app = WebhookApp(config)
    server = ThreadingHTTPServer((config["webhook_host"], config["webhook_port"]), make_handler(app))
    server.serve_forever()


if __name__ == "__main__":
    main()
