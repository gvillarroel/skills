# Craft inside the ChatGPT Desktop component

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
