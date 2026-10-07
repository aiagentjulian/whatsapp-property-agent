# RUN-V16-20261007T155329Z Regression Findings

- Scenarios attempted/completed: 12/4
- Acceptance targets passed: 6/11
- Appointment-ready AI success: 2/3 (0.667)
- Support requests resolved: 8/8 (1.0)
- Support resume: 3/8 (0.375)
- Duplicate support attempts: 21
- One-way handoff violations: replies=0, returns=0, owner reversions=0, replays=0

## Key scenarios

### PEA-001
- Outcome: AI_APPOINTMENT_HANDOFF_SUCCESS
- Support attempts / unique requests / resolved: 2 / 2 / 2
- Findings: Opened with the RM328,000 base-price reference rather than the retrieved sales-package guidance to lead with the current effective from-price hook. It also could have connected the joint decision-maker to the viewing plan.

### PEA-003
- Outcome: MANDATORY_OPERATIONAL_HANDOFF
- Support attempts / unique requests / resolved: 3 / 3 / 3
- Findings: After support returned no actual orientation-plan verification, the AI repeatedly restated the same Type A Sea View/two-carpark record and told the buyer to wait, rather than efficiently setting up the human verification the buyer requested. It made another support request after the explicit human request at turn 7.

### PEA-007
- Outcome: RUN_FAILED
- Support attempts / unique requests / resolved: 0 / 0 / 0
- Findings: No specific weakness recorded.

### PEA-008
- Outcome: RUN_FAILED
- Support attempts / unique requests / resolved: 0 / 0 / 0
- Findings: No specific weakness recorded.

### PEA-011
- Outcome: RUN_FAILED
- Support attempts / unique requests / resolved: 0 / 0 / 0
- Findings: No specific weakness recorded.

## Acceptance targets

{
  "appointment_ready_success_at_least_6_of_9": false,
  "premature_appointment_handoffs_zero": true,
  "missed_ready_buyers_zero": true,
  "duplicate_support_requests_at_most_one": true,
  "support_resume_at_least_80_percent": false,
  "support_result_only_relays_zero": false,
  "failed_resume_cases_zero": false,
  "support_overstatements_zero": true,
  "post_handoff_ai_replies_zero": true,
  "human_to_ai_returns_zero": true,
  "mandatory_handoff_behavior_unchanged": false
}

Acceptance pass: False

## V1.5 comparison

