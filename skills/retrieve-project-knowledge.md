# Skill: Retrieve Project Knowledge

## Purpose

Use this skill when the Agent needs factual or sales-relevant information about the property project in order to answer a customer accurately.

This skill defines how to retrieve and use project knowledge.

It does not define the project facts themselves.

---

## Core Principle

Retrieve only the knowledge needed for the customer's current question or the Agent's current sales objective.

Do not load the entire project knowledge base into every conversation turn.

Use project knowledge to support accurate, relevant answers without overwhelming the model context.

---

## When to Use

Use this skill when the conversation requires project-specific information, including questions about:

- project overview
- developer
- location
- connectivity
- nearby amenities
- unit types
- layouts
- facilities
- tenure
- completion timeline
- pricing
- promotions
- booking terms
- maintenance fees
- financing information supplied by the project
- own-stay positioning
- investment positioning
- FAQ
- objections
- comparisons
- sales materials
- brochure or map links

Do not invoke project retrieval for purely conversational or customer-understanding questions that do not require project facts.

---

# Retrieval Objective

The retrieval process should answer one question:

> What is the smallest set of project knowledge needed to respond correctly and move the conversation forward?

Do not retrieve information simply because it exists.

---

# Knowledge Structure

The project knowledge base is expected to be split into focused Markdown files rather than one large document.

A likely structure is:

```text
knowledge/
└── project/
    ├── identity/
    ├── location/
    ├── product/
    ├── commercial/
    ├── sales/
    ├── support/
    └── assets/
```

The exact file list may evolve when the real project materials are added.

The retrieval implementation should follow the actual repository structure rather than assuming files that do not exist.

---

# Retrieval Flow

For each retrieval request:

1. identify the customer's actual question or information need,
2. identify the relevant knowledge category,
3. retrieve the smallest relevant file or set of files,
4. extract only the facts or positioning evidence needed,
5. answer according to `brain/RESPONSE_RULES.md`,
6. do not expose internal file names or retrieval mechanics to the customer.

---

# Category Routing

Use semantic relevance rather than rigid keyword matching only.

Examples:

## Price or promotion question

Prefer commercial sources such as:

- pricing
- promotions
- booking terms

Do not rely on an old FAQ answer if a more authoritative current commercial file exists.

## Unit or layout question

Prefer product sources such as:

- unit types
- layouts
- specifications

## Location question

Prefer location sources such as:

- location
- connectivity
- nearby amenities
- future development

## Investment question

Use both factual and sales-context sources when needed:

- pricing
- location
- connectivity
- tenant profile or rental evidence
- investment case
- known risks

Do not treat sales positioning as guaranteed financial outcome.

## Own-stay question

Use relevant sources such as:

- layouts
- facilities
- accessibility
- nearby amenities
- own-stay case

## Objection

Retrieve the factual basis first, then objection guidance if available.

Do not answer objections from scripts alone when factual verification is required.

---

# Source Priority

When multiple project files contain overlapping information, prefer the most authoritative and current source.

General priority:

1. current structured commercial or product fact file,
2. current official project fact file,
3. specific FAQ entry,
4. sales positioning or objection guidance,
5. general narrative material.

This priority may be overridden by explicit version or authority metadata in the real knowledge files later.

---

# Facts vs Sales Positioning

The Agent must distinguish between factual knowledge and sales interpretation.

## Factual examples

- starting price
- unit size
- number of bedrooms
- tenure
- maintenance fee
- location
- distance or connectivity when supported
- promotion terms

## Sales-positioning examples

- suitable for families
- potentially attractive for rental demand
- convenient for commuters
- better suited to a certain buyer profile

Sales positioning may be used when supported by project facts, but it must not be presented as a guaranteed fact when it is an interpretation.

---

# Investment Claims

Be especially careful with:

- rental yield
- future appreciation
- occupancy
- guaranteed rental
- future resale value
- investment return

Only state exact numbers when they are supported by authoritative project knowledge.

