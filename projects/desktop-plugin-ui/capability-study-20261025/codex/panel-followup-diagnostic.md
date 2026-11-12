# Codex chart panel follow-up diagnostic

Date: October 25, 2026, America/New_York. This is a local source inspection,
not a new renderer, handshake, account or interaction test. The root reports
that the user selected Expanded, but the current MCP Apps controller lists no
side-panel tabs. A fresh `xy_render_chart` call returned text and structured
chart metadata to the model; no `_meta` object was visible in that model result.

## What the adapter actually declares

The inspected adapter source is
[server.ts](../../../reflex-xy-plugins/chatgpt/src/server.ts). It uses the
official MCP Apps SDK helpers, not a standalone HTML link as its UI contract:

- `registerAppTool` declares `xy_render_chart` with
  `_meta.ui.resourceUri: "ui://reflex-xy/chart-v4.html"` and model/app visibility.
- `registerAppResource` returns the matching resource with
  `text/html;profile=mcp-app`. Its metadata declares inline/fullscreen modes,
  no external connection/resource domains and `frameDomains: ["about:"]`.
- `chartResult` returns model-facing `content` and `structuredContent`, plus
  an app-private `_meta` object containing the render capability, original
  native HTML/SVG preview, editable specification and artifact origin.
- The app-only `xy_open_chart_app` has global/thread entrypoint metadata and
  the same resource URI. It is a host launcher contract, not a model-callable
  substitute or a guarantee that the host exposes a launcher.
- Recolor and artifact tools are app-only. Download uses an embedded resource
  through `app.downloadFile`; visiting capability-bearing loopback URLs is not
  the component's download path.

The matching source
[widget.ts](../../../reflex-xy-plugins/chatgpt/web/widget.ts) requires the
private metadata to initialize. Its update handler rejects a result missing
`artifact_origin`, `render_key` or native previews. Therefore a host that
delivered only the model-visible fields to the widget would produce a chart
result error. The model-visible fields alone cannot tell whether that occurred:
the host may correctly withhold app-private metadata from the model while
delivering it to the app.

Do not classify the source as missing UI registration or private result data
from the root's model-visible result shape. The active installed direct-MCP
server's launch configuration and exact binary identity were outside this
inspection. In particular, current project files are not proof that the same
build is the one serving the existing host connection.

## Expiry and the meaning of Expand

[core.ts](../../../reflex-xy-plugins/chatgpt/src/core.ts) sets a 20-minute
record TTL. Expiry makes record lookup/artifact access fail. The widget checks
expiry before downloads and the server checks capabilities for recolor and
artifact reads. Resource registration and resource reads have no render TTL
condition. Expiry can invalidate controls for an old chart; it does not, by
itself, explain why a side-panel inventory has zero tabs.

The component's **Expand** button calls
`app.requestDisplayMode({mode: "fullscreen"})`. It is shown only when the host
context advertises fullscreen. The browser controller's documented inventory
contains apps opened in side-panel tabs and excludes inline-only components.
A component fullscreen request and the host's open-in-side-panel operation
are separate actions. The user's Expanded reply does not identify which
operation took place. It remains a plausible distinction to check, not an
observation about what the user clicked.

The plot itself uses an embedded sandboxed `srcdoc` iframe, with original SVG
as a data-URL fallback. A nested frame can need its own browser-controller
approval and can limit screenshot support. Neither fact proves the outer app
is registered as a controller-visible tab.

## Supported next checks

1. Preserve the historical
   [installed-host record](../../../../evaluations/reflex-xy/native-desktop-20261025.md)
   separately: it establishes inline Codex-mode chart paint through direct MCP,
   while in-component controls and global/thread launchers remain untested.
2. Use the current, fresh chart. Have the user open the **host's side-panel
   view of that component**, rather than relying on the component's fullscreen
   request. Re-list tabs using the existing MCP Apps browser binding; do not
   create or navigate a substitute tab.
3. If a real app tab appears, bind its returned ID and inspect the outer DOM.
   Check whether it painted a chart or a clear bridge/metadata error before
   clicking controls. Access the nested chart only through supported frame
   locators and any required frame approval.
4. For a lower-layer diagnostic, a client to the named MCP server can use
   standard `tools/list` followed by `resources/read` for the exact declared
   URI. The project already has
   [a stdio contract fixture](../../../reflex-xy-plugins/tests/validate_local_app_stdio.ts)
   that checks resource MIME, packaged widget identity, CSP and app-only tool
   metadata. A separate client verifies only that exact connection, not the
   desktop frontend's resource fetch, bridge or pixels. Do not send `ui/*`
   initialization to the app-server endpoint.
5. If no tab is exposed after the actual side-panel operation, record the
   controller/host discovery gap. Avoid presenting an HTML export, manually
   opened loopback page or standalone browser as successful Codex integration.

No UI action, model inference, account/global configuration read, credential
access, HTTP artifact navigation or source modification was performed in this
diagnostic. The only new file is this English project note. No new claim of
current-host rendering or control acceptance is made.
