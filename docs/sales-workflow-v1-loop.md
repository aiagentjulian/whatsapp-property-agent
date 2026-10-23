# Sales Workflow V1 — Closed-loop Simulation

This is a **closed-loop sales simulation and improvement workflow**, not a standalone scoring rubric.

## Goal

Use synthetic, realistic multi-turn buyers to find where the actual GPT-6 Luna / High property salesperson fails to guide interest toward a viewing, then make **one focused workflow-level improvement**, rerun the same scenarios, and validate on a holdout buyer. Avoid line-by-line prompt patching.

The runtime's two sales branches remain **OWN_STAY** and **INVESTMENT**. There is no third BOTH branch. Do not proactively ask first-home-vs-upgrade. First-time buyer status belongs in financing context, not early sales qualification.

## Golden Conversations V1 — reference bank

The human-readable selling principles are in `brain/SALES_PLAYBOOK_V1.md`.
The nine annotated draft Golden Conversations are in
`brain/golden_conversations_v1.json`. They are **candidate exemplars**, not
validated customer outcomes, and should not be pasted wholesale into Luna's
runtime prompt. Each beat specifies customer input, one possible competent
reply, its sales rationale and a deterministic workflow-stage checkpoint.

Start with a free, deterministic corpus audit:

```sh
python -m app.golden_cases --check
python -m unittest app.test_runtime
```

**Golden examples are now enabled on this TEST branch, not production main.**
The test runtime selects at most two stage-matched fictional examples per turn
through `app/golden_guidance.py` and presents their rationale alongside their
illustrative reply. `GOLDEN_GUIDANCE_MODE=off` disables this for diagnosis;
the default on the test branch is `on`. Do not treat the bank as validated
real-life conversion results or repeat example wording mechanically.

## Golden-guided improvement Loop — run directly (no fresh old-version A/B)

The previous `d4eddeb` simulation report is the historical dissatisfied
baseline; do **not** spend additional API calls reproducing it by default.
Use the new price-evidence and viewing-progression candidate as the starting point. The dated package is evidence, not a verified current offer:

```sh
python -m app.golden_cases --check
python -m unittest app.test_runtime
python -m app.sales_simulation --dry-run
python -m app.sales_simulation --phase golden_initial
```

The last command makes real GPT-6 Luna / High seller calls and responsive
fictional buyer calls. It stores data under ignored
`sales_lab/reports/golden-loop-v2-price-viewing/` by default, **separate**
from the previous `golden-loop-v1` 21-call ledger and `closed-loop-v1`
40-call ledger. A new run can never reset or reuse
the old ledger. Check the ledger before every further phase; never delete it
to bypass the 40-request cap.

1. Review **full** initial transcripts, with specific evidence of whether
   tailored value, curiosity, genuine buying interest and viewing invitations
   emerged. Avoid a judging system that rewards merely sounding friendly.
2. Identify at most one or two recurring failure causes. Make the smallest
   coherent fix, preferably in Golden example selection, sales workflow or
   evidence relevance. Never overwrite approved knowledge or support/handoff
   safeguards. Do not optimize by forcing an invitation after every question.
3. If a candidate fix was needed, run
   `python -m app.sales_simulation --phase golden_retest`.
   Compare **the same personas** against `golden_initial`.
   If no fix is warranted, skip `golden_retest` and record the decision.
4. Run `python -m app.sales_simulation --phase golden_holdout`, including
   `holdout-weekend-couple`, `holdout-commuter-couple`, and a **new**
   four-turn `holdout-price-comparison-family` persona that has not been
   used in previous optimization. Report any weak buying signal, lack of invitation,
   unwanted hard-sell or unsupported claim.
5. Stop after one targeted retest cycle plus holdout, or when the **40 API
   attempts** hard cap is reached, whichever comes first. No endless loops
   and no silent retries. Report exact calls, known tokens, scenario outcomes,
   remaining gaps and a KEEP/REVERT judgment. Retain known weaknesses honestly.

