# HyperFrames Explainer Validation — 2026-10-02

Status: done. The final frozen candidate passes the release thresholds: contract
1/1, naturalistic 3/3 joint, generalization 2/3 joint, boundary 1/1, and unforced
metadata routing 12/12. All 43 recorded attempts remain in the aggregate, including
strict failures that produced correct media.

The bundle creates minimal educational HyperFrames movies and interactive previews.
One initiating event updates a dominant mechanism and complementary measurements or
history through one pure state function and one seekable clock. Colorset1 is the
default. Colorset2 requires an explicit request or a documented semantic need.
Direct labels, values and units stay in the film; controls, claims, assumptions and
verification evidence stay outside it.

Canonical source: [SKILL.md](../../skills/hyperframes-explainer/SKILL.md).
All recorded attempts, model observations, hashes, read paths, strict gates and
independent findings are preserved in [results-20261002.json](results-20261002.json).
Raw run folders remain under ignored `evaluations/runs/`; project media, dependency
caches and screenshots remain under ignored `projects/hyperframes-explainer/artifacts/`.

## Frozen release candidate

The runtime payload contains 21 files, excluding the acceptance fixture and all
dependency/build folders. Its SHA-256 is
`6cd060d1b2b3293a877426cdf48c78b5d930882687466eb6b3a7520cdc4e4cb6`.
Each run copies only this skill, forbids ambient context and discovery, verifies
the first prompt read and observed model, rejects tool errors and outside/sibling
reads, checks exact artifacts, and proves the copied skill remained unchanged.

Spark was attempted first in
`20261002-hyperframes-explainer-contract-spark-1`; the provider rejected
`gpt-5.3-codex-spark` for the configured ChatGPT account before any tool call.
The deliberate exceptions recorded in `SKILLS.md` are
`openai-codex/gpt-5.6-luna` for initial development and metadata routing, and
`openai-codex/gpt-5.6-sol` for the final release cohorts. Sol is available in the
local Pi model catalog. The model exception changes no isolation, zero-error,
exact-output or artifact criteria.

| Case | Exact expectation | Frozen runs | Required joint outcome | Observed outcome |
| --- | --- | --- | --- | --- |
| Command contract | Supplied preflight/build commands; five exact preview outputs | `release-contract-sol-2` | 1/1 strict and independent | 1/1; working browser stage and independent analytic values pass |
| Naturalistic | 40-unit allocation, A 32 to 12 and B 8 to 28, one event and linked histories, colorset1 | `release-naturalistic-sol-6`, `-7`, `-8` | At least 2/3 strict, independent and manual | 3/3 joint passes |
| Generalization | Vehicle speed 2 to 6 m/s, accumulated distance 36 m at 8 s, colorset2 | `release-generalization-sol-6`, `-7`, `-8` | At least 2/3 strict, independent and manual | 2/3 joint passes; all three independent artifacts pass |
| Boundary | Preserve R domain 0–10 ohm; reject undefined exact 12/R at zero; no film | `release-boundary-sol-2` | 1/1 strict and independent | 1/1; exact model/domain retained and no MP4 or finished preview |
| Unforced routing | Twelve requests across seven descriptions and no-skill controls | `routing-luna-2` | Correct intended and neighboring routes | 12/12 metadata selections passed |

Run IDs in the table have the prefix `20261002-hyperframes-explainer-`.
The routing trial loads no forced skill. It tests description-based selection,
not native Codex discovery or a particular model family's certification.

## Deterministic and native evidence

- All 36 bundled deterministic tests pass: analytic integration of ramps and steps,
  source/derived dependency closure, legal control boundaries, conservation,
  palette choice and effective paint, undefined expressions, exact outputs,
  overwrite protection, safe JSON patching, malformed JSON diagnostics and pure seeks.
- The two Full HD acceptance movies use the native HyperFrames renderer, not a
  substituted encoder pipeline. Both native checks report zero lint/runtime/motion
  errors or warnings and zero layout findings. Contrast checks pass 25/25 for
  colorset1 and 45/45 for colorset2.
- Browser audits pass 92 time/input scenarios per fixture, 184 total, including
  reverse seeks, Python-versus-JavaScript state comparisons, visible geometry and
  text bindings, domains, actual computed paint, clipping, labels and preview
  parameter input/reset events.
- Each movie passes exact dimensions/rate/frame-count checks and a complete FFmpeg
  decode. Movie-derived contact sheets and full-resolution screenshots were
  inspected for sparse labels, readable supporting views and stable entity colors.
  Both examples are intentionally silent.

| Local movie under `projects/hyperframes-explainer/artifacts/videos/` | Media | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `colorset1-flow-v2.mp4` | 16 s, 1920×1080, 30 fps, 480 frames, H.264/yuv420p | 1,035,575 | `1ea1bb7f016dfbafddb9435ec28d6c9d1c2330c8632e54cba50c294ed2457466` |
| `colorset2-exchange-v2.mp4` | 12 s, 1920×1080, 30 fps, 360 frames, H.264/yuv420p | 1,134,094 | `f625fe8337381fba35e3919bf6361b173b2b950194e1e757cc344a53747ad3b2` |

Fixtures have editable projects at `artifacts/projects/cs1-final/` and
`artifacts/projects/cs2-final/`; reports are at `artifacts/reviews/cs1-v2-audit.json`,
`cs2-v2-audit.json`, `cs1-v2-media.json` and `cs2-v2-media.json`.
Interactive previews require HTTP serving; their controls are outside the filmed
stage. The browser audit starts and stops its own local server.
Verified runtime versions: HyperFrames 0.8.111, GSAP 3.14.2,
puppeteer-core 25.12.0, Node.js 24.18.0, Chrome 154 and FFmpeg 8.1.1.

