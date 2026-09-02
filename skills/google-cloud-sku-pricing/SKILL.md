---
name: google-cloud-sku-pricing
description: Retrieve, compare, calculate, and export Google Cloud SKU prices across regions using the Cloud Billing Pricing API, a highly compressed offline Parquet catalog, a normalized SQLite snapshot, or the BigQuery pricing export. Use for current public or billing-account prices, regional SKU comparisons, tier selection, usage estimates, portable catalogs, and SQL over cloud_pricing_export.
---

# Google Cloud SKU Pricing

Treat price, geography, consumption model, tier, unit quantity, currency, and
snapshot time as separate dimensions. Never infer a regional price from a SKU
description or compare raw amounts whose units or models differ.

## Choose the source

- For current public catalog questions, use the Pricing API and read
  [references/api-and-data-model.md](references/api-and-data-model.md).
- For negotiated billing-account prices or recurring SQL analysis, prefer the
  pricing export and read [references/bigquery-sql.md](references/bigquery-sql.md).
- When BigQuery is unavailable or the user needs a portable frozen catalog,
  build or query Parquet and read
  [references/parquet-offline.md](references/parquet-offline.md).
- When the prompt supplies a normalized SQLite snapshot, use
  `scripts/sku_pricing.py`; treat the snapshot timestamp as the answer's
  effective time and do not replace it with live data.

## Answer precisely

1. Identify whether the prompt asks for a list price, billing-account price,
   marginal tier rate, normalized per-unit rate, or progressive total cost.
2. Resolve geography from SKU metadata. A SKU usually encodes its region; the
   price endpoint itself does not accept a region selector.
3. Select the requested consumption model. Use `Default` only when the prompt
   requests it or leaves the model unspecified.
4. Preserve every tier. For usage-dependent questions, choose the greatest tier
   start not exceeding usage. For total cost, apply tiers progressively rather
   than multiplying all usage by the final marginal rate.
5. Interpret a tier price as the amount per `pricing_unit_quantity`. Divide by
   that quantity only when the prompt requests a base-unit rate.
6. Use decimal arithmetic. For API Money values, compute
   `units + nanos / 1,000,000,000`; do not use binary floats for final values.
7. Return only the fields and currency requested, while including enough
   evidence to identify the SKU, model, tier start, unit quantity, and snapshot.
8. When a bundled helper already returns a requested decimal or identity value,
   project and copy that value verbatim. Do not retype it from memory, shorten
   it, round it, or recompute it with a lower-precision tool.
9. For a batch, keep an explicit mapping from each question ID to its command,
   requested SKU or filters, and returned payload. Before projecting an answer,
   verify that every echoed identifier matches that question. Never reuse an
   adjacent command's output merely because its shape is compatible.

## Work with a supplied snapshot

Run the bundled helper without editing the read-only skill. Start with:

```text
python skills/google-cloud-sku-pricing/scripts/sku_pricing.py --db <catalog.sqlite> describe --sku-id <SKU_ID>
```

Use `rate` for a marginal tier, `cost` for a progressive estimate, `count` for
catalog filters, and `compare` or `cheapest` only across compatible units. Run
`--help` on the selected command for its exact arguments. Keep machine-readable
answers as JSON and preserve the prompt's requested IDs and output path exactly.
Build the final JSON directly from helper results when possible, then read it
back once to catch transcription loss before answering. For repeated
`describe` calls, check the returned `sku_id` before copying identity,
geography, or model inventory fields; rerun the command if the association is
unclear.

For a supplied Parquet snapshot, use the separate helper:

```text
uv run --script skills/google-cloud-sku-pricing/scripts/parquet_pricing.py --parquet <catalog.parquet> describe --sku-id <SKU_ID>
```

Use `export_pricing_parquet.py` to download a complete public API snapshot or
convert verified Pricing API JSONL into a single ZSTD Parquet file. Keep the
generated manifest with the file. Do not describe this public fallback as an
account-specific contract catalog.

## Validate before answering

- Confirm the SKU exists and report an unresolved SKU instead of guessing.
- Confirm compared rows share currency, unit, unit quantity, and consumption
  model, or normalize explicitly and state the conversion.
- Distinguish `GLOBAL`, `REGIONAL`, and `MULTI_REGIONAL` geography.
- Report the source and effective timestamp for current-price claims.
- For Parquet, verify the manifest digest, complete-pagination flag, snapshot
  ID, and currency before treating the file as a complete catalog.
- If live authentication, permissions, or pagination are incomplete, report
  the missing coverage; never present a partial catalog as complete.
