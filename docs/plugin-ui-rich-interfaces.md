# Rich plugin interface lab

The local **Service Observatory** project implements a service graph, a linked
metrics view, an exact table, a selected-service inspector and an attention
queue. It compares six host routes against the same synthetic task. The
[main preview source](../projects/plugin-ui-rich-interfaces/index.html) links
the runnable alternatives after the build below.

This is a local development project. It does not add a published Pages example
set, change personal host configuration or deploy a cloud agent. Generated
payloads, packages, screenshots and traces remain ignored under project
`artifacts/` or `evaluations/runs/`.

The [target-host follow-up](../evaluations/desktop-plugin-ui/target-hosts-20261112.md)
records actual application and terminal captures, three observed UI repairs,
the portable Codex loader trial, and remaining installation/access gates. Its
evidence is additional to the earlier frozen forward-model cohorts.

## Choose the interface

| Host | Authored interface | Evidence and remaining boundary |
| --- | --- | --- |
| Claude Desktop Chat | Portable MCP App with graph/chart/table tabs, inspector, direct refresh and optional expansion | Real stdio, SDK and browser tests pass. Existing Reflex XY chart paint and More options were observed in the signed-in host; the new package's installation/paint is separate. |
| Claude Code | Native service/view selectors, surface-specific SVG, exact text and a scoped pane | Real native engine tests pass across terminal/Desktop/VS Code and narrow columns. Actual signed-in native pixels remain untested. |
| Pi | Keyboard TUI with dependencies, sampled bars, all 24 exact hourly values and a table; RPC dialogs and print fallbacks | Actual TUI key/character output, real RPC/print, cancellation and geometry checks pass. Browser text previews do not certify terminal pixels or a custom RPC client. |
| Codex | Portable MCP package plus a browser alternative and useful CLI/text results | Installed app-server 0.167.0-alpha.3.2 connects the configured server and executes the exact tool without a model turn. Portable catalog installation and stock inline painting remain separate. |
| ChatGPT Desktop | The shared standard-bridge MCP App with local state and capability-aware actions | Protocol/browser evidence passes. Local-thread installation and new component paint in the actual Desktop build remain untested. |
| Gemini Enterprise | Native Material/VegaChart stream, or a user-opened Canvas root containing IFrameSrcdoc | Official component and Vega-Lite schema checks pass; the embedded content works in a local CSP fixture. A2A hosting/actions, administrator registration and Gemini Enterprise painting are untested. |

Use [the host-specific skill index](desktop-plugin-ui.md) for installation of the
authoring skills. Each bundle remains usable without a sibling skill.

## Explore and reproduce

Run commands from the repository root. Use Node 24+, Python/uv and a supported
Edge/Chromium installation for the browser checks. Project dependencies are
pinned in [package.json](../projects/plugin-ui-rich-interfaces/package.json).
The build can reuse this workstation's existing pinned development installation;
on another checkout install the declared project dependencies first.

```powershell
npm install --prefix projects/plugin-ui-rich-interfaces
uv run --script projects/plugin-ui-rich-interfaces/scripts/fetch-schemas.py
uv run --script projects/plugin-ui-rich-interfaces/scripts/make_data.py
node projects/plugin-ui-rich-interfaces/scripts/build.mjs
uv run --script projects/plugin-ui-rich-interfaces/scripts/build-adapters.py
node projects/plugin-ui-rich-interfaces/scripts/build-previews.mjs
node projects/plugin-ui-rich-interfaces/scripts/verify-browser.mjs
python -m http.server 8872 --bind 127.0.0.1 --directory projects/plugin-ui-rich-interfaces
```

Open `http://127.0.0.1:8872/index.html`. The focused and overview workspaces use
the same data and selection model. The native/Pi/Gemini pages explicitly label
their local preview layer. The separate XY export is produced through the
connected renderer; the core build does not require that plugin.

The synthetic data generator is the source of the shared records and hourly
observations. Derived data files are ignored and regenerated locally. Each
native/Pi package receives its own runtime data copy; the runtime never reads a
sibling skill or another host package.

The MCP build inlines local D3, styles, data and application code, bundles the
server dependencies and emits root portable manifests. It uses function
replacements when inlining JavaScript so replacement tokens inside a bundle
cannot corrupt the generated HTML. Runtime stdout contains only protocol JSON.

Create review ZIPs and a clean extraction with:

```powershell
uv run --script projects/plugin-ui-rich-interfaces/scripts/package.py
```

Artifacts appear under `projects/plugin-ui-rich-interfaces/artifacts/packages/`:
`service-observatory.zip`, `claude-native.zip`, `pi-extension.zip` and
`gemini-payloads.zip`. The Gemini archive contains UI payloads, not a deployed
A2A service. `clean-portable/` is the extracted no-dependency-tree MCP canary.
Use the actual Node command and working directory declared in its `mcp.json`.

## What the critique changed

The focused workspace is the default because the selected service and one
analysis view remain readable together. Overview is a deliberate comparison
alternative; it increases page length and scanning. Opening every chart,
filter and export setting at once was not treated as a quality goal.

The 320/390px layout shows the selected service and its direct neighbors as a
readable list, with visible scope and an explicit full-list action. It preserves
edge direction. The desktop map keeps stable positions, arrowheads and typed
edges, and distinguishes keyboard focus from selection. Long labels retain
their full accessible description while visible text stays inside the node.

