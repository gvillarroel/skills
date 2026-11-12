# Native desktop adapters — 2026-10-24

## Objective and completion boundary

Build integrated ChatGPT Desktop and Claude Desktop versions of XY while
minimizing model usage. Preserve Colorset 1 by default, explicit Colorset 2,
supplied data and progressive controls. A browser tab displaying `chart.html`
does not satisfy this objective. Installed plugin surfaces must be verified.

This project-adapter revision leaves the canonical 19-file skill runtime
unchanged. No new model-based skill forward test was run for unchanged skill
instructions. Earlier cohorts and the overall skill's `validating` status remain
separate from these deterministic integration tests.

## Implemented behavior

- ChatGPT Desktop has a new portable local plugin with root `plugin.json`,
  `mcp.json`, `skills/` and compatibility manifests. App-only
  `xy_open_chart_app` declares global/thread entrypoints and seeds a labelled
  Colorset 1 sample. The advanced data editor calls local render tools directly.
- Claude Code has a native Mod with actual XY SVG preview and native controls.
  `/xy-chart line` and Save image require no model turn. PNG saving preserves
  exact bytes and creates unique project-local exports. HTML is optional output;
  a native SVG preview does not supply XY's DOM/WebGL browser runtime.
- Ordinary Claude Desktop Chat retains a separate MCPB using MCP Apps. Remote
  ChatGPT remains a distinct HTTP package, unnecessary for local Desktop use.
- `--stdio --desktop` forces loopback with an ephemeral asset port, ignores
  inherited public/auth/domain settings, and returns 404 for HTTP `/mcp`.
  No API key, public endpoint or authentication token is required. Artifact URL
  capabilities are access controls, not model tokens.

A natural-language chart request still uses the assistant. Zero-model usage is
claimed only for the tested direct entrypoint and deterministic control paths.
Sources: [local packaging](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually),
[desktop stdio](https://developers.openai.com/plugins/deploy/desktop-only),
[direct entrypoints](https://developers.openai.com/plugins/build/extensions#sidebar-apps),
[MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui),
and [Claude native interfaces](https://code.claude.com/docs/en/plugins/mods/interface).

## Frozen release and checks

```powershell
uv run --script projects/reflex-xy-plugins/scripts/build_plugins.py --desktop --output-dir projects/reflex-xy-plugins/artifacts/releases/0.3.0
uv run --script projects/reflex-xy-plugins/scripts/stage_desktop_demo.py --release-dir projects/reflex-xy-plugins/artifacts/releases/0.3.0
```

| Archive | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `reflex-xy-claude-code.zip` | 35 | 91,424 | `6ea8a1e8c8264fe99861f04828cfed759b05ccd02572d2ec968e346601dfcd43` |
| `reflex-xy-chatgpt.zip` | 46 | 535,204 | `a86146ab7432b3979318027ba461dc32414ad2d644045ad6e20db3750a5051a8` |
| `reflex-xy-chatgpt-desktop.zip` | 34 | 455,598 | `08b3f67a1a9391539faa6d284f8f0a64c12009e954836b0704ebe9544965cdad` |
| `reflex-xy-claude-desktop.mcpb` | 30 | 454,553 | `982841459bf9f543a2b2d1d225bffc1c0b29b1ec0c0da5927084ee00b769a705` |

The frozen bundled Node server SHA-256 is
`fec89f27ead6af327bd6b58d62da1c0e86c15f9eae45052229555dfff7cae599`;
widget `34836937bdf4345cad971e2f8f573a3c09ebabc3790493b7258621239a29a6f5`;
resource `ui://reflex-xy/chart-v3.html`.

All following checks pass without model/API requests:

- ChatGPT type check/build, 6/6 boundary tests, HTTP and desktop-stdio browser
  flows. Exact data, errors, both palettes/default reset, all exports, keyboard
  and mobile checks pass. Counters: 0 model messages, 0 context updates, 0 sampling.
- Final packaged Claude CLI 2.1.302 strict scan, 9/9 native tests, 262 portable
  integration assertions and 8/8 saver checks. Controls produce 0 model calls
  and 0 submitted turns. Saved CS1/CS2 PNGs match XY's original bytes.
- Independent portable schema/complete-payload checks 10/10, official MCPB
  2.1.2 schema, both packaged manifest → bundled Node → stdio → uv paths,
  five tools, app-only controls, entrypoints, palette sequence, five downloads,
  native ink, dynamic asset origin, absent HTTP MCP and v3 CSP/resource.
- Four archive extraction/path/payload audits, exact source identity and all
  19 skill resource hashes. Extracted files remain unchanged after execution.
- Staging safety 15/15, including actual Windows symlinks, source tampering,
  unlisted files, path escapes and unrelated marketplace entry preservation.

Evidence under `projects/reflex-xy-plugins/artifacts/`:
`chatgpt-desktop-v0.3.0/report.json`, `chatgpt-browser-v0.3.0/report.json`,
`chatgpt-bundled-v0.3.0/report.json`, `claude-native-v0.3.0/report.json`, and
`independent/0.3.0/final-summary.json`. Final summaries retain exact commands,
source/package hashes, native logs, schema/stdio and post-execution audits.

## Installed-host audit and remaining work

The helper stages exact sources under `artifacts/desktop-demo-0.3.0/`, configures
absolute Node/uv and repository-contained cache/artifact paths in the two test
MCP manifests, and writes an ignored repository-local marketplace. It performs
no global installation or account writes.

| Requirement | Authoritative current observation | Status |
| --- | --- | --- |
| ChatGPT Desktop installation | Actual Plugins → Add → Add a marketplace form accepts a local folder. The form is unsubmitted; sources are staged. | Incomplete |
| Direct entrypoint and in-app painting | Declared and protocol-tested; not yet invoked in the installed host. Previous browser-tab screenshots are excluded. | Unverified |
| Claude Desktop Code Mod | Desktop 3.6556.2 is signed in. Code displays Get Claude Code and opens official documentation rather than a workspace picker. No Mod pane has painted. | Incomplete |
| Installed controls without model usage | Deterministic counters pass; installed-host actions remain to be measured. | Partially verified |

After preparing reviewable packages and independent checks, requested explicit
authorization to install into global desktop profiles and restart ChatGPT if
necessary, because the repository write scope excludes those profiles. Keep the
goal active pending authorization and actual host acceptance. Authentication,
subscription purchases and security controls are separate user actions.

This goal turn is progress: it changes deployable sources, validates native
execution, stages local packages and establishes real host activation boundaries.
It does not establish completion. Repository pattern-ID, skill, independence,
payload and local-sync checks pass. No published example changed.
