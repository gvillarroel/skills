# Renderer grayscale interleave evidence

Date: 2026-10-05. This report covers Mermaid, PlantUML Colorset Renderer,
UsefulCharts Style, ECharts Animated SVG, and Slidev ECharts. The root agent owns
the canonical palette JSON contracts, global checks, isolated forward cohorts,
backlog state, commit, Pages workflow and final publication acceptance. This
report does not turn an earlier development or compactness run into a passing
release run.

The final chosen categorical sequence is:

```text
#9e1b32,
#000000,#828282,#1c1c1c,#9c9c9c,#363636,#b5b5b5,
#333e48,#cfcfcf,#4f4f4f,#e7e7e7,#696969,#f7f7f7,
#ffffff,
#6d1222,#e8002a,#ffccd5
```

The grayscale includes black. Rank twelve grayscale members by WCAG relative
luminance, split them into six darker and six lighter members, and interleave
the two ascending halves. This retains fairly even adjacent lightness
separation. The four allocation buckets are primary red, grays, white, then
remaining colors. Remove only the actual canvas from the fixed sequence before
allocation. Do not dynamically reorder remaining categories for each canvas.

All 17 CS1 members, named roles and text-on-fill values are preserved. Numeric
continuous ramps, visualMap range order and bounds, chart data and native named
semantic paints remain independent of categorical allocation. CS2 membership
and allocation are unchanged; PlantUML's existing seven-role CS2 native pool is
not expanded. Named PlantUML kind themes and the preserved C4 role assignments
are not category pools.

## Final source identity

The source-of-truth machine summary is
[renderer-validation.json](../../projects/grayscale-interleave/renderer-validation.json).
The hashes below use the repository isolated harness's exact runtime-copy and
snapshot-digest functions, excluding acceptance examples and dependencies.
Subsequent report refreshes require exact current-source equality with these
sealed snapshots and retain a separate project-owned verification copy.

| Skill | Runtime files | SHA256 |
|---|---:|---|
| Mermaid | 27 | `41df6ce186a032fdfa3cdc36d3248d328a5d2d685a61f756e25c5b5792ff02d0` |
| PlantUML Colorset Renderer | 28 | `83568a94f9dd015ba198601e6e9cf16bb6d89f6d9fb8a1fd34109efa9b86d1f3` |
| UsefulCharts Style | 140 | `0764023afe12531bf1c34b490f98000d646b9858aa0c4df774632a9efdb41d4c` |
| ECharts Animated SVG | 26 | `693eff70b4c02656f601c22df2f1297b3b318c0f9f93e049e1a3e33879fad35b` |
| Slidev ECharts | 46 | `ddf028fe8678e5085c3579a9342a55e4a3cea0eb4682c027ac578cc45dfbff5a` |

Runtime edits consist of compact guidance, the two self-contained ECharts
template sequence literals, PlantUML's CS1 native category pools, and independent
allocator regression tests. Existing palette readers already consume the
canonical solid sequence. The final prose pass also corrected Mermaid's compact
composition reference, Slidev ECharts' visual tokens reference, PlantUML's agent
prompt, and the CS1 theme comment. PlantUML role fills in that theme were not
changed. An exhaustive scan of the five runtime bundles, excluding example
galleries and dependencies, found no remaining old separate-black priority
phrases.

## Focused checks

| Command | Observed result |
|---|---|
| `uv run --script skills/mermaid/scripts/test_native_solid.py` | PASS, 21 tests |
| `uv run --script skills/plantuml-colorset-renderer/scripts/test_native_styles.py` | PASS, 21 tests |
| `uv run --script skills/plantuml-colorset-renderer/scripts/test_ditaa_styles.py` | PASS, 12 tests |
| `uv run --script skills/usefulcharts-style/scripts/test_palette_contract.py` | PASS, independent literal/canvas/text contrast/overflow matrix |
| `uv run --script skills/usefulcharts-style/scripts/test_chart.py` | PASS, 27 tests |
| `uv run --script skills/echarts-animated-svg/scripts/test_arrow_options.py` | PASS, independent sequence/canvas/capacity tests, 216 backing contrast cases, supplied quantitative ramp preservation |
| `uv run --script skills/slidev-echarts/scripts/test_arrow_options.py` | PASS, independent sequence/canvas/capacity tests, 216 backing contrast cases, supplied quantitative ramp preservation |

Native conceptual graph checks were run with these commands:

```powershell
uv run --script skills/echarts-animated-svg/scripts/test_concept_graph.py --output projects/colorset-gray-interleave/artifacts/reviews/echarts-native
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output projects/colorset-gray-interleave/artifacts/reviews/slidev-echarts-native
```

The original bulky captures remain in those ignored historical artifact
directories. Small complete JSON reports were copied into the stable current
project:

- `projects/grayscale-interleave/artifacts/reviews/renderer-native/echarts-animated-svg-test-report.json`: PASS, 8 cases. Chromium checked full labels and complete heads, explicit canvas preservation, repeated geometry and brace/XML captions. Expected layout probe rejections produce no final artifacts; final, invalid-input and unexpected parser errors still fail.
- `projects/grayscale-interleave/artifacts/reviews/renderer-native/slidev-echarts-test-report.json`: PASS, 10 cases. Also covers native delivery/resize/restore/replay/reduced states, actual glyph/backing clearance against every shaft and head, requested 90×40 fixed rectangles, no-safe-caption-placement rejection and hard native crossing gates.

Original workflow PNGs were manually reviewed. Red, black, middle gray and the
following interleaved categories retain readable black/white labels, visible
complete heads and independently attributable normal, return and branch routes.
These are scoped native checks, not blanket certification of arbitrary outputs.

## Narrow fixture regeneration and native review

The Mermaid narrow rebuild reused the existing project helper:

```powershell
uv run --script projects/colorset-priority/scripts/rebuild_mermaid_cs1.py --jobs 1 --staging-id gray-interleave-cs1
uv run --script skills/mermaid/assets/examples/mermaid-max-complexity/scripts/validate_gallery.py --report projects/grayscale-interleave/artifacts/reviews/mermaid-gallery-validation.json
```

The build completed all 31 CS1 patterns and preserved all 95 CS2 resources byte
for byte. The validator passed 31 families and 62 source/static/animated pairs.
After C4 preservation, 27 of 31 native static SVG geometry signatures match the
qualified baseline exactly. Four existing generator differences are explicit:
block uses the already adopted compact defaults; class and requirement contain
stochastic hand-drawn separator control points with the same label, body and
endpoint positions; Gantt's date-dependent today marker moved while axis data
and task spans stayed fixed. The XY chart's native quantitative geometry matches
the baseline exactly.

PlantUML was rebuilt narrowly using its pinned native renderer and the existing
single-executable wrapper. The successful build regenerated only CS1 ArchiMate
SVG, chart SVG and ditaa PNG plus their three render-report entries, preserving
all 33 CS2 resources byte for byte. Native geometry stayed fixed. A first local
CLI invocation that incorrectly supplied a multiword Java command to the
single-executable option is retained as failed development evidence; the
successful wrapper invocation is not relabeled as that first attempt. The
project helper is now
`projects/grayscale-interleave/scripts/renderer-rebuild-plantuml-cs1.py`.

The native review command is:

```powershell
uv run --script projects/grayscale-interleave/scripts/renderer-review-fixtures.py
```

The final native JSON and viewport captures are under
`projects/grayscale-interleave/artifacts/reviews/renderer-fixtures-final/`.
Manual changed-frame review passed PlantUML ArchiMate, chart and ditaa; Mermaid
flow, Gantt, block, class, requirement, mindmap, treemap and XY chart retained
complete readable labels, expected black/white contrast and applicable heads.
UsefulCharts acceptance fixtures explicitly use CS2 and do not require a new
category regeneration. Slidev ECharts' acceptance component imports its own
canonical template and uses unchanged CS2.

The newly regenerated native C4 was rejected for overlapping relationship
captions and insufficient label contrast on medium gray. Since its source body
and named role assignments are unchanged, the exact previously qualified
source-bound C4 source/static/animated bytes and manifest entry were restored.
The preserved bottom `Serves gallery assets` caption touches the Documentation
Browser body; this preexisting limitation remains explicit. The rejected native
rebuild is retained and is not an accepted new result. Evidence is
`projects/grayscale-interleave/artifacts/reviews/c4-preserved/preservation-proof.json`.

Every baseline comparison in the project C4/ECharts/fixture diagnostics is now
pinned to `daaee75353c63ed6dde204d57cfdbae6b9936586`, the qualified baseline HEAD
before this grayscale change. Legacy evidence keys containing `HEAD` refer to
that fixed baseline, not whichever commit happens to be checked out later.

## ECharts committed gallery decision

The two preexisting uncommitted ECharts gallery files are preserved exactly:

