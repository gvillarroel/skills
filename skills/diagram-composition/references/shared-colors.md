# One semantic palette across subdiagrams

Choose colors once, before rendering. The composition owns the palette; individual
renderers receive it. One concept keeps its color across radial nodes, matrix rows,
containers, annotations, and the synthesis. Orientation and position do not change
identity. Do not reuse a categorical accent for an unrelated meaning. Prefer a few
meaningful accents and shared neutral surfaces to a different color per panel.

Preserve user-specified colors. Otherwise use the chosen companion theme as the
starting palette, then pass exact overrides to every renderer. Align background,
ink, muted text, neutral edges, and emphasis treatment as well as concept accents.
Keep essential labels readable on the final background; bright colors belong on
swatches, bands, or outlines. Reinforce identity with a label, icon, shape, or
pattern so color is never the only cue. Explain the mapping once if necessary.

## Executable categorical contract

Add an opaque six-digit `color` to each concept that carries color meaning:

```json
"concepts": [
  {"id":"source","label":"Shared source","color":"#007298"},
  {"id":"review","label":"Human review","color":"#9e1b32"}
]
```

Uncolored concepts remain valid. Distinct colored IDs must use distinct colors;
reuse the same ID when views represent the same meaning. Each panel's `concepts`
lists the identities actually present. Every listed colored concept needs a visible
bound mark inside that panel; a mark in another panel or the legend cannot cover it.

Native hub cards, cycle steps, boundary nodes/groups/outer enclosure, taxonomy
groups, matrix row headers, and matrix value objects accept `"concept":"source"`.
The builder looks up its color, preserves dark labels, and adds the SVG bindings.
For example, the same concept can appear in both of these native objects:

```json
{"id":"shared-source","label":"Shared source","concept":"source","icon":"library"}
{"text":"Read","concept":"source"}
```

A local `color` that conflicts with `concept` is rejected. The final audit also
checks the node's fill: use neutral surfaces or related tints/shades with readable
text. A correct border alone cannot validate a contradictory dominant fill.
Do not use independent
literal colors for repeated semantic categories. Brand SVGs retain their official
artwork; the card outline or adjacent swatch carries the composition's concept
color. Never infer a semantic category from a logo's original color.

For custom or specialist SVGs, set the actual paint and tag **each visible accent
mark**, not a parent group or metadata-only declaration. Mark the owning semantic
surface with `data-node-id` and `data-concept-id`; a separate band or swatch uses
`data-color-owner` with that node ID, as explained in
[connectors-and-surfaces.md](connectors-and-surfaces.md):

```svg
<rect x="12" y="12" width="120" height="56" fill="#ffffff"
      stroke="#007298" stroke-width="2.4"
      data-node-id="source" data-concept-id="source"
      data-color-concept="source" data-color-channel="stroke"/>
```

Use `fill` or `stroke` as the channel on a native path, rect, circle, ellipse,
polygon, polyline, line, or text element. Keep that mark opaque and unfiltered.
For definitions/`use`, gradients, or complex art, add a simple visible bound accent
beside the artwork. Source CSS must resolve to the same solid color; `prepare`
preserves binding attributes while materializing computed paint. ID namespacing
does not alter the canonical concept ID.

## Audit and review

The composer carries the registry into `semanticColors` in its report and SVG
metadata. The browser audit compares actual computed paint against that registry,
checks binding IDs/channels, rejects hidden or opacity-altered marks, and requires
coverage in every declared panel. It reports occurrences and panel coverage under
`semanticColors`. Swapped renderer colors, CSS overrides, missing annotations,
and a correct legend beside an incorrectly colored panel must fail. Covered
accents, contradictory node fills, and low-contrast ordinary labels also fail.

This verifies declared categorical accents, not arbitrary semantic inference.
Manually check untagged marks, duplicated occurrences, clipping/occlusion, contrast,
brand recognition, and the neutral theme. A report with `status: not-declared`
means no palette was supplied; it does not certify alignment. Do not remove the
registry or bindings to make a failing audit pass.

For quantitative panels, also share units, domains, breakpoints, and color scales
whenever values are comparable. Do not normalize each panel independently and
then give equal colors different numeric meanings. If different scales are
necessary, label them explicitly and separate them from categorical accents.
Use neutral connectors unless their color has a defined meaning; never borrow a
node's color in a way that falsely assigns identity to the relationship.
