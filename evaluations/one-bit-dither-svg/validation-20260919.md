# One-Bit Dither SVG validation — 2026-09-19

## Scope

Created `skills/one-bit-dither-svg/` with three deterministic output contracts:

- `original`: black plus white.
- `custom`: one exact user color plus white.
- `regional`: rendered source-color medoids paired independently with whichever of black or white has the stronger WCAG contrast ratio.

The transformer renders a settled local SVG in Chromium or loads a Pillow-decodable raster image, samples an ordered Bayer grid, and reconstructs the result as run-length-compressed SVG rectangles. SVG rendering disables source JavaScript and blocks external resources. Raster loading applies EXIF orientation, converts to RGBA, preserves transparent cells, uses Lanczos resizing, and supports a selected zero-based frame from GIF, animated WebP, or multipage TIFF. The output never embeds a raster `<image>` element. Regional selection uses deterministic weighted OKLab medoids so small saturated zones are not erased by large neutral or gradient regions.

The animated extension directly samples self-contained CSS/SMIL SVGs in Chromium or decodes every composited Pillow raster frame. It uses an explicit constant-rate timeline, holds one ordered-dither phase and regional palette across the animation, flattens transparency onto an explicit background, and produces an optimized GIF through whole-timeline ffmpeg palette generation and palette use. It preserves motion and looping as a new rendered animation rather than flattening one frame.

## Deterministic tests

Command:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/test_stylize_svg.py
```

Result after the direct animated-SVG extension: 27/27 tests passed—19 static tests and eight animated tests. Static coverage includes color parsing, mode palettes, transparent-cell omission, regional determinism, black/white companion selection, retention of small saturated zones, SVG aspect ratio, profile density ordering, explicit profile-field overrides, independent validator round trips, embedded profile and source provenance, rejection of raster-image injection, PNG/JPEG/WebP/BMP/TIFF detection, animated GIF frame selection, EXIF orientation, PNG alpha, and CMYK JPEG normalization. Animated coverage includes raster source-timing resampling, cyclic duration extension, animation-wide regional palette assignment, direct SMIL capture, direct CSS capture, required SVG capture duration, blocked external SVG resources, end-to-end SVG and raster ffmpeg encodes, exact two-color palettes, source-provenance checks, and actual-motion validation through distinct decoded frames.

Python compilation passed for all six shipped scripts.

## Real render and browser review

The local validation scene at `projects/one-bit-dither-svg/artifacts/svgs/source.svg` was rendered at 640×360 with a 4-pixel cell, 4×4 Bayer matrix, and contrast 1.15.

| Mode | Palette/regions | Rectangle runs | Validator |
| --- | --- | ---: | --- |
| original | `#000000`, `#ffffff` | 4,516 | pass |
| custom | `#b7410e`, `#ffffff` | 4,516 | pass |
| regional | 8 source-color regions plus required black/white companions | 4,846 | pass |

Microsoft Edge rendered every generated SVG with zero console errors or warnings. Browser screenshots and converter previews were both 640×360. After compositing preview transparency over the browser's white page background, all three comparisons had zero changed pixels, an empty difference bounding box, and zero extrema in every RGB channel.

Visual inspection confirmed recognizable lighthouse, cloud, sun, sea, waves, and rounded transparent corners. The first frequency-only regional prototype collapsed the red sun into the dominant blue/light cluster; that failure led to the weighted OKLab medoid algorithm and a retained saturated-zone regression test. The corrected regional preview keeps the red sun, yellow lighthouse, dark sky/sea families, and their spatial zones.

## Image-dependent quality profiles and D3 showcase

Added four named baselines whose individual fields remain overridable:

| Profile | Render width | Cell | Matrix | Contrast | Regional colors | Intended route |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| compact | 768 | 5 | 4 | 1.25 | 6 | broad silhouettes and large flat geometry |
| balanced | 960 | 3 | 4 | 1.15 | 8 | ordinary illustrations, logos, and charts |
| detailed | 1280 | 2 | 4 | 1.05 | 12 | text, thin lines, compact symbols, and narrow semantic edges |
| manual | 768 | 4 | 4 | 1.15 | 8 | backward-compatible baseline and fully explicit tuning |

