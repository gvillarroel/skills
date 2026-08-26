# Pricing API and data model

Read this reference for live Google Cloud Pricing API work.

## Public endpoints

Enable the Cloud Billing API. Public requests can use a restricted API key;
OAuth with a Cloud Billing read scope is also supported.

```text
GET https://cloudbilling.googleapis.com/v2beta/services?pageSize=5000
GET https://cloudbilling.googleapis.com/v2beta/skus?pageSize=5000
GET https://cloudbilling.googleapis.com/v2beta/skus/-/prices?currencyCode=USD&pageSize=5000
```

Follow `nextPageToken` until it is absent. `skus.list` can filter by service but
not by region. Join a price resource named `skus/<SKU_ID>/price` to
`Sku.skuId`.

For billing-account-specific prices, use OAuth and the required Cloud Billing
permission:

```text
GET https://cloudbilling.googleapis.com/v2beta/billingAccounts/<ACCOUNT_ID>/skus/-/prices?pageSize=5000
```

Do not print API keys, access tokens, environment variables, or billing-account
credentials. Account-specific reads require authorization from the user and
the `billing.billingAccountPrice.get` permission.

## Geography

Read `Sku.geoTaxonomy.type` and the matching metadata arm:

- `TYPE_GLOBAL`: no region list.
- `TYPE_REGIONAL`: `regionalMetadata.region.region`.
- `TYPE_MULTI_REGIONAL`: every entry in
  `multiRegionalMetadata.regions[].region`.

The v1 catalog endpoint `services/<SERVICE_ID>/skus` is a useful public
alternative when a price timeline or service-scoped response is required. It
returns `serviceRegions`, `geoTaxonomy`, and chronological `pricingInfo` in the
same SKU object. Do not mix v1, v1beta, and v2beta response parsers.

## Price dimensions

In v2beta, each public `Price` contains `skuPrices[]`. Each element identifies a
consumption model and a rate with:

- `tiers[].startAmount.value`;
- `tiers[].listPrice.units` and `tiers[].listPrice.nanos`;
- `unitInfo.unit`, `unitDescription`, and `unitQuantity.value`;
- aggregation level and interval.

Billing-account price tiers additionally expose contract price and effective
discount. Keep public list and contract tiers separate because their boundaries
can differ.

## Arithmetic

Use decimal arithmetic:

```text
money = Decimal(units or 0) + Decimal(nanos or 0) / 1e9
base_unit_rate = tier_price / pricing_unit_quantity
```

For usage `U`, the marginal tier is the tier with the largest start amount not
greater than `U`. A progressive total is:

```text
sum(max(0, min(U, next_start) - start) / unit_quantity * tier_price)
```

The final marginal rate multiplied by all usage is not a tiered total.

## Source evidence

For user-facing current values, record the API version, currency, retrieval
time, page completeness, SKU ID, consumption model, tier start, and unit
quantity. Current prices change; avoid unqualified timeless claims.

Official references:

- https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/skus
- https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/skus/list
- https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/skus.prices/list
- https://docs.cloud.google.com/billing/docs/reference/pricing-api/rest/v2beta/billingAccounts.skus.prices/list
- https://docs.cloud.google.com/billing/docs/reference/rest/v1/services.skus/list

