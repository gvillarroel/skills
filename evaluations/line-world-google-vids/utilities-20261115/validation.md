# Incremental production utilities — November 15, 2026

Release 0.7.2 updates line-world-video and line-world-google-vids. It does not
regenerate the delivered native movie or modify a live account in this pass.

## Contents

- [Implementation](#implementation)
- [Runtime and media checks](#runtime-and-media-checks)
- [Measured costs](#measured-costs)
- [Release gates](#release-gates)

## Implementation

The reusable batch CLI replaces project-specific timing, trim and hold-repair
scripts. It accepts existing handoff stories and actual native observations,
preflights all ready media, ceils coverage to frames, preserves source files,
removes duplicate source audio and caches by source content and output settings.
Declared static holds delimit permitted trimming/extension. Dimension mismatch
and essential-motion cuts fail before any scene in that batch is encoded.
Byte-compatible H.264/yuv420p silent sources can be copied rather than re-encoded.
The exact-copy path also checks frame count, rate and duration compatibility.
An input already occupying the default upload filename is preserved by using a
separate prepared subfolder. The common validator accepts a rendered sourceClip
without demanding a redundant visual brief.

Stable-ID edits retain other measurements. Script/language/voice fingerprints
invalidate stale timing, and reused old observation bytes cannot be rebound to
new narration. Content-bound queued tasks require concrete observed native UI
receipts; local preparation alone never claims that an upload occurred. File
history and pending actions allow another operator to resume the same project.

The compact AX parser exposes fresh relevant controls, scene cards/tabs and
timing while omitting unrelated file lists. It refuses non-Vids document text.
It has no UI, network or file operations and cannot override a host URL guard.
Bulk voice generation guidance is based on current Google documentation; because
it can replace existing generated tracks, selective updates remain appropriate
when only some scenes changed. The bulk operation was not newly executed here.

The primary producer now supports validated JSON merge patches with rollback and
no-op detection. Direct browser screenshots are the default; the SVG/resvg route
remains available explicitly. A small benchmark avoids full renders just to
select a backend.

## Runtime and media checks

Commands:

```text
uv run --script skills/line-world-google-vids/scripts/test_vids_batch.py
uv run --script skills/line-world-google-vids/scripts/test_vids_plan.py
uv run --script skills/line-world-video/scripts/test_story_update.py
uv run --script skills/line-world-video/scripts/test_line_world.py
uv run --script projects/line-world-video/scripts/review_utility_evaluations.py
```

All 61 deterministic tests pass: 23 batch/parser, 9 timing/schema, 3 story
update and 26 original producer tests. Real FFmpeg clips exercise cache reuse,
one-scene invalidation, source preservation, restored deleted uploads, corrupted
cache recovery, source-audio removal, frame ceilings and boundary rejections.
The pure parser is fixture-tested, including fresh scene/tab indices and rejection
of unrelated browser documents. Failed initial test expectations (a Windows argv
length limit and incorrect expected total duration) were fixed in the test harness.

Fifteen actual strict isolated pi runs pass: batch contract 1, naturalistic 3,
generalization 3, boundary 1; producer contract 1 and naturalistic 3; final adapter
naturalistic, compact-parser contract and final source-preservation contract 1 each. Model exception remains
openai-codex/gpt-6.1-sol with medium thinking because Spark is unavailable for
this account. Exact output paths, unchanged runtime payloads, clean JSON events
and zero tool errors are checked. No ambient skills or acceptance galleries
were used. Typical traces read the entrypoint, focused references and task files,
without reading vendor runtimes or the batch implementation.

The initial batch source preflight failed because the new reference exceeded
100 lines without a contents section. The runner tried all eight source checks
before reaching producer cases; no pi/model executions occurred for those eight
exits. results-all.json preserves them. The repaired batch passed all eight
actual runs; final follow-up cases cover the final runtime payload. The independent
reviewed-results.json records all seventeen actual runs and their read surfaces:
fifteen passes and two initial strict failures. The first source-preservation
contract produced correct final files after agent recovery, but its initial
sourceClip-only story hit the old validator's redundant visual requirement.
That tool error correctly failed strict validation. The shared schema was fixed,
a deterministic regression added, and the case repeated in a fresh workspace.
That second attempt produced correct domain artifacts but failed strict checks
because the agent first listed nonexistent task directories. The contract prompt
now creates those fixture folders first; the fresh third attempt passes.
Both failures are retained with skill-schema-contract and agent-tool-error classes.
Review checks the actual encoded frames, dimensions, silent streams, contiguous
timing and native-action boundaries rather than trusting final model prose.

A real 21-second 1080p24 local composition rendered 504 frames with no browser,
palette, data-binding or layout findings. Its contact sheet was visually inspected.
This is a local fallback render; native HyperFrames/Google Vids execution is not
claimed for this utility validation. The earlier native narrated MP4 is preserved.

## Measured costs

`utility_benchmark.py` prepares the previous twelve-scene measured sources in an
isolated project, then repeats unchanged. The first measurement was 12.244 s
(8 encodes and 4 compatible copies); the warm pass was 0.588 s (12 cache reuses,
0 encodes). A final compatibility-guard run measured 10.588 s cold and 0.569 s
warm, an 18.61-fold improvement for this repeated preparation, retained under
projects/line-world-video/artifacts/utility-benchmark-final/. No live voice or
editor operation is part of this benchmark.

`render_line_world.py --benchmark-capture --benchmark-frames 6` on the existing
linked example measured browser median 0.05110 s/frame and SVG/resvg median
0.27069 s/frame: 5.30 times faster in this capture microbenchmark. Both samples
are retained. This is not an end-to-end, token-cost or future hardware guarantee.

The fixture AX summary is less than one twentieth of its synthetic full input.
No claim of a measured reduction in billed model tokens is made; benefits come
from smaller observations, avoiding repeated code generation and executing only
changed work.

## Release gates

Version 0.7.2 is packaged with six skills. Extraction digests, the extracted
starter, portable schema and task-local native Codex marketplace/install checks
pass. Host evidence is version-scoped so earlier release reports remain intact.
The changed canonical bundles are synchronized and validated locally. Pattern
IDs, independence tests and payload checks pass. Global validation/synchronization
retain four unrelated existing reference-route findings in curate-semantic-model,
extract-ontologies and extract-with-ontology. No unrelated skill is edited and
no Pages example is published in this pass.
