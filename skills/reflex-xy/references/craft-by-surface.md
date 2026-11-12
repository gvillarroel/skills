# Craft for an XY chart and its surrounding UI

Use this profile for an embedded chart, notebook widget or requested interactive
HTML. A requested plot/export can stand on its own. Add an agent decision flow
only when the task actually asks a person to choose; keep its evidence and
typed result local to that question.

## Separate chart and wrapper authority

| Layer | Apply through | Preserve |
| --- | --- | --- |
| XY marks, axes, labels, legends and theme | The installed public XY API or connected adapter's supported schema. | Source values, units, domains, missing-value gaps, series/category identity and the exact selected colorset. |
| Owned HTML wrapper | Scoped relative type/spacing roles, native controls, explicit disclosure and keyboard focus. | Host chrome and the downloaded native chart/source unless the requested output itself changes. |
| Notebook / Reflex | The actual widget/framework state and supported events. | The difference between a live Python connection and an interactive fixed-data snapshot. |
| PNG/SVG export | Renderer-supported geometry, labels and paint. | Static output has no live browser controls or backend callbacks. |

## Implement the useful part of the craft pass

1. State the question answered by the chart. Show only marks, annotations and
   controls needed for that question or requested output; put additional formats
   and display tools behind a named disclosure when useful.
2. Use supported XY components/theme for chart text and layout. Do not translate
   CSS, arbitrary HTML props or native terminal tokens into Python kwargs or
   the connected JSON adapter. Verify unfamiliar signatures against the pinned
   runtime. The connected adapter uses versioned `kind` fields.
3. Preserve quantitative geometry and use the same categorical mapping in marks,
   legend and filtered views. The primary red is a valid semantic data color in
   colorset1. A rule about reserving a button accent must not recolor a category,
   reverse a ramp or turn normal observations into warning states.
4. Distinguish current selection with supported outline/shape/label or separate
   wrapper state. Keep thresholds and comparison identities explicit; do not
   change source measurements, scales or missing-value gaps for visual polish.
5. Start ordinary wrapper reading at browser-base size. Measure chart labels in
   the actual canvas/export at intended display size; use exact values or an
   equivalent chart/table when the view cannot remain readable. Moving a legend
   into verified empty space must not hide a high endpoint.

## Verify

Execute the declared Python or connected spec checker, render through the actual
engine and inspect native exports and interactive HTML separately. Exercise the
requested pan/hover/selection and narrow wrapper focus/disclosure where present.
Preserve the last valid chart after a failed regeneration. Live server actions
require an actual live connection; returning HTML or changing wrapper state does
not prove a backend update or agent continuation. A clean visual-rule scan cannot
certify data semantics or an embedded host's paint.

This is an independent adaptation of Impeccable's role/hierarchy/polish ideas to
XY's own API, palette and export contracts; no upstream package is required.
