# Simulator V1.6 Aggregate Regression

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 2/3 convertible scenarios allowed to continue normal sales flow (0.667). It resumed successfully after 3/8 resolved support results and reached readiness after support in 1 scenarios. This shows useful capability but not full reliability: the run flagged 0 duplicate support request(s) and 0 overstated support result(s). The Agent completed 2 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 0 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

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

## Agent source and runtime checks

{
  "git_commit": "e25a8acc0341a01b1c04bfa4062bd10533d3014d",
  "files_loaded_into_sales_agent_prompt": {
    "brain/AGENT.md": "9951898b1e2d5c64eb9a3b22520369ac81381990334ac3a53ad6f6c7865f64ce",
    "brain/SALES_FLOW.md": "ebda14858bb13cf1081eed56ce7c1f37a667e42b29cfd7ee24094b0a6a0caabe",
    "brain/INTENT_MODEL.md": "dfe82d8238f0514d8952ded4ba8f1ea55640a9b1f141d71b404de773f50efa59",
    "brain/LEAD_PROFILE.md": "99acd28534ad5aabe36b1438a76305ed3f0b02197a24de54ed4ba88423d64947",
    "brain/RESPONSE_RULES.md": "92cc34b045f843be44d5fd42425c83f9d22a0fc3342b3f12407ad9478b8d60e4",
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
  "sha256_before": "b9c63b1074bdd73f7b84f0ac1c8bc359a457252a8d0fd20d0a079d95ded25832",
  "sha256_after": "b9c63b1074bdd73f7b84f0ac1c8bc359a457252a8d0fd20d0a079d95ded25832",
  "unchanged": true
}

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Normal-flow convertible scenarios | 3 | — |
| Appointment-ready AI successes | 2 | 0.667 |
| Successful appointment-ready handoffs | 2 | 0.5 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Support requests | 8 | — |
| Support completion rate | 8/8 | 1.0 |
| AI resume-success rate | 3/8 | 0.375 |
| Appointment Ready reached after support | 1 | — |
| Human operational completion after successful handoff | 0 | 0.0 |
| Bad-fit correctly identified | 0 | None of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 0,
  "DUPLICATE_SUPPORT_REQUEST": 0,
  "SUPPORT_RESULT_NOT_USED": 0,
  "SUPPORT_RESULT_ONLY_RELAYED": 2,
  "FAILED_TO_RESUME_SELLING": 2,
  "MISSED_READY_AFTER_SUPPORT": 0,
  "PREMATURE_APPOINTMENT_HANDOFF": 0,
  "FAILED_APPOINTMENT_HANDOFF": 0,
  "OVERQUALIFICATION_AFTER_SUPPORT": 0,
  "SUPPORT_RESULT_OVERSTATED": 0
}

## Average Judge scores

- customer_understanding: 4.25/5
- latest_message_responsiveness: 4.25/5
- qualification_discipline: 4.25/5
- selling_angle_relevance: 3.75/5
- objection_handling: 4.0/5
- unit_fit_judgment: 3.75/5
- buying_signal_detection: 4.25/5
- appointment_judgment: 4.75/5
- factual_accuracy: 4.25/5
- sales_naturalness: 3.75/5
- handoff_judgment: 4.75/5
- commercial_progression: 3.25/5
- appointment_readiness_detection: 4.5/5
- handoff_timing: 4.75/5
- handoff_reason_correctness: 5.0/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 4.75/5
- useful_information_capture: 4.0/5
- appointment_ready_progression: 3.5/5
- retrieved_knowledge_utilization: 4.25/5
- support_request_judgment: 4.25/5
- support_result_utilization: 3.5/5
- support_resume_quality: 3.25/5

