# Live readiness follow-up

Date: October 25, 2026, America/New_York. This continues the
[Copilot/Codex study](copilot-codex-study-20261025.md) after the user reported
the chart expanded and the workspace ready. The user later explicitly selected
**Continue without Copilot sign-in** and confirmed the fresh chart expanded
and visible. Respect both instructions; perform no further sign-in or Copilot
model attempt. All authored UI and documents remain English.

## Observations and their boundaries

| Host / surface / version | Execution layer and result | Evidence |
| --- | --- | --- |
| Task-profile VS Code 1.143.1; Copilot Chat 0.71.0 on disk | Scoped extension-host log records Copilot activation at 14:06:04 EDT, then renderer-requested termination and exit 0 at 14:06:53. No activation-failure stack found in the checked log; the proposal diagnostic persists. | `observed-working`: activation attempt/log inspection only; sign-in, completed activation and chat paint are separate. |
| Reopened `paint-workspace`, same portable VS Code 1.143.1 | Native window no longer showed Restricted Mode; Sign In and “Models, sign in to use Copilot” remained visible, with default permissions. | `observed-working`: later native readiness inspection; authenticated model readiness unverified. |
| Same native study window | Before a command-palette input attempt, the window had closed. The helper reported no foreground process; refreshed inventory showed no Code window. No MCP UI command executed; no further launch was made. | `observed-failed`: this automation attempt against an unavailable window; not a product exclusion. |
| Current Codex conversation; installed package baseline 26.1021.3705.0 | One fresh `xy_render_chart` call returned the English study title, CS1 and chart/export metadata. The earlier chart's expiration prompted this refresh. | `observed-working`: connected tool result only, not pixel/control acceptance. |
| Codex MCP Apps controller; controller build unrecorded | After the second expansion confirmation, browser ID `1` briefly listed “Reflex Xy Local MCP XY chart ready”, tab `1`. Binding returned “Tab not found in browser undefined”; later inventory was empty. The short `mcpapps` selector also returned empty lists. | `observed-working`: one discovery result; `observed-failed`: tab binding. Actual DOM/control checks did not execute. |
| Same Codex chart; capture-specific renderer version unrecorded | The user reported the fresh chart expanded and visible. No agent screenshot, DOM read or control result was acquired. | `untested`: agent-verified paint/controls; preserve the human report separately. |
| Local Reflex XY adapter source; repository implementation snapshot | Source declares the proper MCP App UI resource/MIME and private result metadata. Its own Expand button requests fullscreen. Expiry gates chart records/actions, not UI resource registration. | `observed-working`: bounded source inspection, not proof of current frontend delivery. |

The chart's component mode and the host side-panel operation are different.
The observed transient inventory/binding gap does not establish why the tab
became unavailable, nor that Codex cannot render it. Do not replace native
integration acceptance with a manually opened HTML export. Model-visible
absence of app-private `_meta` is also insufficient to diagnose server omission.
See the [source diagnostic](../../projects/desktop-plugin-ui/capability-study-20261025/codex/panel-followup-diagnostic.md).

The Computer Use skill prohibits automating user authentication dialogs and
security/privacy permission requests. The user chose to omit authentication,
so this follow-up proceeds within the available non-authenticated scope. No
permission bypass, copied credential, global account/profile edit or new model
provider is used.

## Exact-CS1 fixture verification

A new [study-specific server](../../projects/desktop-plugin-ui/mcp-probe/live-server-copilot-20261025.ts)
preserves the legacy protocol, tool authority and behavior while adding exact
CS1 authored paint, English help, 44px controls, visible keyboard focus,
responsive wrapping and forced-colors support. The task-only MCP configuration
points to this clone. The earlier configuration and legacy source remain
preserved; no claim is made that the changed server was started in Copilot Chat.

The [preparation and verification note](../../projects/desktop-plugin-ui/capability-study-20261025/copilot/live-followup-preparation.md)
contains exact paths, seven palette bindings/contrast pairs, source hashes and
the ten Nielsen inspection items. Its zero-inference verifier combines:

