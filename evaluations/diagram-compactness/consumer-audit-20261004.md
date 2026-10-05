# Independent consumer artifact review, 2026-10-04

This review covers ECharts, Slidev, and video validation artifacts for the diagram compactness change. Independent artifact reviews treat skill sources as read-only. The later authorized ECharts helper repairs and source freezes are explicitly recorded below. A clean event trace alone is not a passing forward test: every exact required artifact must exist, and visual output must remain readable. Earlier `final-*` runs are development evidence, not the accepted release cohort. Root is rerunning Windows process crashes serially.

## Current v3 evidence

| Run | Observed evidence | Independent conclusion |
| --- | --- | --- |
| `compact-echarts-animated-svg-20261004-v3-contract` | No strict event findings. Static/animated bar SVGs, pair validation, and Chromium preview exist. `artifact-check.json` fails because `deliverables/layout-review.md` is missing. | Incomplete exact-output contract. The available bar preview is readable: title, three labels, axes, values, and marks are visible. No diagram compression was applied to this supplied quantitative geometry. |
| `compact-slidev-echarts-20261004-v3-contract` | A speculative absent-package probe exits nonzero. Later `npm`, plain `node --version`, explicit Node invocation, and shell commands crash with Windows exit codes `3221225773`/`3221225794` or `spawn UNKNOWN`. | Infrastructure failures after the first failed probe; they do not demonstrate a layout defect. Avoid adding compensating skill prose for general process crashes. Requires a clean serial rerun. |
| `compact-video-20261004-v3-contract` | No strict event findings, but all three required files are missing according to `artifact-check.json`. Only source SVG creation began. | Incomplete; no composited scene is available to inspect. Requires a completed rerun. |

Other v3 Slidev jobs had no completed event check at the initial review. Do not infer pass or failure from pending files.

## Concrete development-stage visual defect

`compact-echarts-animated-svg-20261004-final-natural-1` is not an accepted run. Its final static SVG was independently rendered with the bundled Chromium preview helper into `workspace/deliverables/independent-preview.png`.

The preview fails readability and compactness:

- The left Receive box and right Archive box are clipped by the canvas. Their centers are 55 and 1145 on a 1200-pixel canvas, while their rendered half-width is 83.
- Native graph fitting moves the main row from authored y=310 to rendered y=125 and stretches the vertical symbol envelope. Nodes cover the subtitle; the lower Quarantine box covers the legend.
- All six edge captions are placed at the same translated origin, outside the visible canvas. The pair animation validator preserves this geometry and therefore cannot certify its readability.
- The long empty vertical failed-sample route and unused lower canvas area remain despite the review note claiming an accepted compact layout.

The run's `layout-review.md` claims labels, endpoints, title, and legend are visible, contrary to the independently rendered image. Treat visual inspection as a required gate, rather than trusting self-reported findings or a static/animated preservation check.

Minimal reusable repair targets are source-native bounds that include complete symbol envelopes, protection of title/legend regions from actual native view fitting, and an explicit check that edge captions remain individually positioned after native arrow clearance. Reducing source-coordinate gaps alone is insufficient because `layout: 'none'` still fits a native view coordinate system.

The related `final-natural-1`, `final-natural-2`, and `final-natural-3` development traces all first fail SVG parsing at line 3, column 77. An SVG interpolation/serialization path is inserting invalid XML before recovery. The final natural-3 trace also fails a Python diagnostic print under cp1252 when it prints an arrow character. These are development failures retained as evidence; a final recovered artifact does not erase the original strict tool error.

## Review commands

```text
uv run --script projects/diagram-compactness/scripts/inspect_failures.py <run-id> ...
uv run --script skills/echarts-animated-svg/scripts/render_svg_preview.py evaluations/runs/compact-echarts-animated-svg-20261004-final-natural-1/workspace/deliverables/workflow.static.svg --output evaluations/runs/compact-echarts-animated-svg-20261004-final-natural-1/workspace/deliverables/independent-preview.png
```

The independent PNG and bulky artifacts remain under ignored `evaluations/runs/`. This report records only the reusable diagnosis and run IDs. It will be extended when the serial consumer cohorts complete.

## Reusable repair and focused native checks

The diagnosed native fitting/caption defects led to a self-contained helper in both `echarts-animated-svg` and `slidev-echarts`. Each bundle now owns its UV Python wrapper (`scripts/render_concept_graph.py`), native implementation (`assets/templates/render-concept-graph.mjs`), and caption adapter (`assets/templates/concept-graph-labels.mjs`). Slidev also owns its preview wrapper. No helper reads a sibling skill or acceptance fixture. Each compact reference and skill entry point routes simple conceptual workflows through the helper. Quantitative chart paths remain unchanged.

The input uses explicit node IDs/full labels and directed edges. It computes DAG ranks while treating declared return edges separately, or accepts ranks/complete coordinates. Native series view bounds exactly match data center bounds, including two-pixel degenerate spans. This keeps the view transform at 1:1 and leaves complete symbol envelopes inside the canvas. Captions are existing native Line text elements placed on the visible native shaft after arrow qualification. There are no replacement nodes/edges. XML-sensitive metadata is escaped and native font declarations avoid double-quoted family strings in ECharts SSR attributes.

The same laboratory fixture was tightened through focused prototype iterations from 1140×352 to **842×288**, a **39.6% reduction in area at the same 18px node text, 14px captions and 14px heads**. Captions and complete arrows remained visible. Distinct branch/return lanes, full labels, and at least 3.25px actual arrowhead clearance were preserved. The remaining short uncaptioned inter-node gaps protect visible shafts and complete heads; longer captioned corridors are measured locally. This is a safe scoped layout, not a claim of global optimal packing.

