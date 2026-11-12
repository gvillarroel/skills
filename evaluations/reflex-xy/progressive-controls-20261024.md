# Progressive XY controls — 2026-10-24

## Problem and resulting behavior

The previous component exposed palette/view switches, five downloads, an engine
badge, mark metadata and persistent status prose around the chart. The user
requested a simple first view with discoverable advanced capabilities. Release
**0.2.0** uses one primary task and one options disclosure, with Colorset 1 still
the default and explicit Colorset 2 preserved.

The MCP component initially exposes Save image, More options and optional host
fullscreen around an interactive chart. Display and Export groups contain
palette/view selectors, chart tools and one alternate-format selector/download
action. Routine success prose, engine metadata and duplicate outer chart title
are removed. Its compact preview hides only native toolbar chrome; hover and
navigation remain available, while original HTML downloads remain unchanged.
The toolbar toggle preserves the existing view rather than navigating/reloading.

Claude Code initially shows the native preview, Open interactive chart and More
options. Advanced controls group palette/sample/rerender and file actions. The
sample selector explicitly warns it replaces current data. Preview titles are
not duplicated, redraws do not unconditionally autofocus, and routine/repeated
warnings do not occupy the default pane. Last successful data remains the edit
target even after a subsequent failed request.

The [primary-source research note](../../projects/reflex-xy-plugins/notes/interaction-sources.md)
records NN/G progressive disclosure, W3C disclosure semantics and enhanced target
size. Initial action count is a project choice; no human usability study or
complete WCAG claim is made. Native host focus and pointer geometry remain
distinct from measured DOM behavior.

## Frozen reusable skill subject

Promoted a compact self-contained recipe at
`skills/reflex-xy/references/interaction-design.md`, routed conditionally from
the entry point for chat/panel work. The recipe requires no project or sibling
resource. Rendering helpers, XY pin, data grammar and geometry are unchanged.

- Runtime: **19 files**, SHA-256
  `fdb0862f1607e12ff4ddaf1703e3703ce8e12885752cc451d7df29d7f3e36c87`.
- Source/full: **32 files**, SHA-256
  `17447450ed025edcc643c1271461ef09812ff8b45155de6f116767e835153c2b`.
- Source/runtime/full bundle audits pass at
  `projects/reflex-xy-plugins/artifacts/progressive-controls-audit/report.json`.

## Scoped isolated forward test

Ran one fresh strict contract with the existing recorded
`openai-codex/gpt-5.6-sol` exception after earlier Spark provider rejection:

```powershell
uv run --script scripts/run-pi-skill-eval.py reflex-xy --prompt-file evaluations/pi-prompts/reflex-xy-progressive-controls.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id 20261024-reflex-xy-progressive-controls-contract --expect-output interaction-plan.json --expect-output index.html --expect-output-json-field interaction-plan.json::default_colorset=colorset1
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-reflex-xy-progressive-controls-contract/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

**1/1 strict/artifact/manual** passes. The observed model matches, all **17**
tool calls are error-free, read surface is focused, exact outputs exist and the
19-file skill payload is unchanged. The prompt supplies static SVG geometry
and explicitly asks for a focused interface fixture, without a live server.
Do not describe this as generating a complete MCP integration from scratch.

Independent browser review passes **2/2** viewports at 1100 and 390 CSS pixels:
two initial actions, hidden controls excluded, Enter/Space disclosure,
44-pixel targets, explicit palette switching, selection retention, unchanged
geometry and downloaded SVG matching the selected chart. No overflow or page
errors. The narrow first-view screenshot was manually inspected.

```powershell
uv run --script projects/reflex-xy-plugins/tests/validate_interaction_fixture.py --html evaluations/runs/20261024-reflex-xy-progressive-controls-contract/workspace/index.html --output-dir projects/reflex-xy-plugins/artifacts/progressive-controls-pi-review
```

The fixture honestly labels unimplemented PNG/interactive HTML choices; the
shipping adapters retain all five formats through their actual MCP service.
Retain the separate earlier default-palette strict failure and broader cohorts.
This narrow success does not change the overall skill's **validating** status.

## Adapter validation and evidence

Native Code **2.1.302** strict validation, **8/8 native tests** and **195 portable
assertions** pass after the final UI refinement. Final Mod source SHA-256:
`90bf80118cff34c2027dc5b45c42ba87c7fe8a5284e5f5f697267bf259b4ef4f`.
Official MCPB **2.1.2** validates the updated Desktop manifest. Engine tests cover
progressive controls, supported surfaces, data preservation, errors and defaults;
they do not establish installed Desktop/VS Code painter or keyboard acceptance.

MCP type checking, **4/4 HTTP/security boundary suites**, build and real bundled
stdio checks pass. The browser acceptance runs the actual Python/HTTP service
and official MCP Apps bridge, with three initial actions maximum, stable
disclosure position, keyboard behavior, all five exports, error recovery,
canonical paint and 44-pixel authored targets. Focus returns to the Palette
selector only when appropriate; deliberate focus movement to another action is
preserved. A separate default-palette regression remains covered.

Independent final progressive checks pass **2/2 host variants** at
`artifacts/independent/0.2.0/progressive-v4/report.json` inside the project.
One host supports `ui/download-file`; the other uses `ui/open-link`. Both exercise
compact native hover, wheel zoom/double-click reset, toolbar toggling without
navigation or zoom loss, repeated Image/Interactive switching, both palettes,
all formats, loading/error retention, Enter/Space/Escape/focus, hidden tab-order
controls and mobile targets. At 390 pixels, native viewport/root measure 368
pixels, with the 314-pixel data canvas plus its labelled axis margin. Initial
desktop, native mobile and collapsed mobile captures were manually inspected.

The final widget SHA-256 is
`5d1e0e5a6f1d6199f594d6e7e2323ad85b0b6c4926b520ffd355320c8491dd2c`.
Its resource is `ui://reflex-xy/chart-v2.html`; old layout cache keys are not
reused. Canonical interaction guidance is available through both adapters'
exact reference allowlists.

