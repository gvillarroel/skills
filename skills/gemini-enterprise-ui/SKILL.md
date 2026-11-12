---
name: gemini-enterprise-ui
description: Creates and validates Gemini Enterprise agent interfaces with A2UI components over A2A, including catalog/version selection, action state, and administrator registration preparation. Use for Google Cloud Gemini Enterprise UI; Gemini CLI, Code Assist, consumer Gemini, and arbitrary MCP Apps need their own contracts.
---

# Gemini Enterprise UI

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

Target the Google Cloud Gemini Enterprise app. Confirm that product before
borrowing any integration from Gemini CLI, Code Assist, or consumer Gemini.
Read [a2ui.md](references/a2ui.md) for the documented A2UI/A2A route and the
host's supported versions/catalogs. Use [deployment.md](references/deployment.md)
only when preparing hosting, authentication, or registration.

1. Define the task, authoritative data, and direct action contract. Prefer
   host catalog components for ordinary forms, lists, tables, and dialogs.
2. Pin the version/catalog the host accepts. Start from
   [status-panel.json](assets/templates/status-panel.json) for a small v0.9
   stream; adapt it outside this read-only skill. Do not silently upgrade a
   host-bound payload to the newest upstream A2UI/A2A version.
   For a quantitative plot and exact values, adapt
   [chart-and-table.json](assets/templates/chart-and-table.json); retain the
   bound chart spec and object-shaped column definitions.
3. Implement the agent using the appropriate A2A SDK, an A2UI extension and
   version-compatible transport. Register supported catalogs in its agent
   card. Keep any plain-text response useful when UI is unavailable.
4. Handle control actions, cancellation, failed validation, and stale drafts
   on the server. A rendered button does not prove backend action handling.
5. Apply [interaction-quality.md](references/interaction-quality.md). Preserve
   host-rendered catalog styling; exact palettes apply only to authored paint
   actually exposed by the chosen component or documented iframe.
6. Run `python <bundle>/scripts/check_a2ui.py <messages.json>` for bounded
   message integrity, then the matching official envelope/catalog validation,
   A2A streaming/action tests, and real Gemini Enterprise paint when available.
   The bundled checker explicitly does not validate full catalog schemas.

Deliver requested streams, agent source/configuration, tests and exact paths.
Prepare deployable artifacts before any separately authorized cloud change.
Document hosting/admin prerequisites and real-host checks that remain untested.
Never claim cloud registration or production UI from a local JSON check.
