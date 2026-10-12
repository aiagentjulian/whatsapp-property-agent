# Sales Core V2/V3 paired evaluation

- Run: DRYRUN-SALES-CORE-V3-FINAL-D
- Status: COMPLETED (10/10 pairs)
- Model: gpt-6-luna / high

## Scenario outcomes

| Scenario | Pair | V2 turns | V3 turns | Winner |
|---|---|---:|---:|---|
| SCV3-01 Family buying for own stay | COMPLETED | 2 | 2 | TIE |
| SCV3-02 First-time buyer unsure of priorities | COMPLETED | 2 | 2 | TIE |
| SCV3-03 Budget constraints and price concern | COMPLETED | 2 | 2 | TIE |
| SCV3-04 Investor asking about rental return | COMPLETED | 2 | 2 | TIE |
| SCV3-05 Layout requirement and mismatch | COMPLETED | 2 | 2 | TIE |
| SCV3-06 Location and commuting | COMPLETED | 2 | 2 | TIE |
| SCV3-07 Safety, flood and infrastructure concerns | COMPLETED | 2 | 2 | TIE |
| SCV3-08 Cold and hesitant customer | COMPLETED | 2 | 2 | TIE |
| SCV3-09 Changing requirement and returning question | COMPLETED | 2 | 2 | TIE |
| SCV3-10 High intent, sensitive to pressure | COMPLETED | 2 | 2 | TIE |

## Paired blind scores

| Dimension | V2 | V3 |
|---|---:|---:|
| customer_understanding | 3.0 | 3.0 |
| contextual_continuity | 3.0 | 3.0 |
| sales_judgment | 3.0 | 3.0 |
| value_relevance | 3.0 | 3.0 |
| question_quality | 3.0 | 3.0 |
| objection_handling | 3.0 | 3.0 |
| repetition_control | 3.0 | 3.0 |
| factual_accuracy | 3.0 | 3.0 |
| viewing_timing | 3.0 | 3.0 |
| interest_without_pressure | 3.0 | 3.0 |
| naturalness | 3.0 | 3.0 |

## Usage

```json
{
  "model_calls": 90,
  "calls_by_role": {
    "sales_v2": 20,
    "customer_simulator": 20,
    "sales_strategy": 20,
    "sales_v3": 20,
    "blind_judge": 10
  },
  "failed_or_incomplete_calls": 0,
  "latency_seconds_total": 0.0,
  "latency_seconds_mean": 0.0,
  "tokens": {
    "input_tokens": 1080,
    "cached_tokens": 0,
    "output_tokens": 540,
    "total_tokens": 1620
  },
  "estimated_standard_usd": null,
  "cost_basis": "Dry-run synthetic usage; no charges."
}
```

## Transcript evidence

### SCV3-01 — Family buying for own stay (TIE)

dry-run transport check


### SCV3-02 — First-time buyer unsure of priorities (TIE)

dry-run transport check


### SCV3-03 — Budget constraints and price concern (TIE)

dry-run transport check


### SCV3-04 — Investor asking about rental return (TIE)

dry-run transport check


### SCV3-05 — Layout requirement and mismatch (TIE)

dry-run transport check


### SCV3-06 — Location and commuting (TIE)

dry-run transport check


### SCV3-07 — Safety, flood and infrastructure concerns (TIE)

dry-run transport check


### SCV3-08 — Cold and hesitant customer (TIE)

dry-run transport check


### SCV3-09 — Changing requirement and returning question (TIE)

dry-run transport check


### SCV3-10 — High intent, sensitive to pressure (TIE)

dry-run transport check


