# Motion during long chart and diagram focus

Date: November 16, 2026. Release: Line World 0.23.1.

## Behavior and scope

For a chart or diagram kept in focus for more than two seconds, program calm,
meaningful motion through that focus interval. The guide moving nearby does not
satisfy the rule. Exactly two seconds or less is exempt. Preserve fixed data,
labels and camera stability; traces emphasize actual relations rather than
introducing new measurements. Existing appropriate native motion can supply
the effect. Original-paper/photo pixels remain unchanged.

The primary instructions and all four dedicated producer contracts now route
this behavior. The self-contained `focus-motion.js` supplies parent-clock
`trace` and `pulse` overlays, a default 3.2-second cycle, a minimum 2.4-second
period, gentle entry/exit, focus exit and deterministic repeated seeking.
Inactive windows avoid geometry/style reads. Source coordinates and values
remain unchanged. Bind separate continuous edges or use pulse for multipart
geometry: SVG dash patterns restart at each subpath and can otherwise leave
unintended static gaps. The runtime rejects that misleading trace construction.

The linked starter now derives diagram, comparison and history motion windows
from its existing beat durations. The atlas derives entity/pane windows from
its existing clock and activates the effect only when a slot is long enough.
Both expose project-owned `FOCUS_PLAN` and include active motion in their pure
snapshot. The runtime is packaged with every dedicated producer. No approved
speech, scene duration or editor account is changed by this visual layer.

## Target-pixel inspection

`inspect_focus_motion.py` samples five actual browser images inside each
eligible declared focus window. It hides known/marked guides only for motion
proof, checks changed pixels inside the actual target, verifies fixed-data
geometry and reading labels, then checks backward/repeated seeks. The guide
is restored in the poster and optional silent preview.

This bounded test requires an inventory of focus windows; it cannot infer
omitted narrated focus or certify arbitrary simulation semantics. Its stability
gate applies to fixed-data emphasis. Keep actual changing-data simulations in
their own truthful state/units and corresponding review. Sampled motion proof,
source layout checks, encoded frames and measured speech are separate evidence.

```text
uv run --script skills/line-world-video/scripts/inspect_focus_motion.py --html film/scene.html --output film/motion-review.json --screenshot film/poster.png --video film/preview.mp4 --duration 9
```

## Deterministic and package checks

All ten new real-browser tests pass: threshold boundary, actual moving pixels
with unchanged data, repeated/backward seek and focus exit, pulse, period and
ID rejection, disconnected-edge handling, actual MP4 preview, guide-only
negative case, changed geometry/labels and default-starter integration.
An initial test-harness diagnostic nested two Playwright synchronous contexts;
the final tests run the inspector in its own process, matching normal use.

```text
uv run --script skills/line-world-video/scripts/test_focus_motion.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

The actual six-skill package has 332 declared files, 144 primary runtime files
and 22 unchanged native-adapter files. Actual task-local Codex installation,
six-skill discovery, canonical runtime parity and all 20 installed suites /
228 tests pass. The local marketplace archive SHA-256 is
`c6c248a3fcd46cec6c2e043e83955183cf536342a2334a62de0b51219b1da284`.

## Standalone forwards

Use the recorded model exception `openai-codex/gpt-6.1-sol`, medium thinking,
because Spark is unavailable. All runs use a fresh read-only runtime bundle,
strict JSON, exact paths, observed-model/tool-error checks and payload integrity.
Prompts are `line-world-focus-motion-contract.md` and
`line-world-focus-motion-natural.md` under `evaluations/pi-prompts/`.

| Run suffix after `20261116-focus-motion-` | Outcome |
| --- | --- |
| `contract-sol` | Initial strict pass. |
| `natural-1-sol`, `natural-2-sol`, `natural-3-sol` | Initial 3/3 strict passes before the multipart-path guard. Retain as development evidence. |
| `final-contract-sol` | Exact 0.23.0 candidate-payload strict pass. |
| `final-natural-1-sol` | Strict pass; actual fixed curve and input/model connections animate, with stable labels and encoded reading views. |
| `final-natural-2-sol` | Retained strict failure: an initial layout/focus check failed; later manual-review data used stale movie/source hashes. The agent corrected the artifacts and target-motion audit, but event errors remain failures. Classify as agent/recovery, not a hidden pass. |
| `final-natural-3-sol` | Strict pass; actual encoded diagram/curve motion and source geometry checks pass. |
| `repeat-contract-sol`, `repeat-natural-sol` | Both strict passes on the exact 0.23.1 payload after clock/geometry stabilization and explicit repeat diagnostics. |

The 0.23.0 candidate-payload natural cohort is 2/3 strict passes, meeting the ordinary
naturalistic repetition threshold. The primary remains validating for earlier
broader-generation limits. Inspect the final posters and actual encoded frames;
all four final artifacts are eight seconds / 240 frames with no audio. No
native editor, speech synchronization or cloud video is claimed.
Some runs inspect the small motion runtime/inspector to understand integration;
none reads large vendor implementations, acceptance galleries or sibling skills.
Retain these read-surface observations rather than claiming zero source reads.

```text
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-focus-motion-natural.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-focus-motion-final-natural-1-sol --expect-output scene.html --expect-output focus.json --expect-output motion-review.json --expect-output poster.png --expect-output preview.mp4 --expect-output review.md
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261116-focus-motion-final-natural-1-sol/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

