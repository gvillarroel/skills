# Codex empirical UI boundary probes

Date: 2026-10-24 in the user's America/New_York timezone; some captured UTC
timestamps fall on 2026-10-25. Windows 11 build 26200, npm Codex CLI 0.145.0.
The existing CLI reported `Logged in using ChatGPT`. No credentials, account
files, user conversations, or saved thread histories were read by these probes.
The CLI's normal authentication implementation handled its own credentials.

## Source review

Applied OpenAI Docs; searched and fetched the current official UI, extension,
CLI, and app-server pages. Sources used by the canonical reference:

- https://developers.openai.com/plugins/build/chatgpt-ui
- https://developers.openai.com/plugins/build/extensions
- https://learn.chatgpt.com/docs/app-server
- https://learn.chatgpt.com/docs/app-server#mcp-server-elicitation-requests
- https://learn.chatgpt.com/docs/cli/reference

`https://learn.chatgpt.com/docs/mcp` returned 404 and was not used as evidence.
The app-server schema was generated from the installed binary with
`codex app-server generate-json-schema --experimental --out <artifact-folder>`.
Its request surface includes direct tool/resource calls and form callbacks.

## Final protocol cases

The source fixtures live next to this note. Generated schemas, logs, and
reports are under the ignored
`projects/desktop-plugin-ui/artifacts/cross-assistant/codex/` directory.

| Run | Policy | Extended-form opt-in | Assertions | Model calls |
| --- | --- | --- | --- | --- |
| `protocol-final-on-request` | `on-request` | true | 18/18 | 0 |
| `protocol-final-never` | `never` | true | 18/18 | 0 |
| `protocol-final-no-opt-in` | `on-request` | false | 18/18 | 0 |

Example PowerShell command, using `codex.exe` resolved from the installed npm
package (the path is a local installation detail):

```powershell
uv run --script projects/desktop-plugin-ui/cross-assistant/codex/probe.py --codex <absolute-codex.exe> --approval-policy on-request --out projects/desktop-plugin-ui/artifacts/cross-assistant/codex/protocol-final-on-request
```

The matrix varies `--approval-policy never` and `--no-openai-form`. Each uses
its own isolated CODEX_HOME inside the artifact directory, ephemeral threads,
synthetic local MCP tools, no turn/start request, no cloud inference, and no
real account data. Each case checks initialize, thread start, inventory,
text/structured/_meta result transport, PNG transport, standard form action,
URL action, flat openai/form normalization, arbitrary nested-object rejection,
HTML resource bytes, the rejection of app-server `ui/initialize`, downstream
capabilities, and host callback counts.

The first exploratory runs used a flat `openai/form` schema. It was normalized
to `form`, including when the downstream connection did not advertise the
extension. The later nested-object probe returned MCP `-32601` rather than a
host callback. Two exploratory expectation counts consequently failed (14/16
and 15/16); those reports remain preserved. The final fixture separates flat
normalization from the unsupported nested-schema case and tests both. This
does not claim the arbitrary nested schema is a documented valid OpenAI rich
form or that all rich forms fail.

Approval policy was the decisive variable for ordinary elicitation: `never`
auto-declined and produced zero callbacks. `on-request` delivered three
callbacks (form, URL, normalized flat openai/form), with nullable turnId and
the synthetic responses correctly reaching the MCP server. The client accepted
the two basic forms and declined the synthetic URL; no browser was opened.

Two different downstream MCP initializations were observed: app-scoped and
thread-scoped. Only the app-scoped connection advertised `openai/form` when
opted in. No observed connection advertised `io.modelcontextprotocol/ui`.
Metadata/resource transport alone therefore did not prove a frontend renderer.
`ui/initialize` sent to app-server returned `-32600` unknown variant because it
is the wrong protocol endpoint, not because all Codex frontends are excluded.

## Actual CLI model turn

The first requested model, `gpt-6-luna`, failed with model_not_found for this
CLI and ChatGPT account. No tool call ran and no usage totals were returned.
The model exists in the parent app's settings, illustrating why that catalog
cannot be assumed to describe this CLI's available model identifiers.

The installed bundled model catalog was inspected without inference. A second
run with `gpt-5.6-luna` succeeded:

```powershell
uv run --script projects/desktop-plugin-ui/cross-assistant/codex/exec-probe.py --codex <absolute-codex.exe> --model gpt-5.6-luna --out projects/desktop-plugin-ui/artifacts/cross-assistant/codex/exec-bundled-model
```

It used `--ignore-user-config --ephemeral --json --color never`, read-only
sandbox, zero project-document byte budget, a local fixture MCP server, and
the prompt: call the synthetic card once, form once, no other tools, then
return `UI_PROBE_DONE`. Exactly those two calls ran. Exit code 0, 9 valid JSON
events, final marker present, text/structured/_meta payload preserved, form
auto-declined, and no interactive UI appeared in the noninteractive JSON
channel. The `structuredContent` wire field is exposed as `structured_content`
inside this CLI JSON event representation.

Reported usage: 61,487 input tokens, 45,312 cached input tokens, 331 output
tokens, 211 reasoning output tokens. The output stream warned that skill
descriptions were shortened. `--ignore-user-config` did not disable ambient
skill discovery, so the input was larger than the tiny prompt suggests.
Further model turns were avoided. All other tests used zero model inference.
The exec runner requires an explicit model; select it from the active CLI.
The original generated report field `modelRequestsStarted: 1` meant one
top-level turn; it did not count inference HTTP requests across the tool loop.
The runner now names that metric `modelTurnsStarted`. Original raw logs and
reports are retained unchanged.

## Scope limits

These are installed-runtime backend and headless CLI tests. They do not prove
desktop widget paint, terminal image pixels, IDE UI, JavaScript execution,
native rich form controls, purchases, account login, URL navigation, or device
permissions. The root task owns frontend exploration. Treat successful backend
bytes and a passed negative assertion as scoped evidence, not feature support.
