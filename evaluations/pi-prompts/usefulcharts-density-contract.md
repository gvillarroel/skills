Use usefulcharts-style to check the declared-census comparator's exact command interface. This synthetic test does not measure any actual poster or establish aesthetic quality.

Create `reference.json` with this JSON and create `candidate.json` as an identical copy:

```json
{
  "schema_version": 1,
  "family": "timeline",
  "comparison_basis": "same-full-poster-area",
  "counting_protocol": "usefulcharts-knowledge-v1",
  "coverage": "full-body",
  "image_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "ledger": "Synthetic command-interface census; not an actual reference census.",
  "method": "manual-census",
  "census_review": "pass",
  "semantic_review": "pass",
  "legibility_review": "pass",
  "counts": {
    "named_records": [128, 128],
    "typed_relations": [94, 94],
    "temporal_anchors": [200, 200],
    "context_statements": [150, 150]
  }
}
```

Run exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/compare_density.py reference.json candidate.json --report result/density.json --require-pass
```

Read the report and briefly state what it establishes and does not establish. Required outputs are `reference.json`, `candidate.json` and `result/density.json`. Treat the copied skill as read-only; use only this workspace and that skill. Do not inspect repository files, acceptance examples, other skills, Git history or external directories. No network research or poster rendering is needed.
