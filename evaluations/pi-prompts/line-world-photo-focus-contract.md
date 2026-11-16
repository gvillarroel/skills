Make a six-second silent browser-clock photographic treatment test using the
copied read-only `skills/line-world-video` skill. Decode the supplied RGB and
grayscale PNGs below into project-owned files with Python base64/stdlib. This is a
synthetic rendering fixture, not a sourced photograph or documentary claim.
Show it in an inline SVG, with a red guide beside it. Keep geometry and crop
fixed. Restore the original test pattern colors only while focused from 1 to
4 seconds, with a smooth 0.35-second transition inside each boundary. Outside
the interval show the grayscale image. Preserve seeking in either direction.

Use the bundled photo-focus runtime and its focused reference. Keep generated
dependencies beside the HTML, the skill read-only, and all work inside this
workspace. Do not use network image acquisition, accounts, other skills or
acceptance galleries. Keep the plan editable in `photo-focus.json` and embed
the same bindings in the HTML. Await image readiness and inspect the poster
and at least one frame extracted from the actual MP4.

Run this exact final verification/export command after authoring:

```bash
uv run --script skills/line-world-video/scripts/photo_focus.py inspect --html scene.html --plan photo-focus.json --output photo-review.json --screenshot poster.png --video preview.mp4 --duration 6 --fps 24
```

Required exact outputs: `scene.html`, `photo-focus.json`, `photo-review.json`,
`poster.png`, `preview.mp4`, `review.md`. In the review record the intended focus,
actual source/encoded checks, input's synthetic nature and remaining limits.

Supplied synthetic fixture bytes (base64 PNG):

Original: `iVBORw0KGgoAAAANSUhEUgAAACAAAAAQCAIAAAD4YuoOAAAALUlEQVR4nGMU6bnEQAo4e9mHJPVMDDQGTKMWEAKjQUQQjAYRQTAaRATB0A8iAG7jA376/x+XAAAAAElFTkSuQmCC`

Grayscale: `iVBORw0KGgoAAAANSUhEUgAAACAAAAAQCAIAAAD4YuoOAAAALUlEQVR4nGMsKChgIAXw8fGRpJ6JgcaAadQCQmA0iAiC0SAiCEaDiCAY+kEEAFBjAZrQnU95AAAAAElFTkSuQmCC`
