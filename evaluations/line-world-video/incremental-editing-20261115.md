# Incremental video editing: release 0.9.0

Date: November 15, 2026. Scope: make local scene/data/style revisions easier to
execute with bounded context, deterministic edits and verified render reuse.
The existing narrated Google Vids film was not changed or re-exported.

## Released behavior

The primary skill now supplies `scripts/video_edit.py` with `setup`, `inspect`,
`plan`, `apply`, `restore`, `theme`, `status` and `record`. Existing-field paths
select objects by stable ID or another unique value, rather than replacing
arrays. Optimistic fingerprints/expected values, candidate validation,
transaction rollback, exact-byte undo and true no-op writes protect revisions.
Patch/receipt files resolve from the working directory or project, rejecting
conflicting existing files. Reports cannot replace editable inputs/metadata.

The linked and atlas starters create project-owned theme JSON/CSS, a runtime
token reader, a compact editing registry and a copied standalone editor.
All five visual producer bundles include identical theme CSS/JS and an updated
handoff contract. Existing native SVG/imported artwork still needs its own
token integration. The six-skill portable OpenAI plugin and marketplace ZIPs
include these resources; the Google Vids adapter remains canonically unchanged.

Local reuse checks current data, cues, theme, declared renderer inputs, actual
artifact hashes, global starts, overview dependencies and actual join poses.
Changed endpoints propagate work until a stable join. A local render cannot
clear narration review or acknowledge native voice/upload/export operations.

## Deterministic and browser checks

The following suites pass, 98 tests total:

```powershell
uv run --script skills/line-world-video/scripts/test_line_world.py
uv run --script skills/line-world-video/scripts/test_story_update.py
uv run --script skills/line-world-video/scripts/test_video_edit.py
uv run --script skills/line-world-video/scripts/test_focus.py
uv run --script skills/line-world-google-vids/scripts/test_vids_plan.py
uv run --script skills/line-world-google-vids/scripts/test_vids_batch.py
uv run --script skills/line-world-google-vids/scripts/test_narration_cues.py
uv run --script projects/line-world-video/scripts/check_incremental_editing.py
```

Suite counts are 26, 4, 20, 8, 9, 23 and 8. The last command is a separate
browser integration check, not included in that test count. Its retained
`projects/line-world-video/artifacts/incremental-20261115/verification.json`
records six pixel-identical default comparisons against extracted 0.8.1:
linked at 2/26/47 seconds and atlas at 6/72/178 seconds. Both current starters
render 1.05 label scale with unchanged primary red. A custom complete-frame
fixture resolves secondary gray to RGB(79,79,79), increases 27px labels to
28.35px, passes actual text/stroke clearance and keeps its HTML bytes unchanged.
Manual inspection of `theme-preview.png` confirms a full-height divider,
readable table values, quiet bars and an adjacent primary-red guide.

The fixture inspects 224 response bytes instead of 984 full source bytes:
77.24% less data for that particular query. This is not a measured billed-token
or whole-task cost saving. Local commands call no model. The three-scene PNG
render fixture regenerates b after one cue edit, checks its actual measured
endpoint and reuses a/c. A global style edit invalidates a/b/c. These are local
renderer fixtures, not new encoded movies or measured speech.

## Isolated forward trials

Model exception remains `openai-codex/gpt-6.1-sol`, medium thinking, following
the previously retained Spark account rejection. Pi 1.4.0 used runtime-only
105-file bundles, disabled ambient context/discovery/extensions, exact output
paths and strict JSON/model/tool-error/integrity gates.

| Epoch | Case/run suffix | Artifact result | Strict result | Classification |
| --- | --- | --- | --- | --- |
| Initial | `contract` | pass | pass | command contract |
| Initial | `forward-1` | pass | pass | naturalistic revision |
| Initial | `forward-2` | pass | fail | project-relative patch lookup friction |
| Initial | `forward-3` | pass | fail | same lookup friction |
| Final | `v2-contract` | pass | pass | command contract |
| Final | `v2-forward-1` | pass | pass | naturalistic revision |
| Final | `v2-forward-2` | pass | pass | naturalistic revision |
| Final | `v2-forward-3` | pass | pass | naturalistic revision |

All run IDs start `20261115-line-world-edit-`; retain all eight workspaces and
raw event streams under `evaluations/runs/`. The initial two strict failures
each made one unsuccessful lookup before recovering. This was treated as a
skill usability issue and repaired in the CLI, with explicit ambiguity tests.
An initial evaluator diagnostic also addressed the manifest's model at the
wrong JSON level. Corrected only that verifier; preserve its original report
as `trials-verifier-diagnostic.json`. No submitted artifacts were repaired.

The final current runtime payload SHA-256 is
`063b63df473130c917bf1187fcfaa8a9562acc60cf491e6bef15822eb15d12a3`.
All four final copies match current canonical sources with zero deltas and
unchanged payloads during use. The final contract and 3/3 naturalistic trials
pass jointly. Read traces use only the entry skill, its incremental reference,
task inputs and bounded inspection output; no implementation/gallery/sibling
reads occur. The previous broad composition limitation remains separate:
`line-world-video` stays `validating` for generic new-layout generation.

Reproduce each case with the relevant prompt and fresh run ID:

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-incremental-forward.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id <fresh-id> --timeout-seconds 650 --expect-output film/story.json --expect-output film/cues.json --expect-output film/theme.json --expect-output film/theme.css --expect-output film/inspection.json --expect-output film/changes.json --expect-output film/edit-report.json --expect-output film/render-plan.json
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-incremental-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id <fresh-contract-id> --timeout-seconds 650 --expect-output film/story.json --expect-output film/cues.json --expect-output film/theme.json --expect-output film/theme.css --expect-output film/inspection.json --expect-output film/changes.json --expect-output film/edit-report.json --expect-output film/pending.json --expect-output film/reused.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
uv run --script projects/line-world-video/scripts/verify_editing_trials.py
```

Independent output review checks complete unchanged narration, exact cue IDs and
values, semantic patches, compiled styles, compact inspections, no invented
render receipts and expected cache transitions. Its `trials.json` retains
strict and artifact results separately plus per-output hashes/read paths.

## Package and repository gates

```powershell
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script projects/line-world-video/scripts/sync_local.py
```

The portable schema, both actual archives, exact canonical 105/16-file parity,
five matching theme runtime copies, clean extraction/init and native Codex
0.167.0 task-local installation pass. Native app-server `skills/list` discovers
all six enabled plugin-qualified skills. Thirty-six tests execute successfully
from the actual installed archive. All six extracted runtime skill bundles pass
standalone validation. No global install or desktop activation is claimed.

Archive SHA-256 values:

- Portable: `de5e0c6a1252d6742957e192640ed3d8646ae286a904f3b271902617e3d416da`.
- Marketplace: `90a87add37cc3bfd14d86a0324e0bb93f73296e08836234db8cb82677c3639e5`.

Version 0.8.1 archives and the approved narrated movie remain immutable.
Pattern IDs, independence tests, payload gate, focused canonical/packaged
validators and focused 105/16-file installation pass. Global repository
validation and global sync retain the same four unrelated semantic reference
route findings in curate-semantic-model, extract-ontologies and
extract-with-ontology. No unrelated skill was edited to hide those findings.
