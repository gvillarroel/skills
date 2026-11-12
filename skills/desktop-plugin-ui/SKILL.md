---
name: desktop-plugin-ui
description: Compares assistant plugin UI mechanisms and plan interfaces spanning Claude Desktop, Claude Code, Pi, Codex, ChatGPT Desktop, Gemini Enterprise, or Copilot. Use for cross-host surface selection, compatibility studies, and shared-domain adapter blueprints; prefer a dedicated host skill for a single-host implementation.
---

# Assistant Plugin UI Comparison

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

Use this skill for cross-host choices and multi-host blueprints. For a single
known host, prefer the matching dedicated skill when available. Each dedicated
bundle is independently usable; none requires this comparison bundle.

| Target | Optional dedicated skill | Correct mechanism |
| --- | --- | --- |
| Claude Desktop ordinary Chat | `desktop-chat-plugin-ui` | Connected MCP server, MCP Apps iframe, optional MCPB installer. |
| Claude Code terminal / Desktop Code / Claude VS Code | `code-native-plugin-ui` | Native command, Mod tree, and frontend-specific controls. |
| Pi Coding Agent | `pi-extension-ui` | TypeScript commands, native dialogs, widgets, mode-aware TUI/RPC. |
| Codex CLI / desktop / app-server / IDE | `codex-plugin-ui` | Executing-loader-specific plugins, MCP, negotiated forms, frontend rendering. |
| ChatGPT Desktop | `chatgpt-desktop-plugin-ui` | Local-thread desktop-only plugin or remote MCP Apps connection. |
| Google Cloud Gemini Enterprise | `gemini-enterprise-ui` | Host-supported A2UI catalogs over A2A, hosted agent, admin registration. |
| GitHub Copilot | This comparison skill | Select the actual CLI extension or VS Code webview/MCP App route. |

## Compare only the relevant surfaces

Read [assistant-surface-matrix.md](references/assistant-surface-matrix.md) first.
Use explicit product/session context; a model/provider name does not identify
the harness or renderer. Keep Desktop Chat and Code, local/remote execution,
terminal/RPC/JSON, stock host and owned frontend as separate surfaces.

When a dedicated skill is unavailable, this bundle remains self-contained:
read only the matching historical host reference from the matrix and recheck
current primary sources. The retained authoring references, helpers, palettes,
and templates support compatibility and historical reproducibility. Do not
load all host catalogs for a small comparison. Gemini's compact route is
contained directly in the matrix and linked official documentation.

For shared architecture, read [efficient-delivery.md](references/efficient-delivery.md).
Define domain data, actions, authority, draft/commit transitions, and recovery
once. Give each requested host a short adapter record: mechanism, package,
transport, capabilities, fallback, required setup, and validation. Keep a useful
text route. Add inference, services, and frameworks only for requirements that
need them. An ordinary blueprint need not become a formal capability study.

For a plan-only request, produce the requested plan/review artifacts and check
their structure. Do not build unrequested prototypes, test projects or service
inventories merely to justify a proposed route. Name future validation as a
plan; do not report it as completed evidence. Use the compact rich-interface
reference for renderer choices and consult further host detail only when needed.

## Optional historical detail

Read only the reference needed for the comparison: [chat layouts](references/chat-patterns.md),
[bridge](references/bridge-patterns.md), [sandbox validation](references/browser-validation.md),
[current offerings](references/capability-offerings.md), [Claude Chat evidence](references/claude-chat-live.md),
[Claude native limits](references/claude-host-limits.md), [ChatGPT](references/chatgpt-limits.md),
[Codex](references/codex-limits.md), [Copilot](references/copilot-limits.md),
[distribution](references/distribution.md), [elicitation](references/host-prompts.md),
[native patterns](references/native-patterns.md), [native starter](references/native-authoring.md),
[Pi modes](references/pi-extensions.md), [Pi authority](references/pi-stateful-actions.md),
[historical authoring](references/plugin-authoring.md), [portable packages](references/portable-packaging.md),
[composition](references/ui-composition.md), [visual review](references/visual-review.md),
and [probe methodology](references/evidence-and-probing.md).

## Preserve evidence and interaction quality

Use [interaction-quality.md](references/interaction-quality.md) and
[usability-and-color.md](references/usability-and-color.md) for concrete H1-H10
checks, English authored copy, colorset1 by default, explicitly selected
colorset2, real contrast, and styling-owner boundaries. Preserve native host
themes and catalog paint; authored iframe styling remains separate.

Keep `documented`, `observed-working`, `observed-failed`, `conditional`,
`untested`, and `unsupported` scoped to the named host, build, surface, and
layer. A missing check is untested. A model response, returned HTML, valid
package, native engine, or browser fixture is not proof of signed-in host
painting. Keep inherited observations separate from the current task.

For a formal evidence study, use [report-authoring.md](references/report-authoring.md)
and the bundled typed evidence/source/report helpers. For ordinary plans, use
the requested schema directly. Do not add a second ledger merely to describe
build tests. Lead with a recommended route and its reasons; give concrete
validation actions and remaining host checks without universal support claims.
