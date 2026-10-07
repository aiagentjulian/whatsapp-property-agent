# Simulator V1.4 Aggregate Diagnostic

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 10/10 convertible scenarios allowed to continue normal sales flow (1.0). It resumed successfully after 8/8 resolved support results and reached readiness after support in 12 scenarios. This shows useful capability but not full reliability: the run flagged 0 duplicate support request(s) and 0 overstated support result(s). The Agent completed 10 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 12 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 10 | 1.0 |
| Successful appointment-ready handoffs | 10 | 0.909 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 12 | 1.091 |
| Support requests | 11 | — |
| Support completion rate | 8/11 | 0.727 |
| AI resume-success rate | 8/8 | 1.0 |
| Appointment Ready reached after support | 12 | — |
| Human operational completion after successful handoff | 0 | 0.0 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 0,
  "DUPLICATE_SUPPORT_REQUEST": 0,
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
    "appointment_ready_ai_successes": 10,
    "appointment_ready_ai_success_rate": 1.0,
    "successful_appointment_handoffs": 10,
    "premature_handoffs": 0,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 12,
    "support_requests": 11,
    "support_completion_rate": 0.727,
    "support_result_utilization_score": 3.0,
    "duplicate_support_requests": 0,
    "failed_resume_cases": 0,
    "ai_resume_success_rate": 1.0
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 10,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 0,
  "AI_EARLY_HANDOFF": 0,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
  "MANDATORY_OPERATIONAL_HANDOFF": 1,
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
    "appointment_ready_ai_successes": 10,
    "appointment_ready_ai_success_rate": 0.909,
    "successful_appointment_ready_handoffs": 10,
    "premature_handoffs": 0,
    "confirmed_appointments": 12,
    "commercial_progression": 3.0,
    "naturalness": 3.0,
    "handoff_judgment": 3.0,
    "useful_information_capture": 3.0,
    "retrieved_knowledge_utilization": 3.0
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 3.0/5
- Readiness detection accuracy: 1.0
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.0
- Retrieval quality/utilization: 3.0/5
- Critical failures: 0
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 3.0/5
- latest_message_responsiveness: 3.0/5
- qualification_discipline: 3.0/5
- selling_angle_relevance: 3.0/5
- objection_handling: 3.0/5
- unit_fit_judgment: 3.0/5
- buying_signal_detection: 3.0/5
- appointment_judgment: 3.0/5
- factual_accuracy: 3.0/5
- sales_naturalness: 3.0/5
- handoff_judgment: 3.0/5
- commercial_progression: 3.0/5
- appointment_readiness_detection: 3.0/5
- handoff_timing: 3.0/5
- handoff_reason_correctness: 3.0/5
- post_handoff_suppression: 3.0/5
- conversion_attribution: 3.0/5
- useful_information_capture: 3.0/5
- appointment_ready_progression: 3.0/5
- retrieved_knowledge_utilization: 3.0/5
- support_request_judgment: 3.0/5
- support_result_utilization: 3.0/5
- support_resume_quality: 3.0/5

## V1.4 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 10/10 (1.0) |
| Successful appointment handoffs | 10 |
| Mandatory operational handoffs | 1 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 11 / 8 (0.727) |
| AI resume success | 8/8 (1.0) |
| Support result utilization | 3.0/5 |
| Duplicate support requests | 0 |
| Failed resume cases | 0 |
| Appointment Ready after Support | 12 |
| End-to-end confirmed appointments | 12 |
| Correct bad-fit identifications | 1 |
| Useful information capture | 3.0/5 |
| Retrieved Knowledge utilization | 3.0/5 |
| Commercial progression | 3.0/5 |
| Naturalness | 3.0/5 |
| Critical failure flags | 0 |

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
    "appointment_ready_ai_successes": 10,
    "appointment_ready_ai_success_rate": 1.0,
    "support_requests": 11,
    "support_resolution_rate": 0.727,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 12,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "missed_ready_buyers": 0,
    "commercial_progression": 3.0,
    "naturalness": 3.0,
    "support_result_utilization": 3.0,
    "critical_failures": 0
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

- None identified.

## Retrieved Knowledge not used

- None identified.

## Remaining Knowledge gaps

- None identified.

## Remaining sales weaknesses


## Critical failures

[]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