Each bundle's `scripts/test_concept_graph.py` passed seven Chromium cases and two rejection cases. The successful cases cover computed workflow/return/branch layout, repeated output stability, explicit 1200×700 dimensions with unchanged symbol sizes, wrapped long labels plus quotes/ampersands, a single-row graph, a single-column graph, and one isolated concept. Chromium measures complete text and symbol/head bounds, full label containment, readable font minima, head clearance and routes against unrelated node silhouettes. The rejection cases cover a route through an unrelated node and a canvas smaller than the required readable content; neither delivers an SVG.

Final test commands:

```text
uv run --script skills/echarts-animated-svg/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/native-tests-v4
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/slidev-native-tests-final
uv run --script scripts/validate-skills.py --skill skills/echarts-animated-svg --skill skills/slidev-echarts
git diff --check -- skills/echarts-animated-svg skills/slidev-echarts evaluations/diagram-compactness/consumer-audit-20261004.md
```

All commands passed. The target validator accepted the script/resource conventions and standalone links. The final workflow, long-label, and explicit-canvas screenshots were opened and independently reviewed. Earlier focused long-label caption failures are preserved under the same ignored run parent; they caused the native visible-shaft caption repair rather than being accepted as successful renders. Root runs the final isolated consumer cohorts separately after the helper freeze.

## Sol release consumer review

`compact-video-20261004-sol-release-contract` passes all four reported harness gates: exact artifacts, event policy, payload integrity and successful exit. Independent Chromium review loaded the generated compositor at its actual 640×360 dimensions and sampled 0.5, 1.0 and 3.8 seconds. Both Input/Result labels remain 18px and fully readable. Source boxes, named ports and the short horizontal route are clear; there are no page errors, clipping or label overlap. Evidence is retained as `workspace/deliverables/independent-{0.5,1.0,3.8}.png` and `independent-review.json` under that run.

The compositor represents direction with a moving circle along the shaft. It paints no arrowhead in the active or held state; at 3.8 seconds the persistent line has no static directional glyph. The review note states this behavior accurately, but the generated scene contract's `validationChecks` still claims that a directional head remains visible. That head check has not passed: no head was created. For held directional diagrams, a persistent target arrow would retain direction after motion stops. For a signal-only contract, report the moving-pulse behavior honestly instead of declaring a nonexistent head visible. Root received this concrete observation; no video source was edited during this independent review.

Root retained that video contract as **strict pass / visual fail** and is repairing the compositor's actual directional heads and feedback/branch route clearance before a fresh cohort. It is not an accepted visual release result.

`compact-echarts-animated-svg-20261004-sol-release-contract` passes every reported harness gate. The independently regenerated Chromium preview at the supplied 640×420 size shows the complete title, axes, values, category labels and three bars without clipping or overlap. The static/animated pair retains supplied quantitative geometry. Its retained independent PNG is `workspace/deliverables/independent-preview.png`.

`compact-echarts-animated-svg-20261004-sol-release-natural-1` creates every exact artifact and preserves the copied payload, but fails strict event policy because an intentionally tighter layout candidate was correctly rejected for a caption/Analyze overlap. The final restored 842×288 diagram independently passes visual inspection: all six labels, two captions, branch/return routes, shafts and complete heads are clear. Its rejected candidate error remains part of the trace; restored final artifacts do not turn that run into a strict pass.

That expected comparison rejection led to an explicit `--probe` mode in both native helpers. Fresh candidate SVG/option paths prevent stale output from being mistaken for an accepted candidate. Only recognized layout gates return an accepted-false comparison report with exit zero and no delivered candidate SVG/option. Invalid source input, malformed JSON, dependency failures and unexpected exceptions still fail. Normal final renders retain hard failure semantics. Runtime guidance now requires reading `accepted` before previewing a candidate and keeping the last passing layout after rejection.

Updated focused checks passed for each bundle: seven Chromium cases, two normal final-render rejection cases, four comparison probes (accepted, route crossing, undersized canvas, caption/node overlap), and two cases proving that invalid input and unexpected JSON parser errors remain unmasked. The final evidence and commands are:

```text
uv run --script skills/echarts-animated-svg/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/native-tests-probe-final
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/slidev-native-tests-probe-final
uv run --script scripts/validate-skills.py --skill skills/echarts-animated-svg --skill skills/slidev-echarts
```

All passed after adding contents sections to the compact references when they exceeded 100 lines. Root is running fresh frozen helper cohorts; the older Sol natural cohort is retained development evidence.

`compact-video-20261004-sol-head-release-contract` independently passes visual inspection after the head repair. At the 3.8-second held state, the tagged native head is 12×12.8px and points right; its tip is x=348, four pixels clear of the Result body's x=352 left edge and six pixels from the port center. The active 1.75-second signal remains clear of both 18px labels. No page errors, clipping or overlap were observed. Independent screenshots and head geometry JSON remain in that run's deliverables.

That run still fails strict event policy: the first renderer check incorrectly requested two unique `activeBeat` values for a single-scene planning smoke, then recovered with the correct one-beat threshold. Exact outputs and payload integrity pass. Root received the diagnosis and is correcting the planning check guidance; this recovered run is retained evidence, not a strict release pass.

`compact-echarts-animated-svg-20261004-sol-probe-release-contract` preserves the supplied static bar template byte-for-byte (`fc /b` found no differences) and creates all exact required artifacts, but fails strict read policy by opening two preview PNGs from the native Windows OS Temp directory. These are task-generated image reads outside the isolated workspace, not a geometry failure. Root received the exact paths/classification. Preview creation and reads should use relative workspace paths, including on Windows; changing `/tmp` to the native OS Temp directory does not satisfy the isolated workspace contract.

