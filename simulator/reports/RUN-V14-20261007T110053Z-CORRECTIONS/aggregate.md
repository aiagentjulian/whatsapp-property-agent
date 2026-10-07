# Simulator V1.4 Aggregate Diagnostic

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 2/3 convertible scenarios (0.667). The AI made 5 Human support requests; 5 were resolved from scenario fixtures and 5 were judged as successful AI resumption. 2 support-enabled scenarios reached appointment readiness. The Agent completed 2 appropriate appointment-ready handoffs, with 0 premature formal handoffs, 0 missed-ready buyers, and 1 end-to-end confirmed appointments. Support is an allowed capability and does not itself count as a sales handoff. Per-scenario weaknesses and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 3 | — |
| Appointment-ready AI successes | 2 | 0.667 |
| Successful appointment-ready handoffs | 2 | 0.667 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 1 | 0.333 |
| Support requests | 5 | — |
| Support completion rate | 5/5 | 1.0 |
| AI resume-success rate | 5/5 | 1.0 |
| Appointment Ready reached after support | 2 | — |
| Human operational completion after successful handoff | 1 | 0.5 |
| Bad-fit correctly identified | 0 | None of non-convertible |

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
    "appointment_ready_ai_successes": 2,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_handoffs": 2,
    "premature_handoffs": 0,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 1,
    "support_requests": 5,
    "support_completion_rate": 1.0,
    "support_result_utilization_score": 4.67,
    "duplicate_support_requests": 0,
    "failed_resume_cases": 0,
    "ai_resume_success_rate": 1.0
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 2,
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
    "appointment_ready_ai_successes": 2,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_ready_handoffs": 2,
    "premature_handoffs": 0,
    "confirmed_appointments": 1,
    "commercial_progression": 4.67,
    "naturalness": 4.33,
    "handoff_judgment": 5.0,
    "useful_information_capture": 4.33,
    "retrieved_knowledge_utilization": 4.33
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 4.33/5
- Readiness detection accuracy: 1.0
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.0
- Retrieval quality/utilization: 4.33/5
- Critical failures: 0
- Post-handoff AI reply violations: 0
- All scenarios completed: 3/3

## Average Judge scores

- customer_understanding: 5.0/5
- latest_message_responsiveness: 4.67/5
- qualification_discipline: 4.67/5
- selling_angle_relevance: 4.33/5
- objection_handling: 4.33/5
- unit_fit_judgment: 4.0/5
- buying_signal_detection: 5.0/5
- appointment_judgment: 5.0/5
- factual_accuracy: 4.67/5
- sales_naturalness: 4.33/5
- handoff_judgment: 5.0/5
- commercial_progression: 4.67/5
- appointment_readiness_detection: 5.0/5
- handoff_timing: 5.0/5
- handoff_reason_correctness: 5.0/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 5.0/5
- useful_information_capture: 4.33/5
- appointment_ready_progression: 4.67/5
- retrieved_knowledge_utilization: 4.33/5
- support_request_judgment: 5.0/5
- support_result_utilization: 4.67/5
- support_resume_quality: 5.0/5

## Retrieval misses

- PEA-004: The retrieved pricing.md is explicitly a base-price reference, not current effective pricing. The AI appropriately requested operational verification rather than treating the base price as current.
- PEA-010: Retrieved Knowledge did not verify current package validity or a live Saturday slot; the simulator support fixture supplied those operational facts.

## Retrieved Knowledge not used

- PEA-001: At turn 1, retrieved sales-package knowledge said to normally lead a simple price enquiry with the effective post-package entry point. The AI instead opened with the base-price figure and a calculated rebate estimate.

## Remaining Knowledge gaps

- PEA-001: No verified itemized list of other upfront costs was supplied.
- PEA-001: No specific available appointment slot was verified or held.
- PEA-001: A specific unit-level price and availability still require confirmation.
- PEA-004: No substantiated rental comparables, approved yield guidance, or appreciation forecast were available.
- PEA-004: No current remaining inventory was verified.
- PEA-004: The current Type A price basis in the support result is simulator-only evidence, not Pearlmont factual Knowledge or proof of a live pricing-system connection.
- PEA-004: Actual rental demand, competing supply, and exit prospects remain unestablished.
- PEA-010: The fixture did not verify the full package breakdown or terms, or an exact unit-specific price.
- PEA-010: The package price and Saturday slot are simulator-only evidence, not Pearlmont factual Knowledge or proof of a real live-system connection.

## Remaining sales weaknesses

- PEA-001: The opening price response led with the RM328k base figure and calculated an approximate RM302k amount, rather than leading with the retrieved current-package entry-price guidance and clearly separating base price from package price. The later support-backed response clarified the one-carpark reference.
- PEA-004: The AI could have made the investment comparison slightly more actionable by offering to compare the buyer's own completed-condo figures against Pearlmont's known costs, while clearly noting that Pearlmont rent evidence was unavailable. This was a minor opportunity, not a missed appointment signal.
- PEA-010: The brief resumption could have more explicitly tied viewing with the spouse to assessing the relevant unit/package options, though the direct scheduling question was appropriate for this high-intent buyer.

## Critical failures

[]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
