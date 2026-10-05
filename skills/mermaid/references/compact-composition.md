# Compact Mermaid Composition

Use this reference before laying out or reviewing connected diagrams, including flows, state/class/ER relationships, interactions and concept trees. Default to as much compaction as the actual rendered content can safely support. These native defaults target Mermaid 11.16.0.

## Compactness with hard readability limits

Treat complete labels, readable type, visible arrowheads and unambiguous relations as constraints. Optimize empty space and route length only among layouts that pass those constraints. A smaller canvas that loses one of them is a rejected revision.

Preserve every required concept and relation, marker semantics, explicit user dimensions and spacing. Do not shorten factual labels, merge concepts, remove relations, shrink fonts, scale the whole SVG down or clip paths to claim compaction. Keep quantitative charts and proportional timelines governed by their scales and information needs; do not apply diagram rank packing to chart marks, axes or numeric time positions.

Start from the native defaults below, render, then inspect the actual content envelope and busiest route neighborhood at the intended display size. Reclaim unnecessary outer margins and oversized boxes first. Next compare orientation, declaration ordering consistent with the facts, nearby grouping and rank separation to bring linked concepts closer and shorten detours. Reuse released pockets when it keeps the reading order clear. For native sequence diagrams preserve event order, participant identity, activation extents and message-label clearance.

Keep a last passing render while tightening a specific gap or route. Compare the candidate and previous render at the same display width, plus full-size details; smaller raw dimensions alone do not establish improvement. Accept only when:

- Every required label remains complete, readable and inside its intended region; text does not overlap other text, lines, heads or unrelated shapes.
- Shafts and complete heads remain visible with their required contrast, and the target direction and attachment are apparent. Reserve the full head envelope and a short visible shaft near each endpoint; a configured rank gap is not evidence of this clearance.
- Each relation can be followed from its source to its target. Parallel routes stay distinguishable; unrelated edges do not acquire a shared trunk or apparent junction. Crossings are sparse and clearly distinct from joins.
- Group titles, notes, cardinalities, ports and semantic glyphs retain clearance. A short edge must still fit its label and markers.
- The canvas reduction or shorter route is real without a new readability or fidelity defect.

If an attempted reduction fails, restore the last passing spacing or move the particular neighboring group. Stop when there is no concrete safe reduction left; report the scope of comparisons when claiming a measured gain, without claiming a global optimum. Read [arrow contrast](arrow-contrast.md) for head geometry and [editorial diagram contracts](editorial-diagram-contracts.md) when traceability or source fidelity needs more review.

Store a proposed source at a path such as `comparison/candidate.mmd`, outside the skill but inside the task workspace. Style and render that exact relative path with the usual bundled commands, keeping its SVG at `comparison/candidate.svg`. Use a workspace directory instead of `/tmp`: a shell and a native Python process can resolve a temporary path differently, particularly on Windows. Preserve the delivered source and last passing SVG until the candidate has been inspected.

## Color priority

1. Keep the canvas white and distinguish ordinary category boxes with opaque solid fills and zero decorative border width. Containers remain quiet layout surfaces.
2. Use brand red `#9e1b32` first. `csPrimary` and default unclassified boxes use a solid red fill and white inside text. For every other fill choose exactly black or white by the greater WCAG relative-luminance contrast.
3. Reuse roles when meaning repeats. The nine semantic classes use the first nine unique entries of the selected bundled `solidSequence`; every class has no decorative stroke. Preserve connector and class-compartment lines.
4. For indexed categories consume the entire usable `solidSequence`, excluding the actual canvas, before recycling a fill with an explicit border/dash/width overflow variant. For colorset1, use primary red `#9e1b32`, then grays, black, white, and only then the remaining colors. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Native fixed-index families have their documented renderer capacity: extend category styling deliberately, split the view, or retain labels/shape when that native capacity cycles. Do not use borders merely because a fixed native scale ended while usable solid palette colors remain.
5. Use colorset2 for an explicit extended/full-color request or a documented semantic category need. Keep category IDs and styles stable across static/animated views.

