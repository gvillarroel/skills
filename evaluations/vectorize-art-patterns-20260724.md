# Vectorize Art Patterns Evaluation — 2026-07-24

## Result

`vectorize-art-patterns` now produces deterministic single SVGs and independent
multi-pattern collections from verified open or user-owned raster art. The
local 300-pattern acceptance fixture passes provenance, structural SVG,
colorset, global uniqueness, deterministic rebuild, GitHub Pages, and browser
checks.

The skill remains `validating` because the required isolated Spark forward
tests are externally blocked by provider quota before the first model token.
This is classified as `infrastructure`, not a product or skill failure.

## Rights and Runtime Inputs

- Six bundled JPEG sources: five marked `Public-Domain` and one Art Institute
  of Chicago open-access image marked `CC0-1.0`.
- Exact source dimensions, byte counts, HTTPS provenance, license URLs, and
  SHA-256 values are stored in `assets/base-images/manifest.json`.
- Commons and Art Institute acquisition paths enforce a derivative-friendly
  allowlist and atomic writes.
- `CC BY-ND`, `CC BY-NC`, unknown, and tampered records fail closed.
- Colorset authority:
  `assets/palettes/colorsets.json`.
- Colorset-contract SHA-256:
  `c81d32ffb0d55d44e7d3102c7470e251baf34f0bb6472fbede7753df8b9a9eb5`.

## Deterministic Vectorizer Checks

Command:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py --json
```

Result: passed.

- All four modes passed: `organic`, `stain`, `ink`, and `collage`.
- `none`, `repeat`, and `mirror` tile behavior passed.
- Colorset 1 retained its required `#9e1b32` anchor.
- Colorset 2 retained its required `#007298` anchor.
- Identical inputs remained byte-identical.
- Seed `8675309` reproduced composition SHA-256
  `ea0052478b2f065a895493480f2b731b1a71ff52b17daf21baa2933c939c912b`.
- Changing the seed changed both composition identity and SVG bytes.
- Invalid crop scale, negative flow strength, and zero flow frequency were
  rejected.
- Public-domain manifest, explicit `user-owned` processing, restricted-license
  rejection, and tampered-hash rejection passed.

The variation pipeline uses deterministic crop, OpenCV affine rotation, and
smooth sinusoidal `remap` displacement with reflected borders before tracing.

## 300-Pattern Acceptance Fixture

