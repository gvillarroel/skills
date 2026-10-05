# SVG-family native validation

Date: 2026-10-05. Scope: `d3`, `procedural-svg-animation`, `svg-brief-design`, and `threejs-animated-3d`. Canonical runtime sources and the two logo evaluation prompts were frozen before the isolated forward cohorts. This note records focused source and native checks, final source hashes, and the independently accepted primary-logo R2 cohort. Broader isolated acceptance is recorded by the cohort owner.

## Frozen behavior

Colorset1 categories use primary red, the bundled dark/middle neutral interleave including black, white, then the remaining red tokens and pink. Allocators preserve that stable order and remove only the actual canvas token. All four palette copies have SHA-256 `b557cb508d9b31534506b9ae22ad3073e8951b49f6ab4e2251f6727ac92a405c`. The allowed tokens, semantic roles and `textOnFill` mappings remain unchanged; each complete colorset2 object equals its pre-change version.

D3's private logo engine now uses the same categorical sequence. Its source equals the previous source after masking that one sequence, so colorset2 geometry and engine paint rules remain unchanged. Treemap family headers use the category allocator; their child tone ramps retain their previous ordered mapping. Starter network groups and context-window identities use the new category order. Named status paints such as watch, stable and healthy retain their previous values independently of the allocator.

The procedural generator has an independent six-band numeric mapping for Gray–Scott concentration and join-tree field values. Deterministic rendered field comparisons preserve the previous SVG bytes for both colorsets. SVG scaffolds retain their semantic ink and arrows. Three.js takes its categorical materials from the bundled JSON while keeping white lights, SRGB rendering, semantic materials and scalar mappings.

The logo builder needed a narrow repair because its existing whole-document palette adapter also recolored embedded colorset2 registries. It now adapts the surrounding UI while restoring exact bundled JSON, vendor and engine resources, and supplies both palettes to the switchable normalizer. Static registry checks compare the engine's consumed `name`, `allowed`, `roles` and `sequence` fields; the complete allocator metadata remains in JSON. The validator excludes only the byte-identical bundled normalizer from authored-paint syntax scanning, because its JavaScript `rgb(value)` helper is not a CSS paint. Custom functional paint and reordered engine registries still fail.

## Focused checks

All commands were run from the repository root with `uv run --script`; the JavaScript syntax check used Node. Retained bulky outputs are under the original ignored `projects/colorset1-gray-order/artifacts/` location. Future project scripts and evidence use the stable `projects/grayscale-interleave/` project.

| Command after `uv run --script` | Result |
| --- | --- |
| `skills/d3/scripts/test_category_order.py` | 4 tests passed: Python/native JS allocation parity through overflow, logo sequence/semantic parity, treemap header/child separation, switchable studio registries and negative validation cases. |
| `skills/d3/scripts/test_colorset_adapter.py` | 5 tests passed. |
| `skills/d3/assets/examples/skill-tests/test_colorset_priority.py --artifacts projects/colorset1-gray-order/artifacts/d3-capacity` | 2 tests passed; all 16 usable white-canvas solids precede overflow rims, with native text mapping. |
| `skills/d3/assets/examples/skill-tests/test_build_treemap.py --artifacts projects/colorset1-gray-order/artifacts/d3-treemap` | 5 tests passed, including native sizes, replay, reduced motion, data boundaries and portable SVG export in both palettes. |
| `skills/d3/assets/examples/skill-tests/test_create_d3_svg_starter_priority.py --artifacts projects/colorset1-gray-order/artifacts/d3-starters-final` | Passed all five starter modes in both palettes, preserving source data, statuses and labels. |
| `skills/d3/assets/examples/skill-tests/test_build_dense_task_overlap.py --artifacts projects/colorset1-gray-order/artifacts/d3-dense-overlap` | 3 tests passed, including native geometry, composited pixels, replay, reduced motion and portable export. |
| `skills/procedural-svg-animation/scripts/test_category_order.py` | 3 tests passed; six connected-scene category fills and exact scalar field byte comparisons in both palettes. |
| `skills/procedural-svg-animation/scripts/test_connected_scene.py` | 4 tests passed, including actual Chromium labels, routes, movers and reduced motion. |
| `skills/svg-brief-design/scripts/test_scaffold.py` | 17 tests passed. |
| `skills/procedural-svg-animation/scripts/build_procedural_gallery.py --check` | Passed 66 patterns; no missing, extra or changed managed files after regeneration. |

