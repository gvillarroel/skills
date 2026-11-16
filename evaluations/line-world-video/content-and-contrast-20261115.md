# Continuous content and primary-red emphasis — 2026-11-15

This revision covers `line-world-video`, its four dedicated producer copies,
and the native `line-world-google-vids` adapter. The final plugin is 0.12.4.
The user requested detection and removal of empty footage, clearer emphasis,
and subsequently rejected pink object backgrounds. The final default is white
faces with primary-red edges; explicit solid-red faces use white internal text.

## Actual defect and correction

The prior local 0.11 movie had content in all 6099 frames. Fresh inspection of
the actual private Vids project nevertheless found eleven timeline scenes and
a stale announcement claiming ten. Fresh selection of the second scene proved
a five-second extent with zero objects and no starting audio. The other ten
media scenes and original Nyla tracks remained in order. Only the proven empty
scene was removed with the undoable native Scene / Delete scene action.

The complete before/after observations are retained under the CUDA/AlexNet
project's `artifacts/data/native-content-before.json`,
`native-content-after.json` and `native-red-outline-after.json`. Current fresh
selection of every scene verifies ten scenes, zero empty visual scenes and
203.262 seconds at native announcement resolution. Count anchored timeline
button rows; the separate focused-element summary can repeat a button's name.
No sharing, voice generation or account settings were changed.

All ten red-outline clips were rendered and replaced through the normal native
Replace video / Upload controls. A current-browser file chooser attempted the
supported upload API, which reported missing extension file-URL permission.
The existing native Windows Open dialog completed the uploads without changing
that permission. Scene IDs, original voice, source cue times and budgets remain
unchanged. The actual final download is the observed `(6).mp4` export, copied
into the project; no local composite is described as a native Vids export.

## Reusable mechanisms

- `content_scan.py` measures all decoded constant-rate frames at 640×360.
  Ink against the white field must occupy at least 0.1% with at least 5% extent
  in each axis; uniform fields also fail. Exact intervals are reported.
- `visual-review.js` checks source explanatory anchors throughout the camera
  path. Guide dots, dividers, blank panels and unrevealed dashed paths do not
  count. Explicit visible aggregates and distributed observation fields qualify.
  The presence count is a capped lower bound, not a full object inventory.
- Both starter renderers run source and encoded gates. Linked/atlas fixes keep
  content visible from frame zero and overlap handoffs. The retained integration
  comparison rejects 18 empty opening frames in the old linked starter and
  21 frames across six old atlas intervals. Current linked/atlas scans pass
  1680/5550 source samples respectively with no empty intervals.
- `vids_inventory.py` independently checks fresh scene count, empty scenes,
  media order and measured extents. It rejects stale ordinal totals. It consumes
  observations and does not operate an account or authorize deleting useful work.
- `LineWorldTheme.focus` applies reversible 3 px red edges and text on white.
  A face marked `data-focus-fill="solid"` may become solid primary red; only
  explicitly internal `data-focus-on-fill` labels become white. Existing nonwhite
  fills, quantitative colors, photos and logos retain identity. No timer or
  geometry mutation is introduced. The shared browser palette audit rejects
  pink surfaces and translucent red that composites to pink.
- The video palette omits pink from generated category sequences; the canonical
  base token file is unchanged. All producer copies receive the current contract
  and runtime. The project preparer recompiles theme CSS before copying it,
  avoiding stale generated rules after a runtime upgrade.

Caches bind results to movie/source/script/policy hashes and verify cached
bytes. The review returns exact report paths and counts separately from the
compact summary. Gallery entries can share a frame; cache counts are unique.
An explicit operator record remains necessary for `deliveryReady`.

## Deterministic and native package validation

The actual 0.12.4 ZIP was extracted into a clean workspace, installed in a
task-owned Codex home, and discovered with native `skills/list`: all six skills
register. Portable and marketplace ZIP contents match; installed bytes match
the archive and both canonical bundles. Missing required-runtime rejection also
passes. Seven installed runners pass **65 tests**: focus 11, editing 20,
review 5, content/emphasis 7, media 9, narration cues 8, inventory 5.

Evidence: `projects/line-world-video/artifacts/host-checks/openai-0.12.4/verification.json`.
The portable archive has 290 files, 5,104,601 uncompressed payload bytes and
SHA-256 `53cf49c1b9c776b28d39dae052922ce07a070e21c38aeeda90b5d28024a2235e`.
The marketplace archive SHA-256 is
`f3d76e903140a2ce631b590e99c8c9d97447ea3460d2f5826f6749cdf6c40b88`.
No global native activation or account publication is claimed.

## Isolated forward tests

Use the already recorded account exception `openai-codex/gpt-6.1-sol`, medium
thinking, because Spark is unavailable for this account. Strict mode, runtime
isolation, exact outputs, event/tool gates and read-only integrity remain intact.

