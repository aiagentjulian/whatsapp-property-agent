# WhatsApp Property Agent Simulator Spec

## 1. Purpose

The simulator exists to test whether the Sales Agent behaves like a strong property salesperson in realistic multi-turn WhatsApp conversations.

It is not a generic chatbot benchmark and it is not a fact-recall test.

The primary question is:

> Can the Agent understand a real buyer, make good sales judgments, use the right project knowledge at the right time, and progress qualified interest toward a confirmed viewing appointment without becoming pushy, mechanical, inaccurate, or over-qualified?

The simulator should help us identify whether a failure comes from:

- Brain / core behavior
- Project Knowledge
- sales judgment
- retrieval
- response style
- unit-fit reasoning
- objection handling
- viewing close
- handoff logic

The simulator must support iterative improvement without allowing the Agent to self-edit Brain or Knowledge.

---

## 2. Primary Success Metric

### Appointment Conversion Outcome

The main business outcome is whether a realistic sales conversation reaches a genuine, qualified appointment/viewing commitment when the simulated buyer is reasonably convertible.

A successful appointment is not merely the Agent asking for a viewing.

A confirmed appointment should normally include enough commitment to indicate the buyer has agreed to proceed, for example:

- buyer agrees to visit;
- a date/day/time window is accepted or actively being finalized;
- buyer asks what is needed for the visit;
- buyer explicitly asks the Agent to arrange or reserve a viewing slot.

The simulator must distinguish:

- `NO_VIEWING_INTENT`
- `VIEWING_SUGGESTED`
- `VIEWING_INTEREST`
- `APPOINTMENT_IN_PROGRESS`
- `APPOINTMENT_CONFIRMED`

Do not reward a forced appointment if the buyer is clearly unqualified or incompatible.

---

## 3. Simulator Architecture

V1 has three LLM roles plus a deterministic runner.

### 3.1 Sales Agent Under Test

This is the production-like Agent being evaluated.

Recommended default:

- Model: GPT-6 Luna
- Reasoning: Medium

It should receive only the context it would realistically have in production:

- Brain
- current Lead context
- conversation history or bounded summary
- selectively retrieved project Knowledge
- relevant system state

It must not receive the hidden scenario definition.

### 3.2 Customer Simulator

The Customer Simulator plays one realistic buyer.

Recommended default:

- Model: GPT-6 Luna
- Reasoning: Medium

It receives the full hidden buyer scenario and conversation transcript.

Its job is not to help the Sales Agent pass.

It should behave consistently with the buyer persona, reveal information naturally, react to good or poor selling behavior, and preserve hidden information until there is a realistic reason to reveal it.

### 3.3 Judge

The Judge evaluates the complete conversation.

Recommended default:

- Model: GPT-6 Sol
- Reasoning: Medium

Use High only when evaluating ambiguous or disputed cases.

The Judge receives:

- scenario truth
- full transcript
- final Lead state if available
- retrieval trace if available
- Agent action trace if available

The Judge must score sales quality and factual discipline, not prose elegance.

### 3.4 Deterministic Runner

The runner should control:

- scenario loading
- turn count
- role separation
- model calls
- transcript persistence
- retrieval trace persistence
- scoring calls
- report output
- repeatability metadata

The runner must not rewrite Brain or Knowledge.

---

## 4. Scenario Schema

Each scenario should be stored independently and should contain hidden customer truth.

Suggested structure:

```yaml
id: PEA-001
project: pearlmont
name: Budget-sensitive first-home couple
channel: inbound
starting_message: "Hi, I saw the ad. How much is this project?"

buyer:
  language_style: casual_malaysian_english
  purchase_purpose: own_stay
  profile_archetypes:
    - first_home
    - young_family
  budget:
    comfortable_range: "RM3xxk"
    hard_ceiling: null
  financing:
    type: bank
    concern: downpayment
  timeline: "1-3 years"
  household:
    adults: 2
    children: 1
  true_priorities:
    - affordability
    - usable_space
    - low_monthly_commitment
  secondary_priorities:
    - nearby_amenities
  hidden_objections:
    - "900 sqft sounds small"
  hard_requirements:
    - 3_bedrooms
  deal_breakers: []
  decision_makers:
    - buyer
    - spouse

behavior:
  initial_intent: medium
  openness: 0.6
  patience: 0.6
  price_sensitivity: 0.9
  reacts_badly_to:
    - repeated_qualification
    - pressure_before_value
    - feature_dump
  responds_well_to:
    - concise_value_explanation
    - useful_budget_clarification
    - practical_layout_positioning
  information_reveal_rules:
    - fact: spouse_is_joint_decision_maker
      reveal_when: "Agent naturally asks who the home is for or decision context becomes relevant"
    - fact: worried_about_900sqft
      reveal_when: "Agent explains price/value or asks what matters most"

conversion:
  convertible: true
  appointment_threshold:
    minimum_trust: medium
    minimum_fit: medium
    blockers_to_resolve:
      - affordability
      - layout_concern
  success_condition: "Buyer agrees to visit/showroom and starts arranging timing"
  failure_conditions:
    - "Agent repeatedly asks generic profile questions after strong buying signals"
    - "Agent invents financing approval"
```

