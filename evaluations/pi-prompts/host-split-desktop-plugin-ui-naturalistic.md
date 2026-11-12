Use the copied skill for a cross-host assistant UI comparison. Treat `skills/desktop-plugin-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Plan a small release-inspection tool spanning Claude Desktop Chat, Claude
Code, Pi TUI and RPC, Codex CLI and desktop, ChatGPT Desktop local threads,
and Google Cloud Gemini Enterprise. Use one shared release/domain contract
and small host adapters. A release has ID, status, and checks; users can inspect
and filter it without model inference. Explain the package, transport, UI
mechanism, fallback, conditions, and validation for each actual surface.
Write `deliverables/plan.md` and `deliverables/adapters.json`. The JSON must
have an `adapters` array whose records contain `host`, `surface`, `mechanism`,
`validation`, and `remaining_host_checks`. Keep the blueprint proportionate;
do not implement, install, register, or deploy the adapters. Distinguish
source declarations from executed host acceptance.
