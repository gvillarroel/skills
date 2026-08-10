# Mermaid Progressive-Disclosure and File-Count Pareto Study

Date: 2026-08-09

## Outcome

Harbor selected and promoted `reference-safe-label`. The promoted bundle is the
first candidate in this study to pass both development and a newly sealed,
untouched holdout at full reward. It is the canonical `skills/mermaid` bundle.

The current quality assessment is **10.0/10 under the frozen evaluation
contract**. This score means 20/20 selected-candidate trials passed every
required reward across development and holdout; it is not a claim that every
possible Mermaid prompt is solved.

## Optimization Result

| Measure | Frozen baseline | Promoted bundle | Change |
| --- | ---: | ---: | ---: |
| Runtime files | 36 | 14 | -22 (-61.1%) |
| Runtime bytes | 401,976 | 391,086 | -10,890 (-2.7%) |
| `SKILL.md` physical lines | 87 | 56 | -31 (-35.6%) |
| Animation family modules | 23 | 1 | -22 (-95.7%) |

Relative to the two pre-unification skills, the complete evolution reduced the
runtime from 431 files / 11,187,054 bytes to 14 files / 391,086 bytes: 96.8%
fewer files and 96.5% fewer bytes.

The compact core now routes conditional reads explicitly:

- Load `diagram-selection.md` for selection, data authoring, orientation,
  fidelity, or semantic color judgment.
- Load `diagram-types.json` only for exact declarations, aliases, canonical
  family IDs, or `classDef` capability.
- Load `animation.md` only for animation or custom choreography.
- Execute deterministic scripts without reading their implementation except
  while diagnosing a failed command.

All 12 selected-candidate development traces read the authoring references
needed by their tasks and zero read animation material. Two trials inspected
the first part of the styling entry point only after discovering that `uv` was
absent in the isolated runtime and recovering with `python3`. The supplementary
strict Spark forward test read only the prompt, `SKILL.md`, the two authoring
references, and its generated deliverables; it did not read animation material,
script source, examples, repository documents, or sibling skills.

## Frozen Protocol

- Harbor 0.18.0 with the workspace-isolated WSL environment adapter.
- Codex CLI 0.147.0, `gpt-5.6-luna`, medium reasoning, web search disabled.
- Mermaid 11.16.0, two attempts per task, four concurrent trials, no retries.
- Six development tasks and four untouched holdout tasks.
- Baseline and selected candidate both evaluated: 24 development trials and 16
  holdout trials.
- Exact all-or-nothing thresholds of 1.0 for `routing`, `palette`,
  `visual_palette`, `palette_influence`, `render`, `fidelity`, and `metadata`.
- Development dataset SHA-256:
  `6b1d1f1538d7b24a1f41d62b2edf9d3c16bd23e0949b67b3bd0b26b3fbbfb36c`.
- Holdout dataset SHA-256:
  `e48ff301bfff01d1621e10b6c57ade74d23061fefb2fd91ca9f4d261a785934e`.
- Promoted skill digest:
  `sha256:f0eabb48e1b85e7cc08f276911d4a5cd5378235b667bb1906fdfd6d731231970`.

The final configuration is `config-v7-generation-000.yaml`. The raw archive,
jobs, SVG/PNG renders, counterfactual renders, trajectories, and promotion seal
are under ignored
`evaluations/runs/mermaid-pareto-disclosure-files-20260809-v7/`.

## Development

| Candidate | Full passes | Mean reward | Errors | Qualified |
| --- | ---: | ---: | ---: | --- |
| Frozen 36-file baseline | 6/12 | 0.500 | 0 | No |
| `reference-safe-label` | 12/12 | 1.000 | 0 | Yes |

The selected candidate passed both repetitions of explicit Flowchart, inferred
State, inferred extended Sankey, two inferred ER schemas, and the reversed ER
orientation boundary. Every required reward was 1.0. Standard renders had zero
forbidden extended-color pixels. The extended Sankey showed five visible
palette colors and 16% effective palette coverage.

Earlier generations remain recorded but are not promotion evidence. Versions
1–5 exposed evaluator or ambient-skill isolation defects. Version 6 was the
first clean isolated development run; it identified one genuine skill defect:
bare multiword ER relationship labels do not parse. The conditional authoring
reference now requires quoted multiword labels. Version 6's exposed holdout was
not used. Version 7 froze the corrected candidate before the final holdout was
authored and generated.

## Sealed Holdout

Harbor's decision was **PROMOTE**.

| Case | Expected family | Palette | Baseline | Candidate |
| --- | --- | --- | ---: | ---: |
| Reversed application/API-key schema | ER | colorset1 | 0/2 | 2/2 |
| Storage parts of a 200 GB total | Pie | colorset1 | 2/2 | 2/2 |
| Product-delivery concept hierarchy | Mindmap | colorset1 | 2/2 | 2/2 |
| Release schedule and statuses | Gantt | colorset2 | 2/2 | 2/2 |
| **Overall** |  |  | **6/8 (0.750)** | **8/8 (1.000)** |

The candidate gained 0.250 mean reward, had zero errors, no regressed cases,
complete required rewards, and matching declared/observed profiles.

The evaluator rendered SVG and transparent PNG, measured alpha-weighted pixels,
rejected colorset2 signatures under colorset1, and rerendered counterfactual
palette replacements. Visible results were:

- ER colorset1: 26.96% palette coverage, two visible palette colors, 59.12%
  counterfactual influence, zero forbidden extended pixels.
- Mindmap colorset1: 29.88% coverage, one visible palette color, 30.94%
  influence, zero forbidden extended pixels.
- Pie colorset1: 41.41–41.61% coverage, one visible palette color,
  42.36–42.58% influence, zero forbidden extended pixels.
- Gantt colorset2: 78.48–80.48% coverage, four visible colors, all required
  accent/warning/success groups present, and 88.67–90.62% influence.

These checks prove that palette configuration affected the displayed geometry;
unused frontmatter tokens or unused SVG CSS could not pass.

## Post-Promotion Validation

- Canonical bundle is byte-identical to Harbor's promoted candidate copy.
- All Python files compile and the skill quick validator passes.
- All 23 representative animated SVG families reproduce the prior exact
  SHA-256 output after consolidating the family modules; 23/23 hashes match.
- `validate-pattern-ids.py`, `validate-skills.py`,
  `test-skill-independence.py`, and `check-repo-payload.py` pass.
- Strict isolated Spark sanity run
  `mermaid-pareto-v7-post-promotion-spark-1` passed exact output, event,
  integrity, and read-surface gates. Independent rendering scored 100/100 over
  Flowchart, Sequence, ER, Sankey, State, XY, Gantt, and Quadrant, with zero
  findings and visible/counterfactual palette checks passing in every case.

