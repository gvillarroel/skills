# Compact Mermaid Composition

Use this reference when authoring boxes, reducing vertical whitespace, or choosing colors for many elements. These defaults target Mermaid 11.16.0.

## Color priority

1. Use white and neutral gray surfaces for ordinary boxes, containers, notes, and secondary elements. Keep the background white.
2. Use brand red `#9e1b32` for the main emphasis. `csPrimary` uses solid red and white text; default unclassified boxes use white with a red border. Use dark ink `#333e48` or white according to the fill.
3. Reuse roles when the meaning repeats. Use labels, grouping, or shape before introducing another color. `csAccent`, `csMuted`, `csWarning`, `csInfo`, `csSpecial`, and `csNeutral` stay neutral in colorset1; `csCritical` uses a red outline and `csSuccess` uses dark ink with white text.
4. For genuinely indexed series, consume red, dark red, ink, and the gray range first. All 12 generated colorset1 scale slots fit this range. Pink `#ffccd5` is only a last-resort additional category when usable red and neutral choices are exhausted and an additional hue is necessary. It is absent from standard generated styling. Do not turn selected states, secondary roles, or a larger node count into automatic pink fills.
5. Keep colorset2's extended palette only for an explicit extended/full-color request.

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
