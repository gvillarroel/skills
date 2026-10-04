# Colorset 1 Category Priority — 2026-10-04

The user's category priority is primary red, grays, black, white, then the
remaining colors. This revision passes local and public release validation. It corrects the shared
contract, renderer-specific defaults, and published fixtures that bypassed
the category sequence.

The independent expected sequence is:

```text
#9e1b32
#333e48 #4f4f4f #696969 #828282 #9c9c9c #b5b5b5 #cfcfcf #e7e7e7 #363636 #f7f7f7
#1c1c1c #000000
#ffffff
#6d1222 #e8002a #ffccd5
```

Both `sequence` and `solidSequence` expose the complete 17-token order.
An actual canvas token is excluded from categorical bodies on that canvas.
First-cycle bodies remain opaque and borderless; black or white inside text
is selected against the actual body. Only exhaustion permits contrasting
outline variants. Semantic alpha for overlapping regions, source-owned
paints, native line art, and exact-brand artwork preserve their own meaning.

The shared allowed tokens, named roles, text mappings, and Colorset 2 are
unchanged. The independent validator rejects a misplaced secondary red,
black, or white even when palette membership is otherwise complete. This
prevents agreement between incorrectly reordered canonical and copied data
from passing as a correct category contract.

The isolated protocol, prompts, consumer inventory, and literal output
oracle are in [the evaluation bundle](colorset-priority-20261004/protocol.md).
Raw model runs and browser outputs remain under ignored `evaluations/runs/`.
No failed or externally blocked attempt is counted as a pass.

The mandated first Spark dispatches for ECharts, Slidev ECharts, and
vectorization failed before any tool call: the provider does not support
`gpt-5.3-codex-spark` on this ChatGPT account. The three failures and event
streams are retained. Their owning backlog rows now record
`openai-codex/gpt-5.6-luna` as the exception before fresh fallback dispatches.

Representative maintenance commands:

```powershell
uv run --script projects/colorset-priority/scripts/update_priority.py
uv run --script scripts/test-colorsets.py
uv run --script projects/colorset-priority/scripts/rebuild_mermaid_cs1.py --jobs 2
uv run --script skills/mermaid/assets/examples/mermaid-max-complexity/scripts/validate_gallery.py
uv run --script projects/colorset-priority/scripts/prepare_mermaid_review.py
node --experimental-strip-types projects/colorset-priority/scripts/review_mermaid.ts
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --palette colorset1
uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --palette colorset1 --check
```

The Mermaid build regenerates 31 CS1 patterns and preserves the bytes of
95 CS2 source, output, and report files. The gallery validator accepts all
62 static/animated pairs. The independent native-surface review reports no
incorrect inside text, unexplained rims, or actor captions. The procedural
gallery rebuild produces 66 standalone SVGs and its exact regeneration check
has no missing, extra, or changed file.

PlantUML now uses primary red for default categorical bodies. Active
ArchiMate layers and chart mark kinds compress missing roles, so a single
Technology layer or a line-only chart still starts with primary red. Native
JSON/YAML source ports and their straight shaft prefixes move into the
existing gutter when a red body otherwise prevents complete arrow contrast.
Timing adds an opaque same-color label surface and only enough outer-frame
padding to contain it. Semantic data, event coordinates, and remaining
native arrow geometry are preserved. The diagnostic version is
`scoped-solid-v3`.

Both full PlantUML batches pass 29 source records and 55 exported assets,
including the recorded unavailable Chronology case. The 24 default
categorical SVG families contain primary red without prematurely using
dark red, bright red, or pink. All 55 CS2 assets preserve paint and geometry:
28 PNGs are byte-identical and SVG differences are limited to the v3
annotation and canonical line endings. The 56-image browser audit has no
findings, with 548 black/white labels, minimum text contrast 4.5869809,
minimum grouped shaft/head contrast 4.4394444, and minimum ungrouped
connector contrast 3.1327581. All 79 focused tests pass.

D3 corrects actual ordinal, indexed, and hierarchy category bindings in
the gallery, its logo engine, and editable starters. The adapter now
preserves every valid CS1 token before mapping foreign hues, which prevents
the final pink solid slot from being converted to gray. The owning 16-slot
flow and 18-slot wedge regression proves all usable white-canvas solids
precede overflow outlines. Treemap and circle packing use primary-first
family bases and distinct within-family tones; those hierarchy tones encode
children, rather than introducing an additional categorical family.
Dense overlap preserves its region alpha of 0.28, all 100 task identities,
coordinates, memberships and leader endpoints, while its footer receives
a clear caption rail. All five starter modes pass native browser checks
under both palettes, with CS2 category paints retained.

