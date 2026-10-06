# Skill: Sync Google Sheet

## Purpose

Use this skill to keep the human-facing `Leads` Google Sheet synchronized with the canonical Lead Profile.

This skill manages only real Leads that have entered a two-way conversation.

It does not manage outbound prospect lists.

---

## Core Principle

The Lead Profile is the canonical working customer state for the Agent.

The `Leads` Google Sheet is the human-facing CRM view of that state.

The Agent should update the Lead Profile first. The backend then applies a structured patch to the matching row in Google Sheet.

Do not let the LLM freely rewrite spreadsheet rows as unstructured text.

---

# Leads vs Prospects

`Leads` and outbound `Prospects` are separate operational objects.

## Prospect

A Prospect is a person the business intends to contact outbound but who has not yet entered a real two-way conversation.

Prospects belong to a separate outbound Google Sheet or sending source.

Typical Prospect data may include:

- name
- phone
- campaign
- outbound message or hook
- sent status
- sent timestamp
- delivery or send error
- reply status when operationally useful

The Prospect sheet is outside the scope of this skill.

The LLM does not manage Prospect records.

The sending system is responsible for updating deterministic outbound fields such as:

- `SENT`
- `FAILED`
- `sent_at`
- send error information

Sending an outbound message does not create a Lead.

## Lead

A person becomes a Lead only when a real two-way conversation begins.

Rules:

- inbound customer sends first message -> create Lead
- outbound Prospect replies -> create Lead

For an outbound conversion, preserve known system metadata such as source and campaign when creating the Lead.

---

# Scope

This skill manages only the `Leads` Google Sheet.

There should be one current row per Lead.

Do not create a separate handoff sheet, conversation sheet, or duplicate CRM row for the same active Lead unless the product architecture is intentionally changed later.

---

# When to Create a Lead Row

Create a row when the Lead Profile is first created.

## INBOUND

Customer initiates a real conversation:

```text
customer first inbound message
-> create Lead Profile
-> create Leads row
-> lead_source = INBOUND
```

## OUTBOUND

Business sends outbound message:

```text
message sent
-> remain Prospect
-> no Leads row yet
```

Customer replies:

```text
outbound Prospect reply
-> create Lead Profile
-> create Leads row
-> lead_source = OUTBOUND
```

Do not create Leads rows for people who were merely sent a campaign message and never replied.

---

# Row Identity

The backend must update the existing row whenever possible.

Preferred lookup order:

1. `lead_id`
2. canonical normalized phone number when needed as a fallback

Do not create a new row just because the same Lead re-enters through another touchpoint.

If the system identifies the same Lead, update the existing row.

---

# Recommended Leads Columns

The first version should stay compact and human-readable.

Recommended columns:

- `Lead ID`
- `Phone`
- `Name`
- `Source`
- `Source Detail`
- `Campaign`
- `Purpose`
- `Budget`
- `Financing`
- `Preferred Location`
- `Property Preference`
- `Timeline`
- `Motivation`
- `Concern`
- `Stage`
- `Intent`
- `Fit`
- `Need`
- `Last Progress`
- `Next Action`
- `Owner`
- `AI Status`
- `Handoff Status`
- `Handoff Reason`
- `Updated At`

The exact implementation may map these display columns to canonical fields from `brain/LEAD_PROFILE.md`.

Do not add spreadsheet columns casually when the information already belongs inside an existing canonical Lead Profile field.

---

# Field Ownership

Different fields have different authorities.

## System-controlled

Examples:

- Lead ID
- Phone
- Source
- Source Detail when derived from acquisition metadata
- Campaign when derived from campaign metadata
- timestamps
- technical identifiers

The LLM must not invent or overwrite these values.

## Agent-maintained customer state

Examples:

- Purpose
- Budget
- Financing
- Preferred Location
- Property Preference
- Timeline
- Motivation
- Concern
- Stage
- Intent
- Fit
- Need
- Last Progress
- Next Action
- Handoff Status
- Handoff Reason

These come from structured Lead Profile updates.

## Human-controlled control field

`Owner` is the primary manual control field.

Allowed values:

- `AI`
- `HUMAN`

In Google Sheet, `Owner` should use a dropdown rather than free text.

The Agent may read `Owner` but must not autonomously change `HUMAN` back to `AI`.

A human may manually return ownership to `AI` as an exception operation.

---

# AI Status

`AI Status` should be system-derived and human-readable.

Recommended values:

- `ACTIVE`
- `PAUSED`

Mapping:

```text
Owner = AI
-> AI Status = ACTIVE

Owner = HUMAN
-> AI Status = PAUSED
```

Humans should normally not edit `AI Status` directly.

It reflects the effective runtime state.

---

# Owner Synchronization

The backend should poll the `Leads` Google Sheet every 30 seconds for Owner changes.

The backend should also perform an immediate Owner check whenever a new WhatsApp customer message arrives.