`compact-echarts-animated-svg-20261004-sol-probe-release-natural-1` passes strict runtime, exact outputs and payload integrity, then independently passes Chromium visual review. The agent uses the new probe to adopt a tighter **801×288** layout from the helper's 842×288 baseline, a 4.87% width/area reduction with the same 18px node labels and 14px captions. Every node label, relationship caption and complete head remains visible. The distinct elevated retest lane and lower failed-sample branch retain clear endpoints and do not cross unrelated concepts. The retained independent preview reports nine text elements and zero page errors. This is the first healthy post-probe naturalistic consumer run; final repetition status is recorded by root after the whole cohort completes.

## Evidence-only harness recommendation

Root requested a read-only review of `scripts/run-pi-skill-eval.py` and `scripts/test-pi-eval-harness.py` before deciding on an opt-in owned scratch environment. The runner currently inherits the shared OS environment for Pi. Its existing `normalize_policy_path` already resolves an absolute in-workspace read to a workspace-relative policy path; resolved external files, sibling skills, and runtime acceptance examples retain their strict forbidden-read gates.

An explicit `--workspace-temp` option is therefore a principled isolation improvement: create a fresh `workspace/.runtime-temp`, copy the environment for the Pi child only, and override `TEMP`, `TMP` and `TMPDIR` with its absolute forward-slash path. Record the opt-in and those three scratch overrides in the run manifest without logging the complete environment. Python/Node/browser defaults then place normal task scratch inside the owned isolated workspace. This does not provide a filesystem sandbox and does not permit hardcoded external reads.

Keep every existing forbidden-read expression, normalized containment check, exact-output gate, model/error gate and payload-integrity gate unchanged. Test opt-out compatibility, unchanged parent environment, owned-temp reads, continued external/sibling/example rejection, exact missing/wrong outputs and payload mutation. Use the same opt-in across each new frozen cohort and record the changed environment; never reclassify prior external Temp failures as passes. The existing unit tests already demonstrate in-workspace absolute-read normalization and rejection of normalized sibling traversal. No harness source was modified during this subagent review.

## Additional source-fidelity boundary

A literal edge caption `Choose {a}` revealed an ECharts formatter-template collision in the new helper. With a roomy explicit 500-pixel source/target separation, the helper emitted success but native visible text became `Choose series\u00000`, containing an actual NUL character, and the SVG failed XML parsing at line 12, column 212. The source label in accessibility metadata remained literal, so metadata alone would not reveal the corruption. Automatic layout also mismeasured this transformed caption and rejected its overlap rather than preserving the source string.

The compact boundary evidence is retained under `evaluations/runs/20261004-compaction-renderers-manual/native/` (`input-literal.json`, `literal.svg`, option/review JSON). `inspect_literal_svg.py` serializes the text/control character safely and verifies XML failure. Root received the finding before any frozen source edit. An initial hypothesis of omitting the formatter was rejected: ECharts then displays the relationship ID instead of the supplied caption. The scoped repair stores the full literal caption in the native link's `value` and uses the fixed ECharts formatter `'{c}'`. User text is never interpreted as a formatter template.

Both self-contained helpers now pass eight Chromium cases, including `Choose {a}, {b}, {c} & "verify" <next>` with literal braces in node labels and XML-sensitive title/label text. The SVG parses as XML; Chromium finds the exact complete caption and node labels, keeps their readable sizes and bounds, and measures 3.25px arrowhead clearance. The prior seven cases, repeated render, explicit canvas, two hard layout rejections, four comparison probes and two unexpected-input failures continue to pass.

```text
uv run --script skills/echarts-animated-svg/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/native-tests-literal-final
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/slidev-native-tests-literal-final
uv run --script scripts/validate-skills.py --skill skills/echarts-animated-svg --skill skills/slidev-echarts
git diff --check -- skills/echarts-animated-svg skills/slidev-echarts evaluations/diagram-compactness/consumer-audit-20261004.md
```

All checks passed, and the literal-caption PNG was independently opened. The helper sources were frozen after this correction for new `sol-literal-final` strict cohorts. Every older source-changing cohort remains development evidence. The exact own-root process helper found no running `echarts-animated-svg` `sol-probe-release` driver to terminate. Root decided to retain the existing strict harness without an owned-temp environment option; the final cohorts use explicit workspace-owned preview destinations and preserve all existing read-surface gates.

## Frozen literal-caption release cohorts

The ECharts cohort completed with **contract pass and 3/3 naturalistic passes**, using `openai-codex/gpt-5.6-sol`, medium thinking, runtime-only payload, JSON mode, strict gates and every exact required output. Every case has the identical payload SHA-256 `b51f5e3e971863ccc196b8d13cf70f6b67ccddf593019d390c87293125eaa8e4`. The source stayed frozen throughout. UTC timestamps fall on October 5; the audit/run IDs retain the October 4 local start date.

| Run suffix after `compact-echarts-animated-svg-20261004-` | Strict outcome | Independent artifact outcome |
| --- | --- | --- |
| `sol-literal-final-contract` | Pass: exact outputs, no tool/event/read errors, observed Sol, unchanged payload. | Pass. Supplied 640×420 quantitative template remains byte-for-byte unchanged. Title, category/value labels, axes and bars stay readable through replay and viewport resize. |
| `sol-literal-final-natural-1` | Pass, including an expected accepted-false canvas probe. | Pass. 842×288 native workflow; all six concepts, six heads and both captions remain clear. |
| `sol-literal-final-natural-2` | Pass, including an expected accepted-false canvas probe. | Pass. Same readable 842×288 native geometry, with separated retest/failed-sample routes. |
| `sol-literal-final-natural-3` | Pass, including an expected accepted-false canvas probe. | Pass. Same complete content, visible endpoints and readable final animation. |

The independent review loads each actual delivered static/animated SVG in Chromium at its native dimensions, clicks a replay wrapper twice, checks a 1024×768 laptop viewport and reduced motion, and opens each final PNG. Each of the three conceptual runs retains 18px node labels, 14px captions, six complete 14px heads with at least 3.25px measured body clearance, and zero text intersections, clipping or page errors. The quantitative contract retains its supplied font sizes and geometry. The rejected smaller-canvas probes are truthful local comparisons; they do not prove a global packing optimum.