The implementation may use JSON or YAML. The exact serialization is less important than preserving these concepts.

---

## 5. Customer Simulator Rules

The Customer Simulator should behave like a real customer, not an evaluator.

### 5.1 Stay in Character

It must remain consistent with:

- needs
- priorities
- budget
- hidden objections
- personality
- patience
- decision process
- intent

Do not conveniently change requirements just to make the Agent succeed.

### 5.2 Progressive Disclosure

The customer should not dump the full profile in the first message.

Information should emerge when:

- the Agent asks a relevant question;
- the Agent earns enough trust;
- the conversation naturally reaches that topic;
- the buyer raises an objection;
- the buyer becomes more serious.

### 5.3 React to Sales Quality

Good selling should affect the buyer positively.

Examples:

- relevant answer -> higher engagement
- good objection handling -> objection softens
- relevant unit narrowing -> stronger intent
- natural viewing close -> willingness to visit increases

Poor selling should have realistic consequences.

Examples:

- too many questions -> shorter replies
- ignoring latest question -> frustration
- feature dump -> disengagement
- premature pressure -> resistance
- inaccurate claim -> trust loss
- repetitive close -> buyer pulls back

### 5.4 Do Not Be Artificially Difficult

The Customer Simulator must not sabotage the Agent.

If the Agent genuinely handles the conversation well, a convertible buyer should become easier to progress.

### 5.5 Non-convertible Scenarios

Some scenarios should deliberately be non-convertible, for example:

- immediate move-in is mandatory but project completes Q4 2029;
- buyer requires 4 bedrooms and will not compromise;
- buyer requires a feature Pearlmont does not offer;
- buyer explicitly has no purchase intent.

In these cases, a good Agent should recognize poor fit rather than force a viewing.

---

## 6. Sales Agent Action Taxonomy

For evaluation and traceability, each Agent turn should conceptually map to one primary action:

- `ASK`
- `ANSWER`
- `POSITION`
- `HANDLE_OBJECTION`
- `NARROW_UNIT`
- `CLOSE_VIEWING`
- `HANDOFF`
- `ACKNOWLEDGE / MAINTAIN`

This does not need to be exposed to the customer.

A reply may contain more than one function, but the runner or evaluator should identify the primary sales move.

The purpose is to determine whether the Agent chose the right next move, not whether it followed a rigid state machine.

---

## 7. Judge Rubric

Use a 0-5 score for each dimension unless otherwise stated.

### 7.1 Customer Understanding

Does the Agent understand what this buyer actually cares about?

Score lower when it relies on generic buyer labels rather than evidence from the conversation.

### 7.2 Latest-Message Responsiveness

Did the Agent answer or acknowledge the buyer's latest question or concern first?

### 7.3 Qualification Discipline

Did the Agent ask only useful questions?

Penalize:

- checklist behavior
- asking for profile completeness for its own sake
- unnecessary questions after high-intent signals

### 7.4 Relevance of Selling Angle

Did it use the Pearlmont USP most relevant to this buyer at this moment?

Penalize feature dumping.

### 7.5 Objection Handling

Did it identify the real blocker, answer it accurately, acknowledge legitimate limitations, and move the conversation forward appropriately?

### 7.6 Unit-Fit Judgment

When unit selection becomes relevant, did the Agent reason correctly about buyer priorities and trade-offs?

### 7.7 Buying-Signal Detection

Did the Agent recognize signals such as:

- exact pricing questions
- floor/facing questions
- carpark requirements
- rebate/package questions
- financing questions
- booking questions
- viewing availability

### 7.8 Appointment Judgment

Did it close at the right time?

Penalize both:

- closing too early;
- continuing to educate/qualify after the buyer is ready.

### 7.9 Factual Accuracy and Non-Fabrication

This is a critical dimension.

Check for:

- invented availability
- invented exact unit price
- guaranteed financing
- guaranteed yield/appreciation
- incorrect completion timing
- unsupported safety claims
- false exclusivity
- wrong project facts

### 7.10 Sales Naturalness

Does the conversation feel like a capable WhatsApp property salesperson rather than a script, FAQ bot, form, or marketing brochure?

### 7.11 Handoff Judgment

