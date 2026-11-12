# Independent efficient-delivery forward review

Review date: October 31, 2026, America/New_York; execution timestamps are
November 1 UTC. This review covers the frozen efficient-delivery guidance
revision, separately from the preceding composition study and older cohorts.

**Outcome: contract 1/1 and naturalistic 3/3 joint strict/artifact passes.**
The frozen naturalistic requirement was at least 2/3. This is a narrow
model-specific planning/guidance result, not whole-skill or live-host acceptance.

## Frozen subject and method

- Skill: `desktop-plugin-ui`, runtime profile, **40 files**.
- Runtime SHA-256:
  `0c46695ae767c116e1c5d134f76c001809f777d054e566c5e747558d21226457`.
  All four runs have identical before/after payload digests and no changed,
  added or removed skill files.
- Model: `openai-codex/gpt-6.1-sol`, medium, Pi 1.4.0, JSON strict mode.
- Criteria: [frozen delivery criteria](delivery-criteria-20261031.md).
- Prompts: [contract](../pi-prompts/desktop-plugin-ui-delivery-contract.md)
  and [naturalistic](../pi-prompts/desktop-plugin-ui-delivery-naturalistic.md).
- Exact artifacts, complete Markdown and JSON semantics, trace calls, model,
  execution errors, source-link result and payload integrity were inspected
  independently after each run was terminal. No partial output was graded.

The fresh `20261101-desktop-ui-delivery-contract-spark-1` attempt was rejected
before tool calls: the provider reported that `gpt-5.3-codex-spark` is not
supported with this ChatGPT account. It produced no task artifacts. Retain it
as a provider/access blocker; do not count it as a planning failure or pass.
The recorded per-run Sol exception preserves the frozen acceptance thresholds
and did not alter global model settings.

## Results

Every row uses the run prefix `20261101-desktop-ui-delivery-`.

| Suffix | Seconds | Strict | Independent artifact | Joint | Route rows |
| --- | ---: | --- | --- | --- | ---: |
| `contract-sol-1` | 71.359 | Pass | Pass | Pass | Not applicable |
| `naturalistic-sol-1` | 145.514 | Pass | Pass | Pass | 8 |
| `naturalistic-sol-2` | 156.600 | Pass | Pass | Pass | 9 |
| `naturalistic-sol-3` | 184.457 | Pass | Pass | Pass | 9 |

The prompt requires all seven named surfaces and unique host/surface records;
it does not require exactly seven rows. Separate ChatGPT local/remote
transports and Pi JSON/print fallbacks are valid additional records. The
independent checker therefore validates required coverage and normalized
host/surface uniqueness without imposing an unstated exact row count.
All three documents cover ChatGPT, Claude Desktop Chat, Codex desktop, Codex
CLI, Pi TUI, Pi RPC and Claude Code. Required field types and all strings and
arrays are nonempty. All route and generated-UI objects pass JSON Schema.

## Independent semantic findings

The contract selects a registered Pi command, native choice and explicit
arguments for `compact`, `standard` and `detailed`. It distinguishes TUI,
correlated RPC dialogs and noninteractive output; cancellation, stale replies
and shutdown preserve authority. It avoids a web server or model turn for a
small selection and preserves other extensions' status/keys/focus. It explains
OpenUI's authoring/docs connection separately from rendering and actions. The
exact checker command ran, its result was read, and `passed: true` with
`checked_official_urls: 2` was confirmed. This checker validates bundled URLs,
not network freshness or host compatibility.

All three naturalistic plans substantively satisfy the frozen criteria:

- Reuse the existing domain functions, stable IDs, revisions, validation and
  action contracts, with small host-specific packages/controls/bridges. They
  reuse the existing React library in compatible web views and avoid implying
  that React DOM is a native/TUI tree or that one manifest serves every host.
- Prefer predefined components for the bounded inventory workflow. They
  explain Thesys OpenUI's renderer, component registry and action requirements,
  and describe an MCP App wrapper as a proposed integration to validate.
  Agent-skill/docs compatibility does not establish a host renderer.
- Keep ordinary selection, inspection, validation, preferences, undo and
  cancellation direct. Host opening/orchestration and explicit stock
  explanations remain separate possible model work. Codex CLI routes do not
  invent a zero-turn native command merely because a domain action is direct.
- Separate transient selection/drafts, durable scoped preferences, inventory
  authority and model context. All retain input on failure, reject stale
  replies, prevent duplicate writes and handle cancellation after dispatch as
  an uncertain commit requiring reconciliation rather than guaranteed rollback.
- Preserve noninteractive explicit inputs and useful results. RPC request
  correlation, cancellation and rendering are client responsibilities. Plans
  avoid stock sidebar injection and do not universally exclude Codex rich UI.
- Keep occasional map preview distinct from persistent spatial editing.
  Supported larger views or one justified owned workspace are options; they
  do not replace the initial product or require one full app per assistant.
- Propose concrete state, package/protocol, keyboard, visual and actual-host
  checks separately, with styling ownership and H1–H10 tied to interactions.
  Efficiency measures include setup, task/recovery, bundle/dependencies,
  maintenance and inference without fabricated measurements or user preference.

Markdown and JSON agree in each run. No false claim of implementation,
screenshots, actual host UI acceptance, or measured performance was found.
The plans are thorough and longer than ideal for the request's concise prose;
this is a nonblocking editorial limitation, not a missing behavior or incorrect
route. No artifacts were repaired or rerun for this review.

## Trace and evaluator checks

All four traces begin by reading `../prompt.md` and the skill entry point.
Observed provider/model is Sol 6.1, JSON events are valid, tool errors are zero,
and every exact required output is present and nonempty. Contract uses the
exact requested checker command. The only naturalistic shell operations check
their generated artifacts/schema/links; they do not launch hosts, browse,
inspect global configuration or call another model.

Read surfaces remain within the copied runtime bundle and task outputs:
contract reads six focused references; the seven-surface plans read 14, 13
and 14 respectively. These are the selected host/distribution/state/design
references, not acceptance galleries, project artifacts, sibling skills or
outside repository context. The broader source reading is appropriate to the
requested seven-surface plan, though it is not evidence of minimum token cost.

The independent JSON Schema checker includes ten positive/negative controls
for complete coverage, allowed additional transport, a negative surface
qualifier, empty/wrong types, missing field, duplicate pair and missing route.
All controls pass. Route aliases receive manual review; the checker does not
establish host capability truth or Markdown/JSON semantic agreement by itself.

Commands used for independent verification:

```powershell
uv run --script projects/plugin-ui-exploration/scripts/check_delivery_decisions.py --self-test
uv run --script projects/plugin-ui-exploration/scripts/check_delivery_decisions.py --run-id 20261101-desktop-ui-delivery-naturalistic-sol-1 --run-id 20261101-desktop-ui-delivery-naturalistic-sol-2 --run-id 20261101-desktop-ui-delivery-naturalistic-sol-3
```

For each completed run, trace summaries use:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output projects/plugin-ui-exploration/artifacts/manifests/delivery-<case>-trace.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md
```

Naturalistic summaries also require the skill entry read and forbid normalized
example/sibling-skill paths. Strict harness policies additionally enforce the
prompt-first read surface, exact artifacts and unchanged copied payload.

Machine summaries and per-artifact byte counts/SHA-256 values are retained
under `projects/plugin-ui-exploration/artifacts/manifests/delivery*.json`;
`delivery-review-summary.json` records the independently reviewed cohort.
Raw events and generated artifacts remain in the four named ignored run
folders. No live integration, browser paint or executable interoperability
claim follows from this prose-only validation. Retain the skill's broader
validation limitations separately.
