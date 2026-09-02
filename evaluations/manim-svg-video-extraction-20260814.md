# Manim SVG Video Extraction Validation

Date: 2026-08-14

## Scope and ownership

Restored `manim-svg-video` as the standalone owner of SVG discovery, static-companion selection, Manim vector/raster import, SVG-only replacement or mosaic sequencing, generated scene code, MP4 rendering, exact-duration repair, and `composition-manifest.json`.

The complementary `video` skill retains source/storyboard contracts, mixed-media placement, cross-producer ports/events/states, transitions, audio, browser and Slidev capture, encoding, review, and final-program delivery. It now routes standalone SVG/Manim work to `manim-svg-video` and accepts only the resulting MP4 plus manifest when later composition is required.

The extraction moved, rather than copied:

- `scripts/compose_svg_video.py`
- `references/composition-config.md`
- `references/manim-svg-import.md`
- `references/visual-tokens.md`

No Manim implementation script or detailed Manim reference remains in `video`; its remaining mentions are producer-routing boundaries.

## Deterministic validation

- Skill Creator quick validation passed for `manim-svg-video` and `video`.
- `compose_svg_video.py` passed Python compilation.
- A dry run against an ignored local fixture with `pulse.animated.svg` and `pulse.static.svg` discovered one asset, selected the static companion as `render_source`, kept the animated source in the manifest, and reported no conversion error.
- A real Manim Community 0.21.0 smoke render produced H.264/yuv420p at 640×360, 5 fps, and exactly 3.000 seconds. The MP4 is 25,695 bytes with SHA-256 `27cbf3831d439a17b20ff7ac32e3372839bc973125a611a63832aa58c5844299`. A three-state contact sheet was visually inspected and showed visible source geometry and motion.
- `uv run --script skills/video/scripts/test_scene_contracts.py --json` passed 13/13 checks after extraction, including Chromium state, SVG ID namespacing, GIF and HTML master clocks, and a real MP4.
- `uv run --script skills/video/scripts/check_runtime_tools.py --require-render-tools --require-node --json` passed with no missing bundle files.
- `uv run --script scripts/validate-pattern-ids.py`, `uv run --script scripts/validate-skills.py`, `uv run --script scripts/test-skill-independence.py`, and `uv run --script scripts/check-repo-payload.py` passed.
- `uv run --script scripts/sync-local-skills.py` synchronized the canonical sources, and the follow-up `--check` passed across 2,983 source files.

Concurrent worktree note: one finalization rerun briefly found two out-of-scope missing local-resource links in D3 references while those files were changing elsewhere. No D3 file was modified here; the subsequent full `validate-skills.py` rerun passed, as did targeted quick validation, independence, payload, pattern-ID, diff, and per-skill sync checks for `manim-svg-video` and `video`.

## Isolated Spark validation

Both release cases used `openai-codex/gpt-5.3-codex-spark`, high thinking, the runtime payload profile, strict JSON mode, exact output checks, exact command enforcement, model/event checks, zero tolerated tool errors, clean read-surface enforcement, JSON field assertions, and immutable skill snapshots.

### `manim-svg-video`

Prompt: `evaluations/pi-prompts/manim-svg-video-runtime.md`

- `manim-svg-video-extraction-20260814-spark-1`: produced both exact artifacts and passed all JSON fields and skill integrity. The event gate rejected the prompt's `powershell` fence because the harness accepts `bash`, `sh`, or `shell`; classify this as an evaluation-fixture failure. The prompt fence was corrected without changing skill behavior.
- `manim-svg-video-extraction-20260814-spark-2`: passed every gate in 13.312 seconds with five successful tool calls and no invalid events. It created `outputs/svg-video/composition-manifest.json` and `outputs/svg-video/manim_svg_video_scene.py`; asserted asset count 1, duration 4, layout `replace`, and active slots 1. The skill payload remained unchanged at SHA-256 `c85ac8f3955565ad4fce6d5fdc8d4fde1b403010ceb70ed7b3301122976d0335`. The read surface contained only the prompt and the two generated outputs; no repository docs, sibling skills, examples, or script source were read.

### `video`

- `video-svg-boundary-20260814-spark-1`: passed every gate in 29.594 seconds after the Manim resources were removed. It produced the exact mixed-media scene contract and validation report, passed seven asserted fields, used only focused in-bundle references and the scene template, and preserved the skill payload at SHA-256 `3f4f46196aa6bfe302c3a158dc601085f5749c2af195a9fe2c0d214c007e39bc`.

## Decision

Mark both `manim-svg-video` and `video` as `done`. Their trigger and runtime boundaries are complementary, the Manim implementation has one owner, both bundles are independently usable, and local plus isolated regressions pass.
