# Reusable narrated project delivery

## Contents

- [Choose the smallest revision](#choose-the-smallest-revision)
- [Prepare and assemble](#prepare-and-assemble)
- [Package portable inputs](#package-portable-inputs)
- [Review and native handoff](#review-and-native-handoff)

Use `scripts/project_delivery.py` after rendering scene clips and measuring the
actual narration. It is a local FFmpeg utility, not an editor uploader or a
voice generator. Execute its commands without reading its implementation.
Keep the loaded skill read-only and all requests/outputs in the project.

## Choose the smallest revision

| Change | Work to repeat |
| --- | --- |
| Photograph, filter, icon or surface color | Reuse approved speech and cue times; change the object/variant or shared theme; inspect bounds and affected joins. |
| Guide target or route | Keep speech; adjust semantic ports/clearance and inspect the full route, including repeated-value destinations. |
| Narration, language or voice | Review the subject-focused script and contributor context, generate only changed voices, measure actual extents, then align cues and visual budgets. |
| Paper navigation | Preserve captures; use one gradual entry and fixed-scale pans with stable reading holds. Verify emphasis against source text/ink. |
| Local visual clips already match measured speech | Assemble and package them with this helper. Reuse matching digests instead of encoding again. |
| Google Vids delivery requested | Finish actual native replacement, playback, export and download with observed receipts. A local assembly does not clear that work. |

Use the semantic editor's `inspect`, `plan`, `apply` and `status` for small JSON
changes. Use `documentary_assets.py` for real-object treatments and bindings,
`inspect_items.py` for icon/text contrast and centering, `inspect_focus.py` for
small custom figures and `review_video.py` for the whole film. Read only the
reference needed for the selected operation. Do not regenerate a complete
film, rewrite unchanged scripts or read vendor/gallery source to make a small edit.

## Prepare and assemble

Put the assembly request at the project root above all its inputs. Existing
story and observed-reference JSON must have the same ordered scene IDs. Story
scenes contain `clipSeconds` (or `duration`); observed scenes contain measured
`sceneSeconds` (or `duration`). Clips use `01-<id>.mp4`, `02-<id>.mp4`, etc.

```text
uv run --script <skill-root>/scripts/project_delivery.py prepare --story film/story.json --observed film/observed.json --voice film/native-reference.mp4 --voice-provenance "Google Vids; actual downloaded voice reference" --clips film/clips --output film/assembly.json
uv run --script <skill-root>/scripts/project_delivery.py assemble --request film/assembly.json --output film/artifacts/videos/complete-local.mp4 --report film/artifacts/reviews/assembly.json
```

The first command builds the reusable request from actual ordered observations
and verifies clip frame counts against the story. Do not label estimates as
observations. The source reference's audio follows that same scene order.
For differently named clips, author the small request directly:

```json
{"fps":30,"voice":{"file":"voice.wav","provenance":"Actual source and provider, or explicitly synthetic fixture"},"scenes":[{"id":"split","clip":"clips/split.mp4","voiceSeconds":12.37}]}
```

Paths resolve relative to this request, stay inside its project and use no
parent traversal. Keep unique IDs and record voice provenance honestly; the
helper does not independently establish a provider, approval or word alignment.
Supported clocks are 24, 25, 30 and 60 fps; all clips must have compatible H.264
parameters and the selected rate. The helper stream-copies visuals, partitions
actual decoded narration and adds only the silence needed by visual frame
rounding. It rejects speech exceeding a scene budget; extend/rerender that
scene instead of speeding or truncating speech. A nonzero reference-container
tail of at most 250 ms extends the last reading frame. Even a very quiet tail
is preserved. A larger discrepancy requires remeasurement.

Read the compact result and assembly report first. They include exact frames,
padding, tail holds, source/PCM/output digests and `nativeGoogleVidsExport: false`.
The first assembly fully decodes the result. An unchanged repeat checks actual
input/output digests, returns `reused: true` without media commands and updates
the compact receipt so stdout and the report agree about reuse. A changed or
corrupt output needs a new destination, or explicit `--replace` for an owned
revision. Validation finishes before atomic replacement; failures preserve the
previous movie. Matching hashes are cache evidence, not a fresh visual review.

## Package portable inputs

```text
uv run --script <skill-root>/scripts/project_delivery.py bundle --request film/assembly.json --include story.json --include composition --output film/artifacts/packages/sources-r1.zip --report film/artifacts/reviews/source-bundle.json
```

Each `--include` is relative to the request's project root. Select only owned
source files needed by the recipient; do not include the whole working tree.
The archive automatically contains the request, actual voice reference, every
rendered clip, a self-contained copy of this utility, `rebuild.py` and a digest
manifest. Add renderer source, original image files, requests and credits when
they are needed for further editing. Include their complete local dependency
set; the helper cannot infer arbitrary JavaScript/image imports. Do not package
credentials, external private state or dependency/cache directories.

After extracting, run `uv run --script rebuild.py` from the bundle root to
reassemble the included media, or choose `--output artifacts/videos/review.mp4`.
This reproduces local assembly. Regenerating visual clips needs the included
project renderer and its dependencies; a bundle of clips alone is not proof
of a complete source renderer. Verify a clean extraction and required rebuild
before promising that portability. ZIPs are immutable per path; unchanged
requests reuse their recorded digest, while changed revisions need a new name.

## Review and native handoff

When the user needs a download beyond this workspace, deliver an authenticated
file attachment or a verified web link. A Windows/local path is an editable
workspace location, not proof of a working download in the user's chat client.
If the connected Drive tools support local uploads, inspect their current
argument schema, upload the completed MP4 to the user's drive without changing
sharing, read back its actual MIME type/size and use the returned URL. Fetch a
stored video as a complete raw file, not a native-document export, when a
downloadable attachment is needed. Keep signed bearer URLs out of the reply;
use the authenticated file reference. Replace an existing owned delivery only
after grounding its ID and verifying the new bytes. Drive storage of an MP4 is
distinct from native Google Vids assembly/export.

Run `review_video.py` on the complete movie and inspect encoded reading/cue/join
samples. Keep exact video/source hashes with actual operator notes. Whole-frame
content checks, source geometry and manual judgments are different evidence.
For a visual-only revision, compare the approved audio or aligned PCM digests;
do not claim byte identity from matching durations. Preserve readable names and
contributions, primary-red guide, white-on-red content and unclipped labels.
When only visuals change and every scene keeps its approved frame budget,
reuse the approved complete audio stream instead of generating speech again.
Concatenate the revised silent clips, then map that video and the approved
movie's audio with FFmpeg stream copy. Compare actual compressed AAC payloads
(`-map 0:a:0 -c:a copy -f adts`) before claiming exact preservation. If the
approved movie includes one or two final reading-hold frames protecting a
quiet voice tail, preserve those frames too. Fail on an unexplained budget
change; equal total duration alone does not prove per-scene synchronization.
Record a new movie digest and keep the approved reference immutable.

When the native editor is unavailable or upload permission is rejected, retain
the local movie, exact clip queue, scripts, observations and approved speech.
Report the native status accurately. Do not retry around a permission rejection
or manufacture cloud playback/download receipts. Resume from fresh native state
once the actual blocker is resolved. Prefer the verified cloud movie link when
native delivery is complete; identify a local assembly as local throughout.
