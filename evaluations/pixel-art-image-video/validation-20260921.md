# Pixel-art image/video skill validation — 2026-09-21

## Scope and implementation

Created `skills/pixel-art-image-video/` as a self-contained skill for local raster/SVG stills and local video or animated-raster motion. It is deliberately separate from `one-bit-dither-svg`: its defining mechanism is a low-resolution color grid enlarged with nearest-neighbor sampling, not one-bit engraving. The command routes `.png`/`.webp` to still conversion and `.mp4`/`.gif` to motion conversion. It offers chunky, balanced, detailed, and manual pixel-density profiles; stable adaptive, forest4, sunset8, and custom palettes; none, Bayer4, and Floyd–Steinberg logical-grid dither; hard static alpha; timeline selection; MP4 audio preservation; contact sheets; JSON manifests; and an independent output validator.

Static SVG is rendered in Chromium with authored JavaScript disabled and external/local sidecar resource requests blocked. Raster stills honor EXIF orientation. Motion is decoded with ffmpeg at the logical grid, then one adaptive palette is fitted from uniformly spaced frames and reused across the clip. GIF output retains exact palette colors and block pixels. MP4 uses H.264/YUV 4:2:0 and AAC audio for broad playback compatibility; its lossy decoded colors are not asserted to equal the source palette exactly.

## Deterministic tests and real media review

```powershell
uv run --script skills/pixel-art-image-video/scripts/test_pixel_art.py
```

Result: 8/8 passed. Coverage includes color parsing/profile defaults, deterministic bounded adaptive quantization, Bayer phase stability, custom-palette rejection, transparent PNG and exact grid validation, lossless WebP validation, direct self-contained SVG rendering, MP4 audio preservation, and exact-palette GIF motion validation.

Real still-image acceptance used the repository's CC0 source `skills/vectorize-art-patterns/assets/base-images/hokusai-great-wave.jpg`, which its manifest attributes to the Art Institute of Chicago Open Access collection. The image was not copied into the new skill bundle. A 1280×878 balanced output uses a 256×176 logical grid and exactly 20 source-fitted colors; a chunky Bayer variant uses 160×110 and exactly 12 colors. Both independent validators passed checksum, provenance, dimensions, palette bound, and reversible nearest-neighbor grid. Visual review found the balanced variant retained the breaking wave, boats, Mount Fuji, and broad warm/cool structure. The chunky variant produced a more deliberate coarse look but lost fine spray and lettering, supporting the guidance to choose by the smallest important feature.

A previously authored 960×540 chart SVG converted directly to a 1280×720 detailed PNG with a 427×240 logical grid; the independent validator found 25 visible colors under the 32-color adaptive budget and an exact grid. Visual review showed that small labels became speckled even at a 3-pixel block, so the skill recommends `--pixel-size 2` or a separately typeset label layer when tiny text is essential.

A real three-second source MP4 with video and synthetic audio produced a 1280×720 sunset8 MP4. The independent validator found 36 frames, 28 visually distinct decoded frames, exactly 12 fps, a three-second duration, and audio present. `ffprobe` independently reported H.264 1280×720 video, 36 frames, 3.000 seconds, plus an AAC stream also lasting 3.000 seconds; file size was 85,158 bytes. The same source produced a 640×360 forest4 GIF with exactly the four declared greens, an exact nearest-neighbor grid, 36 frames, 25 visually distinct frames, a three-second duration, and infinite looping. Contact-sheet review confirmed staggered growth and stable scene colors. Generated media and review output live under ignored `projects/pixel-art-showcase/artifacts/`.

## Isolated forward test

The default Spark model is known to be unsupported for this ChatGPT account from the prior one-bit-dither release. The backlog records `openai-codex/gpt-5.6-luna` as the deliberate exception for this forward gate.

```powershell
uv run --script scripts/run-pi-skill-eval.py pixel-art-image-video --prompt-file evaluations/pi-prompts/pixel-art-image-video-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id pixel-art-image-video-contract-20260921-luna-1 [...9 expected outputs and 10 JSON field assertions...]
```

Result: strict pass in 102.438 seconds.

- All nine exact paths were created: a new SVG, custom-palette PNG, its manifest and validation report, a new audio-bearing MP4 source, an adaptive-palette MP4, contact sheet, video manifest, and video validation report.
- All ten JSON assertions passed. The still is 640×360 with a 3-pixel grid, exactly four requested colors, and an exact nearest-neighbor reconstruction. The motion output is 320×180, 12/12 visually distinct frames, 8 fps, 1.5 seconds, and contains audio.
- The independent evaluator reran the canonical validators after Pi exited; both still and video passed.
- The agent read only the prompt, `SKILL.md`, the two directly relevant references, and its own output images. It did not read examples, sibling skills, repository docs, or script source.
- Model/event, exact-artifact, JSON-field, and unchanged-bundle-integrity gates all passed. Eleven tool calls, zero tool errors, valid JSON events, observed `gpt-5.6-luna`, and 97,730 total tokens.
- Direct visual inspection showed a legible four-color night harbor with moon, lighthouse, boat, title, and block-sharp water; the video contact sheet showed motion across all twelve frames.

Event inspection command:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pixel-art-image-video-contract-20260921-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

## Repository gates and decision

The following passed on 2026-09-21:

```powershell
uv run --with PyYAML python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/pixel-art-image-video
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
```

The pattern validator reported 1,222 canonical IDs and zero over the 48-character review threshold. The Pi harness test suite passed 14/14. The converter and validator scripts were exercised by both deterministic tests and a strict isolated forward run. Local installation synchronization copied seven changed files, and `scripts/sync-local-skills.py --check` confirmed all 9,982 canonical source files matched. Mark the skill `done`. Remaining honest boundaries: animated SVG is not a direct motion source; JavaScript/Canvas/WebGL require a trusted prior capture, GIF cannot retain audio, MP4 cannot promise exact palette colors because H.264 is lossy, and small source text may be intentionally sacrificed by coarse profiles.
