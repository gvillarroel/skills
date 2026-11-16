---
name: line-world-google-vids
description: Assembles scene clips and narrated scripts in Google Vids through the actual supported interface, measures voice and scene timing, preserves visual continuity, and exports a downloadable complete video. Use for Line World or other prepared video assets that need native Google Vids voiceovers, scene placement, timing review, and verified MP4 delivery.
---

# Google Vids scene production

Use Google Vids as the actual editor and voice provider when requested.
Preserve the requested visual style, language, facts and output paths. Keep
the private project private unless the user requests sharing. Reuse an
authorized signed-in account; inspect connected identity before choosing among
browser profiles. Do not claim a local render was exported by Google Vids.

## Prepare

For new productions or revisions, prefer the resumable
[batch workflow](references/batch-production.md): `vids_batch.py init`, then
`build --observed measurements.json`, `next`, and `confirm` after verified UI
work. It batches clip preparation, reuses identical outputs and invalidates
changed narration. Use `edit --patch changes.json` for stable-ID revisions.
Read only pending scripts/uploads from `next`; keep complete handoff files on disk.
An empty upload queue still needs export and delivery; `next` reports that stage.
The lower-level commands below remain useful for a simple handoff/export check.

1. Read [scene handoff](references/scene-handoff.md). Obtain one clip and script
   per stable scene ID, with the ordered story and meaningful visual cues.
   Keep this skill read-only; generate files in the requested workspace.
2. Run `uv run --script <skill-root>/scripts/vids_plan.py prepare --story story.json --output handoff`
   to produce the ordered scripts, timing worksheet and upload checklist.
3. Keep narration segments short enough to edit and regenerate independently.
   Explain the subject's mechanisms, evidence and consequences. Remove speech
   about how the video was drawn, what the guide does or harmless diagram
   simplifications. Keep brief navigation and limitations needed to interpret
   the evidence. Review scripts before paying the cost of native generation.
   Prefer a consistent voice and language. Use essential figure labels; add
   visible titles only when requested. Optional specialist producers may supply
   D3/Mermaid clips; this adapter also accepts ordinary local MP4 scenes.
4. For visible contributors, require a spoken name and relevant contribution,
   a readable adjacent name/role caption and a semantic cue for the first name.
   A portrait with only a logo or an unspoken name needs a script revision.
   Regenerate only affected voices, then measure their actual new timing.

## Operate the real interface

Read [UI workflow](references/ui-workflow.md). Discover a purpose-built Vids
connector first. When its required operations are unavailable, use the current
computer-use tool and its documented APIs for all live UI interactions.
Observe after actions and derive fresh controls from the current page. For clip
uploads, use `LineWorldVidsUI.uploadNext` from the bundled pure parser, as described
in the UI workflow. It recommends one next step without operating the account.
Request a full current AX tree when deriving controls; diffs omit unchanged ones. Never
use hidden endpoints, browser-profile credentials, private CDP transports or
filesystem session extraction to bypass the interface.

Create or open the requested project, preserve the correct scene order, and
place each clip in its matching scene. Paste its exact script into the native
voiceover editor, generate/insert the voice, and verify the result. The live
interface may combine generation with Insert voiceover. Record what it does;
do not require an obsolete Generate button. Retain the same voice across scenes.
Do not buy an upgrade or bypass an authentication barrier to complete a draft.

## Measure and synchronize

Read [timing and continuity](references/timing-continuity.md). Build timing
from the inserted native voiceovers and scene properties. Word counts are
planning estimates. Do not shorten speech to fit a preselected clip duration.
After inserting a visual, recheck the scene length: video insertion can extend
it and create an unwanted silent tail. Keep playback at normal speed, trim the
reading hold, or regenerate the visual to the measured scene budget.
For a moving guide, read [semantic audio cues](references/narration-cues.md).
Use word timestamps from the actual voice to align stable target IDs, including
separate occurrences of repeated values. Keep all late cues in the rendered
clip; a fixed early animation followed by a hold can break speech-linked focus.

Record observed durations by scene ID in the timing worksheet. Compile it with:

```text
uv run --script <skill-root>/scripts/vids_plan.py compile --story story.json --observed handoff/observed.json --output handoff/timing.json
```

Verify actual start/end poses and voice boundaries, not only total duration.
Before replacing or exporting, read the actual timeline scene-button count and
select every scene freshly. Use `vids_inventory.py` as described in the timing
reference to reject extra empty scenes, stale announcements and shifted media.
An old selected-scene status can disagree with the current timeline count.
The last visual of one scene and first visual of the next must support the
intended cut or pan. Use a short intentional reading pause instead of accidental
blank frames, mismatched camera positions or extended silence.

## Export and verify

Read [verified delivery](references/delivery.md). Use the observed File export/
download action for the complete MP4. Export to Drive also provides an accessible
cloud movie. Keep the actual project URL, downloaded bytes and native receipt.
For batch projects, finish in one resumable command:

```text
uv run --script <skill-root>/scripts/vids_batch.py deliver --project film --video native-final.mp4
```

The first call prepares unobserved fields; fill only actual observations and run
it again. It combines native inventory, cached full decode, cloud metadata and
playback/download receipts, then writes `handoff/delivery.json` and `.md`.
For existing projects outside the batch workflow, use `vids_delivery.py prepare`
and `check` from the same reference. Neither command operates the account.

Inspect speech endings, reading frames and joins in the actual movie. Deliver
the verified playable/downloadable Drive MP4 link first, then the editable Vids
URL, timing and source assets. A voice-only project or a local machine path does
not fulfill a requested complete native/cloud delivery. Keep blocked, estimated,
native and fallback evidence distinct. Read [recovery](references/recovery.md) for UI,
account, language or export failures; preserve completed work while recovering.
