# Distinct emblems and contextual openings

Date: 2026-09-12. Baseline: `3b524e6320914e52deb137347c8a02c8cc9306a5`.

The revision improves a concrete weakness in illustration identity and adds a reusable way to compose meaningful context beside a compact origin. The skill remains **validating**. Equivalent UsefulCharts quality and composition are still unproven.

The [machine-readable evidence](context-and-emblems-summary-20260912.json) retains both frozen cohorts, all ten local composition attempts, source invariants, artifact hashes, browser results and the actual runtime digest. The [previous revision](data-first-branches-revision-20260912.md) records the baseline and earlier deficiencies.

## Visual diagnosis and accepted changes

The reference previews were inspected again alongside the three complete candidate murals at equal display widths. The originals remain local review material and are not redistributed. Relevant official previews are the [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree), [European Royal Family Tree](https://usefulcharts.com/products/european-royal-family-tree) and [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history).

| Dimension | Observed problem | Change and remaining limit |
| --- | --- | --- |
| Illustration identity | Fourteen named subjects used only six distinct drawings. A star and sun were compasses; a lens was a prism; an anchor was a ship. | Eight new original vector drawings distinguish all fourteen subjects. The revised institutional mural changes thirteen placed illustrations. These are illustrative devices, not authentic institutional marks. |
| Opening composition | The 70-record publishing case had broad empty pockets around its origin and a detached category key. | Add an illustrated source-backed paragraph and category counts derived from the actual records. Reserve these boxes during routing. The counts also identify every category, making the separate key redundant. |
| Local branch composition | The education family remained a long right-side sequence, weakening the page's balance. | Reposition its eleven records as one local history. Two mergers become shorter and easier to trace. Keep all seventy records, ninety-seven typed links, text fields, font settings and category colors. |
| Reusable placement | Proposed context boxes could cross the printable field or crowd an institution. | Measure full content height and offer bounded fitting within 120 units of the proposed position. Reserve node envelopes, connection attachments, captions, existing insets and the key. Report every adjustment. Exact placement remains available by omitting the fit flag. |
| Visual review | Agents assumed optional image-processing tools were installed when enlarging details. | Render a requested source-coordinate detail directly with the existing audit browser, then inspect its PNG. The full audit and full preview remain available. |

The private comparison is at `projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/comparison/index.html`. Its four views show the three reference families and the publishing before/after. The emblem table is at `emblems-first/comparison.html`. Baseline SVGs are preserved independently, so rebuilding the canonical examples does not change the comparison's before state.

Reusable guidance is in [semantic emblems](../../skills/usefulcharts-style/references/semantic-emblems.md) and [context insets](../../skills/usefulcharts-style/references/context-insets.md). Rendering, measurement, fitting and inspection live within the skill. None requires project scripts or acceptance fixtures at runtime.

## Source and geometry checks

The existing 141-record mural retains its complete source JSON, 171 typed relationships, printed text, node placement and connector paths. Only the thirteen placed illustrations using newly distinct subjects change. The genealogy and chronology SVGs are byte-identical to the baseline. This is an accepted illustration improvement, not a claim that all three compositions have been redesigned.

The separate 70-record publishing study preserves every non-position node field. The moved records are Schoolbook Society, Teachers' Publishing Guild, Children's Book Room, Language Readers Office, Normal School Press, The Primer Company, School Atlas Office, United Textbook Press, Spoken Book Library, Learning Media Trust and Open Learning Network. Their relationship identities and kinds remain unchanged; routes and influence attachments are recomposed where needed. The page remains 1988 × 2016.885 source units and has 59 route crossings. A crossing count is not an aesthetic score.

Four intermediate education arrangements failed the five-unit node-gutter check. The first native count box also failed because its 228-unit height was smaller than the measured 230.7-unit requirement. All five failed attempts remain in the local evidence. No failed attempt is counted as a finished poster.

## Isolated forward tests

The naturalistic task is a **refinement of a disclosed authored development layout**. It supplies seventy individually authored institutions, ninety-seven typed relations, coordinates and typography, and asks the agent to add an exact illustrated paragraph and a complete category-count overview. It does not instruct which commands to run. It does not test full data-first layout generalization.

The command control supplies fourteen independent fictional teaching collections with all fourteen emblem subjects, two contextual insets and exact commands. Its separated grid is a technical fixture, not the intended editorial composition standard.

Both cohorts use isolated `pi` runtime copies, strict JSON mode, exact required outputs, disabled ambient context/discovery and unchanged skill payloads. GPT-5.5 is the recorded exception for image-dependent naturalistic runs; command controls use default Spark. The exception and the second cohort were recorded in `SKILLS.md` before execution.

| Frozen cohort | Naturalistic strict result | Command control | Independent artifact and browser checks |
| --- | --- | --- | --- |
| A: `usefulcharts-v32-*` | **0/3** | **1/1** | **4/4** final artifacts pass |
| B: `usefulcharts-v32b-*` | **3/3** | **1/1** | **4/4** final artifacts pass |

Cohort A completed every required artifact, but all three naturalistic runs attempted optional image tools that were absent. Runs 2 and 3 also corrected invalid context placement after renderer errors. These remain strict failures. Missing-tool assumptions are agent failures; the repeated placement and review friction motivated the narrower skill improvement. They were not removed from the denominator or relabeled as passes after recovery.

Cohort B used the final 104-file runtime, SHA-256 `85f1eb0bf430e1b20692642d419d0c508ec75fba72bbcf0f8a3b7624997cdba4`. All four runs have zero tool errors, matching observed models, valid JSONL, exact required outputs, unchanged copied payloads and acceptable read surfaces. The three naturalistic agents read their own final full-page PNGs and browser-rendered details. Their source fields, exact text, visible counts and artwork were independently checked. All three distinct final full-page PNGs were also directly inspected by the author.

The normal read surface consists of `SKILL.md`, the relevant context/institutional contract references and the generated task artifacts. No acceptance gallery, sibling skill, repository documentation or project evidence was used by the evaluated agents. The large prompt contains the complete authored source; it is disclosed task input, not an unseen holdout.

Reusable controls:

- [Naturalistic prompt](../pi-prompts/usefulcharts-context-insets.md).
- [Command-control prompt](../pi-prompts/usefulcharts-context-insets-contract.md).
- [Independent artifact contract](../contracts/verify-usefulcharts-context-insets.py).
- [Replay and trace script](../../projects/usefulcharts-style/scripts/audit_context_runs.py).
- [Evidence summary script](../../projects/usefulcharts-style/scripts/summarize_context_revision.py).

The final naturalistic command, repeated with `N` = 1, 2 and 3, was:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-context-insets.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v32b-context-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output result/review.md
```

The final Spark command was:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-context-insets-contract.md --mode json --strict --run-id usefulcharts-v32b-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output result/source.json --expect-output result/context.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
```

The earlier cohort used the corresponding `v32` run IDs. Raw runs remain under `evaluations/runs/`. Independent replay and trace inspection were performed on all eight, including the strict failures.

## Deterministic and browser verification

All **175 skill tests** pass. The new coverage consists of three emblem tests and fourteen context/detail tests. Emblem tests inspect actual browser-rendered pixels at 29-, 37- and 50-unit footprints. Context tests cover exact counts, complete prose, source binding, box measurement, collisions, bounded fitting, unchanged records, connection-attachment clearance, direct detail rendering and invalid detail coordinates. Ten deliberate inset mutations are detected, including missing/hidden/recolored marks, changed totals, overlapping marks, altered type, prose, art identity, box position and intersecting paths.

The existing thirteen institutional SVG mutations and eight painted-connection controls also pass. The three complete mural browser audits have no findings or composition warnings. Gallery checks pass at 1440 and 390 pixels, with working zoom, fit and full-size controls and no browser errors.

The first new fitting test exposed a crowded source attachment; the fitter was corrected to reserve the attachment before cohort B. An earlier mutation-test setup serialized an XML prefix that HTML parsing did not recognize as SVG; it was repaired before cohort A. Neither development defect is omitted from the evidence.

Repository pattern-ID validation, skill validation, independence validation and payload checks pass. The auxiliary skill-creator validator passes with an explicit PyYAML dependency. The Pages build succeeds with 640 files, 42.49 MiB. Its dependency annotation warnings are unrelated to this skill and do not change the successful exit status. Repository-local skill synchronization is part of this revision's release workflow.

Representative commands:

```powershell
uv run --script skills/usefulcharts-style/scripts/test_editorial_art.py
uv run --script skills/usefulcharts-style/scripts/test_editorial_insets.py
uv run --script projects/usefulcharts-style/scripts/compare_context_composition.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/gallery
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
```

## Visual acceptance and remaining work

The fourteen emblem subjects now have visibly different silhouettes at their actual placed sizes. The new context material gives the publishing opening a purpose, and the shorter education branch improves its local balance. Those are accepted changes supported by the inspected images.

The institutional reference still has more intermediate subdivisions, stronger changes of emphasis and more varied local identities. The 141-record study retains five large families for much of its height. The 70-record study retains many long dotted influence paths in the middle and lower page. The genealogy repeats similar nameplate rhythms, while the chronology's five regional histories remain more regular and its larger vertical labels can dominate adjacent prose. This revision does not erase those differences.

The observed improvements and clean technical checks therefore support continued use and refinement of the skill. They do not support an indistinguishability claim, a numeric similarity percentage, or marking the overall goal complete.

## Verified publication

Implementation commit `e040300ac38ebb53150b2d0a9ca4e4b9e936ad55` is on `main`. [Pages workflow 34702510644](https://github.com/gvillarroel/skills/actions/runs/34702510644) completed successfully, including repository validation, generated-output boundaries and unified Pages validation. All eleven public gallery/source/SVG/viewer files match the expected committed bytes after the documented Pages transforms, and the main catalog links to the example set. The [public gallery](https://gvillarroel.github.io/skills/examples/usefulcharts-style/) contains the reviewed institutional emblem change.

The publication receipt is retained in the machine-readable summary and at `projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/publication-verification.json`. Local synchronization completed with fifteen changed files; the canonical skill and its local installation are refreshed. The private original-reference comparison and publishing study remain local review artifacts.
