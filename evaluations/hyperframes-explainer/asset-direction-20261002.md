# HyperFrames Asset Direction — 2026-10-02

Status: validating. This revision responds to weak diagram assets in the first
HyperFrames examples. It keeps the minimal typography and synchronized numerical
model, but selects visual producers before assembling the video.

## Production choice

A read-only inventory of repository-local and personal installed skill roots
found 62 entries and 56 distinct names. The current session's plugin skill catalog
was also considered. The detailed local inventory is retained under the ignored
project review artifacts. Selection is based on what each explanatory moment
needs, rather than the number of tools available.

| Moment or representation | Applied capability | Result |
| --- | --- | --- |
| Identify the controlled inlet | `svg-brief-design` | Original valve body, wheel, stem, channel, reservoir cutaway, feet and capacity ruler |
| Follow the transported quantity | `procedural-svg-animation` | Tracers driven by the analytic accumulated-volume phase; no reset on a rate change |
| Compare input and consequence over time | `d3` | Fixed linear scales, ticks and axes computed with D3 7.9.0; synchronized curves are bound by the HyperFrames kernel |
| Connect the representations | `hyperframes-explainer` | One source, analytic integral, numeric hooks and a single seekable GSAP clock |

The selection guide also routes meaningful depth to Three.js, typed topology to
Mermaid/PlantUML, verified technical identity to icon/logo skills, real appearance
to appropriate media/3D asset searches, and complex composition to the installed
composition skills. These are optional capabilities. Normal standalone runtime
does not depend on sibling skills, galleries or repository artifacts.

The procedural catalog was inspected with `--list` and the motion-follow pattern
with `--describe procedural-svg-motion-follow`. Its native SMIL clock is unsuitable
for an interactive inflow integral. The applied variant uses deterministic indexed
tracers on the inlet path and a canonical volume-derived phase; it follows the
skill's shared-clock composition guidance without importing an autonomous loop.

## Changes promoted into the skill

- Mandatory asset direction before primitive assembly: viewer question, event
  moments, producer, source/state contract, ports, bounds and provenance.
- Subject recognition and actual causal encodings as visual acceptance criteria.
  Minimalism removes redundant labels and decoration rather than useful structure.
- A flattened SVG importer with exact palette checks, stable shape/group selectors,
  explicit bindings and source hashes. All expanded marks enter the existing
  state, input, geometry, contrast and seek audits.
- A blank view-sized scaffold that emits a plan-relative source path. It preserves
  an existing matching plan, creates only its missing SVG, and cannot pass import
  without actual geometry. Mismatched plans and existing SVGs remain untouched.
- Relative offsets for named SVG groups, preserving initial pose and coherent
  motion of all parts. Individual path hooks keep their real rotation pivots.
- Ellipse support and positive-period modulo. A transport phase uses the integral
  of rate rather than current rate multiplied by total elapsed time.
- Common-canvas semantic groups for continuous scenes, while partial panel overlaps
  remain invalid. Actual bounds, collisions, label readability and object contacts
  still require browser/native/manual review.
- A text-anchor compatibility normalization and actionable mojibake findings.
- A deterministic `init` command for nonnegative rate/integral models. It creates
  the requested numerical brief and an adaptive landscape layout before SVG
  scaffolding, with fixed domains and explicit assumptions. It supplies no
  mechanism artwork. This addresses missing-brief probes and malformed nested
  JSON without suppressing tool errors or relaxing any release criterion.
- Explicit geometric recipes for calibrated fills, graduated rulers, clockwise
  SVG rolling, real road contact and neutral mechanical context.
- Expected project-exists and stale-asset guard reports remain `ok:false` without
  a tool infrastructure error; they never overwrite authored work. Require one
  validation gate per tool call, reimport after SVG edits and `--refresh` after
  changes to an owned generated project.

## Delivered production examples

Both directed examples are 1920 × 1080, 30 fps, 16 seconds, H.264/yuv420p. The
preferred colorset1 uses neutral mechanics and red for the controlled fluid.
The explicit colorset2 demonstration uses red for control/rate and blue for
transported/stored fluid. There are no film titles or title cards.

Local artifact locations:

```text
projects/hyperframes-explainer/artifacts/directed/colorset1/
projects/hyperframes-explainer/artifacts/directed/colorset2/
projects/hyperframes-explainer/artifacts/videos/directed-colorset1-final.mp4
projects/hyperframes-explainer/artifacts/videos/directed-colorset2-final.mp4
projects/hyperframes-explainer/artifacts/reviews/directed-cs1-final-media.json
projects/hyperframes-explainer/artifacts/reviews/directed-cs2-final-media.json
```

Each imports four assets, passes 92 browser scenarios, native lint/runtime/layout/
motion checks with zero errors and warnings, and 105/105 contrast checks. Both
movies fully decode and satisfy the exact duration/frame contract. Composed
stills, event contact sheets and final readouts were inspected. A draft native
pivot warning was resolved by representing the butterfly gate with bound
endpoints and an explicit bearing rather than a path mistaken for a dial pointer.

The model is illustrative: imposed inflow, no outflow, constant cross-section and
80 L capacity. Tracers show qualitative transport; the stored amount is the exact
integral. Geometry is not a measured hydraulic law. These assumptions are outside
the film in the source brief/manifest.

## Validation protocol

Development uses `gpt-6.1-sol`; forward tests use `openai-codex/gpt-6-luna`, following
the user's explicit preference. Failed Luna trials are not replaced by Sol passes.
The global Pi 0.84.2 catalog omitted the current model. A project-local descriptor
registers the actual gpt-6-luna ID with the built-in Codex provider. The upstream
CLI requests that ID, and strict event traces verify the observed model. Existing
credentials are read into memory; runtime settings/catalog files remain inside
the ignored project runtime directory.

