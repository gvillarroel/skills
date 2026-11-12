# Surface-specific craft implementation

The Impeccable-informed decision, hierarchy, color and typography guidance is
implemented in eight independent skill bundles. Each `SKILL.md` routes
presentation work to its own compact `references/craft-by-surface.md`. The
comparison router selects a mechanism; individual host bundles implement only
what the actual surface owns. Read the [source review](plugin-ui-impeccable-review.md)
and [micro-decision pattern](plugin-ui-micro-decisions.md) for the shared intent.

## Implementation map

| Skill | Applied mechanism | Boundary and fallback |
| --- | --- | --- |
| `desktop-plugin-ui` | A per-surface ownership matrix and adapter/completion contract. | Plan-only work stays a plan; no extra prototype or application context system. |
| `desktop-chat-plugin-ui` | Owned MCP App HTML, relative type roles, scoped CSS, semantic emphasis, keyboard focus and explicit actions. | Claude Chat chrome stays host-owned; direct chat remains usable when the App cannot return the answer. |
| `code-native-plugin-ui` | Supported native Box/Text/Select/Button constructors, meaningful grouping and authentic command/mount events. | No browser CSS or invented DOM props in Mods; terminal text trees and separate frontend paint checks. |
| `pi-extension-ui` | Native theme roles, ANSI-aware column sizing, bounded tree/evidence view and typed completion. | TUI, RPC dialogs and print/JSON use distinct presentation contracts; deferral remains neutral. |
| `codex-plugin-ui` | CLI/form, actual MCP App, owned app-server client and integrated-browser routes are selected separately. | Loader/tool discovery cannot establish a canvas; host controls, approval policy and surrounding chrome are preserved. |
| `chatgpt-desktop-plugin-ui` | Standard App resource styling and feature-detected optional extensions. | Actual Desktop local/remote placement and host-message capability need independent acceptance. |
| `gemini-enterprise-ui` | Pinned A2UI catalog text/layout/action fields, A2A result handling and supported chart grammar. | No arbitrary CSS/JavaScript or guessed properties; use equivalent catalog text/list/table when a graph is unavailable. |
| `reflex-xy` | Public chart API/connected schema for marks, axes, theme and legends; separate owned wrapper styling. | Preserve values, scales, gaps and category identities. Primary red may encode data. Static exports and snapshots do not gain live callbacks. |

## Reusable decision rules

Apply the presentation pass when authoring or refining UI. Keep a requested
chart/export independent of a human-choice flow unless the task asks for one.
When the agent needs judgment, preserve one question, relevant alternatives
and a selected/deferred result through every representation fallback.

Web reading uses browser-relative type and measured diagram labels; native
surfaces use their own roles and controls; catalog surfaces use schema-defined
properties. Color for data is separate from action/status semantics: visual
polish must not recolor a category, reverse a ramp, alter a domain or invent
missing observations. Group by meaning and keep the primary action contextual.

Validate the layer that owns the result. Browser screenshots measure owned
HTML; native process captures measure terminal cells; constructor tests measure
native engine behavior; schema checks measure catalog validity. Actual host
paint, accessibility, continuation and deployment remain separately scoped.

The [evaluation report](../evaluations/desktop-plugin-ui/surface-craft-20261112.md)
records strict skill-only contracts, checker results and available renderer
evidence. No native App, account, cloud setting or personal plugin configuration
is modified by adopting these instructions.
