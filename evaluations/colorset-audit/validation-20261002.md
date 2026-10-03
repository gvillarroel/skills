# Colorset output audit — 2026-10-02

All 34 canonical skills were reviewed by supported output route. Thirty bundles author visual paint or authored presentation chrome; four have no bundled painter. Authored outputs now use the exact colorset1 or colorset2 tokens. Colorset1 is the default; colorset2 supports explicitly requested or necessary semantic categories. This is a bounded producer, renderer and example audit, not a proof of every arbitrary future program an agent could write.

The shared definition is [docs/colorsets.json](../../docs/colorsets.json), with the [human contract](../../docs/colorsets.md) and [complete per-skill output inventory](coverage.json). Runtime bundles retain independent finite tokens or their own palette copy. They do not require repository documents or sibling skills.

## Coverage and repairs

| Group | Skills | Actual repairs and evidence |
| --- | ---: | --- |
| Diagrams and presentations | 6 | Mermaid, PlantUML, ECharts, Slidev ECharts, Slidev Anime.js and Slidev quality audit: renderer defaults, named/functional paint, Canvas/SVG state, gradient endpoints, CSS hover, PNG gates and runtime asset packs. [Report](diagrams-20261002.md), [exact sources, modes, commands and hashes](diagrams-20261002.json). |
| Custom visuals | 5 | D3, procedural SVG, Three.js, SVG brief and vectorize: finite defaults, custom override rejection, recreation and dithering, material/vertex/light inputs, nested SVG paint, complete generated families and gallery chrome. [Report](custom-visuals-20261002.md), [inventory](custom-visuals-20261002.json). |
| Compositions and video | 7 | Compose synchronized SVG, diagram composition, hierarchy lens, UsefulCharts, HyperFrames, video and Manim: derived tints, wrappers/captions, native/imported modules, highlight and quantitative scales, gallery CSS and actual replay states. [Report](compositions-20261002.md), [inventory and dependencies](compositions-20261002.json). |
| Previews, conversion and reports | 12 | Six provider preview skills, animated SVG to GIF, Asciinema, pixel art, one-bit dither, technical logos and Harbor report aggregation: canonical interface/theme paint, backgrounds, palettes, SVG exports and report charts. [Exact paths and retained tests](support-20261002.json), [browser/media review](support-browser-20261002.json). |
| Data and document bundles | 4 | Google Cloud SKU pricing, Jev batch decisions, repository reviewer creator and simulation data lab: data, SQL, Markdown and JSON output routes reviewed; no bundled authored chart renderer. Simulation's explicit prohibition on live Pi/model evaluations was preserved. |

The fixes apply to actual paint rather than metadata alone. Off-palette inputs fail or are normalized at documented renderer boundaries. Gradient, filter and geometry IDs remain unchanged. Stylesheets supporting both palettes are checked as shared token resources; actual active browser states are inspected separately. HTML script/vendor/decoder/source-color tables are inputs, so the static HTML gate checks CSS and inline SVG and the browser gate checks dynamic output.

Source fidelity is explicit: provider photos/videos/textures/HDRIs, original brand artwork, embedded source images, original recording evidence and requested exact-RGB preserve modes retain original bytes, colors and provenance. Authored controls, framing, labels, captions and technical marks still follow a colorset. Antialiasing, alpha compositing, physical illumination and codec quantization produce derived tones; these are not additional authored tokens. Four pixel/dither lossless derivatives pass actual exact-token pixel checks. GIF motion is checked independently from source paint.

## Validation evidence

- Canonical working-tree gate: 34 skills, 29 independent palette copies, 672 configured artifacts, zero findings. The detached publication tree has a smaller artifact count because ignored generated verification files are absent; its separate release gates must pass before publication.
- Root deterministic support: 21 suites and 259 unit cases pass, including 12 adversarial central-parser tests, original cast preservation, fixed/adaptive/preserve pixel modes, GIF/raster/SVG dither, export identity, sanitized report charts and provider identity/download boundaries.
- Custom producer coverage: 342 deterministic cases, 22 named D3 builders, 66 procedural patterns in both palettes and full/reduced motion, and 1,079 computed SVG inspections over the D3 gallery/composition/logo/texture routes. All 24 Three.js scenes pass build and responsive browser checks.
- Diagram coverage: 31 Mermaid families, 124 canonical SVGs and 178 Mermaid/PlantUML baseline-preservation comparisons. ECharts has 43 chart cards. Final Slidev ECharts checks cover 36 slides and 129 states, with zero errors and two pre-existing density warnings; Anime.js covers 30 slides and 93 states with zero findings.
- Composition coverage: 147 browser states/exports, compose 80 tests, UsefulCharts 243 tests, connector 21 tests and hierarchy decision 11 tests pass. Manim produces an independently inspected 640×360, 5 fps, 15-frame, 3-second MP4.
- Final support browser review: 54 desktop/mobile initial/hover/focus states, zero paint or layout findings. The logo contact sheet checks 12 representative rows, 52 loaded images and seven adaptive choices. The full approximately 8,000-logo audit was not repeated. The pulse GIF is 360×240, 12 fps, 24 frames, 2 seconds, with 20 distinct decoded frames and canonical authored source paint.

