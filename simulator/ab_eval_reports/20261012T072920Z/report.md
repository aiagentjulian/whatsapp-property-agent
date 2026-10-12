# Sales Core V2 vs Cloudflare Clef + GPT-6 Luna

Run ID: `20261012T072920Z`

Status: **complete**

## Result

### pilot

Dialogues: 10

- A_SALES_CORE_V2: composite 3.562; dialogues 4; mean turns 1.
- B_CLEF_ROUTED: composite 4.094; dialogues 4; mean turns 1.
- Paired B − A: 0.5312 (95% CI [-0.0625, 1.3125]); no clear difference; 95% CI includes zero.

#### Blind criterion averages

| Criterion | A: Sales Core V2 | B: Clef routed |
|---|---:|---:|
| intent understanding | 3.75 | 4 |
| natural continuation | 3.5 | 4 |
| valuable questions | 3.25 | 4.5 |
| relevant advantages | 4 | 4.25 |
| customer interest | 3.25 | 3.75 |
| non repetition | 3.75 | 4.5 |
| factual accuracy | 3.5 | 3.75 |
| appropriate pacing | 3.5 | 4 |

#### Scenario results

| Scenario | Pairs | A mean | B mean |
|---|---:|---:|---:|
| E01-own-stay-small-family | 1 | None | None |
| E05-layout-four-bedrooms | 1 | 3.125 | 4.875 |
| E08-cold-short-replies | 1 | 4.625 | 4.5 |
| E10-viewing-saturday | 1 | 1.5 | 2.0 |
| E20-explicit-need-time | 1 | 5.0 | 5.0 |

#### Reply examples

**E01-own-stay-small-family · A_SALES_CORE_V2 · score None**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home around Seberang Jaya, Pearl Residences could be worth considering. Phase 1 homes are 900 sq. ft., with 3 bedrooms, 2 bathrooms and a balcony, in an established urban area. Is having enough room at home your main priority, or is being near work or family more important?

  Later reply: Three bedrooms matches the Pearl Residences layout. There’s a planned SK/SMK school within the development, expected to be completed alongside Phase 1. I’ll check the latest price range and a realistic monthly estimate—instalments depend on the loan terms and eligibility, so I don’t want to guess. I also don’t have verified details on nearby everyday shops yet.

**E01-own-stay-small-family · B_CLEF_ROUTED · score None**

  Customer: Hi, we're looking for a family home around Seberang Jaya. What might suit us?

  Agent: For a family home around Seberang Jaya, Pearl Residences may be worth considering. Phase 1 has a 900 sq. ft. layout with 3 bedrooms, 2 bathrooms and a balcony. Would that size work for your household, or are you looking for more space?

  Later reply: For daily shopping, the project materials point to Sunway Carnival Mall and Chai Leng Park, though I don’t have verified distances to quote. I don’t have a confirmed nearby-school list either. I’d rather not guess the monthly instalment without current pricing and financing assumptions, so I’ll check an up-to-date estimate and the school information for you.

**E05-layout-four-bedrooms · B_CLEF_ROUTED · score 4.875**

  Customer: We need four bedrooms. Does the project have that layout?

  Agent: No—Pearl Residences’ Phase 1 units are all 3-bedroom, 2-bathroom layouts, so they wouldn’t meet your four-bedroom requirement.

**E05-layout-four-bedrooms · A_SALES_CORE_V2 · score 3.125**

  Customer: We need four bedrooms. Does the project have that layout?

  Agent: Pearl Residences Phase 1 doesn’t have a four-bedroom layout; the units are 900 sq. ft. with three bedrooms and two bathrooms. If four bedrooms is essential, it won’t match your requirement. Would three bedrooms still be worth considering, or is four a must-have?

**E08-cold-short-replies · B_CLEF_ROUTED · score 4.5**

  Customer: Can you send me a very short overview? I'm at work.

  Agent: Sure — Pearl Residences offers 900 sq. ft. homes with 3 bedrooms, 2 bathrooms and a balcony. That’s the quick overview for now.

**E08-cold-short-replies · A_SALES_CORE_V2 · score 4.625**

  Customer: Can you send me a very short overview? I'm at work.

  Agent: Sure—quick overview: Pearl Residences’ Phase 1 homes are 900 sq ft, with 3 bedrooms, 2 bathrooms and a balcony.

#### Failures

- `E01-own-stay-small-family` / `A_SALES_CORE_V2` / `customer_ended`: {'type': 'RuntimeError', 'message': 'GPT-6 Luna JSON response did not complete.'}. Full original transcript is in the JSON report.
- `E01-own-stay-small-family` / `B_CLEF_ROUTED` / `customer_ended`: {'type': 'RuntimeError', 'message': 'GPT-6 Luna JSON response did not complete.'}. Full original transcript is in the JSON report.

## Usage

```json
{"openai_model":"gpt-6-luna","openai_calls":46,"openai_input_tokens":263948,"openai_output_tokens":29578,"openai_cost_usd_estimate":0.041184,"openai_cost_cap_usd":10.0,"clef_cost_usd_estimate":0.02299,"combined_cost_usd_estimate":0.064174,"openai_latency_ms_mean":8297,"openai_latency_ms_median":6686,"openai_by_role":{"sales_agent":{"calls":19,"input_tokens":49465,"output_tokens":16605,"latency_ms_mean":11024,"latency_ms_median":10152},"customer_simulator":{"calls":17,"input_tokens":9897,"output_tokens":4053,"latency_ms_mean":3896,"latency_ms_median":4394},"blind_evaluator":{"calls":10,"input_tokens":204586,"output_tokens":8920,"latency_ms_mean":10600,"latency_ms_median":9242}},"clef_model":"@cf/cloudflare/clef","clef_calls":12,"clef_input_tokens_reported_or_conservative_estimate":95792,"clef_neurons_reported_or_estimate":2098,"clef_neuron_cap":100000,"clef_latency_ms_mean":1620,"clef_latency_ms_median":1407}
```

## Recommendation

Pilot evidence only; no integration recommendation is justified until the 30-scenario paired evaluation completes.

All dialogue transcripts, route traces, blind scores, and evidence are in the sibling JSON report. Scores are model-based blind judgments and should be read as evidence, not proof of a production lift.
