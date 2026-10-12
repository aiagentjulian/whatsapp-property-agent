# Sales Core V2 vs Cloudflare Clef + GPT-6 Luna

Run ID: `20261012T073802Z`

Status: **full_completed_with_failures**

## Result

### pilot

Dialogues: 10

- A_SALES_CORE_V2: composite 3.775; dialogues 5; mean turns 1.8.
- B_CLEF_ROUTED: composite 3.95; dialogues 5; mean turns 1.6.
- Paired B − A: 0.175 (95% CI [-0.05, 0.45]); no clear difference; 95% CI includes zero.

#### Blind criterion averages

| Criterion | A: Sales Core V2 | B: Clef routed |
|---|---:|---:|
| intent understanding | 3.8 | 3.8 |
| natural continuation | 3.8 | 4 |
| valuable questions | 4 | 4.2 |
| relevant advantages | 3.8 | 3.8 |
| customer interest | 3.2 | 3.4 |
| non repetition | 4 | 4.8 |
| factual accuracy | 3.8 | 3.4 |
| appropriate pacing | 3.8 | 4.2 |

#### Scenario results

| Scenario | Pairs | A mean | B mean |
|---|---:|---:|---:|
| E01-own-stay-small-family | 1 | 3.0 | 3.375 |
| E05-layout-four-bedrooms | 1 | 4.875 | 4.75 |
| E08-cold-short-replies | 1 | 4.5 | 4.5 |
| E10-viewing-saturday | 1 | 1.5 | 2.125 |
| E20-explicit-need-time | 1 | 5.0 | 5.0 |

#### Reply examples

**E01-own-stay-small-family · A_SALES_CORE_V2 · score 3.0**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home, Pearl Residences’ Phase 1 units are 900 sq. ft., with 3 bedrooms, 2 bathrooms and a balcony. It’s in established Seberang Jaya, with access towards Sunway Carnival Mall and Chai Leng Park. What matters most for your household: the layout, budget, or nearby amenities?

  Later reply: I don’t have a verified current price range, so I don’t want to guess—I’ll check it for you. For the monthly cost, maintenance is RM0.18 per sq. ft. including sinking fund, which works out to about RM162/month for 900 sq. ft. That’s maintenance only, not your loan instalment or other costs. The project information also indicates an approximately 10-acre elevated landscape deck on Level 9. I’ll verify nearby school options and access too, rather than guess.

**E01-own-stay-small-family · B_CLEF_ROUTED · score 3.375**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: Pearl Residences’ Type A could be worth considering: it has 3 bedrooms, 2 bathrooms, a balcony and 900 sq. ft. It’s in an established Seberang Jaya area. Would three bedrooms suit your household, or is having more space a priority?

  Later reply: Maintenance is RM0.18 per sq. ft. including sinking fund, so for a 900 sq. ft. unit it’s about RM162 a month. The monthly loan payment depends on the confirmed price, deposit, loan term and bank rate. I don’t have a verified current price to calculate that honestly, so I’ll check the latest figures. Type A does have a balcony, though I wouldn’t want to promise how airy it feels without checking the layout and orientation.

**E05-layout-four-bedrooms · B_CLEF_ROUTED · score 4.75**

  Customer: We need four bedrooms. Does the project have that layout?

  Agent: Pearl Residences Phase 1 only has a 900 sq. ft. layout with 3 bedrooms and 2 bathrooms, so there isn’t a 4-bedroom option. If four bedrooms is essential, this project may not be the right fit. Is that a firm requirement?

**E05-layout-four-bedrooms · A_SALES_CORE_V2 · score 4.875**

  Customer: We need four bedrooms. Does the project have that layout?

  Agent: No, Pearl Residences Phase 1 only has 3-bedroom, 2-bathroom units, so there isn’t a four-bedroom layout. If four bedrooms is a must, I don’t want to mislead you—this may not be the right fit.

