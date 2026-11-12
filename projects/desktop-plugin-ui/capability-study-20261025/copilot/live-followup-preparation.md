# Copilot live follow-up preparation

Prepared October 25, 2026 after the initial readiness reply. The user later
selected **Continue without Copilot sign-in**; root observed the reopened native
window signed out with Restricted Mode cleared. Preserve that steering:
perform no authentication or Copilot model turn. Root owns all actual assistant
UI actions. This follow-up reviews scoped logs and prepares/tests a synthetic
CS1 fixture; it does not establish Copilot Chat paint. No account storage,
credentials, global profile, terminal GUI or provider was accessed.

Root's final UI observation supersedes the earlier readiness assumption:
the reopened window displayed Sign In and model sign-in requirements with no
Restricted Mode banner. Before root's later command-palette attempt, the window
had closed; the input helper reported no foreground process, and a fresh window
inventory showed no Code window. No MCP UI command executed. Root stopped
without another launch, authentication attempt or model turn. These are
root-reported native observations, separate from this agent's log/browser checks.

## Changed evidence

The task-local `vscode-profile-visible` snapshot captured at 18:14:55 UTC differs
from the prior activation diagnostic:

- `window1/exthost/exthost.log` has 18 lines instead of 12. Line 15 records an
  activation attempt for `GitHub.copilot-chat` at log-local `14:06:04.265`, with
  `activationEvent: 'onStartupFinished'`. This is an observed activation attempt,
  not proof of completed activation, sign-in entitlement or chat paint.
- Lines 17–18 record a renderer-requested termination at `14:06:53.333` and
  extension-host exit code 0. It was not logged as a crash. Do not assume this
  particular extension host remains active after the user's readiness reply.
- Neither the 18-line extension-host log nor the selected renderer errors has
  an actual Copilot activation-failure stack. Renderer line 300 repeats the
  earlier requested-but-not-granted API-proposal diagnostic at `14:06:03.889`.
  The later selected error is a Node `url.parse()` deprecation warning. These
  messages alone establish neither fatal incompatibility nor harmlessness.
- The configured `mcp-chat-live` artifact directory is absent at this read.
  Therefore no startup HTML, initialize, tool-call or resource-read receipt is
  available in that configured location. This is not proof that every possible
  Copilot/MCP process is stopped or that the feature is unsupported.

The sanitized hashes/timestamps and selected diagnostics are retained in
`projects/desktop-plugin-ui/artifacts/capability-study-20261025/copilot/activation-diagnostic-followup-v1.json`.
The prior diagnostic remains unchanged. Current UI readiness must be established
by root's new observation, rather than inferred from these scoped log files.

## Exact synthetic route

The workspace `.vscode/mcp.json` registers `copilot_ui_study` over stdio using
the existing task package's `tsx`. It now points to the new study-specific
`mcp-probe/live-server-copilot-20261025.ts --stdio`, with evidence output directed
to `artifacts/capability-study-20261025/copilot/mcp-chat-live-v2` under the project.
Its safe task-profile settings enable MCP Apps and retain workspace trust and
default sampling permissions. Credentials, databases and global settings were
not inspected or changed.

The source exposes:

- `ui_limits_open`, empty input schema, UI resource
  `ui://assistant-limits/probe-v1.html`, initial synthetic value 7.
- `ui_probe_increment`, app-only visibility, integer input `value` from 0 to 99,
  returning `value + 1`. No filesystem, account or command tool is exposed by
  this server. Other host-enabled tools require separate root inspection.

The prepared minimal prompt for a later signed-in, authorized check is:

> Call copilot_ui_study's ui_limits_open once with {} to open the synthetic UI probe. Do not call other tools or modify files. Reply briefly in English.

Do not submit that prompt during the current signed-out follow-up. Root can
inspect normal server discovery and tool listings without implying model or
chat readiness. A future model choice must come from the real available picker;
this review does not establish model names, multiplier, credit entitlement or
a zero-cost model. If a security/permission gate appears, retain it for the
human rather than bypassing it.

## Controls and expected bounded checks

1. Observe `Connected to host bridge` and value 7; capture the negotiated
   capabilities and host context before acting.
2. Click `Increment locally via tool`: expect 7→8 and an app-only server receipt,
   with no further model inference. Then `Reject invalid input` should retain
   the value and show English recovery feedback. Increment again to verify
   continued operation after rejection.
3. `Check sandbox` records parent-document access, bridge presence and secure
   context. A DOM isolation result is different from network/device permission.
4. `Update model context only` requests context without a follow-up model reply;
   verify the host's actual context result separately from any visible attachment.
5. Fullscreen, picture-in-picture, download and external-link controls are
   disabled when their negotiated host capabilities/modes are absent. Record
   disabled controls rather than force-clicking them. Downloads/navigation and
   resulting permission prompts are separate acceptance steps.

The widget has English labels and `lang="en"`, a status region and 44px minimum
buttons. It is a capability probe rather than a complete usability test.

## New ColorSet 1 clone and verification

The legacy `live-server.ts` remains unchanged at SHA-256
`43e06b0b9a2f0a6341a256478fdc88c6b750544bfad3c64aecfc6235384fc03a`.
The new clone, SHA-256
`8cda1f2ed0657fc8fda3e487b7ecf4587a3f7462746648c1430cbf687bd58e5f`,
replaces authored host-variable/native-default paint with exact CS1 colors,
while preserving protocol, tools, validation and widget behavior. It adds
English capability help, a named action region, 44px controls, responsive
wrapping, and a 3px red keyboard focus outline offset by 3px. Forced-colors
overrides remain host-owned and are authored but not exercised here.

