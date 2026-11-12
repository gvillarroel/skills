# XY cross-host plugin acceptance contract

This project adapts the existing `reflex-xy` skill to Claude Code Mods and an
MCP Apps component for ChatGPT. The checks below distinguish executable adapter
evidence from a real signed-in host installation. A local host mock cannot prove
that a plugin was installed in Claude or ChatGPT.

## Independently checked layers

1. **Runtime package.** Build each distribution from the canonical skill's
   runtime payload. Include its instructions, focused references, deterministic
   helpers, palette data, and required templates. Exclude acceptance galleries,
   `node_modules`, virtual environments, caches, credentials, prior artifacts,
   and repository or sibling-skill dependencies. Exercise an extracted package
   from an isolated working directory.
2. **Declarative chart contract.** Parse JSON with a closed schema. Reject
   unknown factories, unknown keys, arbitrary source code, output paths, network
   URLs, non-finite measurements, mismatched arrays, unreasonable row counts,
   oversize labels, and excessive dimensions. Never evaluate text as Python or
   JavaScript. A literal markup-like label must remain data.
3. **Actual XY execution.** Render representative chart families with both
   `colorset1` and `colorset2` through the public adapter. Require parseable native
   SVG, decodable PNG with non-blank chart paint, and a self-contained interactive
   HTML export. Confirm exact dimensions, numeric source preservation, canonical
   foreground/background colors, and disclosed derived-paint modes. Compare
   palettes using the same data rather than relying on screenshots alone.
4. **MCP protocol.** Test initialization, tools/list, resources/list,
   resources/read, tools/call, error results, output schemas, UI metadata, and
   bounded resource bodies using a real client. A UI tool must advertise
   `_meta.ui.resourceUri`; its resource must use
   `text/html;profile=mcp-app`. Every tool must declare truthful read-only,
   destructive, open-world, and idempotency annotations. Resource CSP must name
   only the actual required origins. Chart computation must not fetch remote
   input or call a model provider.
5. **Artifact privacy.** Return charts in the requesting call's result or use
   owner-scoped, unguessable, bounded handles. Reject arbitrary path traversal,
   unrelated file reads, cross-session artifact reads, and shared last-chart
   state. An anonymous deployment must not be described as multi-user secure
   without an actual ownership boundary. A bearer token is a deployment secret,
   not per-user authentication.
6. **Browser behavior.** In Playwright, exercise the actual component with host
   bridge mocks and real adapter results. Cover initial, loading, successful,
   empty, invalid, and host-call error states; both palettes; switching charts;
   zoom/reset and hover where supported; download payloads; narrow/mobile and
   desktop layout; and absence of external chart requests. Check that inert
   untrusted strings cannot inject a script or create unexpected navigation.
   Native preview and interactive HTML are separate capability claims.
7. **Claude Mod contract.** Validate the manifest, hooks registration, declared
   user configuration, JSON input handling, subprocess argument separation,
   pane state scoping, surface-specific element tree, error reporting, and
   command callbacks. Exercise the registered mod with the official engine
   declaration or a narrow API mock. Require `Svg.source` to stay within the
   131,072-character host limit, with a useful fallback when exceeded. Desktop
   and VS Code receive native SVG; terminal receives only supported elements.

## Reporting boundary

Record the exact commands, package hashes, dependency versions, chart matrix,
error cases, HTTP/bridge behavior, and screenshots under this project's ignored
`artifacts/` folder. Summarize checks and remaining gaps in a compact project
note. Do not call a real host integration verified until installed and invoked
inside that host. A public HTTPS endpoint, developer mode, workspace policy, or
OAuth configuration may still be required for a ChatGPT connection.

## Primary platform sources

Checked on 2026-10-24:

