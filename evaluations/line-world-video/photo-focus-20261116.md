# Photographic focus validation, November 16, 2026

## Scope and implementation

Release 0.24.1 adds original-color restoration for secondary component
photographs only while semantically focused. It preserves the reviewed neutral
image and overlays its aligned prepared original with a parent-clock crossfade.
The default 0.35-second fade is inside each focus boundary. Adjacent/overlapping
windows merge, short windows clamp, and image readiness rejects missing or
misaligned originals. Source URLs, crop, fit, image bounds and original bytes
are preserved. No colorization or reconstruction from gray pixels is involved.
Original paper figures, data encodings and evidence-bearing color retain their
established treatment. Existing approved voice tracks are unaffected.

`photo_focus.py plan` verifies prepared digests, neutral channels and equal
image dimensions before deriving relative paths. `inspect` checks actual paired
URLs, target pixels, original color at focus, neutral endpoints, intermediate
fades, fixed bounds and backward/repeated seeking. It can render a capped silent
preview without another image/model call. Declarations do not independently
prove photographic identity, speech alignment or omitted focus windows.

## Deterministic and visual checks

```text
uv run --script skills/line-world-video/scripts/test_photo_focus.py
uv run --script skills/line-world-video/scripts/test_focus_motion.py
uv run --script projects/line-world-video/scripts/make_photo_focus_demo.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

Fourteen focused tests pass: original/neutral actual pixels, smooth intermediate
pixels, stable geometry/source identity, reverse/repeated seek, short/touching
windows, invalid intervals and duplicate binding, cleanup, readiness mismatch,
paired-source hashes and neutrality, plan merging, actual encoded preview and
rejection of a stuck full-color layer and an external/browser plan mismatch. The ten existing long-focus motion tests
pass, including a fresh linked starter. Scoped source validation passes.

The demonstration reuses the previously reviewed CPU and exact 3 GB GTX 580
photographs and their cached preparations. It retains original files, rights,
source pages and scope in the project-owned media records. CPU: neutral then
color at 0.6--3.5 seconds; GPU: color at 4.1--7.5 seconds; both neutral afterward.
The CPU is illustrative of its system role; this is not a claim about the exact
historical host. The GTX photograph identifies the model/memory variant, not a
claim that this specimen was used by the AlexNet authors. No new source search
or image-generation step was required. Encoded CPU-color, GPU-color and neutral
return frames were inspected for fixed placement, clear labels and guide ports.
The preview is silent, 1920 by 1080, 30 fps, 270 frames, nine seconds.

## Isolated forward validation

Keep the established model exception `openai-codex/gpt-6.1-sol`, medium thinking,
because Spark is unavailable. The forward tasks use only the runtime payload,
a locally created synthetic RGB/grayscale fixture and normal local tools. That
fixture tests integration and rendering, not documentary source selection.
Require exact `scene.html`, `photo-focus.json`, `photo-review.json`, `poster.png`,
`preview.mp4` and `review.md`, strict JSON, zero tool errors, unchanged skill and
an `ok: true` actual-pixel report. Inspect generated posters and encoded frames.

The contract prompt is `evaluations/pi-prompts/line-world-photo-focus-contract.md`;
the naturalistic prompt is `evaluations/pi-prompts/line-world-photo-focus-natural.md`.
Use `scripts/run-pi-skill-eval.py line-world-video --prompt-file <prompt>
--model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict
--run-id 20261116-photo-focus-<case>-sol`, repeat `--expect-output` for each named
artifact and require `--expect-output-json-field photo-review.json::ok=true`.
The contract also requires its exact final command. All three fresh
naturalistic repetitions pass strict gates with actual-pixel reports. Every
video independently passes FFprobe (six seconds, 144 frames, 1080p24, silent)
and full FFmpeg decode; neutral/color encoded frames were inspected. Traces
read the entry point, relevant compact references, occasional runtime/helper
source and project-owned review images, without galleries or sibling resources.
The initial contract artifacts and runtime checks pass, but its strict event
gate fails `no-fenced-command-in-prompt`: the prompt used a `text` fence that
the harness exact-shell recognizer does not accept. Classify this as a harness
fixture-format failure, retain the run and repeat with a `bash` fence. No runtime
or acceptance threshold changed. The corrected-fence contract executes the required command and passes actual
artifacts, but two genuine agent tool errors remain: an unnecessary Python 3.11
fixture invocation and an extra embedded-JSON check that splits a data URI at
its semicolon. Retain that strict failure as agent/recovery, not a runtime bug.
The final contract supplies tiny original/grayscale PNG bytes directly, making
the utility smoke about integration rather than fixture image authoring. Its
strict repeat uses the same frozen runtime; naturalistic repetitions continue
to create their own inputs and remain 3/3. The supplied-input 0.24.0 contract again completes correct artifacts but fails
strictly on an extra ad hoc HTML/data-URI JSON split. Retain this third failed
attempt. Version 0.24.1 adds automatic external/browser plan correspondence
inside the inspector and documents why text splitting is unreliable. This
addresses the observed repeated-work pattern rather than relaxing a gate.

The frozen 0.24.1 exact-command contract passes every strict gate. Its final
three fresh naturalistic repetitions pass actual source/pixel and encoded
artifact checks 3/3 but strict workflow gates only 1/3. Natural-1 adds an overly
strict custom RGB assertion to lossy H.264 output; natural-3 reuses a visual
review record after changing movie/source bytes. These are retained agent/check
and recovery failures. Do not promote the final naturalistic cohort or quote
the earlier 3/3 candidate as final qualification. The main skill remains
validating, including this incomplete workflow/generality gate.

| Run ID suffix (prefix `20261116-photo-focus-`) | Strict result | Final artifacts |
| --- | --- | --- |
| `contract-sol` | Fail: unsupported prompt fence in exact-command harness | Pass |
| `contract-fence-sol` | Fail: agent fixture/JSON recovery tools | Pass |
| `contract-inputs-sol` | Fail: extra HTML/data-URI split | Pass |
| `natural-1-sol`, `natural-2-sol`, `natural-3-sol` | Candidate 3/3 pass | Pass |
| `final-contract-sol` | Pass | Pass |
| `final-natural-1-sol` | Fail: extra lossy-codec RGB assertion | Pass |
| `final-natural-2-sol` | Pass | Pass |
| `final-natural-3-sol` | Fail: stale visual review record | Pass |

All final outputs were independently rerun against the canonical photo inspector,
including external/browser plan matching; all pass. Every final actual MP4
has 144 frames, six seconds, 1080p24, no audio and a full decode pass. Encoded
neutral/color frames were inspected. Trace summaries retain all tool failures;
there are no gallery, sibling or unrelated repository reads. The new utility
and runtime are usable, while arbitrary end-to-end agent execution remains
qualified only to the documented validating status.
The main skill remains validating for its previously recorded broader limits.

## Package and repository boundaries

The portable and marketplace archives contain all six native skills and 340
manifest-declared files. The shared runtime also ships in the four specialized
producer copies. Actual ZIP extraction, task-local Codex installation, all six native skill
registrations and all 21 installed suites (242 tests) pass. Both archives match
and required-runtime removal is rejected. Verify Linux CI before claiming
publication complete.
The primary runtime has 148 files; the unchanged Google Vids adapter has 22.
The root global validator/sync retains four unrelated semantic reference-route
findings; preserve that unrelated work and use the selected clean publication
worktree for full release validation. Scoped local refresh succeeds. Generated
media, screenshots, raw forward runs and CI receipts remain ignored artifacts.
The native Google Vids upload restriction and pending earlier native revisions
are unchanged; this preview is a local visual demonstration.

Local marketplace SHA-256: `83504150127cbc9bebc343bc77743e543e1503407d54b3257151f9a5b76f8fb2`.
Demo SHA-256: `ceb028c23851109fecea4ecbfe10b83d658c47e058544bc985d524ee904682b5`.
