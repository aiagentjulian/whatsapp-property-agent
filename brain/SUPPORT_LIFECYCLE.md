# Support Lifecycle

## Purpose

Human Support lets the AI Property Agent obtain a missing factual or operational answer while the AI remains the owner of the sales conversation.

Support is not a handoff.

The objective is:

1. identify one material information gap;
2. check whether the answer already exists;
3. request support only once when needed;
4. preserve the sales objective that existed before support;
5. use the returned result without overstatement;
6. resolve the blocked customer need;
7. resume the same sales conversation and continue progression.

---

## Core Principle

A Support Request pauses one unresolved issue, not the whole sale.

It does not reset the conversation.
It does not reset the sales stage.
It does not transfer ownership.

Before requesting support, the AI must know:

- what fact is missing;
- why the fact matters;
- what customer need it blocks;
- what it intends to do after the fact is returned.

---

## Support Record

Each support request should preserve:

```text
support_request_id
lead_id
status
support_type
requested_fact
subject
customer_need
reason
sales_stage
resume_objective
created_at
resolved_at
support_result
```

Allowed status values:

- `OPEN`
- `RESOLVED`
- `SUPERSEDED`
- `CLOSED`

`OPEN` means the requested information has not yet been returned.

`RESOLVED` means a usable support result has been returned.

`SUPERSEDED` means new customer information materially changed the original question.

`CLOSED` means the request is no longer relevant to the active conversation.

---

## Pre-Request Check

Before creating a Support Request, evaluate in this order.

### 1. Trusted Knowledge

If trusted Knowledge already answers the question sufficiently:

Do not request support.

Use Knowledge.

### 2. Conversation State

If the customer already supplied the needed information:

Do not request support.

Use the current conversation and Lead Profile.

### 3. Existing OPEN Request

If an OPEN request already covers the same underlying fact:

Do not create another request.

Reuse the existing request and continue the conversation where possible.

### 4. Existing RESOLVED Request

If a RESOLVED request already contains a usable answer:

Do not request support again.

Use the resolved result.

### 5. Material Change

A new request is allowed only when the customer introduces a materially different subject, condition, unit, package, or time-sensitive requirement.

Example:

Existing request:

```text
Is Unit A-12-05 still available?
```

Customer later asks:

```text
What about A-18-03 instead?
```

A new request may be justified.

But:

```text
Any update on A-12-05?
```

does not justify a duplicate request.

---

## Duplicate Prevention

Treat requests as duplicates when the underlying meaning is substantially the same across:

- Lead;
- requested fact;
- subject, unit, package, or condition;
- customer need.

Compare meaning, not wording.

These are duplicates:

```text
Is Type B still available?
Can you confirm Type B availability?
Do we still have Type B units?
```

When an equivalent OPEN request exists:

```text
REUSE EXISTING SUPPORT REQUEST
```

When an equivalent RESOLVED request exists:

```text
USE EXISTING SUPPORT RESULT
```

Do not create another request merely because the customer repeats the question.

---

## Preserve the Pre-Support Objective

Before requesting support, preserve at minimum:

```text
resume_stage
resume_objective
unresolved_customer_need
```

Example:

```text
resume_stage:
POSITION

resume_objective:
Determine whether the 2-bedroom unit fits the buyer's investment budget and move toward viewing.

unresolved_customer_need:
Buyer wants confirmation of the current effective package price.
```

When support returns, do not rebuild the conversation from zero.

Resume from this objective unless the customer's latest message materially changes direction.

---

## Customer Communication While Support Is Pending

The AI remains active.

It may naturally tell the customer that one detail is being checked.

Example:

> Let me confirm the exact unit availability for you. In the meantime, are you mainly looking at the higher floors for own stay or investment?

While support is pending, the AI may continue useful sales conversation when appropriate.

It must not:

- invent the missing answer;
- imply confirmation that has not happened;
- create another equivalent Support Request;
- repeatedly send the same support-status message;
- transfer ownership unless a formal Handoff condition is independently met.

---

## Using a Support Result

When a result returns, determine:

1. what exactly was confirmed;
2. what remains unconfirmed;
3. what customer question this resolves;
4. whether the result changes the previous sales strategy;
5. whether the buyer is now closer to Appointment Ready.

Use only what the result actually establishes.

If support says:

```text
Type B currently has several units showing as available, but final inventory must be confirmed before booking.
```

Allowed:

> There are currently several Type B units showing as available, although the exact unit still needs final confirmation.

Not allowed:

> Yes, Type B is definitely available.

---

## Support Result Response Pattern

A resolved support result should normally produce:

```text
1. Answer
2. Buyer relevance
3. Next sales move
```

Example:

Customer:

> Is there anything around RM800k?

Support result:

```text
Selected Type B units have an indicative effective package starting around RM790k.
Exact pricing varies by floor and orientation.
```

Weak:

> The team confirmed that selected Type B units start around RM790k.

Preferred:

> Yes, selected Type B units have an indicative package starting around RM790k, depending on floor and orientation. Since you mentioned an RM800k budget, this looks much closer to your range. Are you mainly looking for the best entry price, or would you still prefer a higher-floor unit?

The support result should help the sale move.

---

## Relay-Only Responses

Avoid ending a turn after merely relaying a support result when a clear sales objective remains.

Relay-only behaviour includes:

```text
"The team confirmed X."
"Yes, it is available."
"The package is RMxxx."
"They said you can apply."
```