The prior task config is retained byte-for-byte in ignored
`artifacts/capability-study-20261025/copilot/config-snapshots/mcp-pre-cs1-v1.json`;
the before/after hashes are recorded in sibling `cs1-route-v1.json`.

`design_values.py` verifies seven exact paths and seven contrast pairs:

| Authored role | Exact token path(s) | Contrast |
| --- | --- | --- |
| Body text / background | `interface.text.primary` / `colors.neutral.white` | 10.918238644424665:1 |
| Primary button text / fill | `colors.neutral.white` / `colors.brand.primary` | 7.9046884551695875:1 |
| Primary hover text / fill | `colors.neutral.white` / `colors.red.dark` | 11.932745997117243:1 |
| Status/diagnostic text / fill | `interface.text.primary` / `colors.gray.100` | 8.829244121214963:1 |
| Identifying border / white | `colors.gray.600` / `colors.neutral.white` | 5.489814557409947:1 |
| Identifying border / soft fill | `colors.gray.600` / `colors.gray.100` | 4.439444354179186:1 |
| Focus / white | `colors.brand.primary` / `colors.neutral.white` | 7.9046884551695875:1 |

The remaining resolved path is `typography.primary`; no remote font is fetched.
The border-on-soft-fill pair is used for essential non-text contrast, not
ordinary text. Disabled-control text uses the dark primary ink.

The new verifier runs the actual clone over MCP stdio and passes its served
HTML to an offline sandboxed browser with an explicitly synthetic host:

```powershell
# Run from projects/desktop-plugin-ui/mcp-probe.
$env:UI_COPILOT_VERIFY_RUN='v3'
node node_modules/tsx/dist/cli.mjs verify-live-copilot-20261025.ts
```

The retained final v3 report passes **24/24** checks: exact tool/resource contracts,
initial value 7, valid 7→8 action, negative-input rejection preserving 8,
successful recovery to 9, parent DOM denial, context without `ui/message`,
capability-disabled controls, keyboard focus and CS1 paint/layout at 900, 360
and 320 pixels. It records zero page errors, browser network requests, model
turns or provider requests. A manual 320px screenshot inspection confirms
readable English controls, visible focus and no horizontal clipping.

Raw evidence lives in ignored
`artifacts/capability-study-20261025/copilot/cs1-fixture-verification-v3/` under
the project. V2 remains separately at 24/24. Root's 320px review identified an
ambiguous status label in that version: `Connected to actual host` could imply
actual assistant acceptance when rendered in a synthetic host. V3 changes only
the new clone's bundled status copy to `Connected to host bridge`; the legacy
widget/server remain unchanged. V2's clone is archived byte-for-byte at
`cs1-fixture-verification-v2/source/live-server-copilot-20261025.ts`, with its
original SHA-256 `41ed3976d7fc624d7b37fc3b6cb431229bf26f7b3c985af3fa8d400a40d7258a`.
The copy-change/archive hashes are retained in
`config-snapshots/cs1-status-copy-v3.json`. The verifier's expected ready text
was updated, and one fresh v3 run passes all 24 existing checks without new
behavior, account, model or actual assistant UI actions.

V1 remains at 23/24: the initial harness measured programmatic
focus immediately after pointer clicks instead of real keyboard focus. Only
the verifier was corrected, using Tab then Shift+Tab; server/UI source stayed
unchanged. A separate retained startup syntax failure executed zero checks,
and its initial receipt-path mistake was corrected with an explicit repo cwd.
These are verifier failures, not Copilot capability failures. The verifier
refuses to overwrite a completed run receipt.

## Bounded Nielsen inspection of the clone

| ID / label | Concrete finding and remaining limit |
| --- | --- |
| H1 / Visible status | Connecting/connected text, current value and action results are visible; rejected input preserves the value. Long-running/concurrent action status is not tested. |
| H2 / Familiar concepts | English action labels identify synthetic operations; technical capability/context JSON stays under disclosure. Familiarity with representative users is untested. |
| H3 / Control and exits | This probe has no saved user edit to discard; unsupported actions are disabled. Closing, download/link cancellation and host exits are separate actual-host checks. |
| H4 / Consistent conventions | Native button/summary semantics and actual keyboard focus work in the browser. Copilot's surrounding conventions remain outside this fixture. |
| H5 / Prevent mistakes | The real MCP schema rejects the deliberate negative integer. Repeated/concurrent actions and the upper input boundary are not exercised here. |
| H6 / Recognition cues | The current value, readable labels and visible disabled states avoid recall-only controls; capability details remain discoverable. |
| H7 / Efficient paths | Tab/Shift+Tab reaches the primary action with visible focus. Custom shortcuts are unnecessary for this small probe and are not added. |
| H8 / Minimal content | One primary action is emphasized; verbose diagnostics are disclosed on demand. The capability buttons are test controls, not a recommended production dashboard layout. |
| H9 / Useful errors | English rejection feedback preserves 8, and the next valid action reaches 9. Raw diagnostics do not replace recovery copy. |
| H10 / Contextual help | English introductory copy explains synthetic data, no direct-action model reply and disabled host actions; per-host permission help remains an actual-host check. |

This is heuristic inspection, not a representative-user study, screen-reader
application test, or full accessibility certification.

This pass used zero model turns, actual assistant UI actions or account
operations. Synthetic browser success does not establish signed-in Copilot
Chat paint, actual host CSP/permissions, OS delivery or canvas support. It does
not remove the broader skill's `validating` status or recorded semantic failures.