## Final distributions

Built once into `projects/reflex-xy-plugins/artifacts/releases/0.2.0/`:

| Archive | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `reflex-xy-claude-code.zip` | 33 | 85,218 | `be134f434ee011df87bcd0ffb042e93b8a48ed4fb89a2e5d005a8334d6dbdd48` |
| `reflex-xy-chatgpt.zip` | 46 | 525,630 | `f16f6f0140b890bd97391354b3d1ed01c7ec376ffbf4021ef8bcae163c01fa7a` |
| `reflex-xy-claude-desktop.mcpb` | 30 | 453,373 | `1229bfc9d966271243cb5abbf4cc1976395d50d45a5715007b16b588d7ca2225` |

Earlier 0.1.0 and 0.1.1 archives and evidence remain preserved; earlier geometry
matrices are not rerun or pooled into this UI-only change. Packaged verification
is kept separate from source-level tests.

Independent extraction checks accept all three final archives, including safe
paths, payload exclusions, 20 local skill links per archive and byte identity
for all 19 canonical runtime resources. Inventories remain unchanged after
execution. The extracted Code plugin passes native strict validation and 8/8
native engine tests. Official MCPB 2.1.2 accepts the extracted Desktop manifest.
The manifest-to-bundled-Node-to-uv stdio path passes 4/4 native renders in one
connection: explicit Colorset 2 followed by omitted-to-Colorset 1, repeated with
supplied generic data. Native paint, JSON, all downloads, CSP, resource URI v2
and the interaction reference pass. Final package, source-identity, native-Code
and stdio evidence resides under
`projects/reflex-xy-plugins/artifacts/independent/0.2.0/`.

## Retained interaction failures and corrections

- An earlier options region changed the trigger's position when expanded.
  A stable action-row button and separate controlled region fix the jump.
- The initial Image/Interactive transition used `display:none` on the live
  native frame. Independent v1/v2 captures exposed intermittent blank/underfilled
  charts, even when immediate DOM size checks passed. These reports remain
  retained as pre-fix product failures. The final subject keeps the inactive
  frame laid out, visually hidden and inert, preserving native lifecycle/state.
- A later mobile capture appeared clipped because the protocol test page was
  still scrolled to export controls. Settled layout checks, parent scroll reset,
  native-frame captures and manual inspection distinguish capture framing from
  chart paint. Those diagnostics are retained; the final subject passes.
- Showing native tools originally navigated between HTML variants. A fixed
  parent-only boolean message now toggles a preview CSS rule without reloading.
  Original HTML is byte-identical after removing the preview-only shim.

## Boundaries

The component uses the official MCP Apps bridge with real Python XY and real
transports in a protocol host fixture. Signed-in Claude Desktop/ChatGPT account
installation and native app painting remain untested. Compact preview CSS and
a fixed boolean toolbar message do not execute submitted code or modify saved
chart data/source. Static image exports represent the original rendered view.
For live browser viewport exports, use native chart tools.

Repository pattern-ID, skill, independence, payload and local synchronization
checks pass. Runtime/source/full audits establish exact copied resources, not
model-wide usability or broad chart-authoring certification.
