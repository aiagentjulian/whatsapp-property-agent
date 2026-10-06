# Skill — Handoff to Human

## Purpose

This skill executes a human handoff after the Brain has already determined that human involvement is appropriate.

It does not decide whether a handoff should happen. That judgment is defined by `brain/HANDOFF_RULES.md`.

This skill is responsible for changing ownership, updating the existing Lead Profile, pausing AI auto-replies, synchronising Google Sheet control fields, and optionally sending one natural customer-facing handoff message.

The handoff should be simple, explicit and non-duplicative.

---

## Core Principle

One customer keeps one Lead Profile.

A handoff does not create a second customer record, a second summary, or a separate handoff profile.

Instead, update the existing Lead Profile so that a human can continue from the same state.

The Lead Profile remains the single customer state.

---

## Trigger

This skill may run when the current Lead Profile indicates:

- `handoff_status = RECOMMENDED`, or
- `handoff_status = REQUIRED`

These states are determined by the Brain.

### `RECOMMENDED`

Human involvement may improve the sales process, but immediate transfer is not mandatory.

The AI may continue temporarily if doing so remains useful and safe.

### `REQUIRED`

The AI should stop autonomous sales progression and prepare the lead for human ownership.

Typical examples include:

- customer explicitly asks for a human
- special discount or rebate negotiation
- commercial terms require approval
- latest availability requires confirmation
- legal or financing questions exceed the available knowledge
- sensitive complaint or dispute
- final booking or reservation actions require human handling

---

## Ownership

The runtime ownership field is:

`owner`

Allowed V1 values:

- `AI`
- `HUMAN`

Normal autonomous operation:

`owner = AI`

Formal handoff:

`owner = HUMAN`

Once `owner = HUMAN`:

- AI auto-replies must be paused
- the AI must not compete with the human agent
- the conversation may still be recorded
- the Lead Profile may still be updated from new customer information
- the AI may continue internal summarisation if useful
- the AI must not autonomously resume customer messaging

---

## Lead Profile Update

Do not create a new profile.

Update the existing Lead Profile with the minimum useful handoff state.

Typical fields include:

- `owner = HUMAN`
- `handoff_status = HANDED_OFF`
- `handoff_reason`
- `last_progress`
- `next_action`
- `updated_at`

Keep these values concise and operational.

Example:

```text
owner = HUMAN
handoff_status = HANDED_OFF
handoff_reason = promotion requires human confirmation
last_progress = Customer is comparing 3-bedroom options and asked whether an additional rebate is available.
next_action = Human to confirm the latest commercial package and continue toward viewing if the customer remains interested.
```

Do not duplicate the full customer profile inside `handoff_reason`, `last_progress`, or `next_action`.

---

## Google Sheet Behaviour

The Google Sheet `Leads` tab mirrors the current Lead Profile.

When handoff occurs, update the same lead row.

Important control and status fields should reflect:

- `Owner = HUMAN`
- `AI Status = PAUSED`
- `Handoff Status = HANDED_OFF`
- `Handoff Reason`
- `Last Progress`
- `Next Action`
- `Updated At`

Do not create a separate Handoff Sheet for V1.

Do not create a duplicate row for the same customer.

The human agent should be able to open the existing lead row and understand the current state directly.

---

## Customer-Facing Handoff Message

A handoff may include one short customer-facing message when useful.

The message should feel like normal service escalation, not a system failure.

Prefer language such as:

```text
Let me confirm the latest package for you so I don't give you the wrong information. I'll get my colleague to follow up with you.
```

Avoid language such as:

```text
I cannot answer this.
```

or:

```text
The AI is unable to continue.
```

The customer-facing message should:

- acknowledge the current issue
- explain that confirmation or human help is needed
- remain concise
- avoid exposing internal system states

Do not send repeated handoff messages if the lead is already under human ownership.

---

## Duplicate Handoff Protection

If:

`owner = HUMAN`

then a new customer message must not trigger another handoff message.

Do not repeatedly update the customer with the same transfer notice.

The system should recognise that the human already owns the lead.

---

## Human-Controlled Owner Field

In V1, the `Owner` field in Google Sheet is a human-controlled dropdown.

Allowed values:

- `AI`
- `HUMAN`

The AI may read this field.

The AI must not autonomously change `HUMAN` back to `AI`.

A human or deterministic system action is required for that transition.

---

## Owner Polling

For V1, the backend should poll the Google Sheet owner state approximately every 30 seconds.

This keeps the implementation simple while allowing humans to control ownership without a dedicated dashboard.

In addition to the periodic poll, when a new customer WhatsApp message arrives, the backend should check the current `Owner` before calling the LLM or sending any automatic reply.

This immediate message-time check is required so that a recent human takeover is respected even if the 30-second polling interval has not completed yet.

Runtime behaviour:

```text
Customer message arrives
→ check Owner
→ if AI: normal agent flow
→ if HUMAN: record message, do not auto-reply
```

---

## Return to AI

Return to AI is supported in V1 only as an optional manual exception.

It is not part of the normal handoff path.

A human may change:

`Owner = HUMAN`

to:

`Owner = AI`

through the Google Sheet dropdown.

The backend may detect this during the next polling cycle.

The AI must not decide by itself that the human is finished.

The AI must not automatically switch ownership back to itself.

---

## Return-to-AI Behaviour

Changing `Owner` back to `AI` means that future customer messages may again be handled by the AI.

It does not mean the AI should immediately send a new message.

Do not automatically replay or answer every customer message that arrived while the human owned the lead.

When the next customer message arrives after ownership returns to AI:

1. load the latest Lead Profile,
2. load the relevant recent conversation context,
3. understand what the human already handled,
4. continue from the current state,
5. avoid reopening issues that have already been resolved.

Return to AI should be conservative and simple in V1.

---

## AI Status

For clarity, the runtime or Google Sheet may expose:

- `ACTIVE`
- `PAUSED`

Mapping:

```text
Owner = AI     → AI Status = ACTIVE
Owner = HUMAN  → AI Status = PAUSED
```

`AI Status` should normally be system-managed rather than manually edited.

---

## Do Not Handoff Too Early

This skill should only execute after the Brain has already determined that handoff is appropriate.

Do not use this skill merely because:

- a customer asks a normal property question
- the customer raises a standard objection
- the customer is still exploring
- the customer asks for information that exists in project knowledge
- the customer has not yet provided all qualification fields

The AI should remain useful rather than becoming a receptionist that constantly passes customers to humans.

---

## System-Controlled vs LLM-Controlled State

System-controlled or human-controlled fields should not be guessed by the LLM.

Examples include:

- `owner`
- phone number
- lead source
- campaign routing metadata
- AI pause/resume state

The LLM may recommend a handoff and provide the reason.

The runtime is responsible for applying ownership changes and enforcing pause behaviour.

---

## Relationship to Other Files

`brain/HANDOFF_RULES.md` defines when human involvement is appropriate.

`brain/LEAD_PROFILE.md` defines the persistent customer state.

`skills/update-lead-profile.md` defines how that customer state is updated.

`skills/decide-next-action.md` may select handoff as the most useful next action.

`skills/handoff-to-human.md` executes the transfer once the decision has been made.

`skills/sync-google-sheet.md` will define the detailed mapping between Lead Profile fields and the Google Sheet.

---

## Final Principle

Handoff is an ownership change, not a second customer record.

Keep one Lead Profile.

Update the same Google Sheet row.

Pause the AI when a human owns the lead.

Do not repeat the handoff message.

Return to AI is manual and exceptional in V1.
