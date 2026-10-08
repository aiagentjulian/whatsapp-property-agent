# RUN-TARGETED-LUNA-PEA007-R2-20261008 Regression Findings

- Scenarios attempted/completed: 1/1
- Acceptance targets passed: 9/11
- Appointment-ready AI success: 0/0 (None)
- Support requests resolved: 1/1 (1.0)
- Support resume: 1/1 (1.0)
- Duplicate support attempts: 0
- One-way handoff violations: replies=0, returns=0, owner reversions=0, replays=0

## Key scenarios

### PEA-007
- Outcome: MANDATORY_OPERATIONAL_HANDOFF
- Support attempts / unique requests / resolved: 1 / 1 / 1
- Findings: It did not further define the buyer's acceptable evidence threshold or decision timeline before the explicit human-request handoff, although the buyer was clearly not ready for an appointment.

## Acceptance targets

{
  "appointment_ready_success_at_least_6_of_9": false,
  "premature_appointment_handoffs_zero": true,
  "missed_ready_buyers_zero": true,
  "duplicate_support_requests_at_most_one": true,
  "support_resume_at_least_80_percent": true,
  "support_result_only_relays_zero": true,
  "failed_resume_cases_zero": true,
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
    "appointment_ready_ai_successes": 0,
    "normal_sales_flow_convertible_scenarios": 0,
    "appointment_ready_ai_success_rate": null,
    "successful_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 1,
    "support_requests_resolved": 1,
    "support_completion_rate": 1.0,
    "support_resume_successes": 1,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 0,
    "duplicate_support_requests": 0,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0,
    "support_result_overstated": 0,
    "post_handoff_ai_reply_violations": 0,
    "human_to_ai_return_events": 0,
    "end_to_end_confirmed_appointments": 0,
    "critical_failure_count": 0,
    "average_judge_scores": {
      "customer_understanding": 5.0,
      "latest_message_responsiveness": 5.0,
      "qualification_discipline": 5.0,
      "selling_angle_relevance": 4.0,
      "objection_handling": 5.0,
      "unit_fit_judgment": 3.0,
      "buying_signal_detection": 4.0,
      "appointment_judgment": 5.0,
      "factual_accuracy": 5.0,
      "sales_naturalness": 4.0,
      "handoff_judgment": 5.0,
      "commercial_progression": 3.0,
      "appointment_readiness_detection": 5.0,
      "handoff_timing": 5.0,
      "handoff_reason_correctness": 5.0,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 5.0,
      "useful_information_capture": 5.0,
      "appointment_ready_progression": 3.0,
      "retrieved_knowledge_utilization": 5.0,
      "support_request_judgment": 5.0,
      "support_result_utilization": 5.0,
      "support_resume_quality": 5.0
    }
  },
  "comparison_note": "V1.5 duplicate attempts are reconstructed by counting REUSED_VERIFIED_RESULT records. V1.5 did not instrument Human-to-AI return events; V1.6 explicitly audits session, owner, and replay events."
}

## Judge averages

{
  "customer_understanding": 5.0,
  "latest_message_responsiveness": 5.0,
  "qualification_discipline": 5.0,
  "selling_angle_relevance": 4.0,
  "objection_handling": 5.0,
  "unit_fit_judgment": 3.0,
  "buying_signal_detection": 4.0,
  "appointment_judgment": 5.0,
  "factual_accuracy": 5.0,
  "sales_naturalness": 4.0,
  "handoff_judgment": 5.0,
  "commercial_progression": 3.0,
  "appointment_readiness_detection": 5.0,
  "handoff_timing": 5.0,
  "handoff_reason_correctness": 5.0,
  "post_handoff_suppression": 5.0,
  "conversion_attribution": 5.0,
  "useful_information_capture": 5.0,
  "appointment_ready_progression": 3.0,
  "retrieved_knowledge_utilization": 5.0,
  "support_request_judgment": 5.0,
  "support_result_utilization": 5.0,
  "support_resume_quality": 5.0
}

## Remaining Agent weaknesses

- PEA-007: It did not further define the buyer's acceptable evidence threshold or decision timeline before the explicit human-request handoff, although the buyer was clearly not ready for an appointment.
