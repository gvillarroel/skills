# Animated SVG to GIF evaluation — 2026-09-02

## Outcome

PASS. A real conversion exposed and then verified a fix for the single-output
manifest location. When `-o <path>` is used, `conversion-manifest.json` now stays
beside the named GIF instead of being written to the default project directory.

The focused regression suite passed 2/2:

```powershell
python skills/animated-svg-to-gif/scripts/test_convert_animated_svg_to_gif.py
```

A direct browser/ffmpeg conversion of the bundled pulse template produced a
320×180, 1.5-second GIF with 18/18 distinct decoded frames. `ffprobe`, Pillow,
and direct visual inspection passed. The obsolete default-directory manifest
created by the pre-fix run was removed after the corrected adjacent manifest was
verified.

## Isolated runtime validation

- Run: `20260902-animated-svg-to-gif-runtime-spark-1`
- Model: `openai-codex/gpt-5.3-codex-spark`
- Mode: JSON strict
- Runtime payload: 5 files, SHA-256
  `e994a4bb177b1dc198629ad14b722cf2b45d9d16498c929c265adea3f0331403`
- Required outputs: `pulse.animated.svg`, `pulse.gif`,
  `pulse.manifest.json`, and `conversion-manifest.json`
- Result: PASS; exact outputs, model, valid events, zero tool errors, clean read
  surface, and unchanged payload

Command:

```powershell
uv run --script scripts/run-pi-skill-eval.py animated-svg-to-gif --prompt-file evaluations/pi-prompts/animated-svg-to-gif-runtime.md --mode json --strict --run-id 20260902-animated-svg-to-gif-runtime-spark-1 --expect-output pulse.animated.svg --expect-output pulse.gif --expect-output pulse.manifest.json --expect-output conversion-manifest.json
```

Independent inspection confirmed 24 frames, 23 distinct decoded frame hashes,
360×240 output, 2,000 ms total duration, 12 fps in the manifest, a white
background, a readable `Pulse` label, and a visible animated circle. Both
manifests identify `pulse.gif`, and the item manifest records the requested
360 CSS/output width, 2-second duration, and 24-frame count.

The durable trace summary is
`evaluations/animated-svg-to-gif-20260902-read-surface.json`.

## Failure classification

The initial direct smoke wrote its run manifest to the default output directory
despite an explicit `-o` path. Classification: `skill`. The owning script and a
two-case output-directory regression test were updated before the passing strict
run. The isolated release run had no failures.
