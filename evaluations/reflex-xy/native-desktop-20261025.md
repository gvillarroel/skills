# Reflex XY installed-host follow-up

Date: 2026-10-25. Adapter release: **0.3.1**. This follow-up preserves the
[0.3.0 release record](native-desktop-20261024.md) and all retained failures.
The canonical `reflex-xy` skill runtime remains the same 19-file subject; no new
isolated skill-use cohort is claimed. The broader skill stays `validating`.

## Current acceptance by layer

| Surface and layer | Evidence | Result and remaining boundary |
| --- | --- | --- |
| Claude Desktop ordinary Chat, 3.6556.2, local stdio | `observed-working` | Genuine XY chart painted inside the chat. Initial CS1, explicit CS2, Expand, Save image and exact-data editing worked. Controls left the feed at Message 1 of 2 / Message 2 of 2. |
| Claude Chat saved file | `observed-working` | Native Download consent and Save dialog produced a 1920×1080 PNG. The host reencoded the PNG; decoded RGBA pixels equal the original exactly. |
| ChatGPT Windows desktop app, Codex mode, direct same-host MCP | `observed-working` | `reflex_xy_local` loaded after Save and Restart in MCP settings. An actual `xy_render_chart` request returned CS1; the native app window showed the genuine plot inside its framed tool component. |
| ChatGPT installed folder plugin 0.3.1, bundled-server discovery | `observed-failed` | Installed/enabled and version visible; catalog Refresh and a new Try now attempt did not expose `xy_render_chart`. Direct MCP is the observed workaround. No account-tier exclusion is inferred. |
| ChatGPT in-component controls and global/thread launchers | `untested` | Protocol fixtures pass, but actual host button/download/sidebar acceptance remains separate from inline paint. |
| Claude Code user plugin, CLI 2.1.302 | `observed-working` | Version 0.3.0 is installed/enabled at user scope; strict scan and 9/9 native-engine tests pass. The final 0.3.1 archive has unchanged native hook/saver behavior. |
| Claude Desktop Code pane | `observed-failed` | The actual app shows Get Claude Code before project access. No native Mod pane screenshot is claimed. Account authentication/access remains `conditional`. |
| Four final archives and declared launch contracts | `observed-working` | Exact inventory/hash/source identity, 19 canonical resources, versions, portable schema 11/11 and official MCPB 2.1.2 schema pass. These checks do not establish host painting. |

The initial observed ChatGPT Windows package was 26.1016.6573.0; the installed
Codex CLI loader is 0.145.0. Do not infer a newer app package version from an
updated plugin or computer-use package. Actual app results are bounded to this
machine and its tested session.

## Corrected transport and retained failures

The 0.3.0 MCP App outer controls loaded in actual Claude Chat, but its nested
loopback iframe produced `chrome-error://chromewebdata/`. That blank chart
remains a failed acceptance. Release 0.3.1 uses resource
`ui://reflex-xy/chart-v4.html`: original native XY HTML and SVG travel in
app-private `_meta`; the interactive preview uses sandboxed `srcdoc` and the
fallback uses the original SVG as a data URL. It does not substitute another
plotting implementation.

`xy_get_chart_artifact` is app-only and returns bounded original bytes to
standard `app.downloadFile` as an embedded resource. The component does not
fetch an HTTP artifact origin. The loopback asset listener remains optional for
direct clients, and HTTP `/mcp` is absent in desktop mode. Invalid capabilities
return no bytes; previews above 8 MiB and exports above 16 MiB are rejected.

The first 0.3.1 MCPB preflight omitted the new artifact tool from its manifest.
The failing report and complete package remain at
`projects/reflex-xy-plugins/artifacts/independent/0.3.1/mcpb-transport/report.json`
and `artifacts/releases/0.3.1-preflight/`. The corrected final manifest declares
all six tools. Its successful repeat uses a new
`mcpb-transport-final/report.json`; the earlier failure was not overwritten.

The actual Codex 0.145.0 loader also left `${PLUGIN_ROOT}` literal in the earlier
plugin command, environment and working directory. The corrected portable
declaration uses `cwd: "./"` and package-relative paths. `./` passes the published
MCP schema; `.` does not. Real app-server initialization and exact-installed
subprocess rendering pass with that declaration, independently of the Desktop
bundle-discovery failure.

