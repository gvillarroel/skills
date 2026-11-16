# Speech-linked focus and reading clearance — 2026-11-15

Release 0.8.1 corrects the delivered Spanish ML video and promotes reusable
word-cue alignment, safe adjacent ports, short text-aware travel paths and real
SVG text/stroke diagnostics. Red remains #9e1b32. A second highlighted
comparison uses #696969; quiet areas remain pale gray. All five visual plugin
copies ship the same focus runtime and role mapping. Base palette tokens and
the general canonical D3/Mermaid/Iconify/HyperFrames skills are preserved.

## Delivered native film

The actual Google Vids project retained all twelve Nyla voiceovers and private
sharing. Selected native video objects were replaced using Replace video →
Upload. Scene selection, inserted revision filenames, twelve voice clips and
native millisecond scene announcements were observed. A stale helper file
reference temporarily put scene2's clip into scene3; replacing it with the
correct clip restored scene3 to 20.699 seconds and the total to 4:25.9 before
final export. Paths are now passed explicitly. This diagnostic is retained.

The extension uploader lacked file-URL access; the supported native Windows
picker completed uploads without changing that permission. The export click
completed despite a browser-tool timeout/reset. A fresh native observation
showed **Your video has exported** and **Download started**. The newly downloaded
file was copied read-only from Downloads into the project.

Final: `projects/ml-overfitting-vids/artifacts/videos/ml-overfitting-google-vids-revised.mp4`.
SHA-256: `63517dfaf6baf8e4b7ea0f2211df9aee85c61da92cf47b080b66f59e58b8f6a0`.
Native encoder tag: Google. Dimensions 1920×1080, nominal 30 fps, duration
265.914921 seconds, 7,977 decoded frames. No blank or black frames were found.
The 4,254,639 decoded mono16kHz voice samples are byte-identical to the approved
original. Native scene samples and the three percentage ports were inspected.
The secondary bar decodes near [103,103,103], consistent with lossy encoding of
the source [105,105,105].

The full film has 80 semantic cues. Actual ASR global starts 50.44, 51.34, 51.92
bind distinct 60%, first 20% and second 20% targets. Full-resolution native
frames at those starts+0.06 seconds confirm a red guide beside each percentage.
ASR boundaries remain approximate; no word-count estimate is called measured.
All eleven settled source reading frames pass text/text, text/frame and actual
stroke/text checks. Full post-pan guide trajectories and the final overview
have zero text collisions. Transit camera states retain separate visual review.
Source camera/guide join poses match exactly; tiny antialiasing differences use
an explicit mean-channel tolerance 0.01, rather than waiving pose discontinuity.

Commands:

```text
uv run --script projects/ml-overfitting-vids/scripts/prepare_revision.py
uv run --script projects/ml-overfitting-vids/scripts/build_visuals.py
uv run --script projects/ml-overfitting-vids/scripts/audit_revision.py
uv run --script projects/ml-overfitting-vids/scripts/render_clips.py
uv run --script projects/ml-overfitting-vids/scripts/verify_revision.py
uv run --script projects/ml-overfitting-vids/scripts/package_revision.py
```

The first render stopped at a strict antialiasing join check, then resumed at
scene6 after adding exact pose verification and a small raster tolerance. The
renderer evaluates the complete voice duration and reuses identical PNG states;
it no longer freezes after twelve seconds. The portable35-file source ZIP
rebuilds and audits after clean extraction. Its preview controls remain outside
the film. The final video was exported in Vids after replacing every visual.

## Runtime tests and isolated evidence

All 77 deterministic tests pass: original producer 29, adapter 32, word alignment 8
and focus/inspection8. New cases cover repeated numeric identities, unmatched
speech, invalid evidence, safe/impossible ports, label-aware paths, exact cue
arrivals, backward seeking, true stroke conflicts, clipping, a narrowly bounded
quantitative gray exception, and standalone inspection including rejection of a
guide covering text. The helper never edits the source HTML.

