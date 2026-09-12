# UsefulCharts-style institutional and compact composition revision

Date: September 11, 2026 local time; some executions occurred on September 12 UTC.
Status: **validating**. Visual parity with the official references is not established.

This revision responds to the user's rejection of the previous aesthetic result.
It changes both the reusable skill and the authored acceptance posters. Earlier
[topology evidence](topology-revision-20260911.md) remains intact; its provider-quota
failure no longer describes the current evaluation situation.

## Reusable changes

- Replace the institutional fixture's repeated name/type sequences with 141
  individually authored fictional records and 171 explicit relationships. Dates
  and predecessors precede placement; neither is inferred from coordinates.
  Distinguish closures, continuations, mergers, research groups and public bodies.
- Promote [institutional composition](../../skills/usefulcharts-style/references/institution-composition.md)
  into the bundle: compose local stories, reclaim space after endings and reserve
  deliberate influence corridors. Repair the mechanical-arts merger and the
  route into the later optical tradition instead of accepting a long router detour.
- Add a [compact lineage route](../../skills/usefulcharts-style/references/compact-lineage.md)
  and a data-only template. Automatic placement measures every rank, uses larger
  default type for at most 30 records, honors source categories through mergers
  and exports resolved centers for later authored refinement. Small editorial
  canvases may be shorter than the old 1200-unit minimum.
- Make runtime discovery cheaper: select one route, execute the documented CLI,
  and read implementation/tests only for maintenance. A small institutional
  merger is explicitly covered by automatic layout.
- Bundle two unmodified, documented source illustrations: Pearson Scott Foresman's
  observation scene and a 1904 sextant drawing. Their native aspect ratios and
  provenance are embedded. Increase their optical presence in the institutional
  poster; the timeline uses a rectangular observation vignette.
- Give selected timeline events and periods stronger typographic emphasis.
  Preserve all 50 periods, 55 transitions and 60 dated events. Break era rules
  around complete event bounds and start them beyond the year gutter.
- Expand browser auditing to detect illustration/node, illustration/text,
  illustration/bridge and era-rule/text collisions. These checks found real
  defects before the final repairs; a clean audit is not a visual parity score.

## What the images demonstrate

The current source-backed previews are in
`projects/usefulcharts-style/artifacts/images/compact-<poster-id>.png`.
The local [reference / previous / current comparison](../../projects/usefulcharts-style/artifacts/reviews/compact-comparison/index.html)
uses published revision `8777f9a76bcf69f60026dbb40e6698d9da48e392` as its prior version.
Reference images remain local critique material and are not published with the gallery.

The independent reviewer rejected parity twice while recognizing substantial
improvement. The final independent review before the last production repairs is
retained at
`projects/usefulcharts-style/artifacts/reviews/institutions-final-independent-review.md`.
It identified long sparse continuations in the lower lineage, inconsistent artwork
weight, a rule crossing the year 1200, visible gray photographic rectangles and
weak event emphasis beside broad timeline ribbons.

The subsequent author review confirms the year-rule repair, larger observation
drawings and stronger selected event/period labels. The lower lineage still has
long influence corridors. Several museum photographs still have rectangular
backgrounds. The five-region timeline remains less finely articulated than the
official world-history reference. These are open design differences, not evidence
that more records or a higher aggregate technical score would establish parity.

## Deterministic checks

| Check | Result |
| --- | --- |
| Classic renderer tests | 26 passed |
| Editorial renderer tests | 31 passed |
| Deliberately corrupted SVG mutations | 11 detected |
| Genealogy source-backed browser audit | 561 people, 323 paths, 1144 text runs; zero findings |
| Institutional source-backed browser audit | 141 institutions, 171 paths, 579 text runs; zero findings |
| Timeline source-backed browser audit | 50 periods, 55 transitions, 60 events, 380 text runs; zero findings |
| Minimum measured contrast across the three posters | 4.949 |
| Responsive gallery / zoom | 1440 and 390 pixels; three cards; no overflow or page errors |
| Embedded image dimensions | 17 genealogy, 2 lineage and 6 timeline placements checked |
| Evaluation harness regression suite | 12 passed |

