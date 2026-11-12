# Codex plugin PoC independent acceptance

Frozen October 25, 2026 before generated outputs. Prompt:
`evaluations/pi-prompts/desktop-plugin-ui-poc-codex.md`. Baseline subject is the
26-file desktop-plugin-ui runtime `ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7`.
Use existing per-run Sol 6.1 model exception after recorded Spark rejection.

The discovery pass tests one complete contract PoC, not a universal release.
Keep strict harness, independent behavior/package checks and manual review
separate. Preserve all failed attempts and generated files unchanged; make
diagnostic fixes only in labeled copies, then repair the skill before a fresh
forward generation. A corrected copied output is not a forward-test pass.

## Observable checks

- All ten exact required artifacts exist; the initializer/model/read surface
  and copied skill hash satisfy the strict runtime harness.
- Parse portable plugin and MCP manifests against their primary schemas where
  available. Resolve the declared bundled server from the plugin root; reject
  accidental checkout absolute paths, missing files or runtime npm dependencies.
- Parse marketplace, required policy/category and root-relative local path.
  The referenced plugin stays inside its own isolated workspace.
- Start a fresh copied plugin directory through its declared stdio command.
  Independently initialize MCP, discover both tools, validate schemas and call
  all three list filters. Require exact row IDs/states and concise useful text.
- Invalid view must be rejected without a normal success or silent default.
- With form capability, script accept/decline/cancel. Accept returns only the
  requested rows after true confirmation; false confirmation cannot commit.
  Decline/cancel are distinguishable and preserve direct list fallback.
- Exercise installed Codex app-server direct tool calls in an isolated home
  and synthetic ephemeral thread where possible, with no model turn; check
  `never` automatic decline versus supported callback handling. Keep direct
  MCP testing distinct from actual plugin-loader discovery and UI paint.
- Inspect native CLI marketplace/plugin discovery in task-local configuration,
  if supported, without a global install or credentials. A documented but
  untested loader stays untested; a real loader failure remains a failure.
- Independently inspect H1-H10 findings, task-first control count, deterministic
  normal actions, safe cancel and actionable errors. Host-owned theme scope,
  real UI paint and user-study claims must be honest.
- Read the generated usage and rerun the declared build/test/extracted-start
  route where possible. Preserve generator tool errors as strict failures
  even when final independent code execution passes.

Use primary source evidence for APIs, packages and packaging; use native/tool
execution evidence for the exact tested runtime. Do not use the generated
review's own assertion to grade acceptance.
