# Illustrated discovery evaluation — 13 September 2026

The user rejected technically correct diagrams that were insufficiently playful and lacked integrated imagery. This pass updates the evaluator first, then revises the five current project diagrams. The skill remains **validating**: the illustrated acceptance checks below do not establish a matched UsefulCharts knowledge-density census or stylistic parity.

## Evaluator change

The runtime route now requires meaningful body imagery and specific, source-answerable discovery prompts for an illustrated brief. Five dimensions are scored independently: composition, image usefulness, image integration, playful discovery and legibility. Every dimension must reach 3/4; an average cannot hide a missing image layer. Content, geometry and identity defects are separate failures.

The new `assess_illustrated_review.py` checks evidence hashes, bound record IDs, declared family and body-region coverage, per-dimension observations, prior weaknesses and observed repairs. It explicitly does not inspect pixels or certify that a reviewer is truthful. A human or image-capable agent must inspect actual final whole and detail renders. Twelve boundary tests exercise absent imagery, header-only decoration, weak discovery, stale evidence, invented anchors, missing families, duplicate placements, missing direct review, uninspected placed sizes, open defects and unsupported questions.

The panel auditor also measures image viewports and checks them against text. Two additional browser regressions verify that nested SVGs export the root poster, detect real image occlusion and avoid counting clipped-out sheet content as an overlap. The full panel suite is now 11 tests.

Reusable guidance includes inspected, per-object crops rather than assumed equal cells, actual viewport aspect ratios, root-only export selectors, explicit image identity/provenance and source-answerable prompts. The canonical resources are in [the skill](../../skills/usefulcharts-style/SKILL.md), [illustrated discovery](../../skills/usefulcharts-style/references/illustrated-discovery.md) and [the rubric](../../skills/usefulcharts-style/references/evaluation.md).

## Isolated runtime evidence

Three naturalistic Luna high criticism runs and one default Spark command control were preregistered in SKILLS.md before execution. Luna was an explicit model exception because reading the supplied raster inputs was essential. The prompt did not say which candidates should pass. Every run received only the runtime skill and the declared raw inputs in a fresh workspace.

| Run | Strict execution | Independent task check | Runtime |
| --- | --- | --- | --- |
| `20260913-usefulcharts-illustrated-luna-1` | Pass | Read all 6 images; p fails, q fails, r passes | `2d413d2deb87d916e37bf0f6d4b3e5a481cf4b30da2e964793b7f833b95293db` |
| `20260913-usefulcharts-illustrated-luna-2` | Pass | Read all 6 images; p fails, q fails, r passes | Same 128-file runtime |
| `20260913-usefulcharts-illustrated-luna-3` | Pass | Read all 6 images; p fails, q fails, r passes | Same 128-file runtime |
| `20260913-usefulcharts-illustrated-spark-command` | Pass | 12 boundary tests; no claim of pixel review | Same runtime |
| `20260913-usefulcharts-illustrated-spark-final` | Pass | 12 boundary and 11 panel/viewport tests | `bfa0c902472cb4aeff1ea75829ce797a3a32c92d2f6361fd8950954991dcd765` |

The last control was added after a real development failure: `getBoundingClientRect()` on a nested SVG measured the full sheet content rather than the clipped viewport, producing false image/text collisions. The correction maps the explicit viewport corners through the parent's transform. The final control covers that changed runtime. The earlier three visual runs are not relabeled as final-runtime production tests.

All five runs verify the requested observed model, valid JSON events, zero tool errors, exact output paths, a clean runtime read surface and an unchanged skill copy. The three visual runs also verify unchanged input hashes and actual image-read events. Compact evidence, scores and read paths are retained in [the run summary](illustrated-discovery-20260913.json). Bulky traces remain under ignored `evaluations/runs/<run-id>/`.

This is one development discrimination task repeated three times, not a broad held-out production benchmark. The reviewers consistently reject absent or decorative-only imagery, but they give generous aesthetic scores and occasionally call generated illustrations photographs. Provenance and quality therefore remain independently checked. Their suggestion to add mechanism captions was applied to the final instrument poster after the raw candidate input freeze.

## Five revised diagrams

