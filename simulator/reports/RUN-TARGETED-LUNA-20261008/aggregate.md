# Simulator V1.6 Aggregate Regression

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 1/1 convertible scenarios allowed to continue normal sales flow (1.0). It resumed successfully after 3/3 resolved support results and reached readiness after support in 1 scenarios. This shows useful capability but not full reliability: the run flagged 1 duplicate support request(s) and 0 overstated support result(s). The Agent completed 1 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 0 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

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
    "appointment_ready_ai_successes": 1,
    "normal_sales_flow_convertible_scenarios": 1,
    "appointment_ready_ai_success_rate": 1.0,
    "successful_appointment_handoffs": 1,
    "mandatory_operational_handoffs": 1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 3,
    "support_requests_resolved": 3,
    "support_completion_rate": 1.0,
    "support_resume_successes": 3,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 1,
    "duplicate_support_requests": 1,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0,
    "support_result_overstated": 0,
    "post_handoff_ai_reply_violations": 0,
    "human_to_ai_return_events": 0,
    "end_to_end_confirmed_appointments": 0,
    "critical_failure_count": 2,
    "average_judge_scores": {
      "customer_understanding": 5.0,
      "latest_message_responsiveness": 5.0,
      "qualification_discipline": 5.0,
      "selling_angle_relevance": 4.0,
      "objection_handling": 5.0,
      "unit_fit_judgment": 3.5,
      "buying_signal_detection": 4.5,
      "appointment_judgment": 5.0,
      "factual_accuracy": 5.0,
      "sales_naturalness": 4.0,
      "handoff_judgment": 5.0,
      "commercial_progression": 4.0,
      "appointment_readiness_detection": 5.0,
      "handoff_timing": 5.0,
      "handoff_reason_correctness": 5.0,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 4.5,
      "useful_information_capture": 5.0,
      "appointment_ready_progression": 3.5,
      "retrieved_knowledge_utilization": 5.0,
      "support_request_judgment": 4.0,
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
    "brain/RESPONSE_RULES.md": "bc08e3950afaa7342d77f628bb13bb478a6c31376bdd9f6817dbe85263334455",
    "brain/HANDOFF_RULES.md": "189c20445bfa38cf2602b7c64c9c3d5286b99079ccd89bdde02f5250aaec0e3b",
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
  "sha256_before": "43693e395f5a1ca3a2017357587b12f8bc2306e697d24eb880f1f2553bd3e648",
  "sha256_after": "43693e395f5a1ca3a2017357587b12f8bc2306e697d24eb880f1f2553bd3e648",
  "unchanged": true
}

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Normal-flow convertible scenarios | 1 | — |
| Appointment-ready AI successes | 1 | 1.0 |
| Successful appointment-ready handoffs | 1 | 0.5 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Support requests | 3 | — |
| Support completion rate | 3/3 | 1.0 |
| AI resume-success rate | 3/3 | 1.0 |
| Appointment Ready reached after support | 1 | — |
| Human operational completion after successful handoff | 0 | 0.0 |
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
  "number_of_model_calls": 26,
  "logical_requests": 26,
  "calls_by_role": {
    "sales_agent": 12,
    "customer_simulator": 10,
    "human_handoff_executor": 2,
    "judge": 2
  },
  "retry_count": 0,
  "retries": [],
  "usage": {
    "input_tokens": 1003980,
    "output_tokens": 20078,
    "cached_tokens": 76544,
    "total_tokens": 1024058,
    "reported_call_count": 26,
    "total_model_call_count": 26,
    "complete_for_all_calls": true
  },
  "scenario_duration_seconds": 349.267,
  "run_duration_seconds": 349.283,
  "blocking_error": null
}
- customer_understanding: 5.0/5
- latest_message_responsiveness: 5.0/5
- qualification_discipline: 5.0/5
- selling_angle_relevance: 4.0/5
- objection_handling: 5.0/5
- unit_fit_judgment: 3.5/5
- buying_signal_detection: 4.5/5
- appointment_judgment: 5.0/5
- factual_accuracy: 5.0/5
- sales_naturalness: 4.0/5
- handoff_judgment: 5.0/5
- commercial_progression: 4.0/5
- appointment_readiness_detection: 5.0/5
- handoff_timing: 5.0/5
- handoff_reason_correctness: 5.0/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 4.5/5
- useful_information_capture: 5.0/5
- appointment_ready_progression: 3.5/5
- retrieved_knowledge_utilization: 5.0/5
- support_request_judgment: 4.0/5
- support_result_utilization: 5.0/5
- support_resume_quality: 5.0/5

