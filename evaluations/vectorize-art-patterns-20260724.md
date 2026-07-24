# Vectorize Art Patterns Evaluation — 2026-07-24

## Result

`vectorize-art-patterns` is implemented and passes deterministic, provenance,
structural SVG, colorset-contract, acceptance-gallery, GitHub Pages build,
live-provider, visual-browser, repository, and payload checks. Its release
status remains `validating` because the required isolated Spark forward test
was blocked by provider quota before the first model token.

Failure classification: `infrastructure`.

## Runtime Payload

- Profile: `runtime`
- Files: 17
- Final payload SHA-256:
  `bb4b800dd6c451bb013fb61650a064a1d07d5997c8da91d7339e214eaa38e87d`
- Bundled base images: 3
- Bundled licenses: 3 × `Public-Domain`
- Bundled palette contracts: `colorset1` and `colorset2`
- Palette-contract SHA-256:
  `c81d32ffb0d55d44e7d3102c7470e251baf34f0bb6472fbede7753df8b9a9eb5`
- Acceptance fixture: 21 files under
  `assets/examples/vectorize-art-patterns/`, excluded from the runtime profile

The final strict attempt verified that the copied 17-file runtime payload was
unchanged before and after the run.

## Deterministic and Rights Checks

Command:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py --json
```

Result: passed.

- All four modes produced valid SVG: `organic`, `ink`, `stain`, and `collage`.
- `none`, `repeat`, and `mirror` tile paths were exercised.
- A repeated organic mirror render was byte-identical.
- Both canonical colorsets were exercised in two modes each; every visible
  color token was accepted by the selected bundled palette and both
  `colorset1_safe` and `colorset2_safe` passed.
- A separate real-image rerun was byte-identical with SHA-256
  `d11046a03cf772d5d71f63f3db9e565fcccafe7759fe880fd89d4d9d188583cf`.
- `CC-BY-ND-4.0` and `CC-BY-NC-4.0` were rejected.
- A tampered base-image SHA-256 was rejected.
- The explicit `user-owned` input path produced and validated an SVG.
- Running the test did not create `__pycache__` inside the skill payload.

The bundled manifest passed:

```powershell
uv run --script skills/vectorize-art-patterns/scripts/validate_open_assets.py skills/vectorize-art-patterns/assets/base-images/manifest.json
```

It verified three decoded JPEGs, exact byte counts and dimensions, HTTPS
provenance links, derivative-friendly licenses, required metadata, and
SHA-256 parity.

## Live Provider Smoke

Both supported acquisition paths were exercised during implementation:

- Wikimedia Commons supplied the three bundled public-domain works and their
  `imageinfo`/`extmetadata` records.
- Art Institute of Chicago object `27992` was fetched through the official API
  and IIIF at 400 px, normalized as `CC0-1.0`, then passed
  `validate_open_assets.py`. The ignored smoke artifact SHA-256 was
  `812bf8661aed4824cabedb24968b25392ccc737f46d912608553642d76f48ab1`.

The downloader also rejected an output path outside the manifest directory
before writing a file.

## Real SVG Validation

Generated evidence is stored under the ignored directory
`projects/vectorize-art-patterns-validation/artifacts/`.

| Pattern ID | Mode / tile | Paths | Contours | SVG bytes | SHA-256 |
| --- | --- | ---: | ---: | ---: | --- |
| `hilma-chaos-organic` | organic / none | 4 | 116 | 31,243 | `d11046a03cf772d5d71f63f3db9e565fcccafe7759fe880fd89d4d9d188583cf` |
| `hilma-chaos-stain-mirror` | stain / mirror | 4 | 114 | 31,248 | `5f9aa987cd0215a26f42f50bd191735c8d078788fcdcd84fe1b8b0c3284ca24b` |
| `juan-gris-collage` | collage / none | 7 | 271 | 35,815 | `d62258799d34ee4d655e3c258658bab461555769025c7b6a85811c1d5ff0ffa2` |
| `hilma-pleiade-ink-mirror` | ink / mirror | 1 compound path | 31 | 23,395 | `55acadc8ca5a41e2c5a965c52701771d211895fbe07df450482cf8bb0c30329c` |

All four passed `validate_art_svg.py` against their sidecar reports. The checks
confirmed nonempty direct `title` and `desc`, finite view boxes and path data,
source-hash parity, JSON provenance, internal-only references, and zero
`image`, `script`, or `foreignObject` elements. Both mirror outputs contained
the required SVG `pattern` element.

## Colorset Contract and Published Gallery

The deterministic gallery builder produced four base motifs and eight
palette-specific SVGs:

- four `colorset1` variants and four `colorset2` variants;
- four unique ordered-path geometry hashes, with exact geometry parity inside
  every CS1/CS2 pair;
- 13 visible color tokens in total, all drawn from the bundled contracts;
- zero raster embeds or external runtime assets;
- manifest SHA-256
  `9c743dfdec9ecbf2b588d1ef44cd40401b311415d0929db25ffea07f11474c24`.

The gallery rebuild was byte-deterministic across all 18 generated SVG and JSON
files. `validate_example_gallery.py` passed manifest/page/report/SVG parity,
colorset counts, geometry pairing, stable IDs, default visibility, local
downloads, stale-file detection, and palette safety. The example set is
registered as `vectorize-art-patterns` in the main Pages catalog.

## Browser Review

### Original SVG sheet

Playwright CLI loaded a local visual-review sheet containing all four SVGs at
full and thumbnail sizes. Eight of eight SVG image instances completed with
nonzero natural dimensions. The review found:

- organic spirals and asymmetric marks remained recognizable;
- rare gold, green, and blue accents survived palette reduction;
- the Cubist collage retained object hierarchy at thumbnail size;
- the ink output retained irregular calligraphic loops;
- mirror axes met continuously at the vertical, horizontal, and four-way
  junctions; the intended kaleidoscopic axes remained visible;
- no clipped dominant contour, accidental spike, missing color field, or
  raster fallback was visible.

The only console entry was the review server's missing optional `favicon.ico`;
all SVG resources returned HTTP 200.

### GitHub Pages gallery

Playwright CLI then inspected the built Pages output at 1,440 × 1,000 and
390 × 844:

- CS1 and CS2 each showed exactly four cards and updated `aria-pressed`, the
  URL query, descriptive copy, accents, and swatches;
- all eight SVG image resources loaded with nonzero natural dimensions, and
  every one of the eight download URLs returned HTTP 200;
- a direct hash for `vectorize-juan-gris-collage-cs1` overrode a conflicting
  `colorset2` query, revealed the correct card, and scrolled it into view;
- the 390 px layout had zero horizontal overflow and every visible card stayed
  within the viewport;
- desktop CS1, desktop CS2, and mobile CS2 screenshots passed visual review;
- the page emitted zero console errors or warnings.

Screenshots and the machine-readable gallery report remain in the ignored
`projects/vectorize-art-patterns-validation/artifacts/` tree.

## Publication

- Implementation commit: `c708b01f`
- Pull request: `#18`
- Merge commit: `54d1ca5c`
- Pages workflow: `30105911161`, successful in 1m53s
- Live gallery:
  `https://gvillarroel.github.io/skills/examples/vectorize-art-patterns/`

