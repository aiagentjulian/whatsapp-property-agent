# Simulator V1.3 Aggregate Diagnostic

**Executive summary:** Appointment-ready AI success was 6/11 convertible scenarios (0.545). The AI made 14 Human support requests; 6 were resolved from scenario fixtures and 5 were judged as successful AI resumption. 4 support-enabled scenarios reached appointment readiness. The Agent completed 6 appropriate appointment-ready handoffs, with 1 premature formal handoffs, 0 missed-ready buyers, and 1 end-to-end confirmed appointments. Support is an allowed capability and does not itself count as a sales handoff. Per-scenario weaknesses and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 6 | 0.545 |
| Successful appointment-ready handoffs | 6 | 0.545 |
| Premature appointment handoffs | 1 | 0.143 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 1 | 0.091 |
| Support requests | 14 | — |
| Support completion rate | 6/14 | 0.429 |
| AI resume-success rate | 5/6 | 0.833 |
| Appointment Ready reached after support | 4 | — |
| Human operational completion after successful handoff | 1 | 0.167 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 1,
  "SUPPORT_RESULT_NOT_USED": 0,
  "SUPPORT_RESULT_ONLY_RELAYED": 1,
  "FAILED_TO_RESUME_SELLING": 1,
  "MISSED_READY_AFTER_SUPPORT": 0,
  "PREMATURE_APPOINTMENT_HANDOFF": 1,
  "FAILED_APPOINTMENT_HANDOFF": 0,
  "OVERQUALIFICATION_AFTER_SUPPORT": 0
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
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.545,
    "successful_appointment_handoffs": 6,
    "premature_handoffs": 1,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 1,
    "support_requests": 14,
    "support_completion_rate": 0.429,
    "ai_resume_success_rate": 0.833
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 6,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 4,
  "AI_EARLY_HANDOFF": 1,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
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
    "appointment_ready_ai_successes": 6,
    "appointment_ready_ai_success_rate": 0.545,
    "successful_appointment_ready_handoffs": 6,
    "premature_handoffs": 1,
    "confirmed_appointments": 1,
    "commercial_progression": 3.0,
    "naturalness": 3.0,
    "handoff_judgment": 3.5,
    "useful_information_capture": 3.0,
    "retrieved_knowledge_utilization": 3.0
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 3.0/5
- Readiness detection accuracy: 1.0
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.14
- Retrieval quality/utilization: 3.0/5
- Critical failures: 8
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 3.0/5
- latest_message_responsiveness: 3.0/5
- qualification_discipline: 3.0/5
- selling_angle_relevance: 3.0/5
- objection_handling: 3.75/5
- unit_fit_judgment: 3.0/5
- buying_signal_detection: 3.0/5
- appointment_judgment: 3.0/5
- factual_accuracy: 3.83/5
- sales_naturalness: 3.0/5
- handoff_judgment: 3.5/5
- commercial_progression: 3.0/5
- appointment_readiness_detection: 3.0/5
- handoff_timing: 3.83/5
- handoff_reason_correctness: 3.0/5
- post_handoff_suppression: 3.0/5
- conversion_attribution: 3.0/5
- useful_information_capture: 3.0/5
- appointment_ready_progression: 3.0/5
- retrieved_knowledge_utilization: 3.0/5
- support_request_judgment: 4.67/5
- support_result_utilization: 4.42/5
- support_resume_quality: 4.17/5

## Retrieval misses

- PEA-005: No retrieved source or supplied fixture verified the current Pearlmont-side LPPSA process, required documents, or whether a specialist could follow up.
- PEA-007: The retrieved Knowledge did not provide the requested full block-specific site plan, independent flood assessment, or official flood-history information.
- PEA-011: The retrieved materials did not provide which Super Clubhouse facilities are included or how charges are applied. The support fixture supplied no verified answer.

## Retrieved Knowledge not used

- PEA-001: The sales-package source guidance says a light price enquiry should normally lead with a supportable post-package entry price or range. The agent instead led with the base price.
- PEA-010: The retrieved sales-package material explains that package applicability depends on unit category, floor band, and car-park allocation. The AI did not share that context, though it appropriately avoided presenting the dated package as verified current pricing.

## Remaining Knowledge gaps

- PEA-001: Current package validity and applicability to a specific unit were not verified.
- PEA-001: Viewing availability was NOT_CONNECTED in the fixture; no slot was confirmed and no appointment was booked.
- PEA-001: The buyers’ bank eligibility and actual instalment remain unknown.
- PEA-002: Specific viewing availability and whether the children can be accommodated could not be verified because the appointment calendar was not connected.
- PEA-003: Actual viewing slots were unavailable in the scenario; the human executor could not complete this operational task.
- PEA-003: The fixture provides a verified-in-simulation inventory snapshot, not live-world verification.
- PEA-004: No verified rental comparables or substantiated rental yield.
- PEA-004: No verified appreciation forecast.
- PEA-004: No current asking price or package for a 900 sq.ft. unit.
- PEA-004: No verification that RM0.18/sq.ft. is from the latest official fee schedule or confirmation of its current applicability.
- PEA-004: No verified figures for other recurring ownership costs.
- PEA-005: Current LPPSA rates and limits: retrieved reference is dated 4 October 2026 and was appropriately not represented as current before confirmation.
- PEA-005: Current Pearlmont-side LPPSA application process and document checklist.
- PEA-005: Whether a Pearlmont LPPSA specialist can contact or follow up with the buyer.
- PEA-006: The supplied Knowledge did not establish whether each tower has a separate entrance or whether shared facilities are tower-specific.
- PEA-006: Actual lift wait times, crowding levels, and noise levels were not verified.
- PEA-006: The operational fixture did not provide a weekend viewing slot, so no appointment time was confirmed.
- PEA-007: Block-specific high-tension cable distances beyond the retrieved Block 1B figure.
- PEA-007: Whether the requested full site plan and independent or official flood information exist or can be shared.
- PEA-007: Any independent technical assessment or official flood-history evidence.
- PEA-008: Whether RM349,000 is the full amount payable.
- PEA-008: Whether the unit remains available now.
- PEA-008: The exact unit orientation.
- PEA-008: Available viewing times.
- PEA-009: The AI had no verified CRM/registration result in its support response. The human later supplied the scenario fixture result; that fixture is not retrieved Pearlmont Knowledge or evidence of live production capability.
- PEA-010: Latest valid package and effective price were not verified.
- PEA-010: The requested Saturday 2:00 pm slot was not verified; Saturday 11:00 am was verified and accepted.
- PEA-011: Super Clubhouse inclusions and charging details remain unverified in the retrieved materials and supplied support fixture.

