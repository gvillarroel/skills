# Connectors, object surfaces, and visual quality

## Contents

- [Boundary contract](#boundary-contract)
- [Source-internal wires and layering](#source-internal-wires-and-layering)
- [Color application and legibility](#color-application-and-legibility)

Give a connection a semantic owner before drawing it. A port belongs to a node,
row, container, or other actual object; a convenient point in a panel is not a
substitute. Use undirected identity links for the same thing in multiple views.
Use arrows only when a stated relationship has direction. An unlabeled arrow
between explanations can look like a process; name the relationship or use a
shared key when a wire adds no useful information. Keep requested connections.

## Boundary contract

Native panel builders export `objects` and structured `ports` in the generated
plan. For custom or specialist SVGs, mark the actual enclosing rect/circle/ellipse
with `data-node-id` and `data-node-kind="node"` or `"container"`. A node's interior
blocks unrelated wires. A container may admit a wire targeting a child, so do
not hide that entire connection behind the outer container's opaque background.
Do not change a node to a container just to suppress an intrusion finding.

```svg
<rect data-node-id="source" data-node-kind="node"
      data-concept-id="source" data-color-concept="source"
      data-color-channel="stroke"
      x="40" y="60" width="180" height="72" rx="6"
      fill="#f7f7f7" stroke="#007298" stroke-width="2.4"/>
```

Measure marked geometry in its source SVG rather than estimating page coordinates:

```text
uv run --script <skill-root>/scripts/audit_diagram.py measure --input panel.svg --report panel-geometry.json --overwrite
```

The report supplies `objects`, `ports`, and `routingObstacles`; copy these fields
into the matching panel in the authored composition plan. The obstacle boxes
protect source labels and internal wires; they do not invent semantic objects.
The complete `render_diagram.py` pipeline measures them automatically.
Prepare renderer CSS before final import.
Measurement works for axis-aligned rects, circles, and ellipses through ordinary
nested SVG scaling. Use a simple enclosing boundary for rotated/complex artwork.
Keep its artwork intact. Measure again after changing geometry.

```json
"objects": {"source":{"box":[0.1,0.25,0.45,0.3],"kind":"node","shape":"rect"}},
"ports": {"source-right":{"object":"source","side":"right"}}
```

Object boxes are normalized `[x,y,width,height]` in the source viewBox. Port
sides are `left`, `right`, `top`, and `bottom`; the composer derives the midpoint
and its outward direction. Choose the side facing the available corridor. Raw
`[u,v]` ports remain readable for old plans, but an unbound connection is not a
verified final result. Rebuild a native plan or measure and bind imported objects.

The composer verifies paths against node interiors, starts/ends from the outside,
and favors short orthogonal routes with few bends and separated parallel lanes.
Nested containers remain traversable. If a port cannot exit, choose a different
side or allocate more space. Do not route through a box, suppress the error,
move the port away from its object, or remove a requested relationship.

## Source-internal wires and layering

Tag source-internal paths or lines with `data-connector="native"` so the browser
can inspect them too. Export the actual node surfaces, including icon enclosures,
with `data-node-id`; native panels do this automatically.
Bind a wire with `data-from-node="source-id" data-to-node="target-id"`, using
IDs local to that source panel. Native builders add these automatically. The
audit checks both **visible** endpoints against the actual rounded/elliptical
surface, not just its rectangular bounds. It can infer a unique touching object
on older annotated wires, but rejects floating or ambiguous endpoints.

For an intentionally open connection from outside the depicted system, replace
that end's owner with `data-open-start="Upstream input"` or
`data-open-end="External output"`, naming the real external relationship. The
report lists these terminals for review. Do not use an open-terminal annotation
to excuse a missing node connection or silently omit a requested relationship.

Stop a wire at its object's outer boundary. For direct radial edges, intersect
the center ray with the boundary; do not guess coordinates near an icon. The
bundled `radial_anchor` helper handles rectangles and ellipses. Route around
unrelated objects and labels. Keep arrowheads outside the target interior, with
their tip at the boundary and a size independent of line thickness.

Opaque node surfaces can hide a background wire, provided the visible connection
still meets the right boundary. An outline with `fill="none"` cannot hide the
line inside it. Prefer actual boundary trimming to long masked center-to-center
paths. Never solve this by painting all edges under every container: that can
erase the part of the connection that identifies a nested target.

## Color application and legibility

Apply the palette to the whole semantic object coherently. A correctly colored
border does not excuse an unrelated saturated fill. Use neutral surfaces or a
tint/shade of the same concept, with a clearly visible exact-color accent. Keep
text readable against its actual surface, not just against the white page.
The solid-surface check uses 4.5:1 for normal text and 3:1 for large text, following
[W3C's contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
This is a focused diagram check, not a full accessibility certification.

Attach `data-concept-id` to the semantic node surface. The accent is either on
that surface or carries `data-color-owner="<node-id>"`. Mark imported official
logo artwork `data-brand-artwork="true"`; preserve it and apply semantic color
to the enclosing surface. Label the legend with names/icons and swatches; keep
hex values in the editable plan rather than visible reader-facing prose.

The browser checks node-bound port contact, visible intrusion, annotated wire
crossings/overlaps, text interference, object bounds, conflicting fills, covered
accents, and text contrast over ordinary solid surfaces. Compare the screenshot
too: check terminal tips at useful zoom, nearby parallel routes, cropped symbols,
thin accents, and unannotated imported marks. Complex effects and semantic
correctness still require inspection; annotations cannot prove their own truth.

Avoid stretching sparse content merely to occupy a tall span. Use compact groups
with items immediately under their headings; reserve remaining space for a useful
synthesis, relation, or deliberately quiet separation. Preserve every required
fact, fixed output size, and minimum displayed text size.