Post-deploy verification fetched the live main catalog, gallery, manifest, and
all eight SVG resources. The catalog contained the gallery link, the gallery
contained all eight stable pattern IDs, the remote manifest SHA-256 matched
`9c743dfdec9ecbf2b588d1ef44cd40401b311415d0929db25ffea07f11474c24`
exactly, and every SVG returned HTTP 200 with media type `image/svg+xml`.
Production Playwright reached `data-ready="true"`, showed four default
`colorset2` cards, found zero horizontal overflow, and reported zero console
errors or warnings.

## Repository Gates

The following checks passed:

```powershell
python C:\Users\villa\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/vectorize-art-patterns
uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py --json
uv run --script skills/vectorize-art-patterns/scripts/build_example_gallery.py
uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
git diff --check
```

The Pi harness suite passed 11/11 tests. Pattern-ID validation covered 1,236
canonical IDs with zero IDs above the 48-character review threshold. The Pages
build completed with 672 files and copied the gallery into
`docs/examples/vectorize-art-patterns/`.

The canonical 17-file runtime bundle was also copied to the ignored local
installation at `.agents/skills/vectorize-art-patterns`; every installed file
matched its source SHA-256.

## Isolated Spark Forward Tests

Required model: `openai-codex/gpt-5.3-codex-spark`.

Final contract command:

```powershell
uv run --script scripts/run-pi-skill-eval.py vectorize-art-patterns --prompt-file evaluations/pi-prompts/vectorize-art-patterns-contract-smoke.md --mode json --strict --run-id 20260724-vectorize-art-patterns-contract-smoke-spark-2-final --timeout-seconds 900 --expect-output outputs/contract/base-assets-validation.json --expect-output outputs/contract/hilma-organic-mirror.svg --expect-output outputs/contract/hilma-organic-mirror.json --expect-output outputs/contract/hilma-organic-mirror-validation.json --expect-output-json-field outputs/contract/base-assets-validation.json::ok=true --expect-output-json-field outputs/contract/base-assets-validation.json::asset_count=3 --expect-output-json-field outputs/contract/hilma-organic-mirror.json::pattern_id=hilma-organic-mirror-contract --expect-output-json-field outputs/contract/hilma-organic-mirror.json::mode=organic --expect-output-json-field outputs/contract/hilma-organic-mirror.json::tile=mirror --expect-output-json-field outputs/contract/hilma-organic-mirror-validation.json::ok=true --expect-output-json-field outputs/contract/hilma-organic-mirror-validation.json::pattern_element_count=1 --expect-output-json-field outputs/contract/hilma-organic-mirror-validation.json::image_element_count=0
```

Recorded attempts:

| Run ID | Result | Tokens | Tool calls | Payload integrity |
| --- | --- | ---: | ---: | --- |
| `20260724-vectorize-art-patterns-contract-smoke-spark-1` | `The usage limit has been reached` | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-contract-smoke-spark-2-final` | `The usage limit has been reached` | 0 | 0 | passed |
| `20260724-vectorize-art-patterns-colorset-pair-spark-1` | `The usage limit has been reached` | 0 | 0 | passed |

All three attempts observed the required provider/model but stopped before the
first prompt read. No task artifact was produced. The colorset-pair attempt
used the final 17-file runtime payload and required exact CS1/CS2 outputs,
per-palette validation, and geometry parity. Because the same external quota
condition repeated on the final payload, the naturalistic, generalization, and
boundary prompts were not sampled.

## Remaining Release Gate

When Spark quota is available, rerun:

1. contract smoke once;
2. colorset pair once;
3. naturalistic forward three times, requiring at least two passes;
4. generalization three times, requiring at least two passes;
5. boundary recovery once.

Then run independent SVG validation and browser review on every successful
visual artifact, summarize each JSON event trace, confirm the focused read
surface and unchanged payload, update this record, and move the backlog status
from `validating` to `done`.
