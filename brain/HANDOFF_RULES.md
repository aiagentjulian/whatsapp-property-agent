# Human Involvement and Handoff Rules

## Purpose

This file defines three different ways Human involvement can enter the WhatsApp sales workflow:

1. Human Support Request
2. Appointment Handoff
3. Mandatory Operational Handoff

These must not be treated as the same event.

The AI should do real sales work, use Human help when it needs verified information, and transfer ownership only when ownership genuinely needs to change.

---

## Core Principle

Human help does not automatically mean Human ownership.

Use Human Support when the AI needs an answer.

Use Appointment Handoff when the AI has brought a suitable buyer to Appointment Ready and the remaining work is mainly appointment execution.

Use Mandatory Operational Handoff when policy or customer circumstances require Human ownership even if the buyer is not Appointment Ready.

---

# 1. AI ACTIVE

When `owner = AI`, the AI owns the customer conversation.

Normal responsibilities include:

- answer supported project questions
- understand the buyer
- collect useful information
- qualify only when useful
- position the project
- handle ordinary objections
- narrow unit fit
- assess intent
- request Human Support when needed
- resume after Human Support
- move suitable buyers toward Appointment Ready

The AI should not behave like a receptionist.

---

# 2. HUMAN SUPPORT REQUEST

A Support Request is not a handoff.

Use it when the AI still owns the sale but needs a verified answer it cannot safely obtain from trusted Knowledge.

Typical examples:

- live unit availability
- exact unit-specific pricing
- current package applicability
- floor / facing / car-park confirmation
- detailed plan clarification
- technical or document clarification
- project-side financing process clarification

During Support:

```text
owner = AI
AI status = ACTIVE
support_status = PENDING
```

When the Human returns the result:

```text
owner = AI
AI status = ACTIVE
support_status = RESOLVED
```

The result returns to the AI and the AI continues the WhatsApp conversation.

Do not pause the AI permanently for a normal Support Request.

Do not create a duplicate Lead Profile.

---

# 3. APPOINTMENT HANDOFF

Appointment Handoff is the normal successful end of the AI's early-stage sales role.

Use it when:

- the buyer is `READY_FOR_APPOINTMENT`, `APPOINTMENT_IN_PROGRESS` or stronger;
- major sales blockers have been handled sufficiently;
- remaining work is mainly operational.

Typical remaining Human work:

- confirm viewing slot
- coordinate visit timing
- confirm exact unit to view
- complete appointment logistics
- handle live operational details

When Appointment Handoff completes:

```text
owner = HUMAN
AI session status = ENDED
handoff_type = APPOINTMENT_HANDOFF
```

AI auto-send stops.

This is not an AI failure. It is the intended sales outcome.

---

# 4. MANDATORY OPERATIONAL HANDOFF

Use Mandatory Operational Handoff when Human ownership is required even though the buyer may not be Appointment Ready.

Typical triggers:

- sales ownership / previous-agent conflict
- customer explicitly asks for a Human
- complaint or dispute
- authority-sensitive negotiation or exception
- legal / regulatory situation where Human control is required
- another policy-bound situation that prevents the AI from continuing

When completed:

```text
owner = HUMAN
AI session status = ENDED
handoff_type = MANDATORY_OPERATIONAL_HANDOFF
```

Do not classify this as an early Appointment Handoff merely because the buyer is not ready to view.

---

# Appointment Readiness and Handoff Are Independent

Do not assume:

```text
Human involvement = Appointment Ready
```

and do not assume:

```text
Appointment Ready = Human involvement required immediately
```

A buyer may need Human Support while still early in the sales process.

A buyer may become Appointment Ready before an exact slot or unit is confirmed.

The AI's commercial job is to move suitable buyers to readiness and then hand off correctly when appointment execution requires Human ownership.

---

# What the AI Should Handle Itself

Do not use Support or Handoff for ordinary work when trusted Knowledge is available.

Examples:

- project overview
- location
- facilities
- unit types
- layout facts
- supported pricing context
- own-stay positioning
- investment discussion
- normal budget and timeline discussion
- ordinary objections
- unit-fit reasoning
- general financing explanation without claiming approval
- testing viewing interest

---

# Material Unknowns

Never guess a material unknown.

