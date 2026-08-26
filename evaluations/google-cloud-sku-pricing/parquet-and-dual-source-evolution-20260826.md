# Google Cloud SKU Pricing: Parquet Fallback and Dual-Source Evolution

Date: 2026-08-26

## Outcome

The `google-cloud-sku-pricing` skill now supports two explicit operational
paths:

1. Generate GoogleSQL over `cloud_pricing_export` when a billing account has a
   usable BigQuery pricing export. This is the path for account-specific
   contract prices.
2. Download the complete public Pricing API catalog and convert it to one
   portable, highly compressed Parquet file when BigQuery is unavailable.

The public fallback was downloaded directly from Google's Cloud Billing
Pricing API v2beta. The resulting artifact is:

`projects/google-cloud-sku-pricing-parquet/artifacts/data/google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.parquet`

Its adjacent manifest is:

`projects/google-cloud-sku-pricing-parquet/artifacts/manifests/google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.manifest.json`

The parameterized BigQuery contract-price template is:

`projects/google-cloud-sku-pricing-parquet/artifacts/sql/google-cloud-regional-contract-prices.sql`

It passes 12/12 structural and semantic checks and has SHA-256
`09c49c06f767b3bf4de88970863857ad37be5d079f9b9566518f526aa1dc2090`.

## Source Decisions

Google's official Pricing API exposes public services, SKUs, and prices. SKU
metadata carries geography; the price listing operation is not a region
selector. Google's BigQuery pricing export is the appropriate source for
billing-account-specific pricing when it is configured and populated.

Primary documentation:

- <https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest>
- <https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/pricing-data>
- <https://arrow.apache.org/docs/python/parquet.html>
- <https://duckdb.org/docs/lts/guides/file_formats/query_parquet>

The Parquet artifact therefore contains public USD list prices only. It must
not be described as a negotiated or billing-account contract catalog.

## Parquet Artifact

| Property | Value |
| --- | --- |
| Snapshot | `gcp-pricing-636387a8dd1a10dc` |
| Retrieval completed | `2026-08-26T01:29:04.265784+00:00` |
| API version | `v2beta` |
| Pagination complete | `true` |
| Services | 1,776 |
| SKUs | 102,518 |
| Public price resources | 102,518 |
| Price models | 157,646 |
| Tier rows | 167,737 |
| Parquet rows | 167,737 |
| File bytes | 4,399,121 |
| Row groups | 3 |
| Compression | ZSTD level 22, the maximum exposed by the selected Arrow codec |
| Decimal representation | `DECIMAL(38,9)` |
| SHA-256 | `20275538572f0b9c19e2efceaa98127385edb28ba0942097fe029ecb3aebf5c0` |

The verified raw JSONL source was 114,787,210 bytes. The Parquet file is
26.09 times smaller, a 96.1676% reduction. `regions` and `product_taxonomy`
remain list columns so normalization does not create a Cartesian row
explosion.

The exporter:

- downloads all paginated services, SKUs, and prices, or converts an existing
  verified raw snapshot;
- accepts credentials through environment-backed API key, OAuth token, or
  `gcloud`, never through a secret-valued command-line argument;
- verifies raw SHA-256 digests and complete pagination;
- rejects values that cannot be represented exactly as `DECIMAL(38,9)`;
- writes atomically and refuses an existing output unless overwrite is
  explicit;
- embeds snapshot, API, completion, and source metadata in the Parquet file and
  writes a separate manifest.

## Deterministic Validation

The Parquet implementation passed:

- three unit tests covering exact schema and ZSTD compression, progressive
  tiers and comparisons, and fail-closed source digest verification;
- 100/100 exact questions from the first ten-family benchmark;
- 100/100 exact questions from the disjoint v2 benchmark;
- the pre-existing SQLite benchmark and verifier tests.

The 200 Parquet questions cover geography, SKU identity, consumption-model
inventory, list rate, normalized base-unit rate, marginal tier selection,
progressive cost, region membership, filtered counts, and compatible regional
comparisons.

## Harbor Evolution

Three append-only Harbor gates were retained. All use Harbor 0.18.0, GEPA
0.1.2, Pi 0.84.2, and the recorded `openai-codex/gpt-5.4-mini` infrastructure
exception because the default Spark model had exhausted quota during this
evaluation line.

