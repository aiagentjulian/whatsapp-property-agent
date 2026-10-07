# Simulator V1.4 Aggregate Diagnostic

**Executive summary:** Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in 3/11 convertible scenarios (0.5). The AI made 52 Human support requests; 46 were resolved from scenario fixtures and 8 were judged as successful AI resumption. 2 support-enabled scenarios reached appointment readiness. The Agent completed 3 appropriate appointment-ready handoffs, with 0 premature formal handoffs, 0 missed-ready buyers, and 0 end-to-end confirmed appointments. Support is an allowed capability and does not itself count as a sales handoff. Per-scenario weaknesses and fixture limits are detailed below.

## Primary appointment-ready metrics

| Metric | Count | Rate |
|---|---:|---:|
| Convertible scenarios | 11 | — |
| Appointment-ready AI successes | 3 | 0.5 |
| Successful appointment-ready handoffs | 3 | 0.273 |
| Premature appointment handoffs | 0 | 0.0 of handoffs |
| Missed-ready buyers | 0 | 0.0 |
| AI direct appointments | 0 | 0.0 |
| End-to-end confirmed appointments | 0 | 0.0 |
| Support requests | 52 | — |
| Support completion rate | 46/52 | 0.885 |
| AI resume-success rate | 8/46 | 0.174 |
| Appointment Ready reached after support | 2 | — |
| Human operational completion after successful handoff | 0 | 0.0 |
| Bad-fit correctly identified | 1 | 1.0 of non-convertible |

## Support failure modes

{
  "SUPPORT_REQUEST_UNNECESSARY": 5,
  "SUPPORT_RESULT_NOT_USED": 1,
  "SUPPORT_RESULT_ONLY_RELAYED": 3,
  "FAILED_TO_RESUME_SELLING": 4,
  "MISSED_READY_AFTER_SUPPORT": 1,
  "PREMATURE_APPOINTMENT_HANDOFF": 0,
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
    "appointment_ready_ai_successes": 3,
    "appointment_ready_ai_success_rate": 0.5,
    "successful_appointment_handoffs": 3,
    "premature_handoffs": 0,
    "missed_ready_buyers": 0,
    "end_to_end_confirmed_appointments": 0,
    "support_requests": 52,
    "support_completion_rate": 0.885,
    "support_result_utilization_score": 3.58,
    "duplicate_support_requests": 5,
    "failed_resume_cases": 4,
    "ai_resume_success_rate": 0.174
  }
}

## AI outcome classification

{
  "AI_APPOINTMENT_READY_SUCCESS": 0,
  "AI_APPOINTMENT_HANDOFF_SUCCESS": 3,
  "AI_DIRECT_APPOINTMENT_SUCCESS": 0,
  "AI_PROGRESS_BUT_NOT_READY": 3,
  "AI_EARLY_HANDOFF": 0,
  "AI_MISSED_READY_BUYER": 0,
  "AI_LOST_CONVERSION": 0,
  "MANDATORY_OPERATIONAL_HANDOFF": 5,
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
    "appointment_ready_ai_successes": 3,
    "appointment_ready_ai_success_rate": 0.273,
    "successful_appointment_ready_handoffs": 3,
    "premature_handoffs": 0,
    "confirmed_appointments": 0,
    "commercial_progression": 3.25,
    "naturalness": 3.67,
    "handoff_judgment": 4.67,
    "useful_information_capture": 4.25,
    "retrieved_knowledge_utilization": 4.42
  },
  "note": "V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."
}

## Diagnostic quality

- Average useful information capture: 4.25/5
- Readiness detection accuracy: 0.917
- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): 1.25
- Retrieval quality/utilization: 4.42/5
- Critical failures: 18
- Post-handoff AI reply violations: 0
- All scenarios completed: 12/12

## Average Judge scores

- customer_understanding: 4.5/5
- latest_message_responsiveness: 4.0/5
- qualification_discipline: 4.42/5
- selling_angle_relevance: 4.08/5
- objection_handling: 4.08/5
- unit_fit_judgment: 3.92/5
- buying_signal_detection: 4.17/5
- appointment_judgment: 4.5/5
- factual_accuracy: 4.58/5
- sales_naturalness: 3.67/5
- handoff_judgment: 4.67/5
- commercial_progression: 3.25/5
- appointment_readiness_detection: 4.58/5
- handoff_timing: 4.67/5
- handoff_reason_correctness: 4.92/5
- post_handoff_suppression: 5.0/5
- conversion_attribution: 5.0/5
- useful_information_capture: 4.25/5
- appointment_ready_progression: 3.25/5
- retrieved_knowledge_utilization: 4.42/5
- support_request_judgment: 3.5/5
- support_result_utilization: 3.58/5
- support_resume_quality: 3.25/5

## Retrieval misses

