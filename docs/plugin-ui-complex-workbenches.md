# Complex plugin UI workbenches

This is a capacity stress fixture, not the default agent interaction. User review found its global navigation, directory and repeated summaries too broad for one decision. Use the [agent micro-decision pattern](plugin-ui-micro-decisions.md) for a pending human judgment; keep these larger workspaces for explicit application requests and renderer/state validation.

This laboratory extends the [rich interface lab](plugin-ui-rich-interfaces.md)
with 96 services, 205 directed edges, 9,216 scheduled quarter-hour observations,
missing data, coordinated views and a process-local synthetic action sandbox.
All inputs are deterministic. No production system is connected.

The source lives in [projects/plugin-ui-complex-workbenches](../projects/plugin-ui-complex-workbenches/).
Run these commands from that directory:

```powershell
npm ci
npm run build
npm run serve
```

Open `http://127.0.0.1:8874/`. The loopback server serves the standalone
browser sandbox. Its state resets on reload. `artifacts/packages/incident-analysis/`
contains the separate portable MCP App: bundled stdio server, self-contained
resource, plugin manifest and MCP manifest. Its state belongs to the MCP server
process and survives a component reload until that process restarts.

## Workspaces and design decisions

- **Investigation:** a bounded directed neighborhood, exact relationships,
  aligned P95/error charts, a pointer brush, keyboard time controls, comparison
  series and the exact observations. Directory search preserves a pinned
  selection. Narrow panels use relationship buttons and a collapsed directory.
- **Fleet matrix:** a page of service rows and twelve two-hour maximum-P95 bins,
  plus a numeric table. The matrix is explicitly full-day context; an outline
  identifies the active detail interval. Keyboard or pointer cell activation
  opens that service and interval. This aggregation is a maximum of sampled
  P95 values, not a pooled percentile.
- **Reviewed plan:** frozen service ID, reduction, reason, evidence window,
  expected version and request ID. A concurrent edit produces a visible
  conflict and requires fresh review. Canceling review changes no state.
  An acknowledged commit creates one receipt; retries bind the key to the
  normalized payload. Current state can be read after an unknown response.

The form uses an explicit app action and local constraint validation. It works
in a script-enabled iframe without granting ambient form submission. Server
actions stay hidden until capability negotiation and the authoritative state
read succeed. The deliberately separate standalone browser sandbox remains
labeled as a local simulation.

## Reproduce verification

```powershell
node scripts/verify.mjs --label review-1
npm ci --prefix host-tests
node host-tests/capture.mjs --host pi --label review-1
uv run --script scripts/verify-codex.py --codex '<actual-codex-executable>' --packaged --label review-1
```

Start the preview server before the browser suite. Use a fresh label for each
native/package run. The browser suite exercises real Edge rendering at 1440,
1024, 768, 542, 390 and 320 CSS pixels, pointer brushing, exact missing values,
keyboard drilldown, cancellation, conflicts, acknowledgement, payload-bound
idempotency, the real App SDK bridge, a strict iframe sandbox, capability refusal
and actual portable MCP tools. The native capture starts installed Pi 1.4.0
through Windows ConPTY and displays its terminal cells with xterm.js, including
60x16 pagination. It does not invoke a model. Install Pi separately when absent.

The Codex verifier uses an isolated task-local home/catalog, installs the exact
package through the supplied executable, compares server cache bytes, discovers
tools and calls one directly without a model turn. It does not change personal
Codex configuration. Keep stock frontend paint as a separate result.

Raw screenshots, process receipts, MCP exchanges and extracted packages remain
under ignored `artifacts/`. The durable
[evaluation report](../evaluations/desktop-plugin-ui/complex-workbenches-20261112.md)
records final source hashes, results, retained failures and host limits. This
project is a local laboratory, not a newly published Pages example.

## Acceptance boundary

Observed new surfaces include the integrated browser in the current Codex app,
the installed Pi terminal extension, the installed Codex plugin loader/app-server,
and a protocol iframe backed by the actual MCP server. Those observations do
not establish stock ChatGPT MCP App paint, installation of this new App in
Claude Chat, Claude Code panes, or a registered Gemini Enterprise agent. The
earlier [target-host report](../evaluations/desktop-plugin-ui/target-hosts-20261112.md)
retains the separate Claude/XY evidence and account/deployment gates.