The actual D3 gallery audit passes 25 representative patterns, including
all nine Venn and overlap forms. It checks native body order and paint,
inside text, meaningful alpha, arrow contrast, label and source identities,
and screenshot samples of single, pair and triple intersections. An
independent baseline comparison preserves CS2 paint, geometry, blending,
labels and memberships for the same 25 patterns. Direct inspection of the
treemap and dense-overlap captures confirms distinct child tones and
visible shared regions.

The independent review also identified default ECharts boxplots that used
a foreign blue, which became gray under CS1. Both ECharts consumers now
derive an omitted boxplot color from the category allocator; explicit
supplied colors and the CS2 default remain authoritative. Both focused
category/arrow suites pass all 216 arrow backing cases and the added
default-boxplot/source-color controls.

Native graph review subsequently found that ECharts uses the average of
rectangular symbol dimensions to trim a graph edge. Its arrowhead was
covered by the destination body, despite passing a color-only check. The
two owning modules now apply native post-layout clearance, with normal
runtime integration and actual head/shaft containment checks. The original
native failures remain retained alongside fresh passing contracts.

Failed validation and evaluator repairs remain visible in
[the attempt inventory](colorset-priority-20261004/results.json). These
include the fresh provider failures, original Mermaid missing styled-source
reads, a PlantUML expected-output path mistake, ECharts static-SSR fixtures
that omitted `animation: false`, and D3 authoring preflight or workflow
failures. The Mermaid entry point now explains that `--write` updates its
input in place and that separate source outputs must be copied first.
The original naturalistic Mermaid per-node color oracle incorrectly treated
one process chain as eighteen necessarily distinct categories. Its sealed
failure results remain retained; a separately versioned post-sampling
review accepts legitimate semantic role reuse and is supplemental evidence.
The literal per-slot and overflow contract is unchanged and independently
checked against actual native SVG paint.

The final-r3 D3 naturalistic cohort remains a failed candidate. Its
retained failures include a replacement mini-D3 runtime and manually
allocated overflow, an initial missing SVG description that triggered a
strict tool error, and mobile tiles clipped outside the viewport. A
uniformly applied evaluator repair counts each actual painted body once
when the same category index also appears on its parent group and label;
it does not erase the original reports or remove the other failures.
The owning skill subsequently simplified the general categorical-grid route
with a standalone builder before freezing a new contract and complete
three-run naturalistic cohort.

The grid-r4 candidate uses the new general standalone builder. All four
D3 artifact cases and all ten actual desktop/mobile browser surfaces pass,
including genuine D3, complete labels, readable responsive tiles and late
overflow. Only one of the three naturalistic runs passes strict mode: two
guessed the unsupported `--require-ordered-text` checker flag, then
recovered their valid outputs. Those tool errors remain failures. The
checker subsequently added that general compatibility spelling with explicit
repeatable/pipe-sequence semantics and unchanged order rejection, before
another complete frozen cohort.

The final D3 alias-r5 candidate passes the full strict contract and all
three unchanged naturalistic repetitions jointly, including actual native
browser review, exact outputs, clean read surface, observed model and
immutable copied resources. Its ten desktop/mobile browser surfaces have
no findings. The sampled raw runtime SHA-256 is
`4e96adbd4ffff20121409c695a57274ee06b514b4eb0aab6dafd6c3a92e9c861`.
Earlier r3/r4 failures remain retained with their original denominators;
the final source adds general CLI compatibility without weakening the
ordered-content gate.

The ECharts arrow-clearance-r5 contracts pass strict and artifact gates,
and their native heads now have adequate complete clearance. Their browser
reviews still fail the separately retained median-ink observation: native
boxplots combine the median with the body outline in one path, so matching
the outline to the opaque fill hides the median. A separate native median
segment with maximum-contrast black/white ink now passes native SVG, Canvas,
resting-state and hover-state checks without adding a decorative box rim or
changing statistical data. Both helpers qualify the pinned ECharts 6.1.0
native implementation. The normal gallery renderer and the Slidev example's
option/resize lifecycle invoke them. Unsupported graph geometry is rejected
before mutation. Repeated updates preserve data, body paint and labels.