Runtime read surfaces contain only the owning entry point, selected compact/arrow/palette/animation references, small in-bundle palette/template resources, and the task's own JSON or PNG artifacts. There are no sibling skills, acceptance examples, project artifacts or external scratch reads. The supplied chart-animation recipe is approximately 10 KB and is directly required for the requested bar/graph animation; no gallery source was read.

```text
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-literal-final all echarts-animated-svg openai-codex/gpt-5.6-sol
uv run --script projects/diagram-compactness/scripts/review_native_svg.py compact-echarts-animated-svg-20261004-sol-literal-final-contract --file chart.static.svg --animated chart.animated.svg
uv run --script projects/diagram-compactness/scripts/review_native_svg.py compact-echarts-animated-svg-20261004-sol-literal-final-natural-1
uv run --script projects/diagram-compactness/scripts/review_native_svg.py compact-echarts-animated-svg-20261004-sol-literal-final-natural-2
uv run --script projects/diagram-compactness/scripts/review_native_svg.py compact-echarts-animated-svg-20261004-sol-literal-final-natural-3
uv run --script projects/diagram-compactness/scripts/collect_literal_final_evidence.py echarts-animated-svg
```

The collector reruns the required event summarizer for each completed run with `--require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error`; all pass. The bounded retained summary is [echarts-animated-svg-sol-literal-final-20261004.json](echarts-animated-svg-sol-literal-final-20261004.json). Full events/copies remain under ignored `evaluations/runs/<run-id>/`; independent browser geometry and PNGs remain under ignored `projects/diagram-compactness/artifacts/reviews/<run-id>/independent-native/`.

The same frozen SlidevECharts cohort retains two failed attempts before its repetition result is known:

- `compact-slidev-echarts-20261004-sol-literal-final-contract` creates every exact file and preserves its payload, but has three strict tool errors. A browser-discovery loop returns one despite finding Chrome; a speculative SSR option connects names while assigning different node IDs and omits disposal, causing a timeout; a later speculative native inset runs before Line geometry settles. These are sampled agent errors. The recovered final 640×360 SVG independently passes, with three exact 90×40 rectangles and two complete heads. A separate Chromium render of its actual delivered option also passes native 640×360 → 800×450 → 640×360 resize/re-inset checks; repeated insets are stable. A fresh contract retry will use the same frozen payload after the naturalistic batch, rather than relabeling this attempt.
- `compact-slidev-echarts-20261004-sol-literal-final-natural-1` creates every exact file and preserves its payload, but fails strict events. Its first plain-directory HTTP preview visits `/1` without SPA fallback and times out waiting for the graph; recovery visits `/#/1`. Three later unsolicited cleanup attempts fail because a server holds the output directory. The final source independently rebuilds successfully with `npm.cmd run build` from that run's `workspace/deck/`. Initial complete/static, normal and retest click states, navigation replay, 1024×768 resize and reduced motion independently pass: eight full labels, six visible heads, separate routes, zero text overlap/clipping and zero page errors. This recovered visual pass does not erase strict failures.

The evaluator's initial deck scan mistook the two white native caption backings for graph nodes, generating a false head-gap finding near the failed-sample caption. Native node symbols have a two-pixel local shape scaled by their symbol transform; native caption backing paths do not. The evaluator now distinguishes these source-native shapes. Its initial JSON is retained as `independent-deck/browser-initial-validator.json`, and the corrected scan plus opened PNG show no node/head overlap. No skill source was changed for this evaluator correction.

The literal-caption Slidev cohort finished with **0/3 strict naturalistic passes** and a strict-failing contract. Every final artifact independently passes visual checks, but recovered artifacts do not meet the joint release threshold. All four runs used the same payload SHA-256 `d64d82feb67e1d978ff760465dc55a82622b8acb5a5ca4446843502442b59b17`. The full bounded record is [slidev-echarts-sol-literal-final-20261004.json](slidev-echarts-sol-literal-final-20261004.json).

Natural-2's strict failures are a fixed-port connection refusal followed by a click-state readiness timeout. Its final source independently rebuilds and passes normal/retest, navigation replay, resize and reduced-motion inspection at **799×284**, a 6.42% area reduction from 842×288 with unchanged 18/14px labels/captions and 14px complete heads. Natural-3 initially installs an incomplete CLI package whose `dist/cli.js` is missing, then recovers; that package failure is infrastructure evidence. Its later locked-directory cleanup failure is an agent error. The final source independently reinstalls its declared dependencies, builds and passes every real click/replay/resize/reduced state at **772×278**, an 11.50% area reduction from the same baseline. Both keep every concept/relationship and full captions. These are visual wins retained inside strict-failing runs, not accepted release cases.

The repeated serving/capture burden motivated a narrowly scoped self-contained `slidev-echarts/scripts/capture_deck.py`, with its own `SpaHandler`, dynamic loopback port, Chromium/Edge discovery, click handling, browser/server cleanup, and workspace-owned JSON/PNGs. It records actual native labels, symbols, complete heads and readiness markers. It releases keyboard focus before advancing, handles SPA paths/queries, captures replay plus 1024×768 and reduced motion, waits for visible `data-render-ready` markers and two browser frames, and keeps JavaScript page errors as a failing CLI exit. Unready markers time out; hidden inactive-slide markers do not block capture. This ships only in SlidevECharts; ECharts SVG sources remain frozen.