| Diagram | Selected records retained | Image placements | Canvas change from previous diagram |
| --- | ---: | ---: | ---: |
| Musical instruments | 71 | 15 new specimen examples | +39.72% area |
| UNIX/BSD | 47 | 6 new period archetypes | +39.72% area |
| Mars campaigns | 32 | 7 new spacecraft views | 0% |
| Star Trek civilizations and wars | 155 | 6 species + 4 ship illustrations | +10.24% area |
| Star Trek spacecraft | 79 physical ships; 90 printed fragments | 7 large new views + 12 retained trail images | 0% |

The five diagrams retain 384 selected records in aggregate, with identical printed record fields and source objects. Images are not counted as new factual records. All original calendar mark and component-span attributes are identical in Mars and the spacecraft atlas. Released early/future tracks supply space for the enlarged spacecraft views. The civilization history remains an explicitly schematic chronology; it is not relabeled as a numeric x axis.

The instrument image sheet initially leaked neighboring fragments; measured object bounds repair those crops. Mechanism captions connect the concrete objects to the taxonomy. The BSD Berkeley pocket adds a typed 4.4BSD Lite comparison. Mars combines reference-guided artwork with NASA/ISAS/JAXA and DLR reference imagery; failed launches and orbit insertions remain failures. The generic Star Trek representatives are explicitly illustrative people, not dated portraits. Existing accepted ship art is reused; the previously blocked Enterprise-D image request was not retried.

Each diagram passes independent source/printed-field preservation, image/text geometry, canvas bounds, one-page PDF dimensions and PDF label extraction. All 384 records also have explicit source links in the PDFs; script-only SVG source links are restored during export, and caption references use actual in-page destinations. PDF text extraction normalizes Unicode ligatures rather than changing the printed content. All final whole images, dense details and actual Poppler PDF renders were directly inspected. Five conservative declared illustrated reviews pass their evidence-completeness gates. The review states the limits of those declarations.

The offline gallery passes desktop and 390-pixel mobile checks for five visible diagrams, image loading, source links, search, record focus, zoom, before/after comparison and a working exploration drawer. Network requests were blocked during that test. The bundle includes editable SVG, self-contained HTML, PNG, PDF, source JSON and artwork maps. Local project artifacts are not published Pages examples.

## Commands and retained evidence

```powershell
uv run --script skills/usefulcharts-style/scripts/test_illustrated_review.py
uv run --script skills/usefulcharts-style/scripts/test_panel_poster.py
uv run --script projects/usefulcharts-playful/scripts/verify_artifacts.py
uv run --script projects/usefulcharts-playful/scripts/record_review.py
uv run --script projects/usefulcharts-playful/scripts/build_gallery.py
uv run --script projects/usefulcharts-playful/scripts/audit_gallery.py
uv run --script projects/usefulcharts-playful/scripts/summarize_evaluations.py
uv run --script projects/usefulcharts-playful/scripts/record_provenance.py
```

The visual repetitions use `projects/usefulcharts-playful/scripts/run_isolated_review.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-illustrated-criticism.md --model openai-codex/gpt-5.6-luna --thinking high --mode json --strict`, the run IDs above, and exact `deliverables/review.md` and `deliverables/verdicts.json` expectations. The final default Spark control uses `scripts/run-pi-skill-eval.py`, `evaluations/pi-prompts/usefulcharts-illustrated-final-command.md`, JSON strict mode, exact-command checking, and both exact deliverable expectations. Every run is independently processed with `summarize-pi-json-events.py --require-model <observed-model> --fail-on-invalid-json --fail-on-tool-error`.

The reusable evaluator resources remain entirely inside the skill. Project prompts and provenance are under `projects/usefulcharts-playful/design/`; render evidence, five reviews and the before/after gallery are under its ignored `artifacts/` directory. The local installation matches 145 canonical source files. Pattern-ID validation, skill validation, independence checks, payload checks and `git diff --check` pass. No commit, push or Pages publication was performed for these project deliverables.

## Remaining quality boundary

The reference-density requirement remains separate. The area growth of three posters reduces their retained-record density per unit area while providing recognizable images and explanatory captions. It is not reported as a density increase. The final results are more inviting and illustrated, but no claim of being indistinguishable from UsefulCharts is supported. Keep the skill validating until the outstanding reference census and broader production reliability requirements are met.
