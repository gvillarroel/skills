# Deterministic Pi cost-elasticity simulation

This bundle is an offline arithmetic simulation. It made **zero real Pi, Copilot, or model API calls**. Provider costs are token-list-price value; they are not necessarily incremental cash on a prepaid plan.

## Canonical one-million-execution deltas

| Contrast | Luna | Terra | Sol |
|---|---:|---:|---:|
| +1k stable system tokens, 10 calls | $430.00 | $4,300.00 | $8,600.00 |
| +1k uncached system tokens, 10 calls | $2,000.00 | $20,000.00 | $40,000.00 |
| +1k crossing threshold, cold | $50,975.00 | $689,750.00 | $1,377,500.00 |
| fifth sequential tool | $1,813.00 | $18,130.00 | $35,860.00 |
| fifth batched tool | $645.00 | $6,450.00 | $12,500.00 |
| prefix churn, 10 calls | $103,500.00 | $1,035,000.00 | $2,070,000.00 |

## Long-session strategies

The fixed workload has 39 main calls and grows logically from a 40k prompt to 800k without compaction. The 200k strategy inserts an uncached summary call and cold-writes a 40k prompt after every compaction. It therefore includes the cost of cache loss rather than assuming compaction is free.

| Model | No compaction / execution | Cap 200k / execution | Savings / execution | Compactions |
|---|---:|---:|---:|---:|
| Luna | $1.020400 | $0.595200 | $0.425200 | 4 |
| Terra | $9.904000 | $5.952000 | $3.952000 | 4 |
| Sol | $19.598000 | $11.428000 | $8.170000 | 4 |

## Interpretation boundaries

- Luna uses the GitHub Copilot 200k boundary; Terra and Sol use 272k.
- The 800k path is conditional cost arithmetic, not a claim that every Pi/Copilot integration accepts an 800k prompt.
- Fixed-model Pi routing receives no assumed automatic-model discount.
- Compaction can lose useful information. `break-even.csv` converts provider savings into both a per-execution failure threshold and an independent per-compaction failure threshold.
- `scale-results.csv` multiplies one deterministic execution by 1,000 and 1,000,000; it does not fabricate one million observations.

Rate source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
