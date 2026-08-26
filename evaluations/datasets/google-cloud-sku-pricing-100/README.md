# Google Cloud SKU pricing benchmark

This dataset evaluates whether the `google-cloud-sku-pricing` skill can answer
exact questions from a frozen, normalized Google Cloud Pricing API catalog.
It contains 100 questions in ten equal families. Six batches per family are
development data, two are validation data, and two are sealed holdout data.

The generated benchmark uses two deliberately separate databases:

- `processed/catalog.sqlite` is the visible source of truth copied into each
  task. It contains services, SKUs, geographic metadata, public consumption
  models, and all list-price tiers from one complete API snapshot.
- `processed/benchmark.sqlite` is evaluator-only. It contains prompts,
  canonical structured answers, split assignments, and provenance.

Raw API pages and both generated databases are ignored by Git. The checked-in
manifests contain hashes, counts, endpoint configuration, and split summaries,
but never canonical answers. Rebuild commands and the exact source timestamp
are recorded in `processed/manifest.json` after generation.

The question families are geography, SKU identity, model inventory, list rate,
normalized rate, marginal tier, progressive cost, region membership, filtered
catalog count, and compatible price comparison. Decimal price answers are JSON
strings so no binary floating-point rounding enters the acceptance contract.

Generate or verify the local snapshot from the repository root:

```powershell
uv run --script evaluations/google-cloud-sku-pricing/build_benchmark.py --fetch-live
uv run --script evaluations/google-cloud-sku-pricing/build_benchmark.py --verify-existing
```

Live generation uses a Google Cloud OAuth token obtained from `gcloud auth
print-access-token`, follows every pagination token, and never stores the
credential. The Pricing API data is mutable, so a new live fetch creates a new
benchmark snapshot rather than silently changing an existing evaluation.