The showcase at `projects/one-bit-dither-showcase/` generated three sources through the installed `d3` skill: a six-bar chart, an eight-row lollipop chart with thin stems and labels, and a multicolor wedge logo. Browser extraction waited for transitions to settle and inlined computed SVG paint and typography styles before transformation. Each source was converted to `original`, `custom`, and `regional` outputs. Custom colors were `#234e70`, `#0b6e4f`, and `#5b2a86`, respectively.

All nine accepted outputs use `detailed` at 1280×720 with 2-pixel cells and a 4×4 Bayer matrix. The logo was first rendered with `balanced`; visual inspection showed that its broad wedges survived but its small wordmark and tagline degraded, so the final accepted pass correctly escalated it to `detailed`. This is retained as the routing lesson: classify by the smallest semantically important feature, not by the dominant shape size.

Independent validation passed for all nine SVGs. Every final SVG contains only local rectangle runs and metadata, uses the required palette contract, and has no raster, script, `foreignObject`, or external reference. Microsoft Edge rendered all nine with zero console or page errors; comparison against the converter previews found exactly zero changed pixels and a maximum channel delta of zero for every artifact. The three labeled comparison sheets were visually inspected at 1360×962.

## Raster-input expansion

The input contract now accepts any local raster format decoded by the installed Pillow build, with explicit tested coverage for PNG, JPEG, WebP, BMP, TIFF, and GIF. Input detection is content-based rather than restricted to an `.svg` suffix. Raster provenance is embedded and independently checked through source kind, decoder format, selected frame, frame count, and intrinsic oriented dimensions. SVG remains supported through the prior fail-closed browser path.

The existing 928×523 D3 logo screenshot was used as a real PNG input. It was converted into `original`, `custom`, and `regional` outputs at detailed quality, producing 1280×721 SVGs with 2-pixel cells. All three validators required `sourceKind=raster`, `sourceFormat=PNG`, and `sourceFrame=0`. A labeled source-versus-three-modes sheet was visually inspected. Microsoft Edge rendered the three raster-origin SVGs with zero console or page errors and zero pixel differences from their converter previews, bringing the showcase parity total to 12/12 SVGs.

Additional end-to-end format smokes converted a JPEG to custom `#274690` plus white and a WebP to regional color at balanced quality. Both validators confirmed exact source formats and palette contracts. Deterministic tests additionally cover BMP and TIFF decoding, animated GIF frame selection, EXIF rotation before aspect calculation, transparent PNG preservation, and CMYK JPEG conversion to RGBA.

## Animated GIF extension

The extension adds `stylize_animated_image.py`, `validate_animated_gif.py`, `test_stylize_animated_image.py`, and a compact animation guide. The renderer loads composited multi-frame rasters, samples the source timeline at a requested rate, processes each unique source frame only once, and reuses rendered frames when the resampled timeline repeats them. Regional mode builds one histogram across all selected frames before choosing medoids, preventing per-frame cluster identity swaps. The ffmpeg encoder generates a palette from the complete animation and then applies that palette with `sierra2_4a` by default. Opaque frames disable ffmpeg's reserved transparent palette slot, allowing exact two-color encoding.

The animated entry point loads the sibling static engine with bytecode writes temporarily disabled. A post-test runtime check confirmed that ordinary skill execution creates no `__pycache__`, so the same bundle works cleanly when mounted read-only and does not pollute canonical source.

A deterministic 640×360 harbor scene with a sweeping lighthouse beam, moving sea, rain, clouds, moon, and bobbing boat was converted at the `detailed` baseline to a 1280×720 black-and-white GIF. The accepted artifact has 35 frames, a decoded 2.91-second duration, an effective 12.03 fps, infinite looping, exactly `#000000` and `#ffffff`, and a 395,423-byte file size. The independent validator passed GIF format, positive timing, dimensions, looping, frame-rate tolerance, palette limit, exact original-mode palette, and manifest consistency. `ffprobe` independently reported GIF codec, 1280×720, 35 frames, 2.91 seconds, and the same file size. Visual inspection of the GIF and its 12-position contact sheet confirmed coherent beam movement, a readable boat and lighthouse, stable static-object texture, and fine wave/rain detail.