- [Claude Code Mods reference](https://code.claude.com/docs/en/plugins/mods/reference):
  hooks module and manifest contract, process API, surface-specific elements,
  and `Svg.source` limit. The installed engine's generated type declaration is
  authoritative for its version.
- [OpenAI plugin reference](https://developers.openai.com/plugins/reference):
  structured output schema, MCP Apps UI resource metadata, annotations, CSP,
  and the model/component visibility of tool-result fields.
- [Add UI to your MCP server](https://developers.openai.com/plugins/build/chatgpt-ui):
  component MIME type, resource URI linkage, domain allowlists, and bridge.
- [OpenAI plugin security and privacy](https://developers.openai.com/plugins/guides/security-privacy):
  untrusted tool data, server-side enforcement, sandbox restrictions, and
  explicit nested-frame policy.

This contract is project evaluation material. It is intentionally independent
of the adapter's own self-tests and is not part of the installed skill payload.

## Independent execution record

The evaluator-owned scripts live in `../tests/`. Reports and screenshots below
are local ignored artifacts, relative to the project directory. The installed
XY environment used Python 3.14.7, XY 0.0.8, Pillow 13.0.0, and Playwright 1.64.1.

| Layer | Evidence | Observed result |
| --- | --- | --- |
| First renderer matrix | `artifacts/independent/renderer-v1/report.json` | 63/85 passed. Twenty actual preset failures exposed invalid palette lengths, radar closure, wind-rose options, logarithmic axis syntax, and animation mode. Two additional failures were evaluator handling of transparent eight-digit hex; that checker was corrected. |
| Corrected renderer matrix | `artifacts/independent/renderer-v2/report.json` | 85/85 passed: 36 presets in both palettes, two generic supplied-data charts, a markup-like literal title, and ten rejected inputs. Every successful chart had valid native SVG/PNG and offline HTML. Supplied generic measurements remained unchanged. |
| Final packaged renderer | `artifacts/independent/renderer-final/report.json` | 90/90 passed using only the extracted final Desktop package's renderer and default packaged skill discovery. Five additional rejected cases cover a Boolean version, unequal line arrays, empty pie, 500-digit integer, and unexpected theme arguments. |
| Native HTML browser | `artifacts/independent/browser-v1/report.json` | 10/10 passed at 1200 and 390 pixels: non-blank paint, actual wheel zoom, native reset, no external requests, no JavaScript errors, and inert markup-like title. |
| Portable Python source | `artifacts/independent/portable-v1/report.json` | 5/5 source-only reruns passed outside the skill and adapter directories. Generic charts in both palettes, Sankey, pie, and facets retained identical native SVG dimensions/geometry/paint and identical PNG pixels. |
| Streamable HTTP MCP | `artifacts/independent/mcp-v3/report.json` | Real server initialization, tool schemas/annotations, focused skill references, UI MIME/CSP, both palettes, all five downloads, invalid-spec error, and artifact capability rejection passed. Origin, Host, compression, and request-size boundaries rejected the corresponding probes. |
| MCP Apps component | `artifacts/independent/widget-v1/report.json` | Both protocol-host variants passed: native host download and open-link fallback. Actual palette regeneration, native SVG preview, desktop/mobile inner-canvas fit, and preserving the previous chart after a tool error passed with zero JavaScript errors. |
| Final delivery archives | `artifacts/independent/package-final-{claude,chatgpt,desktop}.json` | Claude Code ZIP, ChatGPT ZIP, and Claude Desktop MCPB all passed path, payload, and 19 local skill-link checks. All extracted file inventories and bytes remained unchanged after validation. |
| Native Claude engine | Extracted `artifacts/independent/package-final/claude` | Claude Code 2.1.302 strict plugin validation and all six shipped native engine tests passed with a project-local configuration directory. This validates engine loading and hook contracts, not signed-in Desktop rendering. |
| Claude Desktop package | `artifacts/independent/desktop-stdio-final/report.json` | Official MCPB 2.1.2 manifest validation passed. The extracted extension's actual bundled server initialized over SDK stdio with manifest substitutions and ran native XY through its shipped `uv` path in both palettes. Five downloads, absent-capability rejection, focused skill/catalog reads, and the MCP Apps resource/CSP passed. No Node dependency installation or development `XY_PYTHON` override was used. |

The first component mobile screenshot exposed a cropped native canvas despite
the outer widget having no overflow. Acceptance now waits for and checks the
inner chart canvas against its own iframe viewport. The corrected independent
mobile screenshot shows all six source points and the full wrapped title.

The OpenAI authentication review also found that a fixed bearer token must not
be presented as a ChatGPT OAuth connection. The installation instructions were
corrected: anonymous synthetic-data development and operator authentication are
separate from an authenticated ChatGPT deployment. Private ChatGPT deployment
requires a compatible OAuth gateway or supported tunnel; the package does not
implement an OAuth provider. See the [official authentication guide](https://developers.openai.com/plugins/build/auth).

Final 0.1.0 archive identities:

| Distribution | SHA-256 |
| --- | --- |
| Claude Code ZIP | `bfb301e24b52a6317174401d451059c7b4005b112fb8b999a26067cd4b9b24cc` |
| ChatGPT ZIP | `ae6b9f1793595265491ffb502322bdd78695ac575a7ac93e088895e103bd11e1` |
| Claude Desktop MCPB | `eef10f14d6845a4ac3499057fab5005d31f56557934892c9b68fd7bc22be074d` |

The shared bundled server, widget, renderer, preset definitions, and capability
catalog have identical bytes in the final ChatGPT and Claude Desktop archives;
see `artifacts/independent/final-shared-identity.json`. Their host entry points
and installation instructions intentionally differ.

Representative commands, run from the repository root:

```powershell
# Supply the 36 comma-separated names from shared/capabilities.json as <presets>.
uv run --script projects/reflex-xy-plugins/tests/validate_renderer.py `
  --renderer projects/reflex-xy-plugins/shared/render.py `
  --skill-dir skills/reflex-xy --palettes skills/reflex-xy/assets/palettes/colorsets.json `
  --presets <presets> --output-dir projects/reflex-xy-plugins/artifacts/independent/renderer-release

uv run --script projects/reflex-xy-plugins/tests/validate_native_browser.py `
  --artifact-root projects/reflex-xy-plugins/artifacts/independent/renderer-release `
  --output-dir projects/reflex-xy-plugins/artifacts/independent/browser-release

uv run --script projects/reflex-xy-plugins/tests/validate_mcp_http.py `
  --url http://127.0.0.1:8788/mcp --palettes skills/reflex-xy/assets/palettes/colorsets.json `
  --output-dir projects/reflex-xy-plugins/artifacts/independent/mcp-release

uv run --script projects/reflex-xy-plugins/tests/validate_widget_browser.py `
  --mcp-url http://127.0.0.1:8788/mcp `
  --evidence-dir projects/reflex-xy-plugins/artifacts/independent/mcp-release `
  --output-dir projects/reflex-xy-plugins/artifacts/independent/widget-release

uv run --script projects/reflex-xy-plugins/tests/package_contract.py <archive.zip>
```

The test server must already be running at the supplied address. Tests can use
an existing pinned XY Python with `--python <python.exe>` for renderer and
portable-source checks. No test installs an account connection or publishes a
server. Actual ChatGPT, Claude Desktop chat, and Claude web/mobile activation
remain untested unless a later execution record explicitly supersedes this
boundary.

## Colorset 1 default follow-up: release 0.1.1

The follow-up is a separate subject. The canonical skill, its palette reference,
and its agent prompt now require Colorset 1 for every new chart unless the user
explicitly requests or selects Colorset 2. The previous category-count exception
was removed. Claude Code commands and tool calls no longer inherit a previous
chart's explicit Colorset 2 choice. Explicit Colorset 2 remains supported.

This changes the canonical runtime guidance; the earlier 0.1.0 statement that
the skill was unchanged applies only to that historical release. Focused
skill-only Pi evidence is recorded separately by the release owner. Adapter
passes do not establish a skill-only Pi pass or satisfy the older broad cohort.

Independent evidence is under `artifacts/independent/0.1.1/`:

| Check | Result |
| --- | --- |
| `renderer/report.json` | 4/4 pass using the extracted Desktop renderer and default packaged skill lookup. Explicit Colorset 2 followed by an omitted palette yields Colorset 1 for both a preset and a generic supplied-data chart. Native SVG geometry has the expected blue/red ink; PNG, offline HTML, normalized JSON, editable source and unchanged supplied measurements pass. |
| `stdio/report.json` | The final 0.1.1 Node bundle runs through the manifest and actual `uv` path in one SDK stdio connection. Its four chart results are `colorset2`, `colorset1`, `colorset2`, `colorset1`. Actual native mark ink, normalized specs, downloads, focused updated skill instructions, default capability metadata and the UI resource/CSP pass. |
| Native Claude engine | Final extracted Code package passes strict validation and 7/7 native tests. The added test covers fresh commands/tools after Colorset 2 while preserving explicit pane palette choices. |
| Official MCPB | Final extracted manifest passes the MCPB 2.1.2 schema check. |
| `package-{claude,chatgpt,desktop}.json` | All three archives pass payload/path/link checks. All extracted file inventories and bytes remain unchanged after tests. |
| `source-identity.json` | All three packaged 18-file skill runtimes match the updated canonical source byte for byte. Renderer/presets, Code hooks, and both MCP packages' bundled server/widget match their final project sources. |

The 90-case 0.1.0 renderer/geometry matrix was retained without rerunning or
pooling it into this narrow default-policy gate. Signed-in host activation
remains untested.

| Final 0.1.1 distribution | SHA-256 |
| --- | --- |
| Claude Code ZIP | `52a4a488c8ea06c08cac1d7489f47b34fa3a8c6579e5f70f515ceed3cb66c34b` |
| ChatGPT ZIP | `1f8dc3ce649053a38be41ad7aca5f7b4573eec543bda4c10c9a5889a336689cc` |
| Claude Desktop MCPB | `03f1e7d76f5b1ca260cd72fed063d1489211f5487f5ebfd8ca7784d87974a074` |

Targeted evaluator entry points are `tests/validate_palette_default.py` and
`tests/validate_desktop_stdio.ts --default-sequence true`. The latter also
records the extension version and hashes of its manifest, server and renderer.
Use `tests/validate_release_identity.py` for canonical/runtime/source identity
and `tests/package_contract.py --extracted-root <directory>` for post-test
payload integrity. These are project evaluator tools, not installed runtime
skill resources.

## Progressive interface follow-up: release 0.2.0 acceptance plan

This follow-up changes presentation and interaction, while retaining the native
renderer, chart grammar, exported formats, supplied-data semantics, and Colorset
1 default. Treat it as a new UI subject; preserve earlier release evidence.

| User flow | Independent acceptance |
| --- | --- |
| See the first chart | MCP Apps shows the chart, a useful title, Save image, More options and optional Expand. At most three outer actions are visible. Palette selectors, view modes, format lists, source paths and technical metadata are initially hidden. Code shows its preview, Open interactive chart and More options. |
| Save without learning file formats | Save image invokes the host's image-download operation or supported link fallback with the current native PNG. It remains associated with the displayed chart after a failed update. |
| Find advanced functions | More options exposes both palettes, interactive/static views and all five existing exports. Code also exposes its preset selector, rerender and existing artifact/copy actions. Details remain accessible without becoming the first screen. Closing and reopening the section preserves the chart and chosen palette/view. |
| Use a keyboard | Enter and Space operate disclosure controls. Expanded state and its controlled region are exposed to accessibility APIs. Escape closes the options and returns focus to the disclosure button when focus was inside it. Hidden controls do not appear in the collapsed tab sequence. |
| Use a narrow screen | At 390 pixels, authored web targets are at least 44 by 44 CSS pixels, text stays readable, and outer content fits. The actual inner XY chart fits when interactive mode is requested; an outer overflow check alone is insufficient. |
| Recover from slow or failed updates | Loading is announced. The previous successful preview remains visible while a new palette render is pending and after a tool error. Errors remain understandable and the previous save/export targets remain usable. Controls do not trigger duplicate active requests. |
| Keep defaults predictable | A new model/chart request without a palette still chooses Colorset 1 after a previous explicit Colorset 2 chart. Deliberate palette changes remain available behind More options. |
| Retain native behavior | Requesting interaction reaches the real XY HTML rather than a replacement chart renderer. Existing native factories and supplied measurements still produce the same artifacts. |

Count authored outer controls separately from XY's own interaction toolbar.
Inspect the first screen visually as well as counting DOM buttons: a large
native toolbar can defeat progressive disclosure even when outer buttons are
hidden. The selected design keeps native interaction in the first preview and
hides only its toolbar through a preview-specific response. Independently test
pointer hover, wheel zoom and double-click reset in that compact preview. Show
chart tools must expose the native toolbar without navigating the iframe or
resetting its zoom. A fixed parent-message bridge may only toggle the compact
style's disabled state; reject messages from the child itself, incorrect types,
and non-Boolean visibility values. A downloaded original HTML must retain its
unmodified native content and controls; hiding the preview toolbar must not
rewrite the stored chart or remove an export.

Playwright can verify actual web focus, keyboard dispatch, computed target
sizes, visibility, native chart layout and bridge calls. Claude's native engine
tests can verify render trees and supported button/control dispatch. Native
Claude painter target geometry and real OS keyboard focus remain untested
without invoking the installed host UI; do not infer them from engine mocks.

The independent gate exercises ordinary first-view/save flows before opening
every advanced option, so it cannot pass by starting in the advanced state.

### Independent 0.2.0 execution

Final evidence is under `artifacts/independent/0.2.0/`. The accepted component
subject is widget SHA-256
`5d1e0e5a6f1d6199f594d6e7e2323ad85b0b6c4926b520ffd355320c8491dd2c`.

| Evidence | Result |
| --- | --- |
| `progressive-v4/report.json` | 2/2 complete browser flows pass: standard host download and supported open-link fallback. Each starts with the real MCP result and closed options, exercises desktop and 390-pixel mobile, and saves actual native chart files. The initial view has only Save image, More options and optional Expand. |
| Native interaction and compact response | Actual tooltip hover, wheel zoom and double-click reset pass. Showing/hiding native tools preserves the iframe URL and exact zoom ranges. Self-originated messages, wrong message types and non-Boolean visibility values cannot toggle the compact style. Stripping only the narrow toolbar style and fixed bridge reconstructs the original HTML; downloading the original before/after compact preview returns identical bytes. |
| Progressive controls | Enter/Space, expanded state, stable disclosure-button position, Escape/focus return, collapsed tab order and selected-view retention pass. Palette changes, slow-render saving, injected update error, recovery and all five native export formats remain reachable. The previous successful chart and its PNG remain available during loading and after failure. |
| Mobile paint and geometry | At 390 CSS pixels, the inner viewport and chart root are both 368 pixels; the plot canvas is 314 pixels with its axis margins. Geometry remains stable after settling, capture and disclosure changes. Visible authored targets are at least 44 pixels in each dimension. There is no outer overflow or JavaScript error. Initial desktop, native mobile and both final collapsed-mobile screenshots were manually inspected for title/axes/plot fit. |
| `stdio/report.json` | Extracted final Desktop bundle starts through its actual manifest and `uv`, without an alternate Python override. One SDK stdio connection produces explicit Colorset 2 / omitted Colorset 1 for a preset and again for a generic supplied-data chart: 4/4 native results. Native SVG ink, normalized JSON and all artifact downloads pass. The UI uses `ui://reflex-xy/chart-v2.html`, exposes the new canonical interaction reference, omits local `ui.domain`, and has the correct dynamic-origin CSP. Its widget hash matches the accepted browser subject. |
| `native-code-test.txt` | Final extracted Code package passes 8/8 native engine tests. Strict native plugin validation also passes. This confirms supported native element/control dispatch and state handling, while the native painter geometry and real host keyboard remain outside this test. |
| Official MCPB validation | MCPB CLI 2.1.2 accepts the final extracted Desktop manifest. |
| `source-identity.json` | All three packaged 19-file skill runtimes match the canonical source. Renderer/preset bytes, Code hooks and both MCP server/widget bundles match their final project sources. |
| `package-{claude,chatgpt,desktop}.json` | All three archives pass payload/path/link checks, with 20 local skill links each. All extracted inventories and file bytes remain unchanged after native/stdio execution. |

Retain `progressive-v1/` and `progressive-v2/` as pre-fix evidence, including a
blank native viewport during a hidden-view transition and mobile underfill that
simple outer-width assertions failed to detect. The adapter was changed to keep
the inactive native iframe laid out using visibility/inert state; tests now wait
for settled inner canvas geometry rather than merely counting outer controls.
`progressive-v3/` passes the corrected subject but demonstrates a capture issue:
focusing Export scrolls the parent page, so a viewport capture starts below the
chart title. The final checker records this parent scroll and returns to the
chart before its first-view capture. No failure evidence was removed or pooled
into a success count.

The 90-case 0.1.0 geometry matrix remains historical evidence; it was not rerun
for this presentation change. The canonical skill's new interaction recipe is a
separate changed runtime subject, with scoped Pi validation recorded by the
release owner. Signed-in host installation remains untested.

| Final 0.2.0 distribution | Members | SHA-256 |
| --- | --- | --- |
| Claude Code ZIP | 33 | `be134f434ee011df87bcd0ffb042e93b8a48ed4fb89a2e5d005a8334d6dbdd48` |
| ChatGPT ZIP | 46 | `f16f6f0140b890bd97391354b3d1ed01c7ec376ffbf4021ef8bcae163c01fa7a` |
| Claude Desktop MCPB | 30 | `1229bfc9d966271243cb5abbf4cc1976395d50d45a5715007b16b588d7ca2225` |

Focused evaluator entry points are `tests/validate_progressive_widget.py`,
`tests/validate_desktop_stdio.ts --default-sequence true --progressive-ui true`,
`tests/validate_release_identity.py`, and the post-test archive contract above.
