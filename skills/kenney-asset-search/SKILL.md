---
name: kenney-asset-search
description: "Finds free Kenney game asset packs by theme, category and style, shows numbered previews, downloads the exact selected ZIP, and extracts chosen files with license notices. Use for Kenney sprites, tiles, 3D props, UI, textures and audio packs."
---

# Kenney Asset Search

Search the free public Kenney asset catalog and download a chosen CC0 pack.
Use the bundled helper with Python 3.11+ and `uv`. It has no account, API-key or
paid subscription dependency. Keep outputs outside the skill and use the user's
language in conversation.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, use primary red `#9e1b32`, then grays, black, white, and only then the remaining colors. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Presentation colors

Use colorset1 for authored preview chrome: `#f7f7f7` stage, borderless `#ffffff` cards, black text and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.

## Find candidate packs

1. Extract theme, intended game/resource type, perspective, pixel versus vector
   style and needed formats. Translate the topic to concise English search words.
   A catalog result represents a **pack**, not one sprite or sound.
2. Search and save a stable numbered list:

   ```sh
   uv run --script <skill-dir>/scripts/kenney.py search --query "platformer" --category 2D --limit 6 --out options.json --html options.html
   ```

   Read [source-guide.md](references/source-guide.md) for categories, search
   behavior, individual member selection and free-download navigation.
3. Review the pack previews for perspective, geometry, colors and content. Cache
   thumbnails inside the active workspace and read the returned image paths:

   ```sh
   uv run --script <skill-dir>/scripts/kenney.py previews --manifest options.json --output-dir artifacts/previews
   ```

   Use a fresh directory, or reuse images already downloaded there. Keep images
   in the current workspace: shell `/tmp` paths and Windows image tools can
   resolve to different places. A
   preview sheet can show many resources; do not claim a particular member exists
   until the downloaded inventory proves it. Label unreviewed candidates.
4. Present saved option numbers, pack names, source/preview links and relevant
   differences. Preserve the manifest path and numbering. Prefer compatible
   series when the user requests several related resources.

## Download and optionally extract

Resolve a numbered selection against the saved manifest. For “download it”, use
the single selected pack; ask only which one if ambiguous. Once identified,
download without another permission question. A request to find and download
the best pack authorizes selecting a reviewed match.

```sh
uv run --script <skill-dir>/scripts/kenney.py download --manifest options.json --option 2 --output chosen-pack.zip
```

The helper refreshes the exact pack page, requires its free CC0 ZIP link, checks
the transfer and archive CRCs, and writes `<output>.json` with source, SHA-256 and
member inventory. It protects existing files. It does not follow the paid
All-in-1 promotion.

If the user wants a particular sprite, model or sound, list actual members and
extract only the selected paths into a new directory:

```sh
uv run --script <skill-dir>/scripts/kenney.py archive --zip chosen-pack.zip --out files.json
uv run --script <skill-dir>/scripts/kenney.py extract --zip chosen-pack.zip --member "<exact-path-from-inventory>" --output-dir chosen-files
```

Repeat `--member` for several files; relevant license files are retained
automatically. Inspect candidate images or play audio when exact content matters.
For models, include referenced textures and other dependencies found in the pack.
Return clickable local downloads and the source/license receipt.

## Browser recovery

Open the selected `https://kenney.nl/assets/<slug>` page. Choose **Download**,
then **Continue without donating**. Donations are optional; a paid bundle is a
different product. Retain the selected pack identity and verify the saved ZIP.
If the expected free link is gone, explain the change instead of buying,
registering, or selecting another pack automatically.
