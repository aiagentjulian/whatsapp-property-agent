# Skill: Update Lead Profile

## Purpose

Use this skill to update the existing Lead Profile after a meaningful customer message.

The goal is to preserve a small, reliable, decision-useful customer state that helps future sales judgment.

Do not rebuild the entire profile from scratch on every turn.

Do not treat the profile as a questionnaire.

Do not create missing information merely to make the profile look complete.

---

## Core Principle

Update only what this turn genuinely changes.

Prefer a small patch over a full profile rewrite.

The profile should remain:

- compact
- factual
- commercially useful
- easy for the agent and human salesperson to understand

Do not store long explanations, hidden reasoning, or unnecessary metadata.

---

## When to Run

Run this skill after each meaningful customer message.

Examples of meaningful messages include:

- new personal or buying information
- new property preferences
- budget or financing information
- timeline information
- objections or concerns
- clarification of purpose
- a meaningful change in intent
- a viewing or appointment signal
- a correction to previous information
- information that changes the next sales action

A very light message such as:

- okay
- noted
- thanks
- emoji-only acknowledgement

may require no profile patch unless it changes the conversation state materially.

---

## Inputs

The updater may receive:

- latest customer message
- current Lead Profile
- current conversation summary
- current sales stage
- current intent level
- system-supplied phone or conversation identifier
- system-supplied lead source
- system-supplied campaign or acquisition context

System-supplied fields are authoritative and must not be guessed or overwritten by the LLM.

---

## System-Controlled Fields

The LLM must not invent, infer, or change these unless the system explicitly provides an updated value:

- `lead_id`
- `phone`
- `lead_source`
- `campaign_source`
- acquisition metadata
- technical conversation identifiers

`lead_source` is determined by the messaging system:

- first customer-initiated conversation → `INBOUND`
- outbound contact replies to a prior outbound message → `OUTBOUND`

Sending an outbound message alone does not create a Lead Profile.

The outbound contact becomes a lead only after they reply.

---

## Allowed Update Areas

Use the canonical fields defined in `brain/LEAD_PROFILE.md`.

Common updates may include:

- name
- preferred language
- purchase purpose
- purchase reason
- preferred location
- preferred property type
- size or layout preference
- important features
- budget range
- financing context
- current property status
- purchase timeline
- viewing interest
- appointment readiness
- primary motivations
- decision factors
- decision participants
- active concerns
- resolved concerns
- competitor or comparison projects
- sales stage
- intent level
- fit assessment
- next objective
- handoff status
- handoff reason
- follow-up context
- conversation summary
- last customer intent
- last agent action
- last progress
- next action
- owner when handoff rules require an ownership change

Do not add new schema fields casually.

If a new recurring field is genuinely needed, change `brain/LEAD_PROFILE.md` first.

---

# Evidence Handling

The updater should distinguish only three practical evidence states:

## EXPLICIT

The customer clearly stated the information.

Example:

Customer:

"My budget is around RM900k."

Update:

- `budget_range = around RM900k`
- `evidence = EXPLICIT`

## INFERRED

The customer did not use an exact label, but the conversation strongly supports a reasonable commercial inference.

Example:

The customer repeatedly asks about:

- rental demand
- tenant profile
- vacancy
- rental yield

and frames the property as an income-producing asset.

The updater may record:

- `purchase_purpose = INVESTMENT`
- `evidence = INFERRED`

Use inference when the evidence is strong enough to help the sales conversation.

Do not default to uncertainty merely because the customer did not state an exact category word.

## UNKNOWN

There is not enough reliable evidence.

Keep the field empty or `UNKNOWN`.

Do not force an inference.

---

## Confidence Behaviour

Be willing to infer when the evidence is commercially strong.

Do not confuse:

"not explicitly stated"

with:

"cannot reasonably be known."

At the same time, do not turn a weak guess into a fact.

Examples:

Customer asks once:

"Is it easy to rent out?"

This alone does not necessarily justify:

`purchase_purpose = INVESTMENT`

Customer spends several turns discussing rental income, tenant demand, vacancy, yield and holding return.

This may justify:

`purchase_purpose = INVESTMENT, evidence = INFERRED`

Keep evidence labels minimal.

Do not attach long confidence explanations to every field.

---

# Patch-Only Update Rule

The preferred output is a patch containing only changed fields.

Do not regenerate the whole Lead Profile unless specifically required by the runtime.

Preferred conceptual format:

```json
{
  "updates": {
    "purchase_purpose": {
      "value": "OWN_STAY",
      "evidence": "EXPLICIT"
    },
    "budget_range": {
      "value": "around RM900k",
      "evidence": "EXPLICIT"
    }
  }
}
```

If a stable field did not change, omit it from the patch.

This reduces accidental overwrites and keeps the state stable.

---

# Preserve Existing State

Do not overwrite a valid existing value with:

- UNKNOWN
- empty text
- a weaker inference
- a less precise paraphrase

