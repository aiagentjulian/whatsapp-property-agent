# Simulator V1 Aggregate Report

**Executive summary:** Completed 12/12 scenarios; confirmed 0 appointments among 11 convertible scenarios (0.0). Good judgment 1.0; critical flags 0. Review scenario reports for buyer-fit and accuracy findings.

## Run totals

| Metric | Result |
|---|---:|
| Scenarios attempted | 12 |
| Completed | 12 |
| Failed | 0 |
| Convertible | 11 |
| Confirmed appointments | 0 |
| Appointment interest cases | 5 |
| Conversion / convertible | 0.0 |
| Good judgment rate | 1.0 |
| Good fit rejections | 1 |
| Critical flags | 0 |

## Appointment outcome classifications

{"APPOINTMENT_INTEREST": 5, "NO_APPOINTMENT_BUT_GOOD_JUDGMENT": 6, "BAD_FIT_CORRECTLY_IDENTIFIED": 1}

## Average Judge scores

- customer_understanding: 4.92/5
- latest_message_responsiveness: 4.17/5
- qualification_discipline: 4.83/5
- selling_angle_relevance: 4.0/5
- objection_handling: 4.5/5
- unit_fit_judgment: 4.33/5
- buying_signal_detection: 4.33/5
- appointment_judgment: 4.83/5
- factual_accuracy: 5.0/5
- sales_naturalness: 3.67/5
- handoff_judgment: 4.08/5
- commercial_progression: 3.5/5

## Findings

### Weakest Behaviors

- PEA-001: After the buyer had clearly requested the confirmed figures and floor plan and said they would decide about viewing afterward, the agent kept repeating essentially the same commitment across several turns. This added no value and prompted the buyer to explicitly ask that the agent stop checking in until something was confirmed.
- PEA-002: Turns 6–7 repeat that a colleague will follow up, with the final acknowledgement adding no new information. This is a minor response-style weakness, not a failed close.
- PEA-003: After the handoff, the agent fell into repetitive acknowledgements. It could have confirmed the next action once, said it would ask the colleague for an update timeframe, and then stopped repeating the same summary.
- PEA-004: The repeated handoff acknowledgments became redundant and did not add a specific follow-up process. The agent could have confirmed the requested materials and, without delaying the direct answers, identified the buyer's holding horizon or target return for a more relevant follow-up.
- PEA-005: No material wrong move. The follow-up could be slightly more concrete about how the team will continue the conversation, but the transcript does not establish that a contact method or timing was needed.
- PEA-006: Repeatedly restating that the confirmed plan would be shared after the buyer had already acknowledged the handoff. This added no progress, particularly after the buyer said there was no need to repeat it.
- PEA-007: No material sales error. The handoff would be stronger with a clear owner and a realistic follow-up timeframe; the final acknowledgments also repeat the same commitment without adding a next step.
- PEA-008: The follow-up repeats the same handoff commitment, and one turn is empty. The agent could have confirmed a simple follow-up expectation without implying a viewing was being arranged.
- PEA-009: No material sales error. The promise to update the customer once the team confirms should be followed through by the responsible team.
- PEA-010: The acknowledgments at turns 3 and 4 are redundant. After the buyer had been told that the team would verify and follow up, repeating the same update created no additional commercial progress.
- PEA-011: No material sales error. The map response could have offered to share a verified map later, but the agent appropriately avoided promising an asset it did not have.
- PEA-012: No material sales error. The flexibility check was reasonable and the agent stopped once the buyer confirmed the mismatch was absolute.
### Unnecessary Qualification

### Missed Buying Signals

- PEA-001: At turn 3, the buyer said they would be open to viewing if the upfront cost was manageable. The agent recognised this, but could have made the next step more concrete by clearly linking the follow-up to a viewing after the requested materials were reviewed.
- PEA-006: The buyer said the confirmed plan would determine whether viewing was worthwhile. This is conditional viewing interest, not appointment readiness; the agent correctly did not treat it as a booking.
### Premature Close Cases

### Delayed Close Cases

### Unsupported Factual Claims

### Retrieval Misses

- PEA-001: Current effective pricing and package information was a central concern, but `sales-package.md` was not among the retrieved files, despite `pricing.md` identifying it as the source for current rebate and package mechanics. The agent appropriately did not invent those figures and sought confirmation.
- PEA-009: The retrieved unit-fit and viewing-close material was not needed for the registration-conflict request.
- PEA-009: No supplied source provides a specific registration-ownership policy or verification workflow.
### Handoff Errors

### Unit Fit Mistakes


## Top priorities

