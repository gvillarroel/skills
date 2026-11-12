Our support team wants a ticket queue with search, a selected ticket, editable
priority, a chart, CSV export, and an action that asks the assistant to explain
the selection. We use Claude Desktop Chat, Claude Code in terminal, Codex,
ChatGPT, and GitHub Copilot in VS Code or terminal. Our service is currently
local stdio, but a separate remote deployment is possible. Refresh sometimes
fails, and a customer can cancel an edit. We have limited Claude and Copilot
allowances. Recommend what to share and what must vary by product and surface.

Write an English recommendation to `proposal/support-queue.md` and a compact
decision record to `proposal/host-decisions.json`. Cover workable UI methods,
important limits, transport, state/error/cancel behavior, fallback output,
capability/policy gates, and a practical validation sequence. Use canonical
bundled pattern IDs and cite at least one exact bundled primary-source URL
for each product. Avoid treating protocol metadata, SDK methods, extension
webview success, or native engine tests as proof of stock assistant paint.

JSON needs `snapshot_date`, `hosts`, `patterns` (canonical IDs or objects with
`id`), `historical_observations`, `host_acceptance_verified`, and
`task_empirical_tests_performed`. Include host rows with all five `host_id`
values: `claude-code`, `claude-desktop`, `codex`, `chatgpt`, `copilot`. Each
row needs `host_id`, `host`, `surface`, `ui_method`, `limits` (array),
`evidence`, `validation`, and `sources` (array of exact bundled URLs).
Historical observations need `host_id`, `surface`, `version`,
`evidence_layer`, `result`, and `evidence`. Keep past observed behavior
separate from current-task acceptance: both task-level booleans must be false.

This is a closed-book design task with no signed-in host session. Do not use
network, install or deploy anything, operate external apps/accounts, modify
configuration, or call a provider. `skills/desktop-plugin-ui/` is a copied
read-only resource. Keep generated files elsewhere in this workspace. Check
both completed artifacts with the skill's source checker, inspect its passed
result, and repair findings before finishing.
