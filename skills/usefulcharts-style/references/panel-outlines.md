# Compact outline panels

## Contents

- [Choose the representation](#choose-the-representation)
- [Input contract](#input-contract)
- [Build and inspect](#build-and-inspect)

Use this route for classifications with unequal subtrees, or a sectioned lineage
whose long unbranched prefix wastes a full-page rank grid. The output is a linked
field guide: visible local branches, measured family panels and explicit paired
references between panels. It is an alternative composition, not an automatic
claim of visual equivalence to a continuous UsefulCharts tree.

## Choose the representation

Keep a shared calendar when elapsed time must be comparable. In particular, a user
request for time on x cannot be satisfied by these outlines. Codes in a taxonomy
are identifiers, not dates or quantities. State the position semantics explicitly.

Prefer continuous drawn connectors when following one long cross-family path is
the principal reading task. Use numbered cross references when local browsing is
more important and full-page cables would dominate the page. Every reference must
name its counterpart, show direction and type, and appear at both endpoints. A
shared group, matching color or adjacent position is never a relationship.

## Input contract

Supply a JSON object with:

- `id`, `title`, `position_semantics`, `reading_note` and `source_note`.
- `groups`: `{id, label, color}`. Use six-digit colors with 4.5:1 contrast against
  paper `#f7f7f7`; these are colored text and strokes, not pale panel fills. Examples:
  `#4f4f4f`, `#9e1b32`, `#696969`, `#9e1b32`, `#98700c`, `#4f4f4f`.
- `nodes`: `{id, group, label, date_label?, detail?}`. A classification identifier
  may use `code` instead of `date_label`. Print the entire date qualification or
  context that is required for interpreting the record; arbitrary metadata is
  retained but is not automatically displayed. Node and group IDs are unique.
- `edges`: `{id, source, target, kind, portal?}`. Supported types are `branch`,
  `contains`, `succession`, `influence` and `uncertain`. `branch` and `contains`
  inside a group use local solid connectors. Other types and inter-group links
  use explicitly typed, numbered references. Set `portal: true` for an additional
  incoming link when a local node has more than one structural parent; preserve
  both parents. A local outline must be acyclic with at most one drawn parent.
- Optional `eyebrow`: a short subject-specific line above the title.

No coordinates, ranks, node fonts or page height are needed. Each record is
rendered once, even when several incoming links point to it. All groups must have
records. Group source order is retained within each packed column; the columns
are balanced by measured height. Classification roots matching the panel title
become its visible heading rather than being repeated above the same record.

Do not pass partnerships, time events, annotations, insets or source-prescribed
geometry into this focused route. Use their corresponding construction routes.
The command rejects unsupported rich objects instead of quietly dropping them.

## Build and inspect

```sh
uv run --script <skill-dir>/scripts/create_panel_poster.py brief.json --output-dir result
```

The bundle contains `poster.svg`, `poster.html`, `poster.png`, `poster.pdf`,
`source.json`, `layout.json` and `browser.json`. Keep the initial brief separately
when retaining a before/after comparison. The emitted `source.json` is also a
valid input for rerendering the same bundle: it is loaded completely before any
output is written and its data values remain unchanged. Honor exact requested paths by choosing the correct output directory or
copying the resulting files to those paths, then auditing the actual delivered
SVG and source. Execute the CLI without reading implementation or test files.

The default is two 520-unit panels. Use `--columns 1` through `--columns 4` and
`--panel-width 420` through `--panel-width 1000` when inspection supports a change.
The helper places short identifiers beside names, stacks long qualifications,
reserves wrapped labels and paired references, and balances column heights.
When the shorter column has sufficient free space, the reading guide occupies
that pocket; it remains separate from the represented entities.

Open the PNG and inspect the entire composition and its densest junction. Check:

1. Can a reader distinguish family, record, identifier and relationship type?
2. Does every numbered reference have two named, directional endpoints? Follow
   several of them in the HTML viewer. Verify an incoming contribution does not
   imply that two organizations or objects fully merged.
3. Are panel widths justified by real content? Are dates consuming unnecessary
   separate lines? Are the remaining gaps useful for a reading guide or sourced
   context? Do not add filler, repeat facts, shrink type or move calendar anchors.
4. Does the chosen representation answer the question better than the rejected
   tree? Record the cost of cross references: distant paths require a lookup.

Retain a failed first render or failure report, then rerender the repair. Compare
the same selected node and typed-edge inventory, meaningful context and actual
type sizes. A smaller area with the same readable facts is a compositional gain;
it does not establish the separate reference-density minimum.

For independent reinspection of the delivered paths:

```sh
uv run --script <skill-dir>/scripts/audit_panel_poster.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

The audit checks browser text bounds, text collisions, contrast, complete visible
identity/date/context fields, the embedded source, and local/cross-reference
inventories. It does not independently research facts, certify edge aesthetics,
or replace full-page human visual criticism. Source rows that cannot be verified
or read do not count toward useful knowledge density.

Read `browser.json` as structured evidence: `status` is `pass` or `fail`,
`findings` lists violations, and `records[].fields` contains `label`, `kicker`
and `detail`. The visible `code` or `date_label` is reported as `kicker`; neither
field is inferred from a node ID. `links` and `portals` retain relationship IDs,
endpoints and types. Keep this technical result separate from direct image
inspection. If the active runtime cannot see images, state that limitation and
leave visual acceptance pending instead of claiming that its pixel review passed.
