# Intent Model

## Purpose

The intent model estimates how close a prospect is to taking a meaningful next step toward purchase or appointment.

It is not a generic NLP intent classifier.

Its purpose is to help the agent decide whether it should keep understanding the customer, continue qualification, position the project more strongly, resolve objections, or move toward an appointment.

The model should remain lightweight and judgment-based in V1.

Do not use a numeric score.

Use the full conversation context, not isolated keywords.

---

## Intent States

The V1 intent states are:

LOW
MEDIUM
HIGH
READY_FOR_APPOINTMENT

These labels are internal only and must never be shown to the customer.

Intent may move up or down over time.

Do not assume that intent only increases.

---

## LOW

### Definition

The customer has shown limited evidence of active purchase consideration.

They may be browsing, casually curious, collecting information, or responding without showing meaningful buying behaviour.

### Typical Signals

Examples may include:

- asking only very general questions
- asking for a brochure or basic information
- giving very short or non-committal replies
- showing curiosity without sharing any purchase context
- saying they are only looking around
- responding to an outbound message without showing clear interest

### Agent Behaviour

At LOW intent:

- do not hard sell
- do not repeatedly ask for an appointment
- respond to the customer's immediate question first
- try to understand what brought them into the conversation
- ask only one useful question when appropriate
- keep the conversation easy to continue
- avoid excessive qualification

The objective is to discover whether there is a real need or reason to continue.

---

## MEDIUM

### Definition

The customer has begun to show a genuine property need, preference, or purchase context, but is not yet clearly moving toward action.

They are engaging beyond basic curiosity.

### Typical Signals

Examples may include:

- explaining whether the property is for own stay or investment
- sharing a budget range
- discussing preferred location or property type
- asking about price, layout, facilities, accessibility, or investment considerations
- answering qualification questions meaningfully
- describing a purchase timeline
- comparing the project with alternatives at a general level

### Agent Behaviour

At MEDIUM intent:

- continue natural qualification where useful
- identify what matters most to the customer
- begin positioning the project based on those priorities
- avoid generic sales pitches
- surface the most relevant benefits rather than every feature
- watch for obstacles, concerns, and stronger buying signals

The objective is to determine fit and help the customer move from interest to serious consideration.

---

## HIGH

### Definition

The customer is showing concrete signs of serious purchase consideration.

Their questions and behaviour indicate that they are evaluating whether and how to proceed, not merely whether the project is interesting.

### Typical Signals

Examples may include:

- asking about specific unit types
- asking about unit availability
- asking detailed pricing questions
- discussing booking amount or purchase process
- discussing financing or down payment
- comparing specific units or specific competing projects
- discussing a defined purchase timeline
- involving a spouse, family member, business partner, or other decision maker
- asking questions that reveal active evaluation
- resolving remaining concerns before deciding

### Agent Behaviour

At HIGH intent:

- reduce unnecessary discovery
- do not continue qualification just to complete empty profile fields
- answer concrete purchase questions directly
- resolve the customer's main obstacle or uncertainty
- use relevant project knowledge to support a decision
- introduce a viewing, call, or appointment naturally when appropriate
- avoid over-explaining once the customer is already close to action

The objective is to remove friction and identify whether the customer is ready for the next step.

---

## READY_FOR_APPOINTMENT

### Definition

The customer has shown enough intent that a viewing, call, or appointment is the most useful next step.

The conversation no longer benefits from continued general discovery or education.

### Typical Signals

Examples may include:

- directly asking to arrange a viewing
- asking when they can visit
- offering their availability
- asking how to proceed
- saying they want to see a specific unit or layout
- asking to speak with someone about purchase arrangements
- confirming that they want to move forward after key questions are resolved

A customer may also reach this state through accumulated evidence even without using the word "appointment" or "viewing" explicitly.

### Agent Behaviour

At READY_FOR_APPOINTMENT:

- stop unnecessary qualification
- stop trying to sell additional features unless the customer asks
- move directly toward the appointment or human handoff path
- confirm the customer's preferred next step naturally
- preserve any important known context for the human agent or scheduling layer

The V1 system does not schedule the appointment itself yet.

The V1 objective is to reach and correctly identify READY_FOR_APPOINTMENT.

---

## Buying Signal Strength

Not all signals carry the same weight.

The agent should interpret signals in context.

### Weak Signals

Examples:

- "How much?"
- "Where is this?"
- "How many bedrooms?"
- asking for a brochure
- reacting positively to an advertisement

Weak signals show interest but do not by themselves prove serious intent.

### Moderate Signals

Examples:

- sharing budget
- discussing own stay versus investment
- asking about a specific layout
- explaining purchase timing
- comparing locations
- asking about financing in general

These usually support MEDIUM intent when consistent with the wider conversation.

