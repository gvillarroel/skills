# UsefulCharts-style: narrative chronology revision

Status: **validating**. The user objective remains parity of visual quality and composition with UsefulCharts. This revision improves the chronology and adds a reusable note-placement method. It does not establish indistinguishability.

## Visible comparison and corrections

The reference is the official [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history). The equal-width local comparison preserves the original reference, previously published `47927dfb` study, and revised study at `projects/usefulcharts-style/artifacts/reviews/timeline-narrative-comparison/index.html`. Reference artwork is private critique material and is not republished.

The previous study gave the colored ribbons too much weight, made narrative notes too small, and had too few useful illustrations. Its five persistent regional lanes are still less varied than the much denser reference. A second development composition improved type but introduced white illustration rectangles and a pale, unreadable museum thumbnail. Those image treatments were rejected. The earlier rendered development output remains under `projects/usefulcharts-style/artifacts/timeline-narrative-development/`; it is not a forward-test pass.

The revised study preserves all 50 period identities, names, start/end years, regions, 55 typed relationships and 60 exact dated event notes. Its page remains 1800 × 2400. Colored period area decreases from 768,476.42 to 487,800.9448 square SVG units, or 36.52%; this is an area measurement, not a resemblance percentage. Median event-heading size increases from 10.6 to 12.2 units. Five contextual images replace the previous three. The new transparent [historical anchor-escapement illustration](https://commons.wikimedia.org/wiki/File:Clock_gear.svg) is bundled without changing its 18,375 source bytes, SHA-256 `a8a305dcbf4f716a3af65d9b7fbd019d2ac3f66129480ccadb3fb9d3b8d3868f`; source identity, rights, dates and intrinsic dimensions are retained in provenance.

## A discovered audit blind spot

The earlier auditor checked filled transition polygons against notes and images but did not check a plain connection path against event text. Re-auditing the unchanged `47927dfb` chronology with the new check finds seven text collisions: the uncertain Cairn-to-Union path crosses the clockmaking and winter-post notes. The old recorded audit result is preserved; the fresh failed audit is `projects/usefulcharts-style/artifacts/timeline-narrative-v16/previous-revision-new-audit.json`.

The new auditor checks actual sampled connection paths against event text and illustration viewports. Two Highland periods move left by 50 units to make room for the uncertain corridor. Their dates and relationships remain unchanged. The final revised chronology passes the expanded audit with zero findings. Fourteen deliberately corrupted variants are detected, including paths drawn through event text and event artwork, in `projects/usefulcharts-style/artifacts/timeline-narrative-v16/final-mutations/`.

## Reusable method and scope

`pack_timeline_events.py` changes only event widths and horizontal offsets. It preserves words, dates, type sizes, image dimensions, periods and transitions. It reserves measured lines, complete image viewports, filled bridges and uncertain orthogonal paths. An unsuccessful placement writes no replacement brief. It does not globally backtrack, change the time scale, move dates, truncate notes, or silently shrink type. Its Shapely dependency is declared through `uv`; all required instructions and resources are inside the skill.

Nine focused regressions cover source preservation, an exact period-end boundary, images, obstructed notes, uncertain continuity and invalid inputs. Together with 26 classic and 42 editorial regressions, the suite passes 77 tests. The compact runtime reference explains the geometry, image integration, rendering and review commands. The new compact annotated template addresses the failed small-history composition below.

## Isolated forward evidence

The new naturalistic case contains 12 periods, 11 typed transitions and 18 dated notes across three fictional regions. It does not expose the mural fixture. The independent contract checks exact data, source categories, SVG inventories, clockmaking illustration, source-backed audit and supported PNG inspection. Every required path is an exact-output gate.

Image-dependent cases retain the recorded `openai-codex/gpt-5.5` exception because Spark omits image input. The exact command case uses `openai-codex/gpt-5.3-codex-spark`. Ambient context and skill discovery are disabled. Acceptance fixtures are excluded, and copied skill payloads remain read-only.

- The 71-file v16 payload is `95c3cbd71a1381e9dd11b4bd1dd12433f9ea77c57fde08a1809d33e70ecc6f87`.
- All three v16 regional artifacts pass the independent 12/11/18 data checks and contain supported image inspection. Trials 1 and 3 pass strict execution. Trial 2 first fails placement, tries reading a nonexistent placement report, and attempts an ambiguous edit; its later correct artifacts do not erase those tool errors.
- **All three v16 regional outputs fail visual review.** Trials 1 and 3 use 1800 × 2700 pages; trial 2 enlarges its page to 1800 × 3600. Their notes are too small among excessive empty space. Clean geometry is insufficient.
- The v16 exact-command Spark run passes all five exact outputs, both verbatim commands, source preservation, observed model, clean events/read surface and unchanged payload.
- The 72-file v17 payload is `f9da891285f01d53a9a32b289d6b90a831a0ce46588934ba51b4eaae991f4f9e`. It adds an explicit compact annotated route and template for small histories: 1300 × 1700, larger 18/15-unit notes, and a wider note search. All three fresh runs on the unchanged regional prompt pass strict execution, all six exact outputs, independent 12/11/18 data checks, supported image inspection and unchanged payloads. Their evaluator-side source-backed browser audits also pass with zero findings. The command-control Spark run passes both exact commands and all five outputs.
- **The three v17 images improve small-history legibility, but do not establish visual parity.** All three use 1300 × 1700; the final images were opened and inspected. The notes are readable, the clock image has no opaque rectangle, and the division/merger paths remain clear. Three persistent lanes and recurring note blocks still produce a more schematic cadence than the reference. One small illustration does not demonstrate the varied image integration of a dense published wall chart. Trial 2 also uses narrower wrapping and more horizontal shifts between successive notes than trials 1 and 3. No resemblance percentage is assigned.

The complete record is [the eight-attempt summary](narrative-chronology-summary-20260912.json): seven strict passes, eight independently correct final artifacts, and three explicitly rejected v16 images. These counts refer to two repetitions of one regional development case and a command control, not eight independent subject families or an untouched holdout. Run `projects/usefulcharts-style/scripts/summarize_timeline_revision.py` to collect it without discarding failed attempts. The exact required paths, prompts, hashes and read surfaces remain in that summary and the ignored raw run folders.

## Validation commands

```powershell
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/compare_timeline_revision.py --output projects/usefulcharts-style/artifacts/reviews/timeline-narrative-comparison
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/timeline-narrative-v16/final-mutations
uv run --script evaluations/contracts/verify-usefulcharts-regions.py --check-prompt evaluations/pi-prompts/usefulcharts-narrative-regions.md
uv run --script projects/usefulcharts-style/scripts/summarize_timeline_revision.py
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/timeline-narrative-v16/gallery
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --with pyyaml C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/usefulcharts-style
uv run --script scripts/sync-local-skills.py
uv run --script scripts/build-pages.py
```

Each regional Pi run uses `scripts/run-pi-skill-eval.py usefulcharts-style --model openai-codex/gpt-5.5 --prompt-file evaluations/pi-prompts/usefulcharts-narrative-regions.md --mode json --strict`, a distinct run ID, and `--expect-output` for all six required `result/` files. Command-control runs use `evaluations/pi-prompts/usefulcharts-event-placement-contract.md`, Spark, `--require-exact-command-from-prompt` and all five exact output paths.

All listed local gates pass. The three canonical SVGs pass the expanded browser audit against their exact source JSON; the gallery passes at desktop/mobile widths and all three viewers retain their natural aspect ratios through fit/zoom/native views. The 72-file canonical runtime matches both the frozen v17 forward payload and the local installation, recorded in `projects/usefulcharts-style/artifacts/timeline-narrative-v17/runtime-verification.json`. The quick validator required its PyYAML dependency; the explicit `--with pyyaml` invocation above passes. The Pages build completes with 639 files.

Publication is pending explicit staging, commit, push and a verified Pages deployment. The broader dense composition and illustration-variety gaps remain open.