**E08-cold-short-replies · B_CLEF_ROUTED · score 4.5**

  Customer: Can you send me a very short overview? I'm at work.

  Agent: Sure—quick overview: Pearl Residences offers 900 sq ft homes with 3 bedrooms, 2 bathrooms and a balcony. I’ll keep it brief while you’re at work; happy to share more when convenient.

**E08-cold-short-replies · A_SALES_CORE_V2 · score 4.5**

  Customer: Can you send me a very short overview? I'm at work.

  Agent: Sure—quick overview: Pearl Residences offers 900 sq. ft. homes with 3 bedrooms, 2 bathrooms and a balcony.

#### Failures

No provider/schema/judging failures were recorded in this phase.

### full

Dialogues: 180

- A_SALES_CORE_V2: composite 4.315; dialogues 90; mean turns 3.11.
- B_CLEF_ROUTED: composite 2.004; dialogues 90; mean turns 1.23.
- Paired B − A: -2.3111 (95% CI [-2.6347, -1.9417]); A higher; 95% CI excludes zero.

**Comparison is incomplete. Do not interpret the aggregate score or confidence interval as evidence for either arm.**
- 83 of 90 B_CLEF_ROUTED full-phase dialogues could not call Clef after Cloudflare returned HTTP 429 for its exhausted daily free Neurons allocation.
- Four Customer Simulator calls returned incomplete JSON (two A and two B dialogues).
- The run used a pre-fix A prompt containing an empty Clef-hypothesis field; exact A prompt parity was not complete.

#### Blind criterion averages

| Criterion | A: Sales Core V2 | B: Clef routed |
|---|---:|---:|
| intent understanding | 4.511 | 1.378 |
| natural continuation | 4.311 | 1.344 |
| valuable questions | 4.544 | 2.044 |
| relevant advantages | 4.478 | 2.033 |
| customer interest | 4.033 | 1.344 |
| non repetition | 4.067 | 3.522 |
| factual accuracy | 4.033 | 2.733 |
| appropriate pacing | 4.544 | 1.633 |

#### Scenario results

| Scenario | Pairs | A mean | B mean |
|---|---:|---:|---:|
| E01-own-stay-small-family | 3 | 3.458 | 3.792 |
| E02-first-home-unsure | 3 | 4.25 | 4.667 |
| E03-investment-yield | 3 | 4.417 | 2.5 |
| E04-tight-budget | 3 | 4.417 | 1.667 |
| E05-layout-four-bedrooms | 3 | 4.667 | 1.917 |
| E06-location-commute | 3 | 3.917 | 1.417 |
| E07-objection-school-claims | 3 | 4.792 | 1.542 |
| E08-cold-short-replies | 3 | 4.667 | 2.417 |
| E09-vague-more-info | 3 | 3.083 | 1.5 |
| E10-viewing-saturday | 3 | 2.125 | 1.667 |
| E11-followup-after-spouse | 3 | 4.542 | 1.708 |
| E12-change-from-investment | 3 | 4.583 | 1.667 |
| E13-maintenance-fee | 3 | 4.667 | 1.708 |
| E14-price-after-rebate | 3 | 4.0 | 1.625 |
| E15-facility-overload | 3 | 4.25 | 1.667 |
| E16-privacy-and-crowding | 3 | 4.792 | 1.375 |
| E17-financing-anxiety | 3 | 4.75 | 1.75 |
| E18-no-children-assumption | 3 | 4.208 | 1.792 |
| E19-confused-acknowledgement | 3 | 4.875 | 4.0 |
| E20-explicit-need-time | 3 | 5.0 | 3.542 |
| E21-technical-waterproofing | 3 | 4.583 | 1.625 |
| E22-green-design | 3 | 4.167 | 1.417 |
| E23-compare-projects | 3 | 4.708 | 1.625 |
| E24-investor-short-stay | 3 | 4.917 | 1.5 |
| E25-unit-facing | 3 | 4.125 | 1.542 |
| E26-late-journey-question | 3 | 4.125 | 1.375 |
| E27-decision-maker-spouse | 3 | 4.708 | 1.833 |
| E28-skeptical-salesperson | 3 | 4.292 | 2.083 |
| E29-requirements-shift | 3 | 4.542 | 1.583 |
| E30-ready-but-no-pressure | 3 | 3.833 | 1.625 |

