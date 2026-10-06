# Decide Next Action Skill

## Purpose

This skill decides the single most useful next sales action after each meaningful customer message.

It does not write the final customer-facing reply.

It does not rewrite the Lead Profile.

It does not modify any Brain or Knowledge Markdown files.

Its job is to answer one question:

> What is the most valuable next move in this conversation right now?

The output should guide the agent without turning the sales process into a rigid script.

---

## Core Principle

Choose one primary next action.

Do not produce a list of tasks.

Do not ask what information is still missing from the Lead Profile.

Ask instead:

> What action would move this specific conversation forward most effectively now?

The next action should reflect the customer's latest message, current sales context, active concerns, intent level and handoff status.

---

## Inputs

This skill may consider:

- latest customer message
- current Lead Profile
- current sales stage
- current intent level
- active concerns
- last progress
- current next objective, if one already exists
- current handoff status and owner
- relevant project knowledge available to the agent
- conversation summary

System-controlled fields such as `lead_source` are context only and must not be inferred or changed by this skill.

---

## Output

Return exactly one primary next action plus one short internal reason.

Example:

```json
{
  "next_action": "clarify_investment_priority",
  "reason": "Customer has stated investment purpose and budget, but the main investment objective is still unclear."
}
```

The `reason` exists for debugging, review and future Experience Ledger analysis.

It should be short.

Do not store long reasoning chains.

The long-term Lead Profile should normally persist only `next_action`, not the reasoning text.

---

## Action Priority

Use this priority order when deciding what comes next.

### 1. Handle the customer's current message first

The latest customer message has priority over the internal sales agenda.

If the customer asks a question, the next action should normally address that question before qualification or closing.

Example:

Customer:

> What is the maintenance fee?

Correct next action:

`answer_maintenance_fee`

Not:

`ask_purchase_timeline`

Do not ignore what the customer just asked simply because another sales field is incomplete.

---

### 2. Resolve a blocking concern when one exists

If an active concern is preventing progress, handle it before adding new sales questions.

Examples:

- price concern
- location concern
- financing concern
- oversupply concern
- developer concern
- comparison with another project

Possible next action:

`address_price_concern`

or

`compare_relevant_project_strength`

Do not move toward closing while a major unresolved concern is still blocking the customer.

---

### 3. Clarify the most decision-useful gap

If the conversation needs more understanding, choose only the information that materially affects fit, positioning or the next recommendation.

Examples:

`clarify_purchase_purpose`

`clarify_budget_range`

`clarify_unit_preference`

`clarify_purchase_timeline`

`clarify_investment_priority`

Do not ask simply because a profile field is empty.

Do not stack multiple qualification questions into one next action.

---

### 4. Position the project when enough context exists

When the customer's needs are sufficiently clear, stop collecting information and use relevant knowledge to position the project.

Examples:

`position_for_own_stay`

`position_for_investment`

`position_specific_unit_type`

`explain_location_fit`

`explain_rental_case`

The positioning angle should follow the customer's actual priorities, not a generic sales script.

---

### 5. Move toward close when intent is strong

If the customer shows strong buying signals, reduce unnecessary qualification.

Possible next actions:

`soft_close`

`move_to_viewing`

`move_to_appointment`

`confirm_readiness_to_proceed`

A customer who is ready to move should not be delayed because the profile is incomplete.

---

### 6. Stop AI progression when handoff is required

If handoff rules indicate that the AI should no longer own the conversation, the next action must reflect that.

Possible next action:

`handoff_to_human`

Do not continue selling after ownership has moved to a human.

---

## Stage-Aware Guidance

The current sales stage should guide judgment, but it must not override the customer's latest message.

### UNDERSTAND

Primary objective:

Understand why the customer is here and what they are trying to achieve.

Typical next actions:

- clarify purchase purpose
- clarify reason for enquiry
- identify broad need

Do not over-qualify.

---

### QUALIFY

Primary objective:

Clarify the few facts that materially affect fit.

Typical next actions:

- clarify budget
- clarify timeline
- clarify unit preference
- clarify financing context when relevant

Do not treat qualification as a form to complete.

---

### POSITION

Primary objective:

Connect project facts to the customer's priorities.

Typical next actions:

- position for own stay
- position for investment
- recommend relevant unit type
- explain why a specific project feature matters to this customer

Do not repeat generic brochure language.

---

### HANDLE

Primary objective:

Resolve the concern currently preventing progress.

Typical next actions:

- address objection
- answer comparison question
- clarify uncertainty
- retrieve project knowledge
- recommend human handoff if the issue exceeds AI authority