- PEA-005: No retrieved Knowledge or supplied support fixture verified a Pearlmont-specific LPPSA document checklist.
- PEA-005: No supplied support fixture verified current price options or package validity.
- PEA-007: No material Knowledge retrieval miss is evident: the retrieved risk FAQ supports the Block 1B distance, the raised level, JPS reference, and the requirement not to promise zero risk.
- PEA-007: Document-sharing availability, a tower-specific plan's shareability, and availability of a technical representative were not established by retrieved Knowledge or by the support fixture.
- PEA-011: An itemized list of planned facilities and specific clubhouse booking rules were not present in the retrieved source material.

## Retrieved Knowledge not used

- PEA-003: {'source': 'knowledge/project/pearlmont/03_sales/unit-fit.md', 'evidence': 'The guide says a specific floor/view/carpark combination is a strong buying signal and recommends narrowing the suitable category, verifying availability, and moving toward a viewing rather than prolonged comparison.'}
- PEA-007: The retrieved sensitive-FAQ guidance says to hand off when a decision depends on unconfirmed technical or environmental information. The AI eventually did this, but did not act promptly after the buyer requested the technical team.
- PEA-010: {'path': 'knowledge/project/pearlmont/02_commercial/sales-package.md', 'evidence': 'Retrieved material explains that effective price depends on unit category, floor band, and car-park allocation, and warns that current package validity is time-sensitive. The AI appropriately did not present an unverified effective price, but did not use these mechanics to explain what would need confirming.'}
- PEA-010: {'path': 'knowledge/project/pearlmont/03_sales/viewing-close.md', 'evidence': 'The guidance recommends reducing generic qualification and moving directly to scheduling when a buyer asks about weekend viewing. The AI handed off, but did not first ask for the preferred time or attendees.'}

## Remaining Knowledge gaps

- PEA-001: No verified instalment illustration was supplied in the support trace.
- PEA-001: No verified show-unit availability or viewing slots were supplied in the support trace or human operations fixture.
- PEA-002: Current show-unit viewing days and times could not be verified by the human executor; the requested slot-check task remained incomplete.
- PEA-002: The buyer’s appointment was not confirmed because no specific available time was supplied and accepted.
- PEA-003: The simulator fixture is synthetic operational evidence, not Pearlmont Knowledge or a real production inventory/pricing connection.
- PEA-003: No real-world inventory or price schedule was available to the human executor in this run; the requested real-world check was not completed.
- PEA-004: No verified rental comparables, rental-demand figures, or substantiated yield.
- PEA-004: No sourced appreciation forecast.
- PEA-004: No verified current effective price or package validity for the specific unit.
- PEA-004: No confirmed recurring ownership costs beyond the sourced maintenance fee.
- PEA-005: The buyer’s personal LPPSA eligibility and approval remain unverified and must be determined by LPPSA.
- PEA-005: A Pearlmont-specific property/document checklist was not verified.
- PEA-005: Current price options and package validity were not verified.
- PEA-005: The requested LPPSA contact or channel was not provided.
- PEA-006: {'gap': 'Whether a typical residential floor plan can be shared and whether a viewing can include access to a residential corridor.', 'source_target': 'MISSING_SOURCE', 'note': 'The support fixture did not answer either operational-arrangement question. Its synthetic result confirms shared residential lift lobbies and corridors only.'}
- PEA-007: Whether actual JPS/flood-study documents can be shared and any conditions.
- PEA-007: Whether a tower-specific plan can be shared.
- PEA-007: Whether a technical representative can explain the verified details.
- PEA-007: The fixture did not provide an independent engineering opinion, official flood-history certification, or a zero-risk conclusion.
- PEA-008: Exact unit number and unit-level orientation for the candidate option.
- PEA-008: Live availability and any fresh unit-schedule confirmation.
- PEA-008: What the RM349,000 package includes and any additional buyer-payable costs.
- PEA-008: A verified viewing slot; appointment slots were NOT_CONNECTED.
- PEA-009: The buyer's future Pearlmont questions and viewing interest remain unknown; no further AI sales interaction occurred after the mandatory handoff.
- PEA-010: Whether the 14 August 2026 package was still current.
- PEA-010: The buyer's effective unit-specific price and applicable terms.
- PEA-010: Whether a Saturday afternoon viewing slot was available.
- PEA-011: The retrieved Knowledge did not specify individual facilities on the Level 9 deck or whether particular clubhouse spaces are bookable.
- PEA-011: The support trace returned UNAVAILABLE with no matching simulator fixture; no operational verification was supplied.

## Remaining sales weaknesses

