# Gentle asset motion and divider removal

Date: 2026-11-17. Skill: `line-world-video`. Plugin: `0.27.0`.

## Change and acceptance boundary

Use whitespace and alignment instead of decorative center rules, column
borders or panel frames. Preserve semantic connectors, actual axes, table
rules and original source-document ink. Both bundled starter layouts and
the four copied producer profiles follow this direction.

The standalone `gentle-motion.js` runtime provides pure parent-clock floating
and a single image-detail entry/hold/return. Float complete logo/label or
connected concept groups; never distort individual data points. Keep the
original image inside a fixed clipped viewport. The shared scene-effects
bridge invalidates cached holds when its actual motion transform changes.
Reserve the whole motion envelope and keep the guide adjacent to the
displayed object. The reduced-motion setting returns the static view.

The numeric defaults are editorial choices, not a medical or accessibility
certification. The compact runtime reference cites primary W3C and WebKit
guidance without attributing these numbers to those sources.

## Deterministic checks

```powershell
uv run --script skills/line-world-video/scripts/test_gentle_motion.py
uv run --script skills/line-world-video/scripts/test_scene_effects.py
```

Both pass: twelve actual-browser gentle-motion tests and six scene-effects
tests. They verify visible pixels and bounds, group-relative geometry,
stable ID phases, preserved source images and fixed captions, no empty
detail viewport, hold/return timing, reduced-motion identity, repeat seeking,
scene-local offsets, cache changes and restoration on destruction. The project
inspector has positive/negative fixtures for a fixed caption and empty image
edges. It measures a nested SVG's declared viewport through its screen matrix;
its painted-content bounds would incorrectly follow the moving image. Four
existing atlas-reading tests also pass. Both real starter layouts initialize
without the retired decorative separator.

Use `inspect_gentle_motion.py` with explicit group, image, viewport and caption
selectors to reuse browser verification. Numeric geometry uses a 0.02 CSS-pixel
rounding allowance; screenshots and repeated seeks still compare actual bytes.

## Isolated forward cases

The two prompts are
[`line-world-gentle-motion-contract.md`](../pi-prompts/line-world-gentle-motion-contract.md)
and [`line-world-gentle-motion-naturalistic.md`](../pi-prompts/line-world-gentle-motion-naturalistic.md).
Use the established `openai-codex/gpt-6.1-sol` medium-thinking exception;
Spark is unavailable in this environment. Copy only the runtime payload,
disable ambient context and load only the copied skill. Require exact paths
`artifacts/scene.html`, `artifacts/reading.png` and `artifacts/quality.json`.
Both final release cases pass all strict gates, with zero tool errors, exact
outputs and unchanged runtime payloads (162 files, digest
`891195c76e31f6d685400cc24350654b32ef06cb5fbf372c20bcd3562866fc72`).
Run IDs are `20261117-line-world-0270-contract-release` and
`20261117-line-world-0270-natural-release`. Both use the bundled inspector.
Their actual screenshots were inspected: symbols, labels and source images
are readable, with no center rule, cropped caption or blank image viewport.

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-gentle-motion-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261117-line-world-0270-contract-release --expect-output artifacts/scene.html --expect-output artifacts/reading.png --expect-output artifacts/quality.json
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-gentle-motion-naturalistic.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261117-line-world-0270-natural-release --expect-output artifacts/scene.html --expect-output artifacts/reading.png --expect-output artifacts/quality.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261117-line-world-0270-contract-release/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261117-line-world-0270-natural-release/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

The read surface includes only the prompt, skill instructions, relevant small
references/runtime/helper files and task-owned artifacts. No acceptance gallery,
repository project, parent or sibling skill was read. Original development
results are retained: the first contract and two naturalistic attempts failed
strict mode because their authored checkers used HTML-only `inner_text()` on
SVG, exact floating bounds, or the center of a deliberately cropped color mask.
Their recovered outputs do not erase those tool errors. A passing intermediate
contract is candidate evidence only. The reusable inspector removes those
repeated driver assumptions; the two final cases match the released bytes.

## Movie and delivery scope

Revised `projects/sixties-archival-video/` with no central rule, whole-group
floating and one slow television-detail cycle. All 14 archive clips and the
3,735-frame / 124.5-second budget remain intact. Demuxed approved AAC bytes
match the prior movie exactly (SHA-256
`ab9bc0bf46f2ea526192c676132863862c0e160601be2d2cd0cdfb956e40492a`).
The new movie is `81943aa6a08990dae916a1c600f82a8534930f6bb4d24f86e0cd687373ef60c4`.
Encoded review passes for all 3,735 frames, with zero insufficient-content
frames and frozen operator observations for all six scenes. The actual two
reading views per scene, all five joins at 20/50/80%, and television's four
camera states were inspected. Native Chrome playback passes for all six scenes,
with six exact source-preview seeks, HTTP 206 delivery and no browser errors.

The television enters over four seconds, holds for three and returns over four.
Independent encoded/source structural comparisons have mean RGB differences
of 0.72–1.09 channel levels, versus about 39.3 if the zoom were absent during
the hold. All five floated concept groups change position. Source geometry
covers all 3,735 guide states and 24 speech-linked targets. Authored red, gray
and white color checks and audio level/silence checks pass. This is not a new
listening or ASR pass. Cloud replacement was read back with the matching byte
count and a new complete authenticated raw-file reference before delivery.
Private cloud identifiers and
bearer download URLs stay out of versioned source.

Other historical movies are not claimed as newly rendered by this revision.
The broader main-skill validation and pending native Google Vids upload limits
remain explicit. Local MP4 delivery is not native Vids or HyperFrames export.

## Packaging and publication

The package includes all six skills and 374 files. Both producer copies and
the main skill carry the motion runtime, compact reference, browser inspector
and tests. Repeated packaging now uses a fresh contained smoke workspace rather
than colliding with a previous draft. The two unpublished development builds
remain archived locally; they were never uploaded as public release payloads.
The shared marketplace publisher and unrelated in-progress skills are preserved.

The actual final archives pass portable/native schema, canonical source parity,
task-local native installation and discovery of all six enabled skills. All
24 installed utility suites pass, totaling 275 tests; the two new suites are
included in the installed run. The portable ZIP SHA-256 is
`01b81a735e0f7f350ad29e1a6652ca8ff417bc71e1f15a0e7baeb9e02b8a6e88`;
the marketplace ZIP is
`1e2397b5ead1c7da8ad4d0902372f125e0dd8a2a961a86053995a15b7681d3f3`.
Workspace synchronization verifies 162 main-skill files and 22 unchanged Vids
adapter files. Workspace catalog registration preserves every other entry;
it does not change global host settings or permissions.

The clean publication worktree passes `validate-pattern-ids.py`,
`validate-skills.py`, `test-skill-independence.py` and `check-repo-payload.py`.
The working root retains unrelated concurrent skill-authoring findings; none
is imported into this scoped release. The publication manifest contains only
Line World sources/evidence and the sixties project sources, with generated
media, private receipts, dependency trees and credentials excluded.
