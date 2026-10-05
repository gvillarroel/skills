# Semantic layout and density

## Contents

- [Plan the page](#plan-the-page)
- [Fit without distortion](#fit-without-distortion)
- [Compact connected diagrams by default](#compact-connected-diagrams-by-default)
- [Cross-panel connections](#cross-panel-connections)
- [Review decisions](#review-decisions)

Start with the delivery width, not an arbitrarily huge canvas. For an unspecified
screen figure, use a landscape 1200 x 760 viewBox at 1200 CSS pixels as an initial
budget, then reduce avoidable height or reflow to a smaller readable footprint.
Preserve explicit output dimensions. Use at least 14 displayed pixels for essential labels as a
starting point, then adapt to audience/destination. Physical print sizes need
an explicit viewing assumption; screen pixels are not a universal print rule.

## Plan the page

List each panel's question, family, rough node/label counts, preferred aspect
ratio, importance, and links to other panels. Estimate body dimensions after
headers and padding. Compare layouts before investing in renderer detail:

- Stacked explanations plus a shared synthesis: four columns, two rows; A at
  row 1 / columns 1-2, B at row 2 / columns 1-2, synthesis C at rows 1-2 /
  columns 3-4. This is an example, not a default for every request.
- A long sequence above two comparisons: full-width top span, two lower peers.
- A central relationship with supporting detail: square main region, narrow
  side annotation column; reserve a gutter for links, not another row of boxes.
- A portrait hierarchy: narrow overview at top, deeper tree below, shared legend
  at foot. Do not rotate horizontal labels to save width.

Use weighted tracks when a comparison has longer labels or a hierarchy needs
depth. Align repeated baselines and legend keys, not just panel boundaries.
Reading order belongs in `panels` array order; spatial position should support it.
Allow frameless panels and shared whitespace. Use borders when they carry a
boundary or improve grouping; avoid enclosing every noun in a rounded card.

## Fit without distortion

For source width/height `sw, sh` and body `bw, bh`, the uniform scale is
`min(bw/sw, bh/sh)`. At output width `D` from a viewBox width `W`, a source
font of size `f` appears as `f * scale * D/W`. Budget from that final size.
A 1200px source packed into a 400px region cannot keep its 14px labels readable.
Ask the renderer to draw for the body size first; do not stretch the SVG.

When a fitted panel leaves a long unused strip, inspect whether the source
viewBox contains excess margins, the diagram can change orientation, the grid
tracks can rebalance, or another family makes the facts easier to read. Never
trim marks or labels to improve a packing score. Canvas occupancy alone is not
an objective: negative space can clarify grouping and connector routes.

Treat text as a budget rather than a paragraph destination. Prefer subject
titles, 1-4-word labels, and short relationship verbs when that preserves the
facts. Put the thesis once at page level. Share repeated names in one legend;
retain exact names when recognition is uncertain. Units, conditions, uncertainty,
and negation are often more important than decorative subtitles.

Reserve icon clear space. Test recognition at actual size; a detailed product
logo may require more space than a 24px generic pictogram. Equalize optical size,
not only bounding-box dimensions. Preserve brand artwork and meaningful colors.

## Compact connected diagrams by default

Minimize the occupied footprint and unnecessary connector length subject to
legibility. First size nodes to their measured labels, icons and internal padding;
then group related nodes, place linked panels beside one another and tighten
outer margins, track gaps and unused source viewBox space. Keep group boundaries
and reading order recognizable. Do not stretch short labels into oversized cards
or distribute a small graph across its full allocation by habit.

Route through the nearest clear corridor with few bends. Reserve enough terminal
run for a visible shaft and head, enough space for any relation label, and separate
parallel lanes so a reader can follow one edge from its actual source to target.
Distinct edges must not share a segment that suggests an undeclared junction.
Use an offset/bridge for unavoidable crossings; prefer a local reroute or a node
reordering over a long exterior detour. Derive clearance from final stroke, head
and label bounds rather than one universal gap or occupancy target.

After a readable draft, make up to two focused compaction revisions. Compare
delivery-size previews and the densest crop with the previous passing draft.
Accept a smaller canvas/group footprint or shorter routes only if typography,
arrow visibility, port ownership, lane separation and label clearance still pass.
Revert a failed reduction and retain the tightest passing version; stop when the
next reduction consumes required reading or routing space. With fixed dimensions,
use the recovered room for requested explanatory detail or clear grouping.

For quantitative chart panels, improve information density through useful marks,
dimensions or aligned comparisons. Preserve axes, domains, tick labels, aspect
ratios and comparison space; do not apply diagram node/edge squeezing to them.

## Cross-panel connections

Choose ports on actual concept objects. Use measured object boxes and structured
`{object,side}` ports from the
[boundary contract](connectors-and-surfaces.md); these remain attached under
uniform scaling. Keep
long routes in gutters, label relations near their route, and distinguish shared
identity from dependency with words or line styles. Avoid crossings; when
unavoidable, use a clear bridge/offset or a keyed relation ledger rather than
letting one intersection imply an extra node.

Automatic routing avoids declared node interiors and respects outward terminal
directions. Start there. The browser audit additionally checks labels, actual
surfaces, and wire intersections. Repair a crowded route by changing its bound
side or grid corridor before introducing manual `via` coordinates. Explicit
waypoints must still pass the geometry checks and must be updated after a grid
change. Keep arrowheads clear of symbols and panel titles. Do not remove a label,
hide a requested edge, or move a port away from its object to pass the audit.

## Review decisions

Inspect both the whole figure and its densest region at the intended size. Can
the reader identify the thesis, find each panel's question, trace a named relation,
and distinguish each icon without zoom? If not, fix the responsible source.
If facts and minimum type cannot fit the fixed page, explicitly present the
tradeoff and provide a readable reflow or detail companion when permitted.
Do not claim a zoomed screenshot proves a compact composition is readable.
