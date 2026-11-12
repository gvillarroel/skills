---
name: chatgpt-desktop-plugin-ui
description: Creates, packages, and validates ChatGPT Desktop plugin interfaces using MCP Apps, desktop-only local MCP, and supported OpenAI UI extensions. Use for local-thread UI, forms, cards, file workflows, or deployment diagnosis, with separate local and remote acceptance.
---

# ChatGPT Desktop Plugin UI

Start with the pending human decision. Read
[micro-decisions.md](references/micro-decisions.md) for the default agent UI:
one bounded question, only decision-relevant evidence, and a typed result
returned to the agent. Use a full workspace only when the user requests it.

When authoring or refining presentation, follow
[craft-by-surface.md](references/craft-by-surface.md) for the actual
styling owner, supported mechanism, fallback and acceptance checks.

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

For coordinated investigations, dense matrices and reviewed actions, read
[complex-workspaces.md](references/complex-workspaces.md).

Identify a local Desktop thread versus a remote connection, the actual build,
and account/workspace controls. Read [host.md](references/host.md). Keep Codex,
ChatGPT web/mobile, and Desktop rendering claims scoped to their actual host.

1. Start with useful tools and a standard MCP App when the workflow needs UI.
   Use [mcp-apps.md](references/mcp-apps.md) for resource metadata, the bridge,
   direct actions, state, and browser checks.
2. Use [portable-packaging.md](references/portable-packaging.md) for a local
   package and fresh extracted-runtime verification. A desktop-only local
   stdio route and a remote HTTPS/tunnel connection have different gates.
3. Add optional OpenAI extensions only for the requested capability and feature
   detect each method. Keep a usable standard/text route when absent.
4. Apply [interaction-quality.md](references/interaction-quality.md), preserving
   native permissions, host theme, authored English copy, and owned palettes.
5. Verify package/server/bridge/browser behavior, then actual Desktop discovery,
   paint, direct tools, cancellation, state, and requested placement when the
   host and authorization are available.

Deliver executable sources, requested package or connection configuration,
exact output paths, test commands, and remaining host checks. Keep public
submission eligibility separate from local authoring. A setup screen or browser
fixture alone does not establish live ChatGPT component acceptance.

For sandbox integration tests, use [browser-validation.md](references/browser-validation.md).
