# Whole-film visual review — November 15, 2026

Release: Line World Video **0.11.0**, a portable OpenAI plugin with six coordinated
skills and the Codex compatibility manifest. Canonical behavior changes belong
to `skills/line-world-video/`. This qualifies the bounded review, camera-route
and current film revision; the broader generated-layout limitation remains open.

## Reusable behavior

`scripts/review_video.py` combines full encoded decode/blank-frame statistics,
batched exact-frame samples, scene contact sheets, a seekable gallery, source
reading checks and guide trajectory checks at 30 fps. It reports source geometry
separately from actual encoded-pixel evidence. Timestamped findings are grouped
by scene/target with contiguous intervals. The compact summary is the first
runtime read. A balanced FFmpeg selection expression supports hundreds of
samples without excessive expression-parser depth.

The movie cache keys verified thumbnail bytes by video SHA-256 and frame index.
The source cache covers local HTML, scripts, styles, data, media and fonts,
diagnostic runtimes, scene clocks and declared external inputs. Corrupt frames
are rebuilt. Separate-output guards protect authored sources and skill resources.
Explicit per-scene operator notes must match current movie/source hashes before
`deliveryReady` can become true. A machine pass leaves manual review pending.

`LineWorldFocus.visibleAlong` clips a clear world route against the current
camera bounds, retaining an eligible point on the route instead of clamping the
point off its safe path. The compact speech/review references describe combined
neighboring-scene geometry, figure obstacles and an inset for the guide radius.
All five visual producer copies ship the same focus runtime. No helper silently
operates Google Vids or creates new speech observations.

## Tests and retained development evidence

- `uv run --script skills/line-world-video/scripts/test_focus.py`: 10/10 pass,
  including moving-camera route projection and rejection of an unavailable path.
- `uv run --script skills/line-world-video/scripts/test_review_video.py`: 5/5 pass.
  Real FFmpeg fixtures exercise more than 200 select terms, a transit-only
  collision between clear endpoints, corrected routing, repeat/cache behavior,
  corruption recovery, exact-hash manual gates, unsafe/duplicate scene IDs and
  authored-source protection. Temporary files remain under the caller workspace.
- Early development retained an unbalanced FFmpeg select expression failure.
  A balanced expression resolves it; the large-selection regression test passes.
- Initial production diagnostics found 28 grouped guide/text/figure events and
  four spacing/type advisories missed by the earlier arrival-only audit. World
  routing fixed crossings; one remaining camera-edge clipping sample led to
  `visibleAlong`. No obstacle was ignored merely to obtain a pass.
- Strict isolated runtime-only Pi contract
  `line-world-visual-review-20261115` passes all ten exact outputs, valid event
  JSON, zero tool errors and unchanged skill payload. Command:
  `uv run --script scripts/run-pi-skill-eval.py line-world-video --run-id line-world-visual-review-20261115 --prompt-file evaluations/pi-prompts/line-world-visual-review-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict`,
  plus `--expect-output` for each of these exact paths (also retained in the run
  manifest): `film/fixture.mp4`, `film/story.json`, `film/cues.json`,
  `film/source/index.html`, `film/before.json`, `film/after.json`, `film/notes.md`,
  `film/review/report.json`, `film/review/findings.json`, `film/review/index.html`.
  The observed model is Sol, the previously recorded account exception because
  Spark is unavailable; this is not reported as a Spark run.
- Independent event/read-surface inspection passes. The agent reads its prompt,
  the primary skill, five compact references, the review helper implementation
  and its own task artifacts. It reads no acceptance examples, sibling skills,
  repository documentation or project media. The helper source is read twice
  (about 21 KB per read), a remaining context-efficiency opportunity; it is below
  the large-gallery threshold and directly related to the diagnostic contract.
- The isolated fixture decodes 90 frames, detects two intended transit findings,
  fixes the source path, then reports zero findings and reuses all 11 existing
  thumbnails with zero new captures. Its static FFmpeg movie is explicitly a
  decoding fixture and does not depict the separately authored source path.
  Manual review remains pending there. No production or speech claim is made.
- Final read-only runtime payload digest in the isolated run:
  `126e76c0bb9e21dbfc2941305933d1d811b8b98750a458403069f1489e1bbf3e`.
  Bulky runtime evidence remains under ignored `evaluations/runs/`.