The three phases require at most 12 + 12 + 15 = 39 seller/buyer requests
when all scenarios use their declared turn counts. Skip retest if there is
no candidate change, leaving unused calls available. No extra judge run is
allowed if it would exceed the same 40-attempt cap. That number is an upper-bound
calculation, not a claim of completed runs. Use the separate ledger to confirm
actual usage. Keep the old `main` branch, WhatsApp Runtime, contacts and CRM
untouched. A new real WhatsApp acceptance test happens only after passing the
offline gate and explicitly resetting the authorized TEST Lead.

## Price-ready Sales Loop V1 — stop re-testing the missing quote

**Purpose:** The project already has documented base pricing RM328k–RM362k,
historical 5% / 8% rebate bands and RM0.18/sqft maintenance. Those real
records remain unchanged. For OFFLINE fictional roleplay, remove the
non-current-package bottleneck using an **assumed resolved net quote of
RM330,000** for the example 900sqft / 3-bed / 2-bath unit. This is neither
a verified developer quote nor a live promotion.

The price-ready fixture exists ONLY in `app/sales_simulation.py`,
never in `knowledge/`, live `app/service.py`, Google Sheets or CRM.
It is passed to `SalesAgent.decide` as a synthetic **RESOLVED Support** result.
It also provides an illustration, **not a bank offer**: 10% deposit
(RM33,000), 90% mortgage (RM297,000), 35 years at 4% yearly, around
RM1,315/month loan plus RM162/month published maintenance. Investor
roleplay gets separately labelled **fictional** indicative rental comps,
not verified achieved yields or guaranteed returns. Nothing in this fixture
is authorized for real customer use.

**Do NOT let the fictional customer repeatedly ask for developer pricing
confirmation once Luna has already given the assumed RM330k net price.**
The roleplay buyer still makes realistic independent choices and is free
to object, compare, hesitate or reject a viewing.

```sh
python -m unittest app.test_runtime
python -m app.sales_simulation --dry-run
python -m app.sales_simulation --phase price_ready_initial
# Optional: only if one focused fix is made after reviewing initial transcripts
python -m app.sales_simulation --phase price_ready_retest
python -m app.sales_simulation --phase price_ready_holdout
```

`price_ready_initial` has two **five-turn** responsive own-stay buyer cases;
`price_ready_retest` repeats one case only if a targeted improvement was
made; `price_ready_holdout` has one independent **five-turn** rental investor.
Every seller reply uses real GPT-6 Luna / High. Buyer reactions remain
responsive to each actual seller reply, not fixed lines. Stopping after
handoff is allowed. Do not force buyer acceptance or label invitations as
bookings.

The isolated report directory is
`sales_lab/reports/price-ready-sales-loop-v1/`; the prior 40, 21 and 27
API-attempt ledgers must remain intact. Maximum calls are 18 initial,
9 optional retest, 9 holdout = 36 potential model calls,
plus **no more than 4** extra calls within the 40-attempt hard cap.
Do not erase the new ledger to restart the same experiment.

**Acceptance:** The seller answers the usable assumed price promptly
and does not repeat a pricing Support Request. It uses relevant,
accurate benefits, handles budget and monthly-cost concerns, and moves
warm buyers toward a low-pressure viewing **without assuming interest
or inventing a confirmed appointment**. The buyer can decline. Record
whether an invitation was made, whether it was accepted, an appointment
handoff occurred, or it still stalled; separate these events in reporting.
The goal is SALES CONVERSION BEHAVIOR, not accuracy-check repetition.

## One bounded optimization loop

