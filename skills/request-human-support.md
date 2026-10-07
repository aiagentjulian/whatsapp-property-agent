# Request Human Support Skill

## Purpose

This skill is used when the AI still owns the sales conversation but needs a verified fact or operational answer that it cannot safely provide from trusted Knowledge.

Human Support is not a sales handoff.

The AI remains the customer-facing sales owner, the Human verifies the requested item, the result returns to the AI, and the AI resumes the WhatsApp conversation.

The purpose is to preserve sales continuity without guessing.

---

## Core Principle

Use Human Support for a missing answer.

Use formal handoff for a change of conversation ownership.

Do not confuse the two.

A Support Request should help the AI continue selling. It should not become an excuse to stop selling.

---

## Ownership

During a Support Request:

```text
owner = AI
AI status = ACTIVE
support_status = PENDING
```

After the Human returns a result:

```text
owner = AI
AI status = ACTIVE
support_status = RESOLVED
```

The verified result is added to the AI's current context.

The AI then continues the customer conversation.

Do not set `owner = HUMAN` for a normal Support Request.

---

## When to Use Human Support

Use this skill when the requested information materially matters and cannot be verified from current trusted Knowledge.

Typical examples:

- live or current unit availability
- current unit-specific price
- current package applicability for a specific unit
- floor / facing / car-park confirmation
- detailed layout or plan clarification not present in Knowledge
- project-side financing process clarification
- technical / document clarification
- other real-world verification outside the AI's current trusted sources

Do not request Human Support for information already available in trusted Knowledge.

Do not request Human Support merely because the question is detailed.

---

## Support Request Structure

Each request should contain:

- `support_request_id`
- Lead ID
- support type
- exact question or verification task
- short customer context relevant to the task
- known facts that should not be re-checked unnecessarily
- requested output
- current support status

Suggested support types:

- `UNIT_AVAILABILITY`
- `UNIT_PRICE`
- `PACKAGE_VERIFICATION`
- `UNIT_CONFIGURATION`
- `LAYOUT_OR_PLAN_CHECK`
- `FINANCING_PROCESS_CHECK`
- `DOCUMENT_OR_TECHNICAL_CHECK`
- `OTHER`

Keep the request concise.

Do not dump the whole conversation when a short task-specific context is enough.

---

## Duplicate Prevention

Before creating a Support Request, check previous support requests and results.

Do not request the same information again when a resolved answer already exists.

A new request is justified only when:

- the customer asks for materially different information;
- the previous result was explicitly time-sensitive and a fresh check is genuinely required;
- the previous result did not answer the new question;
- new customer information changes what must be verified.

If none applies, reuse the existing verified result.

---

## Result Handling

Treat the Human result as structured verified input.

The AI must distinguish exactly what was verified from what was not verified.

Example:

Human result verifies:

- Tower 1C
- Level 12
- sea-facing
- 2 car parks
- package total

but does not verify:

- current availability

Then the AI may say those first five items are confirmed.

It must NOT say the unit is currently available.

Never expand a support result beyond the fields actually verified.

---

## After Support Resolves

A resolved Support Request should normally lead to another sales decision.

Use this sequence:

1. answer the customer's question using the verified result;
2. connect the answer to the customer's stated need or concern;
3. decide whether the blocker is resolved;
4. assess whether intent has strengthened;
5. if appropriate, move toward viewing;
6. otherwise continue normal sales conversation.

Do not simply relay the support result and stop.

Human Support should create progress.

---

## Customer-Facing Style

Do not expose internal labels such as SUPPORT_REQUEST.

Natural customer-facing language may be:

> Let me confirm that properly and get back to you.

> I’ll check the exact unit/package detail first so I don’t give you the wrong information.

Do not say the AI is handing off if ownership remains with the AI.

Do not promise a specific response time unless the Human workflow has committed to one.

If the customer directly asks whether they are speaking to an AI or bot, answer truthfully.

---

## Relationship to Appointment Readiness

Human Support may happen before or after the buyer becomes Appointment Ready.

A request for unit availability, exact unit configuration, or final package detail can itself be a strong buying signal.

Do not automatically classify the buyer as unready simply because verification is still needed.

After support resolves, reassess readiness immediately.

---

## Relationship to Formal Handoff

Use formal Appointment Handoff only when the buyer is already ready for viewing and the remaining work is mainly appointment execution.

Use Mandatory Operational Handoff when policy or ownership requires Human control even if the buyer is not Appointment Ready.

Support Request is neither of these.

---

## Telegram Bridge

A future runtime may implement Human Support through Telegram or another internal bridge.

The expected lifecycle is:

```text
AI creates support request
→ internal bridge sends task to Human
→ Human replies with verified result
→ backend binds result to support_request_id
→ result returns to AI context
→ AI resumes WhatsApp conversation
```

The bridge implementation must not change Lead ownership for a normal Support Request.

---

## Do Not Do

Do not:

- use Human Support for facts already available in trusted Knowledge
- change owner to HUMAN for a normal Support Request
- create repeated identical requests
- invent a Human result
- overstate what the Human verified
- relay the answer without deciding the next sales move
- continue asking profile questions when the support result has already made the buyer Appointment Ready
- treat Support Request as a completed sales handoff

---

## Final Principle

Human Support fills a factual or operational gap.

The AI still owns the sale.

Get the answer, use it accurately, and continue moving the buyer toward the right next step.
