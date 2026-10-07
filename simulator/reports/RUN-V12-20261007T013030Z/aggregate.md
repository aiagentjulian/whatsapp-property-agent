# Simulator V1.2 Aggregate Diagnostic

**Executive summary:** V1.2 appointment-ready AI success was 3/11 convertible scenarios (0.273); successful operational handoffs 3/11. This measures the early-stage job, not completed property sales. Human completed 3/3 operational tasks after successful handoff. Whether performance is reliable depends on the primary success rate and the remaining captured-information and sales-progression weaknesses detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 3 | 0.273 |
| Successful appointment-ready handoffs | 3 | 0.273 |
| Premature handoffs | 6 | 0.6 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Human operational completion after successful handoff | 3 | 1.0 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 3,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 2,
  "AI_EARLY_HANDOFF": 6,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
  "BAD_FIT_CORRECTLY_IDENTIFIED": 1
}

## V1.1 comparison

{
  "baseline_run": "RUN-V11-20261007T004245Z",
  "baseline_metrics": {
    "appointment_ready_ai_successes_estimated_from_v1_1_fields": 2,
    "appointment_ready_handoff_successes_estimated_from_v1_1_fields": 2,
    "premature_handoffs": 1,
    "confirmed_appointments": 1,
    "commercial_progression": 3.17,
    "naturalness": 3.92,
    "handoff_judgment": 4.33,
    "useful_information_capture": "not scored in V1.1",
    "retrieved_knowledge_utilization": "not scored in V1.1"
  },
  "v1_2_metrics": {
    "appointment_ready_ai_successes": 3,
    "appointment_ready_ai_success_rate": 0.273,
    "successful_appointment_ready_handoffs": 3,
    "premature_handoffs": 6,
    "confirmed_appointments": 0,
    "commercial_progression": 3.0,
    "naturalness": 4.0,
    "handoff_judgment": 3.75,
    "useful_information_capture": 3.58,
    "retrieved_knowledge_utilization": 4.0
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to the V1.2 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 3.58/5
- Readiness detection accuracy: 0.833
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.5
- Retrieval quality/utilization: 4.0/5
- Critical failures: 19
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 4.33/5
- latest_message_responsiveness: 4.33/5
- qualification_discipline: 3.75/5
- selling_angle_relevance: 3.58/5
- objection_handling: 4.08/5
- unit_fit_judgment: 3.58/5
- buying_signal_detection: 3.92/5
- appointment_judgment: 4.0/5
- factual_accuracy: 4.42/5
- sales_naturalness: 4.0/5
- handoff_judgment: 3.75/5
- commercial_progression: 3.0/5
- appointment_readiness_detection: 4.33/5
- handoff_timing: 3.42/5
- handoff_reason_correctness: 4.58/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 4.17/5
- useful_information_capture: 3.58/5
- appointment_ready_progression: 2.92/5
- retrieved_knowledge_utilization: 4.0/5

## Retrieval misses

- PEA-002: The supplied retrieved material contains approximate room areas but no actual Type A floor-plan image or linear room dimensions. MISSING_SOURCE.
- PEA-003: The AI retrieval trace did not include knowledge/project/pearlmont/02_commercial/sales-package.md, which could have informed a cautious explanation of the documented sea-view/two-carpark package bands.
- PEA-003: No current unit-price source or live inventory source appears in the supplied material; exact price and availability therefore could not be verified.
- PEA-004: No material retrieval miss is evident for the questions answered. The retrieved sources contained the maintenance rate, unit count, base pricing structure, package caveats, and explicit guidance not to invent investment returns.
- PEA-005: No individual eligibility assessment or LPPSA document checklist is supplied in the retrieved material; MISSING_SOURCE for those details.
- PEA-006: MISSING_SOURCE: No authoritative typical-floor plan confirming whether lift lobbies or corridors are subdivided was present in the supplied retrieved material or simulator fixture.
- PEA-007: MISSING_SOURCE: the actual FAQ document requested by the buyer is not supplied.
- PEA-007: MISSING_SOURCE: no site flood-history record or drainage assessment is supplied.
- PEA-007: MISSING_SOURCE: no official engineering assessment or technical pylon safety opinion is supplied.
- PEA-009: No material retrieval miss: the relevant sales-conflict guidance was retrieved.
- PEA-011: Verified day-to-day local details such as traffic, nearby shops, and commute times were not available in the supplied retrieved material. MISSING_SOURCE.

## Retrieved Knowledge not used

- PEA-001: The retrieved package source contains rebate-category mechanics, but the AI appropriately avoided presenting a specific rebate or net price without a unit category and current confirmation.
- PEA-002: The 25.9 sq ft foyer figure was not shared by the AI, though it was not central to the buyer's main furniture-fit concern.
- PEA-003: knowledge/project/pearlmont/03_sales/unit-fit.md says to reduce generic discovery when a buyer asks about specific floor/view/carpark combinations, identify the key trade-off, and move toward suitable-category checking and viewing.
- PEA-003: knowledge/project/pearlmont/03_sales/unit-fit.md identifies confirmation of a two-carpark requirement as a viewing trigger.
- PEA-003: knowledge/project/pearlmont/01_facts/unit-and-layout.md gives the facing sides as well as floor ranges and directs exact unit-to-facing mapping to the latest schedule.
- PEA-003: The supplied sales-package material describes sea-view categories with two-carpark allocations by floor band, but does not establish live availability or an exact current price.
- PEA-004: The retrieved investor unit-fit guidance could have supported a concise discussion of entry cost and holding cost as relevant factors, while making clear that no rental-demand or return conclusion could be drawn.
- PEA-006: knowledge/project/pearlmont/01_facts/location-and-connectivity.md documents segregated residential and commercial access. This is not evidence that lift lobbies or corridors are divided into smaller sections.
- PEA-007: The retrieved unit-and-layout information was not relevant to this buyer's unresolved risk concerns.
- PEA-007: The retrieved viewing-close guidance supported not pushing a viewing while important factual uncertainty remained.
- PEA-008: knowledge/project/pearlmont/02_commercial/sales-package.md: The relevant sea-view rebate bands and the dependence on exact category and carpark allocation were retrieved but not used to frame the budget check.
- PEA-008: knowledge/project/pearlmont/03_sales/unit-fit.md: Its guidance to reduce generic discovery and move toward viewing once a buyer asks about specific floor/view combinations was not followed.
- PEA-009: The retrieved sales-conflict guidance allows a simple, optional question about whether someone has served or registered the customer; the AI skipped that clarification and transferred immediately.
- PEA-010: The sales-package guidance says not to present a dated package as current when validity is uncertain; the AI could have explicitly framed the 5%/8% rebates as a dated reference pending confirmation.
- PEA-010: The viewing-close guidance recommends moving directly to scheduling on weekend-viewing signals and keeping appointment friction low; collecting a preferred time before handoff would have helped.

## Remaining Knowledge gaps

- PEA-001: The supplied context has no verified live appointment availability or calendar connection; the simulator-only human_operations fixture records that slots could not be verified.
- PEA-001: The human response says no actual floor-plan document was available to share. No repository source path for that document is supplied: MISSING_SOURCE.
- PEA-001: Current unit-specific pricing and package validity remain unverified. The retrieved Knowledge at knowledge/project/pearlmont/02_commercial/pricing.md and knowledge/project/pearlmont/02_commercial/sales-package.md supports cautious explanation, not a confirmed current unit price.
- PEA-002: Actual Type A floor-plan image and length-by-width room dimensions are absent from the supplied material; the later human response correctly disclosed this.
- PEA-002: No unit-level availability fixture or connected appointment calendar was supplied. The human could not provide weekend slots or confirm a booking.
- PEA-003: Exact sea-facing unit and floor availability with two carparks.
- PEA-003: Current price for any matching available unit.
- PEA-003: Which priority the buyer would trade off if no option meets both preferences.
- PEA-003: A real project-sales contact or live channel for checking options.
- PEA-004: No verified rental comparables, rental yield, or appreciation forecast were supplied.
- PEA-004: The simulation had no connected current unit schedule, package-validity confirmation, or upfront-cost breakdown. These are simulator limitations, not verified real-world availability facts.
- PEA-005: Individual LPPSA eligibility remains unverified; the fixture supports only published reference terms.
- PEA-005: The supplied LPPSA reference does not provide a document checklist or confirm the best contact for current requirements.
- PEA-005: The customer's existing LPPSA financing status and property affordability context were not established before handoff.
- PEA-006: The lift-lobby and corridor subdivision detail remains unverified. The human_operations fixture explicitly says no authoritative tower-movement/corridor-control plan was supplied; this is simulator-only operational information, not Pearlmont factual Knowledge.
- PEA-007: Whether the actual FAQ document can be obtained or sent.
- PEA-007: Any verified site flood history or drainage assessment.
- PEA-007: Any official technical clarification or safety opinion regarding pylon exposure.
- PEA-008: No current unit schedule, unit-level prices, package eligibility for a particular unit, or unit-specific outlook was available in the simulator fixture.
- PEA-008: No viewing slots were connected, so no appointment time could be confirmed.
- PEA-009: Real-world registration and any team confirmation remained unverified; the simulator-only fixture is not Pearlmont factual Knowledge or evidence of live CRM capability.
- PEA-010: The current validity of the package dated 14 August 2026 is unverified.
- PEA-010: No exact unit-specific current price is verified.
- PEA-010: The 2pm slot was not verified; the fixture lists 11:00 as available only within the simulation.
- PEA-010: No real-world appointment availability or booking confirmation is established.
- PEA-011: Current neighborhood-level details about traffic, nearby services, and commute times were not established.

## Remaining sales weaknesses


## Critical failures

[
  {
    "scenario_id": "PEA-001",
    "flag": "No appointment confirmation",
    "evidence": "The buyer requested available times, but no specific available window was provided or explicitly accepted; the final state is viewing interest, not confirmation.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-001",
    "flag": "Simulator-only operational limits",
    "evidence": "The human_operations fixture states availability and appointment slots are NOT_CONNECTED; Human reported that no slots could be verified. This is not evidence of real production capability.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-003",
    "flag": "PREMATURE_HANDOFF",
    "evidence": "The AI handed off after one response without clarifying the two-carpark versus sea-facing trade-off or progressing a suitable viewing discussion.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-003",
    "flag": "UNSUPPORTED_OPERATIONAL_PROMISE",
    "evidence": "The AI said it would get the latest unit schedule checked, while the explicitly labeled simulator fixture supplies no live inventory or unit-number schedule.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-004",
    "flag": "EARLY_HANDOFF_BEFORE_APPOINTMENT_READINESS",
    "evidence": "At handoff the AI assessment was NOT_READY, and the buyer later said they would compare verified all-in costs against their 4% net benchmark before deciding whether to view.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-004",
    "flag": "SIMULATOR_ONLY_OPERATIONAL_FIXTURE",
    "evidence": "The human_operations fixture explicitly says no live CRM, inventory, pricing, calendar, or salesperson is connected; its verification task does not establish real-world prices or availability.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-005",
    "flag": "EARLY_HANDOFF",
    "evidence": "The AI handed off on the opening eligibility question without first establishing timeframe or basic purchase fit. The customer later said they hoped to buy within 3–6 months but would hold off viewing until LPPSA workability was known.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-005",
    "flag": "UNSUPPORTED_OPERATIONAL_PROMISE",
    "evidence": "The AI promised that the team would check individual eligibility and confirm latest terms, while the simulator-only fixture had no connected salesperson or individual assessment.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-006",
    "flag": "Formal handoff before appointment readiness",
    "evidence": "At handoff the buyer had not expressed viewing intent and said they wanted the layout information before deciding if viewing was worthwhile. The handoff was appropriate for factual verification, but the outcome is AI_EARLY_HANDOFF under the supplied definition because readiness had not been reached.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-006",
    "flag": "Layout answer unavailable",
    "evidence": "The simulator-only human operations fixture provides no authoritative corridor-control plan; the human appropriately reported that the layout could not be confirmed.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-007",
    "flag": "UNSUPPORTED_FOLLOW_UP_COMMITMENT",
    "evidence": "The AI said it would get documents checked and ask a technical team to clarify, while the fixture says no technical assessment is connected and does not supply the actual documents.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-007",
    "flag": "NO_AI_AFTER_FORMAL_HANDOFF",
    "evidence": "The system marked the handoff completed and AI paused; subsequent responses came from Human, not AI.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-008",
    "flag": "EARLY_HANDOFF_BEFORE_READY_BUYER_PROGRESSION",
    "evidence": "The buyer had already specified the priority trade-off, approximate budget, target blocks, and lower-floor option check; the agent assessed readiness only as EMERGING and handed off without testing conditional viewing intent or using the retrieved package guidance.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-008",
    "flag": "SIMULATOR_ONLY_OPERATIONS_LIMIT",
    "evidence": "The human_operations fixture explicitly states there is no live schedule, unit-level pricing, calendar, or salesperson connected; Human could not verify a suitable unit or confirm a slot.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-009",
    "flag": "EARLY_HANDOFF_BEFORE_APPOINTMENT_READINESS",
    "evidence": "The AI handed off at turn 1 with NOT_READY and no viewing intent; the customer had not yet asked the AI to check registration.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-009",
    "flag": "SIMULATOR_ONLY_OWNERSHIP_VERIFICATION",
    "evidence": "Human operations verified only the simulated record; the human explicitly stated that real-world registration and team confirmation were not verified.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-009",
    "flag": "AI_PAUSED_AFTER_HANDOFF",
    "evidence": "The formal handoff completed and AI status became PAUSED; no AI response followed.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-010",
    "flag": "SIMULATOR_ONLY_OPERATIONAL_CAPABILITY",
    "evidence": "The AI said it would get a colleague to confirm, but the fixture explicitly states that no live salesperson or follow-up channel is connected.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-010",
    "flag": "APPOINTMENT_NOT_CONFIRMED",
    "evidence": "The buyer made 11am conditional on package review and later explicitly held off; no specific time was accepted as a confirmed available real-world appointment.",
    "turn": 3
  }
]

## Fixture and integrity notes

Human operational facts are synthetic fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
