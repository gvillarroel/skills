# Pi import-review PoC acceptance

Frozen October 25, 2026 before the forward output exists. Evaluate the prompt
at `evaluations/pi-prompts/desktop-plugin-ui-poc-pi.md` on the copied runtime
bundle with strict JSON harness gates. Keep model/payload/prompt hashes and
all attempts. This is stronger state-transition generalization than the prior
read-only release-filter task.

## Independent execution

- Load the actual generated default initializer using Node 24 type stripping
  and an evaluator-owned constrained API/ctx harness; reject runtime imports,
  process/network/persistence/model calls and UI methods in no-UI mode.
- Capture `import-review` command registration and every custom-message state
  snapshot; require readable English recovery and correct schema/data.
- Inspect initial rows/revisions; commit without review must leave committed
  data empty. Review must include I-11/I-13 and exclude missing-name I-12.
- Changing I-12 to Birch creates a new draft revision and invalidates review;
  committing the old revision must fail without a commit. A fresh review and
  exact revision commit must contain all three valid rows once.
- Repeat the same commit and require no duplicate committed rows. An invalid
  ID, blank name or unknown action must preserve draft/committed state and
  offer usable recovery. A name with spaces must remain intact.
- Cancel clears only the uncommitted review, preserving current draft and
  prior committed data. Menu Escape, edit input Escape and declined commit
  confirmation must not commit or mutate draft; declined confirmation retains
  the reviewed snapshot for retry. No-UI empty invocation emits status/help.
- Exercise the same extension using actual installed Pi 1.4.0 offline RPC
  where feasible: explicit local extension path, separate artifact-local
  `PI_CODING_AGENT_DIR`, no ambient context/extensions/skills/MCP/tools, no
  session write. Require registered command, native UI request/response
  framing, exact state values, zero agent/turn events and clean process exit.

## Artifact and evidence checks

Require all five exact output paths. Verify package declares the actual
extension entry and the local load command is supported. Review test scenarios
for every prompt invariant and H1-H10 findings for real interactions. Host
native theme follows the host; default ColorSet 1 is not proof of exact native
paint. Host-paint and user-study flags remain false. Keep generated code
unchanged; put diagnostic patches in separately named artifact copies. A
passing source/stub/RPC check does not establish actual TUI focus, paint,
resize, installation or representative-user usability.

Classify failures at their owning layer (skill, sampled agent, evaluator,
harness, infrastructure or external service). Do not convert an expected
rejection into a failure or a missing test into an observed failure. The root
agent owns canonical skill repairs and fresh post-repair forward validation.
