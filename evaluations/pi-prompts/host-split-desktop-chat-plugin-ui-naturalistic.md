Use the copied skill for ordinary Claude Desktop Chat. Treat `skills/desktop-chat-plugin-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Build a small read-only inventory connector for ordinary Claude Desktop Chat.
Use three synthetic items with stable IDs, names and stock counts. The user
should see the items, filter in the interface, and recover from a failed refresh.
Produce a runnable local MCP server and actual MCP App resource at
`deliverables/connector/`, including `package.json`, `server.mjs`, and the
component's source. Include a real protocol test and run it. Return useful
text/structured results as well as UI. Do not install in the personal Desktop
account or expose a public endpoint. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
Record exact setup/test commands; keep live host checks separate from fixtures.
