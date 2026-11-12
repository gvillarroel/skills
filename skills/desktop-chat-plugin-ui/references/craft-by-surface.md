# Craft inside the Claude Chat MCP App

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
