---
name: vectorize-art-patterns
description: Simplify openly licensed or user-owned raster artwork and organic artistic patterns into editable standalone SVGs using deterministic smoothing, palette reduction, seeded composition variation, canonical colorset1/colorset2 adaptation, ink, stain, collage, contour-tracing, and tiling pipelines. Use when Codex needs to vectorize or reinterpret raster art, derive non-geometric abstract or Cubist material patterns, build multi-pattern collections with no reused compositions or paths, generate repeatable SVG pattern tiles, create palette-matched comparison galleries or GitHub Pages examples, preserve licensed base-image assets with provenance, or validate that an SVG is truly vector rather than a raster wrapper.
---

# Vectorize Art Patterns

Create a rights-traceable vector interpretation, not a pixel-perfect autotrace. Preserve the source's defining rhythm while reducing color, texture, and contour complexity.

## Core Workflow

1. Lock the exact input, output, style, dimensions, tile behavior, and acceptable loss of detail.
2. Establish transformation rights before downloading or processing:
   - For a web source, read `references/rights-and-provenance.md` and use `scripts/fetch_open_image.py`.
   - Accept only public domain, CC0, CC BY, CC BY-SA, or an explicitly user-owned image.
   - Reject unknown, `ND`, `NC`, fair-use, editorial-only, or otherwise restricted material.
3. Choose the pipeline:
   - `organic`: biomorphic forms, wood grain, foliage, flowing abstraction.
   - `ink`: charcoal, automatic drawing, calligraphic lines, engraving.
   - `stain`: watercolor, marbling, clouds, soft color fields.
   - `collage`: Synthetic Cubism, pasted-paper masses, torn silhouettes.
   - Read `references/pipeline-selection.md` before tuning an unfamiliar source or adding a technique.
   - For a multi-pattern collection, also read `references/collection-generation.md` before choosing parameters or counting outputs.
4. Choose the paint contract:
   - Omit `--colorset` to retain a simplified source-derived palette.
   - Use `--colorset colorset1` for red-neutral work.
   - Use `--colorset colorset2` for expressive multi-hue work.
   - Read `references/colorset-adaptation.md` before producing paired variants or a published gallery.
5. Keep the verified base image immutable. Store ordinary task sources under the task workspace's `assets/base-images/` with `manifest.json`; store outputs under the exact user-requested path. Treat the installed skill directory as read-only.
6. Validate the image catalog with `scripts/validate_open_assets.py`.
7. Vectorize with the bundled script and write a report.
8. Run the structural validator, then inspect the SVG directly in a browser at full size and thumbnail size. For tiles, inspect every seam and the four-way junction.
9. For a collection, reject every repeated composition, complete geometry, or individual path signature. Do not count recolors as independent drawings.
10. Deliver the SVG, report, and required attribution. State that it is a modified vector interpretation.

## Acquire an Open Image

Run from the task workspace root. Put global options before the provider
subcommand. The examples use PowerShell continuations; in Bash, replace each
trailing backtick with `\` or place the command on one line.

```powershell
uv run --script skills/vectorize-art-patterns/scripts/fetch_open_image.py `
  --asset-id hilma-pleiade-14 `
  --output assets/base-images/hilma-pleiade-14.jpg `
  --manifest assets/base-images/manifest.json `
  --max-width 900 `
  commons --title "File:Hilma af Klint 1908 - Pleiade nr 14.jpg"
```

For the Art Institute of Chicago, replace the final line with:

```powershell
  artic --object-id 27992
```

The downloader must stop rather than save a file when metadata is missing, the work is not marked Open Access, restrictions are present, or the license does not allow derivatives.

Validate the downloaded bytes and rights records:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/validate_open_assets.py `
  assets/base-images/manifest.json `
  --output-report outputs/base-images-validation.json
```

## Vectorize

Use a verified manifest entry:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py `
  assets/base-images/hilma-pleiade-14.jpg `
  outputs/hilma-organic-pattern.svg `
  --mode organic `
  --colorset colorset2 `
  --tile mirror `
  --variation-seed 140021 `
  --crop-scale 0.72 `
  --crop-x 0.28 `
  --crop-y 0.63 `
  --rotation -9 `
  --flow-strength 7.5 `
  --flow-frequency 2.4 `
  --pattern-id hilma-organic-pattern `
  --source-manifest assets/base-images/manifest.json `
  --source-id hilma-pleiade-14 `
  --report outputs/hilma-organic-pattern.json
```

For a user-provided image that the user is authorized to modify:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py `
  inputs/my-art.png outputs/my-art.svg `
  --mode collage `
  --rights-basis user-owned `
  --pattern-id my-art-simplified `
  --report outputs/my-art.json
```

Preserve exact output paths. Do not write task artifacts into `skills/`.

## Validate

```powershell
uv run --script skills/vectorize-art-patterns/scripts/validate_art_svg.py `
  outputs/hilma-organic-pattern.svg `
  --report outputs/hilma-organic-pattern.json `
  --expected-pattern-id hilma-organic-pattern `
  --expected-mode organic `
  --expected-tile mirror `
  --expected-colorset colorset2 `
  --require-pattern `
  --output-report outputs/hilma-organic-pattern-validation.json
```

The validator requires editable paths, provenance metadata, direct `title` and `desc`, finite geometry, internal-only references, and no raster `<image>`, scripts, or `foreignObject`.

