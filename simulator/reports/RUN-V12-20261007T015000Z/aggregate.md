# Simulator V1.2 Aggregate Diagnostic

**Executive summary:** No—this run does not demonstrate reliable early-stage sales performance: appointment-ready AI success was 1/11 convertible scenarios (0.091), with 7/10 formal handoffs classified as premature and a missed-ready count of 1. Successful operational handoffs were 1/11. This KPI measures the AI's sales work, not completed property sales. Human completed 0/1 operational tasks after successful handoff. The per-scenario weaknesses and useful-information findings are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 1 | 0.091 |
| Successful appointment-ready handoffs | 1 | 0.091 |
| Premature handoffs | 7 | 0.7 of handoffs |
| Missed-ready buyers | 1 | 0.091 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 1 | 0.091 |
| Human operational completion after successful handoff | 0 | 0.0 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 1,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 2,
  "AI_EARLY_HANDOFF": 7,
  "AI_MISSED_READY_BUYER": 1,
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
    "appointment_ready_ai_successes": 1,
    "appointment_ready_ai_success_rate": 0.091,
    "successful_appointment_ready_handoffs": 1,
    "premature_handoffs": 7,
    "confirmed_appointments": 1,
    "commercial_progression": 2.92,
    "naturalness": 4.25,
    "handoff_judgment": 3.58,
    "useful_information_capture": 4.25,
    "retrieved_knowledge_utilization": 4.25
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to the V1.2 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 4.25/5
- Readiness detection accuracy: 0.75
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.7
- Retrieval quality/utilization: 4.25/5
- Critical failures: 24
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 4.42/5
- latest_message_responsiveness: 4.25/5
- qualification_discipline: 3.92/5
- selling_angle_relevance: 3.67/5
- objection_handling: 4.17/5
- unit_fit_judgment: 3.83/5
- buying_signal_detection: 3.83/5
- appointment_judgment: 3.92/5
- factual_accuracy: 4.58/5
- sales_naturalness: 4.25/5
- handoff_judgment: 3.58/5
- commercial_progression: 2.92/5
- appointment_readiness_detection: 4.17/5
- handoff_timing: 3.33/5
- handoff_reason_correctness: 4.42/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 4.33/5
- useful_information_capture: 4.25/5
- appointment_ready_progression: 2.58/5
- retrieved_knowledge_utilization: 4.25/5

## Retrieval misses

- PEA-001: No shareable floor-plan file or current unit-specific price/availability source appears in the supplied retrieved material (MISSING_SOURCE).
- PEA-002: No official dimensioned floor-plan image was present in the supplied retrieved Knowledge. This is a source gap, not evidence that the AI failed to retrieve the available layout information.
- PEA-003: The supplied retrieved material does not provide a current category-by-category two-carpark schedule or live inventory. This remains MISSING_SOURCE.
- PEA-004: MISSING_SOURCE: No supplied Knowledge or simulator fixture provides sourced rental comparables, verified yield/appreciation data, or current available inventory.
- PEA-007: The requested official site plan/survey and flood assessment or JPS documents were not present in the supplied retrieved material: MISSING_SOURCE.
- PEA-008: No live unit schedule or unit-level price source was available in the supplied material; exact availability, unit mapping, and total cost could not be verified.

## Retrieved Knowledge not used