## Actual CUDA/AlexNet film

The [project review](../../projects/cuda-alexnet-vids/visual-review.md) records
all corrections and exact commands. All ten revised clips were rendered and
uploaded via the normal native Replace video / Upload / Windows Open path.
Fresh selection of scenes 1–10 verified media IDs, unchanged extents, one video
object and one original Nyla voice each. The existing private Google Vids
project exported and downloaded successfully; no speech was regenerated.

The final clean film is 1920 by 1080, nominal 30 fps, 6099 frames,
203.313923 seconds. Complete decode and frame statistics detect no white/black
blank frames. All 53 actual encoded cue ports pass. Seven actual encoded
portrait/logo regions pass (minimum correlation 0.98808). Ten original-voice
windows pass (minimum correlation 0.9933177). Subtitle removal preserves the
exact compressed video/audio payloads and decoded PCM. Native actions pending: 0.

The final whole-film review samples 248 encoded entries and 6098 source poses
at 30 fps, with zero guide findings or reading advisories. Operator inspection
covered all ten contact sheets, native overview and three full-size frames.
Per-scene notes are bound to the current hashes. The repeated final review
reuses all 248 frames and its source audit, capturing zero new frames. It records
`manualReview: recorded` and `deliveryReady: true`. These are explicit sampled
visual and computational audio claims; no new human listening or exhaustive
pixel-equivalence claim is made.

- Original native export SHA-256:
  `8f23dceeabe76abd18e75d532484758faff75a27fccc9f5492d83c756e10a054`.
- Clean delivery SHA-256:
  `45c15f6e0e8626eada8462515a601553fd0b138ef49191ede55b0e9f74794c0e`.
- Current reviewed source SHA-256:
  `226b2699d247c543b806a83f1aabc2d65fd0b6c4f1f567c7795a78321fe33304`.

## Portable package and repository gates

`package_plugin.py` creates the immutable 0.11.0 plugin and marketplace archives,
286 files, 5,052,389 unpacked payload bytes. Portable ZIP SHA-256:
`157f5ac4021aabe800d7925a39956f8f2769b5ad0e37c8a9da48b34fa8d54046`.
Fresh extracted smoke passes. `verify_openai_package.py` verifies both archives,
portable schema, Codex manifest, canonical parity, native local marketplace
installation and all six app-server skill names. Five installed test runners
pass: focus, semantic editing, full-film review, media assets and narration cues.
No global plugin configuration was changed.

Pattern IDs, independence and payload checks pass. The global skill validator
and standard local synchronization retain four unrelated pre-existing reference
route findings: curate-semantic-model/schema-validation-review,
extract-ontologies/premise-reuse and extract-with-ontology/keyword-witnesses plus
product-crawl. Focused validation passes for both Line World canonical bundles.
Using the existing sync helper's bounded file selection, eight changed files
were copied to the ignored local installation; all 128 source-owned hashes and
both installed bundles pass. No unrelated source was changed to clear the gate.

The editable project archive includes the exact 0.11.0 runtime, project sources,
native/clean movies, measured cues, before/after review evidence and retained
baseline movies. The intermediate mixed old-movie/new-source development review
is excluded. Rebuild-verifier reports are external to the archive to avoid
including a stale report about a preceding ZIP. The current verifier binds its
result to the actual ZIP digest, verifies every file, rebuilds the source using
only the bundled plugin and reuses all ten unchanged scene clips. Its browser
check opens the portable review, loads all 248 images and seeks the decoded
movie to the secondary-result cue at 170.866667 seconds without page errors.
The first gallery test used a plain HTTP preview fixture and timed out on video
seeking; opening the standalone review directly, as delivered, resolves it.
The complete preview also passes all ten scene options. Final clean extraction/rebuild evidence lives in the project's
`artifacts/reviews/source-bundle.json`; its archive digest is in
`artifacts/packages/package.json`. Generated media and bulky evidence stay out
of git. No new published gallery or Pages pattern was added in this pass.

Final editable ZIP: 65,747,670 bytes, 1457 hash-listed files plus its manifest,
SHA-256 `9cff0ffa7cb8679089c55caeeac91ea49427e3940ee7292590727ca398ea2025`.
The final clean extraction passes against that exact digest, all ten cached
clips, ten preview scenes, all 248 gallery images and the decoded seek check.
