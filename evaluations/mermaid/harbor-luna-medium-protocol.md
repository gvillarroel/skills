# Mermaid Harbor Evaluation Protocol

## Objective

Measure whether the isolated `mermaid` skill can honor explicit diagram requests,
infer the most informative Mermaid family from prose or tabular data, preserve the
complete data contract, and apply the correct palette policy.

## Fixed Profile

- Harbor: 0.18.0
- Agent: Codex
- Codex CLI: 0.147.0
- Model: `gpt-5.6-luna`
- Reasoning effort: `medium`
- Attempts: three fresh trials per task
- Renderer: Mermaid CLI 11.16.0
- Skill payload: only `skills/mermaid`
- Development tasks: five
- Sealed holdout tasks: five

The model exception from the repository's default Spark profile is explicit and
user-requested. A workspace-scoped WSL adapter is used because Docker is not
available on the evaluation host. Every trial still runs through Harbor's native
job, trial, lock, trajectory, verifier, reward, and reporting flow.
Per-trial WSL roots are removed only after Harbor collects agent logs,
deliverables, verifier output, and rewards; the native job remains the durable
raw evidence.

## Coverage

The ten naturalistic prompts include all of these user-request forms:

- create a named chart from supplied data;
- generate an appropriate diagram from concepts and relationships;
- choose a visualization from supplied quantitative data without naming a type.

The version 6 visible-palette cohort covers explicit and inferred routing across XY, Sankey,
Sequence, Entity Relationship, Pie, Mindmap, Gantt, and Quadrant. Gantt and
Quadrant each appear once in development and again with different facts and
labels in holdout. Five tasks require the default colorset1 palette. Five
explicitly request extended, full-color, or multicolor styling and therefore
require colorset2.

## Independent Gates

The tested agent creates only `deliverables/diagram.mmd` and
`deliverables/decision.json`. Hidden Harbor verifiers independently require:

1. the expected family declaration and exact canonical family ID;
2. colorset1 by default or colorset2 only after an explicit extended request;
3. YAML `theme: "base"`, generated colorset metadata, and no JSON init directive;
4. a successful independent Mermaid 11.16.0 SVG render without error markers;
5. expected palette colors painted on visible geometry in a transparent PNG,
   with per-family minimum pixel coverage and required semantic color groups;
6. a material raster difference after replacing every palette signature color
   with counterfactual sentinels;
7. exact labels, units, directions, order, values, dates, durations, weights,
   coordinates, attributes, or cardinalities supplied by the task;
8. complete decision metadata with a non-empty rationale.

Each trial emits binary `reward` plus separate `routing`, `palette`, `render`,
`visual_palette`, `palette_influence`, `fidelity`, and `metadata` rewards.
Naturalistic quality passes only when at least two of three attempts pass for
every task. Execution exceptions remain errors and are never reclassified as
verifier failures.

## Visible-Pixel Method

Render the candidate twice with Mermaid CLI 11.16.0: once unchanged and once
after replacing colorset signature tokens with high-contrast sentinel colors.
Decode the PNGs without browser DOM assumptions, weight every pixel by alpha,
and composite comparisons over white. Count a palette color only when at least
24 effective pixels are visibly painted. Require colorset1 to show its primary
group while painting no extended signature colors. Require the relevant
accent, warning, success, and special groups for multicolor families such as
Sankey and Quadrant, and accent, warning, and success for state-rich Gantt
fixtures. Coverage floors vary by family from 0.1% to 15% so sparse line work
and large filled regions are judged proportionately.

The counterfactual must change at least 32 effective pixels and 0.05% of the
visible union. This catches palette declarations or unused SVG CSS that never
affect the displayed chart. One bounded rerender is allowed only to absorb a
transient Chromium launch failure; it does not relax syntax, coverage, color,
or counterfactual thresholds.

## Study Ordering

Register and freeze development and holdout datasets before starting any stage.
Run and report development first. Bind its native job and final report by SHA-256,
complete the development stage, and release holdout exactly once against that
unchanged selection evidence. Only then run the holdout stage. Keep task roots,
native jobs, trajectories, verifier details, and reports private under ignored
evaluation storage; publish only source-path-free study indexes and reviewed
aggregate result tables.

## Protocol Revision

The first development-only study was closed without releasing holdout after it
exposed three evaluator defects: language-coupled branch labels, an arrow counter
that did not recognize Sequence syntax, and a cyclic Sankey fixture that Mermaid
cannot render. Version 2 removes those defects before registering a new pair of
datasets. No skill change was selected from the invalid study.

The second development-only study was also closed before holdout release. It
found one verifier defect—rejecting a cardinality-equivalent reverse ER
relationship—and two actionable instruction gaps: ER relationships must include
labels to render, and Sankey units must remain visible through the diagram's
configured value suffix. Version 3
corrects the symmetric ER check and evaluates the revised skill on a newly
registered dataset pair.

Version 3 passed all 15 development trials but failed the released holdout
gate: Gantt did not expose an extended token in the rendered SVG, and two
Quadrant trials translated literal Spanish axis labels. Version 4 adds
Gantt-specific theme variables and an explicit no-translation label contract,
then uses the exposed v3 failures only as development cases and registers a new
holdout cohort.

After version 4 completed, an isolated Luna-medium `pi` render exposed one
additional Mermaid 11.16.0 grammar edge: parentheses are invalid in Quadrant
axis endpoint text. The compact authoring reference now requires plain axis
text. A version 5 Harbor regression then ran the final bundle on Gantt and
Quadrant for three attempts each and passed all 6/6 trials across every reward.

Version 6 replaces SVG-token presence with raster-visible palette coverage and
counterfactual influence. The first development pass exposed unsupported
Quadrant point classes; after removing those classes and correcting the family
capability manifest, the selected development bundle passed 15/15. The sealed
holdout passed 14/15 with zero execution errors and exposed one additional
grammar edge: unquoted colons in Quadrant axis endpoints. The post-holdout
styler now quotes each endpoint separately, preserving the visible punctuation;
a clearly separated Luna-medium diagnostic replay passed 3/3. The replay does
not alter the original holdout result.
