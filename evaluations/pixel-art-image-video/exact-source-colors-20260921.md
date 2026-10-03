# Exact source-color pixel art validation — 2026-09-21

## Change and contract

Added `--palette preserve` to `pixel-art-image-video`. It selects decoded source RGB pixels with nearest-neighbor sampling at the logical grid, skips palette fitting/quantization, contrast, saturation, and dithering, then enlarges that grid with nearest-neighbor sampling. It permits lossless PNG/WebP stills and FFV1-in-MKV motion with RGB-family `bgr0` pixels. MKV retains decoded source audio as FLAC by default. It rejects MP4/GIF, alpha flattening, dither, non-neutral contrast/saturation, and `--colors` in this mode because they would break the exact-color promise. The promise covers selected source RGB pixels, not every original pixel or pre-codec video colors. Transparent pixels have no visible RGB contract; hard alpha thresholding remains part of the pixel-art transformation.

The manifest records a source SHA-256, `render.paletteMode=preserve`, `render.sourceColorsExact=true`, and null palette fields. The validator checks the source hash, every visible PNG/WebP pixel against the corresponding nearest-neighbor source sample, and every decoded FFV1 frame against an independently re-extracted source RGB frame enlarged to full output size. Existing palette modes remain compatible with the previous manifest schema.

## Deterministic and real-image checks

```powershell
uv run --script skills/pixel-art-image-video/scripts/test_pixel_art.py
```

Result: 13/13 passed. New cases cover more than 64 distinct original RGB colors in PNG and lossless WebP, hard-alpha raster and browser-rendered SVG sources, rejected color-changing/lossy options, MKV/FFV1 round-trip with audio, and a negative case that alters an output RGB block and updates its checksum: the validator still rejects it.

The repository's CC0 `van-gogh-bedroom.jpg` source produced `projects/pixel-art-color-demo/artifacts/images/bedroom-exact.png` at 900 × 705, with a 225 × 177 logical grid and 4-pixel nominal blocks. Its manifest and exact-source-color validator passed. Direct visual inspection found the recognizable room and source hue relationships preserved while fine brushwork became pixel clusters. The artifact remains ignored local project output, not a published fixture.

## Isolated skill-only forward test

The recorded model exception remains `openai-codex/gpt-5.6-luna` because the account previously rejected the default Spark model before its first tool call. The runtime payload contained only this skill, not acceptance fixtures or sibling skills.

The first strict attempt, `pixel-art-preserve-colors-20260921-luna-1`, created all nine exact outputs and passed all six JSON assertions, skill integrity, and the independent still/video validators. It failed the strict event gate because the agent made one unsuccessful preparatory probe importing Pillow with bare Python, outside the `uv` environment. This is retained as a tool-error failure, not relabeled as a strict pass. The prompt was then clarified to use `uv` for Python dependencies or ffmpeg for source generation; the skill payload was unchanged.

```powershell
uv run --script scripts/run-pi-skill-eval.py pixel-art-image-video --prompt-file evaluations/pi-prompts/pixel-art-preserve-colors.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id pixel-art-preserve-colors-20260921-luna-2 --expect-output source.png --expect-output exact.png --expect-output exact.json --expect-output exact-validation.json --expect-output source.mp4 --expect-output exact.mkv --expect-output exact-video.json --expect-output exact-contact.png --expect-output exact-video-validation.json --expect-output-json-field exact.json::render.paletteMode=preserve --expect-output-json-field exact.json::render.sourceColorsExact=true --expect-output-json-field exact-validation.json::ok=true --expect-output-json-field exact-video.json::render.paletteMode=preserve --expect-output-json-field exact-video.json::render.sourceColorsExact=true --expect-output-json-field exact-video-validation.json::ok=true
```

Result: strict pass in 168.059 seconds. All nine exact paths and six JSON assertions passed; 17 tool calls produced zero errors and valid JSON events; the observed model was `gpt-5.6-luna`; and the skill payload digest remained `9b880b238413438961244238b386798af0ca502954293c50f7bf8eff02884b27` before/after. The read surface contained `SKILL.md`, the two relevant references, and the agent's own source/results; it excluded examples, sibling skills, and repository context. Trace inspection passed:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pixel-art-preserve-colors-20260921-luna-2/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Independent post-run review found 3,227 distinct RGB colors in the 320 × 192 synthetic source and 500 unchanged selected RGB colors in the 160 × 96 output. A separate Pillow nearest-neighbor reconstruction matched the entire still byte-for-byte. The canonical validators rerun from the evaluator side passed both artifacts. `ffprobe` found eight FFV1/`bgr0` frames and FLAC audio; the validator found eight visually distinct frames, exactly 8 fps, one second, an exact enlarged RGB grid, and source-color equality in every frame. The still and contact sheet were directly inspected.

## Repository gates

The following passed: skill-creator quick validation, `scripts/validate-pattern-ids.py` (1,222 IDs), `scripts/validate-skills.py`, `scripts/test-skill-independence.py`, `scripts/check-repo-payload.py`, and `git diff --check`. Targeted local synchronization copied six changed files and `--check` matched all seven canonical files. No published example source or Pages catalog changed.
