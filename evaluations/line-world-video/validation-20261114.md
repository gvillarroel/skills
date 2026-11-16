# Line World Video — November 14, 2026

## Scope and status

New skill and first dedicated plugin specification for the user's sparse
line-art video brief. Canonical skill: `skills/line-world-video/`. Project:
`projects/line-world-video/`. Status: **done**, release **0.1.1**. The primary
skill has 30 canonical files. The five-skill plugin contains 401 runtime files,
5,351,492 uncompressed bytes, excluding acceptance galleries and dependencies.

The editable acceptance film is 56 seconds, 1920×1080, 30 fps, with four
illustrative cycle-time records. A guiding point connects a particle/relationship
scene, a simple process island, paired comparison, shared-domain histories,
category partition and full-world overview. English source documentation and
video labels follow the repository language requirement.

## Executed evidence

| Check | Command / evidence | Result |
| --- | --- | --- |
| Builder | `uv run --script skills/line-world-video/scripts/line_world.py init --project projects/line-world-video/artifacts/film` and subsequent `build` | Pass: exact project, 56 s, 1,680 planned frames |
| Story invariants | `uv run --script skills/line-world-video/scripts/test_line_world.py` | 9/9 pass: contiguous timing, retiming, numeric validity, IDs, reading budget, history length, immutable inputs, palette reason, aspect ratio |
| Native HyperFrames | Generated project's `node scripts/hf.ts --version`, `lint`, `check --json --timeout 15000`, and `render --quality delivery --workers 1 --experimental-fast-capture=false --output <final.mp4>` | 0.8.111; lint/runtime/layout pass with zero errors and warnings; actual final render exits 0 after 1,680 screenshot-captured frames |
| Icons | Iconify exports `lucide:database`, `lucide:workflow`, `lucide:chart-no-axes-combined` | Real SVGs, receipts/hashes, and complete Lucide/Feather license retained |
| Mermaid source and import | Styler `--write`, then `--check --require-accessibility`; native render with `--config-file mermaid-config.json --css-file mermaid-line-art.css --animation none --require-accessibility` | Actual Mermaid SVG integrated into the final film. Top-level `htmlLabels: false` produces portable SVG text. Native line-art CSS preserves the explicit brief. Scoped `world-*` classes prevent compositor typography from clipping native labels. |
| Browser/vector audit | `uv run --script skills/line-world-video/scripts/render_line_world.py --project projects/line-world-video/artifacts/film --audit-only --report projects/line-world-video/artifacts/reviews/release-audit.json` | Pass: 19 states; visible source-value/focus agreement, truthful shared bar scales, focus paint, producer-label bounds, palette membership and repeat-seek determinism; zero findings |
| Isolated Spark | `run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-contract.md --mode json --strict --run-id 20261114-line-world-contract-spark ...` | Account/provider failure before tools: model unsupported with this ChatGPT account; no artifacts, retained failed run |
| Isolated final cohort | `run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-<case>.md --mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium --run-id 20261114-line-world-v3-<case>-sol-<n>` with every required exact artifact path | 8/8 strict passes: contract 1/1, naturalistic 3/3, generalization 3/3, boundary 1/1. Final current payload equals every tested read-only copy. Exact outputs, model, events, clean read surface and unchanged payload pass. |
| Independent case grading | `uv run --script evaluations/contracts/verify-line-world-runs.py --version v3` | 8/8 pass. Retimed 60-second red/neutral stories and three-record 35-second laboratory stories preserve exact units, values, histories and focus windows; four invalid-input cases reject without replacing valid timing. [Compact results](v3-results.json). |
| Metadata routing | `uv run --script evaluations/contracts/run-line-world-routing.py` and strict JSON trace summary | 12/12 semantic selections, including four positive style requests and eight controls. Original grade 10/12 retained: evaluator initially rejected JSON null for the two correct no-skill selections; corrected grading accepts null as none while still rejecting missing keys. |
| Real movie verification | `uv run --script projects/line-world-video/scripts/verify_delivery.py` | Full decode passes; H.264/yuv420p, 1920×1080, 30/1 fps, 1,680 frames, 56.000000 s, 8,308,925 bytes, no audio. All 14 decoded samples are nonblank; 56/111 half-second intervals show visible motion. Contact sheet and full-resolution hero frames inspected. |
| Preview controls | `uv run --script projects/line-world-video/scripts/verify_preview.py` | 9/9 checks: beat selection, seek, play/pause, pan, reset, controls excluded from film, mobile overflow, 44-pixel controls, no page errors |
| Short-beat completion | `uv run --script projects/line-world-video/scripts/verify_short_timing.py` | Cloud, relationships, category cells and overview fully revealed before shortened beat ends; overview camera settled. Default scene parity passes at 112 exact SVG/state timestamps. |
| Plugin package | `uv run --script projects/line-world-video/scripts/package_plugin.py` and fresh extracted browser audit | ZIP and marketplace pass; 401 file hashes retained; exact starter and full browser/vector audit succeed from the freshly extracted runtime |
| Native host install | `uv run --script projects/line-world-video/scripts/verify_plugin.py` | Codex 0.167.0: version, catalog add, available listing, plugin install and installed listing all exit 0 in a disposable project-owned home. All five cached skills match. Portable primary JSON schema validates with zero errors. No global account/UI installation is claimed. |
| Editable project | `uv run --script projects/line-world-video/scripts/package_demo.py` | 32-file project ZIP excludes caches, installed dependencies and absolute browser configuration. Freshly extracted rebuild exits 0 and reproduces exact timing. |
| Repository patterns | `uv run --script scripts/validate-pattern-ids.py` | Pass: 1,348 canonical item IDs at execution time |
| Independence | `uv run --script scripts/test-skill-independence.py` | Pass |
| Payload | `uv run --script scripts/check-repo-payload.py` | Pass |
| Repository validator | `uv run --script scripts/validate-skills.py` | Final rerun retains only four pre-existing semantic reference-route findings; the new colorset inventory omission is repaired. Scoped source/runtime/full checks all pass. |
| Local sync | `uv run --script scripts/sync-local-skills.py`, then focused `projects/line-world-video/scripts/sync_local.py` | Global sync refuses the four unrelated reference routes. Focused repository-helper sync verifies all 30 canonical/installed files; source and installed bundle validation pass. |

