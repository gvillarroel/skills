# Slidev Anime.js compact diagram validation — 2026-10-04

## Scope and frozen resources

The connected explanatory-diagram default now prefers the smallest layout
that preserves readable labels, fully painted heads, attributable ports,
distinct routes and actual motion envelopes. Quantitative chart dimensions
and the broader Anime.js capability recipes remain unchanged.

The general prose default failed the first naturalistic consumer task:
the authored 1180px stage rendered 1468px wide in a 1280px viewport,
hid the Inventory concept and its endpoint routes outside the slide,
shared lower endpoint legs and moved the parcel horizontally rather than
through the requested return/check mechanism. That outcome justified a
small self-contained implementation route instead of more prose.

The final runtime resources are:

- `assets/templates/ConnectedFlow.vue`: content-measured 18px concepts,
  16px route labels, native SVG dimensions, separate reciprocal branch
  ports and backward lane, complete stationary base routes, 10px user-space
  heads and 8px parcel following each rendered path.
- `scripts/scaffold_connected_flow.py`: exact requested deck/component
  output paths from a narrow JSON topology (two to six ordered main
  concepts, optional one reciprocal check branch and one backward return).
- `scripts/capture_deck.py`: correctly awaited native clicks, replay and
  reduced-motion captures, an owned random localhost SPA server, readiness,
  explicit workspace output paths and browser/server cleanup.
- `references/connected-flows.md`: API, limits, construction minima and
  runtime validation commands, linked from the main skill.
- `scripts/test_connected_flow.py`: browser checks of semantic geometry,
  labels, heads, motion, clicks, replay, reduced motion and the existing
  timeline-machine SVG pack.

The existing SVG pack also needed a demonstrated motion-envelope repair:
passing `transformOrigin: 'center'` to the animation left the SVG CSS pivot
at `0px 0px` with `transform-box: view-box`. Right signal lamps were clipped
at scale approximately 1.2. CSS `transform-box: fill-box` and
`transform-origin: center` now apply only to the tested `.machine-gear`
and `.machine-signal` hooks. The imported SVG geometry is unchanged.

Manual capture found another output issue despite correct text DOM bounds:
direct sibling SVG route labels disappeared or painted at stale positions
after click changes. Giving each static route label its own translated SVG
group preserved all labels during moving and settled screenshots. Reusing
the same component on hidden slides also receives instance-specific marker
IDs through Vue `useId()`.

## Deterministic and visible evidence

Command:

```text
uv run --script skills/slidev-animejs/scripts/test_connected_flow.py --workdir projects/diagram-compactness/artifacts/reviews/anime-painted-tests
```

Passed. The final complete Order/Pick/Pack/Dispatch plus Inventory check map is
457×240 native SVG units. Every concept uses 18px type with visible insets;
route labels remain 16px. All six source/target paths and head triangle
vertices stay outside opaque nodes. Sampled route strokes avoid route
labels. The parcel was observed on all six actual paths, within two screen
pixels of its path, with zero node overlap and more than 15 screen pixels
from each tip. Native clicks select states one/two; Replay restarts the
current motion; reduced motion retains all six base connections. Machine
gear/signal painted boxes stay inside the stage over 60 motion samples.
Both full stationary source-geometry cables remain nondashed and visible
through all machine clicks and remount/replay; cleanup retains exactly two
base copies. The parcel's actual computed fill is primary `rgb(158, 27, 50)`.
The browser reported no page errors.

Evidence: `projects/diagram-compactness/artifacts/reviews/anime-painted-tests/`
contains build/install logs, `browser.json` and manually inspected click and
reduced-motion screenshots. Earlier test failures are retained in prior
review folders: the first evaluator attempted `/2` on a plain static server;
the second retained button focus before a keyboard navigation that Slidev
correctly suppressed. The test now blurs the control and uses native
navigation; the reusable capture server also implements SPA fallback.
Another test caught a replay base copy inheriting its source's current
draw-on dash style. Removing the copied style and explicitly restoring a
full nondashed base repaired the reusable component before release.

Capture helper checks:

```text
uv run --script skills/slidev-animejs/scripts/capture_deck.py --deck projects/diagram-compactness/artifacts/reviews/anime-connected-tests/deck --output-dir projects/diagram-compactness/artifacts/reviews/anime-capture-flow
uv run --script skills/slidev-animejs/scripts/capture_deck.py --deck evaluations/runs/compact-slidev-animejs-20261004-sol-release-contract/workspace/deck --output-dir projects/diagram-compactness/artifacts/reviews/anime-capture-pack
```