## V1.6 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 2/3 (0.667) |
| Successful appointment handoffs | 2 |
| Mandatory operational handoffs | 1 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 8 / 8 (1.0) |
| AI resume success | 3/8 (0.375) |
| Support result utilization | 3.5/5 |
| Duplicate support requests | 0 |
| Failed resume cases | 2 |
| Appointment Ready after Support | 1 |
| End-to-end confirmed appointments | 0 |
| Correct bad-fit identifications | 0 |
| Useful information capture | 4.0/5 |
| Retrieved Knowledge utilization | 4.25/5 |
| Commercial progression | 3.25/5 |
| Naturalness | 3.75/5 |
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
    "appointment_ready_ai_successes": 2,
    "appointment_ready_ai_success_rate": 0.667,
    "support_requests": 8,
    "support_resolution_rate": 1.0,
    "ai_resume_success_rate": 0.375,
    "appointment_ready_after_support": 1,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 1,
    "missed_ready_buyers": 0,
    "commercial_progression": 3.25,
    "naturalness": 3.75,
    "support_result_utilization": 3.5,
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
  "support_resume_at_least_80_percent": false,
  "support_result_only_relays_zero": false,
  "failed_resume_cases_zero": false,
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

## Retrieval misses

- PEA-004: No retrieved source supplied dated rental comparables, achieved-versus-asking rent distinctions, or vacancy evidence.
- PEA-004: No shareable links or copies for the cited package and FAQ documents were available in the supplied material.

## Retrieved Knowledge not used

- PEA-001: {'source': 'knowledge/project/pearlmont/02_commercial/sales-package.md', 'evidence': 'The source says normal opening price questions should usually lead with the current effective post-package from-price or range. Turn 1 instead led with RM328,000 base pricing.'}
- PEA-001: {'source': 'knowledge/project/pearlmont/02_commercial/pricing.md', 'evidence': 'The source documents SPA pricing components and cautions against applying unspecified premiums. The Agent did not use these documented components to explain what is known about price structure, though it correctly declined to invent an upfront-cash total.'}

## Remaining Knowledge gaps

- PEA-001: A verified itemised upfront-cost or upfront-cash breakdown for the RM302,000 reference was not supplied.
- PEA-001: No specific viewing slot was verified or held; the human response reported only simulator fixture weekend viewing hours subject to gallery confirmation.
- PEA-002: Viewing availability could not be verified because the calendar was not connected in this run.
- PEA-003: The retrieved unit-and-layout material gives general block/floor facing information and explicitly requires the latest orientation schedule for exact unit-number mapping. No such plan or schedule was supplied.
- PEA-003: The support fixture did not answer the requested plan-mapping question; it repeated the simulator-confirmed Type A Sea View, unit, carpark, availability, and package information.
- PEA-004: Dated, sourced nearby rental comparables and vacancy evidence: MISSING_SOURCE.
- PEA-004: Shareable source documents or links for the package and Phase 1 unit count: MISSING_SOURCE.

## Remaining sales weaknesses

- PEA-001: Opened with the RM328,000 base-price reference rather than the retrieved sales-package guidance to lead with the current effective from-price hook. It also could have connected the joint decision-maker to the viewing plan.
- PEA-002: After the buyer described the sofa/table circulation concern and supplied the 4-seater detail, the Agent asked for sofa length rather than immediately offering the relevant show-unit check. This was a minor delay; it progressed to a viewing invitation on the next turn.
- PEA-003: After support returned no actual orientation-plan verification, the AI repeatedly restated the same Type A Sea View/two-carpark record and told the buyer to wait, rather than efficiently setting up the human verification the buyer requested. It made another support request after the explicit human request at turn 7.
- PEA-004: After the first support result, turn 3 produced an empty AI message rather than a customer-facing response. Later replies repeated the package figure but did not resolve the rental-evidence blocker or progress the investment discussion.

## Critical failures

[
  {
    "scenario_id": "PEA-003",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After support request 2 resolved, the turn 5 response restated the Type A Sea View/two-carpark record and deferred arranging anything. Turns 6–7 repeated the same limitation without a useful progression toward the buyer’s requested verification or a clear next step.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-004",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After support request PEA-004-SUP-001 resolved at turn 2, the turn 3 Agent action was ACKNOWLEDGE / MAINTAIN with an empty message. No customer-facing response resumed the saved investment-assessment objective at that point.",
    "turn": 3
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
