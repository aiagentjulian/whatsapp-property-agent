# Sales Workflow V1 — Human Scoring Rubric & Simulation Protocol

Purpose: judge whether the **real GPT-6 Luna / High** WhatsApp property salesperson **guides buyers toward genuine interest and a viewing**, not merely whether it sounds friendly. The workflow chooses direction; Luna sells naturally. This is a human evaluation, not a keyword-based conversion score.

## 100-point rubric

| Dimension | Weight | Full-credit behavior | Common deductions |
|---|---:|---|---|
| Workflow direction & discovery | 25 | Correctly identifies Own Stay or Investment, asks only high-value questions at the right moment, and honors direct customer requests | Asks first-home vs upgrade unprompted; offers Both; irrelevant privacy, desks or floor-plan interrogation |
| Turning buyer needs into project value | 25 | Uses **verified Pearl Residences** strengths specifically tied to what the buyer revealed; creates an appealing, believable personal or investment benefit | Lists brochure facts; repeats 900 sqft/3R2B; claims an upgrade without knowing the current home |
| Commercial progression & pacing | 20 | Each substantive answer either teaches the buyer a useful fact, addresses a concern, deepens genuine desire, or advances a real purchasing decision | Question after question, "what matters most" loop, asks which brochure section to hear next |
| Buying signals & viewing discipline | 15 | Reads weak vs warm vs strong signals; may invite a viewing on warm interest; requests human booking only after clear acceptance; does not give up on tentative interest | Premature viewing, missed viewing request, invitation treated as an appointment |
| Natural Malaysian WhatsApp sales tone | 10 | Concise, confident, personable and responsive; buyer feels understood, not interviewed | Questionnaire tone, robotic multiple-choice lists, repeated feature dump or hard-sell pressure |
| Verified claims & financing care | 5 | Truthful verified project specifics, uncertainty/verification for rates, promotions, returns and loans; no invented returns or booking | Unsupported numbers, guarantee of investment return or loan approval |

Score each dimension **0 to its maximum** with a short supporting quote and turn number. Total possible: **100**.

**Pass:** 80+/100 **and no critical failure**. **Strong:** 90+/100 and no critical failure. A score is a **human judgment of this transcript**, not proof of real appointment conversion.

## Critical failures (fail independently of points)

- Invented or guaranteed financial terms, financing approvals, rental yields, capital gains, inventory, facilities or confirmed appointments.
- Claimed a viewing was booked when the customer had only been invited, or skipped the required human handoff.
- Offered `Both` as a third sales workflow path, or proactively demanded `first home vs upgrade`.
- Two or more consecutive broad discovery questions **after useful buyer information is known**, without producing a relevant property benefit or buying step. Judge the actual conversation, not punctuation alone.
- Violated real customer's request to stop or asked an obviously unrelated string of personal questions.

## Simulation suite (13 maximum live model calls, one pass)

These are **synthetic customer messages**, not scraped real leads. The next customer line is fixed: it intentionally does not adapt to the preceding AI response. Review outputs within that limitation.

| Scenario | Turns | Intended behavior |
|---|---:|---|
| `wf_own_stay` | 4 | Short opening, Own Stay household discovery, persuasive relevant benefits for a couple, useful progression with location preference; no Upgrade interrogation |
| `wf_invest_rental` | 3 | Investment → Rental goal → responsible project-specific investment selling; no guaranteed yield |
| `wf_invest_gain` | 3 | Investment → Capital Gain → realistic long-term factors and completion facts; no guaranteed appreciation |
| `wf_financing` | 2 | Own Stay → monthly installment question answered or verified, financing context / first-time buyer status only if materially relevant |
| `wf_viewing` | 1 | Explicit customer request for a visit → natural viewing/booking action, accurate handoff, never invent a confirmed slot |

## How to run

Dry run (no API calls):

```bash
python -m app.eval_sales --suite workflow_v1 --dry-run
```

One **real-model** pass (uses OpenAI API; maximum 13 calls):

```bash
python -m app.eval_sales --suite workflow_v1 --max-calls 13
```

Model must remain **gpt-6-luna / high**. Check effective config before running. Never run a second live pass without new authorization.

The existing legacy scenarios remain available via `--scenario family`, `--scenario viewing`, etc. Neither mode sends WhatsApp messages, touches production CRM, or writes to SQLite. The evaluation is synthetic and isolated in memory. Do not paste Meta/OpenAI tokens or private buyer identifiers into transcripts.

## Human review template

For each scenario, record:

- **Stage path:** expected vs observed, including any customer-question / objection / viewing override.
- **Turn-by-turn notes:** what the customer revealed; what the salesperson did; whether this created buyer value.
- **Score:** direction /25; personal selling /25; momentum /20; viewing /15; tone /10; factuality /5; total /100.
- **Critical failures:** yes/no with exact turn.
- **Recommended follow-up:** `PASS`, `WORKFLOW BUG`, `SALES-QUALITY GAP`, or `KNOWLEDGE GAP`. A failure should be diagnosed once; avoid ad-hoc micro-prompt patches after each line.

Human WhatsApp acceptance still requires **resetting the authorized test Lead** before restarting the live test Runtime. Simulation itself does **not** reset the database (it never uses the database).
