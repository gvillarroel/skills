---
name: iconify-icon-search
description: Search free Iconify icon collections, present numbered previews from a consistent family, and download the exact selected SVG with source and license metadata. Use for interface or presentation icons from Iconify and follow-up requests for chosen icons.
---

# Iconify Icon Search

Find coherent icon choices and export exact SVGs through the public Iconify API.
No account or key is required. Use Python 3.11+ with `uv`; all helper resources
are inside this bundle. Keep generated files outside it. Converse in the user's
language.

## Find icons

1. Translate the intended concept into short English icon keywords. Identify
   outline/filled preference, multicolor versus monochrome, target dimensions,
   and any existing family. For a set, search each concept within one family.
2. Save numbered preview candidates:

   ```sh
   uv run --script <skill-dir>/scripts/iconify.py search --query "home" --prefix lucide --limit 6 --out options.json --html options.html
   ```

   Omit `--prefix` to compare families, then constrain later searches to the
   chosen one. Read [source-guide.md](references/source-guide.md) for collection
   metadata, pagination, SVG export and license handling.
3. Review actual previews. Similar names do not ensure similar geometry, stroke
   weight or filled style. Mark unreviewed candidates honestly. Present the
   saved option number, full `prefix:name` ID, preview, source and collection
   license. Preserve the manifest path and original numbering.

## Download exact SVGs

Resolve a numbered request against its saved list. For “download it”, use the
single selected icon; ask only which option if ambiguous. Download an identified
selection without another confirmation. A request for a complete icon set also
authorizes selecting a coherent reviewed family and exporting the requested icons.

```sh
uv run --script <skill-dir>/scripts/iconify.py download --manifest options.json --option 2 --color "#334155" --size 24 --output chosen-icon.svg
uv run --script <skill-dir>/scripts/iconify.py download --id lucide:house --output house.svg
```

Defaults are `currentColor` and 24px height, preserving aspect ratio. The helper
refreshes the chosen name/alias, retrieves its SVG and collection metadata, checks
SVG structure and records source, author, collection license, export settings and
SHA-256 in `<output>.json`. Existing files and receipts are protected.

Read the result and return clickable SVGs with their source/license information.
Keep the receipt alongside the icons. When packaging for redistribution, read
the returned upstream license and retain any required copyright/permission
notice; the metadata receipt alone is not a substitute for the license text.

## Recovery

Use `https://icon-sets.iconify.design/` to browse the exact collection and icon if
the API fails. Preserve the same `prefix:name`; download the source SVG, not a
screenshot. Explain a removed icon or unavailable export instead of silently
switching families. Use free public collections and avoid paid add-on catalogs.
