# UsefulCharts-style visual revision

Date: 2026-09-11, America/New_York. The final isolated attempt crossed into 2026-09-12 UTC. Skill: [usefulcharts-style](../../skills/usefulcharts-style/SKILL.md). Status: **validating**.

The first gallery was aesthetically inadequate. Its clean geometry did not compensate for sparse diagrams, repeated equal-width chains, oversized empty corridors, a weak title-to-field ratio, and nearly uniform label treatments. The former 25/32, 27/32, and 26/32 scores are superseded as visual acceptance. They are retained only in the historical record.

The revised skill and examples are materially closer to the inspected poster family. They do **not** establish indistinguishability. In side-by-side author review, the remaining regularity of the synthetic genealogy, simpler institutional imagery, and independent timeline tracks still distinguish the examples from the official references. No blinded panel, source-classification experiment, or numeric similarity estimate was performed.

## What changed

- Added an explicit `design: editorial` renderer profile and two focused runtime references. The classic schematic renderer remains compatible but is no longer the aesthetic acceptance target.
- Changed dense examples to 1800 × 2700, with a shallow condensed title, narrow frame, continuous ivory field, and compact source footer.
- Added authored node centers, unequal widths and emphasis, unboxed supporting names, colored principal cards, family pills, white emblem panels, selected portrait images, and serif geographic headings.
- Replaced the institutional example's five equal parallel families with unequal page regions. Later traditions descend from earlier institutions; declared influence can cross regions. Category colors remain stable across nodes and paths.
- Added rounded orthogonal connections, typed dotted influence, union midpoint descent, and haloed crossings. Fixed a real bug where a requested corridor could enter its own source or target box. The router now checks both endpoint entities as obstacles except at the exact attachment.
- Added map and actual-count insets, asymmetric temporal starts and gaps, varied ribbon widths, rotated names, horizontal dated annotations, era dividers, a proportionate cartographic backdrop, and explicit dotted or filled continuations. None of these changes alter interval dates to fit text.
- Corrected the browser audit to measure transformed text and sample actual curved paths. Fixed the viewer stylesheet so nested SVG image viewports retain their declared size.
- Removed the aggregate-score acceptance shortcut. The skill now requires reference comparison at whole-page and detail scales and records visible differences separately from correctness.

The reusable procedure is in [editorial composition](../../skills/usefulcharts-style/references/editorial-composition.md), with the [input contract](../../skills/usefulcharts-style/references/editorial-contract.md) and [updated pattern recipes](../../skills/usefulcharts-style/references/pattern-recipes.md). Dense examples are fixtures, not required runtime reading.

## Actual visual comparison

The local comparison places the official preview, rejected version from commit `e0c473ad728812bf5f51690a21b787c477027394`, and revised example at equal display width. Original aspect ratios remain visible. Reference screenshots are local evaluation material and are not published in the example gallery.