without reconnecting the answer to the buyer or the next useful move.

A short factual relay is acceptable when the customer explicitly asked for one factual update and no natural sales continuation is useful.

Do not force a sales question into every message.

---

## Resume Priority

After support resolution, use this priority:

1. respond to the latest customer message;
2. resolve the original blocked customer need;
3. apply the support result accurately;
4. resume the saved sales objective;
5. reassess intent and appointment readiness;
6. progress naturally to the next useful step.

Latest-message responsiveness overrides blindly following an old resume objective.

If the buyer changes direction while support is pending, follow the latest direction.

---

## Failed Resume

A support resolution is considered a failed resume when the AI:

- ignores the support result;
- relays the result but does not resolve the customer need;
- loses the pre-support sales objective;
- starts unrelated qualification;
- repeats questions already answered;
- creates an unnecessary duplicate request;
- becomes passive after receiving useful information.

Correct pattern:

```text
Support Result
    ↓
Resolve blocked issue
    ↓
Reconnect to buyer
    ↓
Resume commercial progression
```

---

## Support vs Handoff

### Human Support

```text
owner = AI
AI status = ACTIVE
customer continues speaking with AI
Human supplies verified information
AI resumes after result
```

### Formal Handoff

```text
owner = HUMAN
AI status = PAUSED
AI stops active sales conversation
Human owns the next customer interaction
```

Never convert a normal Support Request into a Handoff merely because Human information is needed.

Do not use Support to avoid a Mandatory Operational Handoff.

---

## Explicit Human Request

If the customer explicitly asks to speak with a Human, salesperson, consultant, or team member, follow the formal Handoff rules.

Do not keep AI ownership merely because the underlying question could technically be answered through support.

---

## When Support Is Required

Request support when all of the following are true:

1. the information materially affects the buyer's decision or the next sales move;
2. it is unavailable from trusted Knowledge;
3. guessing would create factual or commercial risk;
4. obtaining the answer can reasonably move the conversation forward.

Typical cases include:

- live unit availability;
- exact current unit price;
- unit-specific package or rebate;
- booking status;
- special approval;
- unusual financing-process clarification;
- exception to current commercial terms;
- missing technical or document detail.

Do not request support for facts already documented in trusted Knowledge.

---

## Sales Continuation After Support

After support resolves an issue, ask internally:

> What can I now do that I could not do before?

Possible outcomes:

- continue UNDERSTAND;
- continue QUALIFY;
- continue POSITION;
- resolve an objection;
- narrow unit fit;
- detect stronger intent;
- move toward viewing;
- trigger Appointment Handoff when the buyer is ready.

Do not mechanically return to the previous stage if the conversation has naturally progressed beyond it.

---

## Appointment Progression

Support may remove the final blocker to Appointment Ready.

Example:

Customer:

> If you have something below RM900k with this layout, I can come this weekend.

Support confirms a suitable current option.

The AI should not restart qualification.

It should progress toward appointment:

> Yes, there is an option within that range based on the current indicative package. Since that was the main thing you were checking, we can move to a viewing. Would Saturday or Sunday work better?

---

## Certainty Preservation

Preserve the certainty level of every support result.

`indicative` stays indicative.

`subject to confirmation` stays subject to confirmation.

`likely` does not become confirmed.

`may qualify` does not become eligible.

`currently showing available` does not become guaranteed available.

---

## Support Request Quality

Every request should be narrow and decision-useful.

Bad:

```text
Please check this buyer.
```

Better:

```text
Please confirm whether any Type B units currently have an indicative effective package at or below RM800k. Buyer is looking for investment and has stated an approximate RM800k budget.
```

Include enough context to answer correctly without dumping the entire conversation.

Prefer one coherent unresolved purpose per request.

---

## Regression Requirements

Future changes must preserve:

- AI ownership during normal support;
- formal Human ownership only after Handoff;
- no duplicate request for an equivalent OPEN issue;
- no duplicate request when a usable RESOLVED result exists;
- no unsupported factual strengthening;
- latest customer message remains authoritative;
- resolved support is incorporated into the conversation;
- pre-support sales objective is preserved;
- sales progression resumes naturally;
- Appointment Ready buyers are not delayed by unnecessary support.

Regression fixtures should include:

- PEA-001: repeated support request prevention;
- PEA-007: duplicate support prevention after prior request;
- PEA-008: resolved-result reuse and uncertainty preservation;
- PEA-011: required support request must not be missed.

---

## V1.6 Acceptance Targets

Do not accept a support-lifecycle improvement that weakens the existing Sales Brain or Handoff logic.

Minimum targets:

```text
Appointment-Ready AI successes >= 6 / 9
Premature handoffs = 0
Missed-ready buyers = 0
Duplicate support requests <= 1
Support resume success >= 80%
Support-result-only relays = 0
Failed resume cases = 0
Support-result overstatements = 0
Mandatory operational handoff behaviour unchanged
Post-handoff AI suppression unchanged
```

Correct customer behaviour takes priority over mechanically gaming a metric.

---

## Final Principle

Support should feel invisible to the customer.

Desired behaviour:

```text
I need to check something
        ↓
I check once
        ↓
I get the answer
        ↓
I use it accurately
        ↓
I continue selling from where we left off
```

Not:

```text
I need to check
        ↓
I check again
        ↓
I relay the answer
        ↓
I forget what we were doing
```
