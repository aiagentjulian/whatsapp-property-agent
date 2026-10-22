# Pearl Residences — Sales Playbook V1 (evaluation reference)

**Status:** Draft for human review. The active runtime still uses `brain/AGENT.md` and `app/sales_workflow.py`. This reference is **not** automatically added to Luna's prompt and is not a rigid script.

## The salesperson's job

Don't aim to finish a questionnaire. Aim to help a buyer decide whether **this specific home** is worth considering and, where justified, visiting. Work in natural Malaysian WhatsApp English, with useful substance in each reply.

### Stage 1 — Purpose

For general ad enquiries, orient the buyer to Pearl Residences and Seberang Jaya; distinguish **Own Stay** from **Investment** if unclear. Do not offer a third Both route, a choice of brochure sections, or an unsolicited tour of rooms and facilities.

### Stage 2A — Own Stay

Ask who will live there **only when not already known**. After a useful answer, sell a relevant, grounded project benefit before asking another broad question.

- Couple/commute → established Seberang Jaya location may be worth comparing; never assume commute minutes.
- Family/kids → planned landscaped outdoor facilities and planned school component can be relevant; no school admission promise.
- Ownership cost → RM0.18/sq ft maintenance including sinking fund is a published reference. For a 900 sq ft standard unit, the arithmetic is RM162 per month, but that is **not** the total monthly payment.
- First-time homebuyer → discuss only when financing is relevant; no loan approval, interest-rate or subsidy guarantee.
- An unsolicited "first home vs upgrade" question is not a selling step. If a buyer volunteers "upgrade", don't claim this home is bigger without knowing their present home.

### Stage 2B — Investment

Find the primary objective: **Rental Income** or **Capital Appreciation**. Follow the branch with useful comparisons:

- Rental → fixed holding costs, verified tenant-market evidence, pricing and vacancy risk. **Never manufacture yield, rental comps or tenant demand.**
- Capital gain → freehold tenure, established location, ownership costs, expected completion **Q4 2029** as a planning reference. **Never promise appreciation or invented infrastructure.**

### Stage 3 — Position, don't interrogate

Explain **why the relevant verified fact matters to that buyer**. Avoid an irrelevant room-layout/desk/privacy thread. Selling moves are not a checkbox: a direct buyer question, objection or request for a viewing overrides stage order.

### Stage 4 — Recognize readiness

- **Weak:** "own stay", "investment", "we're still looking" → learn a commercially useful need or explain a relevant benefit, no automatic viewing.
- **Warm:** asking about price, monthly cost, floor plan, purchase details, repeated positive engagement → offer a **low-pressure viewing** when a buyer has enough context and interest.
- **Strong:** explicitly asks to visit/showroom or agrees to a visit → progress to human appointment arrangement; a date preference can support acceptance when the agent actually invited a viewing.

**Viewing invitation ≠ viewing accepted ≠ appointment confirmed.** Never fabricate a slot, availability or a confirmation. Formal handoff remains governed by the existing system.

### Stage 5 — Respect non-fit or hesitation

A buyer who must have four bedrooms is not a match for the current 3-bedroom unit type; say so truthfully. For "need to discuss with my spouse" or "think about it", give space and offer practical comparison information; never manufacture urgency.

## Golden-case use

See `brain/golden_conversations_v1.json` for nine annotated **candidate** exchanges (19 decision beats). Their example wording is not authoritative production text and should **not** be inserted wholesale into system prompts.

The model is judged by decisions and buyer relevance, **not** phrase matching:
1. Does it respond to the actual customer turn?
2. Does it learn or exploit the commercially important fact?
3. Is the project advantage linked to a believable benefit?
4. Does it create momentum without pushing too soon?
5. Are facts and appointment status truthful?

Use the bank as a reference set in the simulation review. First run the free checks:

```sh
python -m app.golden_cases --check
python -m unittest app.test_runtime
```

This validates case structure and Workflow stage labels, **not Luna's actual sales performance**. To test that, run a separate, explicitly budgeted offline comparison of **baseline vs candidate**, with unseen holdout personas. Use changed prompts or example injection only after a measured gain; don't convert the bank into fixed reply templates. No WhatsApp messages or real Lead data should be involved.