The focused native capture suite passes: two repeated live ECharts 6.1.0 SPA captures with complete literal/XML labels, two click states, three complete heads with readable clearance, native geometry stability, replay/resize/reduced snapshots, success and injected-page-error port cleanup, failing page-error CLI, missing-build rejection and outside-workspace output rejection. An initial deliberately short-wait fixture captured before its asynchronous inset completed; that failure is retained and led to the explicit readiness protocol rather than loosening head checks. The real natural-2 deck prototype also captures cleanly through the new owned lifecycle. Focused fixture/browser artifacts stay under ignored `evaluations/runs/20261004-compaction-renderers-manual/`.

```text
uv run --script skills/slidev-echarts/scripts/test_capture_deck.py --output evaluations/runs/20261004-compaction-renderers-manual/capture-native-focused-final
uv run --script scripts/validate-skills.py --skill skills/slidev-echarts
git diff --check -- skills/slidev-echarts evaluations/diagram-compactness/consumer-audit-20261004.md
```

All pass. The new capture resources and concise build/capture guidance were frozen for a fresh `sol-capture-final` contract plus three naturalistic cases. Earlier literal-caption attempts remain retained development evidence. No strict gate, forbidden-read rule, expected output or quantitative path was weakened.

## Frozen capture-lifecycle cohort

The first completed naturalistic case, `compact-slidev-echarts-20261004-sol-capture-final-natural-1`, passes strict execution and independent native Chromium inspection. Its initial complete/static view, two declared clicks, navigation replay, 1024×768 resize and reduced motion preserve six concepts, six complete heads and both captions. The actual source rebuilds successfully with its declared Slidev 52.20.1 dependency after the agent removes disposable `dist/`. Each independent PNG was opened. There are no native text intersections, clipped envelopes, page errors or ambiguous unrelated endpoints. The accepted **808×278** graph is **7.37% smaller in area** than the helper's 842×288 baseline, with the same readable 18/14px labels/captions and 14px heads. A further reduction was rejected by the arrow-clearance gate and the last passing layout was retained.

The same-source `sol-capture-final-contract` remains a **strict failure / recovered visual pass**. Its manual native browser exploration contains readiness timeouts, speculative graphics access, misaligned endpoint IDs, a temporary stretched native view and a later shell quoting error. Every exact final file exists and the skill payload is unchanged; these facts do not erase tool failures. Independent review parses and renders the final 640×360 SVG with three exact 90×40 rectangles, complete Alpha/Beta/Gamma labels and two clear heads. A separate render of its actual delivered option passes 640×360 → 800×450 → 640×360 native resize/re-inset checks with stable repeated clearance and no page errors. The agent removed task dependencies after delivery; the evaluator restored only the task-workspace ECharts 6.1.0 dependency for this option check. This repair does not affect the copied skill or count as runtime success.

All three naturalistic runs finished with **2/3 joint strict and visual passes** on identical runtime payload SHA-256 `aa0aa5a30c6708d13ec9b65fce33b818ce77bc4f6b1fd021243fea03561e7c55`. The third natural case passes strict execution and independent initial/click/replay/resize/reduced inspection at 842×288; its tighter source-coordinate comparison is correctly rejected because the Failed sample caption would overlap Analyze. Natural-2 has no build or capture errors, but three guessed PNG reads (`slide-1-click-0.png`, `slide-1-click-1.png`, `slide-1-resized.png`) fail because the helper delivers `state-0.png`, `state-1.png`, `resized.png`. Its final native deck independently rebuilds and passes the same five actual browser states. This sampled tool mistake stays a strict failure.

Every natural case retains all six concepts, six complete heads and both full relationship captions with 18/14px native type. At the 1024×768 slide scale the minimum head gap remains approximately 3.4px. Both accepted decks preserve a useful complete initial/export view. Task-owned dependencies and build output removed during agent cleanup were restored by the evaluator only to rebuild the delivered source; this does not change the skill payload or the runtime classification. Every independent PNG was opened. A source-byte comparison between natural-3's copied bundle and canonical source found no changed files.

The native branch caption's white backing masks a short segment of the main Analyze→Review shaft. Both remaining shaft portions align as an unambiguous underpass; the source attachments, complete target heads and separately tilted branch remain attributable. It does not overlap another text glyph or node. The native DOM measured the same 18/14px fonts and identical label bounds across resized/reduced states; an apparent raster enlargement was not treated as a geometry change. A second independent reviewer opened natural-2's reduced and natural-3's click PNGs and confirmed this readable underpass judgment. The scoped visual pass establishes readable content and attributable directions, rather than asserting the absence of every caption/shaft interaction or a globally optimal layout.

The ordinary content-sized helper does not claim support for requested fixed 90×40 symbols. The contract prompt remains unchanged. After all three frozen naturalistic runs, a single fresh same-source contract retry was launched as `compact-slidev-echarts-20261004-sol-capture-contract-retry-contract`; no recovered artifact will be counted as a strict pass. The full capture-cohort evidence is [slidev-echarts-sol-capture-final-20261004.json](slidev-echarts-sol-capture-final-20261004.json).

```text
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-capture-final all slidev-echarts openai-codex/gpt-5.6-sol
uv run --script projects/diagram-compactness/scripts/review_native_svg.py compact-slidev-echarts-20261004-sol-capture-final-contract --file graph.svg --static-only
uv run --script projects/diagram-compactness/scripts/review_native_option.py compact-slidev-echarts-20261004-sol-capture-final-contract
uv run --script projects/diagram-compactness/scripts/review_native_deck.py compact-slidev-echarts-20261004-sol-capture-final-natural-1 --clicks 2
uv run --script projects/diagram-compactness/scripts/review_native_deck.py compact-slidev-echarts-20261004-sol-capture-final-natural-2 --clicks 1
uv run --script projects/diagram-compactness/scripts/review_native_deck.py compact-slidev-echarts-20261004-sol-capture-final-natural-3 --clicks 1
uv run --script projects/diagram-compactness/scripts/collect_literal_final_evidence.py slidev-echarts sol-capture-final
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-capture-contract-retry contract slidev-echarts openai-codex/gpt-5.6-sol
```

