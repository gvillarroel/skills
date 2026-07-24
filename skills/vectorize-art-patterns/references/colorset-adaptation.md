# Colorset Adaptation

Apply a colorset after tracing so paint changes cannot alter contours, path
order, tiling, or source provenance. The machine-readable authority is
`assets/palettes/colorsets.json`.

## Selection

| Choice | Use for | Required visual behavior |
| --- | --- | --- |
| source palette | Source-relative simplification | Preserve dominant source hue relationships |
| `colorset1` | Restrained, editorial, institutional, monochrome-like art | Use red as the primary chromatic cue with dark ink and neutral support |
| `colorset2` | Expressive abstract art or distinct color roles | Use a small multi-hue hierarchy; avoid assigning every available hue |

Use `--colorset colorset1` or `--colorset colorset2`. Omit the option for the
source-derived palette.

## Invariants

- Permit only exact six-digit lowercase hex tokens from the selected colorset.
- Apply the active contract to background, paths, and outlines.
- Do not interpolate, blend, or invent colors between tokens.
- Preserve `viewBox`, path count, path data, fill rules, pattern transforms,
  and source SHA-256 between paired variants.
- Record the colorset and palette-contract SHA-256 in the SVG metadata and JSON
  report.
- Use `-cs1` and `-cs2` as final pattern-ID variants.

The vectorizer maps the background to a suitable light or dark surface, assigns
ink explicitly, and maps color layers deterministically by perceptual
proximity. Colorset1 reserves its primary red for the strongest chromatic
source layer.

## Validate Paired Outputs

Run `validate_art_svg.py` with `--expected-colorset`. It rejects arbitrary
color syntax, disallowed tokens, and a stale palette-contract hash.

For a pair, compare a digest made from the root `viewBox` and ordered path `d`
values. The digest must match even though the complete SVG hashes differ.

## Published Gallery Contract

The acceptance fixture at
`assets/examples/vectorize-art-patterns/` contains four base motifs and two
variants per motif:

- organic field;
- stain mirror;
- ink mirror;
- Cubist collage.

Run `scripts/build_example_gallery.py`, then
`scripts/validate_example_gallery.py`. The validator requires eight unique
pattern IDs, four shared geometry digests, exact page/manifest parity, four
variants per colorset, palette-safe page colors, valid provenance, and no stale
SVG or report files.