Commands:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/build_example_gallery.py
uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py
```

Result: passed.

| Metric | Result |
| --- | ---: |
| Patterns | 300 |
| Families | 15 |
| Colorset 1 / Colorset 2 | 150 / 150 |
| Organic / stain / ink / collage | 80 / 80 / 60 / 80 |
| Unique output hashes | 300 |
| Unique raster compositions | 300 |
| Unique complete geometries | 300 |
| Globally unique path signatures | 1,300 |
| Unique variation seeds | 300 |
| SVG `<use>` elements | 0 |
| Tiled collection members | 0 |
| Total SVG bytes | 7,472,672 |

Source distribution:

- `bailly-beauties-fancy`: 60;
- `hilma-pleiade-14`: 20;
- `hilma-primordial-chaos-16`: 40;
- `juan-gris-still-life-1919`: 40;
- `kandinsky-improvisation-27`: 60;
- `redon-flower-clouds`: 80.

Stable evidence:

- Catalog fingerprint:
  `061c68d2c797a1acf0d497abc65adaadeb836f3b457ec0b5310ab10fd7589c74`.
- Manifest SHA-256:
  `4926a5c21ac7e1886d3d2bb28fb65547edab39667af7f5f063ab85784d5a16d6`.
- Aggregate SHA-256 over all 602 generated `.svg` and `.json` files:
  `996528be8230a456dde46d64a4f9c542a8e82e8a6276de63fc0e43e4ca825e00`.

A second complete build produced the same 602-file aggregate digest exactly.
The builder fails on the first repeated composition, complete geometry,
individual path signature, or variation seed. Colorset changes are not counted
as new drawings.

## Browser and Visual Review

Playwright validated the built Pages fixture at 1,440 × 1,000 and 390 × 844.

- The default page rendered 24 of 300 cards and all 24 SVGs loaded.
- Pagination reported 13 pages; page two contained ordinals 25–48.
- Colorset 1 returned 150 members across seven pages.
- Colorset 1 plus ink returned 30 members across two pages.
- Search for `marbled current` returned exactly 20 members.
- The `pasted-rhythm` family filter returned exactly 20 members.
- Direct hash `vectorize-pasted-rhythm-20-cs2` selected the correct family and
  Colorset 2 subset and rendered the target.
- Desktop used three columns; mobile used one column.
- Both viewports had zero horizontal overflow and zero console errors.

A stratified review rendered 60 SVGs: four deterministic members from each of
the 15 families. All 60 loaded successfully and showed non-geometric variation
appropriate to their organic, stain, ink, or collage family.

A browser raster audit over all 300 SVGs found:

- median contrasting-pixel coverage: 55.11%;
- fifth percentile: 21.71%;
- minimum: 4.75%, with no member below 1%;
- all 150 Colorset 2 members exceeded 0.5% chromatic coverage.

Ignored screenshots and machine-readable reports remain under
`projects/vectorize-art-patterns-validation/artifacts/`.

## GitHub Pages

The fixture uses stable page ID `vectorize-art-patterns` and is registered in
the main Pages catalog. `scripts/build-pages.py` completes with 1,256 files and
copies the 300 SVG downloads, reports, manifest, responsive page, and gallery
runtime into `docs/examples/vectorize-art-patterns/` (34.95 MiB total Pages
output in the final local build).

The 300-pattern gallery was published through:

- implementation PR `#20`;
- merge commit `d5073f434a6d2d476042c97689357b7e903ec22f`;
- successful Pages workflow `30132325089`;
- live URL:
  `https://gvillarroel.github.io/skills/examples/vectorize-art-patterns/`.

Production verification returned HTTP 200 for the page and manifest, matched
catalog fingerprint
`061c68d2c797a1acf0d497abc65adaadeb836f3b457ec0b5310ab10fd7589c74`,
and fetched all 300 SVGs successfully. Every live SVG reported
`image/svg+xml`, was nonempty, and matched its manifest SHA-256. Production
Playwright repeated the desktop/mobile, filtering, pagination, direct-link,
footer, and visible-image checks with zero console errors.

## Repository Gates

Required final commands:

```powershell
python C:\Users\villa\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/vectorize-art-patterns
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py --json
uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
git diff --check
```

All listed gates passed on 2026-07-24. The final runtime profile contains 21
files with payload SHA-256
`f03ad57a1d6d6c3227d8fc575af5143e7c184aff6c0b46b4d5373a089b31c540`.

## Isolated Spark Forward Tests

Required model:
`openai-codex/gpt-5.3-codex-spark`.

Existing attempts:

| Run ID | Result | Tokens | Tool calls | Payload integrity |
| --- | --- | ---: | ---: | --- |
| `20260724-vectorize-art-patterns-contract-smoke-spark-1` | usage limit | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-contract-smoke-spark-2-final` | usage limit | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-colorset-pair-spark-1` | usage limit | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-unique-collection-spark-1` | usage limit | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-unique-collection-spark-2-final` | usage limit | 0 | 0 | passed |

All attempts observed the required provider/model but stopped before the first
prompt read. No task artifacts were produced. The new
`vectorize-art-patterns-unique-collection.md` case exercises exact paths,
six seeded independent compositions, both colorsets, and collection-level
composition/geometry/path uniqueness.

The final attempt observed the required model, produced valid JSON events with
no tool errors, and preserved the final 21-file payload byte-for-byte. It
stopped in 4.562 seconds with `The usage limit has been reached`, zero tokens,
and zero tool calls; the event summarizer passed.

## Remaining Skill Release Gate

When Spark quota is available:

1. run the unique-collection and colorset-pair cases once;
2. run the naturalistic case three times and require at least two passes;
3. run the generalization case three times and require at least two passes;
4. run boundary recovery once;
5. inspect every successful artifact and focused read surface;
6. move the skill from `validating` to `done` only after those thresholds pass.
