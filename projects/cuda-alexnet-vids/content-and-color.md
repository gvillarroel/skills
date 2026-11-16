# Continuous content and vivid emphasis — November 15, 2026

This project uses the six-skill Line World Video 0.12.4 OpenAI-compatible plugin.
The native project is the existing private CUDA/AlexNet film. Spanish narration
is retained source material; these production notes are English.

## Actual empty scene

Fresh native inspection found eleven scene buttons while an old selected-scene
status still said ten. Selecting scene two produced a new announcement:
five seconds, zero objects and no audio clip starting. All ten expected MP4
scenes and original Nyla tracks remained in order around that inserted gap.
The native inventory in `artifacts/data/native-content-before.json` retains every
fresh announcement. Its check finds the count mismatch and the empty second
scene, with 208.262 seconds of announced total extent.

The proven empty scene was removed using the normal reversible Delete scene
action. All ten visual clips were replaced with the clearer emphasis style,
preserving original narration, measured cues and expected scene extents.
Fresh inventory now verifies ten scenes, zero empty visual scenes and 203.262
seconds at native announcement precision. The encoded delivery retains
203.313923 seconds and 6099 frames; rounding/mux duration is verified separately.
No new speech was generated and private sharing was unchanged.

## Color decisions

| Role | Rule |
| --- | --- |
| Guiding dot | Always primary red `#9e1b32`, with the existing travel/focus size changes. |
| Current object | Red text and a 3 px red contour on white. Never use pink object backgrounds. An explicit solid primary-red face uses white internal labels. |
| Existing data fills | Preserve every nonwhite fill, including unannotated grayscale image matrices and processor-core marks. |
| Secondary comparison | Keep `#696969` on the bar and value while the red guide visits it. |
| Essential neutral contours | Use `#828282` so the mechanism remains visible at delivery size. |
| Context and media | Keep quiet grays for supporting context; retain actual photographic pixels and complete brand artwork. |

The shared `LineWorldTheme.focus` helper restores original inline fill/stroke
values and CSS priorities after attention moves. It handles native Mermaid SVG
specificity, does not resize geometry and starts no independent animation.
The project preparer recompiles its owned theme JSON on each build, preventing
stale generated CSS from retaining an earlier emphasis rule.

An intermediate attention-fill attempt could flatten unannotated nonwhite data
cells. The final runtime preserves those fills; a browser regression covers a
nonwhite cell under the same focus group as an ordinary white face. The three
affected clips were rendered and replaced again. A subsequent user correction
removed the attention tint entirely: the current ten clips use white faces and
primary-red edges. All original values, matrix patterns, narration and scene
budgets remain intact. A stronger solid-red style is explicitly opt-in through
`data-focus-fill="solid"` and white internal labels through
`data-focus-on-fill="true"`. No pink background is generated.

## Three independent checks

1. `vids_inventory.py` checks fresh native scene count, ordered MP4 titles,
   object counts and extents. It rejects a stale announcement from another count.
2. Source review checks for an explanatory anchor throughout the camera route.
   Guide elements, dividers, blank panel boundaries and completely unrevealed
   dashed paths do not count. A visible observation field can be an aggregate.
3. `content_scan.py` decodes every constant-rate movie frame to 640×360. Its
   white-field profile requires non-background ink and extent in both dimensions.
   The actual thresholds and exact failing intervals are retained in the report.

These are conservative presence checks, not a requirement to decorate intentional
whitespace. Keep real outgoing or incoming context in view. Do not hide every
object until a camera move has finished or add meaningless marks to pass a gate.
The linked and atlas starter renderers run the guards automatically. Their old
opening/reveal/fade gaps have dedicated baseline/current integration evidence.

## Repeatable review

Run from the editable project's extracted root:

```powershell
uv run --script resources/plugin/skills/line-world-google-vids/scripts/vids_inventory.py --story story.json --observed artifacts/data/native-content-after.json --output artifacts/reviews/native-content-after.json
uv run --script resources/plugin/skills/line-world-video/scripts/review_video.py --video artifacts/videos/cuda-alexnet-final.mp4 --story story.json --timing artifacts/data/final-native-observed.json --cues artifacts/data/cues.json --html artifacts/composition/index.html --clock scene-local --manual-review artifacts/data/content-review-notes.json --output artifacts/reviews/content-after
```

