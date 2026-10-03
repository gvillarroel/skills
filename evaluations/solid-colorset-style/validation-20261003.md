# Solid colorset presentation revision — 2026-10-03

All 30 bundles with authored visual output now prioritize opaque single-color fills without decorative outlines. Interior labels use exact black or white, chosen by maximum WCAG relative-luminance contrast on the effective backing. Categories consume the complete usable palette before explicit border variants. The four nonvisual bundles have no painter to restyle. The existing [34-bundle inventory](../colorset-audit/coverage.json) remains the output-format and source-fidelity record.

The [canonical contract](../../docs/colorsets.md) and all 30 runtime palette copies contain a complete unique `solidSequence` and `textOnFill` map. Allowed color tokens remain unchanged. On white, colorset1 has 16 usable solid colors and colorset2 has 36. Saturated solids come first; soft colors come late. Stable category identity, direct labels and meaningful geometry remain required when nearby shades would otherwise be ambiguous.

Overflow reuses a solid fill with a distinct contrasting palette border, then solid/dashed/dotted traces and widths from 1 to 3 pixels. Shared allocators require at least 3:1 border-to-fill contrast and expose finite capacity. Beyond that capacity, labels, symbols or split views distinguish further identities. Meaningful connectors, axes, open line art, physical shading, explicit user styles and keyboard focus remain supported. Source photos, videos, textures, original logos, imported artwork and exact-RGB conversion modes retain their provenance and fidelity.

## Runtime and source evidence

The final [runtime ledger](final-runtime-20261003.json) selects a strict isolated Pi run whose payload hash matches each current authored-output bundle. Each run copies only that skill's runtime resources, excludes acceptance examples, disables ambient context and discovery, requires exact nonempty artifact paths, validates event JSON and the observed model, rejects tool errors and verifies the copied bundle is unchanged. Each selected trace is summarized again with `summarize-pi-json-events.py`. The ledger retains every earlier attempt, including failures and passing snapshots superseded by subsequent fixes.

Existing model exceptions apply: `openai-codex/gpt-5.6-luna` for 29 bundles and `openai-codex/gpt-6-luna` for HyperFrames. The provider's previously documented Spark rejection is not relabeled as a Spark pass. These are supplementary style regressions; existing broader release statuses and unresolved release cohorts are preserved in [SKILLS.md](../../SKILLS.md).

[Archival prompt normalization](prompt-archival-normalization-20261003.json) records original and committed-reference hashes for seven composition prompts whose trailing line whitespace was removed before committing. Original submitted prompts and their sealed run hashes remain intact; this formatting change is not another model trial.

The [current bundle audit](bundle-audit-20261003.json) checks all 34 source trees and 68 runtime/full profiles. Successful copied-profile checks may be reused only when every current file produces the identical size/hash digest; changed profiles are copied and checked afresh. Source snapshots are checked again at completion. The Pages workflow independently runs a fresh full copied-bundle audit. Committed runtime evidence discloses UTF-8 CRLF-to-LF normalization rather than representing it as another model trial.

## Rendered results

The renderer reports contain exact commands, output hashes, retained failures, independent inspections and practical limits:

- [Diagram renderers](../diagram-solid-style/validation-20261003.md): six current strict trials; Mermaid's 31 families and 62 static/animated pairs (124 SVGs); 54 PlantUML SVGs and two Ditaa PNGs across both palettes; 43 ECharts gallery cards; 14 actual ECharts SVG SSR cases; 36 ECharts slides/129 states and 30 Anime.js slides/93 states. The final ECharts deck has zero errors and two preexisting density warnings. PlantUML chronology retains its documented upstream-unavailable outcome.
- [Custom visuals](../custom-solid-style/validation-20261003.md): five bundles, each with one contract case and three naturalistic repetitions (20 strict passes), plus browser, animation, source-geometry and vendor-byte checks. Reviews cover both D3 palettes, 24 Three.js scenes, 66 procedural SVGs, 60 vectorized derivatives and both abstract maps. Semantic opacity is marked explicitly; ordinary static category fills remain opaque. Meaningful reveal/focus transitions retain their timing.
- [Composition and video](../composition-solid-style/validation-20261003.md): seven current strict trials, 350 producer regressions, 6,240 independent allocator checks and 83 browser states. Navigation, zoom, focus, reduced motion, analytical exports and the 1,200-record hierarchy fixture are covered. A real three-second H.264 Manim output was inspected; its existing SVG text/CSS import limitation is recorded. HyperFrames received preflight and project-generation checks rather than a claimed fresh supplementary MP4.

