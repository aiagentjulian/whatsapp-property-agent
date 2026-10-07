# Simulator V1.5 Aggregate Regression

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 6/9 convertible scenarios allowed to continue normal sales flow (0.667). It resumed successfully after 8/19 resolved support results and reached readiness after support in 5 scenarios. This shows useful capability but not full reliability: the run flagged 3 duplicate support request(s) and 0 overstated support result(s). The Agent completed 6 appropriate appointment handoffs, with 0 premature appointment handoffs, 0 missed-ready buyers, and 1 end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.

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
    "duplicate_support_requests": 3,
    "end_to_end_confirmed_appointments": 1,
    "critical_failure_count": 7,
    "support_result_overstated": 0,
    "support_result_only_relayed": 2,
    "failed_resume_cases": 1,
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
    }
  },
  "delta": {
    "appointment_ready_ai_successes": 0,
    "normal_sales_flow_convertible_scenarios": 0,
    "appointment_ready_ai_success_rate": 0.0,
    "successful_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 0,
    "premature_appointment_handoffs": 0,
    "missed_ready_buyers": 0,
    "support_requests": 8,
    "support_requests_resolved": 7,
    "support_completion_rate": -0.050000000000000044,
    "support_resume_successes": -3,
    "ai_resume_success_rate": -0.49600000000000005,
    "appointment_ready_after_support": 0,
    "duplicate_support_requests": 2,
    "end_to_end_confirmed_appointments": 0,
    "critical_failure_count": 4,
    "support_result_overstated": -1,
    "support_result_only_relayed": 2,
    "failed_resume_cases": 1
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
| Normal-flow convertible scenarios | 9 | — |
| Appointment-ready AI successes | 6 | 0.667 |
| Successful appointment-ready handoffs | 6 | 0.545 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 1 | 0.091 |
| Support requests | 20 | — |
| Support completion rate | 19/20 | 0.95 |
| AI resume-success rate | 8/19 | 0.421 |
| Appointment Ready reached after support | 5 | — |
| Human operational completion after successful handoff | 1 | 0.167 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 3,
  "DUPLICATE_SUPPORT_REQUEST": 3,
  "SUPPORT_RESULT_NOT_USED": 0,
  "SUPPORT_RESULT_ONLY_RELAYED": 2,
  "FAILED_TO_RESUME_SELLING": 1,
  "MISSED_READY_AFTER_SUPPORT": 0,
  "PREMATURE_APPOINTMENT_HANDOFF": 0,
  "FAILED_APPOINTMENT_HANDOFF": 0,
  "OVERQUALIFICATION_AFTER_SUPPORT": 0,
  "SUPPORT_RESULT_OVERSTATED": 0
}

## Average Judge scores

- customer_understanding: 4.5/5
- latest_message_responsiveness: 4.42/5
- qualification_discipline: 4.67/5
- selling_angle_relevance: 4.0/5
- objection_handling: 4.25/5
- unit_fit_judgment: 3.83/5
- buying_signal_detection: 4.58/5
- appointment_judgment: 4.67/5
- factual_accuracy: 4.67/5
- sales_naturalness: 3.83/5
- handoff_judgment: 4.92/5
- commercial_progression: 3.83/5
- appointment_readiness_detection: 4.83/5
- handoff_timing: 5.0/5
- handoff_reason_correctness: 4.92/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 5.0/5
- useful_information_capture: 4.08/5
- appointment_ready_progression: 4.0/5
- retrieved_knowledge_utilization: 4.25/5
- support_request_judgment: 3.92/5
- support_result_utilization: 4.08/5
- support_resume_quality: 3.92/5

## V1.4 metrics

