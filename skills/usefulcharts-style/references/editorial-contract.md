# Editorial renderer contract

Set `design: editorial` and run `render_chart.py` normally. Shared fields and relationship semantics remain as described in [data-contract.md](data-contract.md). Dense authored page defaults: 1800 × 2700 and 13-unit body size. Small automatic lineages and genealogical cohorts measure a compact page with 18-unit names. Use the classic profile only for simple schematic compatibility. Optional `imprint` is an array of up to three short author/edition lines in the header; leave it at its default unless the brief needs specific author details. State synthetic data only when that is true.

## Graph placement and treatments

For ordinary lineage input use `mode: lineage`, `layout: auto`, groups, nodes, and typed edges; [compact lineage](compact-lineage.md) is the short entry route. Automatic placement assigns ranks and category-ordered branch columns, measures row heights and reserves connector gaps. Briefs with at most 30 nodes default to 18-unit body type and may use a page shorter than 1200 units; omit page sizes initially. Consequential landmarks and structural mergers receive stronger treatment while retaining their source category. Explicit page sizes, sizes and treatments are honored and may need repair. The automatic layout preserves topology; it is not a replacement for authored composition in a complex poster.

For authored graphs, each node supplies `x` and `y` as the **center** in SVG units. Avoid `layout: auto` in this case. Supported node fields:

For medium histories, `layout: packed` interprets x/y as relative neighborhood hints and measures the final centers/page from the records. Read [packed stories](packed-stories.md). Do not combine relative hints with absolute route coordinates or fixed page insets. The report exposes the measured centers for a later authored repair.

For a genealogy with explicit generations, `layout: cohorts` accepts integer node rows and normal unions instead of coordinates. Read [cohort composition](cohort-composition.md) for spacing controls, limits, and conversion to authored positions.

| Field | Meaning |
| --- | --- |
| `width` | Total card/label width, usually 60–140 for a dense page; selected landmarks may be wider. Height is measured from wrapped content. |
| `size`, `detail_size` | Main and subordinate type sizes. Names default to page `font_size`; details to 77% of it. |
| `style` | `plain`, `card`, `pill`, `emblem`, or `hero`; choose by semantic importance. |
| `detail_position`, `date_label` | Use `detail_position: outside` to put the exact optional `date_label` above the name panel and `detail` below it. The complete content envelope sets the measured height and connector ports. With the default `inside`, details remain in the panel and a separate `date_label` is rejected so it cannot silently disappear. |
| `icon`, `icon_width`, `variant` | Optional art type, reserved panel width, and deterministic variation. Text width excludes this panel. |

Original art types: `shield`, `crown`, `star`, `compass`, `globe`, `astrolabe`, `book`, `wheel`, `gear`, `lens`, `prism`, `ship`, `tower`, `observatory`, `press`, `obelisk`, `leaf`, and `portrait`. The vector `portrait` is fictional. Museum portraits use `museum-<artwork-id>` and complete objects use `object-<artwork-id>`; available IDs and accurate source/rights records are in `assets/portraits/provenance.json` and `assets/objects/provenance.json`. They are decorative samples for synthetic demonstrations, not identities or evidence for factual charts. The map's provenance is in `assets/maps/provenance.json`. Source identities are embedded alongside museum images; full objects preserve their aspect ratio.

Source illustrations use `illustration-astrolabe-observation` (a mariner observing an angle) or `illustration-sextant-1904` (an encyclopedia drawing). Their original bytes, authors, dates, rights and hashes are in [the illustration provenance](../assets/illustrations/provenance.json). They preserve aspect ratio and are embedded once per source in a reusable SVG symbol. Use them for their actual subjects; the publication date is not an invention date or proof of a fictional event. Do not read the large SVG source merely to use its ID.

Also available: `illustration-telescope-observer` (a large refractor and observer) and `illustration-cuneiform-tablet` (an identified Library of Congress tablet). Both have transparent fields. Their subjects and actual dates remain distinct from any synthetic chart event. Inspect the visible silhouette at its placed size; do not confuse an opaque white PNG with a transparent illustration. A consistent text landmark is preferable to an unrelated decorative object or a conspicuous photo rectangle.

For deliberate white image panels, use `illustration-cogwheel-psf` (two meshing wheels), `illustration-compass-card-psf` (a compass card), `illustration-theodolite-psf` (a surveyor and instrument), or `illustration-printing-press-bookman` (a 1923 typographic ornament depicting a press). These are unchanged sources; the PNGs retain their white field. Start with roughly 40–55 units for wheels/compass and 55–70 for the narrower full figures, then inspect the preview. Do not insert an opaque field directly onto a textured timeline without considering its visible rectangle. The illustration manifest carries exact source identities, rights, dimensions and hashes.

Keep partnered people at exactly the same `y`, with at least 16 units of space between their measured boxes. Parentage must go to a later `y`. A node may retain legacy `row`/`col` placement instead of explicit centers. The source brief is preserved in the report hash.

Routes use rounded orthogonal corridors and preserve source/target semantics. `corridor_y` requests a horizontal bend level; the router repairs it if it would enter a box. For a deliberately composed route, `via` is an array of absolute `[x,y]` bends between the source bottom/union midpoint and target top. Every segment must be orthogonal. Routes that enter any entity, including their own source or target, are rejected. Reserve visible space below a source and above a target before arranging bends.

