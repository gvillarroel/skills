# Sealed holdout revision v2

This revision preserves the original 60 training and 20 validation questions
but replaces all 20 holdout questions after a rejected evolution run allowed a
reflection model to inspect the first holdout prompts. Canonical answers were
not exposed, but prompt visibility is enough to invalidate a sealed holdout.

The v2 holdout is generated from the same immutable catalog snapshot with a new
seed. Every SKU named by any v1 question is reserved before generation, and no
v2 holdout prompt may equal any v1 prompt. The generated benchmark database and
task directories remain ignored by Git; `manifest.json` records hashes and
disjointness evidence without storing prompts or answers.

Build and verify from the repository root:

```powershell
uv run --script evaluations/google-cloud-sku-pricing/build_sealed_holdout_v2.py
uv run --script evaluations/google-cloud-sku-pricing/build_sealed_holdout_v2.py --verify-existing
```

Evaluation status: this holdout was opened once on 2026-08-25 after candidate
selection. The clean direct gate used `openai-codex/gpt-5.4-mini` because the
required Spark model reached its usage limit, and scored 20/20 with no tool or
read-surface findings. Do not reuse v2 to select or tune a future candidate;
generate a disjoint v3 holdout instead.