## Native compact defaults

The styler inserts these values into YAML `config` before rendering. It keeps text size and lets Mermaid measure labels and route edges.

| Family | Configuration | Default values |
| --- | --- | --- |
| Flowchart / Swimlane | `flowchart` | `padding: 6`, `nodeSpacing: 24`, `rankSpacing: 32`, `subGraphTitleMargin: {top: 4, bottom: 12}` |
| State | `state` | `padding: 6`, `nodeSpacing: 28`, `rankSpacing: 32` |
| Class | `class` | `padding: 6`, `nodeSpacing: 28`, `rankSpacing: 36` |
| ER | `er` | `entityPadding: 6`, `diagramPadding: 6`, `nodeSpacing: 60`, `rankSpacing: 80` |
| Sequence | `sequence` | `height: 36`, `boxMargin: 6`, `noteMargin: 8`, `messageMargin: 28` |
| Mindmap | `mindmap` | `padding: 6` |
| Block | `block` | `padding: 6` |
| Requirement | `requirement` | `rect_padding: 6` |

Flowchart's padding is one shared value for both axes. Reducing it from Mermaid's 15 to 6 reduces empty vertical space without scaling text. `nodeSpacing` controls peer separation; `rankSpacing` separates successive ranks, vertically in TB and horizontally in LR. Keep them large enough for edge labels and arrowheads.

In Mermaid 11.16.0, State v2 uses the shared `flowchart` spacing, so the styler also configures its padding and spacing with the State values and the subgraph title margins above. Some State shapes retain fixed internal padding. ER uses `diagramPadding` inside empty entity boxes and `entityPadding` between attribute rows; changing only `minEntityHeight` has no effect in this renderer. ER keeps 80 pixels between ranks so cardinality markers clear relationship labels. The subgraph title margin prevents compact nodes from covering a group heading.

The nine-role ER and Swimlane cases retain the tighter spacing documented in [palette capacity](palette-capacity.md). Other families retain their native geometry or their existing specialized defaults.

Explicit values in an authored family block win, including zero. The styler fills only missing fields, retaining comments and nested options. It preserves inline maps, aliases, and YAML merge maps as complete overrides; use a normal block map to combine your settings with missing compact defaults. Edit authored configuration outside the generated marker blocks, because restyling refreshes those blocks.

```yaml
config:
  flowchart:
    padding: 10
    rankSpacing: 48
    curve: linear
```

## Rendered review

- Style and run `--check`, then render through `animate_mermaid_svg.py --animation none` as shown in `SKILL.md`.
- Inspect ordinary, multiline, and long labels, diamonds, subgraph titles, and labeled edges at the intended display size. Confirm clearance inside the actual node shapes.
- If a specific label or edge needs room, restore or increase that family's padding or spacing, then look for unused space elsewhere. Preserve its exact wording and readable font size.
- Compare SVG box heights and whole-diagram bounds when reporting compaction; frame whitespace, box padding, and rank separation are different measurements.
- Inspect visible fills and label contrast. A declared palette token alone does not prove the geometry uses it.
- Inspect relation text as well as node text: native edge labels can inherit a node's white text while their separate backing is white. The bundled renderer finishes edge-label paint against its own surface without changing the route or text geometry; source inventory and missing-style counts do not prove the label is visible.

Native option references: [Flowchart](https://mermaid.js.org/config/schema-docs/config-defs-flowchart-diagram-config.html), [State](https://mermaid.js.org/config/schema-docs/config-defs-state-diagram-config.html), [Class](https://mermaid.js.org/config/schema-docs/config-defs-class-diagram-config.html), [ER](https://mermaid.js.org/config/schema-docs/config-defs-er-diagram-config.html), and [Sequence](https://mermaid.js.org/config/schema-docs/config-defs-sequence-diagram-config.html). The installed 11.16.0 schema and rendered geometry are the acceptance authority for these pinned defaults.
