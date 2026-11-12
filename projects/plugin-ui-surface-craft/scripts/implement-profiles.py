#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Implement presentation guidance at the styling authority of each UI surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROFILES = {
    "desktop-plugin-ui": """# Select the craft mechanism by surface

Use this profile when a comparison or adapter plan includes presentation.
Keep one domain decision and identify the actual renderer and styling owner.
Do not add prototypes or new application context files to a plan-only request.

| Surface | Apply directly | Preserve or replace |
| --- | --- | --- |
| Owned HTML / MCP App resource | Relative type roles, scoped CSS, spacing, computed contrast, local graphs and focus. | Preserve the surrounding host chrome. Use a readable equivalent when diagram labels cannot fit. |
| Claude Code native controls | Supported native layout, text, selection and button constructors. | Preserve host fonts/theme; use a text tree when a requested frontend cannot paint the graphic. |
| Pi TUI | Theme roles, weight, column-aware spacing and complete choice/evidence/return states. | Use native RPC dialogs or explicit text arguments outside TUI; no browser CSS. |
| Codex CLI / negotiated form | Useful text and the actually negotiated control schema. | A loader or tool result does not establish a graphical canvas. |
| Owned app-server frontend | The client-owned layout and event/completion lifecycle. | Name that client separately from stock Codex Desktop or IDE paint. |
| Gemini Enterprise A2UI | Accepted catalog components, supported style fields and typed A2A actions. | Preserve catalog paint; use an offered list/table/tree instead of inventing CSS or JavaScript. |
| XY chart embedded in a host | Public chart marks/components/theme and supported wrapper controls. | Preserve quantitative geometry and stable series/category color meanings. |

## Implementation contract

For each requested adapter, name its surface, presentation owner, supported
controls/roles, one primary action, typed result and continuation mechanism.
Separate subject/data emphasis from selection, action and status. Keep the
same decision and evidence when replacing a graphical representation.

For owned HTML, start reading text at the browser base size, use measured dense
chart labels and preserve user scaling. For native/catalog surfaces, use their
supported text/layout roles rather than copying CSS values. The chart's data
palette remains a semantic encoding; an action-color heuristic cannot recolor
categories or alter a numeric scale.

## Acceptance

Review the decision and hierarchy before mechanical findings. Then verify the
actual layer: browser pixels and keyboard for owned HTML, native process and
terminal cells for TUI, constructors/events and separate frontend paint for
native panes, or schema/transport and separate registered-host paint for A2UI.
Report unavailable checks as untested. Keep static, interactive, future-context
and agent-continuation claims separate. Do not manufacture optional support.
""",
    "desktop-chat-plugin-ui": """# Craft inside the Claude Chat MCP App

Apply these instructions to the HTML resource owned by the connector. Ordinary
Claude Chat's surrounding controls, fonts, permissions and chrome belong to the
host. Desktop Code is a different native surface.

## Implement in the resource

1. Bind one question, offered option IDs, relevant evidence and selected/deferred
   result. Use native HTML controls and explicit app actions. Keep extra
   navigation, permanent export controls and debug metadata out of the choice.
2. Use scoped CSS and the documented host theme/context when available. Start
   ordinary reading at `1rem`; define a few type/spacing roles. Measure graph
   labels at the rendered width and switch to an equivalent text tree when
   user text scaling makes them unreadable. Preserve the decision and IDs.
3. Give subject emphasis, active selection, primary action and status distinct
   roles. Keep the confirmed palette; pair color with text/shape. An ordinary
   disputed concept need not use an error-colored fill.
4. Keep button copy tied to the selected object. Show keyboard focus with
   `:focus-visible`; pointer selection should not add a second focus frame.
   Preserve readable disabled and pending states without adding another step.

```css
/* Inside the owned App document, never injected into host chrome. */
:root { font-size: 100%; line-height: 1.5; }
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

## Complete the interaction

Register the App callbacks before connecting. Keep server actions unavailable
until the bridge and required server-tool capability are ready. Rehydrate the
authoritative receipt and use `app.callServerTool` for the explicit answer.
Context update alone supplies a future turn; use the advertised text-message
capability for at most one user-initiated continuation and check acknowledgement.
Retain a direct chat fallback when the host cannot deliver the answer.

## Verify

Run real MCP resource/tool checks, the actual SDK bridge in a restrictive iframe,
and narrow/wide keyboard and text-scaling checks. Inspect enabled, disabled,
selected, deferred, failed and restored states. Actual signed-in Claude Chat
paint and continuation require their own observation. Source CSS, an extracted
package and a browser preview establish their respective layers only.
""",
    "code-native-plugin-ui": """# Craft with native Claude Code controls

Identify terminal, Desktop Code or VS Code first. The native runtime owns fonts,
control styling and accessibility behavior. Apply hierarchy through supported
constructors and layout; do not copy an HTML/CSS theme into a Mod.

## Implement with supported primitives

1. Reduce the interaction to the pending question, meaningful alternatives,
   decision evidence and a typed selected/deferred result. Keep ordinary task
   text available if pane placement is denied.
2. Use the bundled native starter's `Box({flexDirection, children})`,
   `Text({children})`, `Select({key, options, value, onSelect})` and
   `Button({key, children, onPress})` contracts. Use only additional properties
   verified for the executing runtime. Browser `className`, CSS `rem`, DOM
   focus selectors and invented `onChange` fields are not native style APIs.
3. Give the question and candidate labels a consistent native hierarchy.
   Use spacing/grouping supported by the host before adding decorative frames.
   Preserve semantic native themes instead of assigning raw RGB escapes.
4. Keep a relationship as an aligned text tree in a terminal. For a frontend
   with verified graphical primitives, use only that frontend's supported
   graphic contract and retain equivalent text. A valid constructor in one
   surface does not establish paint in another.
5. Keep control keys, mount surface and request ID stable. A selection change
   may clarify the primary action label but must not retarget an already frozen
   write. Return through the real native completion/event route.

## Verify at the right layer

Use strict plugin validation and authentic `command.run` events in the native
test engine. Exercise invalid input, unplaced/denied pane, selection, close,
reopen and unrelated-pane pass-through. Then inspect actual terminal/Desktop
Code/VS Code paint, focus, long text and theme behavior for every claimed
surface. A native engine pass cannot establish physical font size or contrast.
Keep login, account and placement gates distinct from rendering defects.
""",
    "pi-extension-ui": """# Craft for Pi TUI, RPC and print

Select the actual Pi mode before presentation. Prefer native `ctx.ui.select`
for a simple choice; a custom TUI is justified when comparative tree structure
helps the same decision. RPC dialogs and print output have their own contracts.

## TUI implementation

1. Guard terminal components with `ctx.mode === "tui"`. Use the bundled
   `micro-choice.ts` as the formatted, self-contained starting point.
2. Use `theme.fg` semantic roles: `accent` for active choice, `warning` when
   uncertainty needs attention, `success` for an acknowledged selected answer,
   `error` for a failed action and `muted`/`dim` for context. Keep deferral
   neutral. Pair roles with words, circles/checks and weight. Preserve the
   user's theme; do not paste browser colors or RGB escape sequences into it.
3. Measure terminal columns with host width utilities such as `truncateToWidth`,
   which account for ANSI and wide characters. Reserve actual host rows and
   keep both alternatives and decision keys reachable in a short terminal.
   Browser `rem`, CSS grids and pixel contrast scans do not style terminal cells.
4. Use bounded whitespace and aligned tree connectors. The evidence disclosure
   returns to the same pending question. Escape there closes evidence; Escape
   at the choice returns deferral, never a default parent.
5. Resolve `ctx.ui.custom` with `done(optionId)` or an explicit no-choice result.
   A native demonstration can put typed details into model-visible history
   with `triggerTurn:false`; do not call that a resumed model turn.

## Other modes

When `ctx.hasUI` is true in RPC, use native selection requests and matching
response IDs. A custom terminal factory does not paint in an RPC client.
For JSON/print accept explicit option IDs and return useful text/structured
results; do not request an invisible dialog. Preserve invalid-input recovery.

## Verify

Use the bundled RPC checker for actual discovery/request/response contracts and
inspect returned choice or deferral independently. Capture the real TUI at
80x32 and 60x16 cells, including evidence, selection, completed result and
neutral deferral. Inspect actual theme roles and ANSI-aware geometry; a version
probe, JSON transcript or HTML terminal mock alone does not prove native paint.
""",
    "codex-plugin-ui": """# Craft for the executing Codex surface

Choose CLI, stock Desktop/IDE, an actual MCP App renderer, or an owned
app-server frontend. Plugin installation and MCP discovery are separate from
the frontend's presentation authority.

## Apply only where the surface permits

| Surface | Implementation |
| --- | --- |
| CLI text or negotiated elicitation | Concise question/options and supported form fields. Preserve host theme, policy and text fallback. Do not treat a tool's HTML as a painted component. |
| Actual MCP App renderer | Scoped resource CSS, browser-relative type, supported native HTML controls, measured graphs and equivalent text. Preserve surrounding host chrome. |
| Owned app-server client | Implement the client-owned type/spacing/color roles plus events, request IDs, pending state, recovery and typed completion. Name that client in the result. |
| Integrated browser preview | Verify the owned page and actual allocated width; keep that observation separate from inline conversation paint. |

## Owned presentation recipe

Keep the decision, options and evidence relevant to one answer. Separate data
or subject emphasis from action/selection/status; retain exact palette meanings.
Use a few semantic type/spacing roles, browser-base reading size and visible
keyboard focus in HTML. Switch a cramped graphic to equivalent text instead of
shrinking labels. Use host-supported text/style roles in native controls.
Do not import a web detector, CSS or arbitrary font into a terminal/form schema.

For an MCP App, wait for the bridge and server-tool capability before enabling
actions. Record the selected/deferred result through the real tool. An update
to model context is future context; an explicit continuation needs advertised
text-message capability and an acknowledged single request. Keep a chat/text
route when that capability is absent.

## Verify

First test the executing loader in a task-local catalog/home, exact cache bytes,
actual server discovery and a direct tool call. Test UI separately in the
frontend that owns it, including keyboard, type scaling, allocated width and
failure recovery. Never infer stock Desktop/IDE paint from an app-server
callback, manifest, owned browser screenshot or optional display-mode request.
""",
    "chatgpt-desktop-plugin-ui": """# Craft inside the ChatGPT Desktop component

Identify the actual Desktop thread, local or remote loader, build and advertised
capabilities. The MCP App resource owns its document; host chrome, permissions,
composer, native dialogs and optional extension surfaces remain host-owned.

## Implement in owned HTML

1. Present one question with comparable alternatives and relevant evidence.
   Prefer native HTML controls and an explicit app action. Keep API options,
   engine details and unrelated navigation out of the first view.
2. Use scoped CSS with documented host theme/context when supplied. Start
   reading text at the browser base size; keep a small role scale for question,
   option, evidence and metadata. Measure dense diagram labels and preserve
   text scaling through an equivalent text/tree representation when needed.
3. Separate subject/data emphasis from selection, action and status. Preserve
   confirmed palettes and semantic data categories. Use the selected object's
   name in the primary action when helpful. Maintain readable disabled/pending
   states, keyboard `:focus-visible` and useful hit areas.
4. Apply optional `window.openai` capabilities only when the actual host
   exposes the required method. Their availability does not grant DOM/CSS
   access to host dialogs, sidebar, composer or native controls.

## Complete through the host contract

Wait for App connection and required server-tool capability before enabling
the answer. Use `app.callServerTool`, validate the real receipt and restore it
on reopen. Future model-context updates and actual continuation are different:
feature-detect text messaging, send at most one explicit continuation and inspect
its acknowledgement. Preserve a direct chat fallback for missing capabilities
or an unknown delivery result. Use explicit app actions rather than depending
on ambient form submission or expanding sandbox permissions.

## Verify

Validate package, tool/resource metadata, actual SDK bridge, restrictive iframe,
and browser keyboard/type-scaling/contrast states. Then observe actual Desktop
discovery, component placement and interaction for the selected local/remote
route. Codex mode, a standalone integrated-browser page and another host's
working App do not establish stock ChatGPT Desktop paint or optional API support.
""",
    "gemini-enterprise-ui": """# Craft through the Gemini Enterprise catalog

Pin the A2UI wire version and the exact catalog accepted by the registered
Gemini Enterprise host. A2A carries the interaction. The host owns component
paint; an arbitrary CSS property or JavaScript object is not a catalog control.

## Implement with catalog authority

1. Reduce the content to the pending question, offered option IDs, relevant
   evidence and selected/deferred result. Keep question/surface/component IDs
   stable across data-model updates and compare question revision on the server.
2. Use catalog text/layout/selection/action components actually present in the
   chosen schema. Prefer grouping, ordering and concise copy for hierarchy.
   Set a text variant, spacing or emphasis property only if the selected
   component schema defines it; otherwise preserve the host's defaults.
3. Do not copy HTML `className`, CSS `rem`, `:focus-visible`, `onChange` or a
   native terminal theme token into component JSON. The bundled read-only
   status starter demonstrates `MaterialColumn` and `MaterialText`, not an
   invented selector/action contract.
4. Use `VegaChart` and `MaterialTable` only with their documented catalog and
   bound chart grammar, as the chart/table starter does. Apply an exact data
   palette only inside authored paint exposed by that grammar. Preserve axes,
   scales, units, missing observations and category identities.
5. If a graph or disclosure primitive is absent, keep the same alternatives
   and evidence in supported text/list/table controls. For example, express
   parent and relevant sibling alongside each option rather than importing a
   D3 canvas or arbitrary iframe. A plain-text answer remains useful.
6. Map the supported action event to the typed agent result through A2A/data-
   model handling. A rendered button does not establish dispatch or completion.
   Do not use MCP App messaging as a substitute for the registered agent action.

## Verify

Run the bundled v0.9 integrity checker, then the actual pinned envelope/catalog
and chart-grammar validators. Check that every styling/control property belongs
to that catalog and that all references resolve. Exercise A2A action/state
transport separately. Finally capture the registered Gemini Enterprise agent
for font scaling, contrast, keyboard, selected/disabled/error and return states.
A local stream/renderer cannot establish host theme or actual deployment paint.
""",
    "reflex-xy": """# Craft for an XY chart and its surrounding UI

Use this profile for an embedded chart, notebook widget or requested interactive
HTML. A requested plot/export can stand on its own. Add an agent decision flow
only when the task actually asks a person to choose; keep its evidence and
typed result local to that question.

## Separate chart and wrapper authority

| Layer | Apply through | Preserve |
| --- | --- | --- |
| XY marks, axes, labels, legends and theme | The installed public XY API or connected adapter's supported schema. | Source values, units, domains, missing-value gaps, series/category identity and the exact selected colorset. |
| Owned HTML wrapper | Scoped relative type/spacing roles, native controls, explicit disclosure and keyboard focus. | Host chrome and the downloaded native chart/source unless the requested output itself changes. |
| Notebook / Reflex | The actual widget/framework state and supported events. | The difference between a live Python connection and an interactive fixed-data snapshot. |
| PNG/SVG export | Renderer-supported geometry, labels and paint. | Static output has no live browser controls or backend callbacks. |

## Implement the useful part of the craft pass

1. State the question answered by the chart. Show only marks, annotations and
   controls needed for that question or requested output; put additional formats
   and display tools behind a named disclosure when useful.
2. Use supported XY components/theme for chart text and layout. Do not translate
   CSS, arbitrary HTML props or native terminal tokens into Python kwargs or
   the connected JSON adapter. Verify unfamiliar signatures against the pinned
   runtime. The connected adapter uses versioned `kind` fields.
3. Preserve quantitative geometry and use the same categorical mapping in marks,
   legend and filtered views. The primary red is a valid semantic data color in
   colorset1. A rule about reserving a button accent must not recolor a category,
   reverse a ramp or turn normal observations into warning states.
4. Distinguish current selection with supported outline/shape/label or separate
   wrapper state. Keep thresholds and comparison identities explicit; do not
   change source measurements, scales or missing-value gaps for visual polish.
5. Start ordinary wrapper reading at browser-base size. Measure chart labels in
   the actual canvas/export at intended display size; use exact values or an
   equivalent chart/table when the view cannot remain readable. Moving a legend
   into verified empty space must not hide a high endpoint.

## Verify

Execute the declared Python or connected spec checker, render through the actual
engine and inspect native exports and interactive HTML separately. Exercise the
requested pan/hover/selection and narrow wrapper focus/disclosure where present.
Preserve the last valid chart after a failed regeneration. Live server actions
require an actual live connection; returning HTML or changing wrapper state does
not prove a backend update or agent continuation. A clean visual-rule scan cannot
certify data semantics or an embedded host's paint.

This is an independent adaptation of Impeccable's role/hierarchy/polish ideas to
XY's own API, palette and export contracts; no upstream package is required.
""",
}

