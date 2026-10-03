# Composition and video arrow validation — 2026-10-03

The six behavior-changed bundles are frozen. Their exact full and runtime file
hashes are in [source-freeze-20261003.json](source-freeze-20261003.json).
All six current strict isolated release trials pass. Their exact required output
hashes, current payloads, browser states and decoded media were independently
inspected and are sealed in [validation-20261003.json](validation-20261003.json).
No commit, push or publication is performed by this workstream.

## Scope and actual repairs

| Bundle | Arrow-bearing surface | Reusable change |
| --- | --- | --- |
| compose-synchronized-svg | Relationship markers, reversible flow ribbons, world trunks and directional chevrons | Opaque readable paints; exact allowed same-hue contrast selection; marker dimensions/refX aligned with painted tips; rectangle visibility routing around nodes, labels and plaques; preserved endpoint bearings; independent collinear routes; focus no longer fades arrow paint. |
| diagram-composition | Native cycle and boundary panels | Neutral shaft/head paint changes from insufficient #9c9c9c to #696969; 1.8-unit shaft supports final display size; browser audit now checks actual projected heads. Hub spokes remain intentionally undirected. |
| usefulcharts-style | Influence/succession connectors and legend glyphs | Contrast-safe allowed role paint against paper; explicit materialized head/shaft tags; painted tip stops outside the target; ordinary descent connections remain undirected. |
| hyperframes-explainer | Flow/storage markers and calibrated inlet/vehicle mechanism glyphs | Correct painted marker refX; generated self-contained audit helper; ordinary velocity, position and flow-direction paths are explicitly recognized by its native audit. |
| video | Shared painter, generic/evaluation scene arrows and published eleven-concept renderer | Opaque solid arrow paint, actual source/target clipping, clear obstacle gutters, preserved final bearing, allowed same-hue contrast choice, routing-failure disclosure, native SVG or D3 caller support. The ESM render-state fallback declares Playwright; contact sheets guard actual frame periods and floor seek timestamps. |
| manim-svg-video | Imported native/CSS/context markers and delivered MP4 | Default auto rasterizes marker-bearing SVGs through Chromium to retain heads. CSS marker shorthand/custom properties are detected. Explicit vector mode refuses unmaterialized markers. Final animated inputs require a readable static companion; explicit source-time snapshots fail when arrows are hidden. |
| hierarchy-lens | Navigation glyphs only; no diagram connector arrows | Inventory and read-only control review only. No source change or gratuitous new connector is introduced. |

The solid borderless category surfaces, exact palette tokens, black/white on-fill
text, stable source/target identities and direction remain in place. Composition
world trunks use clear gutters instead of decorative halos. The two published
Compose SVGs were regenerated without changing their IDs. The three published
UsefulCharts posters were regenerated and remained byte-identical because their
descent connections have no directional head. Published Video painters use the
same reusable helper as normal runtime tasks.

For authored Video arrows, a nonzero visible-intent opacity no longer permanently
fades the shaft/head: old arguments mixed fixed hierarchy multipliers with reveal
progress. Readable arrows use full paint; whole-parent scene reveal remains.
Exact individual-arrow fade choreography is not a preservation claim. Original
imported source media are not silently restyled.

## Browser and deterministic evidence

All large evidence is local under
`projects/arrow-contrast-composition/artifacts/`, which is ignored by Git.
The project scripts are reproducible controls, not required skill resources.

