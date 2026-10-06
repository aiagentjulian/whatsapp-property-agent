# Simulator V1 Aggregate Report

**Executive summary:** Completed 1/1 scenarios; confirmed 0 appointments among 1 convertible scenarios (0.0). Good judgment 1.0; critical flags 0. Review scenario reports for buyer-fit and accuracy findings.

## Run totals

| Metric | Result |
|---|---:|
| Scenarios attempted | 1 |
| Completed | 1 |
| Failed | 0 |
| Convertible | 1 |
| Confirmed appointments | 0 |
| Appointment interest cases | 0 |
| Conversion / convertible | 0.0 |
| Good judgment rate | 1.0 |
| Good fit rejections | 0 |
| Critical flags | 0 |

## Average Judge scores

- customer_understanding: 5.0/5
- latest_message_responsiveness: 5.0/5
- qualification_discipline: 5.0/5
- selling_angle_relevance: 3.0/5
- objection_handling: 5.0/5
- unit_fit_judgment: 4.0/5
- buying_signal_detection: 5.0/5
- appointment_judgment: 5.0/5
- factual_accuracy: 5.0/5
- sales_naturalness: 4.0/5
- handoff_judgment: 5.0/5
- commercial_progression: 4.0/5

## Findings

### Weakest Behaviors

- PEA-009: No material sales error. The agent should ensure the promised team check and update actually happen.
### Unnecessary Qualification

### Missed Buying Signals

### Premature Close Cases

### Delayed Close Cases

### Unsupported Factual Claims

### Retrieval Misses

- PEA-009: The turn 2 and turn 3 retrievals loaded unit/layout and viewing-close material that was not relevant to the registration-conflict request. No ownership policy was available; the agent appropriately handed the issue to the team instead of inferring a policy.
### Handoff Errors

### Unit Fit Mistakes


## Top priorities

[
  {
    "scenario_id": "PEA-009",
    "category": "Knowledge",
    "target_file": "knowledge/project/pearlmont/03_sales/agent_registration_and_conflict.md",
    "reason": "Document the approved registration-check and agent-conflict escalation process, including what the customer should be told while verification is pending."
  }
]

## Critical failures

[]

## Run integrity

- Brain/Knowledge unchanged: True
- Model config: `{"sales_agent": {"model": "gpt-6-luna", "reasoning": "medium"}, "customer_simulator": {"model": "gpt-6-luna", "reasoning": "medium"}, "judge": {"model": "gpt-6-luna", "reasoning": "medium"}}`
- Calls: 6; retries: 0
