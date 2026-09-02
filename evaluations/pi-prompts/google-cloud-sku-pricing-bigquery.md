Read this prompt before taking any other action. Use the supplied
`google-cloud-sku-pricing` skill as your only skill bundle.

Create exactly `regional-contract-price.sql` at the workspace root. Do not
create any other task artifact.

The file must contain executable GoogleSQL over
`PROJECT.DATASET.cloud_pricing_export` that:

- selects the latest ingestion partition and latest `pricing_as_of_time`;
- filters explicit SKUs `1111-AAAA-2222` and `3333-BBBB-4444` to regions
  `asia-east1` and `us-central1`;
- uses the `Default` consumption model and only
  `billing_account_price.tiered_rates`;
- selects the marginal tier at exact NUMERIC usage `125000` by taking the
  greatest `start_usage_amount` not exceeding usage;
- returns SKU, region, consumption model, pricing unit, tier start,
  `pricing_unit_quantity`, account currency code, account currency amount,
  an exact normalized account-currency rate, and effective time;
- preserves region-to-SKU association and does not join tiers by array offset.

Read the finished SQL file once before completing.
