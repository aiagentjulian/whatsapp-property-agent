# WhatsApp Property Agent

This repository contains the Python property-sales Agent, Sales Brain, Skills, Pearlmont Knowledge, SQLite Lead and support workflows, and Google Sheets CRM adapter. The project uses Meta WhatsApp Cloud API webhooks for incoming messages and replies; WhatsApp Web transport is not used.

## Setup

Requires Python 3.9+.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in the shell or local `.env`. The Agent is pinned to `gpt-6-luna` with High reasoning by default. An existing local `.env` or process-level `RUNTIME_REASONING` value overrides the default, so verify the effective value with `python -m app.cli status` after updating and restarting the Runtime. Keep `.env`, OAuth credentials, OAuth tokens, and the local SQLite database private.

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

## Golden Conversations V1 (draft, zero-API reference)

The simplified sales guidance is at `brain/SALES_PLAYBOOK_V1.md` and
nine annotated candidate dialogues are at `brain/golden_conversations_v1.json`.
These are draft behavioral references, not proven sales techniques.
On the **test branch only**, Luna receives at most two examples selected for
the current workflow stage, with a clear instruction to learn from the sales
decision rather than imitate the words. Set `GOLDEN_GUIDANCE_MODE=off` to
disable them. No examples have been added to production `main`.

```sh
python -m app.golden_cases --check
python -m unittest app.test_runtime
```

The first command verifies the bank's structure and expected sales-workflow
stages using **zero API calls**, and the second runs existing local tests.
For the **direct Golden Loop** (no fresh legacy A/B), run:

```sh
python -m app.sales_simulation --dry-run
python -m app.sales_simulation --phase golden_initial
# After reviewing and, only if warranted, making one focused change:
python -m app.sales_simulation --phase golden_retest
python -m app.sales_simulation --phase golden_holdout
```

See `docs/sales-workflow-v1-loop.md` for its strict 40 API-attempt cap,
new isolated ledger, acceptance criteria and full diagnosis requirements.
The `golden_initial/retest/holdout` commands use real API tokens; dry-run
and corpus checks do not. Do not change `main`, send WhatsApp messages
or reset real Leads while evaluating the bank.

## Sales Core V2: local model evaluation and clean test sessions

The Runtime loads a compact Sales Brain, verified factual Knowledge, recent
conversation, and at most two focused selling possibilities. It records an
internal customer signal and sales move alongside each reply. These are
decision aids, not customer-facing scripts.

To test real GPT-6 Luna / High responses **without sending WhatsApp messages
or writing to the production CRM**, run:

```sh
python -m app.eval_sales --scenario family
python -m app.eval_sales --scenario all
```

Review the entire replies for relevance, repetition, natural pacing, factual
accuracy and progression. A successful API call or unit test does **not** prove
sales quality.

For a fresh WhatsApp test, stop the live Runtime first. Register **only** the
designated inbound test number in `WHATSAPP_TEST_CONTACTS` in the private
local environment. It must exactly match the phone stored by the Runtime.
Then run:

```sh
python -m app.cli reset-test-lead --phone "<TEST_PHONE>" --confirm-phone "<TEST_PHONE>"
python -m app.cli status
```

The reset empties that test lead's conversation, profile changes, support and
handoff state without modifying other contacts. It retains the same Lead ID
so the Google Sheets upsert updates the existing row rather than creating
duplicate test leads. The reset profile is queued for the next CRM sync; run
`python -m app.cli sync-sheets` when an authenticated CRM client is available.

Never reset a genuine customer. A new `Hi` never automatically resets a
conversation. Restart the Runtime before resuming WhatsApp tests, and repeat
the manual reset before each genuinely fresh test.

The default model reasoning was raised to High, but an existing local
`RUNTIME_REASONING=medium` in `.env` or the process environment takes
precedence. Change that local value to `high` and restart to make it effective.
