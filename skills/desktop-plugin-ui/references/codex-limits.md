# Codex surface limits and empirical recipes

## Contents

[Measured boundaries](#measured-boundaries), [tool fallback](#codex-ui-tool-fallback),
[resource boundary](#codex-ui-resource-boundary), [elicitation](#codex-ui-elicitation-policy),
[form negotiation](#codex-ui-form-negotiation), [images](#codex-ui-image-channel),
[custom client](#codex-ui-owned-client).

Snapshot: 2026-10-24; Windows 11, npm `codex-cli 0.145.0`.
Distinguish CLI, app-server, Codex desktop, IDE extension, and ChatGPT.
Backend success does not establish a rendered frontend control.

For executable package authoring, use
[portable-packaging.md](portable-packaging.md). A fresh identical-package probe
passed catalog/install on both 0.145.0 and 0.164.0-alpha.11.1, but only the latter
exposed the plugin's MCP tools in the tested ephemeral app-server thread.
Keep this bounded loader split separate from a direct MCP or paint result.

For the October 25 desktop-bundled 0.164.0-alpha.11.1 study and current feature
choices, read [capability-offerings.md](capability-offerings.md). The original
0.145.0 results below remain dated observations, not limits on every newer
desktop/IDE client. In particular, the old executing-connection attribution
for extended forms is corrected by fresh PID-bound evidence below.

The [plugin UI guide](https://developers.openai.com/plugins/build/chatgpt-ui)
describes ChatGPT's iframe and requires useful tools without UI. The
[extensions guide](https://developers.openai.com/plugins/build/extensions)
describes ChatGPT sidebar, composer, file-viewer, and form surfaces. Neither
establishes them in the Codex CLI. Shared directory access is not UI evidence.

## Measured boundaries

| Feature | Installed runtime observation | Limit or next check |
| --- | --- | --- |
| Tool text and structured data | App-server direct calls and one actual `codex exec --json` model turn preserved the synthetic result. | JSON output is data, not a painted card. |
| Tool `_meta.ui.resourceUri` | Present in tool inventory; result `_meta` also appeared in CLI JSON events. | Metadata preservation does not prove UI discovery or rendering; `_meta` is not secret storage. |
| HTML UI resource | `mcpServer/resource/read` returned the exact registered `text/html;profile=mcp-app` document. | Resource bytes alone do not execute JavaScript or create an iframe. |
| MCP Apps handshake | MCP client advertised form/URL elicitation but no `io.modelcontextprotocol/ui` extension; sending `ui/initialize` to app-server returned `-32600`. | App-server JSON-RPC is not the iframe `postMessage` bridge. A separate frontend may implement a renderer. |
| PNG tool content | Direct call preserved image MIME and base64 content. | No terminal pixel rendering or model visual interpretation was established. |
| Standard form and URL elicitation | With `approvalPolicy:"on-request"`, app-server sent host callbacks; synthetic form acceptance and URL decline returned to the server. | The client owns presentation. The probe did not open a browser or complete authentication. |
| Elicitation with `never` | All tested form/URL requests automatically declined, with no host callback. Noninteractive `codex exec --json` also declined the form. | Handle decline as a normal outcome; do not wait forever for a user panel. |
| `openai/form` | A basic flat schema was delivered as ordinary `form`; arbitrary nested-object schema returned MCP `-32601` in the tested thread connection. | Do not infer rich-control support from basic form normalization. Check the exact connection and schema. |
| Extended-form capability | Fresh PID-bound probes on 0.145.0 and 0.164.0-alpha.11.1 show the process serving direct tools advertises `openai/form` when opted in; an idle connection can omit it. | The earlier log-order inference that the executing connection lacked it is withdrawn. Negotiate and identify the actual serving process; nested-schema refusal alone does not diagnose a missing extension. |
| Model availability | `gpt-6-luna` was rejected by this CLI/ChatGPT account; bundled `gpt-5.6-luna` completed the synthetic tool sequence. | An installed or bundled model name is not an entitlement test. Failure does not diagnose a UI renderer. |

Three policy/opt-in protocol cases passed 18 assertions each with zero model
calls. One real CLI turn completed the card/form sequence. Ambient skills
inflated input despite `--ignore-user-config` and disabled project documents;
that switch is not full context isolation. These backend tests do not verify
desktop/IDE paint, terminal pixels, or rich form controls.

## codex-ui-tool-fallback

- **Trigger/input:** A plugin must work in Codex CLI, desktop, and ChatGPT;
  provide a tool schema, concise text, authoritative structured data, and an
  optional UI resource.
- **Rule:** Make the action complete from tool calls and text. Attach the
  optional component only to a render tool when that surface supports it.
  Keep business state on the server. Treat metadata as trace-visible.
- **Failure/fallback:** A client may return the data while never loading UI.
  Preserve IDs and readable status so the model can finish the same task.
- **Validate:** Call once through the real host and inspect tool completion,
  result data, visible frontend, and fallback separately.
- **Evidence:** `observed-working` result transport and actual CLI fallback;
  `untested` Codex desktop widget paint. [Official UI guide](https://developers.openai.com/plugins/build/chatgpt-ui).

## codex-ui-resource-boundary

- **Trigger/input:** A tool has `_meta.ui.resourceUri` and a registered HTML
  resource with the MCP Apps MIME type.
- **Rule:** Verify tool discovery, resource read, then the frontend's actual
  initialization and paint. Route app-server methods over its connection;
  route MCP Apps `ui/*` over the supported iframe-host bridge.
- **Failure/fallback:** Do not send `ui/initialize` to the Codex app-server and
  expect a webview. Do not count a successful resource read as JavaScript
  execution, fullscreen, a modal, or a sidebar app.
- **Validate:** Put different markers in text, resource HTML, and a JS event.
  Confirm which markers the actual frontend produces. Keep data fallback.
- **Evidence:** `observed-working` metadata/resource transport;
  `observed-failed` app-server `ui/initialize`; frontend UI `untested`.
  [App-server contract](https://learn.chatgpt.com/docs/app-server).

## codex-ui-elicitation-policy

- **Trigger/input:** An MCP tool needs a bounded enum/boolean form or URL-flow
  confirmation, with synthetic inputs and an explicit approval policy.
- **Rule:** Implement accept, decline, and cancel. A custom app-server client
  must handle `mcpServer/elicitation/request` and return the matching request
  ID with `{action, content}`. Do not assume `turnId` is non-null.
- **Failure/fallback:** `never` policy and headless clients can decline without
  presenting a form. A URL confirmation does not prove navigation, identity,
  OAuth completion, or a permission grant.
- **Validate:** Compare `on-request` and `never` using the same server. Observe
  both the server request and final MCP response, without a model turn when
  direct app-server calls suffice.
- **Evidence:** `observed-working` synthetic enum/boolean response and URL
  decline through a real app-server, including expected automatic decline
  under `never`. No visual presentation check ran there; form paint is
  `untested`, not an observed failure.
  [Official elicitation contract](https://learn.chatgpt.com/docs/app-server#mcp-server-elicitation-requests).

## codex-ui-form-negotiation

- **Trigger/input:** Richer host-native forms are requested beyond the standard
  MCP form schema.
- **Rule:** Negotiate `mcpServerOpenaiFormElicitation` during app-server
  initialization, inspect downstream MCP capabilities, and use a documented
  schema for that exact connection. Keep a valid standard-form alternative.
- **Failure/fallback:** A flat request labeled `openai/form` can normalize to
  ordinary `form`. The label, a schema accepting arbitrary JSON, or an
  app-scoped capability does not establish thumbnail selectors, nested groups,
  or the thread connection's support. Reject or simplify unsupported schema.
- **Validate:** Exercise one documented rich control and one deliberately
  unsupported schema; log negotiated capabilities and the actual callback
  mode plus serving-process identity. A basic enum test alone is insufficient.
- **Evidence:** `observed-working` basic normalization; `observed-failed`
  arbitrary nested schema (-32601 on 0.145.0; -32602 on 0.164.0-alpha.11.1);
  fresh serving-process opt-in is `observed-working`, while actual rich-control
  paint remains `untested`. Do not reuse the withdrawn missing-extension claim.
  [Extended forms](https://developers.openai.com/plugins/build/extensions),
  [capability opt-in](https://learn.chatgpt.com/docs/app-server#mcp-server-elicitation-requests).

## codex-ui-image-channel

- **Trigger/input:** A plugin returns a raster preview or the user supplies an
  image to a coding task.
- **Rule:** Distinguish model image input, MCP image result transport, a
  downloadable artifact, and a frontend's image viewer. Use actual MIME and
  bytes plus a readable label; keep interactive controls in a supported UI.
- **Failure/fallback:** An image is not an interactive canvas. A base64 result
  does not establish terminal image display. An image argument does not prove
  output-side image rendering or support for arbitrary HTML/SVG execution.
- **Validate:** Verify bytes, then test visual display and interaction in the
  named frontend independently. Use a small synthetic colored image for a
  genuine visual test, rather than the one-pixel transport fixture.
- **Evidence:** `observed-working` PNG transport; visual interpretation and
  display `untested`. CLI image input is `documented` in the
  [command reference](https://learn.chatgpt.com/docs/cli/reference).

## codex-ui-owned-client

- **Trigger/input:** A product needs a bespoke dashboard around a Codex agent;
  the developer owns the frontend and app-server lifecycle.
- **Rule:** Build the UI in that application, initialize app-server, create a
  thread, stream turn/item events, and implement approvals and elicitation.
  Negotiate experimental fields and generate schemas from the installed
  binary before depending on them.
- **Failure/fallback:** Owning a client does not inject arbitrary native panes
  into the stock Codex desktop app, alter its composer, or install a ChatGPT
  sidebar extension. Those require their own documented frontend contract.
- **Validate:** Generate `codex app-server generate-json-schema --experimental
  --out <local-folder>`, test initialization, and round-trip a synthetic form
  before any model inference. Then verify the actual client visually.
- **Evidence:** `documented` client architecture; `observed-working` backend
  initialization, ephemeral thread, direct MCP call, and callback roundtrip;
  bespoke visual client `untested`.
  [App-server](https://learn.chatgpt.com/docs/app-server).
