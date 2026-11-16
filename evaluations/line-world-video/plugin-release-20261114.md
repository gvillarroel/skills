# Line World Video 0.4.1 release evidence

Validated November 14, 2026 in the repository's Windows environment. This release
implements complete frame divisions, a 16-scene comparison atlas, and dedicated
D3, Mermaid, Iconify and HyperFrames video copies. Original general skill
sources are preserved. The actual video finish is patched into the Mermaid
copy, including CSS-defined event backgrounds. The D3 copy adds a bounded
table/comparison builder, browser exporter and dependency-aware UV delegation.

## Current evidence

| Check | Outcome |
| --- | --- |
| Source/timing/partition/SVG import unit tests | 22/22 |
| Atlas browser audit | 34 states; zero findings and zero small-label warnings |
| Native HyperFrames checks | Lint, runtime, layout, motion and contrast pass; one reviewed warning |
| Final MP4 full decode | Pass: 1920×1080, 30 fps, H.264/YUV420p, 185 s, 5,550 frames, silent |
| Preview | 13 checks pass, including seeking, play/pause, section selection, drag/reset, explicit context, mobile controls and warning review |
| Primary strict isolated release cohort | 8/8: contract 1, naturalistic 3, generalization 3, boundary 1 |
| Final dedicated D3 verification | 3/3 strict plus independent artifact grading |
| Native Mermaid timeline | 1/1 strict; native geometry, metadata and neutral event paths verified |
| Iconify source exports | 1/1 strict; provider SVGs, receipts and full license text |
| HyperFrames producer verification | Two fresh strict/independent runs pass; an earlier diagnostic failure is retained |
| Unforced metadata routing | 14/14 |
| Standalone materialized bundle validation | All five skills pass |
| Isolated native Codex installation | Five commands exit 0; all five dedicated names discovered |
| Editable ZIP clean rebuild | Pass; exact timing matches |
| Local source/installation parity | 87 canonical files |
| Pattern IDs, independence tests and eligible payload | Pass |

The [combined report](plugin-v041-results.json) retains sixteen current-source
observations: fifteen strict/independent successes and the earlier HyperFrames
diagnostic failure. The primary eight-run cohort is the formal release cohort.
Producer smokes are separate integration evidence, not a claim that every
derivative completed a full eight-case study. Two fresh HyperFrames checks were
scheduled after its diagnostic; they are not a prospectively planned pooled
three-run cohort.

The model is `openai-codex/gpt-6.1-sol`, medium thinking: the recorded exception
after Spark's retained account rejection. Strict observed-model, valid JSON,
zero tool-error, exact-output, read-surface and unchanged-payload gates remain
enabled. Primary IDs start with `20261114-line-world-v041-`. D3 uses the
`line-world-profiles-v041` materialized source cohort. The earlier Mermaid,
Iconify and HyperFrames copied payloads match the current package byte-for-byte;
the independent grader verifies those matches.

## Reproduction

Run the following from the repository root; native launcher commands run inside
`projects/line-world-video/artifacts/atlas`.

```text
uv run --script skills/line-world-video/scripts/test_line_world.py
uv run --script skills/line-world-video/scripts/render_line_world.py --project projects/line-world-video/artifacts/atlas --audit-only --capture browser --report projects/line-world-video/artifacts/reviews/atlas-032-audit.json
node scripts/hf.ts lint
node scripts/hf.ts check --json --timeout 15000
node scripts/hf.ts render --quality delivery --workers 1 --experimental-fast-capture=false --output ../videos/line-world-atlas-final.mp4
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/package_demo.py --film projects/line-world-video/artifacts/atlas
uv run --script projects/line-world-video/scripts/verify_atlas_preview.py
uv run --script projects/line-world-video/scripts/verify_delivery.py --video projects/line-world-video/artifacts/videos/line-world-atlas-final.mp4 --story projects/line-world-video/artifacts/atlas/story.json --label atlas-final-decoded
uv run --script evaluations/contracts/verify-line-world-plugin-runs.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script projects/line-world-video/scripts/sync_local.py
```

Each primary test uses the repository Pi helper, matching prompt, explicit run
ID, `--model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict`,
and every requested `--expect-output`. The
[producer wrapper](../../projects/line-world-video/scripts/run_profile_eval.py)
redirects only source/run roots and preserves the unchanged strict harness.
The grader summarizes each trace with the model/JSON/tool-error gates, checks
exact values and timing, and proves current resource fingerprints. Raw events,
screenshots and artifacts remain under `evaluations/runs/`.

Project evidence includes `atlas-032-audit.json`, `atlas-032-native-check.json`,
`atlas-final-native-render.log`, `atlas-final-decoded-verification.json`,
`atlas-preview-check.json`, `rotation-warning-review.json`, versioned package
checks and `manifests/release-0.4.1.json` under the project's `artifacts/` folder.
See the [pairing review](atlas-pairings-20261114.md),
[initial release](validation-20261114.md) and
[earlier clean-layout release](clean-layout-20261114.md).

## Retained findings and limits

The native warning concerns fixed Mermaid axis labels traveling with the world
camera. Browser checks prove their own transforms remain unchanged while the
camera moves; the warning remains in the native report. Five atlas grammars
needed invisible metadata repair, distinguished in receipts from successful
native directive support. The atlas fixture is fixed to its native illustrative
data; new data must regenerate those assets or use the linked-data starter.
Pairing judgments are editorial and include intentionally redundant controls.

Earlier diagnostics retain native grammar limits, legend collisions, D3 label
bounds, a prototype global-name collision and Python missing Playwright. The
bounded starter, UV delegation, neutral finish and legend-spacing rules address
these transferable issues. The early HyperFrames probe repaired its final
artifacts after a missing default browser and a label-bound failure, so its
strict trace remains failed. A producer-source copy race occurred before Pi
launched; the wrapper now locks preparation and preserves the prelaunch log.

Full-repository validation and global sync retain four unrelated reference-route
findings in `schema-validation-review.md`, `premise-reuse.md`,
`keyword-witnesses.md` and `product-crawl.md` in semantic skills. Scoped bundle
validation and focused local synchronization pass. Earlier candidates and movies
remain separate from final delivery.
