Build a runnable local proof-of-concept named Queue Review for Claude Desktop ordinary Chat (not the Code tab). This is implementation, not a capability report or architecture-only plan.

Use synthetic immutable data only:
- T-104: status pending, priority high.
- T-105: status pending, priority normal.
- T-106: status closed, priority high.

Implement a stdio MCP server with model-visible `queue_open` (no arguments) and app-only `queue_filter` with required `filter` enum `all`, `pending`, `high`. Both return meaningful plain text and `structuredContent` containing `filter`, `rows` (id/status/priority), and `count`. Opening defaults to all. Validate on the server; reject invalid filters and unknown tools. Filtering does not mutate data or require model inference.

Attach one portable MCP Apps resource to queue_open. The delivered UI must be a single self-contained HTML resource, with its JavaScript dependencies bundled; no CDN, runtime network, local HTTP listener, account, database or provider. Use the standard MCP Apps bridge and host detection. Render the authoritative tool result. The interface has a labeled View selector with All tickets, Pending tickets and High priority, an Apply action and a Cancel action. Choosing a draft option alone must not filter. Apply calls queue_filter directly; Cancel discards the draft and preserves the displayed result without a server/model call. Show busy status, prevent duplicate Apply, retain the prior result and selected draft after a failed call, and offer a usable Retry action. Handle host initialization failure visibly. Use English copy, native accessible controls, keyboard focus and readable layout at 320px and 900px. Use bundled ColorSet 1 by default, exact authored palette tokens and actual contrast checks. Preserve host-owned theme/permission controls.

Deliver these exact files, with any necessary additional small source files:
- `poc/package.json`, `poc/package-lock.json`
- `poc/src/server.ts`, `poc/src/app.ts`, `poc/ui/index.html`
- `poc/dist/server.js`, `poc/dist/ui.html`
- `poc/manifest.json` using the current MCPB format and local Node stdio entry
- `poc/releases/queue-review.mcpb`
- `poc/tests/smoke.ts`
- `poc/USAGE.md`, `poc/review.json`

Use locked dependencies and bundle the server so the final archive starts with installed Node 24 and its included files, without npm install or node_modules after extraction. Preserve editable source outside the runtime bundle. Include scripts to rebuild, run tests and package the archive. The archive must contain the correct host manifest and every declared runtime file. Test a clean extraction, not only the source directory. The MCP server stdout must contain protocol messages only.

Run available meaningful checks: build, server start/initialize, tool/resource discovery and correct MIME/metadata, read UI, each filter, invalid filter and plain-text fallback; validate the host manifest/archive. The smoke test must execute the server and verify behavior. Native application installation and signed-in host UI acceptance are outside this task; do not claim them. If a browser bridge fixture is feasible, test it and report its scope honestly. Avoid handwritten one-line test programs that are hard to debug; use a normal reusable test file.

In review.json include `checks` (name/method/expected/actual/status), `heuristics` (H1-H10 with concrete interaction/finding/evidence/status), `complexity` (controls/required decisions/dependencies/runtime processes/model calls with rationale), `palette`, `host_acceptance_verified:false`, and `user_testing_performed:false`. Keep review concise and factual. USAGE must explain local loading and exact commands plus remaining host checks.

Read only this prompt and the read-only copied `skills/desktop-plugin-ui/` bundle as task context. Do not read repository sources, sibling skills, examples, prior PoCs or installed package sources. You may fetch current primary API/package documentation and install needed npm dependencies into this workspace; normal package execution is allowed. Keep every generated file, dependency cache and temporary file within this workspace, outside the copied skill. Set npm cache to a workspace path on install. Do not call any extra model/provider, change global configuration, publish, or install/activate the plugin in a desktop account. The copied skill must remain byte-for-byte unchanged.