The focused chart proof covers 144 native graph states per owner, with
minimum complete-head clearance 3.1672348 px and minimum shaft/head contrast
3.1043065:1. Median verification covers 48 SVG states, 40 Canvas states and
408 boundary pixels per owner, with minimum boundary contrast 4.7036747:1.
The actual Slidev acceptance deck builds and its boxplot medians follow
initial rendering, source updates and resizing. The final isolated browser
review independently checks 16 chart surfaces: minimum complete-head target
clearance 3.25 px, shaft/head contrast 3.8253:1, and median/body contrast
7.9047:1 in both resting and hover states. External native axis annotations
are outside this release contract's body-label, arrow and median scope.

The final [release assessment](colorset-priority-20261004/summary.md) accepts
18 of 18 selected runs across nine runtime contracts, including three
naturalistic repetitions each for D3, Mermaid and PlantUML. All 53 attempted
dispatches remain retained. Mermaid's supplemental semantic-role review is
explicitly qualified and does not convert the original indexed per-node
oracle failures into passes. A second read-only reviewer independently
recomputed selected payload identities, trace gates, repetition counts and
the retained attempt inventory without modifying evidence.

Final local gates pass: pattern IDs (1,222 IDs), skill structure, standalone
independence, payload checks, Colorset validation (34 skills, 30 palette
copies, 672 artifacts), palette scope (31 JSON files), Pages format and output
boundary tests, and whitespace review. Pages builds 648 files, and local
skill synchronization preserves additional local files and matches all
10,253 canonical files. Model runs retain their immutable raw CRLF resources.
The actual [staged Git binding](colorset-priority-20261004/git-payload-bindings.json)
passes all nine skill inventories (526 runtime files), with zero findings.
Only listed CRLF-to-LF normalization separates copied resources from Git
blobs; meaningful content and complete runtime inventories match.

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/validate-colorsets.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/test-pages-output.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py --check
uv run --script evaluations/colorset-priority-20261004/bind_git_payloads.py --ref INDEX
uv run --script skills/echarts-animated-svg/scripts/test_graph_arrow_geometry.py
uv run --script skills/echarts-animated-svg/scripts/test_boxplot_medians.py
uv run --script skills/slidev-echarts/scripts/test_graph_arrow_geometry.py
uv run --script skills/slidev-echarts/scripts/test_boxplot_medians.py
```

The first source release is
[`8b829ad8816f7736b0916b916b642e5328d9ab2d`](https://github.com/gvillarroel/skills/commit/8b829ad8816f7736b0916b916b642e5328d9ab2d).
Its [exact-commit Pages workflow](https://github.com/gvillarroel/skills/actions/runs/37226186062)
completed successfully. All nine runtime bindings also pass against that
commit, with unchanged identities and complete file inventories.

The public resource verifier initially compared raw Git HTML with published
HTML after whitespace normalization alone. Five of 222 resources differed
because the committed builder adds catalog metadata/favicon links and
rewrites local D3 dependency URLs. Those source-only oracle failures are
retained in `projects/colorset-priority/artifacts/manifests/publication-source-only-v1.json`
and ECharts' `report-source-only-v1.json`. The corrected project-only oracle
loads the exact committed builder, replays its literal CDN patches and
metadata/normalization functions, and compares every resulting byte. All
222 resources pass. The builder SHA-256 is
`40e8c100cba494ee5dca472bb640821cb3d64135b5ac48bc552ca391f28a11f7`.
The ECharts published HTML SHA-256 is
`69799ea4cee42620b1530c2267669c958b30e4e4ab2d21d1ecb440d819f89c3e`;
it exactly matches the committed builder transformation of the selectively
reviewed source. No working gallery draft supplies expected bytes.

The first public Mermaid review covers all 62 static surfaces with zero
inside-text, actor-caption or unexplained-rim findings. The PlantUML review
passes 60 exact resources, 108 desktop/mobile SVG paint parity checks,
56 native assets, and all 16 measurement controls, with zero findings.
Its independent report SHA-256 is
`94526ec278ec1f984af32241eaba4181004f39827614d3e3b89b4072dab1ae82`.
Public ECharts passes 43 cards at both viewports, 24 normal median paint
samples, eight hover bodies, and native undirected graph node/label checks.
Its corrected report SHA-256 is
`55e0cafc5dbf0803beb169c08bf1169a7428f0c9fd037f673cc0a80e52339bdc`.
Directed arrow clearance remains covered by the separate native contracts.

The public D3 paint/data audit passed 25 patterns at desktop and mobile.
Manual inspection then found a mobile presentation failure that its old
gate omitted: a shared 880 px minimum width clips the dense-overlap scene
inside a 370 px card. That report remains retained. The fixture correction
now provides a fitted overview and readable, keyboard-accessible expansion
without changing source geometry, tasks, memberships, alpha or paints.
Local desktop and mobile audits pass all 25 patterns with the revised
SVG/card/viewport containment gate. Expanded detail independently reaches
all 100 task labels at approximately 16.5 px, plus all 13 caption/legend
texts and 109 actual glyphs at approximately 26.25 px. Right/bottom panning
reaches its limits and Fit restores identical resting data/geometry/paint
states. The revised gate rejects the still deployed first version with
exactly the dense containment failure. Final local report SHA-256 values
are `e690a5d6f437644e6f73f632e194e43ebd3bcda8220828d7698c07b31fa31e97`
(desktop) and
`c9bab1b1c2b8a510aa1d3e20d6a1e6a183ab78c4ad195ffcffbaac195fba550d`
(mobile). The CSS correction is scoped to the dense CS1 fixture.
The runtime payloads remain frozen; this correction changes only the
acceptance fixture and project verification tools.

Only the reviewed baseline-plus-native-mark ECharts gallery blobs were
committed; unrelated working gallery edits remain preserved.

```powershell
uv run --script projects/colorset-priority/scripts/audit_d3_gallery.py --viewport desktop --artifacts projects/colorset-priority/artifacts/d3-gallery-fit-local/desktop
uv run --script projects/colorset-priority/scripts/audit_d3_gallery.py --viewport mobile --artifacts projects/colorset-priority/artifacts/d3-gallery-fit-local/mobile
uv run --script projects/colorset-priority/scripts/verify_publication.py --expected-ref <exact-release-commit>
node --experimental-strip-types projects/colorset-priority/scripts/review_mermaid.ts --published
node --experimental-strip-types projects/colorset-priority/scripts/audit_public_echarts.ts --expected-ref <exact-release-commit>
node --experimental-strip-types projects/plantuml-style-repair/scripts/audit_native_gallery.ts --phase <release-phase> --published --expected-ref <exact-release-commit> --require-clean
```

The final visual source release is
[`d9140f7eb985fc8114a9330344f2ab88239e432a`](https://github.com/gvillarroel/skills/commit/d9140f7eb985fc8114a9330344f2ab88239e432a),
deployed successfully by
[Pages workflow 37227216666](https://github.com/gvillarroel/skills/actions/runs/37227216666).
Its nine exact Git runtime bindings pass all 526 files with zero findings;
only commit-reference fields differ from the first binding report. Both
source commits preserve identical accepted runtime identities.

Final public checks pass:

- All 223 changed published resources match the exact committed builder's
  expected output bytes, including the mobile CSS correction. The builder
  identity and ECharts HTML identity remain unchanged.
- D3 passes all 25 patterns at both 1440 px and 390 px, including actual
  overview containment, 100 task labels, 109 caption/legend glyphs, expansion,
  panning and Fit restoration. All 18 arrow records per viewport have
  contrast of at least 3.072:1; 26 native intersection pixel samples retain
  distinguishable alpha blends. Public desktop report SHA-256:
  `75d76b014db41f558f40b603144c7b201743c5d1228bf29805f1cef990d605b9`.
  Mobile report SHA-256:
  `fa57346248ecbfcbb7cc798fecc25ef48d470808d006d955407f851ae54d73f2`.
- Mermaid's repeated public review accepts all 62 static surfaces with zero
  inside-text, actor-caption or unexplained-rim findings.
- ECharts repeats 43 cards at desktop/mobile, 24 median paint samples and
  eight hover bodies, with zero findings and exact committed-builder bytes.
  Report SHA-256:
  `d2541cd5fc764abb22b0ecafd459317a289ff84aa23f3c9363bbf63ab5ed43b8`.
- PlantUML repeats 54 SVGs and two PNGs, 60 exact public resource bindings,
  108 desktop/mobile SVG paint-parity checks, 224 local/public aspect checks,
  and all 16 controls, with zero findings. Report SHA-256:
  `1d8e98962e36056daa4f323d188546c98ee57bb056c60cf3fad4dd77e99800f7`.
  Eight byte-bound public mobile key-card captures also pass direct review,
  including timing, JSON/YAML ports, ArchiMate and Ditaa. Capture proof
  SHA-256: `eab0093de341ea69ae135aa9a2f9822ba1576e9aa9474f87c696f983c6345939`.

The final fixture rebuild, pattern IDs, skill validator, standalone
independence tests, payload checks, Pages metadata validator and local
installation check pass after the mobile fix. All 10,253 canonical local
files match. The release keeps the isolated 18/18 accepted runs and all 53
retained attempts unchanged. External native chart annotations retain the
previously documented scope limitation; no broader annotation-contrast pass
is claimed.