| Family | Reference and first-version defects | Revised result | Remaining visible difference |
| --- | --- | --- | --- |
| Genealogy | The [European Royal Family Tree](https://usefulcharts.com/products/european-royal-family-tree) uses dense, varied rulers/spouses, cross-house connections, portraits, and heraldry. The first example was seven regularly spaced rows of identical partner boxes. | 336 people, 134 partnerships, 214 child/relationship paths; plain spouses, selective portraits, shorter cadet lines, different family depths, irregular schematic intervals, and 15 recorded route crossings. | Seven persistent synthetic spines remain more regular; cross-house traffic and historical focal points are less varied than the reference. More nodes alone would not fix this. |
| Institutional lineage | The [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) distributes different families over unequal historical regions with major emblems and extensive lateral relationships. The first example was an evenly spaced five-column matrix. | 191 institutions, 199 relationships, upper count/map insets, a compact central origin, broad and narrow families, later category transitions, multiple node treatments, and cross-family influence. | Small original vector emblems are less specific and varied than real institutional marks. The generated vocabulary and region boundaries remain more regular. |
| Timeline | The [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history) combines narrow and wide histories, mergers and splits, varied event density, cartography, and artifact imagery. The first example had five uninterrupted strips and sparse adjacent labels. | 78 periods across ten tracks in five regions, 68 explicit continuations, variable widths and offsets, actual dated events, era rulers, museum imagery, and a geographic field. | Tracks remain predominantly independent and annotation vocabulary repeats. The reference has more historically specific branching, geographical rearrangement, and image integration. |

Local evidence:

- `projects/usefulcharts-style/artifacts/reviews/comparison/index.html`: all three reference/before/after comparisons.
- `projects/usefulcharts-style/artifacts/reviews/comparison/*-comparison.png`: normalized full-page comparison sheets.
- `projects/usefulcharts-style/artifacts/screenshots/editorial-final/detail-*.png`: inspected native-scale details of the final genealogy, lineage, and timeline.
- `projects/usefulcharts-style/artifacts/images/final-*.png`: final full-resolution images.

At full resolution the reviewed text remains legible, partnership origins are visible, image panels preserve size, and relationship paths are traceable. The pages are closer to the requested visual family; the requested indistinguishability threshold remains **unproven and not claimed**.

## Technical evidence

| Check | Result |
| --- | --- |
| Existing renderer tests | 26/26 pass |
| New editorial tests | 14/14 pass: preserved source, distinct paths, automatic small layout, invalid art identifiers, image provenance/aspect, unresolved relationships, self-box reentry, requested-corridor repair, numeric time and events, duplicate/backward transitions, filled continuation endpoints |
| Independent SVG corruption checks | 6/6 detected: deleted node, oversized label, invisible label, wrong relation type, detached source, and source reentry |
| Source-backed Chromium audits | 3/3 pass; 725, 584, and 405 measured text elements; zero reported geometry, text, contrast, or source findings |
| Minimum measured text/background contrast | 4.949:1 in each example; this is not a certification of connector colors or every photographic background |
| Desktop/mobile gallery and zoom | Pass at 1440 and 390 pixels; three stable IDs, no page overflow or page errors; Fit/zoom/100% work; 37 genealogy and 24 timeline embedded image viewports retain their declared width |
| Repository gates | Pattern IDs, skill structure, independence, and payload checks pass |

The audit validates visible text, actual node boxes, sampled connector paths, source inventories, and numeric dates. It does not automatically judge illustration quality, semantic association of a nearby family pill, overlap of every decorative object, or aesthetic resemblance. These remain manual checks.

## Isolated runtime attempt

Run: `usefulcharts-editorial-v5-20260911-spark-1`. Model: `openai-codex/gpt-5.3-codex-spark`; strict JSON mode; runtime profile; copied skill read-only; ambient context and skill discovery disabled; exact output paths required. The new profile contains **45 runtime files**, SHA-256 `04b643f006bb57632953d51d4fc1378fcc6113d8f2c1423deb8fe06227bcddf4`.

The provider returned **“The usage limit has been reached”** before any tool call or artifact. Six required files were missing. Harness `passed` is false, payload integrity passes, and no output was accepted. Classification: **external provider capacity failure**, not a skill success or an observed skill-authoring failure. The event summarizer accepts the JSON/model identity, but zero reads and zero artifacts cannot satisfy the runtime gate. The raw run is retained under `evaluations/runs/`.

There is no reason to spend additional calls repeating the same immediate quota failure. Keep `validating`; the revised profile still needs the repository's final contract, repeated naturalistic/generalization, and boundary cohort when capacity is available. Earlier runtime passes used older payloads and do not certify this revision.

## Asset provenance

The 16 portrait samples and eight object samples are public-domain records from the Art Institute of Chicago API. Original titles, dates, authors, source URLs, and SHA-256 values are retained in the bundled provenance files and embedded beside each used image. Images are downloaded from the museum's IIIF service at 200-pixel width; objects preserve their aspect ratio. The [museum API documentation](https://api.artic.edu/docs/#copyright) describes its image copyright policy. Synthetic examples explicitly state that these are decorative samples, not likenesses of invented people or evidence of invented events.

The locator/background geometry derives from Natural Earth's 110m country data, whose [terms identify it as public domain](https://www.naturalearthdata.com/about/terms-of-use/). The bundle records the upstream URL and transformation. Its illustrative category assignments do not assert real geographic prevalence. Vector emblems are original deterministic drawings. UsefulCharts logos and product artwork are not redistributed.

## Reproduction

From the repository root:

```sh
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json --report projects/usefulcharts-style/artifacts/reviews/final-aurelian-families.json --png projects/usefulcharts-style/artifacts/images/final-aurelian-families.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json --artifacts projects/usefulcharts-style/artifacts/reviews/editorial-mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/screenshots/editorial-final
uv run --script projects/usefulcharts-style/scripts/compare_posters.py --repository . --before-revision e0c473ad728812bf5f51690a21b787c477027394 --artifacts projects/usefulcharts-style/artifacts
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-naturalistic.md --mode json --strict --run-id usefulcharts-editorial-v5-20260911-spark-1 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/browser.json::status=pass --forbid-event-command-regex '(?i)\bgit\b' --timeout-seconds 420
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-editorial-v5-20260911-spark-1/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

Repeat the source-backed audit for the other two example IDs. Use a new run ID for every future isolated attempt; do not overwrite the retained failure. Comparison rebuilding requires the locally retained reference previews.

The published gallery preserves all three stable pattern URLs at [the UsefulCharts-style example set](https://gvillarroel.github.io/skills/examples/usefulcharts-style/). Pages publication and final synchronization are recorded in the matching `SKILLS.md` validation note.