Support validation passes [21 suites/264 cases](support-tests-20261003.json), including provider preview chrome, terminal themes, image conversions, technical-logo controls and the Harbor report consolidator. The [support browser/media review](support-browser-20261003.json) checks 42 browser states, four raster outputs and a decoded 24-frame/two-second GIF with 13 distinct frames. Additional actual-browser checks cover [Harbor's 24 unique borderless categories and error badge](harbor-browser-20261003.json) and [logo captions/controls on desktop and mobile](logo-browser-20261003.json). Original brand/source paint is excluded from authored-palette assertions.

[Independent review](independent-review-20261003.md) found and repaired real defects beyond token membership: inherited label halos/backings, outer ECharts labels, translucent canvas contrast, redundant static opacity, decorative D3 rims, inverse navigation text, procedural gallery chrome, a Harbor CSS cascade error and a logo unavailable-state caption. Visual inspections complement computed paint tests; none certifies every possible future output.

Mermaid's final native-family pass checks 186 static/settled/mid-reveal states across both palettes. It includes closed-path backings, actual translucent paint-order composites and referenced marker pairing, rather than only rectangle backgrounds. A separate independent review of all 62 static SVGs confirms their hashes remain stable during acceptance and finds zero unexplained interior/actor-caption contrast failures. Sequence, Venn, Cynefin and Radar screenshots were inspected after the final batch. Meaningful reveal opacity, connectors, native glyphs, control regions and semantic overlap fills are preserved.

## Reproduction and repository checks

The [final gate ledger](final-gates-20261003.json) records 12 successful commands: pattern IDs, skill structure, standalone independence, repository payload, colorset metadata/artifacts, Pages output boundaries, the Pi harness, copied bundle validation, authoring/reviewer tests and native diagram coverage. Colorset metadata tests include malformed sequence and wrong-contrast negative cases. The Pages format validator and regenerated public example catalog are also required before publication.

```powershell
uv run --script projects/solid-colorset-style/scripts/run_final_gates.py
uv run --script projects/solid-colorset-style/scripts/audit_final_bundles.py
uv run --script projects/solid-colorset-style/scripts/audit_runtime.py
uv run --script projects/colorset-audit/scripts/run_support_checks.py
uv run --script projects/solid-colorset-style/scripts/collect_support_tests.py
uv run --script projects/solid-colorset-style/scripts/review_support.py
uv run --script projects/solid-colorset-style/scripts/review_harbor.py
uv run --script projects/solid-colorset-style/scripts/review_logo.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

The root interactive preference preview is generated by `projects/solid-colorset-style/scripts/create_preview.py` into ignored project artifacts. It exposes all 16/36 solid choices before an explicit overflow view. Screenshots, videos, dependencies and bulky raw Pi runs remain untracked. Pattern IDs and existing published links are preserved.

[Local installation verification](installation-20261003.json) copied 730 changed source-owned files, then compared all 10,201 canonical files with the ignored repository-local `.agents/skills` installation. Source and installed bundle validation pass with zero source-owned drift. Extra local files are preserved.

## Publication

Final runtime sealing, local installation and exact-SHA Pages publication are being completed. The publication proof will compare public files with the downloaded artifact from the successful workflow, avoiding platform-specific build or line-ending assumptions.
