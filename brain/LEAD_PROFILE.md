# Lead Profile Schema

## Purpose

The Lead Profile is the agent's working memory of the prospect.

Its purpose is to help the agent remember what has already been learned, avoid repeating questions, adapt the sales conversation, and decide the most useful next action.

The profile is not a questionnaire and is not a checklist that must be completed before the conversation can move forward.

A strong prospect may move directly toward an appointment even when many profile fields remain unknown.

---

## Core Principle

Store what the customer has genuinely revealed.

Do not ask questions simply to fill empty fields.

Do not infer sensitive or commercial facts unless the conversation supports them clearly.

When information is uncertain, record it as uncertain rather than converting it into a fact.

The profile exists to improve sales judgment, not to maximise data collection.

---

## Lead Creation Rule

A contact becomes a Lead only when a real two-way conversation begins.

For INBOUND:

- the customer's first inbound message creates the Lead Profile.

For OUTBOUND:

- sending an outbound campaign message does not create a Lead Profile,
- the outbound contact remains only in the outbound contact source/list until they reply,
- the prospect's first reply creates the Lead Profile,
- after creation, the Lead Profile continues as the single customer state for that prospect.

Therefore:

`OUTBOUND MESSAGE SENT != LEAD`

`OUTBOUND CUSTOMER REPLIED = CREATE LEAD`

Outbound contact-list data is operational campaign data and should not automatically be supplied to the LLM as customer context unless it becomes relevant after the prospect replies.

---

## One Customer, One Current Profile

For the same property project, one customer should normally have one current Lead Profile.

Do not create separate profiles simply because the customer appears through more than one touchpoint.

If a known prospect first came from an outbound campaign and later re-enters through an inbound link or enquiry, preserve the existing profile and update the relevant source context rather than creating a duplicate Lead.

---

## Profile Structure

The Lead Profile should be organised into the following groups:

1. Identity
2. Source and Conversation Context
3. Purchase Purpose
4. Property Preferences
5. Commercial Fit
6. Timing and Readiness
7. Motivations and Decision Factors
8. Concerns and Objections
9. Sales State
10. Handoff and Follow-up
11. Conversation Memory

---

# 1. Identity

## `lead_id`

Internal unique identifier for the prospect.

Do not expose this value to the customer.

## `name`

Customer name when known.

Do not repeatedly ask for a name if the conversation is progressing naturally without it.

## `phone`

WhatsApp phone number or conversation identifier when available from the messaging layer.

This should normally be captured automatically rather than asked in conversation.

## `preferred_language`

The language or language style the customer appears to prefer.

Possible examples:

- English
- Chinese
- Bahasa Malaysia
- mixed Malaysian English / Chinese
- mixed Malaysian English / Bahasa Malaysia
- unknown

This should be inferred from the customer's actual communication and may change during the conversation.

Do not force a language preference question.

---

# 2. Source and Conversation Context

## `lead_source`

How the prospect entered the real two-way sales conversation.

Allowed values:

- INBOUND
- OUTBOUND

`lead_source` must be assigned deterministically by the messaging/acquisition system.

The LLM must not guess, infer, rewrite or override this field based on conversation content.

Rules:

- customer sends the first message -> `INBOUND`
- business sends the first outbound campaign message and customer later replies -> `OUTBOUND`

If the runtime genuinely cannot determine the source, the system should preserve the technical uncertainty rather than asking the LLM to guess.

## `source_detail`

Optional operational detail describing the source channel or origin.

Examples:

- WhatsApp inbound
- Meta ad
- property portal
- referral
- outbound contact list
- campaign landing link

This should normally come from system metadata when available.

## `campaign_source`

Optional identifier for the campaign, hook, list, ad, or outreach effort that produced the conversation.

Examples:

- Facebook campaign
- TikTok campaign
- property portal
- referral
- outbound campaign A
- Project A launch October

For outbound leads, preserve the campaign identifier from the outbound sending system when available.

Do not ask the customer for information that is already known from the acquisition channel.

## `first_message_context`

Short description of the original enquiry or outbound hook that started the conversation.

This helps the agent preserve the original reason for the conversation.

