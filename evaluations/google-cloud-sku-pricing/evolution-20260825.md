# Google Cloud SKU pricing evaluation and evolution — 2026-08-25

## Outcome

The Google Cloud Pricing API can provide services, SKU metadata, geographic
taxonomy, public list prices, consumption models, units, and price tiers
programmatically. Billing-account endpoints and the BigQuery pricing export can
also expose account-specific prices when the caller has the required account
permissions.

This study produced a reusable `google-cloud-sku-pricing` skill, a complete live
USD catalog snapshot, a 100-question SQLite benchmark, a strict verifier, and a
BigQuery regional comparison query. The final runtime skill retained its
original `SKILL.md` and deterministic helper because every completed baseline
evaluation was exact and no evolved instruction candidate demonstrated a
strict improvement. A proposed tie was not promoted. The BigQuery reference was
extended separately and passed a final isolated SQL-generation smoke test.

## API snapshot

Snapshot `gcp-pricing-636387a8dd1a10dc` was retrieved from the v2beta API from
2026-08-26T01:26:56Z through 2026-08-26T01:29:04Z. Pagination completed for all
three public collections.

| Collection or normalized table | Rows |
| --- | ---: |
| Services | 1,776 |
| SKUs | 102,518 |
| Public price resources | 102,518 |
| Consumption-model price rows | 157,646 |
| Price tiers | 167,737 |
| SKU-region rows | 96,265 |
| Product-taxonomy rows | 572,599 |

The raw API pages, normalized catalog database, benchmark database, generated
tasks, and run logs are intentionally ignored by Git. Checked-in manifests
record endpoint, pagination, timestamps, counts, and SHA-256 digests without
including credentials or canonical answers.

Official contracts used by the implementation:

- Pricing API overview:
  https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest
- Public price enumeration:
  https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/skus.prices/list
- SKU and geographic taxonomy:
  https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/skus
- Billing-account prices:
  https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/billingAccounts.skus.prices/list
- BigQuery pricing-export schema:
  https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/pricing-data

## Benchmark contract

The primary benchmark contains 100 questions: ten examples in each of ten
families.

1. Geography type and regions.
2. SKU and service identity.
3. Consumption-model inventory.
4. Public list rate at a usage amount.
5. Price normalized per base unit.
6. Marginal tier at an exact boundary or interior amount.
7. Progressive tiered cost.
8. Explicit regional membership.
9. Exact catalog counts with service, region, and taxonomy filters.
10. Compatible SKU comparison and cheapest-rate selection.

Each prompt has a strict structured answer. Decimal values are plain-decimal
JSON strings, and the verifier rejects missing or extra fields, wrong ordering,
duplicate IDs, binary-float artifacts, and any value mismatch. The split is 60
training questions, 20 validation questions, and 20 holdout questions.

Revision v2 preserves all 80 development questions and replaces the 20 v1
holdout questions with seed `20260826`. Before generation, it reserves every
SKU named by any v1 question. The resulting v2 holdout has zero exact-prompt
overlap and zero named-SKU overlap with v1. Across v1 and v2 there are 120 unique
prompts; the deterministic regression suite executes all 200 benchmark rows.

## Results

| Gate | Runtime | Result | Disposition |
| --- | --- | ---: | --- |
| Runtime-helper reproduction, v1 | Python/SQLite/Decimal | 100/100 | Pass |
| Runtime-helper reproduction, v2 | Python/SQLite/Decimal | 100/100 | Pass |
| Initial isolated agent smoke | `openai-codex/gpt-5.3-codex-spark` | 10/10 | Pass |
| Evolution v4 answer evaluations | Spark + Harbor 0.18.0 + GEPA 0.1.2 | 180/180 | Rejected as a sealed evolution gate |
| Evolution v5 answer evaluations | Spark + Harbor 0.18.0 + GEPA 0.1.2 | 80/180 | Infrastructure failure; rejected |
| Fresh v2 direct holdout | `openai-codex/gpt-5.4-mini` | 20/20 | Pass |
| Final-bundle SQL generation | `openai-codex/gpt-5.4-mini` | Required SQL contract present | Pass |

The direct holdout audit found no model errors, no forbidden network access, no
read outside either task workspace, one `answers.json` write per task, and exact
skill-bundle digests across both tasks. Both strict verifiers returned reward
1.0. The final SQL smoke read only the installed skill and its BigQuery
reference and generated a non-empty query containing the latest snapshot,
regions, consumption models, marginal tier selection, unit quantity, normalized
USD rate, compatibility partition, and effective time.

The Spark-to-`gpt-5.4-mini` substitution is an explicit infrastructure
deviation. Spark reached its account usage limit before the v2 holdout began.
An OpenRouter attempt returned HTTP 402 because that account had no credits, and
the configured Gemini credential was rejected. The alternative model used the
same frozen skill and workspace contract and never received evaluator data.