This second check is authoritative for reply safety.

Flow:

```text
customer message arrives
-> load Lead
-> read current Owner

Owner = AI
-> continue Agent flow

Owner = HUMAN
-> record message/context
-> do not generate or send an automatic AI reply
```

This prevents the AI from replying during the delay between scheduled polling intervals.

---

# Handoff Behaviour

When handoff is executed:

```text
Owner = HUMAN
AI Status = PAUSED
```

The same Lead row is updated.

Do not create another Lead Profile or a separate handoff record merely for normal ownership transfer.

The Sheet should reflect useful handoff context through fields such as:

- Handoff Status
- Handoff Reason
- Last Progress
- Next Action
- Updated At

Once `Owner = HUMAN`, repeated customer messages must not repeatedly fire the same handoff customer message.

---

# Return to AI

Return to AI is supported but is an exception operation in V1.

A human may manually change:

```text
Owner = HUMAN
```

to:

```text
Owner = AI
```

The backend detects the change and restores:

```text
AI Status = ACTIVE
```

Important rules:

- the LLM cannot decide on its own to return ownership to AI
- changing Owner back to AI does not automatically send a customer message
- the system must not replay or individually answer every message that arrived while HUMAN owned the Lead
- future AI responses should use the latest complete conversation context

Normal handoff flow should not depend on Return to AI.

---

# Patch-Only Sync

Do not rewrite the entire spreadsheet row on every turn unless the runtime requires it.

Preferred flow:

```text
meaningful customer message
-> update Lead Profile with structured patch
-> map changed canonical fields to Sheet columns
-> update only changed cells
-> update Updated At
```

This reduces accidental overwrites and preserves human-controlled fields such as `Owner`.

Example conceptual patch:

```json
{
  "lead_id": "lead_123",
  "sheet_updates": {
    "Budget": "RM700k-RM900k",
    "Purpose": "OWN_STAY",
    "Intent": "HIGH",
    "Last Progress": "Customer confirmed budget and wants to compare 3BR options.",
    "Next Action": "Recommend the most suitable 3BR option."
  }
}
```

The backend, not the LLM, performs the actual Google Sheets write.

---

# Do Not Overwrite Human Control

A Lead Profile sync must never accidentally overwrite a human `Owner` change with a stale Agent value.

Before writing Agent-generated patches, preserve the current Sheet-controlled `Owner` unless a valid handoff operation explicitly changes it to `HUMAN`.

`HUMAN -> AI` must come from an explicit human or system-authorized control action, not an ordinary profile patch.

---

# Missing and Unknown Values

Do not fill empty Sheet cells merely for completeness.

If the Lead Profile does not reliably know a value:

- leave the mapped cell blank, or
- preserve the existing value when no update is intended

Do not write guessed values.

Do not repeatedly replace unknown values with noisy text such as `not provided yet` unless the UI design specifically requires it.

---

# Sync Failure Behaviour

A Google Sheet write failure must not cause the Agent to invent a successful sync.

If the Sheet update fails:

- preserve the canonical Lead Profile state in the main runtime/store
- log the sync failure
- retry through backend sync logic as appropriate
- do not ask the customer to repeat information solely because the Sheet failed

Google Sheet is a human-facing CRM surface, not the sole source of conversation truth.

---

# Separation of Responsibilities

## LLM / Agent

Responsible for:

- understanding the conversation
- producing structured Lead Profile updates
- deciding next action through the appropriate skill
- reading effective Owner state before normal progression

Not responsible for:

- directly editing arbitrary spreadsheet cells
- deciding whether an outbound send technically succeeded
- creating fake Prospect states
- automatically returning HUMAN ownership to AI

## Backend

Responsible for:

- Google Sheets API access
- row lookup
- row creation
- patch application
- deterministic system metadata
- Owner polling every 30 seconds
- immediate Owner check on inbound WhatsApp messages
- deriving AI Status
- preserving human-controlled values
- logging and retrying sync failures

## Outbound Sending System

Responsible for the separate Prospect source/list and deterministic sending state.

Examples:

```text
send succeeds
-> Sent Status = SENT
-> Sent At = timestamp

send fails
-> Sent Status = FAILED
-> Error = reason
```

This does not require an LLM.

---

# V1 Summary

The intended architecture is:

```text
Prospects Sheet
-> outbound sending system
-> deterministic send status update
-> customer replies
-> create Lead Profile
-> create row in Leads Sheet
-> AI Sales Agent manages conversation state
-> backend syncs Lead Profile patches to Leads
```

Human ownership control:

```text
Owner = AI
-> AI active

Owner = HUMAN
-> AI paused
```

Synchronization safety:

```text
30-second Owner polling
+
immediate Owner check when a customer message arrives
```

The result should remain simple:

- Prospects are outreach operations
- Leads are real conversations
- the LLM maintains customer understanding
- the backend maintains spreadsheet synchronization
- humans control ownership through one clear dropdown