{
  "baseline_run": "RUN-V15-20261007T120820Z",
  "baseline": {
    "appointment_ready_ai_successes": 6,
    "normal_sales_flow_convertible_scenarios": 9,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_handoffs": 6,
    "mandatory_operational_handoffs": 2,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 20,
    "support_requests_resolved": 19,
    "support_completion_rate": 0.95,
    "support_resume_successes": 8,
    "ai_resume_success_rate": 0.421,
    "appointment_ready_after_support": 5,
    "support_result_only_relayed": null,
    "failed_resume_cases": 1,
    "end_to_end_confirmed_appointments": 1,
    "critical_failure_count": 7,
    "average_judge_scores": {
      "customer_understanding": 4.5,
      "latest_message_responsiveness": 4.42,
      "qualification_discipline": 4.67,
      "selling_angle_relevance": 4.0,
      "objection_handling": 4.25,
      "unit_fit_judgment": 3.83,
      "buying_signal_detection": 4.58,
      "appointment_judgment": 4.67,
      "factual_accuracy": 4.67,
      "sales_naturalness": 3.83,
      "handoff_judgment": 4.92,
      "commercial_progression": 3.83,
      "appointment_readiness_detection": 4.83,
      "handoff_timing": 5.0,
      "handoff_reason_correctness": 4.92,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 5.0,
      "useful_information_capture": 4.08,
      "appointment_ready_progression": 4.0,
      "retrieved_knowledge_utilization": 4.25,
      "support_request_judgment": 3.92,
      "support_result_utilization": 4.08,
      "support_resume_quality": 3.92
    },
    "duplicate_support_requests_attempts_derived_from_reused_results": 10,
    "support_result_overstated": 0,
    "post_handoff_ai_replies": 0,
    "human_to_ai_returns": "not instrumented in V1.5; AI was represented as PAUSED"
  },
  "v1_6": {
    "appointment_ready_ai_successes": 2,
    "normal_sales_flow_convertible_scenarios": 3,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_handoffs": 2,
    "mandatory_operational_handoffs": 1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 8,
    "support_requests_resolved": 8,
    "support_completion_rate": 1.0,
    "support_resume_successes": 3,
    "ai_resume_success_rate": 0.375,
    "appointment_ready_after_support": 1,
    "duplicate_support_requests": 0,
    "support_result_only_relayed": 2,
    "failed_resume_cases": 2,
    "support_result_overstated": 0,
    "post_handoff_ai_reply_violations": 0,
    "human_to_ai_return_events": 0,
    "end_to_end_confirmed_appointments": 0,
    "critical_failure_count": 2,
    "average_judge_scores": {
      "customer_understanding": 4.25,
      "latest_message_responsiveness": 4.25,
      "qualification_discipline": 4.25,
      "selling_angle_relevance": 3.75,
      "objection_handling": 4.0,
      "unit_fit_judgment": 3.75,
      "buying_signal_detection": 4.25,
      "appointment_judgment": 4.75,
      "factual_accuracy": 4.25,
      "sales_naturalness": 3.75,
      "handoff_judgment": 4.75,
      "commercial_progression": 3.25,
      "appointment_readiness_detection": 4.5,
      "handoff_timing": 4.75,
      "handoff_reason_correctness": 5.0,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 4.75,
      "useful_information_capture": 4.0,
      "appointment_ready_progression": 3.5,
      "retrieved_knowledge_utilization": 4.25,
      "support_request_judgment": 4.25,
      "support_result_utilization": 3.5,
      "support_resume_quality": 3.25
    }
  },
  "comparison_note": "V1.5 duplicate attempts are reconstructed by counting REUSED_VERIFIED_RESULT records. V1.5 did not instrument Human-to-AI return events; V1.6 explicitly audits session, owner, and replay events."
}

## Judge averages

{
  "customer_understanding": 4.25,
  "latest_message_responsiveness": 4.25,
  "qualification_discipline": 4.25,
  "selling_angle_relevance": 3.75,
  "objection_handling": 4.0,
  "unit_fit_judgment": 3.75,
  "buying_signal_detection": 4.25,
  "appointment_judgment": 4.75,
  "factual_accuracy": 4.25,
  "sales_naturalness": 3.75,
  "handoff_judgment": 4.75,
  "commercial_progression": 3.25,
  "appointment_readiness_detection": 4.5,
  "handoff_timing": 4.75,
  "handoff_reason_correctness": 5.0,
  "post_handoff_suppression": 5.0,
  "conversion_attribution": 4.75,
  "useful_information_capture": 4.0,
  "appointment_ready_progression": 3.5,
  "retrieved_knowledge_utilization": 4.25,
  "support_request_judgment": 4.25,
  "support_result_utilization": 3.5,
  "support_resume_quality": 3.25
}

## Remaining Agent weaknesses

- PEA-001: Opened with the RM328,000 base-price reference rather than the retrieved sales-package guidance to lead with the current effective from-price hook. It also could have connected the joint decision-maker to the viewing plan.
- PEA-002: After the buyer described the sofa/table circulation concern and supplied the 4-seater detail, the Agent asked for sofa length rather than immediately offering the relevant show-unit check. This was a minor delay; it progressed to a viewing invitation on the next turn.
- PEA-003: After support returned no actual orientation-plan verification, the AI repeatedly restated the same Type A Sea View/two-carpark record and told the buyer to wait, rather than efficiently setting up the human verification the buyer requested. It made another support request after the explicit human request at turn 7.
- PEA-004: After the first support result, turn 3 produced an empty AI message rather than a customer-facing response. Later replies repeated the package figure but did not resolve the rental-evidence blocker or progress the investment discussion.