## Measured fixed-symbol repair and source freeze

The single unchanged-source contract retry is retained as **strict failure / recovered native visual pass**. Four manual-browser exploration commands fail: module loading/readiness, an incidental missing browser resource treated as fatal, and a speculative empty search. All three exact files exist and the copied payload stays unchanged. The recovered SVG is readable at exactly 640×360 with three 90×40 native rectangles and two complete heads; its delivered option independently passes native 640×360 → 800×450 → 640×360 qualification. The bounded retry evidence is [slidev-echarts-sol-capture-contract-retry-20261004.json](slidev-echarts-sol-capture-contract-retry-20261004.json). It is not relabeled a strict pass. The independent static inspector initially assumed an SSR viewBox and normal-flow SVG styling; this browser-produced SVG instead has width/height attributes and absolute positioning. The inspector now reads those native dimensions and places its replay control outside the SVG's box. That evaluator repair leaves the delivered SVG and copied skill untouched.

Repeated manual fixed-symbol preview failures motivated the authorized **Slidev-only** repair. The primary `render_concept_graph.py` input now accepts explicit positive node `width`/`height` and `symbol: "rect"`. It preserves exact symbol dimensions while measuring and wrapping the complete label at the existing readable size. If it cannot fit with protected padding, `fixed-symbol-label-fit` rejects the layout; final render still fails, and a fresh comparison probe returns accepted-false without SVG/option. It does not shrink fonts or silently enlarge supplied symbols. Unspecified symbols retain their measured content sizing, and quantitative chart paths are unchanged.

The self-contained `scripts/qualify_concept_graph.py` loads the task's pinned ECharts 6.1.0 UMD implementation and its own bundled palette/caption modules directly in Chromium. It requires no handwritten ESM server, browser discovery script or sibling source. It reapplies native inset/caption qualification at delivery, larger canvas, restored canvas, replay and reduced motion; checks exact symbol sizes, full DOM label fit, complete bounds/heads, stable repeated inset and sampled routes against unrelated nodes; and returns task-owned JSON plus an explicitly named preview. Page errors, unexpected exceptions and readability findings stay failing exits.

Focused final checks pass:

```text
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/slidev-fixed-native-final-2
uv run --script skills/slidev-echarts/scripts/test_capture_deck.py --output evaluations/runs/20261004-compaction-renderers-manual/capture-native-fixed-final
uv run --script scripts/validate-skills.py --skill skills/slidev-echarts
git diff --check -- skills/slidev-echarts evaluations/diagram-compactness/consumer-audit-20261004.md projects/diagram-compactness/scripts/review_native_svg.py
```

The native suite has ten Chromium SVG cases, including fixed 90×40 rectangles on a 640×360 canvas and repeated output; three hard layout rejections; five expected comparison probes; malformed source/partial fixed dimensions/parser failures that remain unmasked; two five-state native browser qualification cases; an actual Alpha→Gamma route through unrelated Beta that returns a failing qualification; and outside-workspace output rejection. Both fixed and ordinary workflow native qualification pass with at least 3.25px head clearance, complete labels and preserved dimensions. The fixed-symbol live PNG was independently opened. The existing capture suite passes its real native labels, two click states, replay/resize/reduced motion, readiness, SPA/query handling and success/error lifecycle cleanup.

All Slidev sources were frozen before the fresh `sol-fixed-final` contract plus natural-1/2/3 serial cohort. Its runtime payload contains 46 files with SHA-256 `dceb84485e70c00cc7eb6a1f36600533627d99a18768c178e001fa6063541178`. Earlier capture/retry cohorts remain development evidence for the superseded bundle. The accepted ECharts SVG source and cohort were not changed. Final release acceptance requires the new same-source contract and at least two of these three naturalistic cases to pass both strict and independent visual gates.

## Fixed-source development results and first-draft repair

The complete `sol-fixed-final` cohort did **not** pass the naturalistic release threshold. Every run observed only the authorized Sol model, created all exact outputs and preserved the copied source. Its complete bounded evidence is [slidev-echarts-sol-fixed-final-20261004.json](slidev-echarts-sol-fixed-final-20261004.json), including explicit independent manual visual dispositions.

| Case | Strict | Independent actual native inspection | Disposition |
| --- | --- | --- | --- |
| Contract, 70.077s | Pass | Pass: complete 90×40 rectangles/labels on 640×360; two complete heads with 3.25px clearance; actual option remains readable at 640→800→640. | Development pass for superseded payload. |
| Natural 1, 358.649s | Fail | Recovered final deck passes all five opened click/replay/resize/reduced states. | Four initial guessed-layout final renders trigger three caption/node overlap gates and one undersized-canvas gate. Recovery does not erase errors. |
| Natural 2, 242.596s | Pass | Pass: six opened native states, including two declared clicks, replay, 1024 resize and reduced motion; six complete concepts/heads and clearly attributable return/failed routes. | One of three natural cases passes jointly. Manual native layout preserves its 17px labels/13px heads and uses readable legend captions. |
| Natural 3, 472.786s | Fail | **Fail**: the diagonal failed-sample shaft crosses the glyphs of the required `FAILED SAMPLE` graphic caption in every opened state. | Three initial final-render caption/node gates, followed by a recovered caption legibility defect. Neither automated envelope success nor the review's overlap-free claim overrides actual pixels. |

Natural 3 replaces the failed native link caption with `GraphicComponent` text at left 394/top 170. The actual shaft crosses that caption's letters. This is different from the previously accepted, aligned white-backed underpass: here the glyphs themselves intersect the shaft. The independent envelope checker reports complete nodes/heads and nonoverlapping text bounds, which does not check shaft/glyph crossing. The durable evidence retains that automated success and an explicit manual visual failure without relabeling either. All earlier cohort failures remain retained.

