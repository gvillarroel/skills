Prepare an English plugin UI decision reference for an engineering team that
supports five products: Claude Code, ordinary Claude Desktop Chat (with the
Desktop Code tab distinguished), Codex, ChatGPT, and GitHub Copilot. They need
to know which UI methods and limitations belong to each host and surface.

Create exactly `results/cross-reference.md` and `results/cross-decisions.json`.
Use at least ten distinct canonical pattern IDs from the supplied skill. For
each selected pattern explain its input, implementation rule, failure or
fallback, evidence scope, and a concrete validation action. Cover native
controls, MCP Apps, host forms, text/image/artifact output, owned frontend
bridges, transport/deployment, capability negotiation, policy/cancellation,
and token-conscious investigation where applicable. Do not mistake support
in an extension-owned webview or protocol test for support in stock chat.

JSON must have `snapshot_date`, `hosts`, `patterns`, `historical_observations`,
`host_acceptance_verified`, and `task_empirical_tests_performed`. Use exactly
these five `host_id` values among the host rows: `claude-code`,
`claude-desktop`, `codex`, `chatgpt`, `copilot`. Each row needs `host_id`,
`host`, `surface`, `ui_method`, `limits` (array), `evidence`, `validation`, and
`sources` (at least one exact primary-source URL from the copied bundle).
Additional rows may distinguish product surfaces under the same host_id.
Each pattern needs `id`, `input`, `rule`, `fallback`, `validation`, and
`evidence`. Historical observation objects need `host_id`, `surface`,
`version`, `evidence_layer`, `result`, and `evidence`; preserve relevant
recorded successes and failures rather than calling the entire snapshot
untested. Both task-level booleans must be false: this advisory task has no
real host session, and no new empirical host test is authorized.

Use only the supplied snapshot. Do not use network, install software, open an
application, alter accounts/configuration, or call a model/provider. The
copied `skills/desktop-plugin-ui/` directory is read-only. Write all generated
files elsewhere in this workspace. Cite exact bundled source links and date
the evidence. After writing both final artifacts, execute this closed-book
source check, inspect its `passed` field, and fix any findings:

```bash
uv run --script skills/desktop-plugin-ui/scripts/check_sources.py results/cross-reference.md results/cross-decisions.json --fail-on-findings
```