Both passed with three captured states and zero page errors. Pack navigation
actually reached `/1`, `/1?clicks=1` and `/1?clicks=2`; replay reloaded the
current SPA route and remounted visible output. Chromium wake-lock permission
is granted only to the owned localhost origin, using the documented
[`screen-wake-lock` browser-context permission](https://playwright.dev/docs/api/class-browsercontext).
The helper records evidence for review and does not certify layout optimality
or visual quality by itself.

## Retained development attempts

| Run ID | Outcome and classification |
| --- | --- |
| `compact-slidev-animejs-20261004-release-contract` | Exact artifacts and independent build were present, but strict rejected two agent tool errors: npm run outside the deck and an unawaited locator helper closing its browser. Independent review also found the existing SVG pivot clipping. |
| `compact-slidev-animejs-20261004-release-natural-1` | Interrupted after independent visual/semantic failure was established; generic hand authoring produced off-screen concepts, shared legs and inaccurate parcel motion. Retained source, build and screenshots. Natural repetitions two/three were not launched against this known failing behavior. |
| `compact-slidev-animejs-20261004-sol-release-contract` | Interrupted before final review while the candidate was being repaired; source and successful build are retained as development evidence, with no release-pass claim. |
| `compact-slidev-animejs-20261004-sol-final-contract` | Strict failed because a bare Python capture invocation lacked the script-declared Playwright dependency, then an attempted plain pip invocation failed inside the UV environment. The agent recovered, but failures remained. Guidance now gives the explicit UV capture command. This earlier bundle also lacked complete held-state machine base cables. |
| `compact-slidev-animejs-20261004-sol-final-natural-1` and `-2` | Strict and independent visible checks passed, but retained as development because resources were still being repaired before freezing the release cohort. |
| `compact-slidev-animejs-20261004-sol-final-natural-3` | Strict failed on the inherited base-dash test defect, an unavailable optional Pillow montage dependency and an outside-workspace `/tmp` read. The base-dash issue was repaired; the other errors are agent/tool-use failures. No pass claim. |

The first two runs used the backlog-recorded Luna exception after Spark was
unsupported. The final consumer cohort uses the separately recorded
`openai-codex/gpt-5.6-sol` exception, retaining strict model, payload,
read-surface, zero-tool-error and exact-output requirements.

## Release cohort

Frozen candidate command:

```text
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-release2 all slidev-animejs openai-codex/gpt-5.6-sol
```

This serial cohort contains one SVG-pack regression contract and three
fresh naturalistic connected-diagram repetitions. Required exact outputs
are checked with `--expect-output` for every requested deck/component,
package and review path. All traces and failed attempts remain under
`evaluations/runs/`. Completion requires the strict contract and at least
two independently reviewed naturalistic passes; strict exit success alone
is insufficient.

The frozen geometry cohort used runtime payload SHA-256
`31549d0117b2947f118c90de2427198e8d74ad4b1eb691701b0f81c29c3b0f0d`
(42 files), with the following retained outcomes:

| Run ID | Strict result | Independent artifact result |
| --- | --- | --- |
| `compact-slidev-animejs-20261004-sol-release2-contract` | Pass | Rebuilt runtime SVG pack; actual click states, replay/remount and reduced-motion captures passed with no page errors. Source SVG geometry is an exact runtime copy. |
| `compact-slidev-animejs-20261004-sol-release2-natural-1` | Pass | Independently restored the agent-pruned npm dependencies from `package.json`, rebuilt and inspected native 457×240 geometry and visible states; labels, six full directions and motion passed. Dependency pruning was an environment setup step, not a skill or output failure. |
| `compact-slidev-animejs-20261004-sol-release2-natural-2` | Fail | Agent attempted `/dev/stdin` on Windows rather than the documented real JSON file and later issued failing cleanup/assertion commands. Exact artifacts and immutable payload passed. Independent rebuild/captures found readable 457×240 geometry and no page errors, but tool errors exclude this repetition from the strict pass count. |
| `compact-slidev-animejs-20261004-sol-release2-natural-3` | Pass | Independent rebuild and manually inspected native click/motion/reduced screenshots passed at 457×240 with all labels, directions, separate ports and return leg visible; no page errors. |

Thus the frozen geometry cohort passed its contract and two of three
natural repetitions. The three natural results belong to that exact
payload hash; they are not relabeled as trials of a later bundle.

After completion, a narrow paint-role repair changed only the two default
parcel accent literals from the error color `#e8002a` to primary `#9e1b32`.
Neutral common-category stages remain deliberate. One corresponding
computed-color assertion was added to the deterministic test. The measured
layout, route, label, head, port, timing and replay template is byte-identical
before and after this paint repair, with template SHA-256
`a9579bf0bde9540bbab5d673ff777c843040b0afe2be43c008d4b5a60d42c7d7`.

The final painted runtime payload is
`7ffa86e88c07c8d6e9bea387aecb9867103ea9407edd9e7adf6cdafaf7ee1b90`
(42 files). The evaluator-owned source comparison command is:

```text
uv run --script projects/diagram-compactness/scripts/verify_anime_paint_only.py
```

It passed, proving the two paint defaults plus their paint assertion are
the complete runtime diff. Semantic geometry reports match. An earlier
local test measured 454×241 while final captures measure 457×240; the
content-measured boxes track downloaded-font versus fallback font metrics.
No cross-run pixel-identity claim is made from those differing font states.
All final painted text/head/motion tests pass at the measured current size.

Additional final deterministic command contracts use the same final hash:

| Run ID | Strict and independent result |
| --- | --- |
| `compact-slidev-animejs-20261004-painted-contract` | Strict pass with the exact scaffold command and seven exact artifacts. Independently rebuilt and reviewed primary parcel paint, 457×240 native geometry, all six source/target path strings, complete 10-unit heads, moving/settled clicks, Replay and reduced motion; no page errors. |
| `compact-slidev-animejs-20261004-boundary-contract` | Strict pass with the exact command and seven artifacts. Independently rebuilt and reviewed all seven 18px concepts at 749×240, all eight attributed routes/full heads and entire longer motion sequences; 63 observed mover samples cover every route, with zero node/route-label overlaps, all movers inside the frame, primary parcel paint, Replay and complete reduced-motion output. No page errors. |

Commands use `scripts/run-pi-skill-eval.py slidev-animejs --mode json --strict
--require-exact-command-from-prompt --model openai-codex/gpt-5.6-sol`, the
matching `diagram-compactness-slidev-animejs-{painted,boundary}-contract.md`
prompt, the table's exact run ID and `--expect-output` for each of:
`flow.json`, `deck/slides.md`, `deck/components/OrderHandoff.vue` (or
`AccessRouting.vue` for the boundary), `deck/package.json`,
`captures/capture.json`, `captures/state-0.png` and
`deliverables/layout-review.md`. Independent rebuild/capture commands are
`inspect_slidev_animejs.py <run-id>` and, for the longer boundary sequences,
`inspect_anime_boundary.py --deck <run-workspace>/deck --output-dir <review>`.
The local deterministic boundary check passed before the strict run. Its
first evaluator snapshot raced initial Slidev visibility and produced
zero-sized bounds; the evaluator now waits for the SVG's visible state and
settled initial layout. No skill source changed for this evaluator repair.
The passing final generated handoff and boundary components also match
the frozen template exactly after their configuration substitutions.

Each passing trace was summarized with
`scripts/summarize-pi-json-events.py <run>/events.jsonl --require-model
gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error`. The healthy read
surface is the skill entry point, focused integration/connected-flow,
palette and SVG-pack references, small runtime templates, and task-owned
sources/captures; it contains no acceptance galleries or sibling skill.
Strict integrity/model/exact-path checks remain unchanged. Bulky native
screenshots, traces, build logs and comparison JSON stay in ignored run
and project artifact folders.

## Published fixture regression

The maintenance deck wrapper imports the repaired runtime SVG pack. Its
existing timeline-machine slide previously navigated directly from slide
20 to 21 because it lacked click metadata. Adding only `clicks: 2` to that
slide's frontmatter makes the two intended native states accessible.
This fixture-only change is excluded from runtime payloads.

`npm run export:html` in `assets/examples/slidev-animejs/` passed with
Slidev 52.16.0 (620 modules). Evaluator-owned
`projects/diagram-compactness/scripts/inspect_anime_fixture.py` passed
105 timed native samples over states zero/one/two, verifying all painted
gear/signal boxes stay inside the stage, the two full cable copies persist,
current-route replay/remount retains two copies and no page errors occur.
Evidence is under `projects/diagram-compactness/artifacts/reviews/anime-fixture/`.
The stable DOM pattern ID remains `slidev-animejs-timeline-machine`, with
the existing route
`https://gvillarroel.github.io/skills/examples/slidev-animejs/#/20`.
The catalog and IDs are unchanged. Pages publication is handled with the
repository's normal build, validators, source commit/push and CI check.

## Limits

The connected helper supports its stated ordered-row topology rather than
arbitrary networks. It rejects native diagrams wider than 850 SVG units
instead of shrinking labels; longer mechanisms need a related subdiagram.
It uses explicit clear route reservations, not a proof of a global packing
optimum. Fixed presentation constraints and semantic content must still be
respected when adapting the generated component. Other chart and animation
families retain their existing workflows.
