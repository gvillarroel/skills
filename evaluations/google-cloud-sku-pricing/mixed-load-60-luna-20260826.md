# Google Cloud SKU Pricing: Mixed-Load 60-Question Harbor Evaluation

Date: 2026-08-26

## Outcome

The released `google-cloud-sku-pricing` skill passed all 60 newly generated
questions under native Harbor 0.18.0 with Pi 0.84.2 and
`openai-codex/gpt-5.6-luna`.

| Measure | Result |
| --- | ---: |
| Harbor trials | 6/6 complete |
| Questions | 60/60 exact |
| Correctness | 1.000 |
| Format | 1.000 |
| Reward | 1.000 |
| Errored trials | 0 |
| Retries | 0 |
| Total agent tokens | 452,005 |
| Total agent cost | USD 0.05631304 |
| Total Harbor runtime | 11 minutes 14 seconds |

The native Harbor reporter validated every job and trial artifact against the
Harbor result models. All six hidden verifiers reported 10 correct answers out
of 10, no envelope findings, and no per-question mismatches.

## Evaluation Design

The builder generated 12 disjoint candidates and selected seed `20260835` by a
predeclared diversity score. The resulting evaluation contains six tasks with
ten questions each. Every task contains exactly one question from each family:

1. geography;
2. SKU identity;
3. consumption-model inventory;
4. list rate;
5. normalized rate;
6. marginal tier;
7. progressive cost;
8. region membership;
9. filtered SKU count; and
10. compatible regional comparison.

The selected questions span 66 named SKUs, 28 services, 123 taxonomy
categories, 41 regions, seven billing units, and four usage bands. Thirty
questions use an explicit numeric load: 18 zero-load lookups and 12 positive
loads with 12 distinct values from `1` through `61875000`. Each task references
between six and ten distinct services. Representative services include Compute
Engine, BigQuery, Cloud Storage, Vertex AI, Kubernetes Engine, Cloud SQL,
Dataflow, Dataproc, Spanner, Firestore, AlloyDB, Networking, and Cloud Speech
API.

The task contract is disjoint from all released pricing evaluations available
to the builder: zero overlap with 220 earlier prompts and 248 earlier named
SKUs. The canonical answers were not written to the visible task environment or
the durable manifest.

## Canonical Answer Assurance

Every answer had to pass three gates before Harbor execution:

1. derive the canonical answer from the normalized SQLite snapshot using exact
   `Decimal` arithmetic;
2. independently recompute the answer with the bundled Parquet helper over the
   complete ZSTD snapshot and require exact structural and decimal equality; and
3. self-score the canonical payload with the hidden Harbor verifier and require
   reward 1.0.

All 60 answers matched across the SQLite and Parquet paths. The frozen Parquet
artifact has SHA-256
`20275538572f0b9c19e2efceaa98127385edb28ba0942097fe029ecb3aebf5c0`,
contains 167,737 exact `DECIMAL(38,9)` tier rows, and records complete API
pagination. The sealed question contract has SHA-256
`2cdfc50d2d75079609c3caf53fd73cdcb485620c5ff27acb2aba4a6359747e80`;
the hidden canonical-answer contract has SHA-256
`3ee7c029e195f47431d1fa3372eee7f3c14ab3dd61710bb710d4473594ec404c`.

## Runtime and Isolation Audit

Harbor observed the requested runtime in all trials:

- agent: `pi` 0.84.2;
- provider: `openai-codex`;
- model: `gpt-5.6-luna`;
- skill digest:
  `sha256:7e0e2dd6c775e076ae344d3a9fd1cfbb8ceae9e141a65ea0d43f2ea51c0ac14c`.

All six Pi JSONL traces passed strict parsing with zero invalid JSON lines, zero
invalid events, zero tool errors, and zero summarizer findings. The read audit
found no absolute reads outside the isolated task workspace, no reads from
`tests/`, `expected.json`, verifier output, or reward files, and no network
dependency. Normal reads were limited to the evaluated skill, its Parquet
reference/helper, `questions.json`, and the agent's own `answers.json`.

## Launch Diagnosis

The first native launch, job name
`google-cloud-sku-pricing-mixed-load-60-luna-20260826-v1`, failed before any
trial ran because the `uvx` process could not import the local `evaluations`
module. This was a configuration/infrastructure failure, not a skill, model, or
verifier failure. The failed job was left intact. Importability was then tested
under Harbor 0.18.0 with the repository root on `PYTHONPATH`, and the evaluation
was relaunched append-only as `v2`. The `v2` job completed without retries.

## Promotion Decision

Retain the evaluated skill unchanged. The earlier evolution added an explicit
question-to-command-to-SKU-to-payload association and verbatim helper
projection; this larger disjoint evaluation produced no correctness, formatting,
source-selection, tier, unit, region, or association failure that would justify
a new mutation. Changing the skill after a perfect holdout would create an
unevaluated candidate without failure evidence.

## Final Validation Gates

The following release gates passed after recording the Harbor result:

- dataset reconstruction verification: 60 questions, 60 exact independent
  oracle matches, zero findings;
- historical Parquet benchmark test: 1/1 test passed, covering all frozen v1
  and v2 answers;
- native Harbor `JobConfig` resolution: expected custom WSL environment, Pi
  adapter, skill path, concurrency 1, and Luna 5.6 model;
- native Harbor result report: 6/6 complete and passed, zero incomplete-result
  findings;
- six strict Pi JSONL trace summaries: zero invalid JSON, invalid events, tool
  errors, or findings;
- repository pattern-ID validation: passed;
- repository skill validation: passed;
- standalone skill-independence validation: passed; and
- repository payload check: passed.

## Reproduction Commands

```powershell
uv run --script evaluations/google-cloud-sku-pricing/build_mixed_load_harbor_60.py
uv run --script evaluations/google-cloud-sku-pricing/build_mixed_load_harbor_60.py --verify-existing
uvx --from harbor==0.18.0 harbor run --config evaluations/google-cloud-sku-pricing/harbor-job-mixed-load-60-luna-20260826.yaml --print-config
$env:PYTHONPATH = 'C:\Users\villa\dev\skills'
uvx --from harbor==0.18.0 harbor run --config evaluations/google-cloud-sku-pricing/harbor-job-mixed-load-60-luna-20260826.yaml --job-name google-cloud-sku-pricing-mixed-load-60-luna-20260826-v2 --jobs-dir evaluations/runs/harbor-jobs --yes
uv run C:\Users\villa\.codex\skills\harbor-run-results\scripts\report_harbor_jobs.py evaluations/runs/harbor-jobs/google-cloud-sku-pricing-mixed-load-60-luna-20260826-v2 --output-dir evaluations/google-cloud-sku-pricing/reports/mixed-load-60-luna-20260826-v2 --title "Google Cloud SKU pricing mixed-load 60-question Luna 5.6 evaluation"
```

Durable inputs and reports:

- `build_mixed_load_harbor_60.py`
- `mixed-load-60-manifest-20260826.json`
- `harbor-job-mixed-load-60-luna-20260826.yaml`
- `reports/mixed-load-60-luna-20260826-v2/final-report.json`
- `reports/mixed-load-60-luna-20260826-v2/final-report.md`

Bulky task and native Harbor job artifacts remain under `evaluations/runs/`, as
required by the repository retention policy.