A second HD acceptance path preserves the requested cross-skill provenance. The existing `d3` skill output `d3-signal-compass` was wrapped in a deterministic three-second SMIL rotation with an asymmetric bearing tick and stationary typography, then rendered through the installed `animated-svg-to-gif` workflow at 1280×720 and 12 fps. `one-bit-dither-svg` transformed that 36-frame GIF in `original`/`detailed` mode. The final GIF retains all 36 frames and the exact three-second duration, loops infinitely, contains exactly black and white, and is 274,697 bytes. The independent validator and `ffprobe` both pass. Direct inspection of the GIF and 12-frame contact sheet confirms continuous radial rotation, movement of the bearing tick, a stable layout, and a recognizable `Signal Compass` wordmark and tagline. This verifies the real chain “output from another skill → browser-accurate animated GIF → HD one-bit GIF.”

The first palette command exposed an ffmpeg constraint when `max_colors=2` retained a transparent slot. The encoder now sets `reserve_transparent=0` because every animated frame is intentionally flattened to an opaque background; the two-color regression path covers that fix.

## Direct animated SVG extension

The animated entry point now detects SVG by content and captures declarative CSS and SMIL motion itself. It requires `--duration-seconds` for SVG so the caller, rather than a heuristic, defines the intended capture window. Chromium loads only the source file and embedded `data:`/`blob:` resources, keeps authored JavaScript disabled, blocks remote and local sidecar requests, fixes every SMIL and Web Animations timeline at `frame_index / fps`, and screenshots the SVG at the final output dimensions. Those captured frames enter the existing stable dithering and whole-animation palette path without an intermediate GIF or a companion skill.

The independent GIF validator now requires actual motion by default: it hashes every composited RGB frame and requires at least two visually distinct frames. It also accepts source-kind and source-format expectations from the conversion manifest. This prevents a technically multi-frame but visually static GIF from passing the animation contract.

The prior five-bar SMIL chart was converted directly from `release-throughput-bars.animated.svg` with one skill command. The accepted artifact `release-throughput-bars-one-bit-direct-hd.gif` is 1280×720, 72 frames, exactly 3.000 seconds, an exact 24 fps by decoded frame timing, infinite looping, and exactly `#000000` plus `#ffffff`. The validator found 49 visually distinct frames, and `ffprobe` independently reported GIF codec, 1280×720, 72 decoded frames, 3.000 seconds, and a 60,771-byte file. Contact-sheet inspection confirmed the staggered bar growth, readable final values, stationary axes and labels, a stable ordered-dither phase, and a clean return to the empty first state.

The regression suite separately exercises CSS-only motion, SMIL motion, mandatory SVG duration, and rejection of an external image request. All eight animated tests pass alongside the 19 existing static tests.

## Isolated forward validation

The required Spark run was attempted first:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-contract.md --mode json --strict --run-id one-bit-dither-svg-contract-20260919 [...expected outputs and JSON fields...]
```

Result: infrastructure-blocked before the first tool call. `gpt-5.3-codex-spark` returned that it is unsupported for this ChatGPT account. The event stream recorded the requested model, zero tokens, zero calls, and no skill mutation. This is not counted as a behavioral failure or pass.

The backlog therefore records `openai-codex/gpt-5.6-luna` as the deliberate model exception. Strict run:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id one-bit-dither-svg-contract-20260919-luna-1 [...13 expected outputs and 7 JSON field checks...]
```

Result: pass in 82.165 seconds.