`node --check skills/d3/assets/templates/logo-engine.js` passed. The logo fixture was regenerated with the current builder and its existing `../d3-logo-textures/index.html` link, default options and stable IDs. This also brought its previously stale embedded finalizer into agreement with the already canonical runtime; that fixture-only generated drift is intentional.

The final logo checks were:

```bash
uv run --script skills/d3/scripts/validate_logo_artifact.py skills/d3/assets/examples/d3-logo-design/index.html --require-colorset colorset1 --json-report projects/colorset1-gray-order/artifacts/reviews/logo-fixture-final.json
uv run --script skills/d3/scripts/verify_logo_gallery.py skills/d3/assets/examples/d3-logo-design/index.html --json-report projects/colorset1-gray-order/artifacts/reviews/logo-native-final.json --small-logo-screenshot projects/colorset1-gray-order/artifacts/images/logo-small-final.png
```

Both passed. The browser verifier checked 90 unique cards/geometries, full native lettering, all controls, both palette switches and all 90 replay actions. Findings, console errors, page errors and external requests were empty. Manual inspection confirmed readable native compact NORTHLIGHT lettering, the red/black/middle-gray treemap headers with unchanged child ramps, and the 100-label dense overlap output.

The Three.js standalone builder and validator passed with `--token-count 8 --colorset colorset1`. Reports and the manually inspected native PNG are `projects/colorset1-gray-order/artifacts/reviews/threejs-interleaved.json` and `projects/colorset1-gray-order/artifacts/images/threejs-interleaved.png`. Desktop/mobile and timed states retained nine exact material tokens, white lights, visible motion, usable controls and no browser errors. Material tokens are not a claim that every shaded output pixel equals an unlit token.

## Source audit and limits

The read-only reviewer is `projects/grayscale-interleave/scripts/svg-review-native-evidence.py`. Run it with `--report projects/grayscale-interleave/artifacts/reviews/svg-native-evidence.json`. Its final review passed palette boundary checks, the canonical engine comparison and retained native evidence, and emits 96 explicitly owned canonical candidate paths excluding root-owned palette JSON copies. Additional authored paths are the two SVG project reviewers and this note plus the primary-logo JSON/Markdown pair; bulky artifacts and caches are excluded.

The final runtime snapshots, excluding acceptance examples and dependencies, are:

| Skill | Files | SHA-256 |
| --- | --- | --- |
| `d3` | 296 | `1c61ccd9693630dc686eb408cba1736fe83fbf0ff70449a44e2894b779ef2450` |
| `procedural-svg-animation` | 22 | `e889f33fb6c3ddcab0347f8979c0b7bd40465e9244303dd999c8b8dff0830b05` |
| `svg-brief-design` | 10 | `e64b960ffdc7693246c222b35b3ff485751d25c1a2b84d76e1cb953334639af1` |
| `threejs-animated-3d` | 11 | `049d57aba49b0c8f0cba9e29b0c2db61b120ca4240698efe5129ba401fa204f8` |

The retained complete logo native report has SHA-256 `ebd85f18aa66fc68798e90239e29825cc3dc0ba48a5c12a7ac9319d94ae032d0`; the Three.js native report has SHA-256 `2a2e1284887412a4067d0d6c428d0cf7e771be94330663c30dc7b1515a0d835b`. The final reviewer recomputes those hashes and confirms both reports pass with no findings. These focused native proofs precede the D3 guidance-only repair; their builder, engine and palette bytes did not change during that repair.

All 66 procedural fixture geometries and non-ink timing attributes equal their previous values after masking exact hex paints. Two black/white text-fill switch times in the stateful infographic changed deterministically with the new substrate luminance; the reviewer verifies that exception is restricted to readable text ink, with valid ordered times. Other motion paths and clocks did not change.