| Command | Accepted evidence |
| --- | --- |
| `uv run --script projects/arrow-contrast-composition/scripts/test_arrow_projection.py` | Eight actual browser qualification cases: transformed user-space/stroke-width markers agree with decoded browser pixels; dark and alpha backings fail; covered heads fail; wrong refX fails; stroked open head passes; URL arrow paint is explicitly rejected. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_producer_arrows.py` | Twelve cases pass across both palettes: native cycle/boundary/hub geometry, influence/succession arrows including pale requested roles, vector-marker refusal, missing final companion refusal, hidden zero-time snapshot refusal and readable one-second snapshot. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_reverse_flows.py` | Six resting/focus/reduced-motion reverse-flow states pass in both palettes. Minimum measured contrast is 7.9046884551695875:1. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_video_arrow_template.py` | Two palette cases pass with native SVG caller, dark obstacle, clear gutter, tip outside Target and horizontal arrival bearing. Minimum is 4.508317451228126:1. |
| `uv run --script projects/arrow-contrast-composition/scripts/audit_outputs.py` | 141 actual states pass, including Compose resting/focus/navigation/reduced motion, published posters, primitive input states and 11 Video concepts at 11 times. 314 shafts and 384 heads were checked; no browser errors or findings. Minimum is 3.085302662118927:1. |
| `uv run --script projects/arrow-contrast-composition/scripts/audit_hyperframes_native.py` | Four native mechanism/palette projects pass at 88 states each: 352 states total. Current audit resources are copied into those generated projects before auditing. |
| `node projects/arrow-contrast-composition/artifacts/hyperframes/scripts/audit.ts --report projects/arrow-contrast-composition/artifacts/hyperframes/audit-current.json --screenshot projects/arrow-contrast-composition/artifacts/hyperframes/preview-current.png` | Primitive colorset1 audit passes 92 states. |
| `node projects/arrow-contrast-composition/artifacts/hyperframes-cs2/scripts/audit.ts --report projects/arrow-contrast-composition/artifacts/hyperframes-cs2/audit-current.json --screenshot projects/arrow-contrast-composition/artifacts/hyperframes-cs2/preview-current.png` | Primitive colorset2 audit passes 92 states. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_wheel_pointers.py` | Four readable settled probability-selector states pass; the lowest fill contrast is 6.829580022727658:1. This recognizes existing ordinary triangular pointer geometry without changing its source. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_hierarchy_controls.py` | 63 enabled navigation control states pass across four existing pages, resting/hover/focus; common neutral tokens belong to both palettes. Minimum is 5.489814557409947:1. Disabled controls are inactive affordances, not diagram directions. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_manim_backing.py` | All 17 cases pass: 16 tile/source background combinations verify actual PNG alpha, source CSS/shape paint order and retained findings; unsupported root CSS background images still block preservation. Seven combinations meet authored 3:1, nine retain source low-contrast findings. |
| `uv run --script projects/arrow-contrast-composition/scripts/test_contact_sheet_tail.py` | All seven cases pass: real 12fps/2s clips at 6/12/30 samples, 2fps/2s at 6/30 samples, 0.5fps/4s at 6 samples, and unreadable input refusal. All 90 frame tiles exist; actual microsecond seeks never exceed the native last frame PTS. |
| `uv run --script skills/compose-synchronized-svg/scripts/test_synchronized_svg_tools.py` | All 80 tests pass, including routing, focus, readable contrast and scenario semantics. |
| `uv run --script skills/diagram-composition/scripts/test_native_panels.py` | All 13 tests pass. |
| `uv run --script skills/usefulcharts-style/scripts/test_chart.py` | All 27 tests pass. |
| `uv run --script skills/compose-synchronized-svg/scripts/test_network_ports.py` | Both tests pass. |

The source-over sampler measures actual filled region paint and instanced native
marker geometry rather than attribute declarations. It does not round a ratio
into a pass. Opaque coverage produces an error instead of being discarded as
proof of contrast. The projection suite includes independent browser pixels.

There is one narrow moving-signal classification in the final published batch:
`inference-pulse`, `focus-burst-focus`, three shaft sample points. Two belong to
`arrival-to-admission` at (793.125, 209.16666666666666) and (797.375,
209.16666666666666); one intersects `slo-to-control` at (796.6666666666666,
211.63232421875). The foreground shape is the exact connector-owned moving
`arrival-to-admission` signal, not a node, region or label backing. Its motion is
clamped away from all persistent heads. Head samples receive no exemption;
heads and meaningful terminals remain visible. This does not authorize ignoring
arbitrary filled overlays or coincident connector routes.

## Source fidelity and media delivery

The original Manim vector import reproduced a missing triangular head in a real
MP4. Browser preparation restores it. The repaired 720×360, 12-fps, 3-second
output was decoded and visually inspected: the shaft and head remain outside
the Target silhouette. Representative decoded opaque pixel contrasts against
the actual local white backing are 6.09972980752698:1 and
5.572313328732911:1. The SVG stays editable; the Manim image flattens its vector
parts at preparation resolution.

A real 1280×720, 2-fps, 40-second published Video capture was decoded and inspected.
Its representative shaft/head ratios are 8.024387423312161:1 and
7.977883806802925:1. This is an inspected delivery sample, not a proof of every
possible encoder/resolution or every timeline instant.