#### Reply examples

**E01-own-stay-small-family · B_CLEF_ROUTED · score 4.125**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: Pearl Residences has a 900 sq ft layout with 3 bedrooms, 2 bathrooms and a balcony. It could suit a family looking for three separate bedrooms around Seberang Jaya, though whether the space feels right depends on your household’s needs. What matters most to you in a home there?

  Later reply: The maintenance rate is RM0.18 per sq ft, inclusive of sinking fund—about RM162/month for the 900 sq ft unit. I don’t have a verified current selling price or nearby everyday-shop details, so I’ll get those checked. One relevant point: a 25-storey MOE school for SK and SMK is planned, with completion expected alongside Phase 1.

**E01-own-stay-small-family · A_SALES_CORE_V2 · score 3.5**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home around Seberang Jaya, Pearl Residences’ Phase 1 Type A could be a useful starting point: 900 sq. ft., with 3 bedrooms, 2 bathrooms and a balcony. It’s in an established area with connections toward Sunway Carnival Mall and Chai Leng Park. What matters most to your household: bedroom space or everyday convenience?

  Later reply: The school option I can confirm is a planned MOE school within the development, intended for both SK and SMK, with a covered walkway connection. It’s expected to be completed with Phase 1, so it isn’t an existing school yet. For the monthly instalment, it depends on the current unit price and loan terms—I’ll check a reliable indicative estimate rather than guess.

**E01-own-stay-small-family · B_CLEF_ROUTED · score 3.375**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: Hi! Pearl Residences in Seberang Jaya offers a 900 sq. ft. layout with 3 bedrooms, 2 bathrooms and a balcony. It could be worth considering if that setup suits your household. Would 3 bedrooms work for you?

  Later reply: For the 900 sq. ft. unit, maintenance is about RM162/month (RM0.18 × 900 sq. ft.), inclusive of the sinking fund. That’s separate from utilities and any loan instalment, which depends on the unit price and financing terms. I don’t have verified school and shop distances to hand, so I’ll check rather than guess.

**E01-own-stay-small-family · A_SALES_CORE_V2 · score 3.75**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home around Seberang Jaya, Pearl Residences could be worth considering: the Phase 1 homes are 900 sq. ft., with 3 bedrooms, 2 bathrooms and a balcony. It’s in an established area, with Sunway Carnival Mall and Chai Leng Park nearby. Would a 3-bedroom layout work for your household, or are you looking for more space?

  Later reply: A 3-bedroom layout sounds like it could work for you. The school information I can confirm is a planned MOE school within the development, described as accommodating both SK and SMK, with a covered walkway connection. It’s expected to be completed alongside Phase 1. I don’t have verified names for other nearby schools or current pricing to estimate a monthly payment, so I’ll check those rather than guess. Any payment estimate will depend on the price and financing assumptions.

**E01-own-stay-small-family · A_SALES_CORE_V2 · score 3.125**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: Hi! Pearl Residences could be worth considering for a family home around Seberang Jaya. Phase 1 units are 900 sq. ft. with 3 bedrooms, 2 bathrooms and a balcony, in an established area with access to Sunway Carnival Mall and the wider Butterworth network. Would a 3-bedroom layout suit your household?

  Later reply: Glad a 3-bedroom should work for the four of you. The confirmed maintenance rate is RM0.18 per sq. ft. per month, inclusive of sinking fund; utilities and any loan repayment are separate. I can’t give a reliable all-in monthly estimate without current unit pricing and financing details. I’ll check which schools are nearby and their approximate distances.

**E01-own-stay-small-family · B_CLEF_ROUTED · score 3.875**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home around Seberang Jaya, Pearl Residences could be worth considering: its Phase 1 homes are 900 sq. ft., with 3 bedrooms, 2 bathrooms and a balcony. Would that layout suit your household, or are you looking for more space?

  Later reply: Good to hear the 3-bedroom layout may work for your family. The project plan shows an approximately 10-acre elevated landscape deck on Level 9, with the residents’ landscaped area separated from the pay-per-use clubhouse. I don’t have verified current pricing, monthly cost estimates or nearby school details to quote, so I’ll get those checked rather than guess.

