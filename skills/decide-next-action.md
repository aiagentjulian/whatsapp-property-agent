# Decide Next Action Skill

## Purpose

This skill decides the single most useful next sales action after each meaningful customer message or resolved Human Support result.

It does not write the final customer-facing reply.

It does not rewrite the Lead Profile.

Its job is to answer:

> What is the most valuable next move in this conversation right now?

The answer should guide a flexible sales process, not a rigid state machine.

---

## Core Principle

Choose one primary next action.

Do not choose an action because a Lead Profile field is empty.

Choose it because it is the best move for this customer now.

The latest customer message, current blocker, buying intent, support state and ownership state all matter.

---

## Inputs

This skill may consider:

- latest customer message
- conversation history or summary
- current Lead Profile
- current stage
- current intent / appointment-readiness state
- active concerns
- relevant trusted project Knowledge
- retrieved Knowledge
- prior Human Support requests and results
- current support status
- current owner
- handoff state
- last progress
- current next objective

System-controlled fields such as lead source must not be inferred or changed by this skill.

---

## Primary Action Taxonomy

Choose one primary action family:

- `ASK`
- `ANSWER`
- `POSITION`
- `HANDLE_OBJECTION`
- `NARROW_UNIT`
- `REQUEST_SUPPORT`
- `CLOSE_VIEWING`
- `APPOINTMENT_HANDOFF`
- `MANDATORY_HANDOFF`
- `ACKNOWLEDGE_MAINTAIN`

The implementation may use a more specific action name, but it should map to one of these families.

---

## Output

Return one primary next action plus one short internal reason.

Example:

```json
{
  "action_type": "REQUEST_SUPPORT",
  "next_action": "verify_current_two_carpark_availability",
  "reason": "Two car parks are a hard requirement and current availability is not verified."
}
```

Keep the reason short and decision-useful.

Do not expose the internal reason to the customer.

---

## Decision Order

### 1. Respect ownership first

If owner is already `HUMAN`, do not generate another AI sales action.

If a Mandatory Handoff is required, choose `MANDATORY_HANDOFF`.

If an Appointment Handoff has completed, stop AI sales progression.

A normal pending Support Request does NOT change ownership.

---

### 2. Handle the latest customer message first

If the customer asks a direct question, answer it before pursuing the internal sales agenda when the answer is available.

Do not ignore the latest message to complete qualification.

---

### 3. Use trusted Knowledge before requesting Human Support

If the answer is available and sufficiently current in trusted Knowledge:

choose `ANSWER`, `POSITION`, `HANDLE_OBJECTION` or `NARROW_UNIT` as appropriate.

Do not ask a Human to verify something the AI already knows.

---

### 4. Request Human Support when a material answer is missing

Choose `REQUEST_SUPPORT` when:

- the AI should remain sales owner;
- the information materially affects the conversation;
- the answer is not safely available from trusted Knowledge;
- verification would let the conversation continue.

Examples:

- live unit availability
- exact current package for a specific unit
- unit-facing / car-park confirmation
- missing detailed plan information
- project-side financing process clarification
- technical/document verification

A Support Request is not a handoff.

After the support result returns, reassess the next action from the new context.

---

### 5. Use resolved Support Results

If a relevant support result already exists:

do not request it again.

Use it.

Choose the next sales move based on the verified result.

Normally:

`ANSWER` / `POSITION` / `HANDLE_OBJECTION` / `NARROW_UNIT` / `CLOSE_VIEWING`

Do not merely relay the Human answer and end the conversation.

---

### 6. Resolve meaningful blockers

If a concern is preventing progress, handle it before adding unrelated qualification.

Examples:

- budget
- layout
- density
- location
- financing
- safety concern
- investment evidence
- unit fit

Ask one clarifying question only if it changes how the concern should be handled.

---

### 7. Clarify only decision-useful gaps

Ask only what materially affects fit, positioning, objection handling or the next recommendation.

Examples:

- purchase purpose
- budget range
- hard unit requirement
- timeline
- financing context when relevant
- investment objective
- decision-maker context when it matters

Do not complete the profile for its own sake.

---

### 8. Position when enough context exists

When the buyer's priorities are sufficiently clear, stop collecting and sell.

Use the most relevant value proposition rather than a feature dump.

---

### 9. Recognize Appointment Ready

Strong signals include:

- asks to view
- asks when they can come
- asks for weekend availability
- asks which specific units remain
- asks about exact floor / facing / car-park combinations
- asks for package or price tied to a specific purchase decision
- says they would view if a remaining condition is satisfied
- accepts a suitable unit direction and wants the next step

When the buyer is ready:

reduce discovery.

Do not return to basic qualification without a genuine reason.

---

### 10. Close or hand off correctly

Choose `CLOSE_VIEWING` when the AI can naturally test or advance viewing intent.

Choose `APPOINTMENT_HANDOFF` when:

- buyer is Appointment Ready or stronger;
- most sales work is done;
- remaining work is mainly appointment execution.

Examples:

- slot confirmation
- final visit logistics
- exact unit to show
- appointment coordination

Choose `MANDATORY_HANDOFF` when policy requires Human ownership regardless of readiness.

Examples:

- ownership / agent conflict
- explicit Human request
- complaint or dispute
- authority-sensitive situation

Do not classify Mandatory Handoff as an early Appointment Handoff.

---

## Stage Guidance

### UNDERSTAND

Learn why the buyer is here and what matters.

Avoid over-qualification.

### QUALIFY

Clarify only facts that materially affect fit.

### POSITION

Connect the project's relevant strengths to the buyer's priorities.

### HANDLE

Resolve the real concern. Use Support Request if a material verification is missing.

### INTENT

Detect whether the buyer is moving toward real action.

### CLOSE

Move a ready buyer toward viewing or Appointment Handoff.

Do not restart broad discovery at this stage.

---

## Intent Guidance

### LOW

Prefer useful answers and light discovery.

Avoid hard closing.

### MEDIUM

Clarify one important gap, position, and handle early concerns.

### HIGH

Reduce discovery, answer practical questions quickly, resolve blockers and test viewing.

### READY_FOR_APPOINTMENT

Prefer:

- `CLOSE_VIEWING`
- `APPOINTMENT_HANDOFF`

Avoid unrelated qualification.

---

## Duplicate Support Rule

Before choosing `REQUEST_SUPPORT`, inspect prior requests.

If the same task was already resolved, reuse the result.

If it was previously requested and the new request is not materially different, do not request it again.

---

## One Action Only

Bad:

> Ask budget, explain layout, verify unit, then suggest viewing.

Good:

`verify_current_two_carpark_availability`

or

`position_layout_for_family`

or

`move_to_viewing`

The final response may naturally answer plus ask one useful question, but the internal objective should remain singular.

---

## Relationship to Other Skills

`update-lead-profile.md` owns Lead Profile updates.

`request-human-support.md` defines Support Request behavior.

`handoff-to-human.md` and `HANDOFF_RULES.md` govern ownership transfer.

`RESPONSE_RULES.md` governs customer-facing wording.

---

## Do Not Do

Do not:

- generate multiple primary actions
- invent facts
- request support for known information
- repeat resolved support requests
- treat Support Request as ownership transfer
- continue AI sales after formal Human takeover
- force appointment from weak engagement
- keep qualifying after a clear readiness signal
- choose an action merely because a profile field is empty

---

## Final Principle

Do not ask what is missing.

Ask what matters next.

If the AI can handle it, handle it.

If it needs one verified answer, request support and continue.

If the buyer is ready, move to appointment.

If ownership must change, hand off for the correct reason.