[The final runtime ledger](final-runtime-20261002.json) records the selected strict isolated run for each visual bundle, exact artifact hashes, observed model, trace-summary command and current runtime SHA-256 comparison. One supplementary color-contract case per bundle does not replace earlier naturalistic/generalization release cohorts or promote a broader `validating` skill. The group records retain every failed attempt, including evaluator path mistakes, agent assertions, missing dependencies, copied-skill mutation and provider rejection. No failed attempt was relabeled as passing.

Spark was rejected before tools for the current account. The deliberate model exception is observed `openai-codex/gpt-5.6-luna`; HyperFrames uses its existing observed `gpt-6-luna` exception. The model change keeps exact output paths, JSON events, zero tool errors, clean runtime read surface and unchanged copied payload requirements. Execution crossed UTC midnight on 2026-10-03; the audit date follows the user's 2026-10-02 local date.

## Reproduction

Run the required repository and publication gates from the canonical root:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/test-colorsets.py
uv run --script projects/colorset-audit/scripts/run_support_checks.py
uv run --script projects/colorset-audit/scripts/audit_final_runtime_evidence.py
uv run --script scripts/test-pages-output.py
uv run --script scripts/validate-diagram-type-coverage.py --disable-mermaid-browser-sandbox
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

The runtime ledger depends on retained ignored local Pi runs. Published producer fixtures and token checks remain independently reproducible without those bulky runs. Group inventories contain exact skill-specific commands and required paths. Raw runs, screenshots, media, browser installations and build output remain ignored under `evaluations/runs/`, `projects/*/artifacts/` and `dist/pages/`.

## Publication and limits

Publication is being prepared in a detached checkout under `projects/colorset-audit/artifacts/release`. Its explicit source/dependency manifest preserves the original working tree and index. The release uses only the colorset addition to CI, the palette hook to the existing repository validator and the new documentation link. Unrelated root authoring/reviewer CI changes remain outside this publication. Current owning bundles and necessary prior runtime resources are an explicit dependency closure; the mixed Mermaid renderer consolidation is disclosed and tested, not presented as a palette-only text change. The [publication review](diagram-publication-20261002.md) records that distinction.

The [release payload comparison](release-payload-20261002.json) compares all 30 visual bundles with the sealed local Pi payloads. Its initial 69 mismatches contained identical decoded text and differed only in line endings; raw-copying the canonical files closes that worktree byte comparison. The repository's existing `.gitattributes` normalizes committed text to LF. Therefore local Pi payload SHA-256 values describe the tested local bundles; they are not a claim that a fresh Git checkout has identical raw hashes. The committed tree is validated independently with the repository and publication gates, without changing the established LF policy or relabeling prior Pi evidence.

Publication normalizes 130 authored Mermaid/PlantUML SVG fixtures to the same LF form Git stores. This changes no diagram paint, geometry or source facts. The 124 Mermaid pair hashes are refreshed in the gallery manifest. The diagram inventory retains all 178 earlier raw hashes separately from the current publication hashes. Acceptance examples are excluded from runtime Pi payloads, so this correction does not change those sealed bundles.

Independent publication review also restored 13 small historical evidence/prompt documents referenced by the newly published owning backlog rows. The [committed runtime comparison](committed-payload-20261002.json) covers all 30 visual bundles and 9,488 files verified against their Git blobs. Exactly 108 text files normalize CRLF to LF; there are zero substantive differences or missing files.

The full staged whitespace check retains five inherited findings in four exact frozen runtime dependency paths: two reference files with an extra final blank line and the upstream HyperFrames font license/GSAP vendor file. The frozen historical Astra patch also retains two blank context lines required by patch syntax. These five exact paths are excluded only from the scoped whitespace check, preserving runtime/source/evidence bytes; all other staged paths pass that check.

The final deployed commit, GitHub Pages workflow result, frozen release-byte audit and stable example links will be recorded here after publication succeeds. PlantUML chronology remains unavailable upstream. Explicit source-media PNGs require inspection of authored chrome through their matching source/SVG. The Slidev quality isolated case is planning-only and is supplemented by the real full deck audits; no fresh Slidev PDF/GIF/video encode was produced in this pass. Future custom scenes still require their owning paint validator and direct visual review.
