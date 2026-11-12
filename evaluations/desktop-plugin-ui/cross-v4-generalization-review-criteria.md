# Cross-v4 generalization manual review criteria

Prepared before the v4 freeze/runs on October 24, 2026. Keep the existing prompt
and preserved legacy grader unchanged. The separately frozen
`inspect_cross_v4.py` is required for v4: it checks each historical `evidence`
field and successful post-write `check_reports.py` coverage. The legacy grader
may be reported as a comparison; its coarser whole-array rule does not replace
the stronger v4 gate. These criteria guide additional factual review and never
excuse strict failures. Do not add a minimum selected-pattern count absent from
the generalization prompt.

1. **Task contract:** Both exact English artifacts exist. Preserve all requested
   JSON fields and the five applicable host IDs. Both task-level booleans are
   false; historical product tests do not become tests performed by this task.
2. **Codex scope:** Reject universal HTML, but also reject unbounded statements
   such as “Codex has no UI,” “Codex cannot display forms/images,” or “a custom
   frontend is the only way Codex can have UI.” The tested headless CLI and
   app-server observations do not exclude stock desktop/IDE mechanisms. An
   owned app-server frontend is one explicit route when the team owns that
   client, not evidence that every other frontend is impossible. Scope `never`
   automatic decline, HTML-byte transport, and the invalid `ui/initialize`
   endpoint to the tested connection/build.
3. **Evidence field placement:** Every historical observation's own `evidence`
   field contains literal `observed-working` and/or `observed-failed` plus
   explanatory scope. A label only in `result`, another row, a filename, or a
   top-level narrative does not satisfy that field. Include host, surface,
   version, layer and result. Do not label documentation-only possibilities
   as executed observations.
4. **Native versus browser:** Claude native Mods, Copilot terminal elicitation,
   host-owned forms, HTML App forms, MCPB settings, native canvases and VS Code
   extension webviews remain distinct. Image input, result-byte transport,
   native validation, actual pixels and interaction are separate claims.
   `canvases:true`, absent MCP Apps flags and `extensions:false` are not broad
   feature verdicts.
5. **Policy and recovery:** Explain accept/decline/cancel/null, match request IDs
   in an owned Codex client, preserve drafts/last authoritative state, and avoid
   waiting for an interactive form under `never`. A cancelled URL/download or
   consent acknowledgement is not authentication, navigation, delivery or approval.
6. **Historical accuracy:** Preserve Claude Code 57 native-engine cases without
   claiming terminal paint; prior Claude Desktop Chat local paint/actions/error/
   fullscreen without claiming host elicitation, remote or mobile acceptance;
   Copilot actual terminal forms and separate VS Code webview tests; ChatGPT
   setup-to-consent without claiming completed connection or widget paint.
7. **Sources and repair:** Exact primary URLs and canonical pattern IDs come from
   the copied bundle. Check both final reports with bundled machinery and
   inspect its success result. A diagnostic repair may replace every identical
   occurrence through an explicit exact URL mapping; it must not invent a URL,
   suppress unmatched findings, erase evidence, or count a repair as a clean
   run when a tool error occurred. Preserve raw attempts and grader findings.
8. **Deployments and budgets:** Distinguish local stdio, authorized HTTPS and
   Secure MCP Tunnel; keep host origin/CSP/auth/policy gates separate. Prefer
   version/schema/protocol/direct-control tests before model work, distinguish
   inference from network traffic, and do not treat a soft credit cap as a
   zero-cost guard. Future dashboard stages require named-host paint,
   interaction, relevant denial/cancellation, lifecycle and readable fallback.

Report strict, required-v4-grader, helper, citation and manual-content outcomes
separately; label any legacy-grader comparison explicitly. A final correct
artifact does not erase an earlier tool error.
Do not pool v1/v2/v3 results into the frozen v4 cohort.
