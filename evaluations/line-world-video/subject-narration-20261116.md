# Subject-focused narration revision

Date: November 16, 2026 UTC (November 15 local). Release: Line World 0.20.1.
Keep `line-world-video` validating for the previously recorded broad-generation
limits. The Vids adapter's established done status is unchanged; the new complete
native film deliveries are pending an external browser-upload permission.

## Editorial outcome

Review all 28 current scripts: CUDA/AlexNet 10, overfitting 12 and SEAL 6.
Rewrite six scenes: CUDA `parallel-work` and `alexnet-model`, overfitting
`early-stopping`, SEAL `method`, `few-shot` and `arc-table`.

Remove narration about animation fidelity, simplified drawings, the guiding dot
and a chart repeating table rows. Explain thread/block work, feature learning,
validation behavior, adaptation and the 52.5 percentage-point ARC comparison.
Preserve the selected eight-task scope, the actual metric denominator,
independent final testing, ensemble context, forgetting and the absence of a
universal guarantee. Leave brief original-paper navigation in place.

The reusable `references/narration.md` and `scripts/narration_review.py` now
provide an editorial workflow, advisory English/Spanish candidates and a
stable-ID list of changed voices. No lexical scan certifies semantic quality.
The primary, shared producer contract and native adapter route this behavior
before speech generation. The native workflow now requires actual script-glyph
focus, verification of text versus canvas pastes, resolved Windows paths,
picker closure and a real document change before advancing uploads.

## Deterministic and native package checks

```powershell
uv run --script skills/line-world-video/scripts/test_narration_review.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

All eight new tests and all 17 installed utility suites pass. Portable schema,
task-local Codex installation, six native skill registrations, exact package
bytes and canonical source parity pass. Primary runtime payload: 131 files;
adapter: 22 files. Six-skill release: 315 declared files. Preserve immutable
0.20.0 development and 0.20.1 qualified archives separately.

## Isolated runtime validation

Model exception remains `openai-codex/gpt-6.1-sol`, medium thinking, because the
account does not provide Spark. Runtime-only copied bundles, exact outputs,
JSON strict mode, observed model, zero event tool errors and unchanged skill
payloads pass in all five runs:

| Run ID | Editorial outcome |
| --- | --- |
| `20261116-subject-narration-contract-sol` | Strict harness passes; editorial partial failure retains an unnecessary speed disclaimer. Preserve this diagnostic. |
| `20261116-subject-narration-natural-sol-1` | Pass; explanatory scripts retain visible synthetic provenance and substantive scientific limits. |
| `20261116-subject-narration-contract-final-sol` | Pass after explicitly distinguishing a functional mechanism from a measured speed comparison. |
| `20261116-subject-narration-natural-final-sol` | Pass with current primary instructions. |
| `20261116-subject-narration-vids-sol` | Pass; exact handoff file explains script focus, partial voice regeneration, measured timing and upload-permission boundaries without inventing receipts. |

Prompts live in `evaluations/pi-prompts/line-world-subject-narration.md`,
`line-world-subject-narration-natural.md` and
`line-world-vids-subject-revision.md`. Commands use:

```text
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-subject-narration.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-subject-narration-contract-final-sol --expect-output revised-story.json --expect-output narration-review.json --expect-output editorial-notes.md
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-subject-narration-natural.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-subject-narration-natural-final-sol --expect-output story.json --expect-output review.md
uv run --script scripts/run-pi-skill-eval.py line-world-google-vids --prompt-file evaluations/pi-prompts/line-world-vids-subject-revision.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-subject-narration-vids-sol --expect-output handoff/revision.json
```

## Actual film work and limitations

All six affected Nyla voices were regenerated in the existing Google Vids
projects, exported as actual native reference movies and independently
transcribed with the existing faster-whisper base model. Actual scene extents
drive revised cue alignment and frame budgets. Unaffected ML/SEAL local cues
were retained after voice-timing correlation, with explicit evidence; this is
not a byte-identity claim. Full-band AAC phase differences initially rejected
an unchanged ML window. The final timing check uses an 800 Hz low-pass sampled
at 16 kHz, without reducing its correlation or offset thresholds.

| Local movie | Video frames | Duration | Review |
| --- | --- | --- | --- |
| CUDA/AlexNet | 6,618 | 220.6 s | Source trajectory and actual encoded coverage pass; six caption-size advisories inspected. All six people/context observations pass. |
| Overfitting | 7,976 | 265.8667 s | Source trajectory and actual encoded coverage pass; no advisories. |
| SEAL | 6,369 | 212.3 s | Original-paper source audit passes; encoded coverage and manual review pass. |

All 20,963 decoded frames retain meaningful content. Hash-bound manual records
cover the reading montages of all 28 scenes and full-size revised examples.
CUDA/ML generic source trajectory review has zero guide issues. SEAL uses its
paper-specific audit: the generic `#guide` inspector is incompatible with its
generated overlay, and the retained failed diagnostic must not be treated as a
paper-render failure. The subsequent encoded-only review and original-paper
audit cover their respective actual surfaces.

Local outputs are `*-subject-first-local.mp4`, assembled locally with actual
Google Vids speech. They are **not complete native final exports**. Actual Vids
scripts/voices are saved. Only the corrected Windows upload of CUDA scene 6 was
confirmed: its native duration became 30.867 seconds. Earlier forward-slash
picker attempts did not replace clips; retained labels and an unchanged edit
timestamp exposed the failure. Do not count those attempts as uploads.

The documented browser file-chooser flow then explicitly rejected file access,
requesting Chrome extension "Allow access to file URLs". Report that setting,
request user status, and do not broaden extension permissions or route around
the rejection. Native assembly/export remains pending. The actual native voice
reference Drive files are source evidence, not final deliveries. Resume from
each project's `artifacts/revisions/subject-first-0200/resume.json`.

Each current source archive includes the six-skill runtime, visuals, exact
scripts/cues, actual voice reference, local MP4, explicit provenance and a
standalone `rebuild.py`. SHA inventory and clean rebuild pass for the qualified
`*-subject-sources-0.20.1-r3.zip` archives. Preserve the first missing-template
package failure and the r2 development archives rather than overwriting them.

## Repository gates

Pattern IDs, skill independence and payload checks pass. Global validation and
global sync retain exactly four pre-existing unrelated reference-route findings
in the semantic skills. The bounded sync verifies 131 primary and 22 adapter
canonical files. No unrelated source is modified to hide those findings.

```text
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script projects/line-world-video/scripts/sync_local.py
uv run --script projects/line-world-video/scripts/package_subject_sources.py
```
