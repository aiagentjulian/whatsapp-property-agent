# Simulator V1.5 Aggregate Regression

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 10/10 convertible scenarios allowed to continue normal sales flow (1.0). It resumed successfully after 8/8 resolved support results and reached readiness after support in 12 scenarios. This shows useful capability but not full reliability: the run flagged 0 duplicate support request(s) and 0 overstated support result(s). The Agent completed 10 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 12 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

## V1.4 regression comparison

{
  "baseline_run": "RUN-V14-20261007T110053Z",
  "baseline_version": "1.4",
  "baseline_metrics": {
    "appointment_ready_ai_successes": 6,
    "normal_sales_flow_convertible_scenarios": 9,
    "appointment_ready_ai_success_rate": 0.667,
    "successful_appointment_handoffs": 6,
    "mandatory_operational_handoffs": 2,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 12,
    "support_requests_resolved": 12,
    "support_completion_rate": 1.0,
    "support_resume_successes": 11,
    "ai_resume_success_rate": 0.917,
    "appointment_ready_after_support": 5,
    "duplicate_support_requests": 1,
    "end_to_end_confirmed_appointments": 1,
    "critical_failure_count": 3,
    "support_result_overstated": 1,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0,
    "average_judge_scores": {
      "customer_understanding": 4.83,
      "latest_message_responsiveness": 4.58,
      "qualification_discipline": 4.67,
      "selling_angle_relevance": 4.17,
      "objection_handling": 4.58,
      "unit_fit_judgment": 4.08,
      "buying_signal_detection": 4.75,
      "appointment_judgment": 4.92,
      "factual_accuracy": 4.67,
      "sales_naturalness": 4.25,
      "handoff_judgment": 4.92,
      "commercial_progression": 4.08,
      "appointment_readiness_detection": 4.92,
      "handoff_timing": 4.92,
      "handoff_reason_correctness": 5.0,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 5.0,
      "useful_information_capture": 4.25,
      "appointment_ready_progression": 4.08,
      "retrieved_knowledge_utilization": 4.67,
      "support_request_judgment": 4.67,
      "support_result_utilization": 4.5,
      "support_resume_quality": 4.58
    }
  },
  "v1_5_metrics": {
    "appointment_ready_ai_successes": 10,
    "normal_sales_flow_convertible_scenarios": 10,
    "appointment_ready_ai_success_rate": 1.0,
    "successful_appointment_handoffs": 10,
    "mandatory_operational_handoffs": 1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 11,
    "support_requests_resolved": 8,
    "support_completion_rate": 0.727,
    "support_resume_successes": 8,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 12,
    "duplicate_support_requests": 0,
    "end_to_end_confirmed_appointments": 12,
    "critical_failure_count": 0,
    "support_result_overstated": 0,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0,
    "average_judge_scores": {
      "customer_understanding": 3.0,
      "latest_message_responsiveness": 3.0,
      "qualification_discipline": 3.0,
      "selling_angle_relevance": 3.0,
      "objection_handling": 3.0,
      "unit_fit_judgment": 3.0,
      "buying_signal_detection": 3.0,
      "appointment_judgment": 3.0,
      "factual_accuracy": 3.0,
      "sales_naturalness": 3.0,
      "handoff_judgment": 3.0,
      "commercial_progression": 3.0,
      "appointment_readiness_detection": 3.0,
      "handoff_timing": 3.0,
      "handoff_reason_correctness": 3.0,
      "post_handoff_suppression": 3.0,
      "conversion_attribution": 3.0,
      "useful_information_capture": 3.0,
      "appointment_ready_progression": 3.0,
      "retrieved_knowledge_utilization": 3.0,
      "support_request_judgment": 3.0,
      "support_result_utilization": 3.0,
      "support_resume_quality": 3.0
    }
  },
  "delta": {
    "appointment_ready_ai_successes": 4,
    "normal_sales_flow_convertible_scenarios": 1,
    "appointment_ready_ai_success_rate": 0.33299999999999996,
    "successful_appointment_handoffs": 4,
    "mandatory_operational_handoffs": -1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": -1,
    "support_requests_resolved": -4,
    "support_completion_rate": -0.273,
    "support_resume_successes": -3,
    "ai_resume_success_rate": 0.08299999999999996,
    "appointment_ready_after_support": 7,
    "duplicate_support_requests": -1,
    "end_to_end_confirmed_appointments": 11,
    "critical_failure_count": -3,
    "support_result_overstated": -1,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0
  },
  "comparison_note": "Same 12 scenarios and V1.4 Judge schema. Mandatory operational handoffs are excluded from V1.5's normal-flow success denominator. V1.5 additionally loads skills/request-human-support.md, which the V1.4 runner omitted."
}

## Agent source and runtime checks

{
  "git_commit": "2a7cd59637f0bd1d06e32155018dd1f6e21d49be",
  "files_loaded_into_sales_agent_prompt": {
    "brain/AGENT.md": "9951898b1e2d5c64eb9a3b22520369ac81381990334ac3a53ad6f6c7865f64ce",
    "brain/SALES_FLOW.md": "ebda14858bb13cf1081eed56ce7c1f37a667e42b29cfd7ee24094b0a6a0caabe",
    "brain/INTENT_MODEL.md": "dfe82d8238f0514d8952ded4ba8f1ea55640a9b1f141d71b404de773f50efa59",
    "brain/LEAD_PROFILE.md": "99acd28534ad5aabe36b1438a76305ed3f0b02197a24de54ed4ba88423d64947",
    "brain/RESPONSE_RULES.md": "92cc34b045f843be44d5fd42425c83f9d22a0fc3342b3f12407ad9478b8d60e4",
    "brain/HANDOFF_RULES.md": "edfce52688e4b6c0afd052becd7feb5f583d7ef430205e5aa669ee35fd439b79",
    "skills/decide-next-action.md": "565cd382e6d5ad9eec8cb866845cd22592344e19162c53d864ee2756d12e6b22",
    "skills/request-human-support.md": "b8180226c7bc701aff838a8871f9dcf0207c6c2b79eccc03cae1f6fb640fff49",
    "skills/retrieve-project-knowledge.md": "d3b4dc132b6b95fee0458b5ee980b7c51160d0295ee73475b475138bfb09184e",
    "skills/update-lead-profile.md": "cff8bba68025a4b27813f8136980fef5fdb496836ee04ff344f1616590e40d73",
    "skills/handoff-to-human.md": "61eb39c16b7017ce4c9230174035d449c4dcb386da07a9f8fd53f60066799ab9"
  }
}
{
  "support_keeps_ai_owner": true,
  "formal_handoff_switches_to_human_pauses_ai": true,
  "judge_fallback_scores_used": false,
  "judge_schema_validated_for_completed_scenarios": true
}
{
  "paths": [
    "brain",
    "skills",
    "knowledge/project/pearlmont"
  ],
  "sha256_before": "8fbfb254b636b63f0589ad4244eb771bad3115ff43122f25396501034252c4c4",
  "sha256_after": "8fbfb254b636b63f0589ad4244eb771bad3115ff43122f25396501034252c4c4",
  "unchanged": true
}

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Normal-flow convertible scenarios | 10 | — |
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
