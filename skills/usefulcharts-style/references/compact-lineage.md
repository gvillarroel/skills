# A compact branching history

Use this route for a small or medium institutional, intellectual, or craft history
without prescribed coordinates. Start with [the data-only brief](../assets/templates/lineage.json).
Replace its subject, records and links; its institutions are only a fictional example.
No implementation or test-file reading is needed to render this contract.

## Input

Set `design: editorial`, `mode: lineage`, and `layout: auto`. Supply:

- `id`, `title`, and a concise `source_note`.
- `groups`: `{id, label, color}`. Colors are six-digit hex values. A category means
  a tradition, house, discipline or other source-defined family. Keep it stable
  through mergers and changes of importance. A merger is a relationship and an
  emphasis decision; it is not automatically a new color category.
- `nodes`: `{id, label, group, detail?}`. Put dates and short explanations in
  `detail`; arbitrary extra data fields are retained but are not printed.
- `edges`: `{id, source, target, kind}`. Use `branch` or `succession` for structural
  links, and `influence` for a distinct dotted connection. Preserve every explicit
  incoming link to a merger. Succession is dash-dot; branch links are solid.
  Explain the used line types in the reading note. Do not infer extra links from dates.
- `reading_note`: explain whether position means a stage, generation or numeric
  time. Automatic lineage is schematic, not a numeric year scale.

Omit page `width`/`height`, node `x`/`y`, grid rows/columns and `font_size` initially.
The renderer measures content, packs ranks and uses larger type for a small brief.
It does not impose an 1800-by-2700 wall canvas on fourteen records. Honor dimensions
explicitly requested by the user, then review the resulting spacing.

Set `emphasis: true` on consequential landmarks; explicit `style` values are
`plain`, `card`, `pill`, `emblem`, and `hero`. Emphasis affects size/treatment,
while `group` continues to control semantic color. Quieter intermediates can use
`style: plain`. Ended branches remain ended; add their closure in `detail`.

Optional `icon` uses an original vector emblem such as `book`, `wheel`, `globe`,
`ship`, `star`, or `observatory`. For sourced observation artwork use
`illustration-astrolabe-observation`; for a sextant use
`illustration-sextant-1904`. The renderer embeds the image and its identity from
[illustration provenance](../assets/illustrations/provenance.json). Do not call
decorative art an institution's actual logo or historical identity. Other sourced
art and authored layouts are documented in [the editorial contract](editorial-contract.md).

## Execute and inspect

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Both commands create output parent directories. Substitute the exact user-requested
paths. Open the resulting PNG and inspect the two busiest junctions and the whole
page. A readable sparse subject should look intentionally compact; do not invent
records to make it dense. If automatic ordering gives a poor merge or long detour,
use `resolved_layout.nodes` from `layout.json` as a starting point for authored
placement. Fix positions and widths in the brief, then render again. Keep colors,
dates, labels and the relationship inventory intact.
