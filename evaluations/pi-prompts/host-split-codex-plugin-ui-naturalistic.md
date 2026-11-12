Use the copied skill for Codex desktop and CLI. Treat `skills/codex-plugin-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Prepare a portable local Codex plugin that exposes a read-only build summary
for synthetic build B-42 with status passed and seven checks. Include an MCP
App summary view when a frontend supports it, and a usable text result for the
CLI. Create the runnable package at `deliverables/build-summary/`, including
root `plugin.json`, root `mcp.json`, `package.json`, and `server.mjs`. Verify
initialize/discovery/a useful direct tool and resource from a clean runtime
copy. Do not change personal catalogs, start a model turn to test discovery,
or claim stock Codex desktop/IDE painting from a protocol response. Write
`deliverables/review.json` with `host`, `mechanism`, `tests`,
`remaining_host_checks`, and `heuristics`.
