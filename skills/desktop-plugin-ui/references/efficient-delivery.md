# Deliver useful UI with low implementation and runtime cost

Snapshot: 2026-10-31. These are engineering selection rules, not measured
latency or cost rankings. Use the exact host, frontend and mode. Read the
selected host reference for API/installation detail; do not load every catalog.

## Choose the delivery surface

For reusable plugins, share data and action contracts, then choose small host
adapters. Two presentation families often cover the task: web components in
compatible MCP Apps hosts, and native/terminal controls elsewhere. This is a
useful starting architecture, not a requirement to build both families.

| Target | Efficient starting point | Add complexity for a concrete need |
| --- | --- | --- |
| ChatGPT | Useful tools plus a focused MCP App card for structured interaction. | Use a supported larger mode for maps, substantial comparisons or editing. Detect optional extensions. |
| Claude Desktop Chat | Reuse the MCP App's web component and shared bridge logic where compatible. | Adapt theme, dimensions, capabilities and permissions to Claude; shared HTML does not prove host acceptance. |
| Codex desktop / IDE | Readable tool results, artifact links and supported host controls; test any rich component in that frontend. | A local HTML preview/browser view can serve a visual task. Build an owned client when persistent navigation or application state justifies its lifecycle. |
| Codex CLI | Compact text/structured results, files, commands and negotiated elicitation. | Offer a browser artifact for rich visual work; HTML transport does not establish terminal rendering. |
| Pi TUI | One TypeScript extension, a command, native select/input/confirm and explicit arguments. | Use compact keyed status with on-demand detail. Custom TUI serves specialized rendering/input; rich maps or spatial editing may justify a separate browser view or owned web client. |
| Pi RPC | Explicit inputs and results; native dialog requests handled by the client. | An owned web client may draw its own UI, but must implement request correlation and cancellation. RPC has no custom terminal painter. |
| Claude Code / Desktop Code | Commands and supported native controls; a Mod pane when its interaction is useful. | Verify each frontend's elements/props. Native node trees and MCP App HTML are different adapters. |

The [OpenAI MCP UI guide](https://developers.openai.com/plugins/build/chatgpt-ui)
documents optional web UI with useful tool fallback; its component library is
an option for an existing React UI. The
[Claude design guide](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines)
supports focused inline content with a larger view for extended work. Use
[Codex](codex-limits.md), [Pi](pi-extensions.md) and
[native Claude](native-patterns.md) for the respective boundaries.

For a one-off result, use an existing host visualization, native prompt or
artifact viewer when available. A reusable plugin may justify packaging that
a single chart does not need. A local prototype or architectural proposal can
explore an owned frontend within task scope; installing/deploying a new product
is a separate action. Preserve the user's chosen product and workflow.

## Reuse behavior and choose components deliberately

Define stable record IDs, authoritative state/revisions, validation, action
inputs/results and cancel/retry semantics once. Reuse ordinary domain functions
across adapters where that reduces maintenance. Keep manifests, permission
flows, presentation and focus/lifecycle handling host-specific.

For example, an export reviewer can share list, inspect, open and retry
operations. ChatGPT/Claude Chat show a card or table; Pi uses a selector and
inspector; a CLI returns a compact outcome and artifact reference. All adapters
target the same export ID and enforce the same validation/commit rules.

Prefer predefined components receiving data for predictable workflows: list,
result card, form and details. Small HTML/CSS/JavaScript views need no full web
application framework. Reuse the project's framework and component library
when state, complexity or existing dependencies make it the simpler choice.
Keep a single clear primary action per decision and essential recovery visible.

Run filtering, sorting, selection, local validation, navigation and known
button actions directly. Reserve inference for interpretation, reasoning or
generation. A conversational action can intentionally start a model turn;
label it and count it separately. Opening a component may require a host model
turn even when later interactions are direct. A tool/network request is not
automatically an inference request, and direct execution still checks authority.

## Place OpenUI at the rendering layer

Here OpenUI means Thesys OpenUI. Use it when the task benefits from model-chosen
component composition, with a registered component library, compatible renderer
and explicit action handlers. A fixed workflow can remain data-driven without
generating its layout anew. This is a task-based choice, not a ban on generative UI.

OpenUI's [coding-agent setup](https://www.openui.com/docs/mcp) teaches assistants
to build OpenUI applications and exposes documentation through MCP. Installing
that skill or documentation server does not install a renderer into Codex,
Claude, Pi or ChatGPT. Model/provider compatibility and visible host UI are
different capabilities.

The [chat UI integration](https://www.openui.com/docs/build-agents/chat-ui)
requires the application to render OpenUI Lang and handle actions. Bundling it
inside an MCP App is an architecture to validate, not a tested universal host
integration. Native/TUI surfaces need their own adapter or a separate supported
web view. Route deterministic actions directly rather than sending every click
as a new user turn. Never treat generated UI as permission to execute its actions.

## Verify the claimed efficiency

Compare setup/dependencies, time to first useful result, decisions/steps,
bundle size, maintenance across hosts and model requests per interaction where
those costs matter. Label estimates; do not invent benchmarks or user preference.
Keep a justified extra control, service or larger view when the task needs it.

Exercise the same IDs/actions across adapters, cancel/retry and stale replies;
check keyboard focus, narrow layout and the actual supported host container.
Use [visual review](visual-review.md) for material layout changes and keep
browser, native/protocol and signed-in-host evidence separate. Reuse a web
component only after checking bridge, CSP, theme, permissions and lifecycle.