Fourteen actual strict pi runs are retained. Model is
`openai-codex/gpt-6.1-sol --thinking medium`, the existing per-run exception
because Spark is unavailable with this account. All exact outputs, payload
integrity checks, event JSON, observed models and read surfaces are recorded in
[the machine record](speech-focus-20261115.json).

- Initial primary contract passes. Initial primary naturalistic runs 1/2 fail
  strict mode for probing nonexistent `film/vendor`; run 3 passes. Artifacts
  remain retained. The skill now states the correct `assets/vendor` path and
  offers a standalone inspector without demo scaffolding.
- Final primary v2 contract passes and two of three fresh naturalistic runs
  pass strict mode. V2 run 1 retains a premature `focus-review.json` read error.
  Passing outputs have correct reference identity, colors, label clearance and
  deterministic seeking. One still uses an inset divider, so broader arbitrary
  composition acceptance is only 1/3; keep `line-world-video` **validating** for
  that generality. The delivered ML film uses full-frame dividers throughout.
- Adapter contract and three naturalistic cue preparations pass. A final
  exact-current-payload adapter contract also passes after promoting the native
  Replace video recovery recipe. Its alignment script is unchanged across that
  prose-only addition. Native UI/export proof is separate from offline pi.

Command families:

```text
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-speech-focus-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output contract.json --run-id 20261115-line-world-focus-final-contract
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-speech-focus-natural.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output figure.html --expect-output preview.png --expect-output focus-review.json --run-id 20261115-line-world-focus-v2-natural-<1|2|3>
uv run --script scripts/run-pi-skill-eval.py line-world-google-vids --prompt-file evaluations/pi-prompts/line-world-narration-cues-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output aligned.json --expect-output rejection.json --run-id 20261115-line-world-cues-final-contract
uv run --script scripts/run-pi-skill-eval.py line-world-google-vids --prompt-file evaluations/pi-prompts/line-world-narration-cues-natural.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output cues.json --expect-output handoff.md --run-id 20261115-line-world-cues-natural-<1|2|3>
```

Every trace is independently summarized with `summarize-pi-json-events.py
<events.jsonl> --require-model gpt-6.1-sol --fail-on-invalid-json
--fail-on-tool-error`. Failed traces remain failures. Final primary 100-file
payload is `0bcee838fde7f99fdd78aa447b7c95d62227754be9df16b4077ac6b19bed7b41`;
final adapter 16-file payload is
`5e9cf887ffd45cb19ebca8fa365832270bdf7ab7acfb1865e3b7776fda2e4592`.

## Final important-mark correction

Release 0.8.1 adds diagonal safe ports for a curve minimum crossed by a vertical
reference. The final strict current-source contract passes after that narrow
runtime/test change. The earlier v2 generative cohort remains separate evidence.
The source now reserves filled mark envelopes and sampled important strokes,
selects actual uncluttered points along fitted curves, and targets complete node
bounds. All 80 source cue arrivals equal their target ports exactly, and all
reading-scene landed ports clear important marks. The native export additionally
passes six object-port checks beside curves and outside nodes. Only nine native
clips needed this final replacement; scenes 3/6/10 retain identical semantic
poses and visible geometry. Approved PCM remains byte-identical. The original,
r2 movie and both versioned plugin archives remain preserved.

## Packaging and repository gates

The six-skill 266-file plugin archive, clean extracted starter, shared-runtime
hash equality, portable schema and all five task-local Codex installation
commands pass. This does not claim installation in the user's global host.
Focused local sync verifies 100 primary and 16 adapter canonical files.
Pattern IDs, independence and payload checks pass. The global validator/sync
retain the same four unrelated semantic reference-route findings recorded in
earlier releases; no unrelated source was changed to mask them.

```text
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/review_focus_release.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script projects/line-world-video/scripts/sync_local.py
```
