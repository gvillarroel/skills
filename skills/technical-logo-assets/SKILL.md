---
name: technical-logo-assets
description: "Searches, selects, validates, and exports a verified vector-only catalog of technical brand logos with labeled color, grayscale, black, white, and adaptive variants. Use for exact cloud, company, language, framework, database, AI, and developer-tool logos in diagrams, documents, presentations, websites, videos, or other SVG-capable deliverables; do not use for generating new artwork or general-purpose pictograms."
---

# Technical Logo Assets

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, follow the bundled `solidSequence`: primary red `#9e1b32`, then interleaved black/grays (darkest, middle, next darkest, next middle), white, and the remaining colors. Apply this order to categorical identities; keep quantitative and ordered grayscale ramps monotonic. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Core Contract

Use the bundled catalog for exact, redistributable technical brand artwork. It contains 1,960 stable identities across AWS, Google Cloud, Devicon, individually licensed Simple Icons, Font Awesome Brands, Ollama, code assistants, AI providers, agent frameworks, and adjacent developer tools. Every selectable asset is a self-contained vector SVG with a `256×256` viewport, 16-unit padding, and centered `meet` scaling; embedded raster images are forbidden.

Resolve an exact stable ID before export. Never silently substitute a provider logo for a named product, another product with a similar name, or a different variant. If the requested identity or safe variant is absent, report that explicitly.

Treat the skill bundle as read-only. Export selected files into the user's deliverable so other skills and renderers consume portable assets instead of reaching into this bundle. Do not print, read, or traverse thousands of SVG files during normal use.

## Workflow

1. Search the compact manifest with `scripts/list_logo_assets.py`. Narrow by exact ID, provider, category, or text rather than listing the asset tree.
2. Choose an available variant for the target background and embedding method. Read [logo-variants.md](references/logo-variants.md) for adaptive/custom color behavior or licensing constraints.
3. Export with `scripts/export_logo_asset.py` to a path outside the skill. Keep the generated `.provenance.json` and `.license.txt` sidecars with the SVG.
4. Read [integrations.md](references/integrations.md) only when the target format needs embedding, rasterization, or handoff guidance.
5. Validate the exact exported paths and the final rendered result. Preserve aspect ratio, clear space, and legibility; do not crop, trace, redraw, or distort artwork.

## Search and Export

Set `<skill-root>` to this skill's actual directory:

```powershell
uv run --script <skill-root>/scripts/list_logo_assets.py --search lambda --provider AWS --json
uv run --script <skill-root>/scripts/list_logo_assets.py --search claude --variant color --available-only --json
uv run --script <skill-root>/scripts/list_logo_assets.py --id devicon-python --variant adaptive --json
```

Read `available`, `path`, `availableVariants`, `unavailableVariants`, `licenseId`, `artworkStatus`, and `reason`. Search results are bounded by default; use `--limit` deliberately when more candidates are needed.

Export one exact choice:

```powershell
uv run --script <skill-root>/scripts/export_logo_asset.py --id aws-compute-lambda --variant color --output deliverable/logos/lambda.svg
uv run --script <skill-root>/scripts/export_logo_asset.py --id devicon-python --variant adaptive --color "#007298" --output deliverable/logos/python-blue.svg
```

Existing identical exports are idempotent. Existing different files are not overwritten unless `--overwrite` is explicit. A custom color is accepted only for an available adaptive variant; it never recolors the bundled source in place.

## Variant Choice

For authored diagrams following colorset1/colorset2, prefer an available licensed adaptive, black or white variant. Bake `#333e48` or `#9e1b32` for colorset1, or a semantic colorset2 token such as `#007298` when extended categories are requested. Resolve `currentColor` in the consuming SVG/HTML before checking computed paint. Exact color or source tonal variants remain identified brand artwork: preserve their colors and provenance, and declare that source-fidelity scope separately from authored diagram paint. Do not silently recolor a variant marked non-recolorable.

- Use `color` by default. A genuinely monochrome brand remains monochrome.
- Use `grayscale` for tonal black-and-white artwork, not as a one-ink silhouette.
- Use `mono-black` on light backgrounds and `mono-white` on dark backgrounds.
- Use `adaptive` only when the SVG is inlined and can inherit CSS `currentColor`.
- For external `<img>`, `<image>`, CSS background images, diagram renderers, document imports, or video tools, bake a fixed color from an available adaptive variant with `--color`.
- Use `original` when exact pinned source appearance is required or when transformation is not licensed.

AWS and GCP sources retain their no-derivatives restriction. Do not recolor, crop, trace, or redraw them. Provider-authored white artwork is selectable only when preserved unchanged; unavailable variants stay unavailable. Source dates and `artworkStatus` distinguish current, archived, and legacy artwork. Copyright permission does not grant trademark rights or imply endorsement.

## Portable Bundle

Export the complete offline catalog only when the deliverable genuinely needs it:

```powershell
uv run --script <skill-root>/scripts/sync_normalized_logos.py --export deliverable/technical-logos
```

Use a new or empty destination. The helper validates and copies originals, variants, internal source snapshots, manifests, licenses, and the generated license log without network access. Trust its bounded report instead of implementing a second whole-catalog traversal.

## Maintenance

Normal selection and export do not require maintenance commands. Before changing sources, variants, identities, or generated assets, read the maintenance section of [logo-variants.md](references/logo-variants.md). For code-assistant coverage, also read [code-assistant-logo-sources.md](references/code-assistant-logo-sources.md).

Do not hand-edit normalized wrappers, variant files, manifests, source locks, or license logs. Run the bundled deterministic checks after maintenance:

```powershell
uv run --script <skill-root>/scripts/sync_normalized_logos.py --check
uv run --script <skill-root>/scripts/build_logo_variants.py --check
uv run --script <skill-root>/scripts/test_logo_assets.py
uv run --script <skill-root>/scripts/test_logo_variants.py
```
