# BigQuery pricing SQL

Read this reference when the user has enabled the Cloud Billing pricing export
or asks for reusable SQL. The account-specific table is normally named
`cloud_pricing_export`.

## Latest complete snapshot

Prefer a normalizing view because export schemas and beta taxonomy fields can
gain columns. Select the latest ingestion partition and then the latest
`pricing_as_of_time` within that partition:

```sql
WITH latest AS (
  SELECT p.*
  FROM `PROJECT.DATASET.cloud_pricing_export` AS p
  WHERE DATE(_PARTITIONTIME) = (
    SELECT MAX(DATE(_PARTITIONTIME))
    FROM `PROJECT.DATASET.cloud_pricing_export`
  )
  QUALIFY pricing_as_of_time = MAX(pricing_as_of_time) OVER ()
)
SELECT * FROM latest;
```

## Flatten without losing dimensions

Unnest geography, consumption models, and price tiers deliberately. Supply a
sentinel only for global or unspecified geography; do not label an unknown SKU
as regional.

```sql
SELECT
  p.pricing_as_of_time,
  p.service.id AS service_id,
  p.service.description AS service_name,
  p.sku.id AS sku_id,
  p.sku.description AS sku_description,
  p.geo_taxonomy.type AS geo_type,
  region,
  model.consumption_model_id,
  model.consumption_model_display_name,
  p.pricing_unit,
  tier.start_usage_amount,
  tier.pricing_unit_quantity,
  tier.usd_amount AS price_usd,
  SAFE_DIVIDE(tier.usd_amount, tier.pricing_unit_quantity)
    AS price_usd_per_base_unit
FROM latest AS p
CROSS JOIN UNNEST(
  CASE
    WHEN COALESCE(ARRAY_LENGTH(p.geo_taxonomy.regions), 0) > 0
      THEN p.geo_taxonomy.regions
    WHEN p.geo_taxonomy.type = 'GLOBAL' THEN ['global']
    ELSE ['unspecified']
  END
) AS region
CROSS JOIN UNNEST(p.consumption_model_prices) AS model
CROSS JOIN UNNEST(model.list_price.tiered_rates) AS tier;
```

Use `model.billing_account_price.tiered_rates` for negotiated account prices.
Do not join public and contract tiers only by array position; their boundaries
can differ. Emit them as separate price scopes or perform an explicit interval
join.

## Compare regional list prices at a usage amount

Use an explicit candidate SKU list whenever possible. Google does not publish a
universal cross-region product key, and a shared taxonomy path alone does not
prove that two SKUs describe the same product. An empty candidate list below
falls back to the service and taxonomy filters for discovery; review those
candidates before treating the rank as a like-for-like comparison.

```sql
DECLARE target_service_id STRING DEFAULT '6F81-5844-456A';
DECLARE target_taxonomy STRING DEFAULT 'VMs On Demand';
DECLARE target_model STRING DEFAULT 'Default';
DECLARE usage_amount NUMERIC DEFAULT 0;
DECLARE candidate_sku_ids ARRAY<STRING> DEFAULT [];
DECLARE target_regions ARRAY<STRING> DEFAULT [];

WITH latest AS (
  SELECT p.*
  FROM `PROJECT.DATASET.cloud_pricing_export` AS p
  WHERE DATE(_PARTITIONTIME) = (
    SELECT MAX(DATE(_PARTITIONTIME))
    FROM `PROJECT.DATASET.cloud_pricing_export`
  )
  QUALIFY pricing_as_of_time = MAX(pricing_as_of_time) OVER ()
),
eligible_tiers AS (
  SELECT
    p.pricing_as_of_time,
    p.service.id AS service_id,
    p.service.description AS service_name,
    p.sku.id AS sku_id,
    p.sku.description AS sku_description,
    p.geo_taxonomy.type AS geo_type,
    region,
    model.consumption_model_id,
    model.consumption_model_display_name,
    p.pricing_unit,
    tier.pricing_unit_quantity,
    tier.start_usage_amount,
    tier.usd_amount,
    SAFE_DIVIDE(
      tier.usd_amount,
      CAST(tier.pricing_unit_quantity AS NUMERIC)
    ) AS usd_per_base_unit
  FROM latest AS p
  CROSS JOIN UNNEST(
    CASE
      WHEN COALESCE(ARRAY_LENGTH(p.geo_taxonomy.regions), 0) > 0
        THEN p.geo_taxonomy.regions
      WHEN p.geo_taxonomy.type = 'GLOBAL' THEN ['global']
      ELSE ['unspecified']
    END
  ) AS region
  CROSS JOIN UNNEST(p.consumption_model_prices) AS model
  CROSS JOIN UNNEST(model.list_price.tiered_rates) AS tier
  WHERE p.service.id = target_service_id
    AND target_taxonomy IN UNNEST(p.product_taxonomy)
    AND model.consumption_model_display_name = target_model
    AND CAST(tier.start_usage_amount AS NUMERIC) <= usage_amount
    AND (
      ARRAY_LENGTH(candidate_sku_ids) = 0
      OR p.sku.id IN UNNEST(candidate_sku_ids)
    )
    AND (
      ARRAY_LENGTH(target_regions) = 0
      OR region IN UNNEST(target_regions)
    )
),
marginal_rates AS (
  SELECT *
  FROM eligible_tiers
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY sku_id, region, consumption_model_id
    ORDER BY start_usage_amount DESC
  ) = 1
),
compatible_rates AS (
  SELECT
    *,
    COUNT(*) OVER compatibility AS compatible_row_count,
    DENSE_RANK() OVER (
      compatibility
      ORDER BY usd_per_base_unit, sku_id, region
    ) AS price_rank
  FROM marginal_rates
  WINDOW compatibility AS (
    PARTITION BY
      consumption_model_id,
      pricing_unit,
      pricing_unit_quantity
  )
)
SELECT
  pricing_as_of_time,
  service_id,
  service_name,
  sku_id,
  sku_description,
  geo_type,
  region,
  consumption_model_id,
  consumption_model_display_name,
  pricing_unit,
  pricing_unit_quantity,
  start_usage_amount,
  usd_amount,
  usd_per_base_unit,
  compatible_row_count,
  price_rank
FROM compatible_rates
WHERE compatible_row_count > 1
ORDER BY
  consumption_model_id,
  pricing_unit,
  pricing_unit_quantity,
  price_rank,
  sku_id,
  region;
```

This query returns the marginal tier at `usage_amount`, not a progressive
invoice estimate. For local-currency analysis, select
`tier.account_currency_amount` and partition comparisons by
`p.account_currency_code`. For contract prices, repeat the tier CTE against
`model.billing_account_price.tiered_rates` and label that branch separately.

## Comparison contract

Before ranking regional prices, filter or normalize to the same:

- service and product semantics;
- consumption model;
- currency;
- pricing unit and quantity;
- tier start or usage scenario.

A product-taxonomy path helps find candidates but is not a guaranteed universal
cross-region product key. Preserve SKU IDs in every comparison result.

Official schema:
https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/pricing-data
