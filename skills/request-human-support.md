# Request Human Support Skill

## Purpose

Use this skill when the AI still owns the sales conversation but needs a verified factual or operational answer that cannot be safely provided from trusted Knowledge.

Human Support is not a sales handoff.

The AI remains the customer-facing sales owner. The Human verifies one missing item. The result returns to the AI. The AI uses it and resumes the same sales objective.

This skill must follow `brain/SUPPORT_LIFECYCLE.md`.

---

## Core Principle

Use Human Support for one material missing answer.

Use formal Handoff only for a change of ownership.

A Support Request should help the AI continue selling. It must not become an excuse to stop selling, repeatedly ask the same internal question, or lose the pre-support sales objective.

---

## Ownership

During Support:

```text
owner = AI
AI status = ACTIVE
support_status = OPEN
```

After a usable result returns:

```text
owner = AI
AI status = ACTIVE
support_status = RESOLVED
```

Do not set `owner = HUMAN` for a normal Support Request.

---

## When to Use Human Support

Use this skill when all of the following are true:

1. the information materially affects the buyer's decision or the next useful sales move;
2. the answer is not available in trusted Knowledge;
3. the answer is not already available in the Lead Profile, conversation, or prior support result;
4. guessing would create factual or commercial risk;
5. obtaining the answer can reasonably move the conversation forward.

Typical cases:

- live unit availability
- current unit-specific price
- current package applicability
- floor / facing / car-park confirmation
- detailed layout or plan clarification missing from Knowledge
- project-side financing-process clarification
- technical or document clarification
- unusual approval or commercial exception requiring verification

Do not use Human Support merely because a question is detailed.

---

## Mandatory Pre-Request Check

Before creating a request, check in this order:

### Trusted Knowledge

If the answer is already supported:

Do not request support.

### Customer / Lead Context

If the answer is already known from the customer, Lead Profile, or current conversation:

Do not request support.

### Existing OPEN Support

If an equivalent OPEN request already exists:

Do not create another request.

Reuse the existing request.

### Existing RESOLVED Support

If an equivalent RESOLVED result already answers the question:

Do not create another request.

Use the existing result.

### Material Change

Create a new request only when the new question is materially different, such as a different unit, package, condition, or genuinely time-sensitive re-check.

Compare semantic meaning, not wording.

---

## Duplicate Identity

Treat a support task as equivalent when these are substantially the same:

```text
lead_id
support_type
requested_fact
subject / unit / package / condition
customer_need
```

Examples of duplicate meaning:

```text
Is Type B still available?
Can you confirm Type B availability?
Do we still have Type B units?
```

Do not create a new request because the customer asks again in different words.

---

## Preserve Resume Context

Every new Support Request must capture:

```text
sales_stage
resume_stage
resume_objective
unresolved_customer_need
```

The request must preserve what the AI intended to do after the missing fact was resolved.

Example:

```text
resume_stage:
POSITION

resume_objective:
Confirm whether the 2-bedroom option fits the buyer's investment budget and continue toward viewing.

unresolved_customer_need:
Buyer wants confirmation of the current effective package price.
```

Do not rely on the model to reconstruct this from scratch after support returns.

---

## Support Request Structure

Each request should contain:

- `support_request_id`
- `lead_id`
- `status`
- `support_type`
- exact verification task
- subject / unit / package if applicable
- short customer context
- known facts that should not be re-checked
- requested output
- `sales_stage`
- `resume_stage`
- `resume_objective`
- `unresolved_customer_need`

Suggested support types:

- `UNIT_AVAILABILITY`
- `UNIT_PRICE`
- `PACKAGE_VERIFICATION`
- `UNIT_CONFIGURATION`
- `LAYOUT_OR_PLAN_CHECK`
- `FINANCING_PROCESS_CHECK`
- `DOCUMENT_OR_TECHNICAL_CHECK`
- `OTHER`

Keep the request concise and task-specific.

---

## Request Quality

Bad:

```text
Please check this buyer.
```

Better:

```text
Please confirm whether any Type B units currently have an indicative effective package at or below RM800k. Buyer is looking for investment and has stated an approximate RM800k budget.
```

Prefer one coherent unresolved purpose per request.