- PEA-001: The AI could have made the price caveat slightly more informative by explaining that current package eligibility depends on the exact unit category, floor/facing, and car-park allocation; it appropriately did not invent an exact price.
- PEA-002: The retrieved `knowledge/project/pearlmont/01_facts/unit-and-layout.md` describes the layout as having no long internal corridor, a relevant detail for the buyer's circulation concern.
- PEA-003: The unit-fit guide says to filter out one-carpark categories for a buyer whose two-carpark requirement is non-negotiable and identifies confirmation of that requirement as a viewing trigger.
- PEA-004: knowledge/project/pearlmont/01_facts/overview.md contains the Phase 1 total of 1,846 units. That is useful context but not current remaining inventory, so it should have been presented with that distinction.
- PEA-004: knowledge/project/pearlmont/02_commercial/sales-package.md describes package categories and warns that applicability depends on exact unit details and that package validity is time-sensitive. The AI could have explained this limitation alongside the base-price caveat.
- PEA-005: The LPPSA source says the up-to-90% margin reference applies when a first LPPSA financing remains active; the buyer said they have no active financing, so that condition should have been explicitly distinguished from their situation.
- PEA-006: The retrieved location-and-connectivity material says residential and commercial access are segregated. This could have been shared as a relevant but limited fact, with an explicit caveat that it does not confirm separation between towers.
- PEA-008: The retrieved unit-fit guidance says specific floor/view combinations are strong intent signals and should usually lead to narrowing the suitable category and proposing a viewing when appropriate.
- PEA-010: The viewing-close guidance recommends moving directly to scheduling for a weekend-viewing request and keeping appointment friction low; the AI could have collected the preferred time and attendees before handoff. Source: knowledge/project/pearlmont/03_sales/viewing-close.md.

## Remaining Knowledge gaps

- PEA-001: Current validity of the package and a specific unit's price against the buyer's budget remain unverified.
- PEA-001: The fixture does not provide unit availability, show-unit arrangements, or a floor-plan file.
- PEA-001: A rough monthly payment cannot be responsibly estimated without a confirmed price and financing assumptions such as rate and loan amount.
- PEA-002: A verified official Type A floor plan with dimensions was not available in the supplied material. Source recommendation: MISSING_SOURCE.
- PEA-003: Current categories allocated two carparks and whether any are available.
- PEA-003: Whether any available two-carpark category is sea-facing, and the closest currently available alternatives.
- PEA-003: The buyer's willingness to arrange a viewing or gallery discussion.
- PEA-004: MISSING_SOURCE: Sourced nearby rental comparables and substantiated yield or appreciation data.
- PEA-004: MISSING_SOURCE: Current available inventory or remaining phase supply.
- PEA-004: A specific unit and applicable current package/full-entry-cost calculation were not established by the supplied fixture.
- PEA-005: Retrieved Knowledge does not verify whether Pearlmont currently accepts LPPSA or provide the requested official application checklist.
- PEA-005: The simulator-only human_operations fixture lists eligibility as NOT_CONNECTED; it does not verify project acceptance or provide the requested task result.
- PEA-005: The supplied LPPSA reference terms are not individual eligibility or approval confirmation.
- PEA-006: Tower-specific lift-lobby and corridor separation is not established by the retrieved Knowledge.
- PEA-006: The human_operations fixture is simulator-only: it reports NOT_CONNECTED and supplies no authoritative tower-movement or corridor-control plan. The requested check was therefore not completed.
- PEA-006: MISSING_SOURCE: no authoritative tower-separation source is included in the retrieved material.
- PEA-007: No official site plan or survey confirming the Block 1B distance was supplied.
- PEA-007: No official flood assessment or JPS information was supplied.
- PEA-007: The simulator-only human response restated FAQ information but did not complete the requested document-check task.
- PEA-008: MISSING_SOURCE: Current unit-level availability, exact lower-floor stack/orientation mapping, and full unit-specific cost are not supplied.
- PEA-008: The human_operations fixture is simulator-only: it says no live schedule or unit-level price is connected. The human response therefore did not complete the requested verification.
- PEA-009: The supplied ownership guidance requires human verification but does not establish who can take over the relationship; the customer-facing choice remains unresolved.
- PEA-009: The CRM result was supplied by the explicitly simulator-only human_operations fixture, not retrieved Pearlmont factual Knowledge or evidence of live production capability.
- PEA-009: No buyer requirements, budget, purchase purpose, or timeline were established.
- PEA-010: No verified current package or exact unit-specific price was available.
- PEA-010: The 2:00 pm viewing slot was not verified.
- PEA-010: The 11:00 am slot came from an explicitly simulator-only fixture, not real-world availability.
- PEA-011: The retrieved material does not establish exact travel times or distances to the nearby places mentioned, or whether the wider neighbourhood is generally busy; the AI appropriately disclosed these limits.
- PEA-011: A detailed list of specific facilities was not available in the retrieved material, and the AI appropriately did not guess.