- All 13 exact artifacts were non-empty: one source SVG, three transformed SVGs, three PNG previews, three conversion reports, and three validation reports.
- All seven JSON field checks passed, including mode identities, exact custom color `#b7410e`, and `ok: true` for every validation report.
- Event, artifact, JSON-field, and unchanged-skill-integrity gates passed.
- The run made 17 tool calls with zero tool errors and valid JSON events.
- The read surface was limited to the prompt, `SKILL.md`, and generated validation/preview artifacts; it did not inspect script source, examples, repository docs, sibling skills, or project artifacts.
- Observed model: `gpt-5.6-luna`; total usage: 54,404 tokens.
- Independent event summary passed with the required model, valid JSON, and zero tool errors.
- Visual inspection of all three isolated previews passed; regional output retained red, yellow, blue, green, black, and white spatial roles.

The quality-profile revision received a separate strict isolated run:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-quality-profiles.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id one-bit-dither-svg-quality-20260919-luna-1 [...14 expected outputs and 11 JSON field checks...]
```

Result: pass in 113.507 seconds.

- All 14 exact artifacts were non-empty: two new source SVGs; detailed original and custom outputs for a six-row fine-line technical panel; a compact regional output for a broad multicolor badge; three previews; three conversion reports; and three validation reports.
- All 11 JSON assertions passed, including `detailed` at 1280 pixels and 2-pixel cells, `compact` at 768 pixels and 5-pixel cells, exact custom color `#284b63`, and all validation `ok` fields.
- Artifact, JSON-field, model/event, unchanged-skill-integrity, and clean-runtime-read-surface gates passed.
- The run made 25 tool calls with zero tool errors and valid JSON events. It read only the prompt, `SKILL.md`, `references/mode-guide.md`, and generated task artifacts.
- Observed model: `gpt-5.6-luna`; total usage: 113,042 tokens.
- Direct preview inspection confirmed that all six row lines, endpoint circles, and row distinctions survived the detailed outputs, while the compact regional badge retained its large source-color zones.

The raster-input revision received a third strict isolated run:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-raster-inputs.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id one-bit-dither-svg-raster-20260919-luna-1 [...18 expected outputs and 15 JSON field checks...]
```

Result: pass in 180.034 seconds.

- All 18 exact artifacts were non-empty: one transparent PNG source, one two-frame GIF source, four transformed SVGs, four previews, four conversion reports, and four validation reports.
- All 15 JSON assertions passed. PNG outputs declared raster/PNG/frame 0 and detailed quality; the animated output declared raster/GIF/frame 1 of 2 and balanced quality; exact custom color `#145da0` and all validation `ok` fields matched.
- Artifact, JSON-field, model/event, unchanged-skill-integrity, and clean-runtime-read-surface gates passed.
- The run made 22 tool calls with zero recorded tool errors and valid JSON events. Its read surface contained only the prompt, `SKILL.md`, `references/mode-guide.md`, and generated task images.
- Observed model: `gpt-5.6-luna`; total usage: 227,741 tokens.
- Visual inspection confirmed that the PNG retained the tower, hill, sun, waves, transparent rounded corners, and label area in all modes. The selected GIF result showed frame one's orange triangle, green stripe, and black square, not frame zero's blue circle.

The animated extension received a fourth strict isolated run:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-animated-gif.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id one-bit-dither-svg-animated-20260919-luna-3 [...5 expected outputs and 7 JSON field checks...]
```

Result: pass in 87.026 seconds.

- All five exact artifacts were non-empty: a 12-frame source GIF, a transformed custom-color GIF, a contact sheet, a conversion manifest, and an independent validation report.
- All seven JSON assertions passed: custom mode, detailed quality, 1280×720, 10 fps, a two-color encoding limit, and validator `ok: true`.
- Artifact, JSON-field, model/event, unchanged-skill-integrity, and clean-runtime-read-surface gates passed.
- The run made nine tool calls with zero tool errors and valid JSON events. It read only the prompt, `SKILL.md`, `references/animation-guide.md`, and the generated contact sheet and GIF.
- Observed model: `gpt-5.6-luna`; total usage: 54,745 tokens.
- Direct visual inspection confirmed a large circle moving through 12 distinct positions while the lighthouse and three wave lines remained stable and recognizable. The validator confirmed exactly `#283845` and `#ffffff`, positive timing, infinite looping, approximate 10 fps, and manifest agreement.

