# WhatsApp Property Agent

This repository contains the Python property-sales Agent, Sales Brain, Skills, Pearlmont Knowledge, SQLite Lead and support workflows, and Google Sheets CRM adapter. The WhatsApp Web transport has been removed; this project currently does not listen for WhatsApp messages or send replies.

## Setup

Requires Python 3.9+.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in the shell or local `.env`. The Agent is pinned to `gpt-6-luna` with Medium reasoning by default. Keep `.env`, OAuth credentials, OAuth tokens, and the local SQLite database private.

## Local operations

```sh
python -m app.cli status
python -m app.cli leads
python -m app.cli lead <lead-id>
python -m app.cli history <lead-id>
python -m app.cli support
python -m app.cli resolve-support <request-id> --result "Verified answer"
python -m app.cli handoffs
python -m app.cli usage
python -m app.cli knowledge-check "What is the project location?"
```

SQLite remains canonical. Google Sheets syncs stable-ID Lead and Prospect upserts to the existing CRM tabs when a local OAuth token is available. Configure the OAuth Desktop client at `data/lead/google-oauth-client.json` (or set `GOOGLE_OAUTH_CLIENT_PATH`), then run:

```sh
python -m app.cli sheets-auth
python -m app.cli sync-sheets
```

The access token is stored in ignored, permission-restricted `data/lead/google-token.json` (or `GOOGLE_TOKEN_PATH`). Failed CRM writes remain queued in SQLite for later `sync-sheets` retries.

Prospects can be reviewed and created locally. `create-prospect` only creates a `NOT_SENT` Prospect after checking the exact `WHATSAPP_OUTBOUND_ALLOWLIST`; it does not send a message.

The core sales journey is `UNDERSTAND → QUALIFY → POSITION → HANDLE → INTENT → CLOSE`.
