---
name: desktop-plugin-ui
description: Creates, improves, and validates plugins and interactions for Claude Desktop, Claude Code, ChatGPT Desktop, Codex, and Pi extensions; also compares GitHub Copilot UI capabilities. Use for plugin authoring, native controls, MCP Apps, minimal architecture, Nielsen usability review, and host compatibility diagnosis.
---

# Assistant Plugin UI

Identify the exact assistant and frontend, select the simplest supported UI
mechanism, and build or improve the requested plugin. For comparison requests,
explain its tested limits. Investigate or install only within the requested scope.
Read [assistant-surface-matrix.md](references/assistant-surface-matrix.md) for
cross-assistant questions; read only the relevant host reference afterward.

## Build and iterate

For authoring requests, use [plugin-authoring.md](references/plugin-authoring.md)
and only the selected host route. For Pi, use
[pi-extensions.md](references/pi-extensions.md). Produce runnable source and
the requested package or configuration with exact paths, setup commands and
relevant tests; a capability report alone does not complete a build request.
For Claude Code or Desktop Code native plugins, start with the tested starter
and authentic event/test contracts in
[native-authoring.md](references/native-authoring.md). Registration uses `name`;
command execution uses `command`. Do not invent matching test payloads.
For portable OpenAI packages, use
[portable-packaging.md](references/portable-packaging.md) to validate both
schemas, the extracted bundle and the actual executing loader version.
For MCP Apps browser checks, use
[browser-validation.md](references/browser-validation.md) for a real bridge
fixture, safe script evaluation and keyboard tests in a sandboxed iframe.
For Pi editing or committing drafts, use
[pi-stateful-actions.md](references/pi-stateful-actions.md) and its guarded
intent primitive. Capture authority before native dialogs and recheck it
before applying an intent so a late reply cannot overwrite newer state.
Start Pi readiness checks with
`python <bundle>/scripts/probe_runtime.py --host pi` and inspect its JSON.
This [version-only probe](scripts/probe_runtime.py) checks the required host
and Node runtime; direct Pi TypeScript loading needs no compiler probe.
For a requested multi-host blueprint, use that reference's compact planning
route: share domain/state contracts and review once, then describe small host
adapters. Read deeper catalogs only for unresolved host questions.

Use [interaction-quality.md](references/interaction-quality.md) to define the
user outcome, choose controls, separate deterministic actions from inference,
and review essential states. Prefer an existing native control and a local
command when they satisfy the task; justify each extra service, dependency,
configuration decision or custom surface. Preserve a useful text fallback.
Keep each host adapter small; do not invent a universal plugin manifest.

Implement one complete path, exercise success and relevant invalid/cancel/
recovery paths, fix observed problems, and recheck affected behavior. Compare
task completion and recovery with steps, decisions, required inputs and setup
burden before claiming a simplification. Apply H1-H10 to actual interactions;
do not stop at a checklist or add controls merely to satisfy a heuristic.
Finish with tested artifacts, remaining host checks, and concrete limitations.
Keep review notes proportional; generate formal evidence reports only when
the task requires them. Never substitute a lower-layer test for actual host UI.
Build validation notes, including a requested `review.json` with checks and
heuristics, use the requested schema directly. Do not add a second ledger or
Markdown research report merely to describe build tests. Use the formal report
workflow when the requested deliverable is a capability or evidence study.

## Identify the actual surface

Use explicit product and session context first. Treat “Cloud Code/Desktop” as
Claude only when context establishes that intent. Otherwise ask one focused
product question while continuing source review, or state a provisional Claude
assumption. Never invent a Cloud Desktop API. A model provider or model name
does not identify the harness, renderer, account, or permissions.

| Target | Appropriate mechanism | Important boundary |
| --- | --- | --- |
| Claude Desktop ordinary Chat | MCP Apps tool plus sandboxed HTML UI resource | Core MCP, skills, and text tool results alone do not establish interactive UI. |
| Local server installation/settings | Desktop Extension `.mcpb`, typed configuration | A packaging/configuration form is separate from the runtime MCP App. |
| Claude Desktop Code tab / Claude Code / Claude VS Code | Native Mods surface tree and host APIs | Element and prop support differs between these three surfaces. |
| Codex CLI / app-server / desktop / IDE | Tools, content and negotiated elicitation; frontend-owned rendering | Protocol receipt or a JSON event does not prove a visible iframe or form. |
| GitHub Copilot CLI | Negotiated experimental extension UI | Real terminal forms work in the tested build; bare SDK consumers need callbacks. |
| Copilot in VS Code | MCP Apps, native extension webviews, or preview canvas | These are separate mechanisms with different host and policy restrictions. |
| Pi extension | Native extension commands, tools and `ctx.ui` controls; custom TUI only where supported | Distinguish TUI, RPC, JSON and print modes; `hasUI` alone does not establish custom terminal UI support. |
| Standalone browser | Web application or exported HTML | Browser success does not prove integration with Claude. |
| Claude artifact workspace | Host artifact capability | It is not a general plugin API for inserting host panels. |
| ChatGPT Desktop local thread / ChatGPT remote connection | Desktop-only plugin with local stdio, or MCP Apps over supported remote transport | Choose the actual local/remote route. Local success does not establish remote deployment or other thread support; keep OpenAI extensions out of Claude adapters. |