## Remaining sales weaknesses

- PEA-001: The opening answer led with the RM328,000 base price and a conditional RM302,000 calculation instead of the retrieved package guidance to lead with a currently supportable effective entry price or range. It appropriately cautioned that exact package applicability needed confirmation.
- PEA-002: Asked for exact sofa and dining-table lengths after already establishing that the buyer could not picture the flow from area figures; this was a minor, non-blocking extra question.
- PEA-003: Promised that a colleague would coordinate available viewing times despite the scenario's appointment-slots fixture being NOT_CONNECTED. The human executor appropriately disclosed that slots could not be provided.
- PEA-004: After the resolved support request, the AI mostly reported the verified facts and limitations. It could have more directly framed the maintenance figure and missing price/rent inputs as a due-diligence checklist tied to the buyer's 5–7 year horizon and 4% target.
- PEA-005: After the final support result, transparently said the check had reused earlier information, but did not offer a useful next step or continue selling; the conversation ended in repeated acknowledgements while the buyer waited for financing guidance.
- PEA-006: The turn-5 readiness assessment was only EMERGING despite the buyer saying they were open to viewing, followed by asking for a weekend and available times. The AI nevertheless proceeded to the correct operational handoff on the next turn.
- PEA-007: Turns 5–8 repeated that the documents remained outstanding and that the Agent would update the buyer, without a verified answer or a clear, concrete follow-up path.
- PEA-008: At handoff, could have more explicitly distinguished the quoted package total from the buyer’s still-unresolved question about the full amount payable.
- PEA-009: Completed a formal handoff while readiness was NOT_READY. The buyer needed an ownership check before deciding whether to proceed and had not expressed viewing intent.
- PEA-010: It did not use the retrieved package guidance to explain that pricing depends on unit category and car-park configuration. Given the buyer’s direct request for the latest terms and the knowledge’s warning about dynamic validity, withholding an unsupported quote was appropriate.
- PEA-011: The turn-4 answer could have offered a small, optional next step related to the buyer's curiosity, but the buyer had already said they were browsing and then confirmed the answer was enough; not pushing further was appropriate.
- PEA-012: {'turn': 2, 'evidence': "No material weakness; the brief acknowledgment respected the buyer's clear decision and did not continue selling."}

## Critical failures

[
  {
    "scenario_id": "PEA-001",
    "flag": "OPENING_PRICE_NOT_PACKAGE_LED",
    "evidence": "At turn 1 the agent led with RM328,000 base price; retrieved sales-package guidance says to normally lead with the supportable post-package entry price or range.",
    "turn": 1
  },
  {
    "scenario_id": "PEA-001",
    "flag": "APPOINTMENT_NOT_BOOKED",
    "evidence": "The human executor reported no available times confirmed and nothing booked; the buyer said they would check with the wife before deciding on a time.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-003",
    "flag": "OPERATIONAL_OVERPROMISE",
    "evidence": "The AI said a colleague would coordinate available viewing times although the scenario's appointment-slots fixture was NOT_CONNECTED; no actual slots were supplied.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-005",
    "flag": "SUPPORT_RESULT_ONLY_RELAYED",
    "evidence": "At turn 9, the resolved result reused the earlier project information and did not confirm a new contact check. The agent disclosed this accurately but mainly relayed the limitation rather than applying the result to continue useful selling.",
    "turn": 9
  },
  {
    "scenario_id": "PEA-005",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After the turn 8 support result, the turn 9 response ended with not pushing unit comparisons and no alternative next step; turns 10–11 repeated that the buyer would wait, without a constructive sales continuation.",
    "turn": 9
  },
  {
    "scenario_id": "PEA-005",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "A previously returned verified fixture result was requested again; the result was reused without a new Human check.",
    "turn": 8
  },
  {
    "scenario_id": "PEA-007",
    "flag": "REPETITIVE_NONPROGRESSING_FOLLOWUP",
    "evidence": "After two unavailable support results, the Agent repeated that it would keep the documents outstanding and update the buyer, without giving a verified answer or a concrete follow-up route.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-009",
    "flag": "PREMATURE_APPOINTMENT_HANDOFF",
    "evidence": "At turn 5 the AI completed HANDOFF_COMPLETED while its readiness assessment was NOT_READY; the buyer had no viewing intent and wanted only an internal ownership check before proceeding.",
    "turn": 5
  }
]

## Fixture and integrity notes

Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability.
- Brain and protected 03_sales files unchanged: True