The [official MCP setup](https://learn.chatgpt.com/docs/extend/mcp) documents
same-host shared configuration and the Save → Restart flow. In the actual
app this was Settings → Plugins → MCPs. Catalog Refresh, MCP server Restart
and quitting the application are separate operations. The direct server used
absolute installed Node/server/renderer/skill/uv paths, an installed-package
working directory, and project-contained runtime/cache paths. This connection
loaded the current conversation's tools and painted the inline component.

The [portable manifest contract](https://developers.openai.com/plugins/deploy/submission#manifest-fields)
assigns component discovery to root `skills/` and `mcp.json`. Repeating those
paths in the inline OpenAI metadata object cannot change portable discovery.
The current package follows that contract; no speculative metadata duplication
is promoted as a repair. Approved-partner restrictions in
[desktop-only submissions](https://developers.openai.com/plugins/deploy/desktop-only)
concern public publication submissions, not an observed local-use account gate.

## Actual screenshots and file evidence

Local full-app captures are retained under
`projects/reflex-xy-plugins/artifacts/native-install-20261025/screenshots/`:

- `claude-chat-cs1-inline-v0.3.1.jpg` and `.txt`.
- `claude-chat-cs1-fullscreen-v0.3.1.jpg` and `.txt`.
- `claude-chat-cs2-fullscreen-v0.3.1.jpg` and `.txt`.
- `claude-chat-edited-data-cs1-v0.3.1.jpg` and `.txt`.
- `chatgpt-cs1-inline-v0.3.1.jpg` and `.txt`.
- `chatgpt-mcp-restart-control.jpg` and `.txt`.

The Claude conversation is `Reflex-xy chart rendering`, ID
`849bd75d-4adc-4c21-adf5-97ff899645a6`. Its editor applied x=[1,2,3] and y=[2,6,4],
title `Edited in Claude`; omitting the palette returned CS1 after the previous
CS2 choice. The conversation retained two messages during these controls.

The actual Claude save is
`artifacts/native-install-20261025/images/claude-cs1-v0.3.1.png`: **268,433 bytes**,
SHA-256 `e6596479f246176dedf301f5aebaaf41abc0ac48458f812c2fd059e8344dd84e`.
The Python-produced original is **262,650 bytes**. Both decode to exactly equal
1920×1080 RGBA pixels. The wire export bytes are independently identical to the
original before the host's file-save step; actual host-saved byte identity is
not claimed.

The earlier `claude-chat-nested-loopback-failure.jpg`,
`claude-code-access-gate.jpg`, and
`chatgpt-candidate-tool-unavailable-before-restart.jpg` remain failed/gated
evidence. Browser-tab captures from earlier work remain excluded from native
component acceptance. Private profile backups stay in ignored, restricted
storage and are not copied into source or reports.

## Focused verification

The final app build hashes are:

- `server-bundled.js`: `90a6faacc30abdc4fed9a62ac0d1b46759e92753622982f1587cbfba51594b52`.
- `widget.html`: `c1d199dff06b6b1b21c9549b5b9900ba0e90f384fd63d367acbb10b5bf1b1b99`.

The final release was built with:

```powershell
uv run --script projects/reflex-xy-plugins/scripts/build_plugins.py --output-dir projects/reflex-xy-plugins/artifacts/releases/0.3.1 --desktop --app-dist projects/reflex-xy-plugins/artifacts/candidate-0.3.1/chatgpt/dist
```

The source/default build was subsequently regenerated and matches that
candidate byte-for-byte. Type checking, 8/8 boundary/embedded tests, the full
desktop stdio browser fixture, constrained-host fallback and isolated bundled
stdio checks pass. The browser fixture blocks all HTTP(S) requests and records
zero browser requests, model messages, model-context updates and sampling
requests. It paints a real XY canvas, exercises both palettes, new-chart reset,
exact editor data, recovery, five formats, keyboard disclosure and narrow layout.
The constrained fixture shows original SVG when scripts are blocked and a clear
error without exporting when host file saving is unavailable.

Both final portable and MCPB manifest → bundled Node → stdio → uv checks pass
eight checks: six tools/v4 resource, exact packaged widget, native previews,
capability rejection, original export bytes, palette sequence, native mark ink,
and about-only frame CSP. Across the two packages, five exports for three
charts each match original disk and HTTP bytes. These fixtures and protocol
checks make no model/API requests.

Independent package evidence is in
`artifacts/native-install-20261025/final-review/release-audit.json`,
`portable-schema/report.json` and `mcpb-schema.json`. The reproducible audit
script there checks archive paths, exact inventories, version/source identity,
canonical resources and retained older-release digests. Protocol evidence is in
`artifacts/independent/0.3.1/portable-transport/report.json` and
`mcpb-transport-final/report.json`. Browser/fallback evidence is in
`artifacts/chatgpt-desktop-v0.3.1/report.json`,
`artifacts/chatgpt-fallbacks-v0.3.1/report.json` and
`artifacts/chatgpt-bundled-v0.3.1/report.json`.

| Final archive | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Claude Code ZIP | 35 | 91,423 | `3283febdcdceda8a06cd9902f2f62df8530fdc7dc071ce9b62b0a8e0c95077b4` |
| ChatGPT HTTP ZIP | 49 | 545,035 | `eebaf2e67fce7a92b40b4a168722adcb66a144cfb43119edb0c96d1d83e650bc` |
| ChatGPT Desktop ZIP | 34 | 456,774 | `00c928f42bd5a441f5ff0bd2e812ea815049c0fc5f2a429a8c777921557d20fc` |
| Claude Desktop MCPB | 30 | 455,814 | `5017f521e3307868cabdd64e878df42bc40d326c223d7377a44bcec2d0a2bf4f` |

All four frozen 0.3.0 archives retain their recorded digests. The failed
preflight MCPB digest remains
`f5716d1d9dcca7c84ae76ed1326ae1aa491d9a53bcc2801a335324dabec492c7`.

## Usability and palette review

This is a scoped source/fixture/installed-host inspection, not a user study or
a complete accessibility audit. Native XY plot ink uses exact CS1 by default;
CS2 requires explicit selection. Authored primary/focus accents use CS1 red;
other control surfaces inherit documented host theme variables. App chrome,
native file consent and OS Save dialogs are host-owned. No exact-palette or
full contrast claim is made for that host paint.

| Heuristic | Review status | Concrete evidence and limit |
| --- | --- | --- |
| H1 Visible status | pass | Source and fixtures expose connecting/busy/error states and preserve the last valid chart. |
| H2 Familiar concepts | pass | Actual UI uses Save image, Palette, View, Format and Edit chart data; diagnostics stay out of the initial view. |
| H3 Control and exits | untested | The host owns closing fullscreen and file-dialog cancellation; these exit paths were not newly exercised in the installed-host follow-up. |
| H4 Consistent conventions | pass | Labeled native selects and disclosure controls work in the fixture; Claude's palette and editor were exercised directly. |
| H5 Prevent mistakes | pass | New requests reset to CS1, server capabilities gate file bytes, size limits reject oversized payloads, and invalid editor tests preserve the valid chart. |
| H6 Recognition cues | pass | Palette/view values and format labels remain visible after the user opens More options. |
| H7 Efficient paths | pass | Exact-data editing and palette changes in actual Claude leave the message count unchanged; declared direct launchers remain separately untested in ChatGPT. |
| H8 Minimal content | pass | The initial component exposes the chart, Save image, More options and supported Expand; advanced JSON stays behind a second disclosure. |
| H9 Useful errors | pass | Fixtures verify malformed/unsupported requests retain valid output and report recovery text; actual host error recovery was not repeated. |
| H10 Contextual help | pass | Export/data help appears with the related controls, and the unsupported-download fixture reports the host limitation without a model call. |

Repository validation and final documentation checks are recorded by the parent
review after these notes are saved. No published example source changed, so this
follow-up does not represent a new Pages deployment.

## Documentation-only distribution 0.3.2

The final delivery is now **0.3.2**. It corrects the three MCP packages'
`INSTALL.md` instructions: the Desktop guide includes a complete direct STDIO
settings table and Save → Restart, familiar requests render without mandatory
capability preflight, and embedded previews/host-mediated exports do not require
browser access to artifact HTTP routes. The HTTP package also includes updated
source notes. Distribution manifests/package metadata carry 0.3.2.

This is a packaging/documentation revision. Release and bundle metadata
explicitly identify **`mcp_runtime_version: "0.3.1"`** for the MCP adapters;
the Code bundle records null because it has no MCP server. Native hooks,
helpers, PNG saver, shared renderer/presets, all 19 canonical skill resources,
MCP server/widget builds and runtime contracts remain byte-identical to the
final 0.3.1 distribution. The actual installed-host observations above remain
0.3.1 MCP and 0.3.0 Code observations; no 0.3.2 UI or model run is implied.

The documentation-only build command was:

```powershell
uv run --script projects/reflex-xy-plugins/scripts/build_plugins.py --output-dir projects/reflex-xy-plugins/artifacts/releases/0.3.2 --desktop
```

| Delivery archive | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Claude Code ZIP | 35 | 91,437 | `29bc085fdfffa41587a9f24252b53d77aae70e1eeb6573087e2252899fde0411` |
| ChatGPT HTTP ZIP | 49 | 546,380 | `6257a20f2a9430e3cc381dc1e805d6a2d152b1d85ff893b4aa5a870423341c4f` |
| ChatGPT Desktop ZIP | 34 | 457,825 | `8a11aff82ebe99965bb771e899475645971f26057ecd89b3c3881eea66bd9a21` |
| Claude Desktop MCPB | 30 | 456,214 | `b01f7bd37fe241c69a45245843c24ea9d74c1df3a83ccd8981e404edd981d922` |

Fresh identity and manifest/schema checks are recorded under
`projects/reflex-xy-plugins/artifacts/native-install-20261025/final-review-0.3.2/`.
The prior 0.3.1 audit and all older releases remain preserved. Byte identity
transfers the existing runtime test evidence to this delivery; no broad
protocol or model run is repeated for changed installation prose alone.

## Final repository checks

The parent ran the following after the final source/documentation changes on
2026-10-25; all passed:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script projects/reflex-xy-plugins/tests/validate_release_identity.py --extracted-root projects/reflex-xy-plugins/artifacts/releases/0.3.2 --canonical-skill skills/reflex-xy --source-project projects/reflex-xy-plugins --version 0.3.2 --report projects/reflex-xy-plugins/artifacts/native-install-20261025/final-review-0.3.2/source-identity.json
```

Pattern validation covered 1,348 canonical IDs with none above the 48-character
review threshold. The source-identity check confirmed all 19 canonical runtime
resources. Final archive/schema checks, 14/14 local documentation links and
11 documentation outputs with 23 verified primary URLs passed separately.
Scoped whitespace/diff checks passed. The public capability-atlas URL returned
HTTP 200; no example source changed and no new Pages deployment was performed.

Raw native application captures and the compact actual-host acceptance record
remain local under `artifacts/native-install-20261025/`. Actual ChatGPT painting
is verified; its installed-host button/sidebar behavior and the inaccessible
Claude Code painter remain explicit limits, not inferred successes. The
canonical skill's prior isolated cohorts and `validating` status are unchanged.

## Resumed access audit

A fresh read-only CLI audit confirmed `reflex-xy@reflex-xy-local` remains enabled
at user scope and its installed hook is byte-identical to delivery 0.3.2. CLI
authentication reports `loggedIn: false` and `authMethod: none`; this establishes
CLI state only. It does not establish the Desktop account tier or re-prove the
earlier Get Claude Code gate. The current Desktop launch opened ordinary Chat.
An attempted Code navigation was stopped by detected user input; no fresh Code
pane or Mod paint is claimed. The user's draft was left untouched.

The inspector for actual ChatGPT MCP Apps still reported no expanded sidepanel
tab. The next host checks require the user to expand the existing inline chart
and make a local Code project available. These are manual access steps, not
another installation or a model-rendering defect. The re-audit evidence is
`artifacts/native-install-20261025/claude-code-access-reaudit-20261025.json`.

The official [Desktop documentation](https://code.claude.com/docs/en/desktop)
and [command reference](https://code.claude.com/docs/en/commands) document local
plugin scope and directly typed `/reload-plugins`. That Desktop command does
not apply plugin MCP-server changes. Once a Code session exists, `/xy-chart line`
opens the native command path without an assistant completion.
