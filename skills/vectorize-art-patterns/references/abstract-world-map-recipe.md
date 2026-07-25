# Abstract World Map Recipe

Use this recipe when a world map should feel like an artistic memory of continents rather than a precise political or physical map.

## Stable Examples

- Example set ID: `vectorize-abstract-world-maps`
- Final abstract pattern: `vectorize-abstract-continental-drift-cs1`
- Cartographic comparison: `vectorize-biomorphic-world-map-cs1`
- Style reference: `vectorize-biomorphic-drift-03-cs1`

## Trigger

Choose this method when the user wants one or both of these results:

- a recognizable land silhouette filled with organic or collage-like artwork;
- an intentionally imprecise global composition whose continents are suggested by position, relative scale, color, line direction, and negative space.

Do not use the abstract method when geographic boundaries, projection accuracy, data overlays, or location-level truth must be preserved.

## Input and Rights Contract

Use public-domain Natural Earth land geometry as the default global reference. Record its exact source URL, license URL, and SHA-256 before transformation. For an abstract mnemonic, state explicitly that the data informs loose placement and relative scale only; do not imply that the result remains a map projection.

## Implementation

### Recognizable Silhouette

1. Project the public-domain land polygons with a global projection such as Equal Earth.
2. Combine the projected rings into an even-odd clipping path.
3. Place broad asymmetric art paths inside the land clip.
4. Redraw a lightweight coastline only when pale interior masses would otherwise disappear.
5. Keep the art paths editable and independent from the source-derived land path.

### Abstract Continental Mnemonic

1. Remove all source contour paths from the output.
2. Place seven loose groups for North America, South America, Europe, Africa, Asia, Oceania, and Antarctica.
3. Build every group from unequal straight-edged masses. Avoid one regular polygon per continent.
4. Use one dominant diagonal and one reciprocal diagonal to create a reading path through the groups.
5. Use only a few axes with clear compositional roles. Remove lines that function only as visible scaffolding.
6. Preserve oceanic negative space. Add detached fragments only when they bridge the reading path or counterweight a dominant mass.
7. Review at full size, gallery-card size, and 320×180. At the smallest size, the result should still suggest a world arrangement without recovering precise coastlines.

## Colorset 1 Hierarchy

- Use `#6d1222` for broad chromatic fields.
- Reserve `#9e1b32` for smaller primary anchors.
- Use `#1c1c1c` and `#333e48` as structural counterweights and axes.
- Use `#828282`, `#cfcfcf`, and `#e7e7e7` as supporting planes.
- Use `#ffccd5` as a limited pause or hinge.
- Keep `#f7f7f7` or `#ffffff` as negative space.

## Validation

```powershell
uv run --script skills/vectorize-art-patterns/scripts/validate_abstract_world_map_examples.py
```

The validator checks manifest/page parity, exact SVG hashes, Colorset 1 paint, accessibility text, editable paths, internal-only references, stable pattern IDs, independent geometry, the abstract straight-line contract, and the precise map's source-derived clipping contract.

## Pitfalls

- A long Antarctica strip becomes a footer and flattens the composition.
- Equal line weights make the axes look like decorative guides.
- A symmetric tapered Africa mass reads as an arrow.
- Large white masses can disappear against the page unless a neighboring plane or edge restores the silhouette.
- Tiny Pacific fragments often become noise rather than geographic cues.
- Reusing the source coastline inside an "abstract" variant defeats the purpose even when it is hidden.