### Strong Signals

Examples:

- asking whether a specific unit is still available
- asking about exact booking requirements
- asking about down payment or loan structure
- comparing shortlisted units
- discussing when they want to purchase
- asking detailed questions that remove a final uncertainty

These may support HIGH intent.

### Very Strong Signals

Examples:

- "Can I view this Saturday?"
- "I'm free Sunday afternoon."
- "Can I bring my wife to see the unit?"
- "How do I proceed if I want this unit?"
- "Can you arrange a viewing?"

These normally support READY_FOR_APPOINTMENT unless other context clearly contradicts that interpretation.

---

## Cooling and Negative Signals

Intent can decrease.

Examples may include:

- explicitly saying they are only browsing
- saying they are not planning to buy for a long time
- saying the project is outside their realistic budget
- saying they have already purchased elsewhere
- repeatedly showing no interest in continuing
- stating that the location, product, or project does not fit their needs
- previously strong interest followed by a clear decision not to proceed

The agent should update intent when new evidence materially changes the situation.

Do not preserve a HIGH intent label simply because the customer was previously interested.

---

## Engagement Is Not Intent

Do not confuse conversation activity with purchase intent.

The following are not sufficient by themselves to classify a prospect as HIGH:

- replying quickly
- sending many messages
- asking many general questions
- saying "interesting"
- being friendly
- using positive emojis
- spending a long time chatting

The key question is whether the customer is moving closer to a meaningful purchase action.

---

## Intent Confidence

Each intent classification should also have a lightweight confidence level:

LOW
MEDIUM
HIGH

This confidence reflects how clear the available evidence is.

It does not measure how strong the customer's buying intent is.

Examples:

A customer says only:

"Can view?"

Possible interpretation:

intent: HIGH
confidence: MEDIUM

because the message indicates strong interest but the context may still be limited.

A customer says:

"I'm free this Saturday afternoon. Can you arrange a viewing for the 3-bedroom unit?"

Possible interpretation:

intent: READY_FOR_APPOINTMENT
confidence: HIGH

Use confidence to avoid overreacting to ambiguous or isolated statements.

---

## Context Rules

Always evaluate intent using the full available conversation and lead profile.

Do not classify intent from a single keyword when broader context points elsewhere.

Examples:

A customer asking "price?" in their first message may still be LOW intent.

A customer asking "price?" after discussing unit choice, financing, and purchase timing may be HIGH intent.

The same sentence can mean different things at different stages.

---

## Stage Interaction

Intent and sales stage are related but not identical.

A customer may be:

- in UNDERSTAND with MEDIUM intent
- in QUALIFY with HIGH intent
- in HANDLE with HIGH intent
- in POSITION with MEDIUM intent
- ready to skip directly to CLOSE with READY_FOR_APPOINTMENT intent

Do not force intent to match the current sales stage mechanically.

Use intent to influence which stage should receive priority next.

---

## Behaviour Mapping

### LOW

Priority:

UNDERSTAND

Typical behaviour:

- respond
- build comfort
- identify basic need
- avoid pressure

### MEDIUM

Priority:

QUALIFY + POSITION

Typical behaviour:

- understand buying context
- identify fit
- position relevant benefits
- watch for objections and stronger signals

### HIGH

Priority:

POSITION + HANDLE + soft CLOSE

Typical behaviour:

- reduce discovery
- answer specific purchase questions
- solve remaining obstacles
- introduce the next step when natural

### READY_FOR_APPOINTMENT

Priority:

CLOSE

Typical behaviour:

- stop unnecessary discovery
- stop profile completion behaviour
- confirm next-step preference
- move toward appointment or human handoff

---

## Do Not Over-Qualify Strong Prospects

If a prospect shows clear HIGH or READY_FOR_APPOINTMENT intent, do not keep asking low-value qualification questions simply because fields remain empty.

For example, if the customer says:

"I want to view the 3-bedroom unit this Saturday."

Do not respond with:

"May I know whether this is for own stay or investment?"

Move toward the appointment path first.

Missing profile information can be collected later if it is still useful.

---

## Internal Decision Check

Before responding, consider:

1. What is the current intent state?
2. What evidence supports it?
3. Has intent increased, decreased, or stayed the same?
4. How confident is the classification?
5. Does the current intent mean the agent should stop qualifying?
6. Is the customer now close enough to move toward CLOSE?

The intent model should guide behaviour, not replace sales judgment.

---

## V1 Principle

Keep the model simple.

Do not introduce:

- 0-100 intent scores
- weighted formulas
- rigid point systems
- deterministic keyword rules

Use structured LLM judgment grounded in the conversation, lead profile, sales flow, and project knowledge.

The goal is not to measure intent perfectly.

The goal is to help the agent choose the right next sales behaviour.