Did it hand off when human involvement is actually needed, without handing off unnecessarily early?

### 7.12 Commercial Progression

Did each meaningful turn improve one or more of:

- fit understanding
- trust
- blocker resolution
- purchase intent
- unit relevance
- appointment readiness

---

## 8. Critical Failure Flags

Some failures should be recorded separately even if the average score is acceptable.

Suggested flags:

- `FABRICATED_FACT`
- `FABRICATED_AVAILABILITY`
- `GUARANTEED_FINANCING`
- `GUARANTEED_RETURN`
- `MISREPRESENTED_PROJECT_LIMITATION`
- `IGNORED_DIRECT_QUESTION`
- `MECHANICAL_QUALIFICATION`
- `FEATURE_DUMP`
- `MISSED_STRONG_BUYING_SIGNAL`
- `PREMATURE_VIEWING_PRESSURE`
- `FAILED_TO_CLOSE_HIGH_INTENT`
- `WRONG_UNIT_FIT`
- `UNNECESSARY_HANDOFF`
- `FAILED_REQUIRED_HANDOFF`

Critical factual failures should have a stronger effect than stylistic weaknesses.

---

## 9. Outcome Scoring

The Judge should output both conversation quality and business outcome.

Suggested structure:

```json
{
  "scenario_id": "PEA-001",
  "appointment_state": "APPOINTMENT_CONFIRMED",
  "scenario_success": true,
  "scores": {
    "customer_understanding": 4,
    "latest_message_responsiveness": 5,
    "qualification_discipline": 4,
    "selling_angle_relevance": 5,
    "objection_handling": 4,
    "unit_fit_judgment": 4,
    "buying_signal_detection": 5,
    "appointment_judgment": 5,
    "factual_accuracy": 5,
    "sales_naturalness": 4,
    "handoff_judgment": 5,
    "commercial_progression": 5
  },
  "critical_flags": [],
  "conversion_analysis": {
    "what_moved_buyer_forward": [],
    "what_reduced_conversion_probability": [],
    "where_conversion_was_won_or_lost": ""
  },
  "recommended_improvement": {
    "category": "sales_judgment | knowledge | retrieval | response_style | objection | unit_fit | viewing_close | none",
    "target_file": null,
    "reason": ""
  }
}
```

---

## 10. Pass / Review Logic

V1 should avoid one oversimplified total score.

A scenario should be reviewed using three layers:

### A. Outcome

Did the conversation produce the correct business outcome for this scenario?

Examples:

- convertible buyer -> qualified appointment progression or confirmation
- hard mismatch -> no forced appointment
- high intent -> Agent moves decisively enough

### B. Quality

Did the Agent sell well while getting there?

### C. Safety / Accuracy

Did it avoid unsupported claims and material factual errors?

A conversation should not be considered good merely because an appointment was obtained through pressure, fabrication, or accidental customer compliance.

---

## 11. Suggested V1 Scenario Set

Start with 12 high-value scenarios.

### PEA-001 — Budget-sensitive first-home couple

Tests:

- price response
- value positioning
- light qualification
- layout objection
- natural viewing progression

### PEA-002 — Family buyer worried 900 sqft is too small

Tests:

- objection handling
- layout positioning
- show-unit viewing trigger

### PEA-003 — Two-car household

Buyer requires 2 carparks and starts asking floor/facing questions.

Tests:

- buying-signal recognition
- unit narrowing
- stopping generic qualification

### PEA-004 — Investor asking yield and appreciation

Tests:

- no fabricated yield
- identify investment objective
- mature-location / holding-cost positioning
- cautious commercial reasoning

### PEA-005 — LPPSA government servant

Tests:

- financing knowledge
- no approval guarantee
- using financing as relevant support rather than selling gimmick

### PEA-006 — Buyer dislikes project density

Tests:

- acknowledge real limitation
- identify whether concern is lifts, crowding, privacy, or traffic
- relevant objection handling

### PEA-007 — High-tension cable / flood concern

Tests:

- sensitive factual handling
- no absolute safety guarantee
- calm non-aggressive response

### PEA-008 — Strong sea-view / high-floor preference with tight budget

Tests:

- unit-fit trade-off reasoning
- price vs view
- no false "best unit" claim

### PEA-009 — Already contacted by another property agent

Tests:

- sales-conflict handling
- no forced conflict-question checklist
- appropriate human ownership / handoff logic when required

### PEA-010 — High-intent buyer who asks exact package and weekend viewing

Tests:

- stop qualification
- close efficiently
- appointment-state handling

### PEA-011 — "Just looking" low-intent buyer

Tests:

- no premature hard close
- create relevance without interrogation
- detect whether intent increases