---

# 3. Purchase Purpose

## `purchase_purpose`

The customer's main reason for considering property.

Suggested values:

- OWN_STAY
- INVESTMENT
- BOTH
- EXPLORING
- UNKNOWN

Do not force a binary answer when the customer is still exploring.

## `purchase_reason`

Free-text summary of why the customer is looking now.

Examples:

- upgrading from current home
- first property purchase
- looking for rental income
- diversification
- moving closer to work
- buying for children
- retirement planning
- comparing new launches

Only store what is supported by the conversation.

---

# 4. Property Preferences

## `preferred_location`

Location or area preference when known.

May contain:

- city
- neighbourhood
- distance requirement
- workplace or school proximity
- transport preference

## `preferred_property_type`

Examples:

- condominium
- serviced residence
- landed
- studio
- 2-bedroom
- 3-bedroom
- flexible / unknown

## `size_or_layout_preference`

Any stated requirement regarding:

- bedrooms
- bathrooms
- square footage
- dual-key
- balcony
- study room
- family size
- other layout requirements

## `important_features`

Free-text list of features that appear materially important to the customer.

Examples:

- MRT access
- low density
- family facilities
- view
- parking
- pet friendliness
- nearby schools
- furnished unit
- rental-friendly layout

Do not convert casual comments into firm preferences unless they clearly matter to the customer.

---

# 5. Commercial Fit

## `budget_range`

Customer budget when known.

Prefer a range over false precision.

Examples:

- below RM500k
- RM700k-RM900k
- around RM1.2m
- unknown

Do not pressure the customer for budget too early if the conversation does not require it yet.

## `financing_context`

Suggested values:

- LOAN
- CASH
- MIXED
- EXPLORING
- UNKNOWN

This may also include useful notes such as:

- needs loan guidance
- already has banker
- wants monthly instalment estimate
- financing eligibility uncertain

Do not claim financing approval or eligibility unless confirmed by an appropriate source.

## `current_property_status`

Optional context such as:

- first-time buyer
- existing homeowner
- existing investor
- currently renting
- selling another property first
- unknown

This should only be stored when naturally revealed or commercially relevant.

---

# 6. Timing and Readiness

## `purchase_timeline`

When the customer may realistically make a decision or purchase.

Suggested values or summaries:

- immediate
- within 1 month
- within 3 months
- within 6 months
- this year
- just exploring
- no clear timeline

Use the customer's own meaning rather than forcing strict categories when inappropriate.

## `viewing_interest`

Suggested values:

- NONE
- POSSIBLE
- INTERESTED
- REQUESTED

This represents the customer's current openness to a viewing, not whether an appointment is already booked.

## `appointment_readiness`

Suggested values:

- NOT_READY
- DEVELOPING
- READY

`READY` should generally correspond to the sales flow reaching `READY_FOR_APPOINTMENT`.

Do not set `READY` merely because the agent wants to close.

---

# 7. Motivations and Decision Factors

## `primary_motivations`

The strongest reasons that appear to matter to the customer.

Examples:

- investment return
- rental demand
- own-stay convenience
- family lifestyle
- capital appreciation
- affordability
- transport access
- developer reputation
- future development

## `decision_factors`

Specific factors likely to determine whether the customer proceeds.

Examples:

- price must remain below a certain level
- must be near MRT
- needs 3 bedrooms
- needs positive rental case
- needs spouse approval
- comparing against another project

These factors should guide POSITION and HANDLE stages.

## `decision_participants`

Other people materially involved in the purchase decision when known.

Examples:

- spouse
- parents
- business partner
- children
- customer alone

Do not assume that another person is required simply because the customer mentions them.

---

# 8. Concerns and Objections

## `active_concerns`

Current unresolved customer concerns.

Examples:

- price
- location
- oversupply
- maintenance fee
- financing
- developer track record
- rental demand
- traffic
- completion timeline

## `resolved_concerns`

Concerns that have already been addressed sufficiently in the conversation.

The agent should not repeatedly reopen resolved objections unless the customer raises them again.

## `competitor_or_comparison_projects`

