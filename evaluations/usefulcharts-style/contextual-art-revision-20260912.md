# Contextual illustration composition

Status: validating. Baseline: `c2131d548ab101930832eb53f77de7b4f4328243`.

The direct comparison with [UsefulCharts' Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history) shows repeated same-side notes, limited image silhouettes and persistent regional columns in the previous study. This revision improves the local relationship of a dated observation and its illustration. It does not establish the user's requested indistinguishability across chronology, genealogy and institutional histories.

## Implemented composition

The renderer supports `art_position: above`, `below`, `left` and `right`. The first heading line remains on the numeric event date. Above/below images have a five-unit gap; side images reserve their width plus eight units before text wrapping. The packer reserves the entire image viewport, including the earlier interval occupied by an above image. The independent browser audit checks source image identity, actual symbol reference, viewport, visibility, text roles, type sizes and real text anchors.

Three unmodified public-domain Pearson Scott Foresman drawings are bundled with source revisions, hashes, dimensions and rights: [square-rigged ship](https://commons.wikimedia.org/wiki/File:Square-rigged_%28PSF%29.svg), [suspension bridge](https://commons.wikimedia.org/wiki/File:Suspension_bridge_%28PSF%29.svg), and [stagecoach](https://commons.wikimedia.org/wiki/File:Stagecoach_%28PSF%29.svg). They were inspected on poster paper at large and placed sizes. Their technologies and source identities are distinct from the fictional chart events. No UsefulCharts artwork is redistributed.

The selected dense mural is `contextual-art-v28d/side-ship`: the ship sits left of the existing 1131 convoy note; the bridge sits above the existing 1242 road note. All prior five illustrations remain. The complete source still has 50 periods, 55 typed transitions and 60 dated notes on a 1680 by 2400 page, with 18 duration stems and 32 full bands. All source words, numeric years, memberships, connections and type sizes are preserved. Broader note widths use the available corridors; no interval or bridge changes.

Twelve explorations are retained. Nine fail placement around the attempted postal-carriage image or the shifted clock. The final three render and pass browser auditing; the side-ship arrangement is selected after whole-page and native-scale comparison. The coach stays available as a reusable subject asset but is not forced into the crowded dense study. The phase-A configuration remains reproducible in the project script; later phases also retain attempted draft JSON.

## Forward evaluation and correction

The first 90-file runtime has SHA-256 `37dae04e9c329f9d82d768065a153ed40d6b7a24d917070eb70cfca11e06b1fb`. Three fresh runtime-only Pi tests use the documented `openai-codex/gpt-5.5` exception for actual image inspection. The default Spark command control exercises all four arrangements. This is reused development history with a new illustration requirement, not a sealed holdout or blind discrimination study.

The first cohort passes only one of three naturalistic strict gates. Two trials report placement errors around the stagecoach; one also reads a nonexistent placement report after the failure. All three eventually produce complete, independently valid artifacts, but the earlier errors remain failures. Direct image inspection rejects cramped side-note text in runs 1 and 3. Run 2 repairs that problem by widening the composition, although its strict execution still fails.

The corrective change gives side images an automatic footprint in addition to the normal 170-unit prose allowance. An explicit `--max-width` remains a hard limit on the whole group. The compact guide distinguishes a normal 220-unit text-note limit from a wider illustrated group and warns against reducing prose to one-word lines. A new regression proves both the default allowance and preservation of an explicit cap. Three fresh v28b naturalistic runs and a fresh Spark control evaluate this changed payload; all previous attempts remain in the [complete summary](contextual-art-summary-20260912.json).

The final 90-file payload is `afc33c49b870775d4082660dd83758b54e7a09f0f4f105b27a99e3bc50a69391`. All four v28b strict runs pass with the expected models, exact outputs, zero tool errors, clean read surfaces and unchanged payloads. Three evaluator-owned regional contracts and browser reruns preserve every supplied fact and verify the illustrations. All final images were opened by the tested agents and separately by the author. Across both cohorts, 6/8 strict executions and 8/8 final artifact contracts pass; neither earlier failure is discarded.

| Final trial | Canvas | Clock / bridge / coach positions | Direct visual critique |
| --- | --- | --- | --- |
| `usefulcharts-v28b-art-1-20260912` | 1500 × 1900 | Left / below / right | Usable groups; narrow coach text and large empty stretches remain. |
| `usefulcharts-v28b-art-2-20260912` | 1400 × 1780 | Below / above / right | Local image groups accepted; overall lane rhythm remains schematic. |
| `usefulcharts-v28b-art-3-20260912` | 1450 × 1720 | Above / below / right | The clock can be mistaken for an illustration of the preceding harbor note; reject that association despite correct geometry. |

No final trial passes visual parity. The next meaningful repair must consider perceived association and paragraph shape, rather than adding another geometry-only score.

## Validation evidence

- All 137 renderer/placement tests pass: 27 classic, 50 editorial, 19 family, 13 context, 17 note placement and 11 timeline geometry tests. Four image arrangements and three new source identities are exercised; earlier-note, preceding-period and page-start boundaries are protected.
- All 33 chronology SVG mutations are detected, including nine new corruptions of image identity, symbol reference, visibility, viewport, text size, text role and actual date position. The existing genealogy and institutional mutation reports remain retained in the preceding revision.
- All three source-backed mural browser audits pass. The published genealogy and institutional SVGs are unchanged from the baseline.
- Equal-width whole-page and native-scale detail reviews accept the local illustration improvement. Their readable detail does not override the remaining regularity of the full composition.
- The canonical SVG exactly matches the selected prototype after line-ending normalization: `4d1da9a89101614d5465fc40c99e097776ca187af3b324087b3b9e2cb24b38cd`. Its semantic source hash is `035a756e8c8f50a7d83385641bf4214bf11d63ffa5a31f8e8860dd9912ac7e95`. An initial fixture transfer repacked several note preferences from the earlier draft; that version is retained under `contextual-art-transfer-first`. Restoring the baseline packing stage reproduces the reviewed composition exactly.
- The three-card gallery passes desktop/mobile overflow, fit/zoom controls, embedded-image dimensions and browser-error checks. Static repository gates, metadata validation and the 14 Pi harness tests pass. Pages builds 640 files, 42.45 MiB; local installation synchronization is part of the release.

## Reproduction commands

```powershell
uv run --script projects/usefulcharts-style/scripts/fetch_transport_illustrations.py
uv run --script projects/usefulcharts-style/scripts/compose_contextual_art.py --phase d --output projects/usefulcharts-style/artifacts/reviews/contextual-art-reproduction
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py --only five-regional-histories
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script projects/usefulcharts-style/scripts/compare_timeline_revision.py --before c2131d54 --output projects/usefulcharts-style/artifacts/reviews/contextual-art-comparison-reproduction
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/contextual-art-mutations-reproduction
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/contextual-art-gallery-reproduction
uv run --script projects/usefulcharts-style/scripts/summarize_contextual_art.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
```

Replace `N` with 1, 2 and 3 in the forward command and use fresh run IDs for any reproduction:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-contextual-art.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v28b-art-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-contextual-art-contract.md --mode json --strict --run-id usefulcharts-v28b-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output deliverables/brief.json --expect-output deliverables/placements.json --expect-output deliverables/poster.svg --expect-output deliverables/layout.json --expect-output deliverables/browser.json --expect-output deliverables/poster.png
uv run --script evaluations/contracts/verify-usefulcharts-contextual-art.py evaluations/runs/usefulcharts-v28b-art-N-20260912 --output evaluations/runs/usefulcharts-v28b-art-N-20260912/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v28b-contract-spark-20260912/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

The author inspected `projects/usefulcharts-style/artifacts/reviews/contextual-art-final-comparison/comparison.png`, its `detail.png`, the final mural PNG, and all six naturalistic PNGs directly. Per-image decisions and remaining differences are preserved in [the visual reviews](contextual-art-visual-reviews-20260912.json). Private reference art stays outside Git.

## Verified publication

Implementation `4377c05731161cb94550798211e98c4ece5a9c41` passes [Pages workflow 34690575265](https://github.com/gvillarroel/skills/actions/runs/34690575265). All eleven public gallery, source and poster files match the committed bytes after standard Pages transformations. The main catalog retains the stable example-set link. The [revised chronology](https://gvillarroel.github.io/skills/examples/usefulcharts-style/five-regional-histories.html) is published at its existing route.

Verification: `uv run --script projects/usefulcharts-style/scripts/verify_publication.py --commit 4377c057 --workflow 34690575265 --report projects/usefulcharts-style/artifacts/reviews/contextual-art-publication-verification.json`. The final rendered PNG matches the selected prototype exactly, SHA-256 `c5000269f2618d1c1724b441d19b5351f00629ec0b77b7553b54a7e82a47a932`. This is a reproducibility check, not a measure of similarity to UsefulCharts.