Two cases use an isolated runtime payload without acceptance fixtures: a controlled
inlet in colorset1 and a changing-speed vehicle in explicit colorset2. Each case
requires original editable vector art, an asset plan, actual state hooks, a
retained SVG source hash, a real preview, native checks and an exact eight-second
960 × 540, 12 fps MP4. Each frozen release cohort needs at least two joint strict,
independent and manual passes out of three fresh workspaces.
The final initializer cohort retains all three attempts per case; its first
samples use medium reasoning and its remaining samples use high reasoning. This
is a recorded execution-setting change, not a model substitution or a relaxed
validator. Every attempt remains in the denominator and carries its actual setting.

The independent evaluator checks the piecewise integral at forward/backward times,
actual DOM geometry changes across views, driven imported art, zero/max input
counterfactuals, real preview reset, retained source hashes and the actual video
stream/frame contract with complete FFmpeg decode. Manual review checks subject
recognition, calibration, contacts, motion meaning, labels and encoding.

An early evaluator compared maximum input against a baseline already at that same
rate and incorrectly missed a driven wheel. It now compares the genuinely changed
zero input against the baseline before separately testing maximum accumulation.
That correction does not turn any failed strict trace into a pass.

## Commands

```powershell
uv run --script skills/hyperframes-explainer/scripts/test_explainer.py --work-dir projects/hyperframes-explainer/artifacts/reviews/contract-tests-final
uv run --script skills/hyperframes-explainer/scripts/test_asset_import.py --work-dir projects/hyperframes-explainer/artifacts/reviews/motion-tests-final
node projects/hyperframes-explainer/scripts/build-directed-demo.ts
node evaluations/contracts/validate-hyperframes-assets.ts evaluations/runs/<run-id> projects/hyperframes-explainer/artifacts/projects/cs1-final
node evaluations/contracts/validate-hyperframes-assets.ts evaluations/runs/<vehicle-run-id> projects/hyperframes-explainer/artifacts/projects/cs1-final vehicle
uv run --script evaluations/contracts/summarize-hyperframes-assets.py --output evaluations/hyperframes-explainer/asset-direction-results-20261002.json
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
```

The deterministic suites pass 45 state/contract tests and 23 asset tests. Detailed
Pi commands, exact output assertions, payload hashes, trace findings and results
are retained in each run's manifest/command files and the adjacent compact results
JSON. All actual attempts, including failed drafts, remain in the record.

## Current limitations

The custom 3D/raster route and optional audio are documented but are not release
claims from this revision. The isolated tests exercise the self-contained vector
fallback, not app-native skill discovery or every companion skill. Choosing a
specialist from metadata does not by itself validate that specialist's output.

Runtime authoring defects in the development trials included duplicated source
paths, stale SVG assembly, ambiguous rotation attributes, full-canvas semantic
group handling, lost initial pose, unnecessary failed shell/edit probes, and
malformed text. The compact record distinguishes these failures from independent
evaluator corrections and from successfully encoded media.

Before the initializer revision, 27 genuine Luna 6 attempts produced five strict
trace passes and two joint passes on different older payloads. Neither older
payload met the two-of-three release gate after independent and manual review.
The last pre-initializer frozen cohort had one of three strict inlet passes and
zero of three strict vehicle passes; both had zero joint passes. Missing required
ruler geometry, malformed labels, miscalibrated fill and inconsistent rolling
were retained as visual failures instead of counting any encoded MP4 as success.

## Final initializer cohort

The evaluated runtime payload has 25 files and SHA-256
`5b62f993339e198bc03e26cb771f77d06eef34b4e73df3474d94578596bc8997`.
No acceptance fixture, sibling bundle or repository document is available to the
agent. The strict read surface contains the entry point, focused references,
small runtime template/palette files, one focused importer-source read in inlet
18, and task-owned deliverables. No forbidden
read or skill-payload mutation is accepted.

| Case and fresh attempts | Strict | Independent | Manual | Joint |
| --- | --- | --- | --- | --- |
| Inlet: `assets-luna6-17`, `18`, `19` | 1/3 | 3/3 | 3/3 | 1/3 |
| Vehicle: `vehicle-assets-luna6-13`, `14`, `15` | 1/3 | 2/3 | 2/3 | 1/3 |

Inlet 18 and vehicle 15 pass all gates jointly. Inlet 17 repairs a native text
contrast failure; inlet 19 repairs an ambiguous SVG edit and a native contrast
failure. Their final media and numerical/visual reviews pass, but their earlier
tool errors remain strict failures. Vehicle 13 stops after authoring an SVG whose
viewBox exceeds its declared view. Vehicle 14 delivers correct media after an
ambiguous SVG text edit, which remains a strict failure.

Across all 33 new Luna 6 attempts, seven traces pass strict mode and four pass
joint review on their respective payloads. All failed attempts are retained in
[the compact results](asset-direction-results-20261002.json). Neither current
case reaches two joint passes out of three, so the skill remains **validating**.
The separately authored production movies do not substitute for this gate, and
no Sol forward test substitutes for a failed Luna run.

Follow-up work should simplify SVG edits by stable element ID, ensure authored
dimensions preserve the scaffold viewBox, and improve text-background inspection
before native checks. Preserve the fixed protocol and zero-tool-error criterion.
The initializer, calibrated-geometry guidance and asset selection/import workflow
are installed locally; 68 deterministic tests and all repository integrity gates
pass. No new public example set or Pages publication was introduced in this pass.