Do not convert a general investment narrative into a guaranteed financial claim.

Use calibrated language when the knowledge supports an argument but not a certainty.

---

# Missing Knowledge

If the required information is not available in project knowledge:

1. do not invent it,
2. do not silently substitute a guess,
3. answer naturally that the detail needs confirmation when appropriate,
4. trigger or recommend handoff when the missing fact is commercially important or high risk.

Examples include:

- latest unit availability
- unconfirmed promotion
- special rebate
- financing eligibility
- legal or tax detail

Missing knowledge should not automatically trigger handoff if the customer can still be helped accurately with available information.

---

# Conflicting Knowledge

If two sources conflict:

- do not combine them into a fabricated middle answer,
- prefer the clearly newer or explicitly authoritative source when that is known,
- otherwise treat the fact as unresolved,
- avoid presenting either version as certain,
- escalate when the discrepancy materially affects the customer decision.

The runtime should later support simple version or freshness metadata where useful.

---

# Minimal Context Rule

Do not pass whole knowledge folders to the LLM when a small relevant excerpt is enough.

Good:

```text
customer asks about 3BR pricing
-> retrieve unit type + current pricing
```

Bad:

```text
customer asks about 3BR pricing
-> load all project knowledge
```

The goal is to keep context small and reduce model confusion.

---

# Multi-File Retrieval

Multiple files may be used when the customer question genuinely spans multiple topics.

Example:

Customer:

"I'm buying for investment. Which unit is better and is the location easy to rent?"

Relevant retrieval may include:

- unit types
- pricing
- connectivity
- investment case
- rental or tenant evidence if available

Still retrieve only what is necessary to answer this specific question.

---

# Retrieval Does Not Replace Sales Judgment

Knowledge retrieval provides evidence.

The Agent must still use:

- `brain/SALES_FLOW.md`
- `brain/INTENT_MODEL.md`
- `brain/RESPONSE_RULES.md`
- the current Lead Profile

when deciding how to present that information.

The same factual knowledge may be positioned differently for:

- own-stay buyer
- investor
- low-intent browser
- high-intent buyer

Do not use one generic project pitch for every retrieved fact.

---

# Do Not Expose Internal Knowledge Mechanics

Do not tell the customer things such as:

- "According to PROJECT_OVERVIEW.md"
- "I searched the knowledge base"
- "The retrieval system says"

Respond as a property sales agent using the verified information naturally.

---

# Retrieval Output

The retrieval layer should return concise structured evidence to the Agent.

Conceptual example:

```json
{
  "topic": "3-bedroom pricing",
  "facts": [
    "3-bedroom units start from approximately RMX",
    "unit size is approximately X sqft"
  ],
  "sales_context": [
    "layout may suit small families or buyers wanting an extra room"
  ],
  "uncertainties": []
}
```

Do not store hidden chain-of-thought or long reasoning in retrieval output.

---

# V1 Retrieval Strategy

Do not assume a complex RAG system is necessary.

For V1, prefer the simplest implementation that works reliably with the final knowledge structure.

Possible implementation choices after the real project files exist include:

- direct file routing
- lightweight keyword or semantic indexing
- small local search index
- embeddings only if simpler retrieval is insufficient

Do not add vector databases, orchestration frameworks, or unnecessary infrastructure before the real project knowledge shows that they are needed.

---

# Relationship to Project Knowledge Build

This file defines retrieval behaviour before the real project knowledge is populated.

After the property materials are added:

1. finalize the actual knowledge folder structure,
2. map real files to retrieval categories,
3. implement the simplest retrieval mechanism that matches those files,
4. test retrieval in the Simulator with realistic customer questions,
5. only add more complex retrieval if failures demonstrate a real need.

---

# Final Principle

Retrieve narrowly.

Prefer authoritative facts.

Separate fact from positioning.

Do not guess missing information.

Use knowledge to answer the customer's actual question, not to dump everything the Agent knows.
