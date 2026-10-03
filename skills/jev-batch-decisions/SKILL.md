---
name: jev-batch-decisions
description: "Splits large text documents and record collections into bounded batches, evaluates typed decisions with TypeSafe Jev through OpenRouter, and aggregates the results with deterministic reducers or a recursive Jev decision tree. Use for bulk classification, evidence screening, rubric scoring, and document-wide decision questions."
---

# Jev Batch Decisions

Turn a large-input question into explicit decision rubrics, bounded map requests,
and an auditable answer. Use the bundled runner instead of writing another API
client. Jev returns `choice`, `score`, and `noul` decisions; it does not generate
arbitrary JSON objects, extract open-ended quotations, or write summaries.

## Choose the decision contract

1. Define the unit being judged: a complete record, a document fragment, or a
   collection of earlier decisions. Put shared definitions and governing rules
   in `context`, which accompanies every request. A fragment cannot infer a
   qualification or exception that exists only in another fragment.
2. Read [the job contract](references/job-contract.md). Copy
   [the starter job](assets/templates/job.json) into the task workspace and
   adapt its `questions`, review thresholds, and reducers. Express uncertainty
   explicitly with an `unknown` choice where appropriate.
3. Select complete-record input for CSV/JSONL; use paragraph-aware bounded
   windows for TXT/Markdown. Normalize PDF, DOCX, OCR, or HTML first with a
   suitable local extractor, preserving page/section identifiers in JSONL.
   Never pass binary files as text. Inspect extraction completeness before
   making a claim about the whole document.
4. Select a deterministic reducer for counts, any/all, maximum, or mean. Select
   recursive Jev reduction only when the aggregate requires a semantic decision
   and its child decisions preserve everything that decision needs. Read
   [aggregation recipes](references/aggregation.md) for the relevant case.

## Plan, execute, and verify

Commands below are relative to the loaded bundle's parent. Replace the bundle
prefix with its actual path when necessary. Generated files belong outside it.

```sh
uv run --script skills/jev-batch-decisions/scripts/jev_batch.py --job job.json --input records.jsonl handbook.md --out planned --dry-run
uv run --script skills/jev-batch-decisions/scripts/jev_batch.py --job job.json --input records.jsonl handbook.md --out decisions
uv run --script skills/jev-batch-decisions/scripts/jev_batch.py --job job.json --input records.jsonl handbook.md --out decisions --resume
```

- Inspect `plan.json`: source hashes, complete chunk coverage, request sizes,
  map calls, and a conservative upper bound on reduce calls. All map inputs are
  checked before inference starts. Split or restructure an oversized record;
  the runner refuses to truncate it.
- Use the existing `OPENROUTER_API_KEY` environment variable. A live run sends
  the selected content to OpenRouter and consumes that account's credits. A
  user's request to run the model authorizes those calls; do not ask again.
  Use synthetic records for skill tests. Never print, persist, or embed the key.
- The runner uses `https://openrouter.ai/api/alpha/decisions` and
  `typesafe/jev-1.13`, not chat completions. Native question keys do not guide
  inference: the runner puts each item's explicit locator in its instructions.
- `batch_items` controls independent items in one native request; `concurrency`
  controls simultaneous HTTP requests. This is application-side batching, not
  a provider asynchronous batch job. Start small and compare batched decisions
  with single-item controls before scaling a new rubric.
- Require `report.json` status `complete` and complete map coverage. Inspect
  `decisions.jsonl`, `aggregates.json`, and, for semantic reduction,
  `reduce-nodes.jsonl` plus `final.json`. The lineage points back to exact
  source spans/rows in `chunks.jsonl`. Unknowns remain visible.
- Use `--resume` with the unchanged job and inputs to reuse validated request
  checkpoints. A different contract, source, or runner requires a fresh output
  directory. The request cap includes attempts from earlier invocations.
- On failure, inspect the sanitized error and partial report; never interpret
  a partial aggregate as the whole answer. See
  [API behavior and recovery](references/api-and-recovery.md).

## Deliver the answer

Report the decision, scope (records versus fragments versus documents), review
count, source locations, actual calls, reported tokens/cost, and elapsed time.
For prose, compose it from the validated results and inspect the source spans
supporting consequential claims. Do not attribute generated prose or extracted
facts to Jev. Treat confidence as a model score, not demonstrated calibration.
Measure efficiency with the same data and rubrics; concurrency can reduce wall
time while batching can repeat more schema/context tokens.
