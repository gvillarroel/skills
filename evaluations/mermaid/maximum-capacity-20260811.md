# Mermaid Maximum-Capacity Evolution — 2026-08-11

## Objective

Exercise the terminal indexed or semantic style slot for every Mermaid 11.16.0 family that permits multiple elements, then evolve the runtime skill so an isolated agent can author the correct terminal case without being told the count.

## Corrected capacity model

- Mindmap exposes 12 visible indexed fills: the root uses `cScale0`, and 11 first-level branches use `cScale1` through `cScale11`. The capacity is not 14.
- Timeline, Radar, and Pie expose 12 indexed items.
- Treemap exposes 12 colored named hierarchy nodes after Mermaid's implicit transparent root. A named wrapper root consumes `cScale0`, leaving 11 colored direct children.
- Kanban exposes 10 reachable colored columns. Its rendered `section-1` through `section-10` classes map to `lighten(cScale2..cScale11, 10)`; generated rules for `cScale0` and `cScale1` are unreachable by columns.
- Journey exposes seven reachable distinct section classes and an eighth section that cycles to class zero, even though eight `fillType` theme variables exist.
- GitGraph exposes eight branches including main; Venn exposes eight sets. Sankey and XY use their configured palette lengths.
- Families with semantic roles or semantic classes exercise every exposed role/class. Uniform families remain explicitly unbounded instead of receiving invented maxima.

## Deterministic acceptance fixture

`skills/mermaid/assets/examples/mermaid-max-elements/` contains one source for each of the 31 public Mermaid families. The manifest records 25 finite-capacity cases and 200 finite slots. Eleven cyclic families have rendered geometry contracts. The validator:

- styles every source with colorset1 and colorset2 and checks idempotency;
- renders with pinned `@mermaid-js/mermaid-cli@11.16.0`;
- requires every terminal class, label, and count;
- binds indexed CSS selectors to the exact theme key that owns the geometry;
- reproduces Kanban's renderer-owned 10-point lightness transform;
- checks inline geometry colors for Pie, Sankey, XY, Treemap, and Venn;
- rejects declared-but-unused tail colors and transparent Treemap overflow.

The final render run passed 31/31 families, 62/62 styled diagrams, 62/62 SVG renders, 11/11 cyclic contracts, and zero findings. Seven fixture unit tests and the visual-palette transform test pass. The initial static negative control failed as intended before the full tail configuration was added.

## Evaluation-guided evolution

Native Harbor 0.18.0 used `gpt-5.6-luna` with medium reasoning, one attempt per case, no retries, and zero execution errors.

The first development cohort used digest `a0e62e386a8aac3273cd53505f8eef2eb0d7d3d316875ab4a28ce9252fad3ee1`. The pre-guidance candidate passed 2/3 because it stopped Journey before the required cycling boundary. Linking the new capacity reference from `SKILL.md` raised the same cohort to 3/3.

The first holdout digest was `d2016b904ccd7f072f663faba959acc0384cb4dd20623eaa14a2c34b8ae0a6ee`. A Git-HEAD baseline passed 0/3. The evolved candidate reached the correct item count in all three cases but passed 1/3 overall: the evaluator did not recognize Kanban's transformed colors, used an excessive Radar pixel-area threshold, and accepted a transparent twelfth Treemap child. Per the holdout protocol, these cases became development evidence and were not reused for promotion.

The corrected v2 development digest is `fa95e8b339116b94a2a6c3faaa869d81c279eff04450a16882288dda9dd28962`. Radar, corrected Treemap, and Kanban passed 3/3 with every routing, fidelity, metadata, render, palette, visual-palette, and counterfactual-influence subreward at 1.0.

Only then was the fresh disjoint v2 holdout digest `0de814cdf9b4fc80cf918f93bdea9c8901947452823544c9e94495290a24a45e` opened. Timeline, Pie, and Venn passed 3/3 with every subreward at 1.0, zero errors, and zero retries. Their palette coverage ratios were 0.25, 0.51, and 0.51; counterfactual influence ratios were 0.39, 0.50, and 0.67.

## Isolated runtime validation

Strict run `mermaid-maximum-capacity-20260811-spark-2` used `openai-codex/gpt-5.3-codex-spark` with medium thinking and the runtime payload only. It inferred and authored:

- Mindmap: 12 palette slots / 12 authored elements / terminal `Mind branch 11`;
- Journey: 7 distinct palette slots / 8 authored sections / terminal `Journey slot 08`;
- Kanban: 10 palette slots / 10 authored columns / terminal `Kanban slot 10`.

All eight exact outputs and 12 JSON-field assertions passed. The event stream contained valid JSON, the requested model, zero tool errors, no acceptance-fixture reads, and no out-of-scope reads. The copied skill payload remained unchanged. Independent pinned rendering produced valid SVG and PNG outputs with 12/12 distinct Mindmap fills, 7/7 reachable Journey fills plus the boundary cycle, and 10/10 distinct Kanban column fills.

The runtime payload contains 15 files / 406,298 bytes with SHA-256 `5a2a7c876adfaee419f62b99f63205747caebfd5026b0ed83deef407085a1aa4`; `SKILL.md` contains 60 physical lines.

## Reproduction commands

```powershell
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/test_max_elements.py
uv run --script evaluations/mermaid/test_max_capacity_dataset.py
uv run --script evaluations/mermaid/test_visual_palette.py
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/validate_max_elements.py --work-dir <fresh-dir> --npm-cache <cache-dir> --render-attempts 3 --report <report.json>
uv run --script evaluations/mermaid/build_harbor_dataset.py <fresh-run-dir> --run-id <run-id> --profile max-capacity-v2 --attempts 1
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-maximum-capacity.md --model openai-codex/gpt-5.3-codex-spark --thinking medium --mode json --strict --run-id <run-id> --timeout-seconds 900 --expect-output deliverables/standard/mindmap.mmd --expect-output deliverables/standard/journey.mmd --expect-output deliverables/extended/kanban.mmd --expect-output deliverables/capacities.json --expect-output deliverables/style-standard-report.json --expect-output deliverables/style-standard-check.json --expect-output deliverables/style-extended-report.json --expect-output deliverables/style-extended-check.json
```
