---
name: ambientcg-material-search
description: "Searches free ambientCG materials, HDRIs and other assets from a natural-language brief, shows numbered previews, and downloads the exact selected resolution and format package. Use for ambientCG texture discovery and follow-up downloads of chosen assets."
---

# ambientCG Material Search

Find freely released CC0 resources through ambientCG's public v3 API. Use the
bundled helper with Python 3.11+ and `uv`; no account or API key is required.
Keep generated files outside the skill and converse in the user's language.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, follow the bundled `solidSequence`: primary red `#9e1b32`, then interleaved black/grays (darkest, middle, next darkest, next middle), white, and the remaining colors. Apply this order to categorical identities; keep quantitative and ordered grayscale ramps monotonic. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Presentation colors

Use colorset1 for authored preview chrome: `#f7f7f7` stage, borderless `#ffffff` cards, black text and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.

## Find suitable resources

1. Extract subject, surface, color, finish, wear, scale and intended application.
   Translate the search into a few concise English keywords. ambientCG combines
   keywords with AND, so long sentences often hide good matches. Start broad and
   refine only meaningful constraints.
2. Search and save numbered choices:

   ```sh
   uv run --script <skill-dir>/scripts/ambientcg.py search --query "wood" --type material --limit 6 --out options.json --html options.html
   ```

   Read [source-guide.md](references/source-guide.md) for resource types,
   pagination, search recipes and actual package keys.
3. For local image review, download thumbnails into a fresh workspace directory:

   ```sh
   uv run --script <skill-dir>/scripts/ambientcg.py previews --manifest options.json --output-dir artifacts/previews
   ```

   Read the exact returned paths with the image tool. Keep preview files inside
   the active workspace; shell `/tmp` paths and Windows image tools may resolve
   to different directories. Review thumbnails or the source's material preview before describing a visual
   match. The helper retrieves metadata; it does not recognize appearance or
   prove seamlessness. Label unreviewed candidates honestly. Loosen keywords or
   use a relevant alternate phrase when a constrained query returns no results.
4. Show roughly 3–6 choices with their saved option numbers, asset IDs, preview
   and source links, available maps and relevant differences. Save the manifest
   path in context; preserve option numbering if omitting weaker candidates.

## Download the selected package

Use the same saved list for “download option 2”. For “download it”, download the
single selected asset; ask which option only when several remain plausible.
Do not request permission again after the user has chosen a download. A request
to find and download the best match authorizes choosing a reviewed candidate.

```sh
uv run --script <skill-dir>/scripts/ambientcg.py inspect --manifest options.json --option 2 --out selected.json
```

Select a `variants[].key` that matches the requested format and resolution. If
unspecified, a 2K JPG package is a practical modest default for a material when
available. State that choice. Use only an inspected key, for example:

```sh
uv run --script <skill-dir>/scripts/ambientcg.py download --manifest options.json --option 2 --variant 2K-JPG/zip --output chosen-material.zip
```

For HDRIs or other types, inspect their actual variants instead of assuming a
material ZIP. The helper refreshes the exact asset ID, excludes future releases,
uses the returned URL, checks size and file integrity, and saves a SHA-256/source
receipt at `<output>.json`. It refuses an existing file or a missing variant.

Read the receipt and return clickable local files with the selected package,
source and CC0 information. ZIP receipts include a verified member inventory;
keep the complete map package unless the user asks for specific files.

## Recovery

Use the selected `https://ambientcg.com/a/<id>` page if the API is unavailable.
Inspect its free download choices and preserve the same ID and resolution.
Skip supporter-only early access and optional paid services. Explain unavailable
variants or failed transfers instead of substituting a different material.
