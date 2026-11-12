Recommend a plugin UI for a media-review queue using the synthetic lab records
below. Staff search assets, select details, stage/save/cancel priority edits,
inspect a status chart, refresh/recover, export selected records and use
Explain selection. Use ColorSet 2 for authored paint. Preserve `M-204`, `high`,
`pending` and `E_INVALID_PRIORITY`.

All records concern the fictional Lab UI Host 1.4.2 fixture. They are task
inputs, not real assistant-host observations or tests performed in this task:

- Inspected `panel.ts:18` contains the chart mount and an export button handler.
  There is no receipt showing either handler executing.
- `Lab Extension Contract section 2` documents an extension-owned HTML panel.
- `Lab Extension Contract section 4` explicitly prohibits microphone access.
- A human reviewer reported seeing a preview chart; its capture build is unknown.
- A real lab input-validation probe expected E_INVALID_PRIORITY for `urgent`;
  its receipt records that error and saved priority `high` unchanged.
- Another lab form probe accepted a Boolean false value; expected false and
  actual false match. No cancellation was requested.
- A save probe expected committed revision 12, but the receipt records
  E_UNAVAILABLE and unchanged revision 11.
- The mobile smoke test was not run because its device was unavailable.
- A reconnectable preview is proposed only if the session bridge and durable
  store are available; no checks of these prerequisites are provided.

Create exactly `proposal/recommendation.md` and `proposal/recommendation.json`.
Give a useful delivery route, prerequisites, fallback, state ownership across
reload/reconnect/failure, concrete English save/cancel/Explain/export/error
copy, all ten Nielsen IDs/labels with checks, and exact selected palette paths.
Validate any published paths/contrast arithmetic with bundled machinery.
Separate authored paint from host controls and identify remaining acceptance
checks. Do not build a renderer or claim a user study.

Use typed `evidence_records` derived by the skill workflow for every factual
claim used. JSON also needs `recommendation`, `state_plan`, `authored_ui_copy`,
`palette_bindings`, `heuristics`, `sources`, `host_acceptance_verified:false`
and `task_empirical_tests_performed:false`. Link factual recommendations with
`evidence_ids` and reuse the helper-rendered ledger table in Markdown. Preserve
the human report without promoting it to automated interaction acceptance.

Use only this prompt/read-only `skills/desktop-plugin-ui/`; write elsewhere.
Stay offline: no provider/model call, account/sign-in, host/app/global action,
installation, network, prototype or UI test. Inspect typed-mode checker
results for both final outputs and repair until clean. Source locators from
the supplied lab records can be cited without inventing public URLs.