Commands, run from the repository root:

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json --report projects/usefulcharts-style/artifacts/reviews/compact-atlas-of-inquiry.json --png projects/usefulcharts-style/artifacts/images/compact-atlas-of-inquiry.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/compact-mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/screenshots/compact-final
```

The same source-backed browser command was run for the other two poster IDs.
The compact template also renders and audits successfully at 1000 × 766.92 units
with seven records and all seven explicit edges.

## Isolated evaluation and the image-capability finding

The naturalistic [institutions prompt](../pi-prompts/usefulcharts-institutions.md)
contains all 14 fictional records and 16 links, requests meaningful category color
and two emphasized mergers, and requires six exact output paths. Every evaluated
bundle is read-only, runtime-only, excludes acceptance examples and runs without
ambient context. Raw outputs and failures are preserved unchanged.

Five executed Spark attempts were made: v7-1, v8-1 and v9-1/2/3. Every attempt
created all six outputs and preserved its skill payload. None passed strict
validation. The first output used a mostly empty 1800 × 2700 page and changed the
mergers to an unrelated green category. After the compact-layout changes, the v9
outputs retained the correct families, dates and links and used much smaller pages.
Tool errors and unnecessarily broad reads still prevented acceptance.

An important evaluator limitation was then verified. Spark's image-read result
explicitly says: "Current model does not support images. The image will be omitted
from this request." The local `pi --list-models` registry reports `images: no` for
`openai-codex/gpt-5.3-codex-spark` and `images: yes` for `openai-codex/gpt-5.5`.
Counting an image content block without inspecting this omission notice would
falsely credit visual inspection. The independent contract was corrected to reject
omitted images; the v9-1 preliminary artifact pass is superseded accordingly.

A scoped GPT-5.5 exception was recorded in `SKILLS.md` before running the visual
cohorts. This changes the evaluator model, not the task or its acceptance criteria.
The three v10 GPT-5.5 runs did receive and inspect their final PNGs. All retained
the required source records and images, but all failed strict execution due to
earlier render/audit errors. Two also missed the compactness or type-size check.
Their traces showed that small institutional mergers were being routed directly
into manual composition. The v11 entrypoint explicitly begins these cases with
the compact automatic route, then allows authored repair after the first preview.

The final v11 cohort passes **3/3 strict runs and 3/3 independent artifact
contracts**. All three use the identical 55-file runtime payload, SHA-256
`dcbbe7a98e22b1fd0c8aaec2b4065ded565d2ef9edcab31c8d7d37aecb4ecaa9`.
They preserve all 14 records and 16 links, create the six exact files, receive
their PNG through supported image input, make no forbidden Git calls, leave the
copied skill unchanged and produce zero tool errors. Runtime reads are confined
to the entrypoint, compact contract/template, relevant artwork provenance and
occasionally the editorial contract; no implementation, test or acceptance-gallery
reading is needed. Inspecting generated task outputs is recorded separately from
the skill read surface.

| v11 repetition | Canvas | Duration | Strict | Artifact contract |
| --- | --- | ---: | --- | --- |
| GPT-5.5 / 1 | 1278 × 1142.72 | 104.092 s | Pass | Pass |
| GPT-5.5 / 2 | 1278 × 1176.56 | 91.342 s | Pass | Pass |
| GPT-5.5 / 3 | 1278 × 1188.8 | 86.967 s | Pass | Pass |

The author inspected all three outputs, not just the best repetition. They have
clear family identity, legible dates, distinct influence and structural paths,
and stronger treatment for the two mergers. Their small scale is appropriate to
this case. Some wording remains repetitive and the observation drawing is still
optically lighter than the geometric emblems. This limited successful cohort
does not establish visual parity for the dense acceptance posters.

Full run-by-run commands, payload hashes, errors, read surfaces and independent artifact
findings are retained in [the compact evidence](institution-revision-summary-20260911.json).
The summarizer regenerates this evidence without modifying task outputs:

```powershell
uv run --script projects/usefulcharts-style/scripts/summarize_institution_revision.py
```

The isolated command for each vision run is:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --model openai-codex/gpt-5.5 --run-id usefulcharts-institutions-v11-20260911-gpt55-1 --prompt-file evaluations/pi-prompts/usefulcharts-institutions.md --mode json --strict --forbid-event-command-regex "(?i)\bgit\s" --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-institutions-v11-20260911-gpt55-1/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
uv run --script evaluations/contracts/verify-usefulcharts-institutions.py evaluations/runs/usefulcharts-institutions-v11-20260911-gpt55-1 --output evaluations/runs/usefulcharts-institutions-v11-20260911-gpt55-1/independent-contract.json
```

Repetitions use fresh run IDs ending in `-2` and `-3`. The independent contract
checks named records, visible dates, all links, family identity, major-merger
emphasis, source illustration identity, compactness and a supported preview read.
It is an acceptance check for this case, not a general aesthetic similarity metric.

## Source illustrations and rejected material

- [Observation with a mariner's astrolabe](https://commons.wikimedia.org/wiki/File:Astrolabe_PSF.svg),
  Pearson Scott Foresman public-domain dedication, source revision 1115707816.
  Unmodified SVG: 89,342 bytes; SHA-256
  `c9ca9c4cfcc02aaa389e5bc1d1b659c39e2d94605069c1239322205b91d4b302`.
- [Sextant, Nordisk familjebok](https://commons.wikimedia.org/wiki/File:Stronomiska_instrument,_Sextant,_Nordisk_familjebok_transparent.png),
  1904 source, public-domain status documented on the source page, revision
  975234322. Unmodified transparent PNG: 9,083 bytes; SHA-256
  `b2fe0bf2acd852ed3932a7de1c0c51b5977c1fd1e5db5f0403db3dc91a26341f`.

Full identity and rights records ship in `assets/illustrations/provenance.json`.
They are decorative source samples for the fictional histories, not institutional
logos or historical evidence. Two attempted image-generation cutouts had painted
checkerboards in opaque RGB output. They were rejected, retained only in ignored
local evidence and excluded from the runtime bundle and public gallery.

## Release status

The pattern-ID, skill-structure, skill-independence and payload checks pass.
Pages builds into `dist/pages/` with 639 files, 37.08 MiB. Local installation is
synchronized from canonical `skills/` sources. The gallery retains the three
existing stable pattern IDs; no reference artwork is republished.

Keep `validating` until the isolated cohorts, broader family/generalization cases
and actual visual comparison meet the requested standard. A successful small
case would not by itself certify a dense genealogical or chronological poster.