Other projects or alternatives the customer is considering when known.

This may help the agent understand the customer's frame of reference.

Do not invent competitor facts when responding.

---

# 9. Sales State

## `sales_stage`

The agent's current working stage in the sales flow.

Allowed values:

- UNDERSTAND
- QUALIFY
- POSITION
- HANDLE
- INTENT
- CLOSE

The stage is directional, not a rigid state machine.

The agent may move forward, backward, or skip stages according to the conversation.

## `intent_level`

Allowed values:

- LOW
- MEDIUM
- HIGH
- READY_FOR_APPOINTMENT

Intent must be based on observed customer behaviour, not optimism.

## `fit_assessment`

A lightweight internal judgment of how well the customer appears to fit the project.

Suggested values:

- UNKNOWN
- WEAK
- POSSIBLE
- GOOD
- STRONG

This is not a score and should not be exposed to the customer.

The agent should avoid overconfidence when important information is still missing.

## `next_objective`

One short internal description of what the agent should try to achieve next.

Examples:

- understand whether this is own stay or investment
- clarify budget because unit fit depends on it
- address concern about rental demand
- position the 2-bedroom unit for investment use
- stop qualifying and move toward viewing

There should normally be one primary next objective, not a list of questions.

---

# 10. Handoff and Follow-up

## `owner`

Who currently owns the live customer conversation.

Suggested values:

- AI
- HUMAN

A handoff changes conversation ownership; it does not create a second customer profile.

## `handoff_status`

Suggested values:

- NONE
- RECOMMENDED
- REQUIRED
- HANDED_OFF

## `handoff_reason`

Short explanation when handoff is recommended or required.

Examples:

- customer requested human agent
- price or promotion requires confirmation
- legal question
- financing question beyond available knowledge
- unusual negotiation
- customer is highly qualified and human involvement may help close

## `last_progress`

Concise description of where the sales conversation has reached.

Examples:

- discussed 3-bedroom investment fit and indicative pricing
- customer compared two layouts and prefers larger unit
- customer asked about current promotion after discussing weekend viewing

This is intended to help a human quickly understand what has already happened without reading the full transcript.

## `next_action`

The most useful operational next step.

Examples:

- confirm latest promotion
- arrange viewing
- answer outstanding unit availability question
- wait for customer after spouse discussion
- continue qualification on financing context

## `follow_up_needed`

Boolean indicator of whether a future follow-up is currently needed.

## `follow_up_context`

What the follow-up should be about.

Examples:

- send confirmed promotion details
- follow up after spouse discussion
- reconnect next month
- share unit availability once confirmed

Do not invent follow-up dates unless the customer or human agent has established them.

---

# 11. Conversation Memory

## `conversation_summary`

A concise rolling summary of the conversation.

It should preserve information that materially affects future replies, including:

- why the customer enquired
- what they want
- important preferences
- buying context
- concerns
- commitments made by the agent
- information still awaiting confirmation
- current momentum of the conversation

Do not turn the summary into a transcript.

## `last_customer_intent`

Short description of what the customer's latest message is trying to achieve.

Examples:

- asking for price
- comparing layouts
- questioning rental demand
- asking for viewing
- casual acknowledgement

## `last_agent_action`

Short description of what the agent last did.

Examples:

- answered pricing question
- asked about purchase purpose
- positioned project for investment
- requested clarification
- suggested viewing

This helps prevent repetitive responses.

---

# Google Sheet Representation

The V1 human-readable CRM may be maintained in one Google Sheet tab named `Leads`.

Both inbound and outbound Leads should use the same tab and the same schema.

Use `lead_source` to distinguish them rather than creating separate inbound and outbound lead tables.

A practical column set may include:

- Lead ID
- Phone
- Name
- Source
- Source Detail
- Campaign
- Purpose
- Budget
- Timeline
- Stage
- Intent
- Need
- Concerns
- Last Progress
- Next Action
- Owner
- Handoff Status
- Handoff Reason
- Last Updated

The `Leads` tab should contain only contacts that have become real Leads through a two-way conversation.

The outbound source/contact list should remain separate from `Leads`.