- PEA-001: The unresolved monthly-cost concern was not revisited after the layout discussion. This was not a blocker to the buyer’s explicit viewing request, and the Agent appropriately avoided inventing an instalment figure.
- PEA-002: The Agent could have made the final close slightly more concrete by explicitly acknowledging that the buyer could judge the layout with their spouse or family. This is a minor opportunity, not a readiness or handoff failure.
- PEA-003: After receiving a matching verified-in-simulation option, it first presented the match, then disavowed it and repeated requests for real-world records the support fixture could not provide. It did not use the verified result to confidently continue toward a viewing within the simulation.
- PEA-004: The third support request revisited current effective pricing after the first request had already asked for that basis and the result established it was unverified. It was resolved by reusing the existing result rather than obtaining new evidence.
- PEA-005: After providing careful financing information, it did little to build a sales path toward viewing or test whether the buyer would consider one once price and financing questions were clearer.
- PEA-006: After the first support answer, the agent repeatedly issued near-duplicate support requests that reused the same fixture result, then repeated the same limitation to the buyer without meaningfully progressing the conversation.
- PEA-007: After the support fixture repeatedly returned the same summary and explicitly indicated no new check had been performed, the AI kept issuing near-identical requests instead of stopping the loop and honoring the buyer's explicit request for a project/technical-team handoff promptly.
- PEA-008: The agent repeatedly requested essentially the same unavailable live details, then repeated the known fixture facts and limitations without a useful sales next step. The buyer had to ask several times before receiving the requested mandatory human transfer.
- PEA-009: {'evidence': 'The Agent did not reach a subsequent sales conversation or appointment-ready assessment, but the completed mandatory handoff correctly paused AI; this is not a missed appointment handoff.'}
- PEA-010: Did not collect the preferred viewing time or party size, and did not offer any cautiously framed package information from retrieved Knowledge before handing off.
- PEA-011: The requested support lookup returned no fixture answer, leaving the buyer's itemized facilities question unresolved. The AI handled that limitation transparently; this was not a failure to use a verified support result.
- PEA-012: The initial follow-up asking whether timing was flexible was unnecessary because the buyer’s opening message already stated a next-month move-in need. The buyer clarified that it was non-negotiable, and the AI then handled the mismatch appropriately.

## Critical failures

[
  {
    "scenario_id": "PEA-003",
    "flag": "SUPPORT_RESULT_NOT_USED",
    "evidence": "After the resolved fixture supplied the matching option and total, the agent said it could not confirm the unit's availability, carparks, facing, or price and told the buyer not to rely on those details.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-003",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "After support explicitly returned the existing simulator answer and said no new human check was performed, the agent requested another check for substantially the same matching-unit and price information.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-003",
    "flag": "MISSED_READY_AFTER_SUPPORT",
    "evidence": "The buyer's stated condition was a matching sea-facing two-carpark option and confirmed total price; the simulator fixture supplied that match, but the agent did not recognize readiness or progress the viewing.",
    "turn": 7
  },
  {
    "scenario_id": "PEA-003",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "The later support resolutions were followed by limitation statements rather than a useful customer-facing continuation that used the available answer and advanced the sale.",
    "turn": 7
  },
  {
    "scenario_id": "PEA-003",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-004",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "At turn 1, support was asked to check the current effective price basis. At turn 5, the AI requested a current effective price and package check for a specific 900 sq.ft. unit; the fixture result stated no new check was performed and reused the prior result.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-004",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 3
  },
  {
    "scenario_id": "PEA-006",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "After the initial request at turn 3, the agent submitted 12 further requests (turns 4, 6, 7, 10, 11, 13, and 15–20). The support trace marks these as reused results with no new human lookup.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-006",
    "flag": "SUPPORT_RESULT_OVERSTATED",
    "evidence": "The fixture says private corridors are not shown; the agent stated “there aren’t private corridors,” which asserts more than the fixture verifies.",
    "turn": 8
  },
  {
    "scenario_id": "PEA-006",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After the initial useful response at turn 5, later responses largely repeated the same verified corridor fact and the same unconfirmed access limitation, without a fresh useful sales continuation.",
    "turn": 8
  },
  {
    "scenario_id": "PEA-006",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-007",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "After the initial result at turn 2, requests at turn 4 and turns 7–26 repeatedly sought a fresh answer, although the fixture trace marked them as reused results with no new human lookup.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-007",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After the initial contextual answer at turn 3, subsequent customer-facing replies mostly repeated the same facts and unresolved gap; the AI did not establish a useful new next step and delayed the requested team transfer until turn 27.",
    "turn": 5
  },
  {
    "scenario_id": "PEA-007",
    "flag": "DELAYED_MANDATORY_OPERATIONAL_HANDOFF",
    "evidence": "The buyer asked the AI to pass the matter to the project/technical team at turn 9. The AI did not complete the mandatory handoff until turn 27.",
    "turn": 9
  },
  {
    "scenario_id": "PEA-007",
    "flag": "SUPPORT_REQUEST_UNNECESSARY",
    "evidence": "The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.",
    "turn": 4
  },
  {
    "scenario_id": "PEA-008",
    "flag": "DUPLICATE_SUPPORT_REQUEST",
    "evidence": "The turn 6 request repeated the turn 4 request for exact orientation, availability, and full payable amount; turn 9 repeated the fresh-check request made at turn 8. The support trace shows these later requests reused the existing fixture and performed no new lookup.",
    "turn": 6
  },
  {
    "scenario_id": "PEA-008",
    "flag": "FAILED_TO_RESUME_SELLING",
    "evidence": "After the repeated results, turns 5, 7, and 10 largely restated the RM349,000 fixture and unresolved details, without a meaningful customer-facing sales continuation. The buyer said they had asked multiple times and requested a person at turn 10.",
    "turn": 10
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