For paired colorset variants, run the same source and vector parameters twice
with different `--colorset` values and variant-suffixed pattern IDs. Geometry
must remain byte-identical after isolating `viewBox` and path data.

For independent collections, do the opposite: give every member distinct
composition parameters and validate that no complete geometry or individual
path data repeats. Colorset variants are comparison outputs, not additional
unique drawings. Follow `references/collection-generation.md`.

## Publish the Example Gallery

Use the bundled acceptance fixture when maintaining this repository's GitHub
Pages example. Do not read `assets/examples/` for ordinary runtime tasks.

```powershell
uv run --script skills/vectorize-art-patterns/scripts/build_example_gallery.py
uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py
uv run --script scripts/build-pages.py
```

The published set uses the stable page ID `vectorize-art-patterns`, 300
independent drawings across 15 families, and `-cs1` / `-cs2` pattern-ID
suffixes. It contains 150 members of each colorset; no colorset pair shares
composition, complete geometry, or path data. Rebuild and validate the fixture
before publishing Pages.

For global art that ranges from a recognizable land silhouette to an
intentionally imprecise continental mnemonic, read
`references/abstract-world-map-recipe.md`. The focused Pages fixture uses the
stable ID `vectorize-abstract-world-maps`; validate it with
`scripts/validate_abstract_world_map_examples.py`.

Browser review must confirm:

- the subject or visual rhythm remains recognizable at the requested simplification level;
- no dominant contour is clipped, folded, or replaced by accidental spikes;
- color regions do not expose unexpected holes;
- the SVG remains legible at small size;
- a stratified family sample has meaningful contrast and each Colorset 2
  member retains a visible chromatic anchor;
- mirrored tiles have no obvious seams or broken four-way junctions;
- the result does not collapse into unwanted rigid geometry;
- the SVG and JSON report retain the correct source license and hash.

## Output Contract

- Emit standalone UTF-8 SVG with a stable `viewBox`, lowercase hyphen-case pattern ID, direct accessibility text, and editable paths.
- Keep the vector source deterministic: identical bytes, parameters, rights record, and pattern ID must yield identical SVG bytes.
- Embed the source SHA-256, rights basis, license, source URL, and pipeline parameters in `<metadata>`.
- Embed `data-colorset`, the colorset name, and the bundled palette-contract SHA-256. Use only exact palette tokens when a colorset is selected.
- Keep paired colorset variants geometry-identical; map paint only after tracing.
- For a unique collection, keep every composition, complete geometry, and
  individual path signature distinct. Forbid `<use>` and do not count recolors,
  transforms, tile wrappers, or renamed copies as new members.
- Use compound paths with `fill-rule="evenodd"` for holes.
- Use `<pattern>` only for requested repeat or mirror output.
- Do not embed the original raster, remote CSS, fonts, scripts, or external image links.
- Prefer fewer meaningful color masses over many tiny traced fragments.
- Preserve attribution and ShareAlike obligations in the derivative package.

## Technique Extension

When the shipped filters cannot preserve the source:

1. Research the smallest suitable method in official documentation or a primary paper.
2. Test it against the current source and one adversarial source.
3. Keep all randomness seeded or remove it.
4. Compare path count, output size, recognizable structure, thumbnail readability, and tile seams.
5. Add the method to the reusable skill only when it generalizes; otherwise keep it task-specific.

Do not add a new mode as an untested stylistic alias.

## Bundled Resources

- `scripts/fetch_open_image.py`: verify a supported provider, download one open image, and update its provenance manifest.
- `scripts/validate_open_assets.py`: verify base-image hashes, dimensions, MIME types, source URLs, and derivative-friendly licenses.
- `scripts/vectorize_art.py`: generate deterministic organic, ink, stain, or collage SVG paths and a sidecar report.
- `scripts/validate_art_svg.py`: enforce the editable standalone SVG contract.
- `scripts/build_example_gallery.py`: regenerate the 300-member, 15-family Pages collection and its uniqueness manifest.
- `scripts/validate_example_gallery.py`: enforce page/manifest parity, 300 unique compositions and geometries, globally unique path data, no reusable SVG elements, report parity, and colorset anchors.
- `scripts/validate_abstract_world_map_examples.py`: validate the two focused world-map SVGs, page/manifest parity, palette, geometry contracts, hashes, and provenance.
- `scripts/test_vectorize_art.py`: exercise all modes, both colorsets, seeded variation, determinism, invalid variation bounds, restricted-license rejection, and tampered-asset detection.
- `references/abstract-world-map-recipe.md`: create recognizable or intentionally imprecise global artwork without confusing abstract placement with cartographic accuracy.
- `references/collection-generation.md`: generate deterministic collections and enforce no-reuse semantics.
- `references/colorset-adaptation.md`: select colorsets and preserve geometry across palette variants.
- `references/pipeline-selection.md`: choose and tune filters or research an extension.
- `references/rights-and-provenance.md`: apply the license allowlist and attribution rules.
- `assets/palettes/colorsets.json`: self-contained colorset1/colorset2 token contract.
- `assets/base-images/manifest.json`: canonical metadata and hashes for bundled open source images.
- `assets/examples/vectorize-art-patterns/`: published acceptance fixture; exclude it from ordinary runtime reads.
- `assets/examples/vectorize-abstract-world-maps/`: focused Pages fixture for the biomorphic and straight-line global studies.
