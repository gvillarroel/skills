# Vector logo selection and maintenance

Read this reference for color, monochrome, adaptive, and custom-color logo tasks. Use the helpers rather than reading the full catalog. All paths below are relative to this skill; replace `<skill-root>` with its actual location.

## Selection contract

`assets/logos/logo_manifest.json` schema 3 identifies 1,960 stable catalog elements. `logo_variants.json` records the available choices per ID, their hashes, source references, licenses, and transformation methods. A filename suffix and matching `data-logo-variant` distinguish every selectable variant. Unsuffixed original paths are preserved for compatibility.

| Variant | Filename | Meaning and use |
| --- | --- | --- |
| `original` | `<name>.svg` | Original source bytes, unchanged inside a normalized SVG wrapper. |
| `color` | `<name>.color.svg` | Provider-authored palette, an exact upstream color source, or a documented provider brand hex applied to its single-paint mark. Default choice. |
| `grayscale` | `<name>.grayscale.svg` | Vector grayscale filter preserving geometry and tonal differences. This is not a one-ink silhouette. |
| `mono-black` | `<name>.mono-black.svg` | Pure black geometry with transparent negative space. Use on light backgrounds. |
| `mono-white` | `<name>.mono-white.svg` | Pure white geometry with transparent negative space. Use on dark backgrounds. |
| `adaptive` | `<name>.adaptive.svg` | Single-paint inline geometry using `currentColor`. The consumer chooses CSS `color`. |

All selectable variants have `width="256" height="256" viewBox="0 0 256 256"`, 16-unit padding, and centered `meet` scaling. Resize through CSS, SVG width/height, or image scale without changing the aspect ratio. Internal `sources/*.source.svg` snapshots are provenance resources, not normalized selection targets.

`paletteKind="monochrome-original"` means the brand is intentionally monochrome; do not invent a multicolor identity. Derived variants are labeled as transformations, not claimed to be owner-approved. The catalog's coverage is finite: it covers its 1,960 records, not every product that exists.

## Search, choose, and export

```powershell
uv run --script <skill-root>/scripts/list_logo_assets.py --search python --variant adaptive --json
uv run --script <skill-root>/scripts/list_logo_assets.py --id devicon-python --variant mono-white --json
uv run --script <skill-root>/scripts/export_logo_asset.py --id devicon-python --variant mono-white --output deliverable/python-white.svg
```

Read `available`, `path`, `availableVariants`, `unavailableVariants`, `licenseId`, and `artworkStatus`. `--available-only` filters a search; without it, an unavailable request is returned with `path: null` and an explicit reason. An unavailable export fails without writing files. Resolve an exact product and ID before export; do not choose a generic provider mark for a named product or silently switch variants.

Each export writes the requested SVG plus matching `<stem>.provenance.json` and `<stem>.license.txt`. Retain both sidecars. Output must be outside the skill directory. Existing identical outputs are idempotent; different outputs require an explicit `--overwrite`.

## Adaptive color really depends on embedding

Inline the adaptive SVG element in HTML or a parent SVG and set `color: #007298` on that element or its parent. Its fill/stroke inherit `currentColor`; geometry IDs are namespaced per logo/variant. Namespace IDs again if embedding repeated copies of the same SVG in a single document with referenced definitions.

An external `<img src="icon.adaptive.svg">`, `<image href="...">`, CSS background image, or PlantUML image is a separate document and does not inherit the surrounding CSS color. For these consumers, bake a fixed color:

```powershell
uv run --script <skill-root>/scripts/export_logo_asset.py --id devicon-python --variant adaptive --color "#007298" --output deliverable/python-blue.svg
```

This export is labeled `data-logo-variant="custom-color"`, `data-color-mode="fixed-custom-color"`, and `data-color-value="#007298"`; its sidecar retains `requestedVariant: adaptive`. It never modifies the bundled adaptive file. Only literal `#RGB` and `#RRGGBB` values are accepted. There is no forced recolor option for unavailable variants.

## Availability and source constraints

