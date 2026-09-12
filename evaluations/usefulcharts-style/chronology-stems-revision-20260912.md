# Selective duration stems and weighted chronology

Status: validating. Baseline: `e35d36c35b2bf5d403f6464f31a9d2076079c38b`.

The reviewed reference is [UsefulCharts' Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history). Private reference images are retained outside Git. The reference alternates narrow continuities, larger historical phases, denser local groups and subject-specific illustrations. The prior fictional study has five regular territories and large colored duration bands. Its source inventory is deliberately smaller than the reference; this revision preserves all 50 periods, 55 typed transitions and 60 dated notes rather than adding filler.

## Development choices

The new optional stem treatment retains a thin visible rectangle over the exact numeric interval and puts the name in a separate colored capsule. Mixed treatment is essential: the all-stem candidate looked skeletal. Lane weights allocate horizontal space by the authored histories; the period and event offsets remain explicit units, and the year scale remains unchanged.

The selected development candidate is `chronology-stems-v27d/portrait-balanced`: 1680 × 2400, 18 stems, 32 full ribbons, five unchanged contextual illustrations. The previous width was 1800; height, source words, dates, memberships and font sizes are preserved. The principal bands narrow from 50 to 42 units. Repeated split/merge rhythms, five persistent territories and limited illustration variety remain visible. No indistinguishability or similarity percentage is claimed.

The first packer revision conservatively reserved the entire invisible stem envelope. Actual visible shapes are now shared between rendering and placement: both the full duration stem and its full name capsule are obstacles. The browser independently checks the visible stem's duration, width, center, color and visibility, the source-defined lane positions and exact transition fractions. This avoids accepting a correct invisible envelope over an incorrect visible date encoding.

## Forward protocol

Use three strict runtime-only Pi naturalistic repetitions with `openai-codex/gpt-5.5`, retaining the documented exception because PNG inspection requires an image-capable model. Use default Spark for the exact weighted-stem command control. The source bundle is read-only, acceptance fixtures are excluded, every required output path is explicit, and all attempts are retained. Naturalistic data reuse is development evidence, not a sealed validation or blind discrimination test.

The frozen runtime contains 85 files, SHA-256 `de4aa8b5eaeb024990cf4a6459621d5813fb1becc2cc16dc004c5ef45e1b13c3`. All four trials pass strict execution, exact paths, observed model, zero tool errors, clean runtime reads and unchanged payload. Three independent regional contracts preserve the complete 12-period, 11-transition, 18-note prompt. The Spark contract preserves all protected fields and independently verifies visible stem durations and the weighted lane origin.

| Trial | Model | Canvas | Stems / bands | Execution and source | Visual decision |
| --- | --- | --- | --- | --- | --- |
| `usefulcharts-v27-regions-1-20260912` | GPT-5.5 | 1500 × 1900 | 3 / 9 | Pass | Readable; excess page area and long bands remain. |
| `usefulcharts-v27-regions-2-20260912` | GPT-5.5 | 1350 × 1700 | 5 / 7 | Pass | Readable; shallow coastal fork and repeated prose placement remain. |
| `usefulcharts-v27-regions-3-20260912` | GPT-5.5 | 1400 × 1750 | 4 / 8 | Pass | Readable; wide vertical gaps and a less explicit capsule reading note remain. |
| `usefulcharts-v27-contract-spark-20260912` | Spark | 1200 × 1600 | 2 / 1 | Pass | Command control; no aesthetic acceptance claim. |

All three naturalistic PNGs were actually opened by the evaluated agent and separately inspected by the author. Evaluator-side browser reruns pass all three. The traces read only the prompt, entry point, relevant chronology references, small template and result files. They do not read acceptance fixtures, repository files or other skills. See the [complete trial summary](chronology-stems-summary-20260912.json) and [image critiques](chronology-stems-visual-reviews-20260912.json). Basic legibility and field selection transfer in 3/3 trials; visual parity is accepted in 0/3.

## Deterministic and visual evidence

- All 128 skill tests pass: 27 classic, 49 editorial, 19 family baseline, 13 context, 9 note placement and 11 new weighted/stem geometry tests. The 14 Pi harness tests also pass.
- All 24 chronology mutations are caught, including ten new corruptions of actual duration, stem visibility/color, capsule geometry/color, lane placement and a port that still touches the invisible envelope but misses the visible stem. The earlier 19 genealogy and 13 institutional mutation cases remain relevant; their reports are retained in the preceding revision.
- All three published murals pass the updated source-backed browser audit. Gallery desktop/mobile layout, fit/zoom controls and natural image aspect checks pass.
- Full-source comparison with `e35d36c3` preserves every period, event word, typed relation, year, group and font size. The painted-period rectangular-area approximation falls from 487800.94 to 363781.11 SVG units squared (25.42%); this is a geometric description, not a similarity score. At equal display width the change is smaller because the new page is narrower.
- The canonical final SVG matches the inspected selected prototype byte for byte after line-ending normalization: SHA-256 `d2a279b7808bb6679d001967c5dbd32210833aeaeff7b2f7f69c8cd54a3dd6c3`. Source data SHA-256: `af275e037ec84f3defae86c5306b323d780048d389e5a0befc6471691aa9d416`. Final PNG SHA-256: `8662039504406f14932f56c524b2f806f7ca3bfb70a2f4f48d090c9147eed2ab`.
- Twelve local explorations remain under `projects/usefulcharts-style/artifacts/reviews/chronology-stems-v27*/`: six rendered candidates and six `needs-layout` rejections. Whole-image comparisons informed the selected mixed composition. No failed attempt or inconvenient note was removed.
- Pattern IDs, repository structure, skill independence, payload and quick metadata validation pass. The Pages build contains 640 files, 41.89 MiB. Local installation synchronization updates 14 files.

## Reproduction commands

```powershell
uv run --script projects/usefulcharts-style/scripts/prototype_timeline_stems.py --output projects/usefulcharts-style/artifacts/reviews/chronology-stems-reproduction --variants portrait-balanced
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py --only five-regional-histories
uv run --script skills/usefulcharts-style/scripts/test_timeline_geometry.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_family_baselines.py
uv run --script skills/usefulcharts-style/scripts/test_context_landmarks.py
uv run --script projects/usefulcharts-style/scripts/compare_timeline_revision.py --before e35d36c3 --output projects/usefulcharts-style/artifacts/reviews/chronology-stems-final-comparison
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/chronology-stems-mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/chronology-stems-gallery
uv run --script projects/usefulcharts-style/scripts/summarize_chronology_stems.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
```

Naturalistic runs use the following command with `N` replaced by 1, 2 or 3. A fresh reproduction should choose a new run ID to preserve previous evidence.

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-mixed-chronology.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v27-regions-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-stem-placement-contract.md --mode json --strict --run-id usefulcharts-v27-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output deliverables/brief.json --expect-output deliverables/placements.json --expect-output deliverables/poster.svg --expect-output deliverables/layout.json --expect-output deliverables/browser.json --expect-output deliverables/poster.png
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v27-contract-spark-20260912/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

The complete equal-width reference/before/after view is `projects/usefulcharts-style/artifacts/reviews/chronology-stems-final-comparison/index.html`. Private reference art is not redistributed. The skill remains validating because the user's quality-and-composition target is still broader than the evidence achieved here.

The prototype command reproduces the selected final composition with the current renderer. Earlier v27/v27b reports retain the outcomes of the prior conservative obstacle implementation; replaying them with the revised visible-shape packer is not an exact historical rerun. The prototype refuses to overwrite an existing output folder so preserved attempts cannot be silently replaced.

## Verified publication

Implementation commit `f0e0f9375aa28288fe27c2a5878dbb65e21ec57e` passes [Pages workflow 34688838445](https://github.com/gvillarroel/skills/actions/runs/34688838445). All eleven public gallery, source and poster files match the committed expected bytes after the documented Pages transformations. The main examples catalog includes the stable example set. The [revised chronology](https://gvillarroel.github.io/skills/examples/usefulcharts-style/five-regional-histories.html) is published at its existing route.

Verification command: `uv run --script projects/usefulcharts-style/scripts/verify_publication.py --commit f0e0f937 --workflow 34688838445 --report projects/usefulcharts-style/artifacts/reviews/chronology-stems-publication-verification.json`. The receipt is retained locally; the complete SVG files for genealogy and institutions are unchanged from `e35d36c3` after normalizing line endings.