Bulky events and artifacts remain under `evaluations/runs/20261114-line-world-*`.
Trace summaries use `summarize-pi-json-events.py --require-model gpt-6.1-sol
--fail-on-invalid-json --fail-on-tool-error --require-tool-call --require-read
../prompt.md`, with acceptance-gallery reads forbidden. Final traces read the
entry point, compact task references and project-owned outputs, not vendor
bundles, acceptance galleries, sibling skills or repository documentation.

## Failure and recovery record

Browser screenshots timed out on both the scene and simple blank pages using
Chrome, Edge and an existing Chromium headless shell. Computed DOM/SVG export
and resvg 0.5.0 rendered the same seekable vector composition successfully.
Several graceful browser shutdowns also stalled. Intermediate cleanup through
browser-reported process IDs and a private transport handle was removed. The
final implementation uses the public `browser.close()` and runtime context;
fresh isolated audits, the native render and both extracted package tests pass.

Local command execution subsequently stopped acknowledging new commands,
including trivial PowerShell/cmd probes; Node runtime reset and workstation
control were unavailable. Previously completed tool-session output confirmed
the final audit pass. Filesystem patching and existing image inspection remained
available, so source documentation and the package builder were preserved.
The reason for that initial local execution failure is unconfirmed; temporal
proximity to browser cleanup is not proof of its cause. Execution subsequently
recovered and all task delivery work was completed.

The first native layout check found an annotation touching the history axis
caption and brief text overlap during chart crossfade. The annotation now has
its own vertical zone; the old chart fades out before the new chart enters.
The final native lint/runtime/layout check has zero errors and warnings.

Two initial generalization runs produced correct final artifacts after tool
errors from an undocumented `dataStatus` enum. Retain those strict failures;
the compact input-contract reference now gives the exact allowed values. The
V2 cohort passed 8/8. A later visual review found construction timing did not
scale with shortened opening beats. V3 normalizes those reveals and shortens
camera travel within the beat. Its separate final cohort passes 8/8; do not
pool earlier attempts into that score. The delivered default-duration film is
unchanged, verified by the 112-snapshot parity comparison.

The V3 artifact grader initially raised a KeyError on a valid alternate report
field name. The prompt did not prescribe that JSON field. The repaired grader
accepts both explicit timing-preservation representations, then regraded the
unchanged outputs. This was an evaluator repair, not a model retry.

## Scope and remaining repository findings

The starter is a 16:9 paired-value/history visual grammar with 2–8 nonnegative
rows. Other subjects and chart types require deliberate project adaptation.
The vector fallback covers SVG, not arbitrary canvas/WebGL/HTML captures.
The film is silent and illustrative. Native Codex catalog installation was
tested; global desktop activation, Claude UI and public distribution were not.

The four pre-existing global findings are direct-reference routes for
`schema-validation-review.md`, `premise-reuse.md`, `keyword-witnesses.md` and
`product-crawl.md` in unrelated semantic skills. Their existing worktree
changes were preserved. They do not affect this standalone bundle, extracted
plugin or verified movie.

Reusable patterns are in the skill's compact `references/pattern-recipes.md`.
No public gallery was added; there is no Pages publication or push claim.
