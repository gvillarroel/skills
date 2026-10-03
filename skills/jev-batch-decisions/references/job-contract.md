# Job contract

The runner accepts UTF-8 JSON with `version: 1`. Copy the starter template and
edit it outside the skill. All fields below are optional except `version` and
`questions`. Unknown fields fail before network access; this catches misspelled
limits. The bundled validator deliberately supports a compact subset of the
native API: question instructions are strings and all criteria are explicit.

| Field | Meaning |
| --- | --- |
| `model` | Explicit OpenRouter Jev ID; default `typesafe/jev-1.13`. The returned dated version is retained. |
| `context` | Shared definitions, relevant policy, and scope available to every fragment. |
| `questions` | Map of names to native `choice`, `score`, or `noul` questions. |
| `review` | `confidence_min: 0.7`, `noul_low: 0.2`, `noul_high: 0.8` by default. |
| `reducers` | Map of map-question names to deterministic operations. |
| `reduce` | Optional recursive semantic aggregation: its own `questions`, `context`, `fan_in` (4), `max_levels` (12). |
| `limits` | Limits described below. |

`choice` criteria map each option to a description or null. Include `unknown`
when missing evidence is possible; that exact option becomes a review result.
`score` criteria are an ordered array of two or more descriptions. Its value
is a fractional expected level, not an integer class or measured quantity.
`noul` means probability of yes, with optional `true`/`false` descriptions. Its
middle review interval becomes null, never a negative decision.

```json
{
  "version": 1,
  "context": "Review only the current document fragment for an explicitly unresolved production incident.",
  "questions": {
    "blocker": {
      "type": "noul",
      "instructions": "Does this fragment explicitly report an unresolved production incident?",
      "criteria": {
        "true": "At least one incident is explicitly unresolved and affects production.",
        "false": "No such evidence, or all mentioned incidents are resolved."
      }
    },
    "severity": {
      "type": "score",
      "instructions": "Rate the greatest stated current impact in this fragment.",
      "criteria": ["No current impact", "One user affected", "A whole team affected", "Whole service unavailable"]
    }
  },
  "reducers": {"blocker": "any", "severity": "max"}
}
```

## Resource limits

Defaults: `chunk_chars=3000`, `batch_items=4`, `max_questions=32`,
`max_request_bytes=24000`, `concurrency=4`, `max_requests=200`, `attempts=3`,
`timeout_seconds=30`. The byte ceiling includes state, instructions, and
criteria after serialization. It is a conservative engineering limit below
the advertised 32K context, not a tokenizer measurement or a price estimate.
Keep its maximum at 28000 unless a future verified API contract justifies a
code change. A single request may contain many questions about one item and
many independently located items. `max_questions` counts the expanded total.

`max_requests` caps actual HTTP attempts across resumes, including retries and
reduce stages. Planning refuses when map requests alone exceed it. Reduction
size depends on actual decisions, so the plan's reduce bound is deliberately
loose. A run can exhaust its cap during reduction; its report then remains
failed. Set an adequate finite cap before running a large collection.

## Inputs and output files

- TXT/MD: streaming character windows, preferring paragraphs, then lines,
  then words. No overlap. Locations are zero-based, half-open character
  offsets in decoded UTF-8 with an initial BOM removed. Newlines are preserved.
  `hard_text_boundaries` flags words that could not fit intact. These windows
  are not guarantees that a full semantic unit fits.
- CSV: one complete row per map item, headers repeated as object keys. Quoted
  multiline cells remain intact. `row` is one-based, excluding the header;
  `physical_end_line` locates multiline rows. Oversized or malformed rows fail.
- JSONL/NDJSON: one object or array per nonempty physical line. `line` retains
  the original line number, and an optional input `id` is preserved as
  `record_id`. Large records fail rather than being split invisibly.
- Multiple paths are accepted in one run. Different files never share a text
  chunk. Source IDs follow argument order; source hashes bind the content.
  Duplicate paths are rejected. Distinct equal records are still distinct
  observations: deduplicate entity IDs explicitly before inference if needed.

`run.json` binds normalized configuration, source hashes, paths and runner code.
`plan.json` describes coverage and request limits. `chunks.jsonl` and
`map-jobs.jsonl` contain the selected source text for reproducibility; protect
this output directory like the inputs. `decisions.jsonl` contains each map unit,
location, normalized decision, full native answer and request hash.
`checkpoints/` stores validated responses. `attempts.jsonl` stores accounting
events without credentials or provider error bodies. `aggregates.json` contains
global and per-source deterministic results. Semantic trees also write
`reduce-level-*.jsonl`, `reduce-nodes.jsonl`, and `final.json`.

Only `report.json` with `status: complete` establishes whole-run completeness.
In a failed run, previously written aggregate/final files can be stale; consume
them only when that report is complete. A complete run can still contain
decisions requiring review. Coverage is a processing guarantee, not accuracy.