[
  {
    "scenario_id": "PEA-001",
    "category": "Implementation Bug",
    "target_file": "MISSING_SOURCE",
    "reason": "The supplied source catalog contains property knowledge but no conversation-orchestration or turn-management policy that would prevent repeated MAINTAIN-style acknowledgements when no new information is available. Add or identify the applicable policy before assigning a repository path."
  },
  {
    "scenario_id": "PEA-002",
    "category": "Response Style",
    "target_file": "knowledge/project/pearlmont/03_sales/viewing-close.md",
    "reason": "Reinforce concise post-handoff communication: acknowledge the requested weekend follow-up once, avoid repetitive acknowledgements, and distinguish slot-checking from appointment confirmation."
  },
  {
    "scenario_id": "PEA-003",
    "category": "Response Style",
    "target_file": "knowledge/project/pearlmont/03_sales/unit-fit.md",
    "reason": "The supplied unit-fit guidance supports verifying exact availability and progressing interested buyers toward a viewing. Reinforce a concise handoff pattern that confirms ownership and the next update once, then avoids repetitive maintenance messages while the buyer awaits verified options."
  },
  {
    "scenario_id": "PEA-004",
    "category": "Response Style",
    "target_file": "knowledge/project/pearlmont/03_sales/sales-judgment.md",
    "reason": "Encourage concise, non-repetitive follow-up acknowledgments after a handoff, with a useful next step rather than restating the same commitment across turns."
  },
  {
    "scenario_id": "PEA-005",
    "category": "Response Style",
    "target_file": "knowledge/project/pearlmont/02_commercial/lppsa.md",
    "reason": "No material defect identified. Optionally reinforce that a human follow-up should make the next step clear while preserving the no-approval-promise rule."
  },
  {
    "scenario_id": "PEA-006",
    "category": "Knowledge",
    "target_file": "MISSING_SOURCE",
    "reason": "The supplied sources document lift counts and link-bridge locations but do not establish resident movement controls between towers or the precise lift-lobby-to-unit-corridor arrangement. Add an authoritative, verified access and corridor plan so the agent can resolve this buyer's key concern."
  },
  {
    "scenario_id": "PEA-007",
    "category": "Knowledge",
    "target_file": "MISSING_SOURCE",
    "reason": "The supplied Knowledge supports the stated FAQ figures but does not include the shareable original FAQ document or official flood assessment/site records requested by the buyer. Add these sources if available, or make their absence explicit to agents."
  },
  {
    "scenario_id": "PEA-008",
    "category": "Response Style",
    "target_file": "knowledge/project/pearlmont/03_sales/sales-judgment.md",
    "reason": "Encourage a concise, concrete handoff follow-up and prevent blank or repetitive maintenance replies when a buyer is waiting for verified unit information."
  },
  {
    "scenario_id": "PEA-009",
    "category": "Knowledge",
    "target_file": "MISSING_SOURCE",
    "reason": "Provide an explicit agent-ownership and registration-verification handoff procedure, including how to pause duplicate or viewing follow-up and who is responsible for updating the customer."
  },
  {
    "scenario_id": "PEA-010",
    "category": "Implementation Bug",
    "target_file": "MISSING_SOURCE",
    "reason": "The supplied viewing-close guidance says AI auto-send stops once ownership transfers to a human, but no runtime ownership or message-suppression implementation file was supplied. The repeated automated acknowledgments after handoff should be prevented or routed through the human follow-up workflow."
  },
  {
    "scenario_id": "PEA-011",
    "category": "Knowledge",
    "target_file": "knowledge/project/pearlmont/01_facts/location-and-connectivity.md",
    "reason": "The buyer asked for a location map, but the supplied location source contains no shareable map link or asset. Add a verified customer-facing map reference if one exists; otherwise the agent’s honest response is appropriate."
  },
  {
    "scenario_id": "PEA-012",
    "category": "No change",
    "target_file": "knowledge/project/pearlmont/03_sales/unit-fit.md",
    "reason": "The existing unit-fit guidance supports matching the buyer's actual needs and avoiding unsuitable recommendations; the agent followed that principle."
  }
]

## Critical failures

[]

## Run integrity

- Brain/Knowledge unchanged: True
- Model config: `{"sales_agent": {"model": "gpt-6-luna", "reasoning": "medium"}, "customer_simulator": {"model": "gpt-6-luna", "reasoning": "medium"}, "judge": {"model": "gpt-6-luna", "reasoning": "medium"}}`
- Calls: 153; retries: 0

Judge rescore: actual retrieved Knowledge source text was supplied for factual evaluation; no Agent or Customer turns were rerun.
