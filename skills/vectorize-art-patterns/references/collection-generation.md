# Unique Collection Generation

Use this workflow when the request is for several independent patterns rather
than one SVG or a paint-only comparison pair.

## Count Drawings, Not Recolors

A collection member is unique only when all of these are unique across the
collection:

- the raster composition after crop, rotation, and displacement;
- the complete ordered SVG geometry;
- every individual path `d` value.

Do not count a colorset change, background change, tile wrapper, transform, or
reordered copy as a new drawing. Forbid SVG `<use>` and keep `--tile none` when
the brief says that no elements may be reused.

## Deterministic Variation

Create independent compositions before tracing. Vary these inputs together:

- `--variation-seed`: stable integer identity for the composition;
- `--crop-scale`, `--crop-x`, `--crop-y`: source framing;
- `--rotation`: affine rotation in degrees;
- `--flow-strength`, `--flow-frequency`: smooth sinusoidal displacement;
- tracing controls such as `--colors`, `--smoothing`, `--detail`,
  `--min-area`, and `--outline`.

The implementation uses OpenCV affine transforms and `remap` with reflected
borders. These are the relevant primary references:

- [OpenCV geometric image transformations](https://docs.opencv.org/master/da/d54/group__imgproc__transform.html)
- [OpenCV remap tutorial](https://docs.opencv.org/trunk/d1/da0/tutorial_remap.html)
- Simard, Steinkraus, and Platt,
  [Best Practices for Convolutional Neural Networks Applied to Visual Document Analysis](https://doi.org/10.1109/ICDAR.2003.1227801),
  for the established use of smooth elastic distortions.

Keep every variation seeded. Do not use ambient random state.

Example:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py `
  assets/base-images/source.jpg outputs/current-017.svg `
  --mode organic `
  --colorset colorset1 `
  --tile none `
  --variation-seed 170021 `
  --crop-scale 0.68 `
  --crop-x 0.31 `
  --crop-y 0.74 `
  --rotation -12.5 `
  --flow-strength 9.2 `
  --flow-frequency 2.7 `
  --pattern-id collection-current-017-cs1 `
  --source-manifest assets/base-images/manifest.json `
  --source-id verified-source `
  --report outputs/current-017.json
```

## Parameter Coverage

Use a deterministic low-discrepancy sequence or another documented sampler so
the collection covers the parameter space without clusters. Give each family a
semantic purpose and bounded parameter ranges. A useful collection record
includes:

- stable family and pattern IDs;
- source ID, license record, and source hash;
- all variation and tracing parameters;
- output hash, composition hash, complete-geometry hash, and path signatures;
- colorset, palette, path count, contour count, and point count.

Distribute Colorset 1 and Colorset 2 across independent drawings. Do not create
one geometry and count its two colorset variants as two unique members.
Colorset 1 must visibly retain `#9e1b32`; Colorset 2 must visibly retain
`#007298`.

## Uniqueness Gate

Before accepting a member:

1. Reject a repeated variation seed or raster composition hash.
2. Reject a repeated complete-geometry hash.
3. Hash every normalized path `d` value and reject any path signature already
   owned by another member.
4. Reject `<pattern>`, `<use>`, raster `<image>`, scripts, external references,
   and stale output files.
5. Require the colorset anchor and inspect thumbnail contrast.

Fail the entire build on the first collision. Never repair a collision by
renaming the file or changing paint alone.

For a published collection, repeat the build and compare a digest over the
entire SVG/report inventory. Byte-identical inventories are the determinism
proof.

## Visual Review

Inspect a stratified sample from every family, both colorsets, every mode, and
the lowest-complexity outputs. Render the full collection in a browser and
measure:

- successful image loading and zero console errors;
- no horizontal overflow at desktop and mobile widths;
- thumbnail legibility and meaningful contrast;
- filters, pagination, search, and direct links;
- absence of accidental rigid geometry when the brief is organic.

Cryptographic uniqueness is necessary, but it does not replace visual review.
