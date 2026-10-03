# Native fallback panels

## Contents

- [Complete native workflow](#complete-native-workflow)
- [Hub: unordered connectivity](#hub-unordered-connectivity)
- [Matrix: independent comparison dimensions](#matrix-independent-comparison-dimensions)
- [Taxonomy: containment without chronology](#taxonomy-containment-without-chronology)
- [Cycle: real recurrence](#cycle-real-recurrence)
- [Boundary: semantic objects and explicit relations](#boundary-semantic-objects-and-explicit-relations)
- [Review and limitations](#review-and-limitations)

Use this builder when no specialist is available and a panel fits one of the five
supported forms. It sizes text from the requested display scale, wraps within
budgets, separates icons from labels, gives arrowheads a fixed size, and exports
semantic connection ports. It requires only Python/uv, not another skill.
Other forms and elaborate artwork still use specialist or custom SVG sources.

## Complete native workflow

For standard `out/plan.json`, `out/figure.svg`, `out/report.json`, `out/audit.json`,
and `out/preview.png`, author `out/brief.json` with source paths such as
`panels/connectivity.svg`. Run the complete pipeline:

```text
uv run --script <skill-root>/scripts/render_diagram.py --brief out/brief.json --output-dir out --inspect --overwrite
```

Read `out/render-status.json` and the returned `ok`. Correct the authored brief
with a complete JSON write or parse/update/serialize operation, then rerun the
same command. It rebuilds panels, their measured ports, the plan, the composed
SVG, the audit, and the preview together. An expected draft finding returns
`ok: false`; do not use an older figure/audit as evidence of success. Review the
preview. Finish with the same command **without `--inspect`**, and write the
requested review. Supplied imported panels may coexist without a `diagram` field;
prepare/measure those sources first. The granular commands below support other
requested artifact names or a specialist's pipeline.
For repeated identity links between clearly named/colored objects, use `label:""`
with one shared explanatory key when this avoids duplicate labels across narrow
gutters. Keep each link's full meaning in `relation` and preserve every requested
connection.

Author `brief.json` using the composition contract. Add `diagram` to each native
panel and leave its initial `ports` empty. Keep `source` as its exact intended SVG
path. After choosing spans, populate only the compact data for the chosen types.

```text
uv run --script <skill-root>/scripts/build_panels.py --spec brief.json --output-spec composition.json --report panel-build.json --overwrite
```

Inspect `ok`. On `false`, revise the brief using the specific budget/schema
finding; the diagnostic report is saved, but no new plan or SVG is published.
An invalid/colliding/unwritable report path can only be reported on stdout.
On `true`, compose the generated
`composition.json`, not the original brief. When revising your own output, use
`--overwrite`. If the user requests `out/plan.json`, make that the output-spec.
Do not rename exact outputs. Preserve the brief as editable source.
For revisions, parse/update/serialize the current JSON or rewrite the complete
brief with a write operation. Do not use text-match editing on these JSON files.

Every node needs an `id` in lowercase hyphen-case. `label` is visible; optional
`detail` is secondary visible information, normally one short line. Each node
exports object geometry and bound `<id>-left`, `<id>-right`, `<id>-top`, and
`<id>-bottom` ports. Refer to
these in top-level cross-panel links, such as `topology.workspace-right` to
`synthesis.workspace-left` for the same shared workspace. The output report lists all ports. Pick ports attached
to the intended semantic object; automatic routing avoids node interiors.
Read [connectors-and-surfaces.md](connectors-and-surfaces.md) when choosing sides
or importing custom sources. Do not replace generated bindings with guessed points.

Optional `icon` is a local SVG path relative to the brief, or one of the neutral
pictograms `editor`, `assistant`, `runner`, `library`, `cloud`, `person`, `grain`,
`seed`, `plant`, `inspect`, `shelf`, `envelope`, `jar`, `review`. They are generic
symbols, never brand substitutes. External SVGs must satisfy the import contract;
prepare CSS-bearing exports first. Brand artwork is preserved without recoloring.

For cross-panel color identity, use the shared concept registry and native
`concept` fields from [shared-colors.md](shared-colors.md). These produce consistent
solid borderless category surfaces or swatches and auditable SVG bindings.
Choose pure black or white for card labels by their actual fill contrast;
an icon and its semantic swatch may coexist. Literal local `color` values below
remain supported for isolated encodings, but recurring categories use `concept`.

## Hub: unordered connectivity

```json
{"type":"hub","center":{"id":"workspace","label":"Shared workspace","icon":"library"},
 "peers":[{"id":"editor","label":"Editor","icon":"editor"},
          {"id":"assistant","label":"Assistant","icon":"assistant"},
          {"id":"ci","label":"CI runner","icon":"runner"}]}
```

Supports 2-4 peers; use a specialist for larger or non-hub networks. Links have
no arrows. It does not claim peer-to-peer edges or any execution order. Peer
cards are compact; omit detail here and express permissions in the matrix.

Use `"shape":"ellipse"` on a peer or center when the subject needs an elliptical
enclosure; the default is a rounded rectangle. Text uses an inscribed budget and
ports touch the actual curve. For two peers, the center occupies the right side
and the peers stack on the left. Add `enclosure` to place the same connections
inside one named neutral container; preserve the same concept IDs in both views:

```json
{"type":"hub","enclosure":{"id":"facility","label":"Facility"},
 "center":{"id":"repository","label":"Repository"},
 "peers":[{"id":"sensor-a","label":"Sensor A","shape":"ellipse","concept":"sensor-a"},
          {"id":"sensor-b","label":"Sensor B","shape":"ellipse","concept":"sensor-b"}]}
```

Keep ellipse labels brief; put comparison details in the matrix when an ellipse's
text budget rejects them. Do not make a generic pictogram stand for an unrelated
concept. Use the exact short label when no recognizable symbol is available.

## Matrix: independent comparison dimensions

```json
{"type":"matrix","id":"permissions","columns":["Tool","Source","Proposals","Builds"],
 "columnWeights":[1.4,1,1,1],
 "rows":[{"id":"editor","label":"Editor","icon":"editor","values":["R/W","—","—"]},
         {"id":"assistant","label":"Assistant","icon":"assistant","values":["R","P","—"]},
         {"id":"ci","label":"CI runner","icon":"runner","values":["R","—","B"]}],
 "note":"R read · W write · P propose · B publish"}
```

There is exactly one fewer `values` entry than columns: the first cell is the row
label. Values can also be `{"text":"paper envelope","icon":"envelope"}` or
`{"text":"blue label","color":"#007298"}`. Category colors appear as swatches
beside dark text, and as bands above taxonomy headings. Bright yellow remains
yellow without making the essential label hard to read. A visible note/key must decode
abbreviations. Supplied capabilities, colors, and units remain authoritative.

## Taxonomy: containment without chronology

```json
{"type":"taxonomy","id":"catalog","root":"Seed library",
 "groups":[{"id":"grains","label":"Grains","color":"#007298","items":["Oats","Barley"]},
           {"id":"legumes","label":"Legumes","color":"#9e1b32","items":["Peas","Beans"]}]}
```

Supports 1-4 groups in parallel containers. Area has no quantitative meaning.
Groups fit their actual content and align items below the heading, even when the
allocated panel is tall. Use a proper tree specialist for multiple hierarchy depths.

## Cycle: real recurrence

```json
{"type":"cycle","closed":true,"steps":[
 {"id":"borrow","label":"Borrow seeds","icon":"person"},
 {"id":"grow","label":"Grow plants","icon":"plant"},
 {"id":"divide","label":"Divide harvest","detail":"Keep some; return rest","icon":"seed"},
 {"id":"return","label":"Return remainder","icon":"library"},
 {"id":"inspect","label":"Inspect packets","detail":"Before shelving","icon":"inspect"},
 {"id":"shelve","label":"Shelve seeds","icon":"shelf"}]}
```

Supports 3-8 explicit ordered steps with a closing link. Choose cycle only when
the brief includes recurrence. Shorten wording while retaining conditions; do
not drop the distinction between kept and returned material to make a box fit.

## Boundary: semantic objects and explicit relations

```json
{"type":"boundary","id":"workspace","label":"Shared workspace",
 "nodes":[{"id":"source","label":"Source","detail":"All peers read; editor writes"},
          {"id":"proposals","label":"Proposals","detail":"Assistant proposes","icon":"assistant"},
          {"id":"review","label":"Human review","detail":"Approval before source change","icon":"review"},
          {"id":"builds","label":"Build results","detail":"CI publishes","icon":"runner"}],
 "groups":[{"id":"review-boundary","label":"Human review boundary","nodes":["proposals","review"]}],
 "relations":[{"from":"proposals","to":"review","directed":true},
              {"from":"review","to":"source","directed":true}]}
```

Supports 1-5 objects and optional named groups around contiguous node subsets.
Use an explicit group when the brief requires a boundary around proposals;
a separate review card alone does not show that containment. Stacking itself is
spatial, not a process: only declared
relations generate arrows. Adjacent relations use the gap; longer relations use
side lanes. Put the relation meaning in concise node/detail wording and accessible
panel description. Do not add an arrow to imply unspecified causal behavior.

## Review and limitations

Run the composition and browser audit after building. The native builder reduces
geometry work but cannot validate factual claims, symbol recognition, contrast,
or the semantic subject of a title. Verify who does what in every headline: a
member returning seed is not the library borrowing it. Keep the exact requested
canvas and `displayWidth`; changing the viewing scale to pass typography is not
a layout repair. Fix excess text by removing repetition or reallocating space.
The helper returns a budget error rather than shrinking essential text. Do not
fall back to smaller hand-authored text just to avoid that error.