The remaining repeated burden is the authoring sequence: the guide presented the initial guessed layout as a final render and restricted `--probe` to later tighter comparisons. The primary Slidev workflow now begins with IDs/full labels/directed relationships and measured ranks/content bounds. Every unverified first draft, including prescribed rectangles and optional custom coordinates, uses a **standalone** probe with fresh candidate paths. The agent must read `accepted` before preview/qualification; a zero exit deliberately includes expected rejection, so `probe && preview` is invalid. An accepted native preview precedes the exact final render without the probe flag. The rule remains primary through live clicks: use native link captions and their adapter; do not bypass a rejected caption gate with unqualified graphic text. Truly custom graphic captions require actual shaft/glyph clearance inspection in every settled state.

Renderer behavior, fixed-symbol support, native qualification, final hard failures, unexpected-input/parser/dependency failures and quantitative chart paths are unchanged. A focused regression performs a rejected first custom draft (accepted-false, exit zero, no SVG/option), returns to measured complete-label input, accepts a fresh probe and renders the identical inspected native final SVG without probe mode. The full native suite still checks fixed dimensions, full labels/heads, native resize/replay/reduced states and actual route-crossing failure:

```text
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261004-compaction-renderers-manual/slidev-first-probe-native-final
uv run --script scripts/validate-skills.py --skill skills/slidev-echarts
git diff --check -- skills/slidev-echarts projects/diagram-compactness/scripts/collect_literal_final_evidence.py evaluations/diagram-compactness/consumer-audit-20261004.md
```

These focused checks pass. The compact reference remains 9,934 bytes. A new same-source contract plus three naturalistic cases is required after this authoring repair; no prior passing case is reused as release evidence.

The first-probe source is frozen with 46 runtime files and SHA-256 `f0aba4414a1bef31a67b66f768464a09b6218b3dfd6b12da48368c4827620fd7`. Only the Slidev entry point, compact reference and regression test changed from the preceding freeze. Native renderer, qualifier, capture and quantitative implementations are byte unchanged. The actual source/runtime/full authoring audit passes all 34 skills and 68 copied bundles; its ignored proof is `projects/diagram-compactness/artifacts/reviews/slidev-first-probe-source-freeze.json`. The next bounded cohort uses unchanged prompts and exact outputs under the unique revision `sol-first-probe-final`.

## First-probe cohort: retained native visual failures

The four serial Sol trials used that exact frozen payload and unchanged contract/natural prompts. All four strict executions pass, with valid event JSON, the requested model, exact artifacts, no tool errors, a clean read surface and unchanged copied skill bytes. Their native visual gate does not pass the required natural repetition policy:

| Case | Strict execution | Native visual review | Joint result |
| --- | --- | --- | --- |
| Contract | Pass | Pass; exact 90×40 symbols and 640×360 canvas | Pass |
| Natural 1 | Pass | Pass | Pass |
| Natural 2 | Pass | Fail; unrelated routine shaft crosses leading glyphs of `Failed sample` | Fail |
| Natural 3 | Pass | Fail; same native caption/shaft defect | Fail |

The bounded ledger is [slidev-echarts-sol-first-probe-final-20261004.json](slidev-echarts-sol-first-probe-final-20261004.json). These trials remain development evidence; the contract and natural 1 are not reused after the native repair.

The earlier automated browser checker had checked text against bodies and other text but omitted caption/glyph checks against shafts and heads. An `animations="disabled"` independent resized screenshot was also more permissive than the actual default capture. Raw nearest-neighbor crops and byte comparisons establish the actual defect in both default resized and reduced native screenshots; their caption pixels are identical. The evidence does not establish a reduced-only font or cache cause. The original PNGs and trial sources are unchanged. Ignored pixel proof is `projects/diagram-compactness/artifacts/reviews/caption-default-diagnosis/comparison.json`, with both original default states and authored-output comparisons.

## Native caption placement repair

The Slidev-only adapter now searches nearby longitudinal positions and both normal sides of the existing native route, choosing the smallest clear displacement. It measures native backing together with emitted DOM glyph bounds, protects complete heads and bodies, and tests every shaft, including the caption's own shaft. It retains native ECharts text, full labels, fonts, palette, symbols, strokes and arrows. Final emitted glyphs receive a second shaft-clearance postflight. No canvas enlargement or replacement graphic caption is used. The browser qualifier independently samples actual SVG paths and checks glyph/backing polygons against all shafts and complete heads.

Only the owning Slidev caption adapter, SSR helper, browser qualifier, regression test and compact reference change from `f0aba…`. The quantitative recipes and the accepted ECharts animated SVG bundle remain unchanged. `caption-clearance` is explicit expected layout feedback only in a probe: rejected probes exit zero with `accepted: false` and deliver no SVG/option. The same final render fails nonzero; invalid input, parsing, dependencies and unexpected exceptions remain hard failures.

Focused commands:

```text
uv run --script skills/slidev-echarts/scripts/test_concept_graph.py --output evaluations/runs/20261005-compaction-renderers-manual/slidev-caption-search-native-final
uv run --script projects/diagram-compactness/scripts/reproduce_caption_placement.py --output projects/diagram-compactness/artifacts/reviews/caption-placement-regression-final
uv run --script scripts/validate-skills.py --skill skills/slidev-echarts
uv run --script scripts/audit-skill-authoring.py --check-bundles --output projects/diagram-compactness/artifacts/reviews/slidev-caption-placement-source-freeze.json
```

All pass. The focused suite covers ten deterministic native SVG cases, repeated geometry, literal braces/XML, fixed 90×40 symbols, explicit canvas dimensions, expected probe rejection with no artifacts, hard final rejection, invalid/parser failures and native delivery/resize/restore/replay/reduced states. Actual DOM glyph envelopes clear all emitted shafts and heads; head-to-body gaps remain at least 3.2499 px.

