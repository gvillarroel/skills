# Incremental editing

## Contents

- [Small edits](#small-edits)
- [One theme for all producers](#one-theme-for-all-producers)
- [Select local render work](#select-local-render-work)

Use `scripts/video_edit.py` for routine revisions. Execute it; do not read its
implementation or regenerate a complete document to change a few values. Keep
all task files outside the loaded skill. These operations use local Python and
do not call a model, synthesize speech or operate an editor account.

## Small edits

`line_world.py init` registers its project automatically. For custom narrated
projects, register existing JSON once (omit `--cues` when absent):

```text
uv run --script <skill-root>/scripts/video_edit.py setup --project film --story story.json --cues cues.json
uv run --script <skill-root>/scripts/video_edit.py inspect --project film --file cues --path "scenes[id=split].cues[id=test]"
```

Inspection returns the selected value and file SHA-256, with bounded summaries
for large objects. Use unique stable IDs, or a unique phrase selector for older
cue documents. Repeated percentages need separate targets and IDs. A change
patch sets existing fields; selectors must match exactly one object:

```json
{"changes":[
  {"file":"cues","path":"scenes[id=split].cues[id=test].travelSeconds","expect":0.25,"value":0.18},
  {"file":"theme","path":"fontScale","value":1.05}
]}
```

```text
uv run --script <skill-root>/scripts/video_edit.py plan --project film --patch changes.json
uv run --script <skill-root>/scripts/video_edit.py apply --project film --patch changes.json --report film/edit-report.json
```

`plan` is read-only. `apply` validates the complete candidate, checks cue budgets,
writes atomically with rollback, compiles theme CSS and saves an undo revision.
Patch/receipt paths resolve from the working directory, or from the project
when absent there. Conflicting existing paths require an explicit path.
Unchanged edits preserve files and modification times. Optional
`expectedSha256: {"cues":"<inspection hash>"}` rejects intervening edits.
Use `restore --project film --revision <revision>` for an exact-byte undo; a
later conflicting edit blocks it. Structural additions/reordering remain an
explicit authoring task. The existing `line_world.py update` remains useful
for merge patches; its arrays replace complete arrays.

## One theme for all producers

Edit `theme.json`, then use the editor or its `theme` command to compile
`theme.css`. Use exact palette tokens. Primary red stays `#9e1b32`; the default
secondary highlight is `#696969`. Font scale and base line width are bounded.
Changes to type size still require a label/stroke clearance audit.

New starters load the theme automatically. For custom HTML, copy the bundled
`assets/runtime/theme.js` into project assets, link the generated `theme.css`
in the head and load the runtime before the scene. Read
`LineWorldTheme.colors()`, `.fontScale()` and `.lineWidth()` when building SVG.
Use CSS roles `data-color-role="primary-highlight|secondary-highlight|quiet"`
and `data-text-role="label|small"`. Preserve quantitative attributes and the
guide's own size choreography. Existing hard-coded artwork needs this explicit
integration; loading CSS cannot rewrite arbitrary inline JavaScript colors.
The packaged D3, Mermaid, icon and HyperFrames copies include these same theme
resources. Pass project-owned theme/assets between producers.

## Select local render work

```text
uv run --script <skill-root>/scripts/video_edit.py status --project film --details --report film/render-plan.json
uv run --script <skill-root>/scripts/video_edit.py record --project film --receipts film/render-receipts.json
```

Setup tracks existing `scene.js`, `index.html` and static `assets/` files. In
`.line-world/editing.json`, declare every additional renderer/data input in
`sharedInputs` or `sceneInputs: {"split":["figures/split.svg"]}`. Cache reuse is
valid only for tracked inputs. Put cross-scene view IDs in `overviewIds`.
`clock` is `global` for time-dependent whole-film animation, `scene-local` for
independent clips. Do not select scene-local merely to avoid invalidation.

Render the listed `render` scenes first, in story order. `checkJoin` means that
reuse depends on an unresolved predecessor endpoint. Capture real first/last
poses from the renderer (camera, guide and every persistent object needed at
the join), excluding elapsed time and scene index. Record an array of receipts:

```json
[{"id":"split","inputsSha256":"<status fingerprint>","artifact":"clips/split.mp4",
  "firstPose":{"camera":{"x":0,"y":0},"guide":{"x":300,"y":400,"r":10}},
  "lastPose":{"camera":{"x":0,"y":0},"guide":{"x":900,"y":400,"r":10}}}]
```

The helper hashes actual artifact bytes and rejects stale fingerprints or
unequal joins. Rerun status after recording. An unchanged endpoint permits
successor reuse; a changed endpoint propagates work until a stable join.
Global starts, overviews, shared styles and missing/corrupt artifacts invalidate
their dependents. Receipts are renderer evidence, not an automatic visual audit.

Changes to script, voice or language require actual audio remeasurement and cue
realignment. `narrationReview` remains flagged against the first recorded script;
a local render cannot clear it. Use the Google Vids adapter's `edit`, `observe`,
`build`, `next` and confirmed native receipts for the authoritative audio and
upload state. Never infer native completion from this local render cache.