The compositor's default authored gate initially rejected a faithfully imported
pale original at 1.5579550563651177:1. A repeatable exact-path
`--preserve-source-media <original-path>` option now preserves only explicitly
named original assets. It retains every finding in the raster sidecar, records
the manifest policy per asset, and sets `authoredQualityPassed: false` where
appropriate. Only original low-contrast/thin paint findings can be nonblocking;
hidden/covered/missing heads, unsupported geometry, unreadable snapshots,
conversion failure and vector-marker refusal still block. Fifteen qualification
cases pass with source bytes unchanged, actual original #cfcfcf pixels retained,
no exemption for unrelated paths and CSS-variable/shorthand-end marker heads
preserved. Two source-preservation cases reject a transparent marker
child and a zero-opacity shaft; the original transparent-head preparation pass
is retained as a reproduced boundary defect. The source exception is disclosed, never counted as an authored 3:1
pass. The final four backing cases audit transparent SVG areas against the
actual opaque Manim tile: authored #696969 arrows on #333e48 fail at
1.988817387226247:1, an explicitly preserved original retains that disclosure,
an opaque white source canvas overrides the dark tile, and transparent source
on a white tile passes. The PNG remains transparent, and the sidecar records
`deliveryBacking`. The previous white-fallback preparation pass and actual dark
tile screenshot are retained under `source-media/tile-backing-before`.
The additional 16-case matrix checks transparent source, opaque/alpha root CSS
backgrounds, opaque/alpha explicit rectangles and layered CSS/rectangle paint
order over both white and dark actual tiles. It compares the alpha-composited
prepared PNG pixels to the reported backing within 1.1 channel units, accounting
for eight-bit PNG alpha quantization; the contrast gate itself remains unrounded.
Solid/alpha root CSS backgrounds compose over the tile first and are recorded
as `sourceCssBacking`. An opaque source canvas takes precedence. Root CSS
background images are unsupported and stop conversion even under an explicit
source preservation policy. The old false rejection of a CSS-white original
on a dark tile is retained under `source-media/css-backing-before`.
Command: `uv run --script projects/arrow-contrast-composition/scripts/test_source_media.py`.

## Strict isolated trials and retained failures

The selected current trials are Compose2, Diagram2, UsefulCharts2, HyperFrames2,
Manim6 and Video8. Every selected trial passes model/event checks, zero tool
errors, exact required artifact paths, unchanged resource integrity and the
runtime read-surface policy. The independent inspection rechecks current source
and copied payload digests against the run manifest, and required output hashes
against the harness artifact check. All six cases pass. Video8's actual HTML
passes at 0, 0.5, 1, 1.5, 23/12 and 2 seconds, including the final readable seek;
both persistent shaft and head remain present with no signal overlays. Its real
two-second 720×360/12fps MP4 was decoded and visually inspected. Source and Target
are opaque borderless allowed fills; their computed exact white text is the
maximum-contrast binary choice, at 7.9046884551695875:1 and 5.4399561950875235:1.
Manim6 retains a 25-pixel-high decoded triangular terminal outside the Target
silhouette, with only the requested allowed source colors and a passing native
preparation report. The machine record contains each exact run ID and artifact
hash. No failed or repaired earlier trial is selected as strict acceptance.

| Bundle | Exact selected run ID | Independently measured minimum |
| --- | --- | --- |
| Compose | `arrow-composition-compose-synchronized-svg-20261003-2` | 7.645920672817288:1 |
| Diagram | `arrow-composition-diagram-composition-20261003-2` | 5.124406531604723:1 |
| UsefulCharts | `arrow-composition-usefulcharts-style-20261003-2` | 3.6457378015961366:1 |
| HyperFrames | `arrow-composition-hyperframes-explainer-20261003-2` | 7.378543797130064:1 |
| Manim | `arrow-composition-manim-svg-video-20261003-6` | 5.489814557409947:1 |
| Video | `arrow-composition-video-20261003-8` | 9.319198228461115:1 |

The exact strict harness and event-summary commands, including every required
output expectation, are retained per case in
[isolated-retry-20261003.json](isolated-retry-20261003.json). The final independent
inspection command is:

```text
uv run --script projects/arrow-contrast-composition/scripts/inspect_isolated_outputs.py
```

[isolated-20261003.json](isolated-20261003.json) retains the first cohort.
[isolated-second-attempt-20261003.json](isolated-second-attempt-20261003.json)
retains the second attempts.
[isolated-third-attempt-20261003.json](isolated-third-attempt-20261003.json)
and [isolated-fourth-attempt-20261003.json](isolated-fourth-attempt-20261003.json),
[isolated-fifth-attempt-20261003.json](isolated-fifth-attempt-20261003.json)
and [isolated-sixth-attempt-20261003.json](isolated-sixth-attempt-20261003.json)
retain subsequent attempts before final selection.
[isolated-retry-20261003.json](isolated-retry-20261003.json) names the selected
latest trials and exact expected paths. Each trial uses the runtime payload,
`--mode json --strict`, exact output expectations, model verification, zero
tool-error policy and an unchanged copied bundle. The recorded model exceptions
are gpt-5.6-luna, with gpt-6-luna for HyperFrames.