Final repository checks pass: pattern IDs, skill metadata/resource validation,
skill independence, repository payload, all 15 Pi harness tests and scoped diff
whitespace checks. Local sync/check passes for all 10,118 canonical source files;
the new skill's 22 full-bundle files individually match their installed copies.
Git ignore checks confirm both example MP4s and all raw evaluation movies are
excluded from versioned source. The backlog and getting-started catalog mark the
skill done only after the frozen release gates passed.

## Independent acceptance

The evaluator-owned
[case grader](../contracts/validate-hyperframes-explainer-case.ts) checks actual
browser labels and geometric changes against separately calculated expectations.
It does not use the skill's oracle or expression engine to derive expected numbers.
It also probes and fully decodes the MP4, verifies reverse-seek reproducibility,
and captures a browser screenshot. An explicit evaluator runtime supplies
puppeteer-core when an agent removes its local installation after rendering.

Naturalistic expected values include `(A,B) = (32,8), (22,18), (12,28)` at
0/2, 3.5 and 5/8 seconds. Generalization expected distances are 0, 4, 7, 12 and
36 m at 0, 2, 3, 4 and 8 seconds. Final manual inspection must also confirm that
the initiating event has readable consequences in two distinct visible views.

The initial independent label matcher incorrectly treated `A + B` as an A-only
readout in two older trials. It was repaired to distinguish exclusive entity labels
from aggregates. Original reports were retained as
`independent-before-label-fix.json`; corrected reports do not change the strict
agent outcomes or the frozen payload. A third matcher correction associates a
separate numerical readout with its unambiguous adjacent A/B label using actual
DOM bounds; the first report remains as `independent-before-separated-label-fix.json`.
The contract asset check was also corrected to the actual `assets/vendor/` and
`assets/fonts/` paths, retaining `independent-before-asset-path-fix.json`.
These are verifier corrections; no agent tool error was relabeled as a success.

## Development failures and promoted repairs

All attempts remain in the aggregate, including correct media from strict failures.
Common agent failures were ambiguous text edits to repeated JSON fields, invented
paint-role names, wrong working directories, uninstalled browser-package probes,
reading beyond a small report's end and running native checks before layout repair.
One older generalization artifact lacked the public runtime API required by the
skill. These failures are not omitted or counted as strict successes.

In the final frozen generalization cohort, run `-6` passes the independent movie
and numerical checks but fails strict execution: an unnecessary browser lookup
returns a shell error, and three custom preview probes time out while seeking the
stage API on the parent preview window. The API belongs to the filmed iframe.
The bundled audit already checks actual preview input/reset propagation and is the
documented default path. Runs `-7` and `-8` follow a successful path and pass strict,
independent and manual review. The cohort therefore passes 2/3, not 3/3.

The reusable repairs are in the skill: ID-based validated JSON patches, explicit
paint-role keys, commands callable from the workspace root, output-path normalization,
owned-project refresh, expected authoring findings reported without tool failures,
the supplied browser audit before native checks, and small report inspection.
The conserved-exchange fixture also prompted a direct-label rounding rule so
independent rounding cannot suggest a changing conserved total.

The first contract attempt used a non-command code fence and failed the harness's
exact-command extraction. The prompt was repaired to use a bash fence, with that
attempt retained. Two source-gate aborts occurred before Pi or run-directory
creation when the expanded scene reference lacked a contents list; the reference
was repaired before the fresh frozen cohorts. One older Luna run exceeded 900 s:
the Windows command wrapper timed out while its uniquely identified owned Pi
child held stdout open. That expired child was stopped and the timeout was
retained as a harness failure. Other processes were not terminated.

## Reproduction

From the repository root, the final naturalistic/generalization command is:

```powershell
uv run --script scripts/run-pi-skill-eval.py hyperframes-explainer `
  --prompt-file evaluations/pi-prompts/hyperframes-explainer-<case>.md `
  --model openai-codex/gpt-5.6-sol --mode json --strict `
  --run-id 20261002-hyperframes-explainer-release-<case>-sol-<n> `
  --timeout-seconds 900 `
  --expect-output out/video.mp4 --expect-output out/project/index.html `
  --expect-output out/project/preview.html --expect-output out/project/manifest.json `
  --expect-output out/project/brief.json --expect-output out/audit.json `
  --expect-output out/media.json --expect-output out/contact.jpg `
  --expect-output-json-field out/audit.json::ok=true `
  --expect-output-json-field out/media.json::ok=true
```

Use cases `naturalistic` and `generalization`, fresh repetitions `6`, `7`, `8`.
Run the independent grader with the case, the run's `workspace`, its
`independent.json` output, and optional evaluator dependency project.
The contract adds `--require-exact-command-from-prompt`; the boundary requires
`out/preflight.json::ok=false` and `out/diagnosis.json::requiresModelDecision=true`.
Every run manifest preserves the complete exact command and required outputs.

```powershell
uv run --script skills/hyperframes-explainer/scripts/test_explainer.py --work-dir projects/hyperframes-explainer/artifacts/data/tests
uv run --script evaluations/contracts/run-hyperframes-explainer-routing.py --run-id <fresh-routing-id>
uv run --script evaluations/contracts/summarize-hyperframes-explainer.py --output evaluations/hyperframes-explainer/results-20261002.json
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

## Limits

The film tests use illustrative allocation, accumulation and conservation models,
not experimentally validated physical systems. Preflight samples legal boundaries
and event times; it is not a symbolic proof over every arbitrary interior input.
The primitive builder is intentionally small; custom mechanisms must preserve the
public API and extend audit coverage. Silent movies and interactive previews are
covered; the optional audio branch has no isolated release case here. Structural
and media validation cannot prove viewer comprehension. No public gallery or Pages
publication is claimed for these local examples.
