# Unified Mermaid Skill Evaluation — 2026-08-09

## Release Decision

The unified `mermaid` skill is ready for use with grade **A**. The final fixed-payload cohort scored 97.5, 100, and 100 (mean 99.17; median 100). All three runs passed the strict isolated harness, and two of three passed every quality gate. This meets the repository repetition policy.

The release gate required all eight cases to pass diagram routing, source and rendered palette checks, Mermaid 11.16.0 rendering, manifest accuracy, and data fidelity. A score above 90 alone was not sufficient.

## Consolidation and Pruning

The release replaces `mermaid-animated-svg` and `mermaid-colorset-styler` with one self-contained `skills/mermaid/` bundle. The retained runtime surface is:

- one `SKILL.md` and agent descriptor;
- one compact selection/authoring reference;
- one animation reference;
- one versioned Mermaid 11.16.0 family manifest;
- one deterministic colorset styler; and
- the existing modular SVG animation engine.

The two old skills contained 431 files and 11,187,054 bytes. The unified skill contains 36 files and 401,976 bytes: 91.6% fewer files and 96.4% fewer bytes. Acceptance galleries, generated SVG/PNG media, duplicate family data, obsolete prompts, historical validators, and retired Pages generators were removed.

## Evaluation Contract

The isolated prompt is `evaluations/pi-prompts/mermaid-authoring-selection.md`. It requests 13 exact outputs and eight independent cases:

| Case | Request mode | Expected family | Palette |
| --- | --- | --- | --- |
| 01 | Explicit | Flowchart | colorset1 |
| 02 | Explicit | Sequence | colorset2 |
| 03 | Infer from schema and cardinality | ER | colorset1 |
| 04 | Infer from weighted transfers | Sankey | colorset2 |
| 05 | Infer from lifecycle transitions | State | colorset1 |
| 06 | Infer from quarterly values | XY chart | colorset1 |
| 07 | Infer from dates and dependencies | Gantt | colorset1 |
| 08 | Infer from two-axis coordinates | Quadrant | colorset2 |

Every run used `openai-codex/gpt-5.3-codex-spark`, JSON strict mode, exact output checks, unchanged-skill integrity, zero tool errors, no acceptance-fixture reads, and no render/animation-resource reads because rendering was delegated to the evaluator.

## Final Cohort

| Run | Strict harness | Score | Full quality pass | Routing | Palette | Render | Fidelity | Manifest |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| `mermaid-authoring-selection-20260809-spark-13` | Pass | 97.5 | Fail | 8/8 | 8/8 | 8/8 | 7/8 | 8/8 |
| `mermaid-authoring-selection-20260809-spark-14` | Pass | 100 | Pass | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| `mermaid-authoring-selection-20260809-spark-15` | Pass | 100 | Pass | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |

Aggregate accuracy was 24/24 for routing, rendered palette, rendering, and manifest fields, plus 23/24 for fidelity. The failed fidelity case used valid state identifiers but dropped the supplied human labels `In Progress` and `Waiting on Customer`; the other two runs preserved them through aliases. The skill already carries the explicit alias rule, and the measured 2/3 release threshold passes.

## Findings Promoted into the Skill

Developmental runs exposed and corrected reusable authoring failures:

- state labels with spaces must use `state "Human label" as StableId` and transitions must use the ID;
- ER multi-key constraints require `PK, FK`, and attributes with missing source types use the neutral `unknown` type instead of invented types;
- Mermaid 11.16.0 Gantt tasks accept one `after <id>` start expression, so multiple prerequisites must be represented through the latest truthful predecessor plus a human label;
- Sankey bodies accept three-column CSV, not an inline `title` directive; titles and units belong in frontmatter; and
- canonical family IDs such as `xyChart` must not be derived from case-sensitive declarations such as `xychart`.

The browser review also exposed that frontmatter could name colorset2 without making extended colors visible. The styler now uses family-specific Sequence variables, dynamic Sankey `nodeColors`, and actual Quadrant theme variables. Extended Sequence renders blue accents, Sankey renders all five extended colors, and Quadrant renders blue with colorset2 pastel fields. Standard renders contain no extended tokens.

## Raster-Visible Palette Regrade

The final eight-case artifact was regraded after replacing SVG-token matching
with transparent PNG inspection and a counterfactual rerender. It scored 100/100
with 8/8 routing, palette, render, fidelity, and manifest checks. Every case
painted the expected colors on visible geometry and changed materially when its
palette tokens were replaced. Palette coverage ranged from 0.004046 for sparse
Flowchart strokes to 0.974919 for filled Quadrant regions. Extended Sankey and
Quadrant rendered five distinct colors each; colorset1 cases rendered no
forbidden extended signature pixels.

## Visual and Runtime Review

Playwright reviewed the final gallery at 1440×1200 and 390×844. Both viewports showed eight cards, eight loaded SVGs, zero horizontal overflow, and no broken images. The only console event was the local server's expected missing `favicon.ico`. Screenshots are kept locally under `projects/mermaid-unification/artifacts/screenshots/`.

A final animated Sequence smoke produced a faithful colorset2 SVG with 24 animated elements. The Mermaid CLI returned one transient `[object Object]` render failure; the immediate isolated retry and the animated rerun both passed.

## Release Validation

The following release checks passed:

```powershell
uv run --script scripts/build-pages.py
uv run --script scripts/validate-diagram-type-coverage.py --report projects/mermaid-unification/artifacts/reviews/diagram-type-coverage.json
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
git diff --check
```

The coverage report confirms 31/31 Mermaid families and 40 current declarations for Mermaid 11.16.0. Pages rebuilt with 401 files and no retired Mermaid gallery references.

Primary syntax decisions were checked against the official Mermaid documentation for [theming](https://mermaid.js.org/config/theming.html), [ER diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), [Sankey diagrams](https://mermaid.js.org/syntax/sankey), and [Quadrant charts](https://mermaid.js.org/syntax/quadrantChart).
