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

During the next authorized simulation, use the Golden bank to review whether
Luna selected a commercially useful move, not whether it repeated sample text.
Preserve an **unseen holdout** distinct from the Golden cases and compare the
baseline and candidate at whole-conversation level. Do not claim the bank
trained Luna. Only consider selective few-shot injection after observed
holdout improvement and token-cost comparison.

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