For transport, installation, settings, and cross-host differences, read
[distribution.md](references/distribution.md). Do not infer support for Cowork,
headless execution, mobile, or another host from a Desktop result.

## Select patterns and methods

Read only the reference matching the request:

- [capability-offerings.md](references/capability-offerings.md): current
  Copilot/Codex feature choices, version splits, fresh probes and access gates.
- [chat-patterns.md](references/chat-patterns.md): ten patterns for fallback
  output, cards, carousels, fullscreen, forms, charts, files, responsive theme,
  progressive disclosure, and asynchronous state.
- [bridge-patterns.md](references/bridge-patterns.md): six patterns for resource
  registration, tool calls, context and messages, mode negotiation, CSP, and
  capability-dependent browser features.
- [claude-host-limits.md](references/claude-host-limits.md): measured native
  element restrictions, numeric boundaries, authentication, and zero-model tests.
- [claude-chat-live.md](references/claude-chat-live.md): actual Desktop Chat
  installation, iframe paint, app-only interaction, failures and display modes.
- [codex-limits.md](references/codex-limits.md): CLI/app-server/desktop/IDE
  distinctions, form negotiation, approval policy, and content channels.
- [chatgpt-limits.md](references/chatgpt-limits.md): ChatGPT MCP Apps, optional
  host extensions, deployment, state, CSP, and live-test boundaries.
- [copilot-limits.md](references/copilot-limits.md): actual terminal forms,
  ACP limits, VS Code webviews, MCP Apps and preview canvases.
- [native-patterns.md](references/native-patterns.md): native panes, input and
  selection, SVG/image previews, links/copy actions, and lifecycle boundaries.
- [host-prompts.md](references/host-prompts.md): host-rendered elicitation forms,
  URL consent, and native render-site customization beyond custom panes.
- [evidence-and-probing.md](references/evidence-and-probing.md): dated findings,
  negative probes, source inventory, and a repeatable investigation method.

Use the canonical IDs in the selected reference; existing `claude-ui-*` IDs
remain stable, with `codex-ui-*`, `chatgpt-ui-*`, and `copilot-ui-*` additions. For
each selected pattern, provide its trigger, input/data contract, implementation
rule, failure/fallback rule, and a concrete validation action. These patterns
are decision recipes, not an assertion that every host implements every API.

Distinguish host requirements, documented design guidance, and inferred
engineering recommendations. For example, Claude's recommended inline action
count is design guidance; a sandbox CSP denial is an execution restriction.

## Apply usability and color

For every UI recommendation, design, or audit, use
[usability-and-color.md](references/usability-and-color.md). Apply all ten
Nielsen heuristics to the selected interaction and record concrete checks,
findings, fixes and evidence; explain any nonapplicable check. Heuristic review
does not establish user testing or host acceptance.
For implementations, connect these checks to the interaction and iteration
loop in [interaction-quality.md](references/interaction-quality.md).
For exact palette paths or published contrast numbers, use the bundled
[design_values.py](scripts/design_values.py) as described in that reference.

Use bundled **colorset1 by default**. Use **colorset2 only when explicitly
selected for the current deliverable**. Bind authored controls, charts, states
and exports to exact tokens from the chosen palette. Check actual foreground/
background contrast and redundant status cues; palette membership alone is
insufficient. Preserve host-owned chrome, permission/elicitation forms, native
themes and accessibility overrides. Report the styling boundary instead of
inventing CSS support, terminal truecolor or palette compliance for host paint.
For MCP Apps, record authored iframe paint separately from surrounding host
chrome; an iframe is not wholly `host-mapped` because the host supplies theme
context. Preserve requested heuristic IDs and labels verbatim in exact schemas.

## Write component content in English

