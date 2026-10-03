# Compact Mermaid Composition

Use this reference when authoring boxes, reducing vertical whitespace, or choosing colors for many elements. These defaults target Mermaid 11.16.0.

## Color priority

1. Keep the canvas white and distinguish ordinary category boxes with opaque solid fills and zero decorative border width. Containers remain quiet layout surfaces.
2. Use brand red `#9e1b32` first. `csPrimary` and default unclassified boxes use a solid red fill and white inside text. For every other fill choose exactly black or white by the greater WCAG relative-luminance contrast.
3. Reuse roles when meaning repeats. The nine semantic classes use the first nine unique entries of the selected bundled `solidSequence`; every class has no decorative stroke. Preserve connector and class-compartment lines.
4. For indexed categories consume the entire usable `solidSequence`, excluding the actual canvas, before recycling a fill with an explicit border/dash/width overflow variant. Saturated/base colors precede dark/bright/neutral choices; soft colors are late. Native fixed-index families have their documented renderer capacity: extend category styling deliberately, split the view, or retain labels/shape when that native capacity cycles. Do not use borders merely because a fixed native scale ended while usable solid palette colors remain.
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
- If a specific label or edge needs room, increase that family's padding or spacing. Preserve its exact wording and readable font size.
- Compare SVG box heights and whole-diagram bounds when reporting compaction; frame whitespace, box padding, and rank separation are different measurements.
- Inspect visible fills and label contrast. A declared palette token alone does not prove the geometry uses it.

Native option references: [Flowchart](https://mermaid.js.org/config/schema-docs/config-defs-flowchart-diagram-config.html), [State](https://mermaid.js.org/config/schema-docs/config-defs-state-diagram-config.html), [Class](https://mermaid.js.org/config/schema-docs/config-defs-class-diagram-config.html), [ER](https://mermaid.js.org/config/schema-docs/config-defs-er-diagram-config.html), and [Sequence](https://mermaid.js.org/config/schema-docs/config-defs-sequence-diagram-config.html). The installed 11.16.0 schema and rendered geometry are the acceptance authority for these pinned defaults.