The latency view declares units, UTC hours and its daily window. The objective
is a separate dashed reference, not another observation. A shared scale keeps
service comparisons meaningful, and an exact-values table accompanies the
chart. Narrow charts recompute their viewBox/ticks. Pi's bars clearly disclose
their three-hour sampling; a separate Values view retains all 24 observations.

Graph, table, inspector, KPIs and exports derive from one authoritative model.
Selection survives view changes and remains explicit when a filter excludes
it. A filtered export records its scope, revision and excluded selection. Empty
filters, denied panes, failed refresh, retry, canceled late responses and refused
expansion have useful recovery behavior. Optional server actions disappear when
the host does not advertise them; local inspection and exact data remain usable.

The original XY legend overlapped the final upward segment near the objective.
The verified `loc="lower right"` placement leaves that result visible. This was
an authored chart composition issue, not a limitation of the host's renderer.
Saved-image and interactive-HTML semantics stay distinct.

Gemini's catalog offers different useful boundaries: native tables/tabs and
VegaChart preserve host styling; Canvas is a root component for a side panel;
IFrameSrcdoc permits custom composition while blocking outbound connections.
The complete native template uses object-shaped `header`/`field` columns and a
chart spec bound from the surface model. A raw Vega object in the wrong wrapper
or an array of header strings can pass a shallow structural check and fail the
official schema. [Official composite catalog](https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json).

For MCP Apps, capability negotiation and actual returned display mode govern
the enhanced controls. A method existing on an SDK does not establish permission
to download a file or expand a view. The portable data view remains useful when
optional host file APIs are absent. [OpenAI UI contract](https://developers.openai.com/plugins/build/chatgpt-ui),
[Claude display modes](https://claude.com/docs/connectors/building/mcp-apps/display-modes).

## Reusable skill improvements

The seven UI bundles link their own `references/rich-interfaces.md` from
`SKILL.md`. They cover topology selection, bounded neighborhoods and dense
matrices, meaningful Sankey accounting, consistent chart domains, exact values,
large-data reduction, linked state, revision/authority checks, keyboard/focus,
reflow, host alternatives and evidence-based pixel critique.

Two complete runtime resources reduce implementation guesswork:

- [Pi staged inspector](../skills/pi-extension-ui/assets/templates/pi-command/inspect-flow.ts)
  and [real RPC checker](../skills/pi-extension-ui/scripts/check_rpc_command.py)
  cover TUI/RPC dialogs, cancellation across awaits, exact notifications and
  inference-free JSON print without reading installed documentation.
- [Gemini chart/table stream](../skills/gemini-enterprise-ui/assets/templates/chart-and-table.json)
  demonstrates correct envelopes, bindings, table columns and literal/model data.

The owning [XY connected-adapter reference](../skills/reflex-xy/references/connected-adapter.md)
separates simple presets from versioned mixed-chart marks/components. Its
focused [wire checker](../skills/reflex-xy/scripts/check_connected_spec.py) rejects
numeric Sankey indices when nodes are labels, guessed component `type` fields,
unpaired values and nonfinite data. It does not claim to validate the entire
native library or every adapter feature.

## Validation commands and limits

```powershell
node projects/plugin-ui-rich-interfaces/scripts/verify-browser.mjs
node projects/plugin-ui-rich-interfaces/scripts/verify-previews.mjs
node projects/plugin-ui-rich-interfaces/scripts/verify-pi.mjs
claude plugin validate projects/plugin-ui-rich-interfaces/claude --strict --json
claude plugin test projects/plugin-ui-rich-interfaces/claude
uv run --script projects/plugin-ui-rich-interfaces/scripts/validate-a2ui.py projects/plugin-ui-rich-interfaces/artifacts/payloads/gemini/native-messages.json projects/plugin-ui-rich-interfaces/artifacts/payloads/gemini/canvas-messages.json --label final-payloads
uv run --script skills/reflex-xy/scripts/test_connected_spec.py
```

Set `CLAUDE_CONFIG_DIR` to a project artifact directory when running the native
commands if keeping all test state local is required. The Pi checker sets its
own task-local state. The Codex test takes the actual installed core path:
`uv run --script projects/plugin-ui-rich-interfaces/scripts/verify-codex.py
--codex <installed-core> --label <fresh-label>`. It uses an isolated home, removes
API-token variables from the child, keeps policy `never`, and requests no model
turn. It does not modify the user's actual app configuration.

The A2UI validator binds both component and function unions into the official
envelope's `catalog.json` slot and preserves upstream schema base URIs. Theme
semantics, A2A action wrapping and Google host acceptance are outside its check.
Run `fetch-schemas.py` before an offline rerun. It verifies the study's pinned
catalog and Vega-Lite bytes under `artifacts/data/`; source digests are recorded
in validation output. A changed primary-source digest requires a new review of
the source contract rather than an automatic version upgrade.

[The full evaluation record](../evaluations/desktop-plugin-ui/rich-interfaces-20261112.md)
preserves all strict runs, candidate identities, failures, source preflights and
independent artifact checks. Browser fixtures, native engines, schemas, PTY
characters and signed-in product paint are separate evidence. No complete
accessibility conformance or universal host compatibility is claimed.