## Evolution audit and final decision

The first complete evolution run, v4, reported perfect development and holdout
scores. It was rejected after a post-run audit showed that the reflection model
used ambient tools and inspected the original holdout prompts. It did not read
the canonical holdout answers, but prompt visibility alone invalidates a sealed
holdout. That discovery caused the v2 holdout to be generated.

For v5, reflection was hardened with `--no-tools`. The audit confirms zero v2
holdout tokens in all reflection prompts, responses, summaries, and JSON event
logs, and zero reflection tool events. GEPA's best validation score was 1.0.
One proposed instruction mutation tied the baseline and was skipped; the
selected candidate normalized to the same `SKILL.md` as the frozen baseline.

Spark then reached its usage limit. Eight task executions had already produced
80 exact answers. The remaining two development executions and all eight
holdout attempts emitted model error events and no `answers.json`. The upstream
runner recorded those verifier failures as zero rewards but did not count them
as execution errors, so its zero-minimum-gain rule incorrectly labeled a 0.0 to
0.0 tie as `PROMOTE`.

`audit_evolution.py` now fails closed on model error events, missing output,
verifier findings, incomplete question coverage, non-perfect holdout scores,
reflection tool use, or holdout-token leakage. It correctly classifies v5 as an
unsafe promotion. No v4 or v5 candidate was copied into the source skill.

The retained baseline subsequently scored 20/20 on the disjoint v2 holdout.
Because it was already at the benchmark ceiling and every proposed candidate
was either identical or tied, retaining the verified baseline is the only
evidence-supported evolution outcome. Future work must create a v3 holdout;
v2 has now been opened and must never be reused for candidate selection.

## Regional SQL behavior

The Pricing API does not take a region selector on the price-list call. Region
is SKU metadata, so callers must enumerate SKUs and prices, join on SKU ID, and
compare only compatible product candidates. The SQL in
`references/bigquery-sql.md` applies the same contract to
`cloud_pricing_export`:

- select the latest complete pricing snapshot;
- expand geographic regions, consumption models, and all tiers;
- choose the greatest tier start not exceeding the requested usage;
- divide by `pricing_unit_quantity` only for a requested base-unit rate;
- partition ranks by consumption model, pricing unit, and unit quantity;
- retain SKU ID, region, tier start, and effective time in every row;
- keep public list and billing-account price tiers separate.

The query accepts an explicit candidate SKU array. An empty array can be used
for discovery with service and taxonomy filters, but taxonomy is not a universal
cross-region product key; discovered candidates require semantic review before
their prices are presented as like-for-like.

## Reproduction commands

Run these commands from the repository root:

```powershell
uv run --script evaluations/google-cloud-sku-pricing/build_benchmark.py --verify-existing
uv run --script evaluations/google-cloud-sku-pricing/build_sealed_holdout_v2.py --verify-existing
python evaluations/google-cloud-sku-pricing/test_benchmark.py
python evaluations/google-cloud-sku-pricing/test_verify_task.py
```

The rejected v5 run is deliberately expected to make this command exit 1 and
report `unsafe-promotion`:

```powershell
uv run --script evaluations/google-cloud-sku-pricing/audit_evolution.py
```

The accepted historical holdout bundle is audited against its frozen staged
copy, because the BigQuery reference was extended afterward:

```powershell
uv run --script evaluations/google-cloud-sku-pricing/audit_sealed_holdout.py `
  --source-skill evaluations/runs/google-cloud-sku-pricing-holdout-v2-gpt54mini/holdout-01/.agents/skills/google-cloud-sku-pricing
```

Repository release gates:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

## Durable artifacts

- Runtime skill: `skills/google-cloud-sku-pricing/`
- API and data-model contract:
  `skills/google-cloud-sku-pricing/references/api-and-data-model.md`
- Regional BigQuery SQL:
  `skills/google-cloud-sku-pricing/references/bigquery-sql.md`
- Runtime helper:
  `skills/google-cloud-sku-pricing/scripts/sku_pricing.py`
- Dataset manifest:
  `evaluations/datasets/google-cloud-sku-pricing-100/processed/manifest.json`
- Sealed-holdout v2 manifest:
  `evaluations/datasets/google-cloud-sku-pricing-100/processed/v2/manifest.json`
- Benchmark builder and verifier: `evaluations/google-cloud-sku-pricing/`

## Limitations

- The API and taxonomy fields used here are v2beta/Beta and can change.
- Public API prices are not a substitute for billing-account contract prices.
- Prices are time-dependent; the frozen benchmark proves correctness against
  one complete snapshot, not that those values remain current forever.
- Product taxonomy is useful for candidate discovery but does not guarantee
  cross-region product equivalence.
- The BigQuery query was checked against the documented schema and generated by
  an isolated skill run, but it was not dry-run against a user-owned BigQuery
  table because no project or dataset was placed in scope.
