# Review a collection without losing delivery identity

Use this workflow when reviewing several existing films, refreshing examples, or
finding which export a user should open. Declare one **current** movie per
production. Keep drafts, old native exports and voice references as **reference**
entries; never select a winner by filename or modification time alone.

```text
uv run --script <skill-root>/scripts/review_collection.py --manifest collection.json --output reviews --include-reference
```

Paths resolve relative to the manifest. The minimal contract is:

```json
{"videos":[
  {"id":"training","production":"training","role":"current",
   "video":"training-final.mp4","story":"story.json","cues":"cues.json",
   "sourceKind":"svg","html":"composition/index.html","clock":"scene-local",
   "guideSelector":"#guide","manualReview":"training-observations.json",
   "provenance":{"nativeGoogleVidsExport":false,"renderer":"Local browser and FFmpeg"}},
  {"id":"training-previous","production":"training","role":"reference",
   "video":"training-previous.mp4","sourceKind":"encoded"}
]}
```

Choose the real source contract:

| `sourceKind` | Source review |
| --- | --- |
| `svg` | Generic SVG geometry, guide and reading audit; declare the actual guide selector and clock. |
| `paper` | Original-paper source audit, protected words, source-region visibility and calm camera motion. `html` points inside the prepared paper project. |
| `website` | Original screenshot, native light theme, target bounds, guide and measured audio checks. `html` points inside the built website project. |
| `starter` | The linked/atlas renderer's own audit, including full-frame partitions and quantity bindings. |
| `encoded` | Encoded content and full decode; no internal geometry claim. Useful for history, canvas or independent feature demonstrations. |

Do not apply the generic SVG image-obstacle policy to a whole paper or website
capture: the source image intentionally covers the frame. Use its specialist
audit. The collection tool runs these helpers directly without an account
browser or a second skill. It normalizes `scenes` with `duration` or
`clipSeconds`, and the starter's `beats` clock. A reference can omit the story
and use its actual encoded frame budget for review.

Read `summary.json` and affected `result.json` files first. Open `index.html` for
direct MP4 and frame-gallery links. Every movie is identified by SHA-256.
Encoded caches and source-audit receipts are reused only when their actual input
and output hashes match. `--include-reference` decodes historical movies too;
their findings remain visible but do not certify or invalidate a newer current
delivery. The command exits unsuccessfully if a current machine review fails.
Manual status is a separate field.
The helper uses two independent review jobs by default. Use `--jobs 1` for a
constrained machine or `--jobs 3`/`--jobs 4` for a larger archive. Jobs have
separate output folders; the final index preserves manifest order.
For declared long-hold or photographic focus plans, add
`"checks":["focus-motion","photo-focus"]` to the entry. These run the bundled
actual-pixel inspectors and cache their reports by source and tool digests.
Declare the relevant checks; the batch tool cannot infer omitted focus windows.
Each helper runs through its own UV metadata, including optional PDF/rendering
dependencies, so the collection needs no combined image/PDF Python environment.

## Bind real observations

Inspect every current scene, transitions and relevant spoken passages. Record
what was actually checked; unattended extraction is not a visual or listening
pass. Copy movie and source hashes from the entry's `result.json`:

```json
{"videoSha256":"actual movie digest","sourceSha256":"actual source digest or null",
 "scenes":[{"id":"scene-id","reviewed":true,"notes":"Observed result and disposition."}]}
```

Include every scene exactly once. Point `manualReview` to this file and rerun.
Missing notes remain pending; changed hashes become stale. `deliveryReady`
requires current machine checks and matching observations. This record is
distinct from a single-film `review_video.py` attestation; use the collection's
source fingerprint, including specialist source inputs.

Publish an exact delivery index after fixes. Distinguish a new local movie from
an earlier Google Vids export. Keep native blockers and voice provenance
explicit. Claim updated cloud visuals only after observing replacements and a
new native export.
