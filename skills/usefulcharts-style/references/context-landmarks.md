# Source-bound editorial landmarks

Use this layer when a genealogy or institutional history contains meaningful places, territories, schools, courts or movements that are difficult to find among individual records. It complements the graph. It cannot repair repetitive topology or supply missing historical explanations.

Choose a few source-supported orientation points before adding artwork. Use a place caption for a territory, a white outlined pill for a family, and a portrait only for an identified person or a clearly declared fictional demonstration. Keep the distinction visible. A decorative mark at every equal interval produces another mechanical pattern.

## Bind content to a record

Store the exact supplied value on a node, such as `realm: "Bayeux"` or `court: "Whitehaven"`. Add an annotation with `kind: landmark`, the known `node` ID, and `field: realm` or `field: court`. Its visible label is read from that field. Do not provide an independent replacement label, derive a country from a convenient portrait, or invent an event to justify an emblem. The annotation retains the named node's group.

```json
{
  "kind": "landmark",
  "node": "record-id",
  "field": "realm",
  "width": 146,
  "size": 17,
  "icon": "heraldry",
  "variant": 1,
  "art_size": 32,
  "art_position": "beside",
  "dx": -100,
  "dy": -40
}
```

Use `art_position: above` for a narrow vertical pocket or `beside` for a shallow wider pocket. Omit `icon` for a typographic landmark. An optional short `eyebrow` such as `COURT AT` precedes the exact field value; it must describe the supplied fact accurately. Default label type is 18 units, with a minimum of 10. Start around 17–20 for a dense mural and 20–24 for a compact page. Avoid reducing names or making an unreadable caption to fill a gap.

`heraldry` provides seven original fictional devices selected by `variant: 0` through `6`: sprig, crescents, stars, waves, tower, sun and flower. Keep one device and category paint consistent for an invented family. These are diagram identifiers, not authentic historical coats of arms. Say that the devices are fictional in a demonstration's provenance. For a factual chart, omit this generic heraldry or provide an accurately sourced symbol through a custom SVG workflow.

## Reserve required context in a new family

For a new genealogy, declare the node fields and `landmark` annotations in the data-first `layout: cohorts` brief, before assigning positions. Omit page dimensions, coordinates and generation bounds. Use one context caption per person and do not attach another caption to that same person. Reserve their space in the baseline helper:

```sh
uv run --script <skill-dir>/scripts/space_family_branches.py draft.json --output brief.json --report spacing.json --reserve-context
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Render the reserved result directly. Do not pass it through the later pocket-search helper. The baseline pass reserves each full caption above its named person, includes its horizontal footprint and height when measuring the family, retains fitted nameplate widths, and leaves a connector approach below the caption. The renderer routes incoming paths around the reserved context. This avoids repeated failed attempts to squeeze a required caption into an already completed compact tree. Partners still share their baseline and retain their separate source categories.

Use the normal baseline typography defaults. A context reservation is not a reason to choose a huge page, multiply all node widths or shrink type. If the user prescribes a page, use authored composition and the bounded refinement workflow below instead of silently resizing it.

## Fit an existing authored graph

Resolve the genealogy or lineage first. The helper accepts `layout: authored` or `resolved` with every node's `x,y`; it does not accept inset-bearing pages. Write the draft outside the skill bundle, then run:

```sh
uv run --script <skill-dir>/scripts/place_context_landmarks.py draft.json --output brief.json --report placement.json
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

The helper renders a temporary base beside the requested output and uses Chromium to measure actual text, artwork, existing annotations and the complete sampled relationship and partnership paths. It fits the full label/art envelope with clearance, changes only landmark `dx,dy`, and checks the final graph before writing outputs. Inputs, output and report paths must be distinct. It loads no acceptance fixture. This is the refinement route for existing authored genealogy and institutional graphs, not the starting route for required context in a new family.

The default search radius is 240 units, with at most 90 units of vertical movement unless the label is taller. For a territorial orientation caption spanning several generations, an explicit `vertical_radius` may widen that band within the overall radius; the CLI permits `--radius` from 40 to 360. A nearby same-category record must be at least as close as a different-category record, allowing a 12-unit tolerance for small layout variation. These are association guards, not a substitute for looking at the result.

If no pocket fits, the helper fails without deleting the label or changing any source facts. For an optional repeated orientation label, choose another meaningful record carrying the same supplied field. For required local context, compose more space around its actual node or change from stacked to beside artwork at the same readable type size. Do not silently drop requested context, substitute a new anchor with a different fact, or widen the search across the page until it fits.

## Review at two scales

At whole-page width, check that landmarks identify regions and interrupt monotonous chains. At detail scale, check which branch appears to own each caption; a nearby unrelated colored node can make a geometrically valid placement misleading. Check that heraldic details remain visible at their placed size. Mix formats when the space and meaning warrant it; seven identical detached badges are a limited hierarchy improvement.

The browser audit checks exact visible field text, source binding, actual annotation position, content containment, neighboring nodes and annotations, and both relationship and partnership paths. It cannot determine whether the editorial choice is persuasive. Record that judgment separately.
