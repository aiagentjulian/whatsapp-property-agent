# WhatsApp Property Agent

Local WhatsApp Web property-sales agent for controlled testing with allowlisted contacts. The runtime uses the existing Brain, Skills and Pearlmont Knowledge as its source of truth.

## Setup

Requires Python 3.9+, Node.js, and a local headed browser supported by Playwright.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

Set `OPENAI_API_KEY` in the shell or `.env`, then configure `WHATSAPP_ALLOWLIST` as a comma-separated list of exact WhatsApp contact names or phone numbers. Never commit `.env`, the browser profile, or `data/lead/agent.sqlite3`.

## Operator commands

```sh
python -m app.cli status
python -m app.cli login       # opens headed WhatsApp Web for manual QR login; does not process messages
python -m app.cli start       # starts the allowlisted listener; replies are disabled by default
python -m app.cli start --send-replies  # explicit live reply authorization required
python -m app.cli stop
python -m app.cli leads
python -m app.cli lead <lead-id>
python -m app.cli history <lead-id>
python -m app.cli support
python -m app.cli resolve-support <request-id> --result "Verified answer"
python -m app.cli handoffs
python -m app.cli usage
```

The `login` command is the Phase 1 stop point: scan the QR code locally, then stop. It will not start automated replies. Afterward, authorize controlled conversation testing separately and run `start --send-replies`.

Runtime defaults are `RUNTIME_PROVIDER=openai_api`, `RUNTIME_MODEL=gpt-6-luna`, and `RUNTIME_REASONING=medium`. The runtime never silently substitutes another model. The existing Simulator remains on its own Codex CLI / GPT-5.6 Luna configuration.

Core sales journey: `UNDERSTAND → QUALIFY → POSITION → HANDLE → INTENT → CLOSE`.