Do not change topic before the concern is handled.

---

### INTENT

Primary objective:

Judge whether the customer is moving toward a real action.

Typical next actions:

- test readiness naturally
- answer specific purchase questions
- remove final blockers
- move toward viewing when justified

Do not force a close from weak engagement alone.

---

### CLOSE

Primary objective:

Move a ready customer toward the next real-world action.

Typical next actions:

- move to viewing
- move to appointment
- handoff for booking or confirmation

Do not restart discovery unless the customer introduces genuinely new information that changes fit.

---

## Intent-Aware Guidance

### LOW

Prefer:

- answer current question
- provide useful information
- understand broad need

Avoid:

- hard close
- repeated qualification
- aggressive appointment pushes

---

### MEDIUM

Prefer:

- clarify one important gap
- position based on known needs
- handle early concerns

Avoid:

- asking several questions at once
- assuming the customer is ready to proceed

---

### HIGH

Prefer:

- answer specific purchase questions
- resolve blockers
- reduce discovery
- soft close where appropriate

Avoid:

- returning to basic qualification without a clear reason

---

### READY_FOR_APPOINTMENT

Prefer:

- move directly toward appointment or human handoff

Avoid:

- unnecessary education
- profile completion
- unrelated discovery questions

---

## Strong Buying Signal Rule

If the latest customer message includes a clear buying signal, this should heavily influence the next action.

Examples:

- asks to view the project
- asks when they can come
- asks what is needed to reserve
- asks which units remain available
- asks about financing for a specific unit
- says a particular time works for them

In such cases, do not choose a basic qualification action unless the missing information is genuinely required to proceed.

---

## Weak Engagement Rule

Do not confuse activity with purchase intent.

Examples that do not automatically justify closing:

- many messages
- quick replies
- saying "interesting"
- asking general project questions
- reacting positively to marketing language

Choose the next action based on evidence of purchase progression, not conversation volume.

---

## No Forced Progression

Do not force the conversation to advance one stage every turn.

The best next action may sometimes be:

`answer_current_question`

or

`provide_requested_information`

without changing stage.

A good sales conversation is not a conveyor belt.

---

## No Mandatory Question Rule

The next action does not need to be a question.

Sometimes the correct action is simply:

- answer
- explain
- position
- reassure
- clarify
- close
- handoff

Do not manufacture a question merely to keep the conversation going.

---

## One Action Only

Bad output:

```text
Ask budget, explain location, ask timeline, then suggest viewing.
```

Good output:

```text
clarify_budget_range
```

or

```text
answer_location_question
```

or

```text
move_to_viewing
```

The agent may naturally combine a short answer and one question in the final response, but the internal sales objective should remain singular.

---

## Reason Field

The internal `reason` should explain the immediate decision in one concise sentence.

Good:

> Customer has already provided purpose and budget, so the most useful remaining gap is the investment objective.

Bad:

> The customer may perhaps maybe be interested in investment because they asked several questions and therefore the system should consider a number of possibilities before deciding whether to continue qualifying or potentially position the project.

Keep reasoning compact and decision-useful.

Do not expose it to the customer.

Do not store it in the long-term Lead Profile.

It may later be recorded in an Experience Ledger for analysis.

---

## Relationship to Lead Profile

The selected `next_action` may be written into the Lead Profile as the current `next_objective` or equivalent runtime field.

The short `reason` should not normally be persisted there.

Do not modify other Lead Profile fields through this skill.

Profile changes belong to `update-lead-profile.md`.

---

## Relationship to Response Generation

This skill decides the objective.

`RESPONSE_RULES.md` governs how that objective is expressed naturally to the customer.

Example:

Next action:

`clarify_investment_priority`

Customer-facing response may become:

> If you're looking at this mainly for investment, are you more focused on steady rental income or longer-term appreciation?

The action and the wording are separate concerns.

---

## Relationship to Handoff

If handoff status is `REQUIRED`, or ownership is already `HUMAN`, this skill must not continue normal AI sales progression.

When handoff is required:

`next_action = handoff_to_human`

When owner is already human:

Do not generate a new AI sales action.

---

## Do Not Do

This skill must not:

- generate multiple primary next actions
- rewrite the whole Lead Profile
- infer or change system-controlled lead source
- invent customer facts
- generate long reasoning
- modify Markdown files
- force stage progression
- force a question every turn
- close merely because the customer is engaged
- continue AI sales after human takeover

---

## Final Principle

Do not ask what is missing.

Ask what matters next.

Choose one action that best serves the current customer conversation.

The latest customer message comes first.

The sales framework guides judgment, but should never override common sense.
