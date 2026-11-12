# Coordinated complex workspaces

Use these recipes for explicitly requested full workspaces or renderer stress
fixtures. Agent interactions default to a single decision; read
[micro-decisions.md](micro-decisions.md) before expanding the surface. Recreate the behavior from this compact contract; no project or
example source is required. Read the host section before choosing controls.

## Shared data and linked views

Define stable service and edge IDs. An observation contains an ordered UTC
timestamp, nullable P95 in ms and nullable request-error percentage. Edges
contain source, target, relationship type, rate and rate unit. A useful stress
case has 96 services, 96 quarter-hour samples per service, missing observations
and several hundred directed edges. Keep these as test inputs, not size limits.

Use one selected ID and one half-open interval `[start, end)` for the detail
charts, exact values, summaries and scoped export. Keep an explicit pinned
selection when directory filters hide it. Separate editable drafts from this
selection and authoritative server state. Preserve identity and keyboard focus
after redraw; if a focused relationship disappears, focus the selected heading.

Show a bounded direct neighborhood and visible/total edge counts. Limit nodes
by measured space on each side, not only total count. Preserve the full exact
relationship list and directory search. Use a stable layered drawing with arrow
heads; distinguish event/request units. Do not interpret call fan-out as a
conserved Sankey flow. At a narrow allocated width, replace the drawing with
readable relationship buttons instead of scaling SVG text down.

Plot P95 and error percentage on separate labeled axes, aligned in time. Keep
comparison identity and stroke style explicit; use consistent domains for the
same quantity. Retain missing values as line gaps and exact table entries.
Label midnight at the end of the stated day as `24:00`, or include its next-day
date. Provide From/To controls alongside any pointer brush.

For a dense fleet, use a paged service-by-time matrix with a numeric table.
State the aggregation: maximum of sampled P95 values is not a pooled P95.
Keep a full-day matrix explicitly labeled as context when details use a shorter
window, and outline the active interval. Never imply that the context overview
uses the detail filter. A missing bin needs its own symbol or label.

## Frozen review and acknowledged actions

Review a frozen target ID, normalized values, reason, evidence window, expected
revision and request ID. Do not let later selection changes retarget the draft.
Canceling review causes no write. Compare the revision atomically at commit;
retain the draft and require another review after a conflict.

Bind an idempotency key to the normalized reviewed payload. Recheck it after
asynchronous work: simultaneous identical requests must commit once, while a
different payload using the same key must fail. Keep an acknowledged receipt
and a way to read current authoritative state. A lost response is an unknown
outcome, not proof of rollback; reconcile before creating another request.

Promise cancellation only where the backend can honor it. A noncancelable
commit may temporarily disable closing its progress dialog, with clear pending
copy and bounded recovery. Do not label a closed dialog or ignored late response
as a canceled write. Sandbox plans must clearly state their synthetic authority
and whether state survives reload or process restart.

## Reproduction and acceptance

For an HTML App, use explicit app actions with local constraint validation for
review. Do not depend on ambient HTML form submission or navigation: a sandbox
may allow scripts while blocking forms. Verify the real SDK bridge under that
restriction, and keep server actions hidden until capability negotiation and
the authoritative state read succeed.

Implement a shared domain layer, then the host adapter, its capability fallback
and keyboard route. Validate source invariants, actual tool transport, browser
or native renderer, and the signed-in target separately. A local preview,
protocol iframe, installed plugin and stock-host paint are distinct results.

Exercise 1440, 1024, 768, actual panel width, 390 and 320 CSS pixels where a web
surface exists. Measure labels at their final rendered scale. Scope horizontal
scroll to numeric tables, preserve the selected context, collapse secondary
directories on narrow views, and provide an empty-filter recovery. Capture
wide and narrow screens, an actual matrix drilldown, stale-version refusal,
cancel-before-commit and an acknowledged success. Fix observed failures before
claiming acceptance. An offscreen pointer test must scroll its target into view;
classify harness failures separately from artifact defects and retain both.

## Host adapter

Use an MCP App iframe for custom linked graphs and charts, plus useful text
tool results. Feature-detect server tools before exposing mutations and reconcile
receipts through the connected server. A browser page or an installed package
does not establish ordinary Claude Chat paint. Verify the actual signed-in Chat
surface and distinguish it from the Desktop Code tab.