| Metric | Value |
|---|---:|
| Appointment-ready AI success | 6/9 (0.667) |
| Successful appointment handoffs | 6 |
| Mandatory operational handoffs | 2 |
| Premature appointment handoffs | 0 |
| Missed-ready buyers | 0 |
| Support requests / resolved | 20 / 19 (0.95) |
| AI resume success | 8/19 (0.421) |
| Support result utilization | 4.08/5 |
| Duplicate support requests | 3 |
| Failed resume cases | 1 |
| Appointment Ready after Support | 5 |
| End-to-end confirmed appointments | 1 |
| Correct bad-fit identifications | 1 |
| Useful information capture | 4.08/5 |
| Retrieved Knowledge utilization | 4.25/5 |
| Commercial progression | 3.83/5 |
| Naturalness | 3.83/5 |
| Critical failure flags | 7 |

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
    "support_requests": 20,
    "support_resolution_rate": 0.95,
    "ai_resume_success_rate": 0.421,
    "appointment_ready_after_support": 5,
    "premature_appointment_handoffs": 0,
    "mandatory_operational_handoffs": 2,
    "missed_ready_buyers": 0,
    "commercial_progression": 3.83,
    "naturalness": 3.83,
    "support_result_utilization": 4.08,
    "critical_failures": 7
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

- PEA-003: The retrieved unit-and-layout source says exact unit-number-to-facing mapping requires the latest orientation schedule; no such schedule was retrieved. The support fixture supplied a scenario-specific answer instead.
- PEA-005: The retrieved LPPSA material covered published reference terms and cautioned against guaranteeing eligibility, but did not establish Pearlmont Phase 1 route acceptance or the project-side checklist. The AI correctly sought operational verification for those missing facts.
- PEA-007: {'missing_information': 'An actual shareable FAQ document or link, official flood records or independent assessment, and confirmed pylon distances for Blocks 1C and 1D were not present in the retrieved material or supplied by the support fixture.', 'source_target': 'MISSING_SOURCE'}
- PEA-008: Current unit-level availability and current package validity were not established by retrieved Knowledge or the support fixture.
- PEA-011: {'turn': 4, 'information': 'Specific facilities-deck amenities were not contained in the supplied retrieved source material.'}

## Retrieved Knowledge not used

- PEA-001: The retrieved current-package source cautions against treating a generic starting price as an exact current unit price. The AI did caveat that RM302k was not a confirmed 1-carpark Type A price, but did not obtain the requested unit-specific confirmation.
- PEA-001: No retrieved Knowledge source provided the requested monthly repayment figure. The AI offered its own clearly qualified illustration rather than representing it as a verified bank quote.
- PEA-003: {'source': 'knowledge/project/pearlmont/03_sales/unit-fit.md', 'evidence': 'The guide advises reducing generic qualification when buyers ask about specific floor/view/carpark combinations and moving toward a suitable category and viewing.'}
- PEA-003: {'source': 'knowledge/project/pearlmont/03_sales/viewing-close.md', 'evidence': 'The guide recommends connecting a viewing to the buyer’s unresolved decision point. The Agent did not articulate that connection.'}
- PEA-004: Retrieved overview.md identifies the FAQ source and states that it was updated 17 September 2026. At turn 9, the Agent said it could not confirm the date or document source instead of explaining this retrieved information and clarifying that it lacked a shareable copy or link.

## Remaining Knowledge gaps

- PEA-001: The requested one-carpark Type A price and 30-year payment estimate were not supplied by the support results returned to the AI.
- PEA-001: The requested shareable plan attachment or link was not provided in the customer-facing response.
- PEA-001: Specific open weekend slots could not be verified because the appointment calendar was not connected.
- PEA-002: Actual weekend slot availability could not be verified because the appointment calendar was NOT_CONNECTED. No specific slot was promised or confirmed.
- PEA-003: The human executor could not verify this week’s or weekend viewing slots; no slot was confirmed.
- PEA-003: The exact unit and package details came from a simulator-only support fixture, not retrieved Pearlmont Knowledge or a live production inventory connection.
- PEA-004: No verified rental comparables, substantiated yield, or appreciation forecast were available.
- PEA-004: No authoritative nearby competing-supply breakdown or catchment analysis was available.
- PEA-004: No verified customer-shareable FAQ copy or approved link was returned by the support trace.
- PEA-004: No unit-specific itemised quote or current remaining inventory was verified.
- PEA-005: Current unit categories and price schedule were not provided in the transcript.
- PEA-005: The buyer's individual LPPSA eligibility, personal document checklist, and approval remain for LPPSA to assess.
- PEA-006: Retrieved Knowledge does not establish that private corridors exist or verify crowding/noise levels.
- PEA-006: The support fixture provides a simulator-only possibility of viewing a representative shared corridor, subject to gallery access on the day; access for a specific date and current viewing slots were not verified.
- PEA-007: Actual FAQ document or link to share.
- PEA-007: Any official flood records or independent flood assessment.
- PEA-007: Confirmed pylon distances for Blocks 1C and 1D.
- PEA-007: The simulator fixture is limited synthetic evidence; it does not establish a real developer lookup or live operational connection.
- PEA-008: Current availability of unit 1C-12-03.
- PEA-008: Whether the RM349,000 package is currently valid.
- PEA-008: Exact view from the stack, which the agent appropriately said should be checked at a visit.
- PEA-009: The retrieved internal guidance does not establish who should own the next customer contact in this specific case. A human should resolve that operationally before any further outreach.
- PEA-010: No exact unit-category price breakdown was verified; no specific unit/category was selected.
- PEA-011: The specific facilities list was absent from retrieved Knowledge. The scenario fixture supplied an answer through the separate support channel, but it was not requested or used.

