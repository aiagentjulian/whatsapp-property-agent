"""Local HTTP endpoints for Meta WhatsApp Cloud API webhooks."""
import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .config import get_config
from .meta import MetaCloudAPI
from .service import Runtime


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

    def handle_payload(self, payload):
        handled = 0
        ignored = 0
        entries = payload.get("entry", []) if payload.get("object") == "whatsapp_business_account" else []
        for entry in entries:
            for change in entry.get("changes", []):
                if change.get("field") != "messages":
                    ignored += 1
                    continue
                value = change.get("value") or {}
                metadata = value.get("metadata") or {}
                if metadata.get("phone_number_id") != self.config["meta_phone_number_id"]:
                    ignored += 1
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
                    if not text or not sender or not external_id:
                        ignored += 1
                        continue
                    outcome = self.runtime.process_inbound(sender, external_id, text, send_reply=True,
                                                           sender=self.meta.send_text)
                    handled += 1
                    if outcome.get("status") != "duplicate" and outcome.get("lead_id"):
                        # SQLite is canonical; the existing outbox retries a failed CRM sync later.
                        self.runtime.sync_crm()
        return {"handled": handled, "ignored": ignored}


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format, *_args):
            # Avoid logging customer content, contact details, or credentials.
            return

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
            if urlsplit(self.path).path != "/webhook":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 1_000_000:
                    self.send_error(413)
                    return
                payload = json.loads(self.rfile.read(length))
                outcome = app.handle_payload(payload)
            except (ValueError, TypeError, json.JSONDecodeError):
                self.send_error(400)
                return
            except Exception:
                # Meta retries non-2xx deliveries. Inbound IDs are persisted/deduplicated before
                # AI processing, so returning 2xx avoids duplicate sends after uncertain outcomes.
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = json.dumps(outcome).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main():
    config = get_config()
    if not config["meta_webhook_verify_token"]:
        raise SystemExit("META_WEBHOOK_VERIFY_TOKEN is required")
    app = WebhookApp(config)
    server = ThreadingHTTPServer((config["webhook_host"], config["webhook_port"]), make_handler(app))
    server.serve_forever()


if __name__ == "__main__":
    main()
