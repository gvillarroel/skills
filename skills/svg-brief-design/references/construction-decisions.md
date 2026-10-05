# Purpose and construction

Use these methods when their geometry and information needs fit the brief.
They provide starting structures; they do not select a finished design for you.

## Preserve the requested topology

Translate spatial words into reserved regions before making paths. An empty
center means a clear central area, not several small white cells separated by
lines. A frame's curves belong around its opening. A long bar keeps its shallow
occupied proportions even on a larger canvas. An open body needs edges whose
alignment and spacing imply continuity across gaps.

For a flowing circular frame, start with the original `orbit` scaffold:

```text
python <skill-root>/scripts/scaffold.py init orbit --recipe design.json --output artwork.svg
```

Edit its count, inner_ratio, coverage, taper, rotation and direction, then build
again. The generator confines tapered bands to an annulus, so they cannot cross
the reserved central disk. Lower coverage separates the bands; higher coverage
overlaps their ends. Choose the relationship the brief needs, inspect the joins
and shape the gaps before adding details. Do not add a second rim merely to hide
awkward junctions. For a noncircular subject, make different geometry rather than
forcing an orbit into it. Other exact geometry belongs in the scaffold guide.

## Compact connected explanations

Size each labeled node from its final text and a 6-unit vertical/10-unit
horizontal inset as the starting point. Pack related
concepts together, shorten connector detours and crop unused outside space.
Reserve every label, full arrowhead, identifiable source/target port and
separate parallel/return route before reducing a gap. Keep a visible shaft
between endpoints; a tip touching another line or hidden behind a node fails.
Do not route through a label or silently share an unrelated edge's segment.

Render at intended size, try one tighter gap or branch arrangement, and compare
the occupied bounds and every relationship. Keep the smaller version only
when labels, endpoints and route tracing remain equally clear; undo the first
readability loss. Stop when local alternatives cannot save more space safely.
Reflow or enlarge a constrained canvas instead of reducing the font. Keep the
negative space that defines artwork and the scales of quantitative graphs.

The flow scaffold uses readable content-sized nodes centered in the allotted
box. Its canvas remains the declared size; for an unconstrained diagram, choose
canvas dimensions around the occupied nodes/routes plus their clearance.

## Let white describe the form

For an open mechanical form, draw its principal rails, plates or facets around
the channels that describe its body. Coordinate their directions and widths;
connected contour flow can imply a body without filling the whole silhouette.
Avoid a solid slab followed by a few tiny holes. Keep essential facial openings
and joints visible after all black parts overlap. Inspect their combined shape.

## Match notation and ink to the use

For a sparse printed illustration, begin with the explanatory trace and joined
axes. Give them related, substantial weights at the final display size; check
that arrowheads meet their shafts without a collar. A practical starting point
is a principal trace about 1–2 percent of the occupied drawing's short dimension,
with axes slightly quieter. Adjust optically after rendering. Add only reference
letters that explain the relationship, and use coherent curvature rather than
jitter to vary an organic gesture. A serif font by itself does not create the
print idiom. Preserve mathematical accuracy and requested measurements whenever
the brief asks for a quantitative graph.

For a compact identifier, choose the shallow footprint and primary identifier
first. Add required codes or navigation cues in a clear order. Do not invent a
full specification table, but do not remove a requested code, heading or data
field in the name of simplicity. If a machine-readable code is requested, encode
its actual payload with an appropriate implementation.

Render and open the drawing at working size and as a thumbnail. Check the brief's
reserved regions and required features before judging decoration. Repair one
visible relationship—such as a pinched opening, merged joint or oversized label—
and render the final state again. Do not claim a visual inspection without one.
