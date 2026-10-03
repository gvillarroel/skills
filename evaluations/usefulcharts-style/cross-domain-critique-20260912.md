# Cross-domain diagram critique and space reuse

Date: 2026-09-12, America/New_York. The skill remains `validating` for the broader
reference-density and stylistic-parity requirements.

Three sourced subjects were actually rendered, inspected and revised: Research
UNIX/BSD releases, musical-instrument classification, and historical Mars launch
campaigns. The resulting [comparison gallery](../../projects/usefulcharts-cross-domain/artifacts/index.html)
contains the before/after images, editable SVGs, offline viewers, PDFs and source
JSON. The local server is `http://127.0.0.1:8768/index.html`; the gallery also works
from its ZIP after extraction. These are project studies, not published Pages
examples. No public example source or catalog was changed.

## Observations that changed the skill

| Case | Observed first failure | Repair | Preserved information | Measured result |
| --- | --- | --- | --- | --- |
| UNIX/BSD | Geometry passed, but the long central release chain left most of the upper and middle width empty. | Balanced family outlines; dates beside names; local branches plus paired, typed references between panels. | 47 records, 51 relationships, qualified dates and all supplied record notes. | 1146 × 3164.19 to 1148 × 2363.48; 25.18% less total canvas area. |
| Instruments | The 71-record rank tree exceeded the renderer's canvas limit. Its first printable panel version still put codes above every name and left a large lower-right gap. | Inline codes, content-sized roots and balanced panels; a reading guide occupies the shorter column's released pocket. | 71 categories, 66 classification connections and all selected identifiers/notes. | First printable outline: 1328 × 3555.68 to 1148 × 2131.92; 48.17% less area. |
| Mars | Program-specific tracks and a short horizontal scale stacked neighboring launches into 15 rows. | A shared track pool; comparison of seven uniform scales at unchanged type; a sourced reference inset in an independently verified empty pocket. | 32 launch campaigns, 52 dated event marks and six component operating intervals. | 15 to 9 tracks, five shared across programs; 2990 × 2984.75 to 4285 × 2037.5. Total area falls only 2.17%, despite the much larger height reduction. |

The area comparison retains each selected node and edge inventory; no record was
discarded to obtain those reductions. Counts are not a completed knowledge-density
census. Repeated headings, repeated reference endpoints, drawing segments and
generic release notes are not additional useful facts. The taxonomy has no
temporal anchors: its codes must never be counted as dates.

The BSD revision is easier to browse locally and fills the three vertical thirds
more evenly. It also changes the reading cost: a cross-family path requires a
numbered lookup instead of a continuous cable. The instrument revision removes
the most conspicuous blank tail and places the caveat about acoustic instruments
and pickups beside the classifications it qualifies. Its selected electrical
subdivisions remain shallower than several acoustic branches. The Mars revision
has a clearer horizontal form and more useful local stacking, but its middle and
lower body remain unevenly occupied. It is retained as a chronology prototype,
not accepted as a reference-density or aesthetic-parity result.

The new reusable route is [compact outline panels](../../skills/usefulcharts-style/references/panel-outlines.md),
implemented by `create_panel_poster.py` and `audit_panel_poster.py`. It preserves
visible labels, identifiers and notes; validates local forests; retains extra
parents through explicitly typed portals; packs measured panels; and exports
the actual SVG/source/audit bundle together. The input can be replayed from the
emitted source. Nine deterministic cases cover data copying, qualified fields,
paired references, column reuse, cycles, extra parents, missing endpoints,
unsupported rich objects, contrast and a narrow-but-readable layout.

[Shared calendar guidance](../../skills/usefulcharts-style/references/shared-time-rows.md)
now compares total area as well as track count when choosing a uniform scale. It
also searches free rectangles from the plot top and occupied bottoms instead of
assuming all space before the last record is unavailable. The required x-as-time
route remains separate from schematic outlines.

## Source and factual boundaries