The first Compose/HF trials read forbidden run-manifest context; HF also used
incorrect prototype schema/search commands. Video's first trial used a broken
wrapper and an inappropriate clip-size floor. Manim's first trial assumed system
Python had Pillow. These failures remain retained. Native DOM painter support,
compact schema/command guidance and task dependency facts reduce that friction.
Video2 additionally exposed an actual missing Playwright dependency in the
render-state checker; the source now declares it and the same HTML passes.
Video3 used an invented frame filename, passed an uncreated contact sheet to a
validator and serialized a literal backslash-n suffix after JSON. Those are
retained agent output/tool failures, not accepted release results. Manim2 passed
strict but its snapshot preceded the final CSS marker detection repair and is
not used for release. Manim3 passed strict and arrow/media geometry checks, but
independent decoded/source review rejected authored #ff0000/#222222 outside the
palette. Its artifacts remain intact; the next task specifies allowed source
role paints. Video4 failed externally with a harness MemoryError in its 1 MiB
artifact hash read and Windows 0xC000012D commitment limit during trace summary;
it has no completed evaluation-result and is not accepted. Global Pi execution
is serialized after this shared resource failure, with no hash-routine bypass.
Video5 used plain system Python for an optional Playwright inspection and failed
with ModuleNotFoundError, then repaired that command. Manim4 used an exact RGB
match on a compressed decoded frame and failed on an empty pixel set, then
repaired the inspection. Both remain strict failures; the next prompts specify
the explicit uv dependency and bounded decoded-color tolerance. No rendering
source repair was needed for these agent inspection mistakes.
Video6 exposed a real contact-sheet tail defect: its valid six-sample command
rounded 1.9166666667s up to 1.917s, beyond the final 12fps frame. The helper now
probes the frame period, guards dense/low-fps sampling and floors microsecond
seeks; the same real Video6 MP4 command succeeds. Unreadable/nonconstant tails
still produce extraction errors. The failed strict trace remains. Video6 also
added an unrequested moving dot: paused seek2s places it beneath the head and
the actual sampler reports head contrast 1:1. Its earlier readable frames pass,
but its final state is independently rejected. The subsequent task keeps one
persistent arrow without optional dots. Manim5 probed the required repair-suffix
filename before creating it, although the compositor printed its existing exact
two-second unsuffixed output. Its copied/repaired artifacts remain, and the next
task explicitly copies the printed actual output to the required alias before
probing. Neither repaired trial becomes strict acceptance.
Video7 invoked dependency-bearing bundled scripts with plain Python for --help,
causing a missing-dependency tool error. The guidance already specifies uv; the
final task makes that invocation explicit for every bundled script, including
help. The source stays unchanged and Video8 passes on the same frozen payload.

Earlier deterministic routing failures and negative browser evidence are retained
under the local artifacts folder. Failed prototype media commands and test
fixture errors are not reclassified as passing results.

Run selected trials through the recorded commands, or use
`uv run --script projects/arrow-contrast-composition/scripts/run_retry_arrows.py`
with its explicitly selected skills/attempts. Independently inspect their current
payload hashes, required output hashes, actual browser geometry/paint and decoded
media with
`uv run --script projects/arrow-contrast-composition/scripts/inspect_isolated_outputs.py`.

## Limits and release boundary

The sampler qualifies solid fills, native fill alpha, ancestor opacity,
opacity filters, ordinary marker children/transforms, user-space/stroke-width
units and centered meet/none viewBox scaling. URL arrow/backing paint and
intermediate marker instances are reported as unsupported. Custom marker
alignment, clip/mask geometry, blur and complex filters require separate actual
pixel review. Narrow connector intersections are geometrical direction checks,
not filled backing regions. Authored arrows must still remain unambiguous.

The accepted evidence covers the listed producers, fixtures, sampled readable
states and delivery sizes. Whole fades to/from hidden are transitions. It does
not claim universal coverage of arbitrary imported SVGs, every frame, unknown
future assets or all resolutions. Source fidelity exceptions remain separate.
Shared policy, backlog state, full repository gates, local installation, Pages
build, commit, push and exact-SHA publication verification are owned by the root
integration workstream and must finish separately.