Final primary run `line-world-red-outline-release-20261115` passes all 11 exact
outputs. Its 114-file runtime digest is
`e78076103ffaf705b0ded8590ee22c80dedbd29dcd0768551c96d91db67cf61d`.
The diagnostic detects exactly frames 30–59 of a three-second guide-only gap.
The corrected 90-frame movie has zero encoded/source gaps. An unchanged repeat
reuses both scans and all 11 unique thumbnails, with zero new captures. Twelve
gallery entries share those thumbnails. The evaluator inspected the corrected
contact sheet: white process face, red edge, gray mechanism and adjacent guide.
The trace reads only the prompt, entrypoint, two compact references and its own
generated images. No acceptance fixtures, sibling skills or helper internals
were read. Its manual review correctly remains pending for a diagnostic fixture.

Final adapter run `line-world-vids-inventory-release-20261115` passes seven exact
outputs using its unchanged 18-file bundle digest
`59fae7da7776e99b5e369fa62c828ccee26e2c2a5e9c9707c562ea0c1f5ddff1`.
It checks stale/empty inventory observations and prepares a truthful UI handoff;
the isolated run does not claim a native account operation.

Reproduce the primary command with `scripts/run-pi-skill-eval.py
line-world-video --prompt-file evaluations/pi-prompts/line-world-content-contrast-contract.md
--mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium`
and all eleven paths declared by that prompt as repeated `--expect-output`.
Use the retained manifest for the exact invocation. Summarize both event traces
with `scripts/summarize-pi-json-events.py <events> --require-model gpt-6.1-sol
--fail-on-invalid-json --fail-on-tool-error`.

Retain earlier attempts without relabeling them as passes: the initial preflight
needed a reference contents list; `line-world-content-contrast-final-20261115`
failed strict tool gating because source scene records lacked `start` during
combined findings serialization. The actual helper defect was fixed and a CLI
regression added. `line-world-content-palette-release-20261115` retained an
agent-side wrong report-key assertion error; report paths were documented and
the prompt clarified. Earlier `content-contrast-release`, `content-schema-release`
and `vids-content` runs passed their then-current bundles, but are not substitutes
for the final red-outline payload. An initial starter guard that counted blank
panel borders/unrevealed paths was rejected and corrected.

## Final encoded evidence and limits

The native download SHA-256 is
`db2939106aa95461cf8ca621fb8a2922f1d9af7b78e41995f36ef4dfd87f974f`.
The caption-free delivery SHA-256 is
`6ce267121fef869e4f0dbef8d0fbe840f4c6fde3086159485839c228a527bdb1`.
The latter is a container stream copy, with identical video/audio streams and
decoded PCM; only the optional default subtitle track is omitted.

Both preserve 1920×1080, 6099 frames and 203.313923 seconds. Full decode passes,
all 53 encoded guide arrivals pass, and the ten retained voice-reference windows
have correlation at least 0.9933177768. The measured mux difference against the
frame budget is 0.0472563 seconds. All seven portrait/logo crops pass, and all
25 input-matrix cells retain the nine dark/sixteen light pattern.

The new project-specific emphasis verifier checks all 53 source cue poses and
75 actual encoded white faces. The final movie passes; the retained pink film
fails all 75 faces across 25 cue checks. It excludes photo pixels. This catches
an old same-name upload without treating photographic skin colors as a style
defect. The earlier tint-flattened data matrix is retained as a negative too.

Presence gates prove conservative pixel/source coverage, not narrative quality
or useful information in every object. Native observations alone cannot prove
same-name media bytes. Source sampling is finite, and retained-audio correlation
does not claim fresh human listening. The broader generated-layout generality
limit remains open, so the primary skill stays `validating`.

The final complete review has zero insufficient-content frames, zero source
empty intervals, zero guide events and zero advisories. The operator inspected
all ten current encoded contact sheets, native replacement previews and the
overview; its per-scene notes bind the actual movie/source hashes. The final
`deliveryReady` value is true. The unchanged attested repeat reuses all 249
thumbnails and both scans, capturing zero new images.

## Repository handoff

Pattern IDs (1348), independence and payload gates pass. Global structure and
the standard local sync remain blocked by four existing, unrelated semantic
reference-route findings in curate-semantic-model, extract-ontologies and
extract-with-ontology. Both changed bundles pass scoped validation and were
refreshed with the bounded repository sync helper: 114/18 files verified,
10/0 copied. Other work is preserved. No new Pages example was published.

The final source-bound visual review and clean editable-ZIP rebuild are recorded
in the project's `artifacts/reviews/content-after/summary.json` and
`artifacts/reviews/source-bundle.json`; see the [project minutes](../../projects/cuda-alexnet-vids/content-and-color.md)
for exact reproduction commands and the current video links.

The final editable ZIP clean extraction/rebuild passes: 3002 manifest-bound
files, all payload hashes match, the rebuilt runtime reuses all ten clips,
all ten source scenes pass their browser audit, and the portable gallery loads
all 249 samples and seeks the actual movie at 170.866667 seconds. The archive is
103,206,760 bytes with SHA-256
`ffdf98bc7547f9264dddd4bd30caf9d6454c59fac2957391e3b748826e3ca371`.
The package adds its own manifest as entry 3003. `git diff --check` passes;
preexisting line-ending notices do not modify unrelated work.
