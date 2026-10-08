# WhatsApp Property Agent

## Google Sheets CRM and controlled outbound

SQLite remains canonical. The Runtime queues stable-ID Lead and Prospect upserts in SQLite, then syncs them to the existing `Leads` and `Prospects` tabs when a local Google OAuth token is available. Failed writes remain pending for `sync-sheets` retries. The adapter checks the existing headers before writing and refuses ambiguous duplicate IDs.

To connect the local Runtime, install the dependencies with `python -m pip install -r requirements.txt`, create/download a Google OAuth Desktop client JSON for the account that can edit the CRM spreadsheet, and save it to `data/lead/google-oauth-client.json` (or configure `GOOGLE_OAUTH_CLIENT_PATH`). Then run `python -m app.cli sheets-auth` and approve the Google consent prompt. The access token is stored in the ignored, permission-restricted `data/lead/google-token.json` (or `GOOGLE_TOKEN_PATH`). Run `python -m app.cli sync-sheets` to retry queued writes. The Runtime performs queued CRM syncs on startup and after handled inbound messages when authorization is available.

Controlled outbound is disabled until a test number is explicitly listed in `WHATSAPP_OUTBOUND_ALLOWLIST` and exact opening copy is approved in `OUTBOUND_OPENING_MESSAGE`. Create a Prospect with `python -m app.cli create-prospect <phone> --campaign <name> --source-detail <source>`. This creates only a `NOT_SENT` Prospect. Review the copy and run `python -m app.cli send-outbound <prospect-id>`; the command displays the recipient and exact text, then requires typing `SEND` immediately before one message. A `SENDING` or `UNCERTAIN` Prospect cannot be sent again automatically. Outbound replies are monitored for sent Prospects and convert once into an `OUTBOUND` Lead.

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