Write every generated component and all authored visible and accessible copy
in English: titles, controls, placeholders, tooltips, chart labels, sample
content, loading/empty/success/error/cancel states, validation, notifications,
help and exports. Apply this to HTML, native nodes, terminal controls and text
fallbacks, plus reports and code comments. Set the authored document language
to `en` where supported. Inspect runtime states and accessible names, not only
the source files; translate legacy display copy when adapting an existing UI.

Preserve API identifiers, protocol values, proper names and source records.
Keep source text separate from translated display copy when needed. Host-owned
chrome and dialogs follow the host's locale; do not claim to have translated
them or change account/OS language settings to satisfy authored-copy checks.

## Report capability honestly

Attach one or more evidence labels, with scope:

- `documented`: primary documentation or inspected source declares behavior;
  identify which basis and keep runtime execution separate.
- `observed-working`: a named executed check matched its stated expectation
  in a named runtime, version and surface, including an expected refusal.
- `observed-failed`: a named executed check did not meet its expectation.
- `conditional`: depends on negotiated capabilities, policy, plan, or platform.
- `untested`: no relevant execution result is available.
- `unsupported`: an explicit contract excludes the behavior on that surface.

For evidence reports, follow [report-authoring.md](references/report-authoring.md)
and use [evidence_ledger.py](scripts/evidence_ledger.py) to derive typed
`evidence_records` before writing recommendations. Give each atomic claim its
basis, host, surface, version and layer. Only an executed check has an action,
expected result, actual result and pass/fail outcome. Source inspection,
human reports and unperformed checks must not acquire an executed outcome.
Use the derived labels verbatim; do not handwrite a second classification.
An absent test is `untested`, never a failed test. A handler declaring an API
call is source evidence, never proof that the request ran.

Keep legacy `historical_observations` only for executed observations when an
existing contract requires that array. Put source declarations, user reports
and not-run checks in typed records instead of forcing them into observed
labels. Task-level acceptance flags describe the current task, not bundled
history. Keep user-reported visibility distinct from agent-verified controls.

A protocol fixture, native engine, ordinary browser, real extension host,
terminal painter, and signed-in assistant chat are different evidence layers.
Never promote a lower-layer pass to a higher-layer UI claim. Keep historical
observations separate from acceptance of the current task. SDK methods, mode
enums and advertised capabilities do not establish visible rendering. Distinguish
account, policy, transport and harness blockers from product exclusions.
An observed custom-client dashboard is one available route. When stock Codex
desktop/IDE painting is untested, report it as `untested`; do not describe an
owned frontend as the only way to provide a dashboard or UI.

## Investigate and maintain

1. Read the smallest relevant bundled reference. Treat its dated findings as a
   baseline; recheck official sources before giving current installation or API
   advice. If browsing is unavailable, disclose the snapshot date.
   Copy citation URLs exactly from the source; do not reconstruct domains or
   paths from memory. Preserve fragments when linking a specific method.
   Use `uv run --script scripts/check_sources.py --list-sources` from this
   bundle when exact source links are needed; Python 3.11+ can also run it.
2. Inventory host/build/OS, Chat or Code surface, extension version, local or
   remote transport, SDK major versions, account controls, and negotiated
   capabilities. Avoid collecting credentials or unrelated account content.
3. Start with version/help, schema/native tests, protocol initialization, and
   direct local controls. Avoid model calls for setup, buttons or cancellation.
   Record inference counts separately from other network activity. If a model
   call is needed, use a minimal fresh session and the user's budget constraint.
   Reproduce one useful success and one relevant failure with synthetic data.
   Use the SDK/server and a sandboxed browser fixture where possible; use the
   native Mod test engine for native nodes. Keep app/account installation and
   external writes within the user's authorized scope.
4. For missing UI, diagnose enabled tools, resource URI, MIME, resource fetch,
   initialization, result delivery, CSP, host policy, then layout/paint. Record
   the first failing layer rather than declaring the entire mechanism broken.
5. Record exact command, environment, versions, expected/actual result, evidence
   layer, timestamp, and artifact paths. Retain failed attempts. Promote only
   the bounded reusable finding into the appropriate reference.

For formal evidence/capability reports, follow the completed-output and URL
repair checks in [report-authoring.md](references/report-authoring.md). Check
both artifacts with `check_reports.py --require-evidence-records` and inspect
its typed-record coverage. A clean checker does not establish factual truth
or host acceptance. Keep inputs and scratch files inside the task workspace.

For authoring, lead the response with created artifacts, behavior and tests.
For comparisons, lead with the recommended surface and method, then selected
patterns, scoped evidence, source links and remaining host checks. Keep plain
text usable when UI is unavailable. An information-only request does not
authorize OS opening, global configuration changes, publication or messaging.
