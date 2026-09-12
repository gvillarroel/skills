# UsefulCharts-style topology revision — 2026-09-11

Status: **validating**. The user requires the skill's output to match the originals in quality and composition. This revision improves reusable composition machinery and the three acceptance posters. It does **not** establish indistinguishability, and the provider usage limit prevented a fresh isolated agent result.

## What changed

- Added family-unit cohort placement for explicitly recorded genealogy. Partnerships form units, parentage determines ordering, and successive cohorts can expand or contract. The render report exports resolved centers for further authored refinement. Small datasets still need a compact canvas.
- Rebuilt the genealogy's source records and topology. It includes substantial contractions and later expansions, cross-family marriages, individual lifespans and reigns, understated partnership marks, and later family labels. Dates are generated before layout from parental marriages and succession constraints. The synthetic declaration remains visible.
- Replaced generic institution-name permutations and repeated movement headings with specific fictional places, institutional functions, and distinct founding narratives. Branch icons now retain their field's meaning.
- Rebuilt parallel history around explicit succession, division, union, and uncertain continuity. Added fractional attachment ports and narrow transition widths. Filled bridges have one semantic center path, without a competing orthogonal fork.
- Replaced repeated event snippets with 60 distinct dated headlines and consequences. An optional 1850 map adds historical cartographic context; its original bytes and public-domain source record ship with the skill. Museum objects are decorative samples, not evidence of the fictional events.
- Extended the browser audit to independently check event dates and complete transition polygons. This detected two real fill/text intersections in the candidate; the affected event was recomposed and the final audit passes.

## Current acceptance artifacts

All are editable 1800 × 2700 SVG posters with JSON sources and zoomable HTML viewers. Source files remain under `skills/usefulcharts-style/assets/examples/usefulcharts-style/`.

| Poster | Entities | Relationships | Additional records | Chromium findings |
| --- | ---: | ---: | --- | ---: |
| `aurelian-families` | 561 people | 323 descent/uncertain paths | 261 partnerships | 0 |
| `atlas-of-inquiry` | 191 institutions | 199 branching/influence paths | Distinct family narratives | 0 |
| `five-regional-histories` | 50 dated periods | 55 typed transitions | 60 dated events | 0 |

More records do not imply better design. The timeline deliberately uses fewer, individually authored phases than the previous 78-phase fixture. Readability and explanatory value must be judged from the images.

All three audits preserve source inventories and achieve a minimum measured text contrast of 4.949. The genealogy also passes 566 checks of explicitly dated parent-child pairs: parents precede births, are between 18 and 65 at those births, and are alive at conception/birth within the stated tolerance. Supporting relatives without complete life dates are outside this check; it is not a comprehensive historical or demographic validation.

Local full-page previews, detail crops, browser reports, and reference/previous/current triptychs are retained under `projects/usefulcharts-style/artifacts/`. The comparison entry point is `reviews/topology-comparison/index.html`; it uses previous commit `2d3b2e5d5ce3645c4974e548b23f037334295ae0`. The original comparison evidence is preserved in its earlier folder. Official UsefulCharts previews are local critique material and are not redistributed with the public gallery.

## Visual review and limits

The independent reviewer inspected the previous candidate at whole-page and matched-detail scale. It rejected equivalence: persistent family lanes, synchronized date intervals, and uniform partnership/portrait marks still exposed a template. This revision responded with substantial branching changes, causal life records, lighter partnership marks, and additional interior labels. The current candidate is also inspected separately against the official references.

The final independent critique did not grant parity to any family. It recognized the genealogy's distinct dates, terminal branches, and larger reorganizations; it still requested stronger figure hierarchy, more specific interior landmarks, and tighter use of open areas. The lineage remains systematic: institution types progress in similar steps, and repeated emblems do little to identify individual institutions. The timeline has distinct narratives and legible political relationships, but broad blocks, a conspicuous map, and small rectangular artwork weakened its balance.

