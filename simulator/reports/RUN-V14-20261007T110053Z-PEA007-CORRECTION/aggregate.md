# Simulator V1.4 Aggregate Diagnostic

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 0/1 convertible scenarios (0.0). The AI made 3 Human support requests; 3 were resolved from scenario fixtures and 2 were judged as successful AI resumption. 0 support-enabled scenarios reached appointment readiness. The Agent completed 0 appropriate appointment-ready handoffs, with 0 premature formal handoffs, 0 missed-ready buyers, and 0 end-to-end confirmed appointments. Support is an allowed capability and does not itself count as a sales handoff. Per-scenario weaknesses and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 1 | — |
| Appointment-ready AI successes | 0 | 0.0 |
| Successful appointment-ready handoffs | 0 | 0.0 |
| Premature appointment handoffs | 0 | None of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Support requests | 3 | — |
| Support completion rate | 3/3 | 1.0 |
| AI resume-success rate | 2/3 | 0.667 |
| Appointment Ready reached after support | 0 | — |
| Human operational completion after successful handoff | 0 | None |
| Bad-fit correctly identified | 0 | None of non-convertible |

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
  "SUPPORT_RESULT_OVERSTATED": 0
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
    "appointment_ready_ai_successes": 0,
    "appointment_ready_ai_success_rate": 0.0,
    "successful_appointment_handoffs": 0,
    "premature_handoffs": 0,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 0,
    "support_requests": 3,
    "support_completion_rate": 1.0,
    "support_result_utilization_score": 4.0,
    "duplicate_support_requests": 1,
    "failed_resume_cases": 0,
    "ai_resume_success_rate": 0.667
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 0,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 1,
  "AI_EARLY_HANDOFF": 0,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
  "MANDATORY_OPERATIONAL_HANDOFF": 0,
  "BAD_FIT_CORRECTLY_IDENTIFIED": 0
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
    "appointment_ready_ai_successes": 0,
    "appointment_ready_ai_success_rate": 0.0,
    "successful_appointment_ready_handoffs": 0,
    "premature_handoffs": 0,
    "confirmed_appointments": 0,
    "commercial_progression": 3.0,
    "naturalness": 4.0,
    "handoff_judgment": 5.0,
    "useful_information_capture": 4.0,
    "retrieved_knowledge_utilization": 5.0
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 4.0/5
- Readiness detection accuracy: 1.0
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): None
- Retrieval quality/utilization: 5.0/5
- Critical failures: 2
- Post-handoff AI reply violations: 0
- All scenarios completed: 1/1

## Average Judge scores

- customer_understanding: 5.0/5
- latest_message_responsiveness: 5.0/5
- qualification_discipline: 4.0/5
- selling_angle_relevance: 4.0/5
- objection_handling: 5.0/5
- unit_fit_judgment: 3.0/5
- buying_signal_detection: 4.0/5
- appointment_judgment: 5.0/5
- factual_accuracy: 5.0/5
- sales_naturalness: 4.0/5
- handoff_judgment: 5.0/5
- commercial_progression: 3.0/5
- appointment_readiness_detection: 5.0/5
- handoff_timing: 5.0/5
- handoff_reason_correctness: 5.0/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 5.0/5
- useful_information_capture: 4.0/5
- appointment_ready_progression: 2.0/5
- retrieved_knowledge_utilization: 5.0/5
- support_request_judgment: 3.0/5
- support_result_utilization: 4.0/5
- support_resume_quality: 4.0/5

## Retrieval misses

- None identified.

## Retrieved Knowledge not used

- None identified.

## Remaining Knowledge gaps

- PEA-007: The retrieved FAQ Knowledge states the approximate 36 m distance, 20 m reference, raised platform, and river-management information, but does not establish the underlying standard for the 20 m figure or provide independent engineering or block-specific flood-history evidence.
- PEA-007: The support answer did not confirm an actual FAQ, plans, document link, or technical contact.

## Remaining sales weaknesses

- PEA-007: Turn 6 repeated the technical-contact availability query already made at turn 4; the result was reused rather than newly verified.

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
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