1. **Baseline.** Inspect the current workflow and existing `app/eval_sales.py`. Run the deterministic unit suite. Simulate conversations with the real Luna seller and a simulated customer actor that responds **to the actual seller reply**, not an unrelated prewritten list. Use fictional personas only. Capture the workflow stage and sales move every turn.
2. **Evaluate.** Review the entire transcripts, not just a response. Diagnose why the seller asked a question, whether it used what the buyer already said, whether its project-specific benefit was convincing and accurate, and whether viewing was proposed at an appropriate time. Look for *observable improvement in the customer's expressed interest*, not superficial word choices.
3. **Improve.** Change the smallest **sales-workflow control or evidence-selection rule** that addresses a recurring cause. Fix prompt wording only when the failure is genuinely in expression, not as the default. Add deterministic regression tests. Do not change unrelated CRM, outreach, Meta webhook, support, handoff or production behavior.
4. **Rerun.** Replay the same fictional buyer personas from clean in-memory state, compare progression and failure rates against baseline, and test **at least one unseen holdout persona**. No cherry-picking a single lucky response. Revert the candidate if worse, no measurable gain, or factually unsafe.
5. **Stop.** Maximum **2 candidate iterations** after a baseline, and a hard limit of **40 OpenAI API calls across the entire exercise** by default. Stop earlier if the candidate passes or the budget is reached. No background/automatic endless looping.

## Synthetic buyer personas

Cover both routes, including:

- **Own Stay:** couple, small family, real practical priorities (commute, budget, space), varying interest levels. A plain `own stay` reply must not trigger a floorplan or privacy interrogation.
- **Investment:** rental-income investor and capital-appreciation investor; no invented yield or guaranteed appreciation.
- **Purchase intent overrides:** customer asks price, monthly payment, parking or layout; an objection; warm interest; explicit viewing request; ambiguous acknowledgement.
- **Holdout:** different combination from the ones used to select the candidate change.

Keep synthetic buyer motivations private from the selling agent, so the seller learns them naturally by conversation. The buyer simulator must be plausibly responsive, not cooperative regardless of what the salesperson says.

## Acceptance signals

Prioritize these outcomes:
- The salesperson learns the essential commercial direction without long question chains.
- After a useful buyer answer, the next move demonstrates **a relevant verified project benefit or a concrete purchasing step**; it does not simply ask what matters most.
- The salesperson doesn't repeatedly introduce room/privacy/desk questions that the customer never raised.
- It can answer direct project/financing questions immediately, with correct caution where facts are unverified.
- It invites a viewing naturally on warm/strong buying signals. An invitation is not an appointment; handoff occurs only after clear acceptance.
- No unverified pricing, investment returns, loan eligibility, unit availability or promised booking.

A brief numeric score may help compare **whole conversations** (sales direction, personalization, momentum, viewing timing, truthfulness), but it is subordinate to concrete transcript evidence. A mock customer's acceptance is not proof of real-world conversion.

## Safety and execution

- Reuse `app/eval_sales.py` or build a small isolated extension. Do not send WhatsApp messages, hit Meta endpoints, read customer profiles, touch live SQLite or sync Google Sheets. Do not use real customer names/numbers.
- Use **GPT-6 Luna / High** for the seller. A lighter appropriate model/reasoning can simulate the buyer; score with deterministic checks and a distinct reviewer when warranted.
- `--dry-run` must use **zero paid API calls** and validate setup, scenario definitions, and workflow stage progression.
- A real-model run must be opt-in, display/track the upper bound on API calls, and save redacted transcripts plus before/after findings under ignored local test artifacts (do not commit real model traces automatically).
- Never edit or deploy production (`main`). Commit/push to `codex/v2-handoff-ack` only if the candidate passes offline tests and shows meaningful improvement.
- When ready for a fresh **real WhatsApp test** (separate from the simulation), stop the test runtime, reset only the explicitly allowlisted test Lead with `reset-test-lead` and confirm profile, history, support and handoff are clear **before** restarting. No automatic reset of any real Lead.

## Required output

One concise report with: baseline transcript excerpts; recurring failure cause; exact structural change; same-case before/after; unseen holdout result; API calls and approximate tokens; test status; decision to **keep or revert**; latest test-branch commit. Do not call the candidate better solely because the seller sounds more polished.