## Actual demonstration and starter checks

`make_focus_motion_demo.py` creates a nine-second silent 1080p30 local film with
three simple model stages and a fixed illustrative curve. Two continuous edge
traces cover the diagram's 3.6-second focus; a curve trace covers its 4.7-second
focus. The guide transfers between figures; both remain visible throughout.
There are no headings, camera moves or changing numerical values.

The actual preview has 270 frames, SHA-256
`24a2c96a6d98492426894def4607b7d0544f22868f1627892a52decc925f1023`.
The target-pixel checks pass for all three traces, with stable text/data and
repeat seeking. Inspect actual encoded diagram/curve frames separately from
the source poster. The inline SVG is an original conceptual example, not a
claim of a native Mermaid asset or sourced scientific measurements.

The default linked starter passes target-motion and existing layout audits.
The native atlas builds with 20 Mermaid families / 26 D3 forms. Extending its
first scene to 28 seconds exercises longer focus slots; its target-pixel audit
passes with unchanged labels/data. Existing atlas layout checks remain separate.
This is existing-fixture validation rather than new broad-generation evidence.

## Repository and publication boundaries

Pattern IDs, independence and payload checks pass. The original dirty checkout
retains its four pre-existing unrelated semantic reference-route findings;
scoped Line World checks and the clean publication tree are validated separately.
The native Vids upload-permission status remains unchanged.

The package workflow now installs a browser and runs the actual motion tests
before publishing installable artifacts. Reuse the clean publication worktree,
merge only Line World backlog/index/inventory changes and preserve unrelated
working-copy edits. `prepare_publication.py` now selects the release note by
package version and avoids appending duplicate frozen-runtime attributes.
No new Pages example/catalog is introduced: the demonstration and bulky media
remain project-owned ignored artifacts. Verify the actual main-branch push and
CI package/Pages results before reporting publication complete.


## Linux repeat diagnostic and 0.23.1 recovery

The first published package workflow (run 43859959142) failed a strict pixel
repeat on `linked-history-build`, while the other seven default-starter holds
and all other motion tests passed. Retain that failed run; a Windows pass did
not establish Linux repeat behavior. The Pages workflow for that commit passed.

Version 0.23.1 settles registered timelines at zero, stops the GSAP ticker
before capture and after each explicit parent-clock render, and caches path
length by actual geometry instead of remeasuring fixed curves on each frame.
It compares normalized RGB images, actual repeated geometry and actual paint
state. It also records maximum channel difference, changed-pixel count and
paint diagnostics for any repeated-frame mismatch. Pixel equality is still
strict; motion thresholds are unchanged. Do not assert a specific rasterizer
cause from the original boolean-only failure report.

The ten browser tests, all 228 installed tests, current-payload contract/natural
forwards and the unchanged nine-second demonstration pass locally. Verify the
new actual Linux workflow before declaring the CI recovery complete. Root
publication artifacts retain the initial failure and current workflow receipts.
