# Reflex XY capability atlas

Date: 2026-10-24. Skill: [reflex-xy](../../skills/reflex-xy/SKILL.md).
Status: `validating`. The published example surface and isolated skill-use
cohort are separate evidence subjects. Correct gallery output does not waive
the retained strict runtime failures below.

## Subject and coverage

The executable baseline is `xy==0.0.8`, release commit
`6483032a7947e1f44ced1a560ac08f1025637529`.
The [upstream repository](https://github.com/reflex-dev/xy),
[release](https://github.com/reflex-dev/xy/releases/tag/v0.0.8), and
[official documentation index](https://reflex.dev/docs/xy/llms.txt) were checked.
The atlas indexes the released public surface rather than claiming to exhaust
every possible parameter combination or establish production performance.

- 57 visual mechanisms, each rendered in Colorset 1 and Colorset 2: 114
  interactive HTML charts, native SVGs and native PNGs.
- Cartesian marks, distributions and uncertainty; matrix and density views;
  flows and funnels; polar charts; annotations; scales, secondary axes and
  formatting; linked facets, navigation and selection; symbols, styling,
  animation, named-column overrides and a registered custom mark.
- All 105 names in the released `xy.__all__` are indexed with signatures,
  documentation and coverage status. The supplemental pyplot index contains
  159 public callables. Function coverage distinguishes direct calls from
  execution through a documented factory alias.
- The catalog exposes 19 point symbols, dash presets, curve and scale choices,
  colormap names, native chart DOM slots, axis styling and mark properties.
  An option inventory is not a claim that every option has a dedicated chart.
- Each card has stable `xy-<mechanism>-cs1` or `-cs2` IDs and API/search
  metadata. The main examples index links the atlas. The earlier 12-chart
  colorset gallery and its published IDs remain available.

The initial atlas cohort's frozen runtime profile has 18 files and inventory SHA-256
`9b99fa1c74684f2bb2090d90c75b64b99e004b8103a80bc00249a94c8c8331c8`.
Its source/full profiles have 31 files and inventory SHA-256
`dd7a54ea292af8b808783c852abd259c1aa804c26a2e984453f01a9f421fb2f8`.
These are profile inventory digests, not hashes of an archive. Acceptance
examples are excluded from the runtime profile. No authored runtime file
changed during the eight-attempt cohort.

Manual review then corrected error-bar cap units and stacked-area legend
headroom. That intermediate 18-file runtime digest is
`eaab7a3ee1f03faeb9b6cb0b215edecc64c2fa8d06ec37686022ac8914ae9d8d`;
its 31-file source/full digest is
`e53d0b5f11a36de7c9904d6006d8223cd627add57039d41a99965060228a54be`.
The initial cohort remains evidence for its earlier subject. A separate
focused contract evaluates the corrected uncertainty recipe; it does not
replace failed attempts or certify the unmet broader thresholds.

A later Sankey label-contrast correction uses dark node colors with canonical
white annotation text. Its 18-file runtime digest is
`fc516b8295be4db1319006310e08181d3a9e3d36716b5ac3268e95c7c3151eb7`;
its initial 31-file source/full digest is
`208c1c6e383401f6fffab899281b67a2120e1b143d56b256a39cbbe2a05d687b`.
Its focused contrast contract remains separate from the earlier subjects.
The [intermediate cap-unit contract](errorbar-caps-2026-10-24.md) passes 1/1
strict, independent geometry/trace and manual review. It chose .16-unit cap
half-extents, with .32 full spans and unchanged original task outputs. Two
evaluator-only screenshot/API errors were retained; the corrected capture
method did not repair or relaunch the task.

Final manual mobile review identified a common Cartesian legend placement
problem. The final runtime adds the proven footer recipe to its colorset
reference; its 18-file digest is
`7c045720cd6a24dcab11bcafc57a310868da8093686083a179a2653a75ba360a`.
The final 31-file source/full digest is
`ee6f8943a8a0da3380cdeb103a1e879cb4481d9930228df9974d47ede47364ca`.
The footer contract evaluates this final subject separately.
Inventory digests describe the exact evaluated local Windows payload bytes.
Git normalizes text line endings to LF; publication verification records both
byte identity and LF-normalized identity for downloadable source and rejects
any difference beyond line endings. Each isolated copied payload remains
subject to its own exact byte-integrity gate.

## Reusable corrections promoted into the skill

The new [advanced chart recipes](../../skills/reflex-xy/references/advanced-charts.md)
cover uncertainty, distribution, field and flow mechanisms without requiring
the acceptance gallery at runtime. Six Python fences executed and five
resulting native charts rendered successfully.

The output reference documents a narrow upstream SVG compatibility repair.
Some line-only point symbols receive duplicate `fill` attributes from native
XY 0.0.8. The helper repairs only the recognized `fill="none"` plus matching
hexadecimal stroke case, validates the result, leaves valid SVG byte-identical,
and fails on unrelated malformed XML. Six deterministic controls pass. The
atlas retains malformed originals as text and records every repaired path.
It does not replace native chart geometry with another renderer.

Other promoted guidance covers total grid width for facets, pixel sizes at
chart construction, unambiguous direct color arrays, named axis labels,
scatter-only range-selection geometry, and the separation between static
HTML and Python callback delivery. Final visual corrections moved polar
legends away from plot rims, gave line-only symbols explicit strokes, placed
rotated category labels below ticks, and gave facet headings the intended CSS
specificity.
Manual review also corrected error-bar caps from seven perpendicular
data-axis units to .18; the released wrapper docstring incorrectly describes
pixels. The reference now explains the observed native contract. A clear
y-domain band keeps the stacked-area legend off its opaque upper layer.
Sankey's native labels consume the theme's global `annotation_text`, so its
example and reusable recipe now pair repeated dark canonical node colors with
canonical white text. The native gradients remain visible, node names retain
identity, and native/HTML checks verify the label result.
The reusable Cartesian footer recipe uses `loc="upper left"`,
`anchor=(0,-.18)` and `ncols=3`, with bottom padding 112 at height 480. XY
does not reserve outside legend space automatically, and top padding also
moves the chart title. The recipe preserves data/domains and requires checking
axis-title clearance and canvas bounds at each target size.

## Native, browser and host validation

The Pages build produces 1,180 files across the repository.
The atlas source ZIP contains 13 portable source/helper files and supports
isolated regeneration. HTML/SVG/PNG downloads cover all 114 cards; native
PDF/JPEG/WebP samples cover both palettes. PNG dimensions are recorded
independently from SVG dimensions because upstream facet heading composition
differs between native formats.

Native paint validation distinguishes 92 exact palette variants from 22
variants using declared derived colors. Continuous interpolation, density
opacity, annotation bands and native funnel text exceptions are disclosed;
they are not silently reported as exact canonical paints.

The independent verifier passed 114 charts at desktop and mobile sizes,
offline rendering, real canvas paint, stable IDs, native output structure,
palette scopes, API anchors, source ZIP identity/regeneration, download links,
filtering/search, single active iframe, and client interactions. Focused
interaction probes exercise CSV export, synchronized facet navigation,
x-only zoom and exact history restoration after animation, selection modes
with formatted hover, and disabled controls.
Its complete pre-correction pass records 228 real chart renders, 57 equal
CS1/CS2 native geometry/text pairs, 580 links, 105 API entries, 13 matching
source ZIP files, standalone regeneration of all 114 charts, 12 filter/search
states, two Explore states and 15 targeted feature states. There were zero
console errors, page errors or external browser requests. The subsequent
cap-size/legend correction requires its own rebuilt-output visual check;
the earlier successful report remains retained.

The corrected release check also passes: eight affected desktop/mobile
renders and all 114 SVGs, 114 PNGs, 57 geometry/text pairs, 580 links, 105 API
records and 13 rebuilt ZIP source files. Manual review confirms compact caps
and clear legends in both palettes. Independent native geometry recovers .18
data-unit cap half-extents, or .36 full spans, within native .01-pixel
rounding. Retained evidence is under
`projects/reflex-xy/artifacts/capability-atlas-review-corrected/`.

The final shared footer correction passes 40 actual HTML views: ten affected
mechanisms in both palettes at desktop/mobile. Legends sit at least 45 pixels
below the plot and four pixels below axis titles, entirely within the
480-pixel canvas. Twenty native SVG paint checks and native PNG/HTML manual
review pass. All remaining core mechanisms received a full mobile visual
review. Evidence is under
`projects/reflex-xy/artifacts/api-probes/core-legend-footer-final/`.

The final frozen Pages-tree audit passes all complete native/API/link/ZIP
gates again, with 48 affected desktop/mobile chart renders and 47 targeted
feature states, including 40 footer-layout and four Sankey-contrast states.
All five native Sankey labels are canonical white in each palette; actual
HTML and manual screenshots confirm dark backgrounds and legible names.
There are zero console/page errors or external browser requests. Evidence:
`projects/reflex-xy/artifacts/capability-atlas-review-frozen/atlas-verification.json`.

Host fixtures actually exercise widget/show construction, view state,
selection rows/coordinates, append/reset/clear, memory, batch export, pyplot,
ColumnStore/Column operations, plugin registration/cleanup and export config.
Both colorsets pass optional Reflex 0.10.0 compiler dry runs. Optional pandas
3.1.0 and PyArrow 26.0.0 cases pass, including null-free zero-copy ingestion,
nullable copies preserving NaN, and chunk coalescing. GitHub Pages serves
static examples; notebook callbacks and Reflex events require their Python
hosts. Actual browser-to-Python callback delivery and broad performance are
not established by these checks.

Reproduction commands from the repository root:

```powershell
uv run --script skills/reflex-xy/scripts/test_xy_svg_compat.py
uv run --script skills/reflex-xy/assets/examples/reflex-xy-capabilities/build.py --output-dir projects/reflex-xy/artifacts/capability-rebuild
uv run --with "xy[reflex]==0.0.8" --with "reflex==0.10.0" --script skills/reflex-xy/assets/examples/reflex-xy-capabilities/host_examples.py --output-dir projects/reflex-xy/artifacts/host-reflex --colorset colorset1 --with-reflex
uv run --with pandas --with pyarrow --script skills/reflex-xy/assets/examples/reflex-xy-capabilities/data_tools.py --output-dir projects/reflex-xy/artifacts/data-tools --with-dataframes
uv run --script scripts/build-pages.py
projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe projects/reflex-xy/scripts/verify_capability_atlas.py --pages-root dist/pages --route examples/reflex-xy-capabilities --output-dir projects/reflex-xy/artifacts/capability-atlas-review-final
```

The evaluator Python environment needs XY 0.0.8, Playwright, Pillow and an
installed Chromium browser. Its native Windows environment is an evaluator
resource, not a runtime dependency of the skill bundle. Detailed local
reports and screenshots remain under `projects/reflex-xy/artifacts/`.

## Frozen isolated skill-use cohort

The predeclared eight-attempt runtime-only cohort used
`openai-codex/gpt-5.6-sol`, retaining the existing model exception after the
mandated Spark model was rejected before tool execution. Strict JSON mode,
exact output paths, integrity checks and focused read-surface gates were not
waived. All attempts consumed the same frozen 18-file runtime. The two new
prompts test the narrow SVG repair contract and an independently authored
two-palette uncertainty view; original naturalistic and boundary prompts
remain unchanged.

| Case | Run ID suffix after `20261024-reflex-xy-atlas-` | Strict/joint | Independent artifact and manual review | Retained failure |
| --- | --- | --- | --- | --- |
| Contract | `contract-sol-1` | Pass | Pass | None |
| Naturalistic | `naturalistic-sol-1` | Fail | Pass | Extra ambiguous `locator("canvas")` matched three native layers. |
| Naturalistic | `naturalistic-sol-2` | Pass | Pass | None |
| Naturalistic | `naturalistic-sol-3` | Fail | Pass | Extra whole-canvas hover scan for raw identifiers timed out. |
| Generalization | `generalization-sol-1` | Pass | Pass | None |
| Generalization | `generalization-sol-2` | Fail | Pass | Extra literal identifier assertion incorrectly expected serialized IDs as raw HTML text. |
| Generalization | `generalization-sol-3` | Pass | Pass | None |
| Boundary | `boundary-sol-1` | Fail | Pass | Two incorrect callback inspections caused tool errors; two absolute read-tool accesses to installed XY source violated the declared isolation policy. |

Joint results are contract 1/1, naturalistic 1/3, generalization 2/3 and
boundary 0/1: 4/8 overall. All eight independent artifact/manual checks pass.
Five tool errors and two isolation-policy violations remain failures. There
were no rerolls, evaluator repairs, source changes, waivers or pooled earlier
passes. The naturalistic minimum of 2/3 and boundary minimum of 1/1 are unmet,
so the skill remains `validating`.

Independent grading reruns the untouched generated source and checks actual
data, palettes, native XML, canvas output and source paths. Naturalistic
charts preserve all 12 requested observations; uncertainty charts preserve
all 18 center/lower/upper values in each palette. Review found readable
legends and honest static-host limits. A separate trace reviewer reconciled
raw JSON events, shell commands, read surfaces and all 18 file hashes in each
copied bundle. No repository docs, acceptance fixture or sibling skill was
consumed. The boundary's installed-source reads remain policy failures even
though they are not repository leakage.

Harness prompts, exact expected paths, thresholds and the original frozen
digest are retained in the [eight-attempt plan](capabilities-20261024-plan.json).
Actual commands are retained in `projects/reflex-xy/artifacts/atlas-pi/plan.json`
and per-attempt manifests
under `evaluations/runs/20261024-reflex-xy-atlas-*/`. The project runner
`projects/reflex-xy/scripts/run_atlas_pi.py` refuses to overwrite those runs.
The independent grader is `projects/reflex-xy/scripts/verify_atlas_pi.py`.
Compact result and independent trace review are retained as
`projects/reflex-xy/artifacts/atlas-pi/summary.json` and `trace-audit.json`.
Earlier [original](validation-20261024.md) and
[colorset](colorsets-20261024.md) subjects retain their own results.

The later [Sankey contrast contract](sankey-contrast-2026-10-24.md), run
`20261024-reflex-xy-sankey-contrast-contract-sol-1`, retains a failed joint
result on its `fc516b82...` copied subject. Artifacts, source replay, exact
data, native geometry/contrast and manual HTML/SVG review pass; five model
tool errors fail strict mode. The model tried a nonexistent annotation API,
made a Python argument-order syntax error, used an unsupported subtitle,
imported undeclared Pillow, and made an incorrect path-index assertion.
Canonical source also evolved to the footer subject during that attempt;
that separate freeze mismatch remains recorded. The isolated copied payload
itself stayed byte-identical. No failed attempt was rerun or repaired.
All five node labels remain over dark native fills, with minimum measured
contrast 11.93:1 in Colorset 1 and 9.32:1 in Colorset 2. This result does not
alter the initial cohort or the broader `validating` status.

The final [footer legend contract](footer-legend-2026-10-24.md), run
`20261024-reflex-xy-footer-legend-contract-sol-1`, passes 1/1 strict,
independent data/layout/trace and manual review on the final `7c045720...`
18-file runtime. All 27 tool calls complete without tool or policy errors;
both copied and canonical payloads remain unchanged. The agent adapts the
recipe to 960 by 600 pixels, two/three legend columns, bottom padding 150 and
anchor `(0,-.24)`. All 12 line vertices and 12 grouped bars per palette are
preserved; paired native geometry matches. The minimum native legend gap is
90.70 pixels below the plot and 53.86 below the axis title. Four native and
four HTML screenshots pass manual review, with zero offline browser errors
or external requests and unchanged original task hashes. Commands:
`uv run --script projects/reflex-xy/scripts/run_footer_legend_pi.py` and
`uv run --script projects/reflex-xy/scripts/verify_footer_legend_pi.py`.
This scoped pass does not replace earlier failures or promote the broader skill.

## Repository and publication checks

Pattern IDs validate at 1,348 canonical IDs. The main Pages catalog contains
16 discoverable example sets. Repository skill validation, independence,
payload, colorset contract, authored/generated Pages boundary tests and
unified Pages format validation pass. The scoped source/runtime/full bundle
audit passes for the frozen subject. Local installation sync/check is part
of the release procedure and passes for all 31 final canonical files. The
scoped sync uses the repository helper's source-file, copy and validation
functions for `reflex-xy`, preserving unrelated local installations.

Publication target:
[XY capability atlas](https://gvillarroel.github.io/skills/examples/reflex-xy-capabilities/),
[API index](https://gvillarroel.github.io/skills/examples/reflex-xy-capabilities/api.html),
[host recipes](https://gvillarroel.github.io/skills/examples/reflex-xy-capabilities/hosts.html).
Publication workflow and independent live-site verification are recorded
after deployment in the task's release evidence.