The native inventory command evaluates retained observations; it does not operate
an account. The final gallery and per-scene notes bind inspection to the actual
movie/source digests. Read its compact `summary.json` first. Its 249 entries
include scene/cue samples and the least-content frame. Unchanged repeats reuse
verified thumbnails and the source/content scans rather than doing those jobs
again. Exact delivery digests and stream parity are in
`artifacts/manifests/delivery.json` and `artifacts/reviews/delivery-parity.json`.

The prior 0.11.0 movie and source snapshots remain in
`artifacts/baseline-content-coverage/`; the archived visual gallery points to
that old movie. Mixed old-movie/new-source development reports are not final
encoded evidence and are excluded from the editable delivery archive.

## Final red-outline verification

The final native download contains 6099 frames at 1920×1080 and lasts
203.313923 seconds. The caption-free stream copy preserves video/audio bytes
and decoded PCM, omitting only the optional default subtitle stream.

- Native SHA-256: `db2939106aa95461cf8ca621fb8a2922f1d9af7b78e41995f36ef4dfd87f974f`.
- Delivery SHA-256: `6ce267121fef869e4f0dbef8d0fbe840f4c6fde3086159485839c228a527bdb1`.
- Full encoded/source review: zero insufficient-content frames, zero empty
  source intervals, zero guide events and zero spacing/type advisories.
- All 53 encoded guide arrivals, all 25 input-matrix cells and all seven media
  crops pass. Ten retained voice-reference windows correlate at least 0.9933177768;
  this is computational verification, not a new human listening claim.
- `scripts/verify_emphasis.py` checks all 53 source cue poses and 75 encoded
  white faces. Current output passes all 75; the retained pink export fails all
  75 across 25 cue checks. Photographic pixels are excluded from that color gate.
- All ten current encoded contact sheets were visually inspected. The explicit
  per-scene record binds this review to the movie/source digests. The last review
  is `deliveryReady: true`, reusing all 249 thumbnails and both unchanged scans
  with zero captures.

Use `scripts/verify_emphasis.py --video artifacts/videos/cuda-alexnet-google-vids-final.mp4
--output artifacts/reviews/red-outline-after.json` for the project-specific
encoded color regression. The general bundled palette audit additionally rejects
pink geometric surfaces and translucent red composited over white. A valid
white-face result does not replace visual review or the content-presence gate.

The native proof is `artifacts/screenshots/google-vids-red-outline.jpg`.
The editable Vids project remains
[CUDA and AlexNet](https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit).

## Current solid-surface revision: 0.14.2

The current film uses borderless gray individual bodies and primary-red active
bodies with white internal labels. Group shells retain white interiors and
discreet gray/red outlines. The white/gray/red composition remains qualitative;
there are no pixel-area quotas or pink object backgrounds. Quantitative matrix
fills, the dark-gray second comparison, portraits and brand artwork are preserved.

All ten native Vids clips were replaced with the prepared files and freshly
inventoried. The downloaded native movie is 203.313923 seconds and 6,099 frames.
The caption-free final file copies its video/audio streams without re-encoding.
Current review: `artifacts/reviews/content-after/summary.json`, 249 encoded
samples, zero guide events, zero empty intervals and hash-bound manual notes.
The color verifier now checks solid bodies and white labels; its outline-film
negative control fails 582 body comparisons across 57 poses. Final current film
passes 1,292 body comparisons, 31 white-label checks, 53 encoded guide arrivals,
25 matrix cells and seven contributor/logo crops.

`verify_emphasis.py` now performs this source/encoded solid-body comparison.
Its previous white-face implementation is retained under the outline baseline.
A new shared-runtime version conservatively invalidates old local render-cache
fingerprints; the portable source checker reports that state instead of marking
those old clips as newly rendered. The actual native delivery is independently
verified. Project sources include the six-skill 0.14.2 plugin.