## V1.6 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 1/1 (1.0) |
| Successful appointment handoffs | 1 |
| Mandatory operational handoffs | 1 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 3 / 3 (1.0) |
| AI resume success | 3/3 (1.0) |
| Support result utilization | 5.0/5 |
| Duplicate support requests | 1 |
| Failed resume cases | 0 |
| Appointment Ready after Support | 1 |
| End-to-end confirmed appointments | 0 |
| Correct bad-fit identifications | 0 |
| Useful information capture | 5.0/5 |
| Retrieved Knowledge utilization | 5.0/5 |
| Commercial progression | 4.0/5 |
| Naturalness | 4.0/5 |
| Critical failure flags | 2 |

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
    "appointment_ready_ai_successes": 1,
    "appointment_ready_ai_success_rate": 1.0,
    "support_requests": 3,
    "support_resolution_rate": 1.0,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 1,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "missed_ready_buyers": 0,
    "commercial_progression": 4.0,
    "naturalness": 4.0,
    "support_result_utilization": 5.0,
    "critical_failures": 2
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
    "appointment_ready_ai_successes": 1,
    "normal_sales_flow_convertible_scenarios": 1,
    "appointment_ready_ai_success_rate": 1.0,
    "successful_appointment_handoffs": 1,
    "mandatory_operational_handoffs": 1,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 3,
    "support_requests_resolved": 3,
    "support_completion_rate": 1.0,
    "support_resume_successes": 3,
    "ai_resume_success_rate": 1.0,
    "appointment_ready_after_support": 1,
    "duplicate_support_requests": 1,
    "support_result_only_relayed": 0,
    "failed_resume_cases": 0,
    "support_result_overstated": 0,
    "post_handoff_ai_reply_violations": 0,
    "human_to_ai_return_events": 0,
    "end_to_end_confirmed_appointments": 0,
    "critical_failure_count": 2,
    "average_judge_scores": {
      "customer_understanding": 5.0,
      "latest_message_responsiveness": 5.0,
      "qualification_discipline": 5.0,
      "selling_angle_relevance": 4.0,
      "objection_handling": 5.0,
      "unit_fit_judgment": 3.5,
      "buying_signal_detection": 4.5,
      "appointment_judgment": 5.0,
      "factual_accuracy": 5.0,
      "sales_naturalness": 4.0,
      "handoff_judgment": 5.0,
      "commercial_progression": 4.0,
      "appointment_readiness_detection": 5.0,
      "handoff_timing": 5.0,
      "handoff_reason_correctness": 5.0,
      "post_handoff_suppression": 5.0,
      "conversion_attribution": 4.5,
      "useful_information_capture": 5.0,
      "appointment_ready_progression": 3.5,
      "retrieved_knowledge_utilization": 5.0,
      "support_request_judgment": 4.0,
      "support_result_utilization": 5.0,
      "support_resume_quality": 5.0
    }
  },
  "comparison_note": "V1.5 duplicate attempts are reconstructed by counting REUSED_VERIFIED_RESULT records. V1.5 did not instrument Human-to-AI return events; V1.6 explicitly audits session, owner, and replay events."
}

## Retrieval misses

- PEA-007: The actual site plan, independent engineering opinion, official flood-history certification, and JPS documents were unavailable in the retrieved and simulator materials.

## Retrieved Knowledge not used

- None identified.

## Remaining Knowledge gaps

- PEA-004: Rental comparables and actual rental evidence.
- PEA-004: Substantiated yield or appreciation data.
- PEA-004: Phase-wise supply and current remaining inventory.
- PEA-004: Verified viewing availability.
- PEA-007: Actual Block 1B/tower site plan.
- PEA-007: Independent engineering assessment.
- PEA-007: Official block-specific flood-history or JPS documentation.
- PEA-007: Verified residual-risk conclusions and any formal guarantees.

## Remaining sales weaknesses

- PEA-004: It issued a duplicate support request after the investment result had already been resolved, although it correctly reused the result afterward.
- PEA-007: It did not add a concise next-step framing for how the buyer could reassess suitability after receiving the requested documents, although the explicit human request justified the mandatory transfer.

## Critical failures

[
  {
    "scenario_id": "PEA-004",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "The turn 6 support request repeated the already resolved investment request and was marked REUSE_RESOLVED.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-004",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 6
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic simulator data, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: False
