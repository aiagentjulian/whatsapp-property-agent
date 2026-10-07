# V1.5 Regression Findings

Run: `RUN-V15-20261007T120820Z`
Agent source commit: `2a7cd59637f0bd1d06e32155018dd1f6e21d49be`

## Intended Agent fixes

### Support Vs Handoff Distinction — SUCCEEDED

All 19 support results preserve owner=AI and ai_status=ACTIVE; all 8 formal handoffs record owner=HUMAN and ai_status=PAUSED. The two PEA-009 ownership conflict and PEA-005 explicit-human-request paths are classified mandatory.

### Duplicate Support Prevention — FAILED

Three scenarios triggered duplicate-support flags: PEA-001 repeated the same layout-keyed request six times; PEA-007 repeated a technical-risk check; PEA-008 repeated availability checks after the result explicitly left availability unknown.

### Field Level Support Result Accuracy — SUCCEEDED_WITH_SCOPE_NOTE

No support-result overstatement cases were flagged. In PEA-008 the AI explicitly said availability was unconfirmed, including in its appointment-handoff message. PEA-003 availability and package claims matched the fixture, which explicitly verified them.

### Support Result Sales Continuation — PARTIAL_FAILURE

Two support results were judged relay-only and one scenario failed to resume selling. PEA-003 answered with verified unit details but did not connect them to the buyer need before handoff; PEA-004 relayed results without relevant progression.

### Package Led Opening — SUCCEEDED_WITH_FOLLOW_ON_WEAKNESS

PEA-001 opened with an indicative effective package starting reference (RM302k), distinguished it from exact unit pricing, avoided a precise unsupported calculation, and asked about car-park need. It later entered a six-request support loop and delayed the requested useful follow-up.

## V1.5 versus accepted V1.4

| Metric | V1.4 | V1.5 | Change |
|---|---:|---:|---:|
| appointment ready ai successes | 6 | 6 | 0 |
| normal sales flow convertible scenarios | 9 | 9 | 0 |
| appointment ready ai success rate | 0.667 | 0.667 | 0.0 |
| successful appointment handoffs | 6 | 6 | 0 |
| mandatory operational handoffs | 2 | 2 | 0 |
| premature appointment handoffs | 0 | 0 | 0 |
| missed ready buyers | 0 | 0 | 0 |
| support requests | 12 | 20 | 8 |
| support requests resolved | 12 | 19 | 7 |
| support completion rate | 1.0 | 0.95 | -0.050000000000000044 |
| support resume successes | 11 | 8 | -3 |
| ai resume success rate | 0.917 | 0.421 | -0.49600000000000005 |
| appointment ready after support | 5 | 5 | 0 |
| duplicate support requests | 1 | 3 | 2 |
| support result overstated | 1 | 0 | -1 |
| support result only relayed | 0 | 2 | 2 |
| failed resume cases | 0 | 1 | 1 |
| end to end confirmed appointments | 1 | 1 | 0 |
| critical failure count | 3 | 7 | 4 |

### Average Judge scores

| Dimension | V1.4 | V1.5 |
|---|---:|---:|
| customer_understanding | 4.83 | 4.5 |
| latest_message_responsiveness | 4.58 | 4.42 |
| qualification_discipline | 4.67 | 4.67 |
| selling_angle_relevance | 4.17 | 4.0 |
| objection_handling | 4.58 | 4.25 |
| unit_fit_judgment | 4.08 | 3.83 |
| buying_signal_detection | 4.75 | 4.58 |
| appointment_judgment | 4.92 | 4.67 |
| factual_accuracy | 4.67 | 4.67 |
| sales_naturalness | 4.25 | 3.83 |
| handoff_judgment | 4.92 | 4.92 |
| commercial_progression | 4.08 | 3.83 |
| appointment_readiness_detection | 4.92 | 4.83 |
| handoff_timing | 4.92 | 5.0 |
| handoff_reason_correctness | 5.0 | 4.92 |
| post_handoff_suppression | 5.0 | 5.0 |
| conversion_attribution | 5.0 | 5.0 |
| useful_information_capture | 4.25 | 4.08 |
| appointment_ready_progression | 4.08 | 4.0 |
| retrieved_knowledge_utilization | 4.67 | 4.25 |
| support_request_judgment | 4.67 | 3.92 |
| support_result_utilization | 4.5 | 4.08 |
| support_resume_quality | 4.58 | 3.92 |

### Required scenario notes

- **PEA-001:** Package-led indicative starting reference was used; exact unit applicability was caveated. Six repeated support requests followed, and the agent did not provide an attachment, verified exact package price, or the requested useful payment illustration from the fixture.
- **PEA-003:** The support fixture explicitly verified availability and price, so the claims were in-scope. The Agent did not tie the answer back to buyer needs before the viewing handoff.
- **PEA-005:** LPPSA project-route details were used correctly. The buyer explicitly requested a team member, triggering a distinct mandatory handoff.
- **PEA-007:** One duplicate support request reused the already-returned technical-risk result; the requested document/link remained unavailable in the fixture.
- **PEA-008:** No availability overstatement. The agent repeatedly requested the same availability check despite prior results expressly leaving availability unconfirmed.
- **PEA-009:** Mandatory ownership-conflict handoff stayed distinct from appointment handoff.
- **PEA-010:** One support request verified current package and an available Saturday slot; the agent moved directly to appointment handoff.

## Integrity

- 12 of 12 scenario reports and transcripts are present; every Judge report passed all 23 required score fields.
- Support results returned to AI ownership; formal handoffs transferred ownership to Human and paused AI.
- No Judge fallback scores were used.
- Brain, Skills and Pearlmont Knowledge tree hashes match before and after the run.
- Human Support results are synthetic scenario fixtures, not claims of a live production system.
