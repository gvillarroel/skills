# Mermaid Skill Evaluation — Harbor with Luna Medium

Date: 2026-08-09

## Outcome

The unified `mermaid` skill passes the per-task release gate in both the broad
version 4 study and the stricter version 6 visible-pixel study. Version 6's
selected development bundle passed 15/15; its sealed holdout passed 14/15 with
zero execution errors. A separate post-holdout replay of the exposed syntax
edge passed 3/3 after the deterministic fix.

Current quality is **high but not perfect (9.2/10)**. Routing and fidelity were
15/15 in the latest holdout, and all 14 renderable trials proved that the
requested palette occupied actual pixels and materially changed the image.
The remaining deduction reflects one parser-sensitive holdout failure and the
fact that its fix has targeted replay evidence rather than a new untouched
holdout. The original 14/15 remains unchanged.

## Latest Visible-Pixel Study

| Stage | Full reward | Routing | Palette | Visible pixels | Influence | Render | Fidelity | Metadata | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial development | 14/15 | 15/15 | 14/15 | 14/15 | 14/15 | 14/15 | 15/15 | 15/15 | 0 |
| Corrected development selection | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 0 |
| Sealed holdout | 14/15 | 15/15 | 14/15 | 14/15 | 14/15 | 14/15 | 15/15 | 15/15 | 0 |
| Post-holdout diagnostic replay | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |

The v6 verifier renders transparent PNGs, counts alpha-weighted pixels for the
expected palette groups, rejects colorset2 signatures under colorset1, and
rerenders a counterfactual palette. A source fails when its palette exists only
in frontmatter or unused SVG CSS. Measured holdout coverage ranged from
0.381553 to 0.964481 and counterfactual influence from 0.393134 to 0.991117.

## Frozen Profile

- Native Harbor 0.18.0 with a workspace-isolated WSL environment adapter
  because Docker was unavailable.
- Codex CLI 0.147.0 with `gpt-5.6-luna`, medium reasoning, and web search
  disabled.
- Mermaid 11.16.0, three attempts per task, four concurrent trials, and zero
  automatic retries.
- Exact outputs: `deliverables/diagram.mmd` and
  `deliverables/decision.json`.
- Independent rewards: routing, palette, render, fidelity, metadata, and the
  all-or-nothing aggregate reward.
- Promotion gate: at least two full passes out of three for every task, not an
  aggregate-average threshold.

## Final Cohort Coverage

The ten natural-language tasks covered XY, Sankey, Entity Relationship, Gantt,
Quadrant, Sequence, Pie, and Mindmap. They included an explicitly named chart,
an explicitly named diagram from concepts, and open requests that supplied data
but required the skill to choose the appropriate family. Five tasks required
the default colorset1 contract and five explicitly required colorset2.

| Split | Full reward | Routing | Palette | Render | Fidelity | Metadata | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 13/15 | 15/15 | 14/15 | 15/15 | 14/15 | 15/15 | 0 |
| Holdout | 13/15 | 15/15 | 14/15 | 15/15 | 14/15 | 15/15 | 0 |
| Combined | 26/30 | 30/30 | 28/30 | 30/30 | 28/30 | 30/30 | 0 |

All five development tasks and all five untouched holdout tasks met the 2/3
per-task gate. Standard-palette Sequence, Pie, Mindmap, XY, and ER cases were
3/3. The harder extended Gantt and Quadrant cases were 2/3 in both development
and holdout.

## Evaluation-Guided Improvements

Six study generations and live smoke runs executed 145 Harbor Luna trials in
total. Only frozen development and holdout cohorts are used for release scores;
diagnostic and post-holdout replay runs are reported separately.

1. Version 1 exposed evaluator defects in language-coupled flow labels,
   Sequence arrow counting, and a cyclic Sankey fixture. Its holdout remained
   sealed.
2. Version 2 exposed a symmetric ER-verifier defect plus real skill gaps around
   mandatory ER relation labels and visible Sankey units. The skill now uses
   `config.sankey.suffix`, and the styler preserves functional Sankey options.
3. Version 3 passed development 15/15 but failed holdout on Gantt colorset2
   rendering and translated Quadrant axis labels.
4. Version 4 added Gantt-specific Mermaid theme variables and a verbatim-label
   contract. Its newly frozen holdout passed the predefined gate.
5. A strict isolated Luna-medium `pi` run then found that parentheses in
   Quadrant axis endpoints do not parse in Mermaid 11.16.0. The compact
   reference now requires plain axis text. The corrected artifacts passed the
   strict Pi gates and independent SVG rendering, and the final bundle passed a
   6/6 Harbor regression across Gantt and Quadrant with every reward at 1.0.
6. Version 6 replaced source/SVG token checks with alpha-weighted raster
   coverage and counterfactual influence. It exposed unsupported Quadrant point
   classes in development and an unquoted-colon Quadrant axis in holdout. The
   family manifest and styler now remove unsupported semantic classes and quote
   each axis endpoint separately. Corrected development passed 15/15, the
   sealed holdout remained 14/15, and the explicit post-holdout replay passed
   3/3 without being counted as holdout.

## Residual Risk

The latest holdout's only failure was an invalid unquoted colon in one Quadrant
axis endpoint. The deterministic styler now quotes both endpoints and the
three-attempt replay passed, but that replay cannot replace untouched holdout
evidence. A consumer that requires deterministic 100% compliance should retain
the bundled style check, independent render, literal-label review, and visible-
pixel palette gate as delivery checks.

The publication summaries and decisive metrics from the superseded organized
study snapshots are consolidated in this record to minimize durable files. The
complete protocol is `harbor-luna-medium-protocol.md`; raw jobs, prompts,
responses, rendered evidence, and reports stay under ignored
`evaluations/runs/` storage.
