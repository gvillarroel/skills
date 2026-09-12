# UsefulCharts-style: separated name panels and measured story composition

Status: **validating**. The broad user objective remains parity of visual quality and composition with UsefulCharts. The improvements below do not establish indistinguishability. All three fresh v15 library runs and the command contract pass strict isolation and independent artifact checks. The unresolved-source control passes exact artifact review in two of three runs and strict execution in one; its failures remain recorded.

## Reference and visible diagnosis

The main institutional reference remains the official [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree). The other two comparison families remain [European Royal Family Tree](https://usefulcharts.com/products/european-royal-family-tree) and [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history). Product previews are local critique material and are not redistributed in the gallery.

At equal display width, the published v13 institutional example used too much colored area for dates and explanatory prose. Dates usually belonged beside the incoming connection; the name deserved the colored panel; historical consequences needed a quieter field. Repeated generic emblems and avoidable route detours reinforced the template appearance. These findings are independent of the geometric audit.

The local comparison is `projects/usefulcharts-style/artifacts/reviews/institution-panel-comparison/index.html`. It preserves all three official/reference/before/after families. The before revision is `a377b870017ac11ad7c33867421257e83324be27`.

## What changed

- Added measured external dates and captions with `detail_position: outside` and an explicit `date_label`. The colored panel contains the name; the full date/name/caption envelope remains an obstacle and sets attachment ports. A separate date cannot silently disappear in an unsupported inside treatment.
- Strengthened the source-backed browser audit to check exact printed details and date expressions as well as record names. Deliberately changed visible dates and captions are detected even when the SVG's metadata still matches the original source.
- Added four unmodified, inspected source illustrations for deliberate white panels: a compass card, meshing cogwheels, a surveyor using a theodolite, and a 1923 printing-press ornament. The bundled provenance records source URLs, rights, intrinsic dimensions, bytes and SHA-256. A microscope source was rejected because its numbered explanatory callouts became clutter at the intended size. Opaque PNG backgrounds are documented, not called transparent.
- Reworked the existing 141-institution mural without adding or removing a record or relationship. Exact names, founding dates, categories, contexts and all 171 typed links match v13. Colored panel area falls from 673,297.50 to 400,386.96 square SVG units, a 40.53% reduction in this measured area—not a similarity score. The final authored composition has 63 geometric crossings, versus 64 in v13; an intermediate artwork revision had 71 and was repaired. Some routes remain long because the supplied histories require distant influences.
- Added `layout: packed` for medium institutional histories. Relative x/y neighborhoods are compacted by measured separation and directed attachment constraints. Names remain readable; coordinates and page dimensions are resolved without scaling type down. A separate category key is automatic. Fixed coordinates, absolute routes and insets stay in the authored workflow. The reusable reference and small runtime template contain the method; acceptance examples are not needed during ordinary use.

The packed route was motivated by a real failed forward result: fifty records and 71 links occupied a 2200 × 3300 page with tiny names and large unused corridors. A local development recomposition preserves the underlying records and links and produces a 1758 × 2478.68 page with 18-unit names and purposeful plain/colored treatment. That local repair is **development evidence**, not an isolated forward pass. Its files are under `projects/usefulcharts-style/artifacts/library-composition-development/`.

## Isolation and failure retention

Image-dependent forward cases use the existing, scoped `openai-codex/gpt-5.5` exception: Spark explicitly omits image input. Command and unresolved-source controls continue to use `openai-codex/gpt-5.3-codex-spark`. Neither the model exception nor the new layout relaxes the task contracts or permits ambient context.

The v14 development runtime contained 64 files, SHA-256 `ba3159980f962c5d152b840e3867b7ce866bdabaf3fb7c9e3a20939de784f75b`. The v15 runtime contains 67 files, SHA-256 `e0d1b0ef459738e58c9520a6f0cea69a43b7ab569c809edb17f64d35849a4236`.

| Attempt | Outcome and classification |
| --- | --- |
| `usefulcharts-v14-libraries-20260912-1` | Cancelled evaluation setup: the original prompt contained an invalid apostrophe in one required ID and an extra table separator column. The original prompt, trace and partial artifacts remain unchanged. This attempt is not a behavioral pass. The corrected prompt has 50 valid IDs and 71 resolved relationships. |
| `usefulcharts-v14-libraries-20260912-2` | All six outputs and the independent 50-record/71-link/approximate-date contract pass. Strict mode fails on four tool errors, including a task script attempted through an external temporary path, an initial overlap and an annotation outside the page. Independent visual review rejects the oversized, sparse composition. This failure motivated the packed route and workspace-relative builder instruction. |
| `usefulcharts-v14-separated-20260912-spark-1` | Correct artifacts and command, but the old harness misread a closing JSON fence as the start of a shell block and expected intervening prose to execute. Classified as a harness failure. The original result remains failed; the parser was repaired with two regression cases. |
| `usefulcharts-v15-separated-20260912-spark-1` | Fresh strict pass on the final v15 payload: four exact outputs, exact shell command, observed Spark model, valid events, zero tool errors, confined reads and unchanged payload. |
| `usefulcharts-v15-libraries-20260912-1` through `-3` | 3/3 fresh strict GPT-5.5 passes, all six exact files, 50 records/71 links, exact date expressions, supported PNG inspection and independent artifact checks. All three final PNGs were also inspected by the author. |
| `usefulcharts-v15-boundary-20260912-spark-1` through `-3` | All three preserve the known identities/dates, retain the unresolved `unknown-42` reference, write `needs-data`, and produce no finished SVG. Trial 1 additionally creates a placeholder person record beyond the supplied inventory; its exact-source check fails. Trials 2 and 3 pass the artifact check. Only trial 3 passes strict execution: trials 1 and 2 perform unnecessary directory/existence probes that return nonzero before writing the requested files. The two failed executions are retained. |

The library case is a new domain with six unequal traditions, multiple mergers, a terminated branch, long influence links and approximate founding dates. It is not the mural acceptance fixture. The evaluator-owned contract is `evaluations/contracts/verify-usefulcharts-libraries.py`; it checks exact source meaning and supported image inspection, not visual resemblance.

The complete ten-attempt record is [the compact evaluation summary](panel-and-packed-revision-summary-20260912.json). There are five strict passes: three library runs, the final command contract and one boundary run. The earlier prompt-setup cancellation, harness failure, visual/agent failure and two boundary execution failures are retained. Every final v15 run uses the same 67-file payload. Normal traces read the entry point, focused references, a small template or provenance manifest and their own outputs; none reads an acceptance gallery, sibling skill or repository document.

The evaluator was also corrected to recognize `child`/`parents` as well as `child_id`/`parent_ids` in an unprescribed review JSON schema. This removes a false rejection of boundary trial 3 without changing its source or relaxing the exact named-parent requirement. Trial 1's extra placeholder remains a real exact-inventory failure.

At equal width, the fresh library outputs improve typography, external date hierarchy and the contrast between major institutions and quieter continuations. Trial 1 is 1680 × 2615.59; trial 2 is 1580 × 3075.44; trial 3 is 1414 × 2874.47. Trials 2 and 3 remain narrow and tall, with long lower publishing/influence corridors. These are visible limitations, not grounds for claiming parity. The unchanged v14/v15 image comparison includes all three fresh outputs at `projects/usefulcharts-style/artifacts/reviews/packed-forward-comparison/index.html`.

## Verification completed locally

- 68 renderer regressions: 26 classic and 42 editorial, including external content, relative-position packing, long labels, mergers, exact categories, geometry and invalid-hint boundaries.
- 14 Pi harness tests, including mixed JSON/shell fences and preserved multiline commands.
- All three mural rebuilds and source-backed browser audits pass. Their preserved inventories are 561 people/261 unions/323 paths; 141 institutions/171 paths; and 50 periods/55 transitions/60 events.
- Nine final institutional SVG mutations are detected, including altered visible dates/captions, stale source revision, removed records, illegible labels and false or detached relationships.
- Desktop 1440px and mobile 390px gallery checks, every viewer's fit/zoom/native scale, seven nested institutional artwork viewports and absence of page errors pass.
- Repository structure, independence, payload and pattern-ID checks pass. Quick skill validation, the Pages build and local installation synchronization pass. Final required gates are repeated after the evidence and backlog edits.

Representative commands:

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script evaluations/contracts/verify-usefulcharts-libraries.py --check-prompt evaluations/pi-prompts/usefulcharts-dense-libraries.md
uv run --script projects/usefulcharts-style/scripts/review_panel_composition.py --output projects/usefulcharts-style/artifacts/institution-composition-v14/source-and-composition.json
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json --artifacts projects/usefulcharts-style/artifacts/institution-composition-v14/final-mutations
```

Each v15 library run uses `scripts/run-pi-skill-eval.py usefulcharts-style --model openai-codex/gpt-5.5 --prompt-file evaluations/pi-prompts/usefulcharts-dense-libraries.md --mode json --strict`, a fresh run ID and `--expect-output` for all six exact `result/` files. Preserve the model, event, read-surface and unchanged-payload gates. Follow each run with the independent artifact checker and a real image review.

## Remaining visual work

The institutional date/name/caption hierarchy is substantially better, but the large mural still has persistent subject districts and several long influence corridors. The genealogy retains broad generational patterns in its lower regions. The dense chronology retains broad ribbon streams. A new medium-history mechanism does not establish parity for these other morphologies. Keep the full objective active and continue comparison at equal whole-page width and equal detail scale.

The cohort review and local synchronization are complete. Publication is pending explicit staging, commit, push and a verified Pages deployment. The currently published revision remains v13 until that verification is recorded.
