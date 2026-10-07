# Simulator V1.4 Aggregate Diagnostic

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 6/9 convertible scenarios allowed to continue normal sales flow (0.667). It resumed successfully after 11/12 resolved support results and reached readiness after support in 5 scenarios. This shows useful capability but not full reliability: the run flagged 1 duplicate support request(s) and 1 overstated support result(s). The Agent completed 6 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 1 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 6 | 0.667 |
| Successful appointment-ready handoffs | 6 | 0.545 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 1 | 0.091 |
| Support requests | 12 | — |
| Support completion rate | 12/12 | 1.0 |
| AI resume-success rate | 11/12 | 0.917 |
| Appointment Ready reached after support | 5 | — |
| Human operational completion after successful handoff | 1 | 0.167 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 1,
  "DUPLICATE_SUPPORT_REQUEST": 1,
  "SUPPORT_RESULT_NOT_USED": 0,
  "SUPPORT_RESULT_ONLY_RELAYED": 0,
  "FAILED_TO_RESUME_SELLING": 0,
  "MISSED_READY_AFTER_SUPPORT": 0,
  "PREMATURE_APPOINTMENT_HANDOFF": 0,
  "FAILED_APPOINTMENT_HANDOFF": 0,
  "OVERQUALIFICATION_AFTER_SUPPORT": 0,
  "SUPPORT_RESULT_OVERSTATED": 1
}

## V1.2 direct comparison

