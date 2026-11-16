# Line World collection review, 0.26.0

This project maintains the current movie index and the review of earlier
standalone exports. `collection.json` declares eight current demonstrations and
29 reference files from the frozen initial inventory. Intermediate quality-pass
renders are local build output, not additional published deliveries.

## Current local movies

| Production | Movie | Duration | Audio |
| --- | --- | --- | --- |
| Machine learning and overfitting | [MP4](../ml-overfitting-vids/artifacts/videos/ml-overfitting-polished.mp4) | 265.867 s | Approved actual Google Vids voice; identical AAC payload |
| CUDA and AlexNet | [MP4](../cuda-alexnet-vids/artifacts/videos/cuda-alexnet-polished.mp4) | 220.667 s frame budget | Approved actual Google Vids voice; identical AAC payload |
| SEAL paper walkthrough | [MP4](../seal-paper-vids/artifacts/videos/seal-paper-polished.mp4) | 212.300 s | Approved actual Google Vids voice; identical AAC payload |
| Reddit navigation | [MP4](../reddit-navigation-video/artifacts/videos/reddit-navigation.mp4) | 104.867 s frame budget | Existing measured Edge speech |
| Linked data style | [MP4](../line-world-video/artifacts/videos/line-world-polished-linked.mp4) | 56 s | Intentionally silent |
| D3/Mermaid atlas | [MP4](../line-world-video/artifacts/videos/line-world-reviewed-atlas.mp4) | 185 s | Intentionally silent |
| Long focus motion | [MP4](../line-world-video/artifacts/focus-motion-demo/focus-motion-demo.mp4) | 9 s | Intentionally silent |
| Photographic color focus | [MP4](../line-world-video/artifacts/photo-focus-demo/photo-focus-demo.mp4) | 9 s | Intentionally silent |

Open the generated [collection index](artifacts/current/index.html) for exact
movie/source hashes, actual encoded frames and current/historical status.
These are local exports. Earlier native Google Vids projects/exports are
retained evidence; the native upload/export limitation has not been resolved
by a local render. No movie in this current index claims a native HyperFrames
render or a newly completed Google Vids export.

## Corrections promoted to the plugin

- Preserve full semantic reading holds in linked atlas views. Dividing every
  hold by guide visits previously made all 136 motion windows ineligible.
- Add the scene-local effect bridge and include real motion/fade state in PNG
  cache identities. Preserve static hold reuse when effects are inactive.
- Use reviewed original colors during 39 CUDA photograph focus bindings,
  with neutral entry/exit and identical crop/bounds. Keep hardware photographic.
- Increase portrait contribution captions to 26 px and remeasure line spacing.
  The first larger-type pass exposed an Ian Buck caption overlap; it was fixed.
- Route atlas guide and quantity flights around labels. Reserve internal travel
  lanes, shrink the guide while moving and keep all encoded quantities intact.
- Fit native diagram glyphs at 24 px, separate treemap name/value lines, move a
  colliding redundant axis unit, and space the native pie legend. Measure actual
  nested `tspan` glyph sizes instead of their empty parent text style.
- Keep paper emphasis outside source words/figures, increase source attribution
  to 24 px, and trace existing margin marks on the shared clock during long
  reading holds. Preserve the pinned PDF captures and calm camera pans.
- Distinguish harmless sparse SVG edge antialiasing from a real repeat-seek
  change using reported pixel bounds plus exact geometry/paint checks.
- Use a white inset trace on a thick primary-red stroke; a red trace inside the
  same thicker red mark had no visible motion.
- Force transparent animation-layer fill over imported Mermaid CSS. A producer
  node rule otherwise filled cloned rectangles, obscured text and made primary
  red appear pink. The source inspector now rejects opaque emphasis layers.
- Keep the linked full-frame category areas as white outlined groups, with
  readable red/gray labels. Preserve the exact proportional partition without
  turning the whole frame into solid color. Focus travels beside the value.
- Run collection reviews through each specialist's own UV environment, retain
  source-specific checks, reject stale operator notes and use bounded parallel
  jobs. Do not treat full paper/website captures as generic SVG obstacles.

Reddit retains its actual native light captures and measured narration. Its
rules and account shots intentionally use narrow interface regions; the white
space preserves the original interface rather than inventing extra controls.
Both independent feature demonstrations retain their existing movie bytes.

## Reproduce review and visual-only assembly

```powershell
uv run --script projects/line-world-quality-review/scripts/inventory.py
uv run --script projects/line-world-quality-review/scripts/assemble_review.py
uv run --script projects/line-world-quality-review/scripts/make_collection.py
uv run --script skills/line-world-video/scripts/review_collection.py --manifest projects/line-world-quality-review/collection.json --output projects/line-world-quality-review/artifacts/current --include-reference --jobs 3
```

The scanner writes `artifacts/inventory-current.json`; the versioned
`baseline-inventory.json` freezes the original reference set. Production
sources and renderer commands remain in their owning projects. Assembly checks
each scene frame budget, retains the two CUDA final hold frames protecting the
approved tail, copies the approved AAC packets and verifies their digest.
It does not synthesize speech or write to a cloud editor.

Machine review and actual visual decisions are separate. Hash-bound per-scene
notes live in local `artifacts/manual/`; the durable evaluation summary records
the final scope and any retained limitations.
`observations.json` freezes the 63 actual per-scene judgments. After verifying
their exact movie/source hashes, `scripts/apply_observations.py` can apply those
records to this review. It refuses changed media/sources; it cannot approve a
newer unseen movie automatically.
