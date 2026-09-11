# UsefulCharts-style skill evaluation

Date: 2026-09-11. Skill: [usefulcharts-style](../../skills/usefulcharts-style/SKILL.md). Status: **validating**.

The skill and three original example posters are implemented and locally verified. The examples reproduce recognizable composition decisions from the reference family: a condensed title, a light continuous field, compact labels, stable category colors, branching or parallel spatial structure, and typed, deliberately routed relationships. They are simpler and more regular than UsefulCharts' largest illustrated posters.

The final release gate is **not passed**. The last three isolated Spark runs reached the provider usage limit before producing all required artifacts. Earlier trials also exposed real authoring failures, which are retained below. Do not interpret the visual example passes as full runtime reliability.

## Evidence and deliverables

- [Reference analysis](reference-analysis-20260911.md): four official product previews, observed composition decisions, and review-driven changes.
- [All trial outcomes](run-summary-20260911.json): 18 isolated Pi attempts, including failures and incomplete provider-limited attempts. Eight passed the launcher; one of those also exposed an ambient Git-status read on manual review and is not accepted as an isolated pass.
- [Example gallery source](../../skills/usefulcharts-style/assets/examples/usefulcharts-style/index.html): original genealogy, lineage, and timeline posters; SVG, source JSON, and zoomable HTML for each.
- [Public example gallery](https://gvillarroel.github.io/skills/examples/usefulcharts-style/): the same three original posters, listed in the main Pages catalog with stable pattern links.
- [Independent content checker](../contracts/check-usefulcharts-output.py): evaluator-owned names, relationships, and numeric time geometry.
- [Routing control](run-routing.py): separate metadata-only classification, with no forced skill loading.

Raw runs, screenshots, browser reports, and mutation artifacts remain ignored under `evaluations/runs/usefulcharts-*` and `projects/usefulcharts-style/artifacts/`. UsefulCharts' source artwork is used only for local reference inspection and is not included in the published gallery.

The delivered runtime profile contains 12 files (202,532 bytes) and has SHA-256 `cf9c1f77420fd8ee4a0204f0aa7b2d4dc6adcd1988fc34aca2f07866cd80cb1f`. It excludes the acceptance gallery. The last provider-limited attempts used SHA-256 `9e01f4e1f4e772faa2c2bf1927cb9d82539060d4304f4a8cead1d5bc1e6eaeaa` and verified that their copied payload remained unchanged. After those attempts, font-license whitespace was normalized and the compact recipes were aligned with the existing automatic-lineage recommendation and narrow-ribbon timeline design. No renderer behavior, license wording, or font binary changed. The delivered hash has not passed a final Spark cohort. Every focused reference is under 8 KB. The font is a licensed runtime asset; it is embedded by the renderer rather than loaded as model context.

## Published example review

All three examples use an 1800 × 2400 viewBox and entirely synthetic source data.

| Example | Data coverage | Browser/source checks | Manual review |
| --- | --- | --- | --- |
| `usefulcharts-dynastic-genealogy` | 70 people, 30 partnerships, 32 child relationships including one uncertain link | Pass; 167 text elements; zero geometry/contrast/source findings | Partnership midpoints and two cross-house relationships inspected at full resolution. Two unrelated route crossings remain readable with halos and no junction dots. |
| `usefulcharts-branching-lineage` | 76 institutions, 75 branches, three influence edges | Pass; 230 text elements; zero geometry/contrast/source findings | Shared origin, five stable category families, compact names, and three differentiated influence routes inspected. One unrelated crossing is visually clear. |
| `usefulcharts-parallel-history` | 25 intervals, five regions, years 1000–2000 | Pass; 77 text elements; zero geometry/contrast/source findings | Narrow ribbons and endpoints follow one time scale. Opaque label surfaces prevent tick lines from passing through text. No descent is invented between phases. |

The minimum measured text/background contrast is 6.027:1 in each example. This is a text check; it is not a blanket certification of every colored connector or every possible custom palette.

The gallery passes Chromium checks at 1440-pixel desktop and 390-pixel mobile widths: three unique pattern cards, no horizontal page overflow, no page errors, and working Fit page, 100% detail, and zoom controls. All three poster details and the final generated Pages gallery were visually inspected.

### Anchored visual rubric

Scores are reviewer judgments on a 0–4 scale, not percentages of pixel similarity. The acceptance threshold is 24/32, no dimension below 2, and no unresolved content or occlusion failure.

| Dimension | Genealogy | Lineage | Timeline |
| --- | ---: | ---: | ---: |
| Poster composition | 3 | 3 | 3 |
| Spatial hierarchy | 3 | 3 | 4 |
| Connection/chronology semantics | 3 | 3 | 4 |
| Color system | 3 | 4 | 3 |
| Typography | 4 | 4 | 4 |
| Density and rhythm | 2 | 3 | 2 |
| Reference-family resemblance | 3 | 3 | 2 |
| Fidelity and usability | 4 | 4 | 4 |
| **Total** | **25/32** | **27/32** | **26/32** |

The strongest resemblance is the branching lineage: colored families, a common origin, hierarchy, and compact repeated nodes. The genealogy is deliberately regular and leaves more empty space than the royal reference. The timeline matches the parallel temporal grammar but lacks the original's illustrated annotations and more varied historical density. These limitations are visible and are not hidden by the aggregate scores.

## Isolated agent evaluation

Harness: Pi 0.84.2; model: `openai-codex/gpt-5.3-codex-spark`; thinking: high; strict JSON mode; runtime-only copied skill; ambient skills and context disabled. Each repetition used a fresh workspace. Required paths were passed individually through `--expect-output`.

| Cohort | Launcher result | Reviewed outcome and failure classification |
| --- | --- | --- |
| Development contract | 1/1 | Starter produced exact files. This is command-contract evidence, not general visual ability. |
| Initial contract / naturalistic / generalization | 2/3 | Naturalistic run repaired narrow labels but accumulated tool errors and an out-of-range file read. Its completed artifact preserved all 28 institutions and 29 relationships. |
| v2 naturalistic | 0/3 | Manual grid widths, long details, internal ID constraints, and an assumed Pillow dependency produced errors. These failures motivated automatic lineage layout, broader internal IDs, better width budgeting, and image-reading guidance. |
| v3 naturalistic | 2/3 launcher; **1/3 after isolation review** | Automatic placement produced good artifacts in repetitions 1 and 2. Repetition 1 also ran ambient `git status`; that violates the intended isolated read surface despite the launcher's pass. Repetition 3 used manual placement and needed repair. All three final SVGs pass independent institution/relationship checks. |
| v3 generalization | 1/3 strict | All three final timeline artifacts pass independent checks for all 15 phases and exact visible numeric interval geometry. Two runs first wrote malformed JSON and failed the zero-tool-error gate. |
| v3 contract and missing-parent boundary | 2/2 | Exact contract output passed; missing parent `unknown-42` was retained and reported as `needs-data`, without inventing a parent or producing a finished chart. |
| v4 generalization | 0/3 complete; **infrastructure-blocked** | Final guidance recommends native-object JSON serialization, and evaluation prompts explicitly prohibit Git discovery. Each run read nine task/skill resources before the provider returned “The usage limit has been reached.” Required output files were missing. No incomplete attempt is counted as a pass. |
| Metadata routing | 8/8 | Correctly selected the poster skill for genealogy, branching history, and parallel chronology; selected Mermaid, D3, or none for the negative controls. This is classification evidence, not an end-to-end app discovery test. |

The independent checker was corrected after manual review to accept uppercase lettering and the prompt's legitimate “led to” interpretation as institutional succession. Explicit splits still require branch semantics, influence remains distinct, and every endpoint must match. The original checker was too specific about presentation and relation vocabulary; the correction does not accept missing institutions, wrong endpoints, or invented ancestry.

The final prompts add an explicit no-Git artifact boundary and the final launcher commands add `--forbid-event-command-regex '(?i)\bgit\b'`. This addresses the observed read-surface gap without modifying the repository harness or counting the affected earlier run as isolated.

## Deterministic and adversarial validation

- **26/26 renderer tests pass:** typed unions, uncertainty/adoption, endpoint identity, duplicate and missing records, chronology, temporal overlap, cycles, preserved input, output-path safety, text escaping, embedded font/license, contrast, automatic rank placement, and deterministic output.
- **5/5 deliberately corrupted SVGs are rejected:** deleted person/institution, oversized text, invisible text, wrong relationship kind, and detached source endpoint. These checks mutate visible SVG data independently of the renderer.
- **3/3 published examples pass** source-backed Chromium geometry and actual image inspection.
- Repository skill validation, pattern IDs, skill independence, payload checks, system quick validation, and the 12-test Pi harness suite pass.
- The three-test authored-docs/Pages-output boundary suite passes. The complete Pages build and 13-entry pattern-page catalog validation pass.
- The local installation is synchronized; all 24 canonical bundle files match.

The first local Pages build exposed absent executable shims in three existing ignored `node_modules` directories. Reinstalling their already locked dependencies with `npm ci --ignore-scripts --no-audit --no-fund` repaired the local build. No dependency manifest, lockfile, or authored source in those other skills was changed.

## Reproduction commands

From the repository root:

```sh
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json --report projects/usefulcharts-style/artifacts/reviews/atlas-of-inquiry-browser.json --png projects/usefulcharts-style/artifacts/images/atlas-of-inquiry.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json --artifacts projects/usefulcharts-style/artifacts/reviews/mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py dist/pages/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/screenshots/pages
uv run --script evaluations/contracts/check-usefulcharts-output.py evaluations/runs/usefulcharts-naturalistic-v3-20260911-spark-2/workspace --case naturalistic --report projects/usefulcharts-style/artifacts/reviews/naturalistic-v3-2-independent.json
```

Final generalization command; repeat with fresh run IDs for repetitions 1–3:

```sh
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-generalization.md --mode json --strict --run-id usefulcharts-generalization-v4-20260911-spark-1 --expect-output museum/data.json --expect-output museum/timeline.svg --expect-output museum/viewer.html --expect-output museum/layout.json --expect-output museum/browser.json --expect-output museum/preview.png --expect-output-json-field museum/browser.json::status=pass --forbid-event-command-regex '(?i)\bgit\b' --timeout-seconds 420
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-generalization-v4-20260911-spark-1/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

A clean event summary alone does not establish success: provider-error messages and missing artifacts must also be checked. `run-summary-20260911.json` retains these provider failures explicitly.

## Remaining release work

When Spark capacity is available, run a fresh final-payload contract, three naturalistic repetitions, three generalization repetitions, and the missing-parent boundary case using the current prompts and no-Git command gate. Require at least 2/3 accepted naturalistic and generalization passes, inspect all final artifacts, and recheck clean reads and payload integrity. Keep the skill `validating` until that evidence exists.

Historical research accuracy, portraits/maps, writing-system comparison matrices, and very large interconnected genealogies remain outside the validated surface. The useful current capability is original editable genealogy, branching-lineage, and parallel-interval posters with an explicit visual and semantic review workflow.
