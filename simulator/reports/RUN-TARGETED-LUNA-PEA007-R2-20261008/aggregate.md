# Simulator V1.6 Aggregate Regression

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 0/0 convertible scenarios allowed to continue normal sales flow (None). It resumed successfully after 1/1 resolved support results and reached readiness after support in 0 scenarios. This shows useful capability but not full reliability: the run flagged 0 duplicate support request(s) and 0 overstated support result(s). The Agent completed 0 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 0 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

## V1.5 regression comparison

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

## Agent source and runtime checks

{
  "git_commit": "baa7915760219a32b7a35a7b41beedcd4c2067d2",
  "files_loaded_into_sales_agent_prompt": {
    "brain/AGENT.md": "9951898b1e2d5c64eb9a3b22520369ac81381990334ac3a53ad6f6c7865f64ce",
    "brain/SALES_FLOW.md": "ebda14858bb13cf1081eed56ce7c1f37a667e42b29cfd7ee24094b0a6a0caabe",
    "brain/INTENT_MODEL.md": "dfe82d8238f0514d8952ded4ba8f1ea55640a9b1f141d71b404de773f50efa59",
    "brain/LEAD_PROFILE.md": "99acd28534ad5aabe36b1438a76305ed3f0b02197a24de54ed4ba88423d64947",
    "brain/RESPONSE_RULES.md": "92cc34b045f843be44d5fd42425c83f9d22a0fc3342b3f12407ad9478b8d60e4",
    "brain/HANDOFF_RULES.md": "917ef832e65e2ee47f16ed23e54b67020b0e5c8c977b91f291b5284393a753d2",
    "brain/SUPPORT_LIFECYCLE.md": "ca9f49be2e953499b167d919305804567fca7d2a4c43a16b3d5481133b6d4fdc",
    "skills/decide-next-action.md": "5aa74892ddff784dd98e58c35ee85503ab973ba0eb9621a9abfd6cfd3309a8b2",
    "skills/request-human-support.md": "94fef07c3da89a3c05dbcadf1d1d29d6aaf101a4110c2ed3044a8b8127f7e970",
    "skills/handoff-to-human.md": "223b739f19fefff2e4acdc462a3fd920527e7a1676b0edc3fb456a290514cd80",
    "skills/retrieve-project-knowledge.md": "d3b4dc132b6b95fee0458b5ee980b7c51160d0295ee73475b475138bfb09184e",
    "skills/update-lead-profile.md": "cff8bba68025a4b27813f8136980fef5fdb496836ee04ff344f1616590e40d73"
  }
}
{
  "support_keeps_ai_owner": true,
  "formal_handoff_switches_to_human_and_ends_ai_session": true,
  "support_attempts_reuse_equivalent_requests": true,
  "support_resume_context_preserved": true,
  "formal_handoff_one_way_clean": true,
  "judge_fallback_scores_used": false,
  "judge_schema_validated_for_completed_scenarios": true
}
{
  "paths": [
    "brain",
    "skills",
    "knowledge/project/pearlmont"
  ],
  "sha256_before": "56633eccedeed296bc990863843116ea31a662f272b8a232a06b229a3c7ecc9a",
  "sha256_after": "56633eccedeed296bc990863843116ea31a662f272b8a232a06b229a3c7ecc9a",
  "unchanged": true
}

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Normal-flow convertible scenarios | 0 | — |
| Appointment-ready AI successes | 0 | None |
| Successful appointment-ready handoffs | 0 | 0.0 |
| Premature appointment handoffs | 0 | None of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Support requests | 1 | — |
| Support completion rate | 1/1 | 1.0 |
| AI resume-success rate | 1/1 | 1.0 |
| Appointment Ready reached after support | 0 | — |
| Human operational completion after successful handoff | 0 | None |
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

## Average Judge scores


## Provider and usage accounting

{
  "provider": "codex_cli",
  "model_config": {
    "sales_agent": {
      "model": "gpt-5.6-luna",
      "reasoning": "medium"
    },
    "customer_simulator": {
      "model": "gpt-5.6-luna",
      "reasoning": "medium"
    },
    "judge": {
      "model": "gpt-5.6-luna",
      "reasoning": "medium"
    },
    "human_handoff_executor": {
      "model": "gpt-5.6-luna",
      "reasoning": "medium"
    }
  },
  "number_of_model_calls": 10,
  "logical_requests": 10,
  "calls_by_role": {
    "sales_agent": 4,
    "customer_simulator": 4,
    "human_handoff_executor": 1,
    "judge": 1
  },
  "retry_count": 0,
  "retries": [],
  "usage": {
    "input_tokens": 367105,
    "output_tokens": 7158,
    "cached_tokens": 33280,
    "total_tokens": 374263,
    "reported_call_count": 10,
    "total_model_call_count": 10,
    "complete_for_all_calls": true
  },
  "scenario_duration_seconds": 132.184,
  "run_duration_seconds": 132.187,
  "blocking_error": null
}
- customer_understanding: 5.0/5
- latest_message_responsiveness: 5.0/5
- qualification_discipline: 5.0/5
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
- useful_information_capture: 5.0/5
- appointment_ready_progression: 3.0/5
- retrieved_knowledge_utilization: 5.0/5
- support_request_judgment: 5.0/5
- support_result_utilization: 5.0/5
- support_resume_quality: 5.0/5

## V1.6 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 0/0 (None) |
| Successful appointment handoffs | 0 |
| Mandatory operational handoffs | 1 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 1 / 1 (1.0) |
| AI resume success | 1/1 (1.0) |
| Support result utilization | 5.0/5 |
| Duplicate support requests | 0 |
| Failed resume cases | 0 |
| Appointment Ready after Support | 0 |
| End-to-end confirmed appointments | 0 |
| Correct bad-fit identifications | 0 |
| Useful information capture | 5.0/5 |
| Retrieved Knowledge utilization | 5.0/5 |
| Commercial progression | 3.0/5 |
| Naturalness | 4.0/5 |
| Critical failure flags | 0 |

## Earlier-version comparison

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
    "appointment_ready_ai_successes": 0,
    "appointment_ready_ai_success_rate": null,
    "support_requests": 1,
    "support_resolution_rate": 1.0,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 0,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "missed_ready_buyers": 0,
    "commercial_progression": 3.0,
    "naturalness": 4.0,
    "support_result_utilization": 5.0,
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

## V1.6 acceptance targets

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

## V1.5 direct comparison

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

## Retrieval misses

- PEA-007: A direct official flood assessment or block-specific authority flood-history record was not available in the retrieved material.
- PEA-007: The exact FAQ/site-plan document requested by the buyer was not directly supplied.

## Retrieved Knowledge not used

- None identified.

## Remaining Knowledge gaps

- PEA-007: Independent engineering opinion remains unavailable.
- PEA-007: Official block-specific flood-history certification remains unavailable.
- PEA-007: The exact individual house/unit finished-floor level remains unconfirmed.
- PEA-007: A customer-facing copy of the FAQ/site plan was not directly provided.

## Remaining sales weaknesses

- PEA-007: It did not further define the buyer's acceptable evidence threshold or decision timeline before the explicit human-request handoff, although the buyer was clearly not ready for an appointment.

## Critical failures

[]

## Fixture and integrity notes

Human support and operational facts are synthetic simulator data, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: False