The last repair names four specific genealogical courts, caps wide timeline ribbons at 78 units, reflows adjacent events, and reduces the historical-map opacity from 0.20 to 0.12. Current previews and source-backed audits reflect those changes. They address concrete defects but do not resolve all the critique. The final review remains unblinded; the author and reviewer know the skill and source. No numeric similarity score or provenance-identification claim is assigned.

## Deterministic validation

Commands run from the repository root:

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json --report projects/usefulcharts-style/artifacts/reviews/topology-aurelian-families.json --png projects/usefulcharts-style/artifacts/images/topology-aurelian-families.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/topology-mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/screenshots/topology-final
```

The same browser audit was run for the other two poster IDs. Results: **26 classic tests, 22 editorial tests, eight adversarial mutations, and three source-backed browser audits pass**. Mutations include a filled bridge painted over a period and a shifted event date anchor. Responsive gallery widths 1440 and 390, zoom controls, nested-image dimensions, and browser console checks pass.

## Isolated forward attempt

Case: `usefulcharts-cohorts`, a naturalistic family poster with repeated intermarriage, terminal branches, and exact output paths. Model: `openai-codex/gpt-5.3-codex-spark`. Run: `usefulcharts-cohorts-v6-20260911-spark-1`. Local date: September 11; execution began at `2026-09-12T00:48:17.608987+00:00`.

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --run-id usefulcharts-cohorts-v6-20260911-spark-1 --prompt-file evaluations/pi-prompts/usefulcharts-cohorts.md --mode json --strict --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-cohorts-v6-20260911-spark-1/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

Outcome: **infrastructure-blocked**, provider usage limit before the first tool call. All six required artifacts are missing. Valid JSON, observed model identity, and unchanged copied payload are recorded, but they are not a successful task execution. The strict evaluation correctly fails. Its runtime bundle contains 49 files, SHA-256 `4a3703f68d62e80d430c44d6b3e1d1d7b95258dd62693ffeec354a3da4bcf25b`. The copied payload excludes examples and contains no sibling skills.

The final 49-file runtime is SHA-256 `a3e8ef0f612859749d9f8f726d07b0305deffdd42bc6cd58f1792d6b98eb831d`. The only runtime difference after that blocked attempt is the reduced historical-map opacity in `scripts/editorial_poster.py`. Do not present either bundle as forward-test certified or substitute an earlier successful run. The failed run's artifacts were retained without modification; a fresh strict run remains required when the external quota permits execution.

Keep the skill `validating` until fresh strict agent runs and the relevant naturalistic/generalization/boundary cohorts succeed, and until visual comparison no longer exposes the remaining composition defects.

## Source record

The historical backdrop is [Milner's 1850 map](https://commons.wikimedia.org/wiki/File:Milner%E2%80%99s_1850_Map_of_the_World.jpg), source revision 1232330688, marked public domain. The unmodified JPEG is 664,623 bytes, SHA-256 `30ceeeebf9a3597b69c8a0663222667f58cb6a66065e0c72948d0570d46c483d`. Its title, author, year, URL, rights, and intended decorative use are recorded in `assets/maps/milner-1850.json` and embedded into rendered SVGs that use it.

## Repository and delivery checks

`scripts/validate-pattern-ids.py`, `scripts/validate-skills.py`, `scripts/test-skill-independence.py`, and `scripts/check-repo-payload.py` pass. `scripts/build-pages.py` builds the catalog and examples into `dist/pages/` (638 files, 36.78 MiB); the existing Vue dependency warnings are non-fatal. `scripts/sync-local-skills.py` refreshes the ignored local installation. Each command is run with `uv run --script`.

The stable public gallery is [UsefulCharts-style examples](https://gvillarroel.github.io/skills/examples/usefulcharts-style/). The three existing pattern IDs and URLs remain unchanged. Deployment verification is retained locally in `projects/usefulcharts-style/artifacts/reviews/topology-publication.json` after pushing the source commit and observing the Pages workflow.
