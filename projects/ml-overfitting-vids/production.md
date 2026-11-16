# Native Google Vids ML explainer

The requested Spanish narration is source material for the film. Production
documentation is English. The film has no automatic visible titles. Primary
red is `#9e1b32`; the second highlighted comparison uses `#696969` and quiet
marks use pale grays on white. The revised final MP4 is an actual Google Vids
export. Its decoded voice samples are byte-identical to the approved original.

## Editable timing

`story.json` is the single project input. Each scene has an exact script, stable
ID, visual brief, source clip path, `clipSeconds` and `essentialAnimationSeconds`.
The `motion` object controls camera travel (`panSeconds`, 0.65 seconds) and final
world zoom (`overviewSeconds`, 2 seconds). `artifacts/revision/cues.json` controls
80 semantic focus arrivals from the actual approved voice's ASR word times.
Each cue has an editable scene-local `at`, stable `target` and `travelSeconds`.
Travel normally lasts 0.28 seconds and starts before the spoken word. The point
arrives beside its target, shrinks in transit, briefly grows to radius14 and
settles at radius10. Adjust those radii in the project focus options or bundled
focus.js defaults, then recheck clearance using the maximum radius/keyline.

To shorten the film, edit the narration first and regenerate that scene's native
voice in Vids. Measure the resulting duration before changing the visual hold.
To slow camera motion, increase `panSeconds` or `overviewSeconds`; recheck that
the target is visible before its reference. To change point speed, edit each
cue's `travelSeconds` (0.1–0.45 seconds) while keeping `at` bound to speech.
Do not shift a spoken cue merely to accommodate a decorative path. Do not speed speech
automatically. Native scene selection announcements expose milliseconds with
screen-reader support enabled; the ordinary timer rounds to tenths. Ceil visual
coverage to the next 30 fps frame and extend only the final held image.

The five corrections in `artifacts/handoff/frame-repair.json` record this
conversion. Voice duration fields are explicitly conservative bounds from the
native scene extent where isolated waveform duration is unavailable.

Rebuild local assets from this project root:

```powershell
uv run --script scripts/train_demo.py
uv run --script scripts/build_visuals.py
uv run --script scripts/render_clips.py
```

The portable source package already includes the measured experiment, local
runtime and cue file, so rebuilding visuals does not require retraining. To
realign new narration, use the installed plugin's `narration_cues.py` with its
word transcript, measured scene timing and semantic cue spec. Preserve separate
occurrences for repeated values. The current percentages occur at global
50.44, 51.34 and 51.92 seconds; ASR word boundaries remain approximate.

Serve this folder locally and open `artifacts/composition/preview.html` for the
silent editable preview with scene selection, scrub and playback. Those controls
are outside the film. The final voiced movie is delivered separately.

The renderer uses an isolated local browser for authored HTML and exports each
scene at 1920 by 1080, 30 fps. It never connects to a signed-in browser.
`renderAt(sceneIndex, localSeconds)` is deterministic and seekable. Camera
endpoints share one world; a scene starts at its predecessor's final pose.
Small antialiasing differences have an explicit audit tolerance. Generated
files remain under artifacts/. Replace the corresponding video object in its
existing Vids scene, preserve its voiceover, and recheck duration and order.
The playhead and selected insertion scene can differ. Local rebuilds do not
update an existing native export; download a new complete MP4 after changes.

The renderer evaluates the full scene duration and reuses PNG bytes only when
the complete camera/guide state is unchanged. It keeps late narration cues
active. `essentialAnimationSeconds` and `staticHoldAfterSeconds` follow the last
required cue rather than an early fixed freeze. Reading-frame checks include
text/text, text/frame and actual stroke/text intersections. The largest guide
envelope is checked throughout every post-pan scene and overview. Inspect
camera transit states separately; source geometry checks do not prove audio.

The plugin's line-world-google-vids helper compiles observed timings and checks
the downloaded MP4. Evidence stays under artifacts/handoff/ and artifacts/reviews/.
An automated transcript provides independent content/order evidence and is
labeled separately from listening.

## Measured experiment and schematic views

The seeded synthetic regression uses 240 observations from 120 entities with
group-disjoint 60/20/20 partitions. Preprocessing stays inside five-fold grouped
cross-validation. A limited training-only search covers 20 degree/regularization
combinations. The selected configuration is degree 3 and Ridge alpha 0.3.
The independent test opens once after freezing choices and refitting development.

Validation MSE: mean baseline 0.9561; selected pipeline 0.0686. Final test MSE:
0.05845. A percentile 95% interval, approximately 0.036 to 0.088, bootstraps
entities from fixed-model held-out errors. It is conditional on this fitted
model and sampled entities; it does not include all selection or future drift
uncertainty. Early stopping and production monitoring are explicitly schematic.
The film does not claim zero overfitting.

Technical sources:

- [Scikit-learn: leakage](https://scikit-learn.org/stable/common_pitfalls.html)
- [Scikit-learn: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Google ML: overfitting](https://developers.google.com/machine-learning/crash-course/overfitting/overfitting)
- [Google ML: regularization](https://developers.google.com/machine-learning/crash-course/overfitting/regularization)
- [Google Vids: voiceovers](https://support.google.com/docs/answer/15070345?hl=en)
- [Google Vids: timing](https://support.google.com/docs/answer/14960797?hl=en)

## Solid-surface revision, plugin 0.14.2

Use borderless gray individual bodies and primary-red active bodies with white
internal labels. Keep grouping shells white with discreet outlines. The current
caption-free native delivery is `artifacts/videos/ml-overfitting-solid-final.mp4`;
its audio and video streams are copied directly from the retained Vids download.
All 7,977 frames pass content presence. Complete guide trajectories, including
pans and the affine summary zoom, pass the source audit. Eleven concise concept
labels replace miniature copy during the final overview; full-size reading shots
preserve all values and qualifiers. Native voice PCM is byte-identical to the
approved original. See `artifacts/revision/solid-review-final/summary.json` and
`artifacts/revision/solid-review-notes.json` for current hash-bound review.