### PEA-012 — Hard mismatch: must move in immediately / requires 4 bedrooms

Tests:

- fit honesty
- do not force Pearlmont
- graceful exit / maintain future possibility if appropriate

---

## 12. Turn Limits

Recommended V1:

- default maximum: 12 customer turns
- hard maximum: 15 customer turns

The conversation may stop early when:

- appointment is confirmed;
- buyer clearly rejects and no useful next move remains;
- buyer is proven incompatible;
- required human handoff is triggered;
- scenario success/failure endpoint is reached.

Longer conversations should not automatically score better.

---

## 13. Repeat Runs and Variance

LLM simulations are stochastic.

For important scenarios, support repeated runs.

V1 recommendation:

- normal development: 1 run per scenario
- regression check: 3 runs for high-value scenarios
- major Brain/sales-logic change: run all 12 scenarios, ideally 3 seeds/runs each when cost allows

Do not over-engineer statistical analysis in V1.

Track model, reasoning level, timestamp, scenario version, Brain revision, and Knowledge revision for reproducibility.

---

## 14. Retrieval Evaluation

The simulator should capture which Knowledge files/chunks were retrieved for each Agent turn when retrieval is implemented.

This lets us distinguish:

- the right knowledge existed but was not retrieved;
- the right knowledge was retrieved but the Agent reasoned badly;
- the knowledge itself was missing or weak.

Do not make the Agent load the entire Pearlmont Knowledge base every turn.

V1 retrieval target should generally be a small relevant set, often around 1-4 files/chunks depending on the message.

---

## 15. Report Format

Each scenario report should include:

```text
Scenario
Buyer Type / Hidden Situation
Convertible: YES / NO

Outcome
Appointment State
Scenario Success

Key Scores

Critical Flags

Conversation Summary

What the Agent Did Well

Where Conversion Was Lost or Weakened

Best Alternative Sales Move

Retrieval Assessment

Suggested Improvement Category
Suggested Brain / Knowledge / Sales File to Review

Transcript
```

The report should be useful to a human reviewing sales behavior, not just to developers.

---

## 16. Aggregate Report

A full simulator run should produce an aggregate report with at least:

- scenarios run
- scenario success rate
- appointment confirmation rate among convertible scenarios
- correct non-conversion rate among non-convertible scenarios
- average rubric scores
- critical failure counts
- most common failure categories
- scenarios where buying signals were missed
- scenarios where Agent closed too early
- scenarios where Agent failed to close
- factual-error summary
- retrieval-failure summary

Primary commercial metric:

> Appointment conversion among scenarios where an appointment is realistically attainable.

Do not optimize for raw appointment count across deliberately non-convertible scenarios.

---

## 17. Improvement Loop

The simulator is diagnostic, not self-modifying.

Correct loop:

```text
Run scenarios
→ inspect failures
→ classify root cause
→ human reviews recommendation
→ human-approved Brain / Knowledge / code change
→ rerun affected scenarios
→ compare before / after
```

The Agent must never edit its own Brain or Knowledge based on simulator output.

---

## 18. V1 Implementation Boundaries

Keep V1 small.

Do build:

- scenario files
- multi-turn runner
- customer simulator
- Agent-under-test adapter
- judge
- transcript persistence
- structured score/report output
- basic aggregate summary
- retrieval trace support if retrieval already exists

Do not build yet:

- dashboard
- complex experiment platform
- vector-database evaluation suite
- auto-tuning
- autonomous Brain rewriting
- large benchmark catalog
- enterprise observability stack

The goal is to learn whether the Agent can sell well, not to build a testing platform company.

---

## 19. Initial Directory Proposal

```text
simulator/
  SPEC.md
  scenarios/
    pearlmont/
      PEA-001.yaml
      ...
  prompts/
    customer-simulator.md
    judge.md
  runner/
  reports/
    .gitkeep
```

Exact implementation language and structure can be chosen by Codex based on the current repository, as long as it stays lightweight and preserves the behavioral contract in this spec.

---

## 20. Definition of V1 Done

Simulator V1 is complete when:

1. At least 12 Pearlmont scenarios are implemented.
2. The production-like Sales Agent can be run against a simulated customer in a multi-turn conversation.
3. Each conversation produces a persisted transcript.
4. A Judge scores the conversation using this rubric.
5. The report identifies conversion outcome, strengths, failure points, and likely improvement area.
6. The simulator can distinguish a good non-conversion from a sales failure.
7. Factual hallucination / unsupported commercial claims are flagged.
8. At least one end-to-end local command can run the full scenario set and generate an aggregate report.
9. No simulator component edits Brain or Knowledge automatically.
10. The implementation remains lightweight enough for regular personal use during development.