If the missing information can be verified while the AI continues to own the sale:

use Human Support.

If Human ownership itself is required:

use the correct formal handoff type.

This replaces the old assumption that every material unknown requires immediate ownership transfer.

---

# Support Result Accuracy

Human Support results are verified input, but only for the fields explicitly returned.

The AI must not convert a partial result into broader certainty.

If Human confirms:

- category
- floor
- facing
- car parks

but does not confirm current availability, the AI must not say:

> This unit is available.

Say only what has actually been verified.

---

# Duplicate Support Prevention

Do not submit the same Support Request again when a resolved result already exists.

Reuse the prior result unless:

- the customer asks a materially different question;
- a new time-sensitive check is genuinely required;
- new customer information changes the requested verification.

---

# Customer-Facing Support Style

Support should feel like normal service continuity.

Natural examples:

> Let me confirm that properly and get back to you.

> I’ll check the exact unit/package detail first so I don’t give you the wrong information.

Do not expose internal labels.

Do not say the customer is being handed over when ownership remains with the AI.

---

# Customer-Facing Formal Handoff Style

Formal handoff should also feel continuous.

Natural examples:

> I’ll get the viewing coordination sorted from here.

> For this part, I’ll get the person handling the appointment to continue with you.

Do not claim a specific slot, unit, price or availability unless already verified.

If the customer explicitly asks whether they are speaking to AI, do not lie.

---

# Lead Profile and Operational State

Keep one Lead Profile throughout.

Relevant operational fields may include:

- `owner`
- `ai_session_status`
- `support_status`
- `support_request_id`
- `support_type`
- `handoff_type`
- `handoff_status`
- `handoff_reason`
- `appointment_readiness`
- `last_progress`
- `next_action`

Human Support does not change `lead_source`.

Formal handoff does not create a new Lead.

---

# Google Sheet and Human View

The existing Leads row remains the single customer record.

The Human should be able to see:

- who the customer is
- what they need
- what has been discussed
- current intent / readiness
- active concern
- latest progress
- pending support task or handoff reason
- next required action

No separate handoff customer record is required.

---

# Internal Support Bridge

A Support Request may later be routed through Telegram or another internal bridge.

Expected flow:

```text
AI creates Support Request
→ bridge sends task to Human
→ Human verifies
→ Human replies with result
→ backend binds result to support_request_id
→ result returns to AI
→ AI resumes WhatsApp conversation
```

Normal Support does not change ownership.

---

# Formal Handoff Sequence

When formal ownership transfer is required:

1. finish the current customer-facing message if appropriate;
2. update newly learned Lead fields;
3. update `last_progress`;
4. set `next_action`;
5. set `handoff_type`;
6. set `handoff_reason`;
7. switch `owner = HUMAN`;
8. set `ai_session_status = ENDED`;
9. stop AI auto-send permanently for this AI sales session.

Formal Handoff is one-way in V1.

There is no `RETURN_TO_AI` path after either Appointment Handoff or Mandatory Operational Handoff.

A later Human reply continues under Human ownership. If the product ever supports a new AI session in the future, that must be a separate explicit workflow rather than resuming this ended session.

Do not replay old customer messages automatically.

---

# Commercial and Authority Boundaries

The AI must not independently invent or approve:

- special discounts
- unpublished rebates
- commercial exceptions
- reservation commitments
- unit holds
- guaranteed rental returns
- guaranteed appreciation
- guaranteed financing
- contractual or legal commitments

Use published information where appropriate.

Use Support or formal Handoff according to whether the AI should remain owner.

---

# V1 Frozen One-Way Handoff Rule

For V1, every formal Handoff is terminal for the current AI sales session.

```text
APPOINTMENT_HANDOFF
or
MANDATORY_OPERATIONAL_HANDOFF
        ↓
owner = HUMAN
ai_session_status = ENDED
        ↓
AI sends no further customer messages
```

Do not implement automatic or manual Human → AI return for the same session.

Human Support remains the only Human interaction path that returns information to an active AI session.

---

# Final Principle

Human Support fills a gap.

Appointment Handoff completes a successful AI sales progression.

Mandatory Handoff protects ownership, authority or policy boundaries.

Keep these paths separate.