def main():
    for name, text in PROFILES.items():
        skill = ROOT / "skills" / name
        (skill / "references/craft-by-surface.md").write_text(text, encoding="utf-8", newline="\n")
        entry = skill / "SKILL.md"
        content = entry.read_text(encoding="utf-8")
        link = ("When authoring or refining presentation, follow\n"
                "[craft-by-surface.md](references/craft-by-surface.md) for the actual\n"
                "styling owner, supported mechanism, fallback and acceptance checks.\n\n")
        if "[craft-by-surface.md]" not in content:
            if name == "reflex-xy":
                marker = "When embedding a chart in a chat component or small application panel, read\n"
            else:
                marker = "For graphs, charts, dense tables, or linked multi-panel interfaces, read\n"
            if marker not in content:
                raise ValueError(f"Missing presentation route in {name}")
            content = content.replace(marker, link + marker)
            entry.write_text(content, encoding="utf-8", newline="\n")
        if name != "reflex-xy":
            reference = skill / "references/micro-decisions.md"
            content = reference.read_text(encoding="utf-8")
            anchor = "## Host adapter\n\n"
            route = ("Use [craft-by-surface.md](craft-by-surface.md) to implement these\n"
                     "criteria with this host's actual controls and styling authority.\n\n")
            if route not in content:
                reference.write_text(content.replace(anchor, anchor + route), encoding="utf-8", newline="\n")
    interaction = ROOT / "skills/reflex-xy/references/interaction-design.md"
    content = interaction.read_text(encoding="utf-8")
    marker = "## First view\n"
    addition = ("For an agent decision, make the primary action return that choice; save/export\n"
                "can stay secondary. A requested chart or export does not require a human\n"
                "decision flow. Follow [craft-by-surface.md](craft-by-surface.md) for chart versus\n"
                "wrapper styling: primary red may encode data, and visual polish must preserve\n"
                "category mappings, values, scales and missing observations.\n\n")
    if addition not in content:
        interaction.write_text(content.replace(marker, addition + marker), encoding="utf-8", newline="\n")
    print(f"Implemented surface-specific craft guidance in {len(PROFILES)} independent skill bundles.")

if __name__ == "__main__":
    main()