{
  "baseline_run": "RUN-V12-20261007T015000Z",
  "baseline_metrics": {
    "appointment_ready_ai_successes": 1,
    "appointment_ready_ai_success_rate": 0.091,
    "successful_appointment_ready_handoffs": 1,
    "premature_handoffs": 7,
    "missed_ready_buyers": 1,
    "end_to_end_confirmed_appointments": 1,
    "critical_failure_count": 24
  },
  "v1_3_metrics": {
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_handoffs": 6,
    "premature_handoffs": 0,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 1,
    "support_requests": 12,
    "support_completion_rate": 1.0,
    "support_result_utilization_score": 4.5,
    "duplicate_support_requests": 1,
    "failed_resume_cases": 0,
    "ai_resume_success_rate": 0.917
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 6,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 3,
  "AI_EARLY_HANDOFF": 0,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
  "MANDATORY_OPERATIONAL_HANDOFF": 2,
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
  "v1_3_metrics": {
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.545,
    "successful_appointment_ready_handoffs": 6,
    "premature_handoffs": 0,
    "confirmed_appointments": 1,
    "commercial_progression": 4.08,
    "naturalness": 4.25,
    "handoff_judgment": 4.92,
    "useful_information_capture": 4.25,
    "retrieved_knowledge_utilization": 4.67
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 4.25/5
- Readiness detection accuracy: 1.0
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.12
- Retrieval quality/utilization: 4.67/5
- Critical failures: 3
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 4.83/5
- latest_message_responsiveness: 4.58/5
- qualification_discipline: 4.67/5
- selling_angle_relevance: 4.17/5
- objection_handling: 4.58/5
- unit_fit_judgment: 4.08/5
- buying_signal_detection: 4.75/5
- appointment_judgment: 4.92/5
- factual_accuracy: 4.67/5
- sales_naturalness: 4.25/5
- handoff_judgment: 4.92/5
- commercial_progression: 4.08/5
- appointment_readiness_detection: 4.92/5
- handoff_timing: 4.92/5
- handoff_reason_correctness: 5.0/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 5.0/5
- useful_information_capture: 4.25/5
- appointment_ready_progression: 4.08/5
- retrieved_knowledge_utilization: 4.67/5
- support_request_judgment: 4.67/5
- support_result_utilization: 4.5/5
- support_resume_quality: 4.58/5

## V1.4 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 6/9 (0.667) |
| Successful appointment handoffs | 6 |
| Mandatory operational handoffs | 2 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 12 / 12 (1.0) |
| AI resume success | 11/12 (0.917) |
| Support result utilization | 4.5/5 |
| Duplicate support requests | 1 |
| Failed resume cases | 0 |
| Appointment Ready after Support | 5 |
| End-to-end confirmed appointments | 1 |
| Correct bad-fit identifications | 1 |
| Useful information capture | 4.25/5 |
| Retrieved Knowledge utilization | 4.67/5 |
| Commercial progression | 4.08/5 |
| Naturalness | 4.25/5 |
| Critical failure flags | 3 |

## V1.3 comparison

{
  "baseline_run": "RUN-V13-20261007T023345Z",
  "baseline": {
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.545,
    "normal_sales_flow_convertible_scenarios": 10,
    "appointment_ready_ai_success_rate_comparable": 0.6,
    "support_requests": 14,
    "support_resolution_rate": 0.429,
    "ai_resume_success_rate": 0.833,
    "appointment_ready_after_support": 4,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "missed_ready_buyers": 0,
    "commercial_progression": 3.0,
    "naturalness": 3.0,
    "support_result_utilization": 4.42,
    "critical_failures_legacy_reported": 8,
    "critical_failures_reclassified_using_v1_4_scope": 5,
    "judge_score_means_reliable": false
  },
  "v1_4": {
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.667,
    "support_requests": 12,
    "support_resolution_rate": 1.0,
    "ai_resume_success_rate": 0.917,
    "appointment_ready_after_support": 5,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 2,
    "missed_ready_buyers": 0,
    "commercial_progression": 4.08,
    "naturalness": 4.25,
    "support_result_utilization": 4.5,
    "critical_failures": 3
  },
  "comparison_note": "V1.3 unavailable Human Support outcomes are not treated as AI failures for the support-resolution comparison. V1.3 score averages are unreliable due missing-score fallback/default behavior; V1.4 shows validated Judge means."
}

## Judge score integrity

{
  "present": true,
  "evidence": "Yes. Accepted V1.3 per-scenario report artifacts contain 3s for dimensions absent from the Judge payload, introduced by the rescore/defaulting pass. The committed V1.3 aggregate path itself treated missing values as zero, but also explicitly defaulted post_handoff_suppression to 5. V1.4 validates every required score and has no neutral-score fallback.",
  "comparison_score_caveat": "V1.3 Judge score means are unreliable; unavailable Human Support responses are not counted as Agent failures in the V1.4 comparison."
}

## Retrieval misses

- PEA-004: The retrieved pricing.md is explicitly a base-price reference, not current effective pricing. The AI appropriately requested operational verification rather than treating the base price as current.
- PEA-008: Current unit availability and a specific viewing slot were not available in retrieved Knowledge; the support fixture did not verify availability, and the human executor could not verify a slot.
- PEA-010: Retrieved Knowledge did not verify current package validity or a live Saturday slot; the simulator support fixture supplied those operational facts.

## Retrieved Knowledge not used

- PEA-001: At turn 1, retrieved sales-package knowledge said to normally lead a simple price enquiry with the effective post-package entry point. The AI instead opened with the base-price figure and a calculated rebate estimate.
- PEA-002: Bedroom-specific area figures and foyer area were available in the retrieved layout source but not used. These were optional details and would not by themselves answer the furniture-clearance concern.

## Remaining Knowledge gaps

- PEA-001: No verified itemized list of other upfront costs was supplied.
- PEA-001: No specific available appointment slot was verified or held.
- PEA-001: A specific unit-level price and availability still require confirmation.
- PEA-002: The retrieved Pearlmont Knowledge contains bedroom areas and project-material layout descriptions, but no bedroom dimensions or furniture-clearance measurements.
- PEA-002: The appointment calendar was NOT_CONNECTED, so the available viewing times could not be verified.
- PEA-003: The human executor could not verify live inventory or confirm a viewing slot. The support fixture is simulator-only evidence, not Pearlmont factual Knowledge or a real-world inventory record.
- PEA-004: No substantiated rental comparables, approved yield guidance, or appreciation forecast were available.
- PEA-004: No current remaining inventory was verified.
- PEA-004: The current Type A price basis in the support result is simulator-only evidence, not Pearlmont factual Knowledge or proof of a live pricing-system connection.
- PEA-004: Actual rental demand, competing supply, and exit prospects remain unestablished.
- PEA-005: The support fixture did not establish the buyer's individual eligibility, approval, or applicant-specific document requirements.
- PEA-005: The human executor supplied an indicative Type A starting price but not a full unit-specific price schedule or availability confirmation.
- PEA-005: The human executor did not identify a specific person or LPPSA channel for verifying requirements.
- PEA-006: The supplied sources and simulator access fixture do not establish peak-hour crowding or noise levels.
- PEA-006: The simulator access fixture does not confirm separate entrances or lift areas between residential blocks.
- PEA-006: Evening slots and access to the residential lift lobby were not verified by the human executor.
- PEA-007: The retrieved FAQ Knowledge states the approximate 36 m distance, 20 m reference, raised platform, and river-management information, but does not establish the underlying standard for the 20 m figure or provide independent engineering or block-specific flood-history evidence.
- PEA-007: The support answer did not confirm an actual FAQ, plans, document link, or technical contact.
- PEA-008: Current availability of unit 1C-12-03.
- PEA-008: Whether a Saturday 2–4pm viewing slot is available.
- PEA-008: Actual view from the unit, which the fixture says should be checked at a visit.
- PEA-009: The transcript ends without a further customer-facing response to the buyer's final confirmation question. AI was correctly paused after handoff; no additional human response is shown.
- PEA-010: The fixture did not verify the full package breakdown or terms, or an exact unit-specific price.
- PEA-010: The package price and Saturday slot are simulator-only evidence, not Pearlmont factual Knowledge or proof of a real live-system connection.

## Remaining sales weaknesses

- PEA-001: The opening price response led with the RM328k base figure and calculated an approximate RM302k amount, rather than leading with the retrieved current-package entry-price guidance and clearly separating base price from package price. The later support-backed response clarified the one-carpark reference.
- PEA-002: It did not obtain more specific bedroom-fit evidence before moving to the viewing. The available Knowledge provided bedroom areas but not dimensions or furniture clearances; a suitably bounded support query could potentially have added detail, though it was not necessary to reach readiness.
- PEA-003: The handoff wording could have made the outstanding operational checks and their unconfirmed status more explicit. This did not make the handoff premature or undermine AI appointment-ready success.
- PEA-004: The AI could have made the investment comparison slightly more actionable by offering to compare the buyer's own completed-condo figures against Pearlmont's known costs, while clearly noting that Pearlmont rent evidence was unavailable. This was a minor opportunity, not a missed appointment signal.
- PEA-005: After the buyer asked to check the current price schedule, the AI did not obtain or provide that information itself before the requested human transfer. The transfer was nevertheless valid because the buyer explicitly asked to connect with someone.
- PEA-006: No material sales or support failure. The AI appropriately left specific lobby access and evening timing for operational verification rather than implying either was confirmed.
- PEA-007: Turn 6 repeated the technical-contact availability query already made at turn 4; the result was reused rather than newly verified.
- PEA-008: Claimed current availability was confirmed when neither the support fixture nor retrieved Knowledge verified it.
- PEA-009: The initial response was brief and did not explicitly acknowledge the buyer's concern about avoiding duplicate follow-up, though the promised check addressed it.
- PEA-010: The brief resumption could have more explicitly tied viewing with the spouse to assessing the relevant unit/package options, though the direct scheduling question was appropriate for this high-intent buyer.
- PEA-011: Both replies were generic maintenance. The first could have offered a concise project orientation or invited one specific, optional question; the second largely repeated the invitation to message later.
- PEA-012: The flexibility question was reasonable but not essential given the buyer's stated requirements; it did not lead to pressure or unnecessary further qualification.

## Critical failures

[
  {
    "scenario_id": "PEA-007",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "Turn 6 again asked whether a technical contact was available, a point already included in the turn 4 request. The result trace says the prior verified result was reused and no second lookup was performed.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-007",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-008",
    "flag": "SUPPORT_RESULT_OVERSTATED",
    "evidence": "The simulator-only fixture supplied the unit category, floor, sea-facing designation, car parks and scenario package total, but did not verify current availability. The agent nevertheless said, “I’ve confirmed unit 1C-12-03 is available.”",
    "turn": 4
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True


## Rerun notes

# V1.4 scenario reruns

PEA-001, PEA-004 and PEA-010 were rerun after audit found unmatched valid price/package or customer-shareable plan checks. PEA-007 was rerun to let Human Support verify the document-summary question before any person-to-person transfer. Their final reports replace the initial scenario results in this accepted run. The correction source files remain in the sibling `RUN-V14-20261007T110053Z-CORRECTIONS/` and `RUN-V14-20261007T110053Z-PEA007-CORRECTION/` directories. The remaining eight scenarios completed in the original full-suite run.

PEA-007 used the `SIMULATOR_SYNTHETIC_VERIFIED_FIXTURE` technical summary (three requests, all resolved); it completed at `AI_PROGRESS_BUT_NOT_READY` without an appointment push because the buyer remained evidence-gated. One repeated technical-contact request was flagged as duplicate.
