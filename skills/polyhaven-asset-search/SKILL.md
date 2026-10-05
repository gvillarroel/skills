---
name: polyhaven-asset-search
description: "Finds free Poly Haven textures, HDRIs and 3D models from a visual brief, presents numbered previews, and downloads the exact selected resolution, format and dependent files. Use for Poly Haven resource discovery and follow-up downloads of selected assets."
---

# Poly Haven Asset Search

Use the public Poly Haven API to find CC0 assets and deliver the user's chosen
files. No account or API key is needed. The bundled Python 3.11+ helper runs with
`uv` and includes its own local support module. Keep generated files outside the
skill directory. Respond in the user's language.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, follow the bundled `solidSequence`: primary red `#9e1b32`, then interleaved black/grays (darkest, middle, next darkest, next middle), white, and the remaining colors. Apply this order to categorical identities; keep quantitative and ordered grayscale ramps monotonic. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Presentation colors

Use colorset1 for authored preview chrome: `#f7f7f7` stage, borderless `#ffffff` cards, black text and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.

## Search and shortlist

1. Identify the resource type: `textures`, `hdris`, `models`, or `all`. Extract
   subject, surface, wear, setting, lighting and required resolution from context.
   Start with the available information. The native semantic search accepts
   natural language, including non-English queries; keep phrases under 101 characters.
2. Search and save a stable list and preview gallery:

   ```sh
   uv run --script <skill-dir>/scripts/polyhaven.py search --query "weathered wooden planks" --type textures --limit 6 --out options.json --html options.html
   ```

3. Review previews with available image or browser tools. To inspect local
   thumbnails, use this helper and read its returned image paths:

   ```sh
   uv run --script <skill-dir>/scripts/polyhaven.py previews --manifest options.json --output-dir artifacts/previews
   ```

   Use a fresh preview directory, or reuse its existing images. Keep thumbnails
   in the active workspace, such as `artifacts/previews/`.
   Shell `/tmp` paths and Windows image tools can resolve to different places;
   do not use OS temporary directories for images you need to inspect.
   Search scores rank
   candidates; they do not certify material, location, seamlessness or exact visual
   fit. If visual review is unavailable, say the matches are unverified. Refine
   the query when an essential constraint is missing. Read
   [source-guide.md](references/source-guide.md) for taxonomy, variant keys and
   the distinction between an image, a PBR material and a model package.
4. Present roughly 3–6 options with their **saved option numbers**, titles, source
   links, preview links and relevant differences. Retain the manifest path.
   Credit Poly Haven in the response and gallery; its API requires source credit.
   If curating the manifest, preserve its IDs and option numbers, and read/write
   JSON explicitly as UTF-8. Regenerate the gallery with the bundled renderer
   so its encoding and preview URLs remain correct:

   ```sh
   uv run --script <skill-dir>/scripts/polyhaven.py gallery --manifest options.json --html options.html
   ```

   Keep detailed visual observations in the accompanying comparison. The gallery
   displays candidate previews without certifying their visual suitability.

## Download exactly the selection

Resolve “download option 2” against its saved manifest. Resolve “download it”
against a single selected resource. Ask only which option if the reference is
ambiguous. Once identified, download without another permission question. A
request to find and download the best match also authorizes choosing a reviewed
match. A search-only request calls for a shortlist.

Inspect the chosen identity to discover actual variants:

```sh
uv run --script <skill-dir>/scripts/polyhaven.py inspect --manifest options.json --option 2 --out selected.json
```

Honor the requested format and resolution. If unspecified, use a suitable modest
resolution, normally 2K, and state the choice. Choose only keys that inspection
actually returned. For example, when these keys exist:

```sh
uv run --script <skill-dir>/scripts/polyhaven.py download --manifest options.json --option 2 --variant Diffuse/2k/jpg --output chosen-color.jpg
uv run --script <skill-dir>/scripts/polyhaven.py download --manifest options.json --option 2 --variant Diffuse/2k/jpg --variant nor_gl/2k/exr --variant Rough/2k/exr --output-dir chosen-material
```

Use `--output-dir` for model files with dependencies; the helper preserves their
relative paths. A single map is an image, not a complete PBR material. Match the
normal-map convention to the target application. The helper refreshes the same
asset, excludes unreleased assets, downloads only selected variants, checks
provider sizes and MD5 when supplied, computes SHA-256, and protects existing
outputs. It does not replace a missing variant with another resolution.

Read the receipt before reporting success. Return clickable local files or the
bundle's `receipt.json`, selected resolution/formats, source and CC0 information.
Mention any visual criterion that remains unverified.

## Recovery

Use the actual `https://polyhaven.com/a/<id>` page if the API contract changes.
Inspect its free public download choices and retain the same asset and variant.
Skip early-access entries and paid tools. Stop a failed download with a clear
reason rather than claiming success or silently substituting another asset.
