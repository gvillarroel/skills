# Editorial renderer contract

Set `design: editorial` and run `render_chart.py` normally. Shared fields and relationship semantics remain as described in [data-contract.md](data-contract.md). Default page: 1800 × 2700; default body size: 13. Use the classic profile only for simple schematic compatibility. Optional `imprint` is an array of up to three short author/edition lines in the header. State synthetic data only when that is true.

## Graph placement and treatments

For ordinary lineage input use `mode: lineage`, `layout: auto`, groups, nodes, and typed edges. Automatic placement assigns ranks and category-ordered branch columns, sizes the canvas from the content, and chooses simple root/card/plain treatments. Explicit page sizes are honored and may need repair. The automatic layout preserves topology; it is not a replacement for authored composition in a complex poster.

For authored graphs, each node supplies `x` and `y` as the **center** in SVG units. Avoid `layout: auto` in this case. Supported node fields:

For a genealogy with explicit generations, `layout: cohorts` accepts integer node rows and normal unions instead of coordinates. Read [cohort composition](cohort-composition.md) for spacing controls, limits, and conversion to authored positions.

| Field | Meaning |
| --- | --- |
| `width` | Total card/label width, usually 60–140 for a dense page; selected landmarks may be wider. Height is measured from wrapped content. |
| `size`, `detail_size` | Main and subordinate type sizes. Names default to page `font_size`; details to 77% of it. |
| `style` | `plain`, `card`, `pill`, `emblem`, or `hero`; choose by semantic importance. |
| `icon`, `icon_width`, `variant` | Optional art type, reserved panel width, and deterministic variation. Text width excludes this panel. |

Original art types: `shield`, `crown`, `star`, `compass`, `globe`, `astrolabe`, `book`, `wheel`, `gear`, `lens`, `prism`, `ship`, `tower`, `observatory`, `press`, `obelisk`, `leaf`, and `portrait`. The vector `portrait` is fictional. Museum portraits use `museum-<artwork-id>` and complete objects use `object-<artwork-id>`; available IDs and accurate source/rights records are in `assets/portraits/provenance.json` and `assets/objects/provenance.json`. They are decorative samples for synthetic demonstrations, not identities or evidence for factual charts. The map's provenance is in `assets/maps/provenance.json`. Source identities are embedded alongside museum images; full objects preserve their aspect ratio.

Keep partnered people at exactly the same `y`, with at least 16 units of space between their measured boxes. Parentage must go to a later `y`. A node may retain legacy `row`/`col` placement instead of explicit centers. The source brief is preserved in the report hash.

Routes use rounded orthogonal corridors and preserve source/target semantics. `corridor_y` requests a horizontal bend level; the router repairs it if it would enter a box. For a deliberately composed route, `via` is an array of absolute `[x,y]` bends between the source bottom/union midpoint and target top. Every segment must be orthogonal. Routes that enter any entity, including their own source or target, are rejected. Reserve visible space below a source and above a target before arranging bends.

## Annotations and insets

`annotations` contain `{x,y,width,label,size?,kind?,group?,icon?}`. `kind: pill` creates a family label and finds a nearby position clear of entity labels; `kind: heading` uses a serif place heading and optional crest above it. These are decoration/context positions, not numeric time assertions. Inspect their association with the correct branch after placement.

Instead of `x,y`, use `node` with optional `dx,dy` to anchor an annotation to a measured node center after layout. Unknown node anchors fail.

`insets` contain `kind`, `title`, and `box: [x,y,width,height]`:

- `isotype` derives and displays actual node counts per category. One symbol equals one record; it does not invent a population statistic.
- `map` uses the supplied `countries` mapping from Natural Earth country IDs to category IDs, plus a short `note`. Unassigned countries are neutral. Reserve a region of the page that does not contain nodes or connector corridors.

## Chronological ribbon composition

Use `mode: timeline`, shared numeric `time`, named `lanes`, and `periods`. Each period provides normal dates/category/lane plus:

- `offset`: horizontal units from its lane's left edge.
- `bar_width`: actual ribbon width; allow enough room for wrapped rotated type.
- `size`: optional name size. Names are rotated inside the actual interval rectangle; dates are never stretched to fit.

`events` contain `{id?,lane,year,label,detail?,offset,width,size?,detail_size?,icon?,art_size?,group?}`. Their y position comes from the same year scale. A bold headline precedes normal-weight detail and any illustration. Event ID, year, and origin position remain independently inspectable in the SVG. Supply only relevant, distinct events and reserve enough height before the next event.

`eras` contain `{start,end,label}` for shared horizontal dividers and rotated margin labels. `map_texture: true` or `natural-earth` uses a restrained geographic field. `map_texture: milner-1850` embeds a public-domain historical map with its provenance. A decorative map is not a map of the chart's data; say so in the reading note. The historical image's source and rights record is `assets/maps/milner-1850.json`.

`transitions` explicitly connect known periods: `{id,source,target,kind,style?,source_port?,target_port?,ribbon_width?}`. Use `succession`, `division`, `union`, or `uncertain` according to the source. An uncertain relation should use `style: dotted`; ordinary transitions may use `ribbon`. Dates never change and transitions cannot go backward.

Ports are fractions of ribbon width, default 0.5, and must remain at least five units inside each edge. For a split or merger, separate the attachment ports and supply a narrow `ribbon_width` (for example 10). Omit width or use zero for a full-width continuation. The semantic center path follows the filled bridge, avoiding a second elbow that could look like another fork. Reserve its entire polygon, not just the centerline. Width is compositional unless the data explicitly defines a quantitative encoding.

## Validation

Run the browser audit with `--source brief.json`. It measures transformed text, samples actual rounded paths, checks node/edge inventories and endpoints, and recomputes numeric time positions. All annotations and insets also require visual review. A self-contained SVG can still be aesthetically weak; apply the separate comparison loop in [editorial-composition.md](editorial-composition.md).
