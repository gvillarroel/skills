Use the copied skill for ChatGPT Desktop local threads. Treat `skills/chatgpt-desktop-plugin-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Build a ChatGPT Desktop local-thread plugin for inspecting three synthetic
support tickets and their status. Include an interactive MCP App with local
filtering and a refresh action, plus useful text/structured tool output.
Create the runnable package at `deliverables/ticket-view/`, including root
`plugin.json`, root `mcp.json`, `package.json`, `server.mjs`, and component
sources. Validate the packaged runtime with a real MCP client. Do not publish,
register a public tunnel, or modify personal settings. Write
`deliverables/review.json` with `host`, `mechanism`, `tests`,
`remaining_host_checks`, and `heuristics`. Keep Desktop acceptance and optional
OpenAI APIs explicit if they cannot be exercised locally.
