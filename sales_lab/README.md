# Sales Lab — realistic WhatsApp sales improvement

Codex coordinates short experiments with the **real** `app.agent.SalesAgent`, Sales Brain, Knowledge Retrieval, structured decisions and existing OpenAI Responses transport. There is no WhatsApp, database, Google Sheets or production Runtime involvement.

## What this lab is for

Improve the Agent's ability to turn an ordinary property-ad enquiry into **willingness to arrange a viewing with a human salesperson**. It is not an FAQ-completeness, room-measurement, technical-audit or final property-closing benchmark.

Use **only ordinary prospects and common hesitation** in routine simulations. Approximate scenario emphasis: 40% normal interest and 60% normal hesitation; this is an experiment design, not a market statistic. Examples: asking about general price/promotion/location, own stay vs investment, comparing properties, monthly affordability, needing to discuss with a spouse, being undecided or needing a convincing reason to visit. Mix motives and personalities. Never force every customer to demand a floor plan, room-by-room measurements or an exact unit-level all-in quote.

The Customer Simulator must remember information already shared. A customer told the home has three bedrooms should not irrationally ask again if it has three bedrooms. Customers should not volunteer viewing interest or comply with invites automatically. Responses should reflect the actual salesperson's persuasiveness and the private buyer's realistic motives. Use short, natural WhatsApp language.

**0% contrived rare-technical personas** in the ordinary sales loop (for example high-tension-cable interrogations, unusual structural/legal audits, detailed square-foot measurements for every bedroom). Exceptional real-life questions belong in a separate human-escalation/functional check, not repeated paid sales simulations.

Use existing developer evidence and the separate dated sales-lab pricing snapshot as a **general reference**, never a purported live offer. A customer who understands and considers a general starting price plausible should not be forced by the simulator to demand a final specific-unit quote before viewing. Legitimate price hesitation remains possible.

## Operator procedure

1. Use the current experimental branch and an isolated run directory with a fresh API ledger. Inspect actual commit and working tree; preserve local private files.
2. Check Codex version and native subagent availability. Main Codex coordinates a Customer Simulator and independent Judge through native tools. Prefer Luna/Low for customer and Luna/Medium for Judge when available; report effective models only when verifiable.
3. Customer subagent holds private motivation, budget, concerns and patience. Reset the same private persona per anonymous trial; reveal **only** its public customer messages to SalesAgent. Send only the real salesperson reply back to Customer. Never expose private persona, Judge scores or rubric to SalesAgent.
4. Validate the real SalesAgent path with fake HTTP dry run before live calls for each code fingerprint. The actual SalesAgent uses GPT-6 Luna / High through OpenAI API. Do not substitute Codex-generated sales replies.
5. Let each realistic customer journey continue until a natural endpoint: agreement to arrange a viewing, clear decline/disengagement, appropriate human handoff, or no meaningful remaining sales opportunity. Do not impose a fixed turn count or prolong dialogue without a sales reason.
6. Send anonymized conversations and buyer reactions to the independent Judge using `rubric.md`. Judge does not see source diffs or version mapping.
7. Diagnose the actual path before changes. Prefer simplifying conflicting Sales Brain instructions, providing more relevant evidence, or fixing a demonstrable behavioral cause rather than stacking rules or writing fixed scripts. Blind-retest comparable scenarios.
8. Continue evidence-based repair/retest rounds while useful hypotheses remain, without an arbitrary API-call or turn cap. Stop on exhausted credible hypotheses or consistent degradation. Hold out a fresh scenario until a candidate is frozen. Keep the best proven version; revert failed changes. Do not stop after each stage for approval. Technical failures stop the affected run; never retry them automatically.
9. Deliver KEEP / NEEDS REVIEW / REVERT with direct dialogue evidence, buyer interest/appointment movement, full API ledger and Git status. Commit and push only acceptable changes and reports to the experiment branch.

```sh
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial dry --scenario own_stay --customer 'Hi, I saw your property ad. How much?'
python3 -m app.sales_lab --run-dir sales_lab/reports/NEW_RUN \
  --trial baseline --scenario own_stay --customer 'PUBLIC CUSTOMER MESSAGE' \
  --live --env-file /absolute/path/to/existing/.env
```

Repeat live calls serially for each customer turn, using separate dry/live trial labels. New runs have no fixed call quota or dialogue turn cap. `ledger.jsonl` is the append-only API event journal (reservation, completion or failure) with usage when available; `ledger.json` remains the readable summary and accepts older ledgers. Any cap recorded in a legacy ledger continues to apply. The harness reserves calls before HTTP, locks concurrent turns, stops after errors and does not silently retry. A source fingerprint change requires a new trial and fresh dry run. Use `--end-dialogue --close-reason '...'` to record a natural endpoint without another SalesAgent call. Store private personas locally, not in Git.

Pending `SUPPORT_REQUEST` state is carried between turns. Do not invent human Support answers. Keep the sales conversation moving with what is known where possible; only a genuinely material, buyer-requested missing fact should block the next decision. Formal handoff stops AI turns; no booking is actually executed in Sales Lab. Invitation, interest, agreement to arrange, handoff and confirmed booking are distinct.

Simulated conversation variation makes results qualitative evidence, not proven conversion-rate uplift.