- **Actual MCP stdio:** resource/tool metadata and MIME, initial value 7,
  valid increment 7→8, rejected negative input preserving 8, and recovery to 9.
- **Offline synthetic browser:** context without `ui/message`, parent DOM
  denial, capability-disabled controls, English copy and layouts at 900, 360
  and 320px. Real keyboard navigation produces the 3px CS1 focus outline.

The first retained fixture run passes 23/24 because the harness measured
programmatic focus after mouse input. A corrected harness uses Tab/Shift+Tab;
its separate v2 run passes **24/24**, with zero page errors, browser network
requests, model turns or provider requests. Root inspected the 320px screenshot:
controls are readable and English, with no horizontal clipping. An additional
copy refinement changes “Connected to actual host” to “Connected to host bridge”
so the status remains truthful in a synthetic host. Its fresh **v3 passes
24/24** with zero page errors, network requests or model turns. The exact v2
source is archived with its receipt; legacy source remains unchanged. The
current clone SHA-256 is
`8cda1f2ed0657fc8fda3e487b7ecf4587a3f7462746648c1430cbf687bd58e5f`.
Its raw receipt is
`projects/desktop-plugin-ui/artifacts/capability-study-20261025/copilot/cs1-fixture-verification-v3/report.json`.

This is fixture evidence, not Copilot Chat paint, real OS download/navigation,
device permission, canvas acceptance or representative-user testing. All prior
startup/verifier failures remain retained. The legacy server is unchanged.

## Canonical promotion and scoped validation

Promote the bounded readiness/discovery findings into the capability guide and
Copilot limits, and distinguish fullscreen from host side-panel opening in the
existing mode-negotiation pattern. Keep all 42 pattern IDs and language,
Nielsen/CS1-default/explicit-CS2 rules unchanged.

Freeze the new **22-file** source/runtime/full subject at SHA-256
`9146fdf19d45fa9f3e3608f48677ca43b21ca16763e302956caccbe6a6ac68cf`.
The [narrow forward prompt](../pi-prompts/desktop-plugin-ui-live-followup.md)
and [independent criteria](live-followup-review-criteria.md) are frozen before
the single isolated Luna run. It is a status diagnostic, not a renderer test or
a replacement for the prior failed five-case offerings cohort. Required exact
outputs are `followup/status.md` and `followup/status.json`, with both current
host/test flags false. The existing explicit Luna exception is unchanged.

The [single retained forward run](live-followup-v1-luna-1.md) passes strict
execution **1/1** and final checking **1/1** (12 URL occurrences, five listed
historical rows), but conservative manual/joint acceptance is **0/1**. It
labels unestablished readiness/paint as `observed-failed` without a named failed
action, and implies a fullscreen request was observed without identifying
static source inspection. Its four requested status areas otherwise pass.
Retain the output and its failures; no rerun or reviewer repair was performed.
The exact 22-file payload, prompt, criteria and task-level false flags are
preserved; execution has zero tool errors. This does not clear prior cohorts.

Local synchronization updates only the three changed reference files and
verifies all 22 files from a non-ignored scoped source. Source checking passes
80 official URL occurrences; authoring source/runtime/full profiles match the
frozen hash. Pattern-ID, skill, independence, payload and scoped diff checks
pass. An independent final canonical/installed comparison requires exactly
22 files and the frozen hash; receipt paths are under ignored
`projects/desktop-plugin-ui/artifacts/data/` with the `live-followup` prefix.
Archive the source staging folder only after the nonzero sync check, and use
direct snapshots for any subsequent integrity check.

Overall status remains **validating** for the retained evidence-label failures
and live-host acceptance gaps. The user's no-sign-in choice remains in force.
This follow-up consumes zero Claude/Copilot inference; the one isolated
instruction test uses the recorded OpenAI Luna exception. No deployment,
publication, global account edit, commit or push was performed.
