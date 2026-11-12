# Codex backend and UI capability study

Snapshot: October 25, 2026. This study inventories current installed cores and
tests synthetic backend contracts with **zero new model turns**. It makes no
fresh desktop/IDE paint claim. The machine-readable
[capability matrix](capability-matrix.json) separates observed, documented,
conditional and untested offerings.

The important distinction is now versioned: the npm command uses **Codex
0.145.0**, while the current Windows desktop package **26.1021.3705.0** bundles
**0.164.0-alpha.11.1**. Both transport useful tools, media and form callbacks.
Current plugin documentation also explicitly supports Codex in the ChatGPT
desktop app and the CLI plugin browser, while excluding plugin bundles from
the IDE extension. Direct MCP configuration remains documented for the IDE.
That bundle restriction must not become an MCP-tool exclusion.
[Plugin availability](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors),
[plugins](https://learn.chatgpt.com/docs/plugins),
[MCP configuration](https://learn.chatgpt.com/docs/extend/mcp).

## Environment and provenance

| Component | Observed value | Evidence scope |
| --- | --- | --- |
| npm package / native core | `@openai/codex` 0.145.0 | Package metadata and executable `--version` |
| Desktop-bundled core | 0.164.0-alpha.11.1 | `codex.exe --version` from the desktop `bin/2993767bd1dfb009/` folder |
| Windows package | `OpenAI.Codex` 26.1021.3705.0 | Read-only Appx metadata; package family `OpenAI.Codex_2p2nqsd0c76g0` |
| Existing authentication | CLI reports `Logged in using ChatGPT` | Sanitized CLI status only; no credential file or account identity was collected |
| IDE extension | Build not established by this inventory | No `code` command on PATH or standard `.vscode/extensions` directory; alternate installations/profiles remain possible |

Executable SHA-256 values are
`83751f15cb6a0a7b97df67752c001e3fe1c20e18ffbfec3ff63567296205eb6c`
for npm and
`1103e9e09c71fa2cd0afd6d8f3b9a2d63174fe8efd7cb5bd09f1cb14ef58a098`
for the desktop-bundled core. The full paths, commands, exit codes and generated
schema counts are in
[inventory.json](../../artifacts/capability-study-20261025/codex/inventory-v1/inventory.json).
The [desktop metadata](../../artifacts/capability-study-20261025/codex/desktop-metadata.json)
retains the bounded package/IDE observations.

The OpenAI Docs broad Codex route was applied after reading the repository
instructions and local Codex skill baseline. Its manual helper fetched the
current official manual into the project artifact cache. Targeted official
documentation was then searched and fetched for plugin availability, MCP,
app-server, UI and extensions. Only official OpenAI documentation supports the
public product claims here. No user conversations or credential contents were
read. All runtime experiments use fresh project-contained `CODEX_HOME`
directories and synthetic data; there are no global configuration writes or
foreground application launches.

## Current experiments and retained failures

The earlier 0.145.0 probe and its existing results remain intact. A dated copy
replayed that baseline against the two current binaries:

| Fresh baseline case | Result | Interpretation |
| --- | --- | --- |
| npm, on-request | 18/18 | Original assertions still match 0.145.0 |
| Desktop core, on-request | 17/18 | Old nested-schema error-code assertion no longer matches |
| Desktop core, never | 17/18 | Same retained version-specific mismatch |
| Desktop core, no extended-form opt-in | 17/18 | Same retained version-specific mismatch |

All three failed reports remain under their original fresh case names. The
arbitrary nested-object form still fails: **0.145.0 returns -32601**, while
**0.164.0-alpha.11.1 returns -32602**, with a wire-parameter parse error.
That is a specific invalid-request outcome, not a declaration that the newer
core lacks MCP or that all rich forms are unsupported.

Separate version-aware feature cases declare the expected code explicitly and
add media, typed forms, state and connection correlation:

| Fresh current-contract case | Result | New model turns |
| --- | --- | --- |
| npm, on-request | 21/21 | 0 |
| Desktop core, on-request | 21/21 | 0 |
| Desktop core, never | 21/21 | 0 |
| Desktop core, no form opt-in | 21/21 | 0 |
| npm, per-process experimental MCP Apps flag | 21/21 | 0 |
| Desktop core, same experimental flag | 21/21 | 0 |

These are six fresh cases, not replacements for the baseline failures. Expected
negative responses are tested outcomes, and do not mean that every UI feature
passed. A minimal model turn was unnecessary for the additional backend facts.
The earlier actual 0.145.0 CLI model turn remains historical evidence in the
[prior Codex report](../../cross-assistant/codex/validation.md).

## What the interfaces offer

| Feature | Current observed or documented offering | Boundary |
| --- | --- | --- |
| Text and structured results | Both cores preserve text, `structuredContent` and `_meta` in synthetic MCP results. | Transport is separate from model interpretation and frontend controls. |
| CLI output | Installed help exposes JSON events, schema-constrained final output and image attachments. | A JSON schema is an output-data contract, not an HTML UI. |
| Models | Isolated `model/list` samples default to `gpt-5.6-sol` in npm and `gpt-6.1-sol` in the desktop core; sampled entries list text/image inputs. | No current account entitlement or inference test was performed; a model does not select the renderer. |
| HTML | `ui://` HTML bytes, MCP App MIME and `_meta.ui.resourceUri` survive tool/resource calls. | The embedded JS marker was delivered, not executed by this backend study. |
| MCP Apps | Official docs describe iframe UI and a shared bridge. | `ui/initialize` belongs at the supported iframe/host bridge, and is rejected at the app-server endpoint tested here. |
| Forms | Standard string, integer, boolean, enum and enumerated-array schemas reach synthetic client callbacks. Accept, decline and cancel round-trip. | Native form pixels, keyboard and screen-reader behavior remain untested. |
| Policy | `on-request` forwards callbacks; `never` declines without forwarding them. | This is elicitation policy evidence, not a command/file approval UI test. |
| Extended forms | Flat `openai/form` and `openaiForm` normalize to ordinary `form`, including without opt-in. | A valid richer image-picker UI was not tested. The arbitrary nested schema is a deliberate negative. |
| Images | The baseline preserves valid PNG result content; help/catalogs expose input image paths. | The one-pixel fixture proves transport, not meaningful vision, generation, terminal display or an interactive canvas. |
| Other media/resources | Both cores carry a valid WAV, CSV resource link and embedded SVG resource. | Playback, native SVG painting, video, camera/microphone permissions and OS downloads remain untested. |
| Tool state | A synthetic versioned mutation succeeds; a stale write returns `isError` while preserving authoritative state. | This is fixture-server state, not widget or durable business storage. |
| Progress | The progress tool returns its final result. | No progress notification is forwarded in this direct-call route; in-turn item streaming and visible progress widgets require separate tests. |
| Thread state | Fresh ephemeral metadata is readable before a model turn; history mode is legacy in npm and paginated in the desktop core. | No existing user history, persistence across restarts or thread UI was tested. |
| Placement | The UI and extensions guides document inline/fullscreen/PiP, sidebar, conversation panels, file viewers and composer entry points in their stated frontend scope. | Their schemas do not grant those surfaces to the CLI TUI or IDE. A custom client is one available route; it is not the only possible dashboard route. |
| Native controls | Server schemas describe user questions, elicitation, command/file approvals and permission requests. | Backend requests are separate from actual controls or arbitrary plugin-defined native panes. |
| Deployment | Stdio works in these probes. Docs cover MCP Streamable HTTP separately from app-server listeners. | WebSocket app-server transport is marked experimental/unsupported in current docs; remote listeners and authentication were not exercised. |

The app-server powers rich clients and explicitly separates thread, turn, item,
approval and client-response contracts. Current MCP tool-call items can use
`appContext.resourceUri`; the top-level `mcpAppResourceUri` field is deprecated
in the documentation. That is useful frontend metadata, not evidence that this
study painted a component.
[App-server](https://learn.chatgpt.com/docs/app-server).

The current UI guide gives a portable MCP Apps foundation and optional host
extensions. The extensions guide documents richer forms, sidebar apps,
conversation panels, file viewers, composer mentions and settings, with
surface/eligibility qualifications. Its MRTR requirement is specifically for
**OpenAI-registered MCP servers**, not a blanket rule for every local server.
[UI guide](https://developers.openai.com/plugins/build/chatgpt-ui),
[extensions](https://developers.openai.com/plugins/build/extensions).

## Connection attribution correction

The original uninstrumented logs recorded one MCP initialization advertising
`openai/form` and another omitting it. The earlier reference inferred which
connection executed the tool from ordering. The new fixture adds a process ID
to every received request and correlates initialization with actual tool calls.
In **both current cores**, the process serving direct calls advertises
`openai/form` when opted in. A separate idle process omits it. Without opt-in,
the serving process omits that extension and standard forms still work.

Withdraw the old claim that the executing thread connection lacked the
extension. The evidence supports a narrower account: capability negotiation,
flat-schema normalization and invalid nested-schema parsing are distinct.
No valid richer-control rendering was established. The current PID logs and
callbacks are retained in each current-contract case's `report.json` and
`mcp-events.jsonl`.

## Schemas, feature flags and frontend checks

Both binaries generate their experimental JSON schemas successfully: **347
files / 126 client requests** for npm, and **458 files / 175 client requests**
for the desktop core. Each exposes 11 server-request methods. The newer core
adds project/section/queue/attachment and event-stream methods, among others;
its elicitation union also includes `openaiForm` and
`openai/userVerification`. Device verification was not invoked.

The request unions contain no `ui/*`, fullscreen, sidebar, canvas or display-mode
placement method names. This bounds the app-server API tested here. It does
not override public plugin UI contracts or actual desktop renderer evidence.
The exact inventory and differences are in
[schema-summary.json](../../artifacts/capability-study-20261025/codex/schema-summary.json).

Fresh isolated feature listings show `apps`, `plugins`, `image_generation` and
`in_app_browser` as enabled, while `enable_mcp_apps` is under development and
false. Testing only that last flag as a per-process true override preserved
all 21 backend checks, but still did not advertise
`io.modelcontextprotocol/ui` in the observed downstream connections. This flag
alone is not an established desktop-UI activation procedure. Enabled image,
voice or browser flags likewise are not execution or entitlement evidence.

The root task is checking the actual current desktop component through its
supported app-panel tools. A returned chart result alone is a tool success,
pending actual panel paint. Separately, the existing
[Reflex XY installed-host record](../../../../evaluations/reflex-xy/native-desktop-20261025.md)
attributes a genuine inline chart paint to an earlier ChatGPT desktop Codex-mode
session using direct same-host MCP after Save and Restart. That report pins its
observed package to **26.1016.6573.0**, retains failed folder-plugin server
discovery and reports direct MCP as the successful workaround. Do not silently
rebind that historical screenshot to today's 26.1021.3705.0 package or claim
its controls, downloads or sidebar were accepted.

## Reproduction and evidence

Source probes live beside this report:

- [inventory.py](inventory.py): captures help/version/feature/schema data from
  two explicitly supplied executable paths in isolated homes.
- [protocol_probe.py](protocol_probe.py) and [fixture.py](fixture.py): dated
  baseline replay, preserving the original version-specific assertions.
- [feature_probe.py](feature_probe.py) and
  [feature_fixture.py](feature_fixture.py): version-aware typed media/state/form
  tests, synthetic client actions and PID-correlated connections.

Representative commands, with executable paths taken from `inventory.json`:

```powershell
uv run --script projects/desktop-plugin-ui/capability-study-20261025/codex/inventory.py --npm-codex <npm-core.exe> --desktop-codex <desktop-core.exe> --out projects/desktop-plugin-ui/artifacts/capability-study-20261025/codex/inventory-v1
uv run --script projects/desktop-plugin-ui/capability-study-20261025/codex/protocol_probe.py --codex <desktop-core.exe> --approval-policy on-request --out projects/desktop-plugin-ui/artifacts/capability-study-20261025/codex/desktop-on-request-v1
uv run --script projects/desktop-plugin-ui/capability-study-20261025/codex/feature_probe.py --codex <desktop-core.exe> --approval-policy on-request --nested-error-code=-32602 --out projects/desktop-plugin-ui/artifacts/capability-study-20261025/codex/desktop-current-contract-v1
```

The other current cases use `--approval-policy never`, `--no-openai-form` or
`--enable-mcp-apps` in separate fresh directories. The npm cases explicitly use
`--nested-error-code=-32601`. A source snapshot with hashes under
`probe-sources-v1/` preserves the fixture and runner used before adding the
optional experimental-flag argument. Prior sources/results remain untouched.

New experiments started **zero model turns**, issued no `turn/start`, opened
no user conversation history, invoked no account/permission flow and made no
global configuration changes. The audio is ten milliseconds of generated
silence; SVG/CSV/HTML and all messages are synthetic and authored in English.
HTML uses exact CS1 red/dark-neutral/white values. A model catalog request and
official documentation retrieval are distinct from inference; no network-free
claim is made for the entire research session.

## Recommended canonical deltas

1. Pin npm CLI, desktop package, bundled core and IDE extension independently.
2. Correct the old connection attribution using the PID-correlated evidence.
3. Keep nested-invalid error assertions version-aware, retaining all old
   failures and distinguishing an invalid schema from a missing whole protocol.
4. Add WAV, CSV resource-link, embedded SVG and typed standard forms as backend
   evidence, with playback/paint/download and native rich controls separate.
5. Distinguish documented IDE plugin-bundle availability from IDE MCP setup.
6. Attribute the historical direct-MCP desktop paint and folder-plugin failure;
   keep the fresh current-package result separate.
7. Record direct-call progress as unobserved while keeping in-turn streaming
   and frontend progress indicators as separate checks.

These are recommendations only. This agent did not edit the canonical skill,
backlog, installed settings or earlier evidence.

For later UI implementation, retain the existing H1-H10 contract: truthful
status, task vocabulary, safe exits, host conventions, validated/versioned
actions, visible context, discoverable efficient paths, focused content,
recoverable errors and contextual help. This backend study observes inputs and
outcomes for several of those contracts; actual focus, copy announcements,
layout, color contrast, cancellation controls and usability remain frontend
acceptance checks. No heuristic inspection or model modality substitutes for
those results.