Do not bundle unrelated checks unless they genuinely form one operational question.

---

## Customer-Facing Behaviour While Pending

The AI remains active while support is pending.

Natural wording may include:

> Let me confirm that properly so I don't give you the wrong information.

> I'll check the exact unit/package detail first.

The AI may continue useful qualification, positioning, or objection handling while waiting if doing so is natural.

Do not:

- invent the missing answer;
- imply confirmation before it exists;
- create a duplicate request;
- repeatedly send the same waiting message;
- expose internal labels;
- claim the customer is being handed over.

---

## Result Handling

Treat the Human result as verified input only for the fields actually returned.

First determine:

1. what exactly was confirmed;
2. what remains unconfirmed;
3. what customer need this resolves;
4. whether the original blocker is removed;
5. whether the buyer's intent or appointment readiness has changed.

Never strengthen the certainty level.

If the result says:

```text
currently showing available
```

do not say:

```text
definitely available
```

If the result says:

```text
indicative
```

keep it indicative.

If the result says:

```text
may qualify
```

do not say:

```text
eligible
```

---

## After Support Resolves

Use this sequence:

1. respond to the customer's latest message;
2. answer the original blocked question using the verified result;
3. connect the result to the buyer's need;
4. resume the saved sales objective unless the latest message changed direction;
5. reassess intent and appointment readiness;
6. choose the next useful sales move.

Do not rebuild the sales conversation from zero.

Do not return to unrelated qualification.

Do not merely relay the Human result and stop when a clear commercial next step remains.

---

## Support Result Response Pattern

When useful, the response should contain:

```text
Answer
+
Buyer relevance
+
Next sales move
```

Example:

Customer:

> Is there anything around RM800k?

Support confirms:

```text
Selected Type B units have an indicative package starting around RM790k, depending on floor and orientation.
```

Weak:

> The team confirmed selected Type B units start around RM790k.

Preferred:

> Yes, selected Type B units have an indicative package starting around RM790k, depending on floor and orientation. Since you mentioned an RM800k budget, this is much closer to your range. Are you mainly looking for the best entry price, or would you still prefer a higher-floor unit?

Do not force a follow-up question when a short factual answer is genuinely the most natural response.

---

## Failed Resume Conditions

Treat resume as failed when the AI:

- ignores the support result;
- relays it without resolving the buyer's need;
- loses the saved objective;
- starts unrelated qualification;
- repeats already answered questions;
- creates an unnecessary duplicate request;
- becomes passive after a useful result;
- delays an Appointment Ready buyer with unnecessary discovery.

---

## Appointment Readiness

Support may remove the last meaningful blocker.

Example:

Customer:

> If you have something below RM900k with this layout, I can come this weekend.

If support confirms a suitable option, do not restart qualification.

Move toward viewing or Appointment Handoff according to the current handoff rules.

---

## Relationship to Formal Handoff

Use Appointment Handoff when the buyer is Appointment Ready and remaining work is mainly appointment execution.

Use Mandatory Operational Handoff when policy, ownership, complaint, explicit Human request, or authority-sensitive circumstances require Human control.

Support Request is neither.

If the customer explicitly asks for a Human or team member, follow the formal Handoff rules instead of keeping AI ownership through support.

---

## Regression Expectations

The following behaviours are mandatory:

- no duplicate request for an equivalent OPEN issue;
- no duplicate request when a usable RESOLVED result exists;
- support preserves AI ownership;
- resume context is stored before the request;
- support certainty is preserved;
- the latest customer message takes priority;
- support results are used for sales progression;
- Appointment Ready buyers are not delayed.

PEA-001, PEA-007, PEA-008 and PEA-011 should remain explicit regression fixtures for this lifecycle.

---

## Do Not Do

Do not:

- request support for known information;
- change owner to HUMAN for normal support;
- create repeated equivalent requests;
- invent a Human result;
- overstate what was verified;
- lose the pre-support objective;
- relay the answer without deciding what it enables next;
- restart broad qualification after support;
- delay a ready buyer because some profile fields remain empty;
- treat Support Request as a completed sales handoff.

---

## Final Principle

Human Support fills one factual or operational gap.

The AI still owns the sale.

Check once, use the answer accurately, and continue from where the conversation left off.