## Remaining sales weaknesses

- PEA-001: At customer turn 3, the buyer explicitly requested a floor plan and budget-fit unit check and said they were open to a show-unit viewing. The AI's per-turn assessment still marked NOT_READY, despite viewing having become an appropriate next step.
- PEA-002: It formally handed off while readiness was still emerging and promised to obtain an official floor-plan image without a verified source or supported fixture for delivering it.
- PEA-003: Treated inventory verification as a reason to hand off without recognizing that the buyer was already suitable for a viewing discussion or proposing one.
- PEA-004: It handed off before establishing the buyer’s return threshold or holding horizon and without using the retrieved Phase 1 total to answer the supply question as far as available evidence allowed.
- PEA-005: It formally handed off immediately after the buyer described a medium-term purchase plan, without establishing whether viewing or a project overview would be appropriate after the financing question is answered.
- PEA-006: The handoff response did not state the verified residential-versus-commercial access segregation, while making clear that tower-to-tower lobby and corridor separation remained unknown.
- PEA-007: It said it would get the official documents checked and confirm what could be shared, implying an operational capability the simulator fixture does not establish. The eventual human response could not provide or verify those documents.
- PEA-008: It handed off immediately after the buyer disclosed a clear budget, accepted a floor compromise, and requested a specific sea-view unit/package check tied to genuine purchase intent. It did not turn that progress into a conditional viewing invitation or establish whether a suitable option would make viewing appropriate.
- PEA-009: Handed off immediately without learning whether the customer wished to continue exploring Pearlmont. This was before appointment readiness and left meaningful sales discovery for whoever takes over.
- PEA-010: Handed off without first asking the buyer's preferred Saturday time or whether anyone else would attend, leaving a small amount of avoidable coordination work.
- PEA-011: The overview response described the commercial and school components broadly; a slightly more concise orientation could have kept the exchange even lighter. This did not materially impair the interaction.
- PEA-012: The initial question about whether the buyer would consider a later move-in or three bedrooms was not necessary to establish fit, given how clearly the requirements were stated, though it was brief and non-pressuring.

## Critical failures

