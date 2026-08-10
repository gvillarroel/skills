# Unified D3 Harbor Evaluation Protocol

## Objective

Measure whether the isolated `d3` skill can create and validate faithful D3
visuals across quantitative visualization, animation and interaction,
parametric logos, SVG recomposition, and composition critique while enforcing
colorset1 by default and colorset2 only after an explicit extended-color
request.

## Fixed Profile

- Harbor: 0.18.0
- Agent: Codex 0.147.0 through the native Harbor adapter
- Model: `gpt-5.3-codex-spark`
- Reasoning effort: medium
- Attempts: three fresh trials per task
- Concurrency: four trials
- Skill payload: only `skills/d3`
- Environment: workspace-scoped WSL adapter because Docker is unavailable
- Browser: cached Chromium controlled through Playwright Core
- Development tasks: three
- Optimizer-visible validation tasks: two
- Sealed final holdout tasks: five

The WSL adapter is an evaluation-isolation boundary, not a security sandbox.
Prompts forbid ambient repository discovery and network use, Harbor locks the
installed skill digest, and raw trajectories remain private ignored evidence.

## Dataset Design

The ten naturalistic tasks are byte-disjoint and use unique IDs. Development
and validation together cover the same four routes as holdout without sharing
facts, labels, values, pattern IDs, or artifact fixtures.

| Split | Visualization | Logo | Recomposition | Evaluation | Colorset1 | Colorset2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 2 | 1 | 0 | 0 | 2 | 1 |
| Validation | 0 | 0 | 1 | 1 | 2 | 0 |
| Holdout | 2 | 1 | 1 | 1 | 3 | 2 |

The builder validates split counts, task-ID uniqueness, task-content digests,
route parity across the optimizer boundary, and palette coverage. The Harbor
organizer independently rejects overlapping source trees, task IDs, or task
digests and records immutable dataset locks.

## Independent Gates

The tested agent creates either:

- `deliverables/visual.html` plus `deliverables/decision.json`; or
- `deliverables/evaluation.md` plus `deliverables/decision.json` for critique.

The evaluator-owned verifier does not call a skill validator. It independently
requires, as applicable:

1. exact artifacts and decision metadata;
2. the requested route and stable `d3-*` pattern ID;
3. actual D3 API evidence and `data-renderer="d3"`;
4. self-contained output with no CDN or remote data dependency;
5. a successful browser render with zero page or console errors;
6. SVG viewBox, title, description, IDs, classes, tag counts, and data
   attributes declared by the task;
7. exact visible labels, values, units, order, counts, and relationships;
8. colorset1 by default or colorset2 only when explicitly requested;
9. active palette metadata and only exact lowercase six-digit active tokens;
10. alpha-aware visible-pixel palette coverage and a material raster change
    after counterfactual replacement of signature colors;
11. requested animation or interaction evidence; and
12. selector-specific, arithmetically traceable critique findings for
    evaluation tasks.

Each trial emits binary `reward` plus separate `routing`, `palette`,
`visual_palette`, `palette_influence`, `render`, `fidelity`, `metadata`, and
`d3_contract` rewards. A naturalistic task passes only when at least two of its
three attempts receive full reward. Execution exceptions remain errors.

## Evolution and Selection Boundary

All three datasets are registered before the first stage starts. Only the
development split may guide edits. The validation split is optimizer-visible
selection evidence and runs after development is complete. The selected skill
bundle and selection report must then be recorded by SHA-256 on the promotion
stage.

Holdout remains sealed until the organizer accepts that completed selection
evidence. It is released once, then run against the unchanged selected bundle.
Holdout prompts, verifier details, rewards, and trajectories are not used for
further evolution, candidate selection, or score rewriting. Any later
diagnostic is reported separately and cannot replace the original holdout.

## Reproduction

Build the ignored datasets and configs:

```powershell
uv run --script evaluations/d3/build_harbor_dataset.py `
  --output-root evaluations/runs/d3-unified-harbor-20260809-v1 `
  --run-id d3-unified-20260809-v1 `
  --attempts 3 `
  --concurrency 4
```

Validate each native config with Harbor `--print-config`, then follow the
append-only stages in `harbor-study-20260809-v1`. Keep tasks, locks, ledgers,
jobs, reports, screenshots, DOM captures, responses, and trajectories private;
publish only organizer indexes and reviewed aggregate tables.
