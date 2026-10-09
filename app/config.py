import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path=None):
    """Load simple KEY=value entries without overriding the process environment."""
    env_path = Path(path or ROOT / ".env")
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def get_config():
    load_env_file()
    model = os.getenv("RUNTIME_MODEL", "gpt-6-luna")
    provider = os.getenv("RUNTIME_PROVIDER", "openai_api")
    reasoning = os.getenv("RUNTIME_REASONING", "high")
    if provider != "openai_api":
        raise ValueError("RUNTIME_PROVIDER must be openai_api for the runtime.")
    if model != "gpt-6-luna":
        raise ValueError("This MVP is pinned to gpt-6-luna; model substitution is disabled.")
    if reasoning not in ("low", "medium", "high"):
        raise ValueError("RUNTIME_REASONING must be low, medium, or high.")
    return {
        "provider": provider,
        "model": model,
        "reasoning": reasoning,
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "database": Path(os.getenv("DATABASE_PATH", "data/lead/agent.sqlite3")),
        "allowlist": [x.strip() for x in os.getenv("WHATSAPP_ALLOWLIST", "").split(",") if x.strip()],
        "outbound_allowlist": [x.strip() for x in os.getenv("WHATSAPP_OUTBOUND_ALLOWLIST", "").split(",") if x.strip()],
        "test_contacts": [x.strip() for x in os.getenv("WHATSAPP_TEST_CONTACTS", "").split(",") if x.strip()],
        "outbound_opening_message": os.getenv("OUTBOUND_OPENING_MESSAGE", "").replace("\\n", "\n"),
        "google_oauth_client_path": Path(os.getenv("GOOGLE_OAUTH_CLIENT_PATH", "data/lead/google-oauth-client.json")),
        "google_token_path": Path(os.getenv("GOOGLE_TOKEN_PATH", "data/lead/google-token.json")),
        "meta_access_token": os.getenv("META_ACCESS_TOKEN", ""),
        "meta_phone_number_id": os.getenv("META_PHONE_NUMBER_ID", ""),
        "meta_webhook_verify_token": os.getenv("META_WEBHOOK_VERIFY_TOKEN", ""),
        "meta_graph_api_version": os.getenv("META_GRAPH_API_VERSION", "v25.0"),
        "webhook_host": os.getenv("WEBHOOK_HOST", "127.0.0.1"),
        "webhook_port": int(os.getenv("WEBHOOK_PORT", "8080")),
    }