[
  {
    "scenario_id": "PEA-001",
    "flag": "Readiness_under-detected_at_first_appropriate_viewing_point",
    "evidence": "The buyer asked for a budget-fit unit check and said they would be open to viewing a show unit, but the AI assessment remained NOT_READY. The AI marked READY_FOR_APPOINTMENT on its next turn.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-001",
    "flag": "Operational_task_not_completed",
    "evidence": "The simulator-only fixture says current unit pricing/package validity is not verified and availability/show-unit arrangements are NOT_CONNECTED; the human response also had no floor-plan file. The executor reported these limits but did not complete the requested checks.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-001",
    "flag": "Simulation_fixture_is_not_production_capability",
    "evidence": "The human_operations fixture explicitly states there is no live CRM, inventory, pricing, calendar, or salesperson connection. Its NOT_CONNECTED results are simulator-only.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-002",
    "flag": "EARLY_FORMAL_HANDOFF",
    "evidence": "The AI handed off at turn 3 with readiness assessed as EMERGING; the buyer had said they wanted to review the plan before deciding on a viewing.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-002",
    "flag": "UNSUPPORTED_DELIVERY_PROMISE",
    "evidence": "The AI said it would get the official floor-plan image, but the human could not verify or provide it and the task was not completed.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-002",
    "flag": "NO_APPOINTMENT_COMMITMENT",
    "evidence": "The buyer asked for the plan to assess furniture fit before deciding whether to view; no specific viewing time or window was accepted.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-003",
    "flag": "EARLY_FORMAL_HANDOFF",
    "evidence": "The buyer had established two carparks as a must-have, sea-facing as a preference, and floor flexibility, but the AI assessment remained EMERGING and it handed off without raising a viewing.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-003",
    "flag": "UNCOMPLETED_OPERATIONAL_TASK",
    "evidence": "The simulator-only human fixture explicitly had no live inventory or unit-number schedule; it reported that the requested category and availability checks remained unverified.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-003",
    "flag": "NO_AI_AFTER_HANDOFF",
    "evidence": "The AI was paused at formal handoff and did not respond afterward.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-004",
    "flag": "EARLY_HANDOFF",
    "evidence": "The AI formally handed off while its own assessment was NOT_READY; the buyer had requested evidence to judge an investment case, not a viewing or appointment.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-004",
    "flag": "RETRIEVED_FACT_NOT_USED",
    "evidence": "The retrieved overview states Phase 1 has 1,846 units. The AI did not share this contextual total or clarify that current available supply was unknown.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-004",
    "flag": "OPERATIONAL_TASK_NOT_COMPLETED",
    "evidence": "The human fixture supplied no current unit price/package or rental comparables. Its Phase 1 total does not complete the requested current-supply check or the AI’s package/comparables task.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-005",
    "flag": "EARLY_FORMAL_HANDOFF",
    "evidence": "The AI handed off at turn 2 while its assessment was EMERGING and before the buyer had expressed viewing intent or appointment readiness.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-005",
    "flag": "OPERATIONAL_TASK_NOT_COMPLETED",
    "evidence": "The human response said it could not verify Pearlmont LPPSA acceptance or the required documents; the fixture eligibility value is NOT_CONNECTED.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-005",
    "flag": "LPPSA_CONDITION_NEEDS_CONTEXT",
    "evidence": "The AI repeated the up-to-90% margin condition even after the buyer stated they had no active LPPSA financing, without clarifying that the cited condition concerned an active first financing.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-006",
    "flag": "FORMAL_HANDOFF_BEFORE_APPOINTMENT_READINESS",
    "evidence": "The AI handed off while its assessment was NOT_READY; the customer had said the separation information was needed before deciding whether the development felt manageable.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-006",
    "flag": "OPERATIONAL_TASK_NOT_COMPLETED",
    "evidence": "The simulator fixture returned NOT_CONNECTED and stated no authoritative plan was supplied; this is not a completed verification.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-006",
    "flag": "AI_PAUSED_AFTER_HANDOFF",
    "evidence": "No AI response followed HANDOFF_COMPLETED.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-007",
    "flag": "OPERATIONAL_CAPABILITY_IMPLIED",
    "evidence": "The agent promised to get the official documents checked, but the simulator fixture has no connected technical assessment and supplies no requested documents.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-007",
    "flag": "REQUESTED_OPERATION_NOT_COMPLETED",
    "evidence": "The human response stated it could not verify or provide the requested site plan/survey or flood/JPS documents; the fixture marks the task incomplete.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-008",
    "flag": "EARLY_HANDOFF_BEFORE_VIEWING_PROGRESSION",
    "evidence": "The buyer disclosed a RM350k ceiling, accepted a lower-floor compromise for a decent sea view, and requested a specific unit/package check; the AI handed off without testing conditional viewing interest or suggesting a viewing.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-008",
    "flag": "OPERATIONAL_TASK_NOT_COMPLETED",
    "evidence": "The simulator-only fixture reports NOT_CONNECTED, and the executor stated that availability, view, and total cost remained unverified.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-009",
    "flag": "EARLY_HANDOFF_BEFORE_APPOINTMENT_READINESS",
    "evidence": "The formal handoff occurred on the customer's opening question, before purchase fit or viewing intent was established; medium sales discovery remained.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-009",
    "flag": "CUSTOMER_POINT_OF_CONTACT_QUESTION_UNRESOLVED",
    "evidence": "After the human's single operational response, the customer asked whether this agent could take over or they should continue with the other agent. No answer is present.",
    "turn": 2
  }
]

## Fixture and integrity notes

Human operational facts are synthetic fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