| Working draft | SHA256 |
|---|---|
| `index.html` | `4a14dd301f49060991a38f99953347e3922411e4b05ca3405ad890084f7c2dc7` |
| `scripts/build-gallery.mjs` | `bf7c68a9a14ccb62ffbe007cb8c9c44dbd16deba8cba62af884186a303d451f8` |

The qualified baseline builder was reproduced in an isolated project with the
current canonical template/palette. Its SHA256 is
`fbcb66452c3ecc2329eb2b0534324f30eea15b0a707128977a04c8b0c893b49d`.
The isolated generated index is
`8d105d5603f270a0fe26564ec108b37f37ef7cd688007122181ba0a26546c752`.
The native verifier, all 43 cards, replay and reduced-motion checks passed.
All profiles are explicitly CS2. Seven original representative native captures
were manually reviewed for the scoped palette/contrast result. The network
graph is undirected; no arrowhead presence is claimed for it. The tree retains
its baseline label-on-route interaction.

Independent comparison confirms that all 43 embedded native SVG visual
structures preserve paths, transforms, paint, fonts and text against the
qualified baseline. Raw structural attributes are exact for 42 cards; only the
43rd's generated boxplot chart-instance timestamp differs. Evidence is
`projects/grayscale-interleave/artifacts/reviews/echarts-head-native-final/head-native-comparison.json`.

Root therefore decided to preserve the committed ECharts gallery index and
builder. Neither the two working drafts nor the ignored isolated candidate is
staged or committed. The isolated candidate remains proof only. Future CS1
outputs consume the changed canonical template and palette and are covered by
the independent literal and native tests above.

## Exact-commit publication verification

The new project verifier is
`projects/grayscale-interleave/scripts/renderer-verify-publication.py`. It never
uses current working drafts or `dist/pages` as expected content. It loads the
target commit's builder, discovers its copied source routes and ignore patterns,
and replays exact committed CDN, catalog metadata, favicon, body metadata,
legacy redirect and text normalization transforms. It verifies all resources
in affected copied galleries, including complete SVG/HTML galleries. Canonical
palette definitions not served by Pages are explicitly classified as exact
commit GitHub raw-source checks, rather than invented Pages routes.

Compiled Slidev and Three.js bundles require the artifact of an explicitly
named successful Pages workflow whose head SHA equals the target commit. The
verifier downloads that run's sole unexpired `github-pages` artifact, checks
static source expectations against it, and uses it as the expected content for
generated gallery bundles. Archive paths are checked without filesystem
extraction. The deployed resources must then match those exact bytes.

Before publication, prepare a plan:

```powershell
uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref RELEASE_COMMIT --base-ref daaee75353c63ed6dde204d57cfdbae6b9936586 --plan-only
```

After root's exact Pages run succeeds, verify the new release:

```powershell
uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref RELEASE_COMMIT --base-ref daaee75353c63ed6dde204d57cfdbae6b9936586 --workflow-run PAGES_RUN_ID
```

The expected SHA and workflow run are mandatory release provenance. A byte
mismatch, missing resource, incorrect workflow SHA, absent or empty generated
gallery entry page, or mismatched declared archive digest fails. An orphan JS
asset cannot substitute for a compiled gallery's `index.html`. Root retains
ownership of selecting and verifying the exact GitHub
workflow run and of final publication acceptance.

The verifier's self-test passed correct exact bytes, one added byte rejected,
missing resource rejected, committed CDN/metadata transforms and owned server
lifecycle cleanup. Additional deterministic artifact cases accept a nonempty
entry page, reject an orphan script or empty entry page, and reject a mismatch
against a declared artifact digest:

```powershell
uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --self-test
```

A development end-to-end check against the already published baseline also
passed, including exact workflow artifact provenance and all 543 expected
resources with zero deployed mismatches and zero source/artifact mismatches:

```powershell
uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref daaee75353c63ed6dde204d57cfdbae6b9936586 --base-ref 6d8867106c66b1acdd479f874cbc7763d502b948 --workflow-run 37265922899 --output-dir projects/grayscale-interleave/artifacts/reviews/publication-verifier-development-baseline-final
```

The final baseline integration also verifies the artifact's declared SHA256 and
the three compiled gallery entry pages. The earlier development report remains
retained in the sibling `publication-verifier-development-baseline` directory.
This is development proof that the verifier handles the known baseline; it is
not publication acceptance for the new grayscale commit. That final commit and
its workflow have not yet been supplied at this report's completion. Root's
release cohorts, repository gates and final publication evidence are recorded
separately.