The project regression copies the exact original natural 2 and 3 components without changing their source bytes, then builds old/new native decks with their own bundled adapters. Both original collisions reproduce. In the corrected default capture, all clicked/replayed/resized/reduced states have at least 4.43 px retest and 5.41 px failed-sample glyph-to-shaft clearance. Canvas, node and head paths, shaft geometry/strokes, label strings and fonts are equal between each old/new state. Full native PNGs and nearest crops are retained under `projects/diagram-compactness/artifacts/reviews/caption-placement-regression-final/natural-{2,3}/{old,new}/`; the report records original Vue hashes and screenshot hashes. Development reproduction attempts remain retained, including classifier, initial-state timing and wake-lock permission corrections.

The repaired source is frozen with 46 runtime files and SHA-256 `c5f20fbe78097acd533a6825fac55a1c4e74c4361f696e236d2e96168f789806`. All 26 accepted ECharts animated SVG runtime files still have SHA-256 `b51f5e3e971863ccc196b8d13cf70f6b67ccddf593019d390c87293125eaa8e4`. Exact inventories are in `projects/diagram-compactness/artifacts/reviews/slidev-caption-placement-source-snapshot.json`; the fresh authoring audit passes 34 canonical sources and 68 copied runtime/full bundles. A fresh unchanged contract and three natural cases will use the unique revision `sol-caption-placement-final` after independent source closure. No earlier trial is harvested as a release pass.

## Final caption-placement cohort: all four joint passes

The peer byte review closes all 46 Slidev runtime files at that exact `c5f20…` hash and all 26 accepted ECharts animated SVG files at unchanged `b51f5…`. Its proof is `projects/diagram-compactness/artifacts/reviews/slidev-caption-placement-peer-byte-review.json`. The following fresh serial command completes on 2026-10-05 with unchanged prompts, exact output gates and the explicit pre-recorded Sol model exception:

```text
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-caption-placement-final all slidev-echarts openai-codex/gpt-5.6-sol
uv run --script projects/diagram-compactness/scripts/collect_literal_final_evidence.py slidev-echarts sol-caption-placement-final all
```

| Case | Duration | Strict execution | Independent native/browser | Actual manual visual | Joint result |
| --- | ---: | --- | --- | --- | --- |
| Contract | 83.420 s | Pass | Pass | Pass | Pass |
| Natural 1 | 231.802 s | Pass | Pass | Pass | Pass |
| Natural 2 | 246.238 s | Pass | Pass | Pass | Pass |
| Natural 3 | 256.435 s | Pass | Pass | Pass | Pass |

The full bounded evidence is [slidev-echarts-sol-caption-placement-final-20261004.json](slidev-echarts-sol-caption-placement-final-20261004.json). Every case observes only `gpt-5.6-sol`, valid JSON events, zero tool errors, exact requested artifacts, a clean runtime read surface and unchanged copied skill bytes. Each case has its own actual native browser proof and manual review; the three natural cases all pass the required repetition policy. No former cohort pass is counted here.

The contract preserves the complete 18 px Alpha/Beta/Gamma labels, exact native 90×40 rectangles and 640×360 delivered canvas. Independent static and actual live native option checks confirm full heads with 3.25 px body gaps, actual 640→800→640 resize and zero repeated-inset changes. All eight native images were inspected.

Each natural deck preserves all six complete concepts and six directed relationships through its normal-flow and one-click retest states, replay, laptop resize and reduced motion. Both `Retest` and `Failed sample` remain complete, opaque and font14 or larger, with clear return/branch attribution and complete heads. Default native full images and nearest raw-pixel crops were inspected, including the glyph area that failed in the previous source. Measured minimum glyph-to-shaft paint gaps are:

| Natural case | Retest | Failed sample |
| --- | ---: | ---: |
| 1 | 4.4298 px | 5.4114 px |
| 2 | 5.3126 px | 5.7942 px |
| 3 | 6.4611 px | 6.4431 px |

Natural 1 and 2 removed authored intermediate captures before their final handoff. Their exact expected deck sources and review remain present, so this does not change the strict result; the report does not claim those authored PNG paths still exist. The independent reviewer rebuilds source-identical copies of their retained decks and retained read-only skill resources in evaluator-owned project artifacts, checks original source/deliverable SHA-256 values before and after, and captures actual native default states there. Natural 3 retains all five authored PNGs; those and all five independent default states were inspected. Original trial sources, deliverables and PNGs are unchanged. Each run's `independent-retained-build/build-proof.json`, `independent-deck/browser.json`, `manual-review.json` and `caption-pixel-crops.json` record this distinction.

The project-only checker now requires positive relationship-caption association before clearance: `Retest` must belong to the unique emitted Review→Analyze return and `Failed sample` to the unique Analyze→Quarantine branch, based on actual node/route/glyph geometry. Missing, hidden or tiny captions fail. A readable opaque homonym placed in clear legend space cannot substitute for either relationship. The five-state regression passes ten caption/state checks for positive attribution and omission, zero opacity, font13 and replacement-legend rejection. Peer review approves this correction for the known six-node prompt with mandatory manual native frame review; it does not claim general native Text provenance or certify arbitrary diagrams. No frozen skill source or prompt changes accompany that checker correction.

The unchanged lifecycle suite also passes native two-click/replay/resize/reduced capture, full literal labels/heads, SPA query routing and port cleanup on success/page errors; page errors, missing builds and external output paths still fail. Its proof is `evaluations/runs/20261005-compaction-renderers-manual/slidev-caption-capture-native-final/test-report.json`. Structure, in-bundle validation and `git diff --check` pass. This closes the Slidev ECharts compact conceptual diagram behavior; quantitative chart dimensions and recipes remain unchanged, and no global packing-optimality or model-wide certification is claimed.