unless the customer has clearly corrected or changed the information.

Example:

Existing:

`budget_range = RM700k–RM800k`

New customer message:

"Actually I can stretch to RM1m if the unit is right."

Update the budget context.

Do not retain the older range as if it is equally current.

---

# Customer Corrections

The customer's latest clear statement should generally override older information.

Example:

Earlier:

`purchase_purpose = INVESTMENT`

Later:

"Actually this one is more for my own stay."

Update to:

`purchase_purpose = OWN_STAY, evidence = EXPLICIT`

Do not preserve both as current unless the customer explicitly says both purposes matter.

---

# Derived Sales State

The updater may revise:

- `sales_stage`
- `intent_level`
- `fit_assessment`
- `appointment_readiness`
- `viewing_interest`
- `next_objective`

using the rules in:

- `brain/SALES_FLOW.md`
- `brain/INTENT_MODEL.md`

Do not change these mechanically from one isolated keyword.

Use the broader conversation context.

---

# Strong Intent Rule

When the customer demonstrates strong buying intent, do not keep collecting data simply because profile fields are empty.

Examples:

- asks to view this weekend
- asks which unit is currently available
- asks how to reserve
- discusses financing for a specific unit
- asks for next steps to proceed

In these cases:

1. capture the new information,
2. update intent when justified,
3. update `last_progress`,
4. update `next_action`,
5. move toward CLOSE or handoff when appropriate.

Do not make profile completion the blocker.

---

# Weak Intent Rule

When the customer is casually browsing:

- keep updates light,
- do not over-infer,
- do not aggressively increase intent,
- do not create unnecessary next actions.

The profile should reflect the actual conversation, not sales optimism.

---

# Concerns and Objections

When the customer raises a new concern:

add it to `active_concerns` if it is materially relevant.

When a concern has been sufficiently addressed:

move or mark it as resolved.

Do not repeatedly reopen a resolved concern unless the customer raises it again.

Do not duplicate the same objection in multiple forms.

---

# Last Progress

`last_progress` should be a short operational summary of what materially changed in the conversation.

Good:

"Customer clarified own-stay purpose, budget around RM900k and preference for 3-bedroom units."

Bad:

"Customer said many things and seems interested."

Bad:

A transcript of the last several messages.

Keep it concise enough for a human salesperson to scan quickly.

---

# Next Action

`next_action` should describe the single most useful operational next step.

Examples:

- clarify the customer's main own-stay requirement
- answer concern about rental demand
- confirm current promotion
- move toward weekend viewing
- human to confirm latest availability

Do not turn `next_action` into a list of questions.

Do not create multiple competing next actions unless a runtime later explicitly supports them.

---

# Conversation Summary

Keep `conversation_summary` short and decision-useful.

It should preserve only information that materially affects future replies.

Include when relevant:

- why the customer is looking
- key needs
- budget context
- important preferences
- decision factors
- unresolved concerns
- commitments made
- what is waiting for confirmation
- current momentum

Do not store:

- full transcripts
- hidden chain-of-thought
- lengthy reasoning
- every greeting or acknowledgement
- repeated information already represented cleanly elsewhere

---

# Do Not Store LLM Reasoning

Never write the model's private reasoning process into the Lead Profile.

Store only the resulting state that is useful for future sales decisions.

For example, store:

`purchase_purpose = INVESTMENT, evidence = INFERRED`

Do not store:

"I think this customer is probably an investor because they asked three questions about rental yield, and therefore..."

---

# No Mandatory Completion

There are no mandatory profile fields that must be collected before the sales conversation can progress.

Do not create:

- completion percentages
- required-field gates
- qualification scores based on profile completeness

The profile exists to support sales judgment.

The conversation must not become a form-filling exercise.

---

# Relationship to Google Sheet

This skill updates the canonical Lead Profile state.

The Google Sheet sync layer mirrors the useful profile fields for human visibility.

The LLM should not format the Google Sheet directly from free text.

The runtime should map canonical Lead Profile fields to Sheet columns using the dedicated sync skill.

Lead Profile first.

Google Sheet sync second.

---

# Recommended Output Shape

When implemented with structured model output, prefer a compact patch such as:

```json
{
  "updates": {
    "purchase_purpose": {
      "value": "INVESTMENT",
      "evidence": "INFERRED"
    },
    "budget_range": {
      "value": "around RM1.2m",
      "evidence": "EXPLICIT"
    },
    "intent_level": {
      "value": "MEDIUM"
    },
    "last_progress": {
      "value": "Customer clarified an investment focus and budget around RM1.2m."
    },
    "next_action": {
      "value": "Understand whether the customer prioritises rental income or capital appreciation."
    }
  }
}
```

Only changed fields should normally appear.

---

# Final Principle

Extract what changed.

Infer when the evidence is strong.

Do not be timid by default.

Do not guess weakly.

Preserve stable state.

Keep the profile small.

Keep it useful.

Never let data collection interfere with a good sales conversation.