#### Failures

- `E01-own-stay-small-family` / `B_CLEF_ROUTED` / `customer_simulator_error`: complete. Full original transcript is in the JSON report.
- `E02-first-home-unsure` / `B_CLEF_ROUTED` / `customer_simulator_error`: complete. Full original transcript is in the JSON report.
- `E03-investment-yield` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (545f2b35-41b1-4f1d-8de8-38ef21371f04)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E03-investment-yield` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (bb15e427-eba0-411d-9981-70179f51d79f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E04-tight-budget` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (f1ded4d0-293e-45eb-8f5c-c63af5a5995b)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E04-tight-budget` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (bdf0c8bc-ed04-4d50-acfa-553994824b33)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E04-tight-budget` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (14a5c50e-bc4b-4477-a2ce-c9ea28ce664f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E05-layout-four-bedrooms` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (5c555ddc-886c-451e-a2cf-54044be4e0bd)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E05-layout-four-bedrooms` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (66f83ea5-5402-444c-9732-6fcce6da01fa)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E05-layout-four-bedrooms` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (d0036299-b30f-4267-b13d-82711deb1d0a)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E06-location-commute` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (81bc2389-c143-41cf-8d89-52370459277c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E06-location-commute` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (c8b3fc93-c89d-4612-954e-ce678d56996d)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E06-location-commute` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (66d4baf4-b2da-4a73-8271-94b9be1778ba)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E07-objection-school-claims` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (11dee7e7-1036-4d15-8ec4-f9ee1e16edb5)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E07-objection-school-claims` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (956f55ba-6147-4910-9ae0-376661341aaf)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E07-objection-school-claims` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (7721137f-36c7-4f1b-b2d4-1fd534044bf2)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E08-cold-short-replies` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (39f383e9-5aa4-40ab-bd06-0bd8fa6ad26f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E08-cold-short-replies` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (e92fb32c-79ce-44cd-9638-3e96711ea355)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E08-cold-short-replies` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9f342b7a-5295-4e37-bbf9-012ff46f9f17)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E09-vague-more-info` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (ced5550d-4feb-49d4-ac3b-13bcae812eaa)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E09-vague-more-info` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (25a4ac1c-4657-4e48-9379-52a6a9b5e53e)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E09-vague-more-info` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (1f214a6e-60ac-4f7b-861d-fb33ab021dae)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E10-viewing-saturday` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (c2a85663-1125-440a-8897-613872c78014)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E10-viewing-saturday` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (749e1ff9-2358-4d89-ade7-9de8772aa6bf)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E10-viewing-saturday` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (74b313f8-783f-4477-853c-6c6333ad3aa3)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E11-followup-after-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (ad2c4a2a-0889-4aec-98f4-80e8eb4b953b)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E11-followup-after-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (482e610f-6c06-4bdb-9424-157f91c01e44)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E11-followup-after-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (00b319e7-ed5f-492b-9e46-45da46422731)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E12-change-from-investment` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (5b040455-a93b-403f-8e3c-1e296d8b5c7b)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E12-change-from-investment` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (d4b8958b-c71d-4811-a758-dc6dd7ad63fb)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E12-change-from-investment` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (e8145490-f9c9-4713-b416-760bd29dc4bb)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E13-maintenance-fee` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (c657df02-068e-41c3-97d4-61c5e68ffb1c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E13-maintenance-fee` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (731f68b2-7171-4898-9f3b-1089619ce44d)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E13-maintenance-fee` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9e81dd75-571b-422e-b724-f1283797f8dd)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E14-price-after-rebate` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9a42db50-7099-44c7-b2ef-abca6cdf2aed)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E14-price-after-rebate` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (706182d5-2511-4d94-ad8f-ad2b6c62ec31)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E14-price-after-rebate` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (dcd38411-3ff7-46bc-b68b-1aa14aa5da6f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E15-facility-overload` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (3b841fee-0f3a-425c-9657-45a2580a4d8f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E15-facility-overload` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (365825ad-63d4-4e76-b194-205f29c976d6)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E15-facility-overload` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (618e05e1-35d9-4436-b31f-288d44985591)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E16-privacy-and-crowding` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (d9f73b6c-4148-4a4e-9477-7a2a72363893)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E16-privacy-and-crowding` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (f32319af-3dc7-40c8-9812-32740df55dc3)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E16-privacy-and-crowding` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (aa38e163-1d19-4c9b-a280-dc008035da55)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E17-financing-anxiety` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (270e3370-c9c0-4a17-9441-b85e431dd6d4)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E17-financing-anxiety` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (1de9c994-6e0d-4017-a25d-d2bfc7b29e97)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E17-financing-anxiety` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (b327fb29-b366-4111-b7ce-4653954583ae)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E18-no-children-assumption` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (a6ce7c68-462c-4d01-a12b-0d40db68af45)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E18-no-children-assumption` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (dd753c41-a9f9-4080-8dd2-f977229def03)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E18-no-children-assumption` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (c6a99d8f-1641-4b8e-a2a8-f29b13b2748c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E19-confused-acknowledgement` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (88941617-afab-4171-a182-88453f176165)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E19-confused-acknowledgement` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (af27cc44-56b5-41a6-8ebf-811b53218933)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E19-confused-acknowledgement` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (b9e79ab6-eef9-4cf5-b367-c61724efb2ba)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E20-explicit-need-time` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (3fe09842-cb84-48b5-85b1-91e2d49dfc33)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E20-explicit-need-time` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9d9f884d-1c3c-4ce3-914a-e8630e8081f2)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E20-explicit-need-time` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (0a9657cd-024f-4c9e-8a8f-2f1399bf3a8c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E21-technical-waterproofing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (6461c7ec-e190-4268-a725-d79b89e698fb)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E21-technical-waterproofing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (93ee0104-cf04-495a-8f45-79f445a89ee6)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E21-technical-waterproofing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (33cc5df6-dfde-4cd6-8df5-93c41a3b1832)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E22-green-design` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (1e80db2f-ed0b-49c3-a0e4-5a8bfffd82bd)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E22-green-design` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (558dc7f8-63fe-4912-a3d0-bb8aed2fe11f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E22-green-design` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9240cf76-83bf-48d6-ae36-28d81523064a)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E23-compare-projects` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (0075dfe0-b678-4765-b7f8-60db73c2fa9f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E23-compare-projects` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (4d5048f1-0d85-42fb-9666-63cb92644012)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E23-compare-projects` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (f022bdb1-99b8-4769-8785-f1f7c5ec5205)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E24-investor-short-stay` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9717ab92-cb76-457a-9044-4301f3f6a89a)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E24-investor-short-stay` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (bd478b96-fdec-493c-8a51-2c415a1fdefd)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E24-investor-short-stay` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (0cd7c416-c357-4b33-a2d1-52710de70af3)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E25-unit-facing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (77d52a4b-0416-4ba6-a6f1-22477fb541ee)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E25-unit-facing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (e37e2b3f-30b8-4d7c-8074-0e0a216d4b52)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E25-unit-facing` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (9ac05666-40bb-407a-8777-2ffbcec30c2d)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E26-late-journey-question` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (6847ab41-25d9-407e-a559-0c36d81d78a4)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E26-late-journey-question` / `A_SALES_CORE_V2` / `customer_simulator_error`: complete. Full original transcript is in the JSON report.
- `E26-late-journey-question` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (e0fa3809-3725-4a1e-a867-80f289bec5db)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E26-late-journey-question` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (232cbaf9-c4df-4358-98a3-1c3574b0f109)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E26-late-journey-question` / `A_SALES_CORE_V2` / `customer_simulator_error`: complete. Full original transcript is in the JSON report.
- `E27-decision-maker-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (f810c001-f804-47b9-a1aa-044e60e7423c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E27-decision-maker-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (99ae1670-767c-4af7-91c3-11d4e8f79048)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E27-decision-maker-spouse` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (86381e2d-57e7-47d7-aa02-e17ecee5a02c)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E28-skeptical-salesperson` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (f5a43555-d270-4f94-8568-defe935b4575)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E28-skeptical-salesperson` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (03c798f8-dc62-48b1-aaf1-bb2ffff8b132)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E28-skeptical-salesperson` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (268a5435-5752-42c8-8cd4-2ddc74582f67)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E29-requirements-shift` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (0263c120-8dec-4a62-aac1-c062a6e5fb45)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E29-requirements-shift` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (27afea51-bd63-4947-8162-a04ae0d2b0db)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E29-requirements-shift` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (16ac3657-0367-43d5-bf80-c3553229b2ce)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E30-ready-but-no-pressure` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (ac188051-2c7d-4a67-be16-c6dd6a074e2f)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E30-ready-but-no-pressure` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (c1bd9642-da36-4643-b446-888a3b134b44)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.
- `E30-ready-but-no-pressure` / `B_CLEF_ROUTED` / `agent_error`: {'type': 'RuntimeError', 'message': 'Cloudflare Clef API failed (HTTP 429): {"errors":[{"message":"AiError: AiError: you have used up your daily free allocation of 10,000 neurons, please upgrade to Cloudflare\'s Workers Paid plan if you would like to continue usage. (d30f2b10-3af6-4352-bfd7-34b92170583a)","code":4006}],"success":false,"result":{},"messages":[]}'}. Full original transcript is in the JSON report.

## Protocol caveat

The run was launched before the final parity fix; A included an empty clef_routing_hypotheses:null field. The existing Sales Core V2 system prompt/model/schema/retrieval stayed the same, but exact user-prompt parity was not complete. The code now omits this field entirely from A.

## Usage

```json
{"openai_model":"gpt-6-luna","openai_calls":830,"openai_input_tokens":4830311,"openai_output_tokens":534972,"openai_cost_usd_estimate":0.750517,"openai_cost_cap_usd":10.0,"clef_cost_usd_estimate":0.074439,"prior_attempt_cost_usd_estimate":0.064174,"combined_cost_usd_estimate":0.88913,"openai_latency_ms_mean":8063,"openai_latency_ms_median":7017,"openai_by_role":{"sales_agent":{"calls":325,"input_tokens":792568,"output_tokens":252778,"latency_ms_mean":9721,"latency_ms_median":8710},"customer_simulator":{"calls":315,"input_tokens":156206,"output_tokens":62061,"latency_ms_mean":3767,"latency_ms_median":3530},"blind_evaluator":{"calls":190,"input_tokens":3881537,"output_tokens":220133,"latency_ms_mean":12351,"latency_ms_median":11722}},"clef_model":"@cf/cloudflare/clef","clef_calls":120,"clef_input_tokens_reported_or_conservative_estimate":310161,"clef_neurons_reported_or_estimate":6785,"prior_attempt_neurons":2098,"combined_clef_neurons_reported_or_estimate":8883,"clef_neuron_cap":100000,"clef_latency_ms_mean":1440,"clef_latency_ms_median":1420,"clef_successful_calls":37,"clef_failed_calls":83,"prior_attempt_clef_calls":12,"all_attempts_clef_calls":132}
```

## Recommendation

Retain Sales Core V2 for now. The five-scenario pilot is inconclusive. The full phase recorded 180 dialogue attempts, but 83 Clef-routed B dialogues failed on Cloudflare HTTP 429 after the daily free Neurons allocation was exhausted; four simulator calls also failed. The full A/B score gap and interval are invalid, and the run used an A prompt with an empty Clef field. Do not integrate Clef or claim A is superior from these results.

All dialogue transcripts, route traces, blind scores, and evidence are in the sibling JSON report. Scores are model-based blind judgments and should be read as evidence, not proof of a production lift.