Runs `one-bit-dither-svg-animated-20260919-luna-1` and `-2` produced all required artifacts and passed content assertions but failed the strict event gate because optional evaluator-authored inspection commands first used an undeclared ambient Pillow install, read absolute temporary paths, or applied an invalid global ink-color centroid assertion to a dithered background. No product conversion or validator failed. The final prompt now requires the declared Pillow environment, workspace-relative review artifacts, direct visual motion review, and palette verification through the shipped validator; run `-3` passed cleanly.

The direct animated-SVG revision received a fifth strict isolated run:

```powershell
uv run --script scripts/run-pi-skill-eval.py one-bit-dither-svg --prompt-file evaluations/pi-prompts/one-bit-dither-svg-animated-svg.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id one-bit-dither-svg-animated-svg-20260919-luna-2 [...5 expected outputs and 11 JSON field checks...]
```

Result: pass in 138.011 seconds.

- All five exact artifacts were non-empty: a newly authored declarative animated SVG, its direct custom-color GIF, a contact sheet, a conversion manifest, and an independent validation report.
- All 11 JSON assertions passed. The manifest declared SVG source kind/format, custom mode, detailed quality, 1280×720, 24 frames, and `browser-timeline`; the validator declared `ok: true`, 24 frames, and exactly two colors.
- The validator measured 22 visually distinct frames out of 24, an exact two-second duration, exact 12 fps by decoded timing, infinite looping, and only `#1b4d3e` plus `#ffffff`.
- Artifact, JSON-field, model/event, unchanged-skill-integrity, and clean-runtime-read-surface gates all passed. The run made 11 tool calls with zero errors and valid JSON events.
- Runtime reads were limited to the prompt, `SKILL.md`, `references/animation-guide.md`, `references/mode-guide.md`, and the generated GIF/contact sheet. The skill payload digest was unchanged.
- Observed model: `gpt-5.6-luna`; total usage: 103,350 tokens.
- Direct contact-sheet inspection confirmed staggered growth across all five labeled bars, readable title/value structure, and a return toward the first state.

Run `one-bit-dither-svg-animated-svg-20260919-luna-1` also completed the task and passed the shipped validator, artifact gate, event gate, and skill-integrity gate. Its harness result was invalid only because the evaluator requested an exact `distinctFrameCount=10` even though the prompt correctly required a minimum of 10; the valid output contained 20. Run `-2` removed that erroneous equality assertion while retaining the validator's minimum-motion contract and passed.

## Repository gates

The following passed after the implementation:

```powershell
uv run --with PyYAML python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/one-bit-dither-svg
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

Pattern validation reported 1,222 canonical item IDs and no IDs above the review threshold. The repository validator, independence tests, and payload check passed.

The canonical bundle was synchronized into `.agents/skills/one-bit-dither-svg/`; a subsequent `scripts/sync-local-skills.py --check` reported that all 9,975 canonical source files in the local installation were in sync. Generated Python bytecode caches were removed from the canonical bundle before handoff.

## Release decision

Mark `one-bit-dither-svg` done. The quick skill validator, pattern-ID validator, repository validator, skill-independence suite, payload check, 27 deterministic tests, real HD delivery checks, and strict isolated direct-SVG run all pass. The static path does not preserve source paths, raster editability, text editability, animation, or interaction and may select one animated/multipage frame. The animated path directly preserves declarative CSS/SMIL SVG motion or multi-frame raster motion as a newly rendered GIF, but still flattens editability, interaction, transparency, and vector structure. Inputs may be local self-contained SVGs or local rasters decoded by Pillow; animated output requires ffmpeg. JavaScript-driven SVG, HTML canvas, video, remote URLs, and interactive state still require a separate trusted capture step. These boundaries are explicit in `SKILL.md`, the mode guide, and the animation guide.
