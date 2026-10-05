---
name: pexels-media-search
description: "Finds free Pexels photos and videos from a natural-language brief, presents numbered previews with creator credit, and downloads the exact chosen original photo or video rendition. Use for Pexels stock media search and follow-up downloads; the API requires a free Pexels key."
---

# Pexels Media Search

Find free Pexels media for the user's project and download their chosen file.
Run the self-contained helper with Python 3.11+ and `uv`. Keep generated files
outside the skill directory and use the user's language in conversation.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, follow the bundled `solidSequence`: primary red `#9e1b32`, then interleaved black/grays (darkest, middle, next darkest, next middle), white, and the remaining colors. Apply this order to categorical identities; keep quantitative and ordered grayscale ramps monotonic. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Presentation colors

Use colorset1 for authored preview chrome: `#f7f7f7` stage, borderless `#ffffff` cards, black text and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.

## Access and search

1. If API access is not already established, check it without revealing secrets:

   ```sh
   uv run --script <skill-dir>/scripts/pexels.py status --out access.json
   ```

   The helper reads `PEXELS_API_KEY` from the environment. A key is free but must
   belong to the user. Never print it, put it in arguments/manifests, or ask the
   user to paste it into the conversation. If absent, use the browser workflow
   below when available; otherwise explain the setup requirement and provide the
   free [API signup page](https://www.pexels.com/api/). Do not invent API results.
2. Extract subject, action, setting, orientation, color, space for text, and
   whether the request is for a photo or video. Use a concise English query by
   default, or a supported locale. Read [source-guide.md](references/source-guide.md)
   for filters, variants and source requirements.

   ```sh
   uv run --script <skill-dir>/scripts/pexels.py search --type photo --query "foggy forest" --orientation landscape --limit 6 --out options.json --html options.html
   ```

3. Review previews before judging composition or exact content. The search helper
   cannot verify empty space for a title, absence of people, mood, or video action.
   Label candidates unverified if no visual review is possible. Refine the query
   or page when important criteria are missing.
4. Present roughly 3–6 choices with the saved option numbers, typed IDs, source
   and preview links, author, dimensions, and duration for videos when provided.
   Include a prominent Pexels link and creator credit. Keep the manifest path.

## Download the chosen media

Resolve the user selection against the same manifest. Typed IDs distinguish
`photo:123` from `video:123`. For an ambiguous “download it”, ask only which
option. An identified download request needs no further confirmation. A request
to find and download the best match authorizes choosing a reviewed candidate.

```sh
uv run --script <skill-dir>/scripts/pexels.py inspect --manifest options.json --option 2 --out selected.json
uv run --script <skill-dir>/scripts/pexels.py download --manifest options.json --option 2 --output chosen-photo.jpeg
```

Photos default to the `original` URL. Use its inspected extension, which can be
JPEG or PNG, and preserve it. For video, choose an actual `video_file` variant ID
from inspection that matches requested dimensions and use `--variant ID` with
an `.mp4` output. If dimensions are unspecified, choose a suitable available
rendition, normally 1080p, and state it. Never call a preview or crop an original.

The helper refreshes the exact asset and variant, downloads without sending the
API credential to the media host, validates the transfer, and writes a source,
creator, license and SHA-256 receipt at `<output>.json`. Read that result before
claiming completion and return a clickable file link. Preserve existing files.

## Browser workflow without an API key

Open `https://www.pexels.com/` with an available browser tool. Choose Photos or
Videos, search, and inspect individual source pages. Record each actual page URL,
numeric ID, preview and creator in a numbered list saved outside the skill.
Download the selected page's **Free download** choice at the requested size.
Verify the local file, dimensions/format and source identity; record provenance.
Do not scrape hidden credentials, bypass challenges or substitute sponsored
paid results. If browser downloads are unavailable, return the direct source
page and the missing capability instead of claiming a file was saved.