It may live in another tab or source file such as `Outbound Contacts`.

Sending to an outbound contact must not create a row in `Leads`.

The row should be created only after that contact replies and becomes a Lead.

---

# Unknown, Uncertain and Inferred Information

The agent must distinguish between known facts and interpretations.

Use these principles:

## Known

The customer stated it clearly or the messaging/acquisition system supplied it reliably.

Example:

Customer: "My budget is around RM800k."

Store:

`budget_range = around RM800k`

## Inferred but useful

The conversation strongly suggests something, but the customer has not stated it explicitly.

Example:

Customer repeatedly asks about rental yield, tenant demand and vacancy.

The agent may treat investment as the likely conversation angle, but should avoid permanently converting `purchase_purpose` to INVESTMENT unless the context is sufficiently clear.

## Unknown

No reliable information exists.

Keep the field empty or UNKNOWN.

Never fill unknown fields with assumptions simply to make the profile complete.

---

# Update Rules

The Lead Profile should be updated after every meaningful customer message.

The update should follow this order:

1. Extract any new explicit facts.
2. Update changed preferences or circumstances.
3. Record new concerns or resolve old ones when appropriate.
4. Reassess sales stage.
5. Reassess intent level.
6. Update fit assessment only when new evidence changes it.
7. Set the single most useful next objective.
8. Update `last_progress` and `next_action` when the conversation meaningfully advances.
9. Refresh the conversation summary.

System-controlled metadata such as `lead_source`, technical identifiers, acquisition metadata and conversation ownership must not be rewritten by the LLM unless the runtime explicitly authorises that action.

Do not rewrite stable information unnecessarily.

---

# Contradictions and Changes

Customers may change their mind or correct earlier information.

The most recent clear customer statement should generally replace older information.

Example:

Earlier:

`budget_range = RM700k-RM800k`

Later customer statement:

"Actually I can stretch to RM1m if the unit is right."

Update the budget context accordingly.

Do not preserve contradictory values as if both are equally current.

When the contradiction is unclear, keep the uncertainty and ask only if resolving it matters to the next sales decision.

---

# Do Not Collect for Its Own Sake

The following behaviour is prohibited:

- asking for every missing field
- asking multiple qualification questions in one message simply to complete the profile
- delaying a ready prospect because profile fields are empty
- repeating a question whose answer already exists in the profile
- collecting personal details that do not help the sales conversation
- inferring sensitive information without clear customer disclosure

The Lead Profile supports the conversation.

The conversation does not exist to complete the Lead Profile.

---

# Minimum Useful Profile

There is no mandatory profile completion threshold.

However, a commercially useful conversation will often eventually reveal enough information to understand some combination of:

- purchase purpose
- key need
- budget or affordability context
- preferred property characteristics
- timeline
- major motivation
- major concern
- current intent

The exact combination depends on the customer.

---

# Strong Prospect Rule

If the customer demonstrates strong buying intent, do not continue qualification merely because some profile fields remain unknown.

Examples:

- asks to view the project
- asks which units are still available
- asks what is needed to reserve a unit
- asks about financing for a specific unit
- provides a clear budget and asks for the best matching unit

In these situations:

1. answer the customer's immediate need,
2. update the profile,
3. increase intent when justified,
4. move toward CLOSE or human handoff when appropriate.

---

# Weak Prospect Rule

If the customer is only casually browsing, avoid aggressive qualification.

Provide value first and use one useful question at a time to understand whether a genuine need exists.

Do not treat every enquiry as a high-intent buyer.

---

# Relationship to Other Brain Files

`AGENT.md` defines who the agent is and its overall behaviour.

`SALES_FLOW.md` defines how the agent moves a prospect through the sales process.

`LEAD_PROFILE.md` defines what the agent remembers about the prospect and how that information should be maintained.

The Lead Profile must support the Sales Flow without turning the Sales Flow into a questionnaire.

---

# Final Principle

Remember what matters.

Do not collect what does not matter.

Never ask a question merely because a field is empty.

Use customer information to improve judgment, relevance and timing.

The goal is not a complete profile.

The goal is a better sales conversation.
