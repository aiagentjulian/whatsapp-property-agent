# Sales Lab — normal buyers, appointment-first

This isolated experiment uses the **real** `app.agent.SalesAgent` (GPT-6 Luna / High). The Customer and Judge are native Codex subagents. No live WhatsApp, Meta, Sheets, database or production deployment.

**One sales objective:** turn an everyday property-ad enquiry into genuine willingness to **arrange a viewing**, then hand arrangements to a human salesperson. The Agent is not judged on completing an FAQ, qualifying every detail, or closing the purchase.

## Ordinary customer contract

Use varied ordinary Malaysian prospects who saw the Pearl Residences ad. A buyer may be interested, browsing, comparing, price-conscious, discussing with a partner, or unsure about timing. Vary these situations naturally; do not enforce a fixed interest/hesitation percentage. **No exotic technical interrogations or adversarial buyer tests** in the sales-optimization loop. Such cases can go to a human in production.

A real buyer writes briefly and **remembers what was said**. If bedrooms or the general starting price have already been explained, they do not ask again without a new reason. The simulator must not keep introducing invented approval requirements (exact car park, approved floor plan, current unit quote, each room's sqft) before viewing. A genuine buyer may ask for normal costs, but not every persona should develop the exact same price barrier.

Buyers are not automatically agreeable: a weak pitch may be ignored, a relevant benefit can build interest, and a poorly timed viewing request can be declined. The simulator must allow an ordinary hesitant buyer to make progress when the Agent earns it, rather than being scripted to defer forever. Customers must not ask for viewing unprompted merely to help the Agent pass.

For native Codex Customer Simulator personas and turn-by-turn behavior, follow [customer_simulator.md](customer_simulator.md). Create and freeze the private persona before any Agent response; run separate Customer Simulator subagents for paired transcripts so customer reactions follow each actual conversation instead of a copied message script.

## Commercial test premise — do not manufacture the same price objection

The lab price fixture is `pricing_snapshot_2026-08-14.json`. For this **hypothetical as-of-14-Aug-2026** sales exercise only, treat that day's developer package as the known promotional context: an eligible-category **approximately RM302k after-rebate base reference**. It is **not** proof of a current October 2026 offer or an all-in unit quote.

- The Agent may introduce that promotion succinctly as a sales hook; it need not recount base-price mathematics, quote carpark premiums, or repeat historical-pricing warnings in every reply.
- Once a customer says the general bracket seems workable, the simulator should move to normal motivation and buying considerations instead of reopening whether the same price is current.
- If a customer independently and specifically needs a final all-in quote, a financing illustration, or a different unit's price, handle the real uncertainty. Do not invent answers.
- Never use this dated premise for a real customer or deploy it as an actual October offer. Never manufacture availability, urgency, countdowns or promotional deadlines.

**Example normal journey (not a script):** ad enquiry → simple attractive price/project context → one useful need → buyer-specific reason to own → ordinary hesitation → Agent offers a compelling reason to see the property → buyer either accepts arrangements, asks one meaningful follow-up, or declines.

The customer should not be made to repeat facts or wait for unavailable documents purely to prolong the experiment.

## Testing and judging

1. Establish source commit, keep an isolated run directory, preserve private local persona files and run fake-HTTP validation through the real SalesAgent.
2. Customer subagent holds private needs and reacts to **actual Agent messages**. Only customer-facing messages go to SalesAgent; never leak persona instructions, targets or grading.
3. Allow as many natural turns and actual API calls as the experiment needs; stop a dialogue on arrangement agreement, real disengagement, proper human handoff, or lack of a meaningful next sales step. Do not use a fixed turn or API cap, and do not produce endless follow-up loops.
4. Have an independent blind Judge assess **change in buying/viewing willingness caused by the salesperson**, with `rubric.md`. A viewing invitation is not agreement. Verify `APPOINTMENT_HANDOFF` separately for explicit consent.
5. Diagnose concrete weak selling behavior; modify only evidence-backed causes. Retest comparable normal personas and fresh holdouts. Revert unproven regressions and continue autonomously while credible ideas remain.
6. Preserve the real API/token journal, test results and git commit; push the experimental branch only. Never merge/deploy or touch runtime customer data.

```sh
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial dry --scenario own_stay --customer 'Hi, saw the property ad. Can share the price?'
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial baseline --scenario own_stay --customer 'PUBLIC CUSTOMER MESSAGE' \
  --live --env-file /absolute/path/to/existing/.env
```

Calls are serial; each source fingerprint needs a fresh fake dry-run. New runs have no fixed quota; older ledger caps remain enforced. `ledger.jsonl` records attempts and usage, and `--end-dialogue` records natural completion without a paid call. Pending Support is not silently fabricated or resolved. Do not reset ledgers after failure; inspect errors.

**Judge success on legitimate appointment progression and realistic conversations, not canned compliance or score inflation.**
