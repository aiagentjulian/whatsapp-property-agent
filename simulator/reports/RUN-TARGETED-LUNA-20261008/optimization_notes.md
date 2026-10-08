# Targeted Luna Regression and Optimization Notes

Date: 2026-10-08

## Starting state and verification

- Repository: `/Users/julianong/Developer/whatsapp-property-agent`
- Branch: `main`; initial HEAD `baa7915`, equal to `origin/main`.
- Codex CLI: `0.154.0`. Local `codex debug models` catalog listed `gpt-5.6-luna` and Medium reasoning. All four Simulator roles were configured to that model/reasoning; provider was `codex_cli`.
- No `OPENAI_API_KEY` was used. The CLI provider strips it from the child environment.
- Usage before live scenarios: 9% of the 5-hour allowance and 38% of the weekly allowance; no paid credits. The hard cap was three live scenario attempts.

## Existing evidence reviewed

Reviewed available V1.4, V1.5, V1.6 and partial CLI baseline reports, including transcripts and Judge results:

- `RUN-V14-20261007T110053Z`
- `RUN-V15-20261007T120820Z`
- `RUN-V16-20261007T155329Z` and `DRYRUN-V16-20261007T170019Z`
- `RUN-CLI-BASELINE-20261008` and `RUN-CLI-BASELINE-20261008B`
- `DRYRUN-V14-POST-AUDIT`, `DRYRUN-V15-REGRESSION`

The historical CLI baselines used `gpt-5.6-sol`, predate the current Luna configuration, and stopped on usage exhaustion (the second baseline stopped during PEA-008). They are evidence of prior behavior, not Luna results.

## Prioritized scenario diagnoses

- **PEA-001 — Pricing opening:** V1.6 used the Type A package-led RM302,000 reference with unit/package caveats after the RM328,000 base reference. This followed effective-package pricing guidance. Not rerun.
- **PEA-003 — Support and handoff:** Prior V1.6 evidence shows repetition around the same unit-plan limitation. The customer ultimately explicitly requested a human, so the Mandatory Operational Handoff and terminal ownership transfer were correct. Not rerun; no appointment conversion was owed.
- **PEA-004 — Investment objection/support resume:** Earlier V1.6 evidence includes an empty post-support response and later a repetitive pending-document loop. The partial CLI baseline instead used available assumptions to advance the comparison, while correctly keeping the buyer not ready. In the Luna run below, the Agent used verified costs and the buyer’s own rent assumptions to produce a clearly caveated sensitivity, then handed off only viewing logistics after the buyer expressed viewing interest. The Judge also flagged a third support attempt as duplicate/unnecessary because the same investment fixture had already been resolved. That attempt asked whether a source/contact existed; the fixture reused its prior result, so the semantic necessity is ambiguous and remains a follow-up weakness.
- **PEA-007 — Technical objection:** Earlier V1.6/CLI evidence supports a correct non-conversion: the buyer required actual documents/independent technical review and explicitly requested a human. Mandatory Handoff was correct. The prior customer-facing promise of a “technical colleague” was unsupported because specialist availability was not established. A concise handoff rule was added and checked in a second PEA-007 run; the Agent no longer named a technical specialist, preserved the 2.4 m figure’s scope, and the Judge recorded no critical flags. The general-team follow-up wording still deserves monitoring.
- **PEA-008 — Support lifecycle:** Historical V1.4 evidence included a readiness path but also an availability overstatement; the partial current CLI baseline failed on usage exhaustion before a valid Judge result. Current Luna behavior remains untested.
- **PEA-011 — Low-intent browsing:** Earlier V1.4 evidence correctly avoided forcing a viewing, with a minor missed opportunity for a brief orientation question. The latest V1.6/CLI live evidence is incomplete due usage exhaustion. Current Luna behavior remains untested.

## Change and validation

Changed file: `brain/HANDOFF_RULES.md`. The rule clarifies that transfer to the general Human team does not establish specialist availability, document access, or follow-up capability. No scenario, Knowledge, scoring, schema, or Support/Handoff architecture changed.

Static configuration validation and `git diff --check` passed. Fake-transport runs completed for PEA-004 and PEA-007, and a second fake-transport PEA-007 run completed after the handoff-rule edit. The 23-dimension Judge schema and all acceptance definitions were preserved.

### Live targeted outcomes

| Run | Scenario | Result | Judge | Calls |
|---|---|---|---|---:|
| `RUN-TARGETED-LUNA-20261008` | PEA-004 | `AI_APPOINTMENT_HANDOFF_SUCCESS`; ready only after the customer said viewing was worthwhile; zero premature handoffs | 2 critical flags for the repeated/reused investment Support Request; otherwise positive sales progression and no overpromise | 18 |
| `RUN-TARGETED-LUNA-20261008` | PEA-007 | `MANDATORY_OPERATIONAL_HANDOFF`; buyer `NOT_READY`; explicit request for a technical human; no post-handoff AI reply | No critical flags; handoff correct; original wording promised a technical colleague | 8 |
| `RUN-TARGETED-LUNA-PEA007-R2-20261008` | PEA-007 | `MANDATORY_OPERATIONAL_HANDOFF`; buyer `NOT_READY`; terminal transfer retained | No critical flags; no named-specialist promise; general-team follow-up wording remains worth monitoring | 10 |

The Luna PEA-004 case is an appropriate conversion, not forced conversion: the buyer supplied their own rent assumptions, accepted the sensitivity framing, and then asked about viewing slots. PEA-007 is a correct non-conversion, not an Agent failure to obtain an appointment.

## Usage

Across three live scenario attempts: 36 model calls total, no retries; 1,371,085 input tokens, 27,236 output tokens, 1,398,321 total reported tokens. All calls reported usage. No provider interruption, authentication error, paid credit, OpenAI API call, full-suite run, or additional scenario attempt occurred. Usage after the first round was 13% for the 5-hour window and 38% for the weekly window.

## Accepted, reverted, and remaining

- **Accepted:** the concise general-Human-versus-specialist handoff clarification in `brain/HANDOFF_RULES.md`; the follow-up PEA-007 Judge/transcript supports removing the unsupported specialist designation.
- **Reverted:** an initial PEA-004 pending-document wording idea was removed because the Luna transcript did not exercise it and therefore did not validate it.
- **Remaining:** PEA-004’s repeated/reused request for source/contact merits a future focused review; PEA-008 and PEA-011 have no current Luna run; the handoff wording should continue to avoid implying the general team can supply unavailable documents. No more live scenarios were run after reaching the three-attempt cap.

## WhatsApp MVP recommendation

Proceed with a bounded WhatsApp MVP implementation and operator review path. Keep sales responses supervised until a connected support/contact workflow can confirm who owns specialist follow-up and what evidence can actually be shared. The targeted evidence does not justify unattended production handling or a claim that every support request will be fulfilled.
