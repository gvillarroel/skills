Current visual review (0.26.0): [seal-paper-polished.mp4](artifacts/videos/seal-paper-polished.mp4). See the [collection review](../line-world-quality-review/review.md) for exact delivery identity and current validation. This is a local visual revision with the approved Google Vids AAC voice preserved; earlier native export records below remain historical evidence.

# SEAL paper walkthrough

This example explains the actual paper **Self-Adapting Language Models** by Adam
Zweiger, Jyothish Pari, Han Guo, Ekin Akyürek, Yoon Kim and Pulkit Agrawal. Source:
[arXiv:2506.10943v2](https://arxiv.org/abs/2506.10943v2), revised September 18, 2025,
licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The original PDF pages remain the visual evidence. Added material consists of
Spanish explanation, red focus overlays, camera moves and two derived bar views.
Original figure colors and typography are preserved. The film has no added title
card; the opening is a capture of the paper's own title and abstract. Source PDF
SHA-256: `3abf83bcf05862d5e6e72078dc0e47ebfcf2e72866e9fdfe1dbc3663c72a9dc6`.

## Delivered files and provenance

- `artifacts/videos/seal-google-vids-final.mp4`: current complete native Google
  Vids export, 1920x1080, approximately 207.96 seconds and 6,238 frames.
- [Watch or download the MP4 in Drive](https://drive.google.com/file/d/14QqiYhYFqT1bLxN9ZgWlJYJdIKJmp02-/view):
  verified playback and enabled download in the owner's existing account.
- `artifacts/videos/seal-paper-final.mp4`: retained 207.9-second local comparison
  render, 6,237 frames, using the same visuals and native voice source.
- `artifacts/composition/index.html`: offline editable preview with play and seek.
- `story.json`: exact Spanish scripts, original-page rectangles, semantic targets,
  derived values, measured cues, camera choices and native-scene shot changes.
- `artifacts/composition/timing.json`: frame-rounded visual scene clock.
- `artifacts/data/native-timing.json`: original measured Google Vids voice-scene
  clock, 207.802 seconds, before frame rounding.
- `artifacts/data/transcript.json` and `aligned-cues.json`: approximate independent
  ASR word evidence from the native export and 36 resolved visual references.
- `artifacts/reviews/delivery.json`, `encoded-review.json`, `encoded-content.json`
  and `visual-decisions.json`: actual output identity and review evidence.

[Completed Google Vids project](https://docs.google.com/videos/d/1xE-nlSa3WwpO0CggajlAYQA09OnymGae2ch7l2DcpPA/edit)
contains six exact scripts, their original voice tracks and six verified visual
clips. Each scene has one video object and its retained narration. Native
File > Export to Drive produced the playable MP4 in the Vids Exports folder;
File > Download > MP4 produced the complete 17,119,832-byte local export.
The Drive file remains restricted to its existing owner.

An earlier browser URL-verification stop left a voice-only draft. The follow-up
used normal visible UI actions and the native file picker after safely activating
the correct tab. No extension permissions, sharing permissions, alternate
browser transport or credentials changed. Native completion evidence is in
`artifacts/reviews/native-inventory.json`, `native-drive-export.json`,
`native-encoded-review.json` and `native-content.json`; actual editor/player
screenshots are under `artifacts/screenshots/`.

In the retained local comparison render, all decoded native voice samples are retained exactly in the intermediate WAV,
with only silence inserted at the six frame-rounded scene boundaries. The final
MP4 encodes that WAV to AAC; do not claim byte-identical final AAC audio or a
native audio bitstream parity from that local receipt. The current native visual
export is verified separately.

## Paper route

| Scene | Original evidence | Explanation |
| --- | --- | --- |
| `method` | Page 1 title/abstract; Figure 1, page 2 | Candidate self-edits, temporary model updates, evaluation and the outer learning loop |
| `knowledge` | Figure 2, page 5 | Passage to generated training material to a LoRA update and no-passage evaluation |
| `few-shot` | Figure 3, page 5 | ARC demonstrations, augmentation choices, training settings and held-out input |
| `arc-table` | Table 1, page 7; experimental scope on page 6 | Four rates and the selected eight-task evaluation limit |
| `knowledge-table` | Table 2, page 8 | All 15 values, three settings and the reversal of the GPT-4.1 comparison |
| `limits` | Figure 6, page 8; two paragraphs on page 9 | Forgetting, computational overhead and dependence on reference tasks |

Important interpretations: the ARC rate counts successful self-edits on a small
selected subset; it is not full ARC accuracy. The 47.0 versus 46.3 comparison is
0.7 percentage points, with no statistical-superiority claim. SEAL falls behind
the GPT-4.1 synthetic-data comparison in both continued-pretraining settings.
The paper does not establish unlimited continual learning or absence of forgetting.

## Change timing without rewriting geometry

Edit `story.json`, then rebuild the composition. Keep `scenes[].id`, target IDs,
and row IDs stable. All `at` values are scene-local seconds.

- `scenes[].duration` controls the complete scene budget. Round to an integer
  number of frames at `fps`. Keep the full spoken ending and a reading hold.
- `scenes[].cues[].at` controls guide arrival at the spoken reference. Source
  phrases and ASR timestamps are retained alongside each cue. If narration
  changes, obtain new word timings rather than stretching the old cue schedule.
- `scenes[].shots[].at` switches between original pages/regions within the same
  voice track. Each interval needs a cue. Keep a little lead time for its 0.65 s
  visual handoff. The final scene visits the page-9 cost and evaluation paragraphs
  and returns to the forgetting figure.
- `cameraZoom: false` preserves a stable figure and its axes. The default paper
  camera enters once, then pans at a fixed scale. The 0.17.0 revision uses a
  maximum 1.3 scale, 2.6-second entry, two-second preferred pans and reading holds.
  It keeps the overview when densely spaced narration cannot support a slow pan.
- `emphasis: "margin"` uses short exterior segments, checked against words,
  source bodies and original raster pixels. No closed rectangular overlay is
  drawn. The guide remains active if no clear margin can accept a mark.
- The two page-9 limitations now share one stable view. Their separate spoken
  cues move the guide between paragraphs without changing crop or scale.
- `avoid` protects complete raster figure bodies. Keep the guide beside the
  heatmap, including its unselected cells, axes and labels.
- A cue's `row`, `column` and optional `guide: "chart"` connect an original cell
  to the matching derived bar. Preserve column units and all source numbers.

From an extracted source bundle:

```text
uv run --script tools/line-world-video/scripts/paper_video.py build --project artifacts/composition --story story.json
uv run --script tools/line-world-video/scripts/paper_video.py audit --project artifacts/composition --report artifacts/reviews/new-audit.json --poster artifacts/images/new-poster.png --poster-scene knowledge-table --poster-at 26
uv run --script tools/line-world-video/scripts/paper_video.py render --project artifacts/composition --output artifacts/videos/clips --report artifacts/reviews/new-render.json
uv run --script scripts/finish_video.py
uv run --script scripts/review_delivery.py
```

Use repeated `--scene stable-id` flags for a bounded visual revision. If the last
pose of a scene changes, also render its immediate successor, whose opening
crossfade references that pose. Ordinary reading holds reuse a captured image.
`inspect` and `locate` provide bounded source text/coordinates without custom
extraction code. The bundled tools do not automate a signed-in browser.

## Validation scope

Review the final encoded movie and the source separately. Automated checks cover
every encoded frame's visible content, every source frame's guide/text/body
clearance, 36 encoded guide arrivals and all 19 table values. Extractable PDF
words do not cover raster typography; actual diagram crops, focus borders, joins
and the linked views were also inspected visually. Original embedded raster
diagrams retain the resolution of the paper, including at close-up scale.

The source archive includes the original PDF, captured pages, editable composition,
the actual voice reference, clips, final MP4, attribution, relevant utilities and
the OpenAI/Codex-compatible plugin. It does not include the ASR model weights.