| Gate | Development validation | Baseline raw holdout | Important diagnosis | Decision |
| --- | --- | --- | --- | --- |
| v1 | 1.0 | 0.936538 | One Parquet decimal was shortened after the helper returned the exact value; one BigQuery label regex rejected an equivalent label. | Keep baseline; add verbatim-copy rule. |
| v2 | 1.0 | 0.909677 | The agent copied a model inventory from the preceding `describe` response despite the requested helper call returning the correct SKU; three BigQuery regex checks rejected equivalent `CAST`/`SAFE_DIVIDE` forms. | Keep baseline; add question-to-command-to-SKU association. |
| v3 | 1.0 | 0.983871 | Parquet passed 10/10 in both baseline attempts. BigQuery passed 30/31 raw because the eligibility regex did not accept exact `CAST(640000 AS NUMERIC)` or an exact `params.usage_amount` binding. | Keep baseline; automatic proposal was worse in development. |

The v3 automatic mutation scored below its parent on the development
subsample and was not selected. No automatic candidate was promoted. The
versioned source skill is the manually evolved baseline containing both
transferable fixes.

The raw v3 BigQuery artifacts were not rewritten or rescored. A separate
read-only audit verified both preserved SQL queries semantically:

- each query has the exact usage bound of 640,000;
- one expresses it as `<= CAST(640000 AS NUMERIC)`;
- the other expresses it as `<= params.usage_amount` after binding
  `NUMERIC '640000' AS usage_amount`;
- each therefore passes the recovered eligibility condition and all 31
  contract checks.

`audit_dual_source_evolution.py` also verifies:

- every Harbor trial's skill provenance and post-trial content stability;
- zero baseline execution errors across v1-v3;
- the two v3 Parquet baseline rewards are exactly 1.0;
- the public Parquet SHA-256 is unchanged;
- no v3 holdout SKU, region, or scenario token appears in reflection prompts,
  responses, summaries, or event logs;
- reflection event logs contain zero tool calls;
- the two candidate-side Windows/WSL `python.exe: Invalid argument` failures
  are classified as known external failures and did not cause a promotion.

## Isolated Runtime Validation

Strict isolated run
`evaluations/runs/google-cloud-sku-pricing-bigquery-20260826` passed in 86.422
seconds with:

- the exact requested `regional-contract-price.sql` artifact;
- observed model `gpt-5.4-mini` only;
- zero invalid JSON events and zero tool errors;
- unchanged skill payload;
- prompt-first behavior;
- a confined read surface: the prompt, `SKILL.md`,
  `references/bigquery-sql.md`, `references/api-and-data-model.md`, and the
  generated SQL read-back.

The generated SQL uses the latest partition and `pricing_as_of_time`, preserves
SKU-region association, selects billing-account contract tiers, applies the
greatest eligible tier, normalizes with exact `BIGNUMERIC` arithmetic, and
returns all requested dimensions.

## Reproduction Commands

```powershell
uv run --script skills/google-cloud-sku-pricing/scripts/test_pricing_parquet.py
uv run --script evaluations/google-cloud-sku-pricing/test_parquet_benchmark.py
uv run --script evaluations/google-cloud-sku-pricing/build_dual_source_harbor_dataset.py --verify-existing
uv run --script evaluations/google-cloud-sku-pricing/build_dual_source_holdout_v2.py --verify-existing
uv run --script evaluations/google-cloud-sku-pricing/build_dual_source_holdout_v3.py --verify-existing
uv run --script evaluations/google-cloud-sku-pricing/audit_dual_source_evolution.py
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/google-cloud-sku-pricing-bigquery-20260826/events.jsonl --require-model gpt-5.4-mini --fail-on-invalid-json --fail-on-tool-error
```

## Limitations

- The snapshot is frozen, not live. Refresh it before making a current-price
  claim.
- The Pricing API is v2beta and may change.
- The Parquet contains public USD list prices, not account-specific negotiated
  rates.
- The generated BigQuery SQL was structurally and behaviorally evaluated in
  Harbor, but it was not submitted to a user-owned BigQuery project because no
  project, dataset, billing export, or authorization was placed in scope.