- BSD uses the official [FreeBSD family-tree source](https://cgit.freebsd.org/src/tree/share/misc/bsd-family-tree).
  The selection ends in 1995. Conflicting early dates retain ranges; 4.1bBSD
  remains visibly undated. The graphic is schematic lineage, not elapsed time.
- Instrument codes use the [MIMO 2011 author-hosted classification](https://biblio.ugent.be/publication/01HN30DTX2BZYYEVXRG7Q7M06Q).
  Selected labels are abbreviated and deeper categories are omitted. The current
  diagram is an original factual selection, not a reproduction of the PDF pages.
- Mars uses the [NASA Mars 2020 landing press kit](https://mars.nasa.gov/system/downloadable_items/45585_mars_2020_landing_press_kit.pdf),
  pages 69–70. This historical 1960–1999 launch selection does not replay the
  press kit's obsolete future plans as actual missions. Some day-level table
  entries conflict with mission histories, so the graphic deliberately uses
  years. A campaign can carry several vehicles: the two Viking campaigns retain
  separate orbiter/lander intervals. An encounter endpoint is not a retirement
  date, and an unknown end date is not invented.

An obsolete instrument-classification URL returned a valid two-page PDF of a
WordPress homepage. It was rejected after inspecting its subject; the correct
26-page author's copy was located and retained. The information-design guide now
requires checking actual subject and edition after a successful fetch. Source
PDFs, text extracts, URL/hash manifest and rendered source pages remain under the
project's ignored `artifacts/sources/`. The failed download is retained separately
and is not part of the valid three-source manifest or deliverable ZIP.

## Independent artifact verification

The [independent result](../../projects/usefulcharts-cross-domain/artifacts/reviews/independent-checks.json)
compares the final node/edge arrays with the original project inventories,
checks actual calendar geometry independently from the renderer's x metadata,
follows paired HTML links, exercises zoom, verifies a single PDF page and all
PDF record labels, and checks the context pocket against mission footprints.
All three final artifacts pass. Final PDFs were additionally rendered with
PyMuPDF and visually inspected; their selectable text, symbols and layout match
the SVG compositions. A cropped Mars preview initially exposed a percentage-sized
background problem; the project background now uses fixed canvas extents.

| Final artifact | Text elements | Minimum contrast | Additional independent evidence |
| --- | --- | --- | --- |
| BSD | 176 | 4.88:1 | Six paired-reference clicks; all 47 PDF labels; three PDF fonts. |
| Instruments | 158 | 5.03:1 | All 71 PDF labels; three PDF fonts; readable lower-right guide. |
| Mars | 162 | 9.36:1 | 52 exact calendar marks; six component intervals; all 32 PDF labels. |

The gallery passes HTTP, link, six-preview-image, JavaScript, 430-pixel mobile
overflow and offline checks. The ZIP contains the final editable bundles,
comparison previews, verification summaries and the bundled font license.

## Isolated runtime evidence

All runs use Pi 0.84.2, high reasoning, a fresh runtime-only skill copy, exact
required output paths and strict JSON mode. The unchanged naturalistic
[museum prompt](../pi-prompts/usefulcharts-panel-outlines-forward.md) supplies
32 synthetic records, 29 containment links and two differently typed cross-family
links. The [independent checker](../contracts/check-usefulcharts-panel-outlines.py)
imports no evaluated skill implementation. It verifies the supplied semantics
and actual visible fields/bounds in a fresh browser.

| Cohort | Runtime | Strict execution | Independent final artifacts | Direct agent image review |
| --- | --- | --- | --- | --- |
| Spark A, IDs ending `-1` through `-3` | `b8b697f1f496e2c3ecc07faaf1199e1442f320084388fc4070f6106472b351af` | 0/3 | 3/3 | Unavailable in this model runtime. |
| Spark B, IDs ending `-b1` through `-b3` | `9d4c375aa07c4cadee886d632bae639efe7ba0cdb71f00849fa6b74aebcf1bb6` | 0/3 | 3/3 | Unavailable; geometry/ASCII attempts are not pixel criticism. |
| Preregistered Luna probe, IDs ending `-luna-1` through `-luna-3` | Same final 124-file runtime as Spark B | 3/3 | 3/3 | All three read the actual PNG and describe the composition. |

Every ID begins `20260912-usefulcharts-panel-outlines`. Both failed Spark cohorts
remain in the evidence. A exposed invalid write/read calls, a rejected same-source
rerender, an overly restrictive minimum width, and faulty auxiliary checks.
Replaying the emitted source is now supported, narrow panels are checked by
measured fit, and the audit's `kicker` field is documented. B still made unrelated
tool mistakes: an unavailable Pillow import, a missing brief read, and a custom
PNG decoder that assumed the wrong format. B3 also read renderer implementation
unnecessarily. These are failed end-to-end runs, not clean release passes.

The local Pi registry reports Spark without image input and Luna with image input.
The Luna exception was recorded in the backlog before dispatch, both to test the
image-review stage and to address the user's earlier Luna question. Its results
support Luna as an executor and visual reviewer of this guided poster route;
they do not establish a general model ranking, arbitrary design ability, or
UsefulCharts parity.

Luna run 1 actually revised the reading guide after seeing its first render to
make the non-merger and uncertain-association meanings explicit. Runs 2 and 3
inspected their initial and final images and accepted their compositions. Manual
review found a small factual error in run 2's prose: it says four supplied detail
statements, while all five supplied detail statements are present in its artifact.
Thus all three technical/visual-execution probes pass, but the prose is not
uniformly error-free. Run 1 also used unnecessary recursive cleanup of its own
generated relative directories; strict tool checks do not certify that cleanup
style. Those trace details are retained rather than hidden by the aggregate pass.

The independent checker initially required a separate `code` field and rejected
Spark A2's combined `A1 Label` representation. The prompt requires both facts to
be visible, not a specific JSON field arrangement. The checker was corrected to
accept either representation while still checking exact code/name pairs and
typed edges. No agent output was edited to obtain that corrected result.

The [compact runtime summary](cross-domain-runtime-summary-20260912.json) retains
runtime digests, exact-output gates, integrity, read paths, selected scope-sensitive
commands and failures. Full manifests, traces, stdout/stderr and copied bundles
remain in the nine ignored run folders. All copied payloads are unchanged. The
successful Luna runs read the entry point and focused references, never acceptance
examples, sibling skills or project artifacts.

## Reproduction commands

```powershell
uv run --script projects/usefulcharts-cross-domain/scripts/build_briefs.py
uv run --script projects/usefulcharts-cross-domain/scripts/build_panel_studies.py
uv run --script projects/usefulcharts-cross-domain/scripts/build_mars.py
uv run --script projects/usefulcharts-cross-domain/scripts/verify_studies.py
uv run --script projects/usefulcharts-cross-domain/scripts/build_gallery.py
uv run --script projects/usefulcharts-cross-domain/scripts/audit_gallery.py
uv run --script projects/usefulcharts-cross-domain/scripts/render_final_pdfs.py
uv run --script skills/usefulcharts-style/scripts/test_panel_poster.py
```

The gallery audit expects `serve_gallery.py` running on loopback port 8768.
The original branch baseline is reproducible with `create_branch_poster.py` and
`projects/usefulcharts-cross-domain/data/bsd.json`. The rejected rank-tree attempt
on `data/instruments.json` reports the canvas-limit failure. The first printable
panel revision is retained, with its complete source and layout, under
`artifacts/revision-1/`.

Representative isolated command; repeat with the recorded fresh run IDs:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-panel-outlines-forward.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20260912-usefulcharts-panel-outlines-luna-1 --expect-output deliverables/poster.svg --expect-output deliverables/poster.html --expect-output deliverables/poster.png --expect-output deliverables/source.json --expect-output deliverables/browser.json --expect-output deliverables/review.md
uv run --script evaluations/contracts/check-usefulcharts-panel-outlines.py evaluations/runs/20260912-usefulcharts-panel-outlines-luna-1/workspace
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20260912-usefulcharts-panel-outlines-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

The corresponding Spark commands omit `--model` and require
`gpt-5.3-codex-spark` in the trace summary. `summarize_runs.py` replays all nine
trace-summary checks and retains their expected nonzero Spark outcomes.

## Final repository and installation checks

Nine panel tests and eight shared-row tests pass. The final pattern-ID,
repository structure, skill independence and payload checks pass; `git diff
--check` reports no whitespace errors. Targeted synchronization refreshed eight
files, and the subsequent check confirms that the local installation matches
all 141 canonical source files. The isolated 124-file runtime digest is unchanged.
No published example, Pages catalog or deployment was changed in this study.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_shared_rows.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/usefulcharts-style --destination .agents/skills/usefulcharts-style --check
git diff --check
```
