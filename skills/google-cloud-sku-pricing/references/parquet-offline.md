# Offline Parquet pricing catalog

Read this reference when BigQuery is unavailable, the prompt asks for a
portable catalog, or a reproducible frozen snapshot is preferable to live
calls. This path contains public list prices. It does not substitute for
billing-account contract prices.

## Build a complete snapshot

The bundled exporter can download all public services, SKUs, and prices from
the v2beta Pricing API and convert them to one Parquet file. Keep credentials in
an environment variable or the active `gcloud` session; never put a token or
API key in the command line.

```text
uv run --script skills/google-cloud-sku-pricing/scripts/export_pricing_parquet.py \
  --download-dir <new-empty-raw-directory> \
  --output <catalog.parquet> \
  --manifest-output <catalog.manifest.json> \
  --currency USD
```

The exporter uses `GOOGLE_CLOUD_API_KEY` when present. Otherwise it uses
`GOOGLE_OAUTH_ACCESS_TOKEN` or `gcloud auth print-access-token`. Restrict API
keys to the Cloud Billing API. The raw directory must be new or empty so one
snapshot cannot silently overwrite another.

To convert a previously downloaded complete snapshot, use `--raw-dir` instead
of `--download-dir`. The exporter verifies the manifest, pagination flag, and
SHA-256 digest of every JSONL collection before writing. It writes atomically
and refuses to replace existing output unless `--overwrite` is explicit.

## Storage contract

The file has one row per SKU, consumption model, and price tier. Repeated
metadata compresses efficiently, while `regions` and `product_taxonomy` remain
list columns so they do not create a region-by-taxonomy cross product.

- Decimal columns use `DECIMAL(38,9)`. Conversion fails instead of rounding a
  source value that does not fit.
- `list_price` is the amount per `unit_quantity`, not automatically a base-unit
  price.
- `tier_start` is the inclusive start for a marginal tier.
- Public API Money is reconstructed exactly from `units` and `nanos`.
- Snapshot ID, UTC retrieval time, API version, currency, source, and complete
  pagination are stored both as columns and Parquet key-value metadata.
- The default writer uses ZSTD at Arrow's maximum supported level, dictionary
  encoding, page statistics, a page index, and Parquet format 2.6.

## Query with the bundled helper

Use the helper for common operations:

```text
uv run --script skills/google-cloud-sku-pricing/scripts/parquet_pricing.py \
  --parquet <catalog.parquet> describe --sku-id <SKU_ID>
```

Use `rate` for the marginal tier, `cost` for a progressive estimate, `count`
for catalog filters, and `compare` or `cheapest` only for compatible explicit
SKU IDs. Run `--help` on the selected command for exact arguments. The helper
returns JSON and uses decimal arithmetic for final values.

## Query directly with DuckDB

DuckDB reads the file without loading it into a database. Filters and projected
columns are pushed into the Parquet scan.

```sql
SELECT
  snapshot_id,
  retrieved_at,
  service_id,
  sku_id,
  sku_name,
  geo_type,
  regions,
  consumption_model_description,
  unit,
  unit_quantity,
  tier_start,
  list_price,
  list_price / unit_quantity AS price_per_base_unit
FROM read_parquet('catalog.parquet')
WHERE list_contains(regions, 'us-central1')
  AND consumption_model_description = 'Default'
ORDER BY service_id, sku_id, tier_start;
```

Select the marginal tier at a usage value with the greatest eligible start:

```sql
WITH eligible AS (
  SELECT *
  FROM read_parquet('catalog.parquet')
  WHERE sku_id = 'SKU_ID'
    AND consumption_model_description = 'Default'
    AND tier_start <= CAST('1500' AS DECIMAL(38,9))
)
SELECT *
FROM eligible
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY sku_id, consumption_model_id
  ORDER BY tier_start DESC, tier_position DESC
) = 1;
```

Calculate progressive cost by bounding every tier at the next start; do not
apply the final marginal rate to all usage:

```sql
WITH input AS (
  SELECT CAST('1500' AS DECIMAL(38,9)) AS usage
), tiers AS (
  SELECT
    p.*,
    LEAD(tier_start) OVER (
      PARTITION BY sku_id, consumption_model_id
      ORDER BY tier_start, tier_position
    ) AS next_tier_start
  FROM read_parquet('catalog.parquet') AS p
  WHERE sku_id = 'SKU_ID'
    AND consumption_model_description = 'Default'
)
SELECT
  sku_id,
  currency_code,
  SUM(
    (LEAST(input.usage, COALESCE(next_tier_start, input.usage)) - tier_start)
    / unit_quantity * list_price
  ) AS progressive_cost
FROM tiers
CROSS JOIN input
WHERE input.usage > tier_start
GROUP BY sku_id, currency_code;
```

Before ranking regions, require the same product semantics, consumption model,
currency, unit, unit quantity, and usage scenario. Preserve each SKU ID and
snapshot timestamp in the result.

Official format references:

- https://arrow.apache.org/docs/python/parquet.html
- https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
- https://duckdb.org/docs/stable/data/parquet/overview