## Remaining sales weaknesses

- PEA-001: It issued six support requests in succession, repeatedly receiving the same layout result instead of resuming the conversation after the first response. Its eventual customer-facing answer did not provide the requested attachment, verified package price, or fixture-backed payment estimate.
- PEA-002: The Agent did not explore which furniture arrangement or room was most concerning. This was a minor opportunity, not a readiness blocker.
- PEA-003: After receiving the answer, the Agent mostly relayed it. It did not contextualize the match to the buyer’s priorities or continue selling with a buyer-centered viewing rationale before handoff.
- PEA-004: After the buyer raised the future FAQ date, the Agent said it could not confirm the document source or date despite retrieved Knowledge specifying the source and stated update date. More broadly, it supplied facts but did little to connect the price answer to the buyer’s investment comparison or test a useful next step.
- PEA-005: After the buyer explicitly requested a team member, the AI appropriately made a mandatory operational handoff rather than continuing sales. The conversation did not progress to unit selection or viewing intent before that transfer; this was not an appointment-readiness miss.
- PEA-006: The turn 2 response gives several access and lift details at once. They are relevant and supported, but could have been slightly more concise before checking whether the information addressed the buyer's concern.
- PEA-007: The second support request repeated the earlier request, and its result reused the same fixture without resolving the buyer’s remaining need for an actual document/link or additional block-specific evidence. The subsequent conversation became repetitive rather than establishing a useful next step for delivering verifiable material.
- PEA-008: It repeated availability support requests after the same fixture result had already been returned without answering availability, creating a redundant support loop. It also could have checked the large discrepancy between the buyer’s budget and the quoted package figure.
- PEA-009: No material AI error is evident. The unresolved next-contact question followed the handoff and requires an operational ownership disposition before further follow-up.
- PEA-010: The close was concise and effective, but could have tied the viewing more explicitly to comparing the buyer’s unit-category options. This is a minor opportunity, not a readiness or handoff failure.
- PEA-011: {'turn': 4, 'evidence': 'When asked what the facilities deck includes, the Agent disclosed its knowledge limit but did not request the available scenario support answer.'}
- PEA-012: No material weakness. The AI could optionally offer to help again if the buyer's requirements change, but a brief, respectful close was appropriate.

## Critical failures

[
  {
    "scenario_id": "PEA-001",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "Turns 5–9 repeatedly requested the same plan and additional pricing/payment information after the turn-4 request had already returned a resolved layout fixture. Each subsequent request reused that same result without performing another lookup.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-001",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-003",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "Following the resolved support request, the Agent relayed the result but did not contextualize it to the buyer’s needs or continue useful selling before the buyer supplied the viewing intent.",
    "turn": 2
  },
  {
    "scenario_id": "PEA-007",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "The turn 5 support request repeated unresolved items already included in the turn 2 request. The support trace says the same verified fixture was reused and no second lookup was performed.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-007",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-008",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "After the first availability request at turn 4, the agent repeated substantially the same availability request at turns 5, 7, and 8. The returned fixture explicitly did not confirm availability and was reused without a new lookup.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-008",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 4
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
