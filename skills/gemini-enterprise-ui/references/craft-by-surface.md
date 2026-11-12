# Craft through the Gemini Enterprise catalog

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