Development failures were retained in the session and are described here: the first procedural scalar fixture lacked a required `signature`; the first starter run exposed status paints accidentally following category indices; palette-only logo refresh and the first full rebuild exposed stale/altered embedded registries and a validator false positive for its trusted normalizer. Each received the narrow repairs described above and the final focused checks passed. The earlier failed starter artifacts remain in `artifacts/d3-starters/`; the final artifacts are separate.

The categorical order improves adjacent neutral separation but does not certify every spatial adjacency, cyclic wrap, transparency blend or contrast-filtered direction palette. Very light gray followed by white remains a small gap on a canvas that permits both; arrow and text contrast requirements remain independent. Native inspection covered representative D3/Three.js outputs and the logo verifier's complete gallery, not every manually authored future scene. The root owns broader isolated acceptance, repository-wide validation and publication.

## Forward development diagnosis and guidance refreeze

The first primary-logo cohort used D3 runtime SHA-256 `5945460536d87fef41bcdb38d00460c51c64347a58409994562d54be10ee9a63` (295 files). Preserve every original outcome. The command contract and first natural run passed their strict gates; the remaining two natural runs failed:

- `gray-20261005-logo-r1-d3-naturalistic-2` timed out with return code 124 after 307.523 seconds. Its retained event trace also contains two tool errors: applying `--require-extended` to the studio HTML at line 238, and running the Playwright verifier with plain Python at line 337. It recovered to create all four output paths, but that recovery does not pass either strict condition. It also ran the full interaction verifier instead of the requested compact check and added separate exports.
- `gray-20261005-logo-r1-d3-naturalistic-3` exited Pi successfully but failed strict event validation with return code 4. Artifacts and skill integrity passed; the sole event finding was plain-Python `verify_logo_gallery.py --help` at line 224, which raised `ModuleNotFoundError: No module named 'playwright'`. Its later uv invocation created all required outputs. Manual inspection of both retained native PNGs confirmed readable ATLAS lettering; those images are supplementary development evidence, not accepted forward runs.

The runtime guidance had not named the logo browser verifier or its compact command. A narrow repair adds `references/logo-studio.md`, directly links it from the mandatory studio route, names the verifier's uv invocation including `--help`, and provides the `--small-only` report/screenshot flags. The compact reference includes the runnable sequence and the settled-SVG boundary for extended paint checks. No renderer, API, template or palette changed in this repair.

The new D3 runtime is frozen at SHA-256 `1c61ccd9693630dc686eb408cba1736fe83fbf0ff70449a44e2894b779ef2450` (296 files). The other three bundles remain unchanged. Category regression tests still pass all four cases, the documented uv verifier help succeeds, and the diff check passes. The two primary-logo prompts and original run folders remain unchanged; no failed first-cohort run is counted as passing.

## Final primary-logo forward acceptance

[Primary-logo validation](primary-logo-validation.md) and its [hash-bound JSON](primary-logo-validation.json) accept the fresh unchanged-prompt R2 cohort on that exact current 296-file runtime. The command contract and natural repetitions 2 and 3 jointly pass strict and independently inspected native gates; the complete three-repetition natural cohort reaches 2/3. Each run observes only `openai-codex/gpt-5.6-luna`, preserves the copied payload, and supplies the exact HTML, static report, native report and 96 × 64 PNG paths. The final reviewer independently confirms current and copied runtime hashes, prompt text and raw byte hashes, actual artifact bytes, read surfaces, report findings and observed model.

All four retained outputs pass current independent static/native compact checks. All eight authored and independently recaptured PNGs were opened at original size and show complete readable ATLAS lettering without clipping or glyph overlap. Their common SHA-256 is `0ae2904d6816a045385205061577a177c54c6f0d67dd40686a0d377eee8a371b`. R2 naturalistic-1 remains a strict failure: an unnecessary plain-Python Pillow import at event line 527 fails after the documented uv flow succeeds. Its later standard-library recovery and native artifact pass do not contribute to acceptance. The original R1 timeout and Playwright import failure remain retained separately, with raw hashes in the final JSON.