- `license-no-derivatives`: retain source artwork unchanged. The AWS and GCP collection is handled conservatively under its recorded CC-BY-ND-2.0 terms. Exact unmodified white source assets may be offered, but color transforms, grayscale filters, tracing, cropping, and hand-redrawing are not generated as a workaround.
- `no-safe-single-paint-source`: available artwork uses multiple paints, cutouts, masks, gradients, images, text, or complex CSS and no verified upstream single-paint alternative was found. Use `color` or licensed `grayscale`; do not collapse a detailed logo into a solid silhouette.
- `artworkStatus` distinguishes official releases, archived sources, legacy artwork, and curated project marks. GCP records use Google's official legacy console package; five AWS symbols use archived January 2026 release artwork. These identifiers are source-matched, not represented as the latest branding.

Prefer provider-authored Devicon `plain`/`line` or Lobe Icons monochrome geometry over converting a multicolor original. Preserve negative space. The current fixed-color and adaptive variants are derived only from verified single-paint geometry under a recorded permissive copyright license. Trademark rights and current brand-use policies remain separate.

## Maintenance and verification

Do not run maintenance during a normal selected-logo export. Generated outputs are reproducible from the bundled original sources and alternate snapshots; no external clone, sibling skill, gallery, or project artifact is needed for an offline rebuild:

```powershell
uv run --script <skill-root>/scripts/build_logo_variants.py
uv run --script <skill-root>/scripts/sync_normalized_logos.py --check
uv run --script <skill-root>/scripts/test_logo_assets.py
uv run --script <skill-root>/scripts/test_logo_variants.py
```

The validator inspects the actual decoded XML recursively, forbids raster/external/active resources, verifies embedded outline fonts, checks original and alternate source hashes, regenerates all variant bytes from source recipes, and checks exact inventory, metadata, and normalization. Browser QA must additionally verify decoding, nonblank paint, light/dark backgrounds, adaptive color inheritance, and representative scaling.

For maintenance-only visual QA, run `scripts/build_logo_audit.py --output <artifact-directory>/logo-audit.html`. Open the generated self-contained page, inspect its representative contact sheet on light/dark backgrounds, change the adaptive color control, and run the full SVG audit. The audit checks every selectable SVG's decoding and nonblank pixels, grayscale/black/white paint, and every adaptive logo under two CSS colors. Save its JSON report and screenshots outside the skill. Do not read the large generated HTML into an agent's runtime context.

`logo_variant_sources.json` pins alternate SVG bytes, attribution, license, and deterministic recipes. `build_logo_variants.py --sources <prepared-directory>` refreshes alternate sources from exact provider commits declared in the identity manifest. Its prepared directories are `devicon/`, `lobe-icons/`, and `simpleicons/`; preserve their pinned repository structure. Never change a source commit without rechecking identity, license, and rendered appearance.

`vector_source_lock.json` preserves reviewed replacements for the former raster/cloud sources and the OpenCode symlink. `build_logo_manifest.py` applies the lock after source enumeration, rejects stale upstream identities, and refuses any unreviewed raster source. For original source refreshes, `sync_normalized_logos.py` fetches hash-pinned raw URLs or release ZIP members; archived ZIP sources have both archive and member SHA-256. A changed archive fails closed. Preserve the last known-good originals before a migration. The one-time `upgrade_logo_vectors.py` requires exact provider maps, a full dry inspection, and a fresh backup before `--apply`.

For complete distribution, `sync_normalized_logos.py --export <new-empty-directory>` validates and copies originals, variants, alternate snapshots, manifests, the generated license log, and complete license texts without network access. It never deletes existing destination content.

## Primary references

- [AWS architecture icon packages](https://aws.amazon.com/architecture/icons/) and [AWS Icons for PlantUML](https://github.com/awslabs/aws-icons-for-plantuml).
- [Google Cloud icons and legacy console package](https://cloud.google.com/icons).
- [Devicon SVG version meanings](https://github.com/devicons/devicon/wiki/SVG-Versions).
- [Lobe Icons source collection](https://github.com/lobehub/lobe-icons).
- [SVG color and currentColor](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/color).
- [Creative Commons Attribution-NoDerivs 2.0](https://creativecommons.org/licenses/by-nd/2.0/).