For `mode: lineage` and `kind: influence` between two nodes, optional `source_port` and `target_port` choose `left`, `right`, `top` or `bottom` on the complete content envelope. Defaults remain source `bottom` and target `top`. `via` bends begin and end at the chosen sides, and the arrow points into the actual target side. Other graph relationship kinds retain the default vertical attachments. The browser audit verifies the declared side against both the visible endpoint and independent source JSON. These string side names are separate from the numeric timeline fractions below. Read [influence routes](influence-routes.md) when selecting or recomposing them.

## Annotations and insets

`annotations` contain `{x,y,width,label,size?,kind?,group?,icon?}`. `kind: pill` creates a family label and finds a nearby position clear of entity labels; `kind: heading` uses a serif place heading and optional crest above it. These are decoration/context positions, not numeric time assertions. Inspect their association with the correct branch after placement.

Instead of `x,y`, use `node` with optional `dx,dy` to anchor an annotation to a measured node center after layout. Unknown node anchors fail.

For an exact source-derived place or movement caption, use `kind: landmark`, `node`, and `field`. It reads the visible label from that node field, retains the node category, and reserves the complete serif label and optional emblem envelope. See [context landmarks](context-landmarks.md) for `eyebrow`, `art_position`, the seven fictional `heraldry` devices, local placement, limits and source-backed browser verification.

`insets` contain `kind`, `title`, and `box: [x,y,width,height]`:

- `isotype` derives and displays actual node counts per category. One symbol equals one record; it does not invent a population statistic. Supply `groups: ["category-id", ...]` to include small categories or choose an explicit order. Otherwise only categories with more than twelve records appear. Selected IDs must be unique and known.
- `map` uses the supplied `countries` mapping from Natural Earth country IDs to category IDs, plus a short `note`. Unassigned countries are neutral; unknown category IDs fail. Set `legend: true` for a nearby key derived from the mapped categories. Allow enough height for its rows. Reserve a region of the page that does not contain nodes or connector corridors.

## Chronological ribbon composition

For a few parallel phase sequences, use `layout: compact` and [compact chronology](compact-chronology.md): horizontal names, visible endpoint dates and measured page dimensions. The following authored fields apply to the dense ribbon route; do not impose them on a compact first preview.

Use `mode: timeline`, shared numeric `time`, named `lanes`, and `periods`. Each period provides normal dates/category/lane plus:

- `offset`: horizontal units from its lane's left edge.
- `bar_width`: actual ribbon width; allow enough room for wrapped rotated type.
- `size`: optional name size. Names are rotated inside the actual interval rectangle; dates are never stretched to fit.
- `treatment`: `ribbon` by default, or `stem` for a thin full-duration line with a local rotated name capsule. `bar_width` then measures the capsule's envelope; `stem_width` defaults to 5 and must be at least 2 and no wider than that envelope. Optional `label_position` is 0–1 across the capsule's available vertical travel, default 0.5. These two fields require stem treatment. Compact horizontal-label timelines retain their existing ribbon treatment.

Each lane can provide a positive `weight`, default 1. The available width is distributed proportionally in source order. Changing weights never moves dates, but lane-relative offsets remain absolute units and need recomposition. Read [narrative chronology](narrative-chronology.md) for treatment selection and note placement against actual painted shapes.

`events` contain `{id?,lane,year,label,detail?,offset,width,size?,detail_size?,icon?,art_size?,art_width?,art_height?,art_position?,group?}`. Their first heading line stays on the numeric year; normal-weight detail follows it. Event IDs, dates and text roles remain inspectable in the SVG. `art_position` is `below` by default, or `above`, `left`, `right`; it requires an icon. Above/below images are centered with a five-unit gap. Side images leave an eight-unit gap and reduce the prose width. `width` encloses text and art together. `art_size` defaults to a square; use `art_width` and `art_height` for the intended footprint. Reserve the complete wrapped text and image viewport, including space before the date for an above image. The renderer rejects artwork covering periods; the browser checks image identity, dimensions, placement, visibility and collisions. See [narrative chronology](narrative-chronology.md) for measured placement and illustration choices.

`eras` contain `{start,end,label}` for shared horizontal dividers and rotated margin labels. `map_texture: true` or `natural-earth` uses a restrained geographic field. `map_texture: milner-1850` embeds a public-domain historical map with its provenance. A decorative map is not a map of the chart's data; say so in the reading note. The historical image's source and rights record is `assets/maps/milner-1850.json`.

`transitions` explicitly connect known periods: `{id,source,target,kind,style?,source_port?,target_port?,ribbon_width?}`. Use `succession`, `division`, `union`, or `uncertain` according to the source. An uncertain relation should use `style: dotted`; ordinary transitions may use `ribbon`. Dates never change and transitions cannot go backward.

Ports are fractions of ribbon width, default 0.5, and must remain at least five units inside each edge. For a split or merger on a full band, separate the attachment ports and supply a narrow `ribbon_width` (for example 10). Stem endpoints require 0.5 so the connection meets visible ink. A bridge tapers to the stem width at that end. Omit width or use zero for a continuation across the full visible endpoint widths. The semantic center path follows the filled bridge, avoiding a second elbow that could look like another fork. Reserve its entire polygon, not just the centerline. Width is compositional unless the data explicitly defines a quantitative encoding.

## Validation

Run the browser audit with `--source brief.json`. It measures transformed text, samples actual rounded paths, checks node/edge inventories and endpoints, and recomputes numeric time positions. All annotations and insets also require visual review. A self-contained SVG can still be aesthetically weak; apply the separate comparison loop in [editorial-composition.md](editorial-composition.md).
