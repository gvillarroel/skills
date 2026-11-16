# Incremental native handoff

## Contents

- [Start and resume](#start-once-then-resume)
- [Measured batch build](#measure-and-build-in-one-batch)
- [Selective edits and receipts](#edit-and-acknowledge-only-completed-ui-work)
- [Compact UI observations](#keep-ui-observations-compact)
- [Complete the delivery](delivery.md)

Use `scripts/vids_batch.py` for repeatable production and revisions. It preserves
measurements, prepares uploads in one FFmpeg batch, caches identical outputs,
and lists only native UI actions still needed. It never operates Google Vids.
Keep the skill read-only; all state/media/history are written in the project.

## Start once, then resume

```text
uv run --script <skill-root>/scripts/vids_batch.py init --story source-story.json --project film
uv run --script <skill-root>/scripts/vids_batch.py next --project film --limit 3
```

The story uses the existing scene handoff schema. Add `sourceClip` for each
rendered input; the generated upload goes to `media/<stable-id>.mp4` without
modifying that input. Relative inputs resolve from the source story at init.
Declare `staticHoldAfterSeconds` only when the producer guarantees that the
remaining clip is a static reading hold. Retiming may trim/extend this hold;
the tool rejects cuts through essential animation and undeclared holds.
It rejects a dimension mismatch instead of silently distorting the artwork.

Keep the same IDs across edits. Reordering does not change media filenames.
`.vids/state.json` stores measurements with script/language/voice fingerprints,
native confirmations and local clip receipts. A changed script/voice invalidates
its old measurement. A changed source file invalidates its upload. Source hashes,
frame budgets and encoding settings key the clip cache; corrupt cache bytes are
rebuilt. Unchanged prepared media are reused without another encode.

## Measure and build in one batch

Commit the scripts and insert the actual native voiceovers. Then save current
observations as JSON with `voice` and `scenes` containing stable `id`,
`observed: true`, `voiceoverSeconds`, `sceneSeconds`, and optional nonnegative
`audioLeadSeconds`/`tailSeconds`. Preserve actual units and evidence.

```text
uv run --script <skill-root>/scripts/vids_batch.py build --project film --observed measurements.json
```

Alternatively import copied native scene announcements together:

```text
uv run --script <skill-root>/scripts/vids_batch.py observe --project film --input scene-announcements.txt --announcements --voice Nyla --order-verified --voiceovers-inserted
uv run --script <skill-root>/scripts/vids_batch.py build --project film
```

The two flags attest observations already made through the real interface.
They do not authorize or perform UI mutations. Text import maps scene ordinals
to the verified current story order and records speech as a conservative bound
from the scene containing the inserted voice. JSON supports exact audio properties.
Do not import old announcements after editing scripts or changing voices.

Build preflights the ready batch before encoding anything, ceils durations to
frames and strips source audio so it cannot duplicate native narration. It writes
`handoff/timing.json`, `resolved-story.json`, `observed.json`, `queue.json`,
`scripts.txt` and a small `build.json` summary. A missing/stale voice remains a
pending action; it never becomes a fabricated measured timeline. `--plan-only`
avoids media work. Use the original verifier for the actual downloaded export.

## Edit and acknowledge only completed UI work

Patch by stable ID rather than regenerating the story:

```json
{"scenes":[{"id":"split","script":"The revised exact narration."}],"order":["prepare","split","evaluate"]}
```

```text
uv run --script <skill-root>/scripts/vids_batch.py edit --project film --patch changes.json
uv run --script <skill-root>/scripts/vids_batch.py build --project film
uv run --script <skill-root>/scripts/vids_batch.py next --project film --limit 3
```

Edit validates before writing and saves the prior story under `.vids/history/`.
Supported changes include title, language, voice, existing scene script/source/
hold fields and complete ID order. Edit motion/data geometry in its producer.
After completing a queued native upload or order verification, confirm its exact
task ID with a receipt array containing `observed: true` and concrete `evidence`.

```text
uv run --script <skill-root>/scripts/vids_batch.py confirm --project film --receipt ui-receipts.json
```

The receipt is a local journal of fresh UI observations, not automatic proof.
Task IDs include content fingerprints; stale receipts are rejected. Confirming
local preparation never claims an upload, generated voice or native export.

## Keep UI observations compact

The pure `assets/runtime/vids-ui.js` parser accepts fresh CUA accessibility text
and returns only the Vids URL, save status, precise announcement, timers, current
media/script and enabled relevant controls. It has no UI/file/network operations.
Load its small definition into the current documented CUA runtime once, then use:

```javascript
const raw = await app.getAXState({emit:false,disableDiffing:true});
nodeRepl.write(LineWorldVidsUI.summarize(raw));
```

Use indices only with that fresh state. After actions observe again. The helper
does not fix a missing control, an unverified URL or a browser policy stop;
follow the host's documented handoff. It intentionally omits unrelated file lists.
For uploads, `LineWorldVidsUI.uploadNext` returns one recommendation from current
state and queue targets; see the [UI workflow](ui-workflow.md). An empty upload
queue is not a finished delivery: run `vids_batch.py deliver --project film
--video native-final.mp4` and follow [verified delivery](delivery.md).

When all scenes need fresh narration, inspect the native All scenes bulk action
before generating individual voices. For a revision affecting one scene, update
that scene. Google documents that generating all voiceovers can replace existing
generated tracks; preserve completed scenes by following the selective queue.
UI labels vary; the bulk operation was documentation-verified, not newly executed
against a live account in this utility pass.

Sources: [native AI voiceover controls](https://support.google.com/docs/answer/15070345?hl=en-GB),
[bulk replacement behavior](https://support.google.com/a/users/answer/15599399?hl=en).
