# CUDA/AlexNet visual review — November 15, 2026

This is the archived 0.11.0 review. Read [the current content/color revision](content-and-color.md)
for the latest delivery. Its old movie remains under `artifacts/baseline-content-coverage/`.

The current ten-scene film was revised and exported again through its existing
[Google Vids project](https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit).
The delivery is `artifacts/videos/cuda-alexnet-final.mp4`, 1920 by 1080,
nominal 30 fps, 6099 frames and 203.313923 seconds. The separate original
Google Vids download is retained beside it. The clean delivery only omits
Google's optional default subtitle track through verified container stream copy.

## Findings and corrections

| Initial finding | Applied correction |
| --- | --- |
| 28 grouped guide/figure/text findings across travel and pans | Protect all meaningful rectangles, circles, portraits and labels; route neighboring scenes in world coordinates and retain the clear route inside the moving camera. |
| Related Mermaid labels rendered at different sizes | Use one shared fit scale for both native Mermaid lanes, preserving their geometry and complete labels. |
| CUDA media too close to the top edge | Move the portrait/logo row down and leave 50 pixels of headroom. |
| First convolution rectangle only 5 pixels from the divider | Move the full-width divider to leave 30 pixels of separation. |
| Small ImageNet schematic qualifier | Increase the qualifier from 23 to 26 pixels and improve its bottom inset. |
| Decorative red image strokes | Use quiet gray thumbnails, reserving red for the current semantic focus. |
| Secondary result's value changed to red on attention | Keep the second bar and 26.2 percent label dark gray; the adjacent guide stays primary red. |
| Missing opening icon links | Complete the small algorithms triangle. |

The 28 findings are grouped by affected scene/target, not 28 defective frames.
The baseline remains in `artifacts/baseline-visual-review/`. The baseline gallery
uses that retained old movie. `artifacts/reviews/visual-source/` is a development
check combining new source geometry with old movie samples and is not final
encoded-video evidence or part of the editable delivery archive.

## Final inspection and evidence

The final gallery is `artifacts/reviews/visual-after/index.html`. Operator
inspection covered all ten scene sheets and 248 encoded sample entries,
including openings, reading states, travel starts/midpoints, cue arrivals,
joins and the ending. The full-size learned-features, AlexNet and runner-up
frames were inspected separately. Quiet secondary strokes and partial objects
at the edge during intentional world pans remain deliberate. No visible title
banner was added. Essential names, values, units and schematic qualifiers remain.

- Complete decode: all 6099 movie frames, zero detected white/black blank frames.
- Source guide scan: 6098 poses at 30 fps, zero grouped collisions or clipping.
- Source reading/spacing checks: zero current advisories; repeat seeking passes.
- Actual encoded cue ports: 53/53 pass.
- Actual encoded portrait/logo crops: 7/7 pass; minimum pixel correlation 0.98808.
- Original Nyla voice: all ten independent reference windows pass, minimum
  correlation 0.9933177. Narration, word cues and scene extents were retained.
- Native UI: ten fresh scene selections, one video and one original voice per
  scene; export completed and no pending native action remains.

The operator notes in `artifacts/data/visual-review-notes.json` identify every
scene and bind the decisions to exact movie/source digests. The helper records
`manualReview: recorded` and `deliveryReady: true`. This records the actual visual
inspection, sampled source geometry and computational audio checks. It does not
claim independent human listening, continuous mathematical collision proof or
pixel-level equivalence for every source frame.

## Repeatable command and faster revisions

Run from the extracted editable project root:

```powershell
uv run --script resources/plugin/skills/line-world-video/scripts/review_video.py --video artifacts/videos/cuda-alexnet-final.mp4 --story story.json --timing artifacts/data/final-native-observed.json --cues artifacts/data/cues.json --html artifacts/composition/index.html --clock scene-local --manual-review artifacts/data/visual-review-notes.json --output artifacts/reviews/visual-after
```

The repeated final run reused all 248 movie samples and its unchanged source
audit, capturing zero new frames. Hashes are verified before reuse. On a new
movie or source change the old operator notes are rejected; inspect the new
results before recording new notes. Read `summary.json` first and use
`findings.json` to find affected scene/time intervals without reading the full
diagnostic report or hundreds of pictures into model context.

Keep visual styles in `theme.json`, local cue arrival/travel values in
`artifacts/data/cues.json`, and measured scene lengths in
`artifacts/data/final-native-observed.json`. The semantic editor can inspect and
patch a stable scene/cue ID, plan affected outputs and skip unchanged renders.
Source `clipSeconds` must still fit retained narration. A visual revision should
replace only changed native media and preserve unchanged speech. This pass
changed guide routes throughout the film, so all ten clips required replacement.

Current native SHA-256:
`8f23dceeabe76abd18e75d532484758faff75a27fccc9f5492d83c756e10a054`.
Current clean movie SHA-256:
`45c15f6e0e8626eada8462515a601553fd0b138ef49191ede55b0e9f74794c0e`.
Current source review SHA-256:
`226b2699d247c543b806a83f1aabc2d65fd0b6c4f1f567c7795a78321fe33304`.

## Current solid-surface review

The 0.14.2 source and current native export pass the complete ten-scene review:
249 encoded samples, 6,099 decoded content frames and 6,098 source guide poses.
There are zero detected guide events, reading advisories or empty intervals.
The operator inspected every scene sheet and recorded the current decisions in
`artifacts/data/content-review-notes.json`. The delivered MP4 preserves native
video/audio streams; voice correlation and source word-time limitations remain
explicit in the reports.
