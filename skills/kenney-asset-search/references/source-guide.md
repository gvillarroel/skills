# Kenney source guide

## Catalog and taxonomy

The public asset catalog exposes `2D`, `3D`, `UI`, `Audio`, `Pixel`, and
`Textures`. Individual packs also have theme tags and series. Search examples:

- 2D: platformer, characters, dungeon, space, racing.
- 3D: city, nature, furniture, vehicles, props.
- UI: buttons, input prompts, panels, crosshair.
- Textures: pattern, skybox, terrain.
- Audio: interface, impact, footsteps, music.

These are query recipes, not a claim that every topic currently exists.
Use broad words first; Kenney's search is not a guaranteed semantic matcher.
Filter by the relevant category and inspect neighboring packs/series when useful.

```sh
uv run --script <skill-dir>/scripts/kenney.py search --query "pattern" --category Textures --out textures.json --html textures.html
uv run --script <skill-dir>/scripts/kenney.py search --query "city" --category 3D --page 2 --out more.json
uv run --script <skill-dir>/scripts/kenney.py inspect --id pattern-pack --out selected.json
```

The actual website query parameter is `search`, not `q`. The helper parses the
public catalog page, excludes non-asset links and deduplicates slugs. It fetches
one page at a time. `--limit` is 1–20; fewer results or an empty page describes
that retrieval window, not the complete catalog.

The `previews` command caches up to 20 saved pack thumbnails in a fresh local
directory, capped at 4 MiB each. It preserves option numbers and returns portable
image paths. Reuse those files for later inspection, or choose a new directory
after refining the search. This downloads previews only, not asset ZIPs.

## Stable selection and free download

Use `--id PACK_SLUG`, or `--manifest FILE` with exactly one `--option` or `--id`.
The helper reads the selected source page again. It checks its canonical identity,
the CC0 license link, and the page's `donate-text` free ZIP link. It verifies that
the ZIP belongs to that pack's media directory. The hashed directory in a
download URL is an implementation detail; never fabricate it from a pack name.

Default `--max-mib 512` bounds downloads. The helper rejects HTML responses,
length mismatches, corrupt ZIP members, unsafe paths, collisions and symlinks.
It writes a SHA-256/source receipt with the ZIP's member inventory. The original
ZIP preserves the source package; it is not automatically unpacked.

## Exact member extraction

The archive command reads ZIP names without running their contents. Choose exact
paths from that inventory. `extract` requires a fresh output directory and
retains case-sensitive member names and relative subdirectories. It automatically
adds `License.*`, `Licence.*` or `COPYING` files when present. Its extraction
receipt binds the selected files to the local ZIP hash.

For a named character/action, inspect contact sheets or several actual frames;
filenames alone may be insufficient. For audio, listen to candidate files. For
a 3D model, retain its referenced material and texture files. Do not execute
scripts or binaries included in an asset pack as part of discovery.

## Source references

Verified on 2026-09-27:

- [Asset catalog](https://kenney.nl/assets): category navigation and pack search.
- [Support and licensing](https://kenney.nl/support): asset-page game resources
  are CC0, including commercial use without required attribution.
- [Example free pack page](https://kenney.nl/assets/pattern-pack): free Download
  dialog and optional donation. Paid aggregate bundles and tools are separate.

No official public search API is assumed. If the catalog HTML changes, use the
browser on the same source pages and update parsing only from observed markup.
