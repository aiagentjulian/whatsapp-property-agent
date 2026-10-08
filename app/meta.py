"""Minimal WhatsApp Cloud API client."""
import json
import urllib.error
import urllib.request


class MetaCloudAPI:
    def __init__(self, config):
        self.token = config["meta_access_token"]
        self.phone_number_id = config["meta_phone_number_id"]
        self.version = config.get("meta_graph_api_version", "v25.0")
        if not self.token or not self.phone_number_id:
            raise RuntimeError("Meta Cloud API credentials are not configured")

    def send_text(self, recipient, body):
        url = "https://graph.facebook.com/%s/%s/messages" % (self.version, self.phone_number_id)
        payload = {"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": body}}
        request = urllib.request.Request(
            url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Do not include provider response text, which could contain request details.
            raise RuntimeError("Meta Graph API rejected the send (HTTP %s)" % exc.code) from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("Meta Graph API send outcome is unknown (%s)" % type(exc).__name__) from None
        messages = result.get("messages") or []
        if not messages or not messages[0].get("id"):
            raise RuntimeError("Meta Graph API accepted no message ID; send outcome is uncertain")
        return {"message_id": messages[0]["id"], "status": "accepted"}
