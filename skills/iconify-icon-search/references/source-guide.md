# Iconify source guide

## Collection discovery and coherent sets

```sh
uv run --script <skill-dir>/scripts/iconify.py collections --out collections.json
uv run --script <skill-dir>/scripts/iconify.py search --query "settings" --prefix lucide --out settings.json --html settings.html
uv run --script <skill-dir>/scripts/iconify.py search --query "cart" --prefix lucide --out cart.json --html cart.html
uv run --script <skill-dir>/scripts/iconify.py inspect --id lucide:house --out selected.json
```

Lucide is one possible line-icon family, not a required aesthetic. The live
collections response provides names, categories, tags, palette behavior, author
and license metadata. Use it to find a family suited to the user's interface.
Keep one manifest per concept when building a set, then retain the exact IDs
in the final selection. Never interpret option 2 from one list as option 2 of another.

Search accepts `--limit 1-20` and `--start` for the next result window. The API
has its own minimum page size; the helper saves only the requested shortlist and
reports a `next_start`. A match is a name/tag candidate until visually inspected.

## Export details

The complete identity is `prefix:name`, including aliases. The helper checks
`/{prefix}.json?icons={name}`, reads collection info, and downloads the generated
`/{prefix}/{name}.svg`. Keep this name even when the underlying geometry is an
alias of another icon. The same numeric position in a later search is unrelated.

`--size` is height (1–4096); width follows the original aspect ratio.
`--color` supports a CSS named color, `currentColor`, or hex. Color affects
geometry that uses currentColor, not necessarily the explicit palette of
multicolor icons. Inspect the saved SVG if exact appearance matters.

SVGs are XML-validated; scripts, event attributes, raster image elements and
external hrefs are rejected. The receipt records the source and locally computed
SHA-256. No rasterization or redesign is part of this export. The default 4 MiB
download cap is sufficient for ordinary icons and can be set explicitly.

## Sources and licenses

Verified on 2026-09-27:

- [Public API](https://iconify.design/docs/api/) is free; hosted open-source
  collections retain their own licenses.
- [API queries](https://iconify.design/docs/api/queries.html): `/search`,
  `/collections`, `/collection`, icon JSON and generated SVG endpoints.
- [Icon sets](https://iconify.design/docs/icons/all.html): free/open-source
  collection licenses; do not label every icon CC0 or attribution-free.

Use the API-returned license title, SPDX identifier when present, author and
upstream URL. If required attribution/license text must accompany a distributed
project, retrieve it from the returned upstream license page, retain its exact
notice, and link it with the exported set. Do not invent a blanket license.

On a blocked request, respect the provider response. Inspect the official
browser source instead of probing private endpoints or paid icon collections.
