Review a proposal called "Cloud Code / Cloud Desktop". The brief does not
identify those products, and nobody can clarify them during this review.
Its author expects one React DOM iframe to work in native Claude panes,
Codex CLI, ChatGPT, and GitHub Copilot. They plan to infer support from SDK
method names, send `ui/initialize` directly to Codex app-server and `ui/show`
to Copilot ACP, treat cancellation as permission, use native file: links,
assume fullscreen and device permissions are universal, and call the product
production-verified after a protocol resource read or browser fixture passes.

Write `review/cross-boundaries.md` and `review/cross-status.json` in English.
Assess each assumption at the correct surface, propose conditional workable
alternatives, and identify the next check. Preserve ambiguity without blocking
the review or inventing a Cloud API. Explain documented exclusions precisely;
do not turn a failed method or untested frontend into a blanket statement that
an entire assistant has no UI, forms, images, canvases, or plugin support.

JSON needs `product_confirmed`, `host_acceptance_verified`,
`task_empirical_tests_performed`, `assessments` (objects with `topic`, `status`,
`reason`, `fallback`, `evidence_layer`, `validation`, `sources`), `patterns`
(canonical bundled IDs or objects with `id`), and `historical_observations`
(objects with `host_id`, `surface`, `version`, `evidence_layer`, `result`,
`evidence`). All three booleans must be false. Retain historical empirical
successes and failures within their actual scope, with exact bundled source
links and the snapshot date; this review performs no new host acceptance test.

This is a closed-book advisory task. Do not use network, install or open apps,
alter accounts/configuration, or call providers. The copied
`skills/desktop-plugin-ui/` directory is read-only. Write outputs elsewhere
in this workspace. Check both completed artifacts using the bundled source
checker, inspect its passed result, and fix any findings before finishing.
