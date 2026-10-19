# Sales Lab V1

A short, Codex-coordinated experiment using the real `app.agent.SalesAgent`, Brain,
retrieval, strict decision schema and existing OpenAI Responses transport.
No WhatsApp, database, Google Sheets or runtime services are loaded.

## Operator procedure

1. Fetch the requested base and create an isolated worktree/experiment branch.
2. Check `codex --version`, `codex features list` and native session tools.
   Python cannot invoke this session's internal subagents. Main Codex coordinates
   one reusable Customer Simulator and one independent Judge through native tools.
   Prefer Luna/low for customers, Luna/medium for Judge. The coordinator's model
   is controlled by its host session; record the actual model, don't claim a switch.
3. Customer subagent holds private motivation, budget, concerns and patience.
   Reset the same persona per anonymous trial, respond naturally to actual replies,
   and stop at viewing agreement or meaningful conclusion. Do not feed private
   personas, reactions, rubric or scores to SalesAgent.
4. Run the fake HTTP dry run below before live calls for each source fingerprint.
5. Run three development cases, normally 2–3 customer turns. Feed ONLY the
   customer's public utterance into the CLI. Feed ONLY salesperson reply back to
   the customer. Main Codex records customer reactions separately.
6. Judge receives anonymized complete dialogue + customer reaction + verified
   Knowledge, without source diffs or version mapping. Score with `rubric.md`.
7. Diagnose the complete exposed path once. Change only the demonstrated cause;
   no fixed dialogue scripts or unnecessary prompt rules. Retest same opening,
   private persona, model/reasoning, three-turn cap and source evidence.
8. At most three repair rounds. Reserve holdout for final promising candidate; never
   use it for tuning. No clear improvement or new severe issue: revert candidate.
9. Save KEEP / REVERT / NEEDS REVIEW, evidence, source mapping, call ledger and
   token usage. Commit infrastructure and qualified changes; push experiment only.

```sh
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial dry --scenario own_stay --customer 'Hi, own stay from your ad' --api-limit 18
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial baseline --scenario own_stay --customer 'PUBLIC CUSTOMER MESSAGE' \
  --api-limit 18 --live --env-file /absolute/path/to/existing/.env
```

Repeat the second command for each public turn and scenario, serially. Fake and
live dialogues use separate trial names. Candidate changes require another fake
run with a new trial name. Dialogue, profile and pending Support state are held in memory during inference
and persisted only in this run directory. Pending Support requests are passed
back to SalesAgent in the same shape as Runtime `support_context`; no fake answers
are generated and requests remain OPEN for this offline evaluation. Do not edit a dialogue's source midway.
Use ONE run directory across baseline, candidates and holdout: the 24-attempt
budget applies to the whole experiment, including failed/uncertain attempts.
`--api-limit` sets and persists a run's cap from 1 through 24; later calls must
use the same cap. The ledger reserves before HTTP, locks concurrent turns, stops
on any error and never retries. A process crash leaves the experiment stopped for
operator review. Do not reset its ledger to bypass a limit. Synthetic reports
contain no real leads.

A SUPPORT_REQUEST stays pending with no invented human answer. The customer may
continue naturally; stop if they choose to wait for verification. Formal handoff
stops AI turns; no actual handoff is executed.
A customer's final agreement can be recorded without another paid turn; label
handoff processing as untested in that case. Never count invitations as bookings.

Scenarios include own-stay, couple/home-office and investment, plus autonomous
loop cases: genuine purchase interest with no customer-led viewing request,
early exploration with explicit low intent, and a reserved price-concern holdout.
Private fixtures are coordinator-only. Actual dialogue may branch between versions;
this is qualitative paired evidence, not a statistically reliable sales conversion study.
