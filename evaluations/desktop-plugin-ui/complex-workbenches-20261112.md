# Complex plugin UI workbenches — 2026-11-12

This is a capacity stress fixture, not the default agent interaction. User review found its global navigation, directory and repeated summaries too broad for one decision. Use the [agent micro-decision pattern](../../docs/plugin-ui-micro-decisions.md) for a pending human judgment; keep these larger workspaces for explicit application requests and renderer/state validation.

The host split and preceding rich-interface evidence were published first in
`0eb8b262e48dfcffcbfa97988ad3f5d0a6d03573` on `main`. The subsequent laboratory
adds 96 services, 205 directed edges, 9,216 scheduled quarter-hour observations,
missing values, three coordinated workspaces and a revisioned synthetic action
sandbox. See the [run guide](../../docs/plugin-ui-complex-workbenches.md) and
[machine-readable evidence](complex-workbenches-20261112.json).

## Final acceptance scope

| Layer | Result | What was actually established |
| --- | --- | --- |
| Edge browser, model invariants, MCP transport and SDK iframe | 48/48 | Six widths (1440/1024/768/542/390/320), real pointer brush and keyboard matrix activation, exact gaps/export scope, review/cancel/conflict/acknowledgement, concurrent idempotency, actual App SDK-to-server actions in a script-only strict iframe, absent-capability fallback and no uncaught exceptions. |
| Installed Pi 1.4.0 | 6/6 | Actual TypeScript extension in Windows ConPTY, native matrix and exact observations, 60x16 pagination, all 16 quarter-hour rows reachable, repeated scope/units/legend and normal exit without a model turn. xterm.js displays the real terminal cells. |
| Desktop-bundled Codex 0.167.0-alpha.3.2 | 10/10 | Task-local portable marketplace installation, exact server cache bytes, real app-server discovery and direct tool result without a model turn or personal configuration changes. |
| Current app's integrated browser | Observed | Actual narrow-panel review, version-1/version-2 refusal, fresh review, one acknowledged plan at version 3 and subsequent current-state read. This is the standalone browser-local sandbox, separate from inline MCP App paint. |
| Isolated skill-only forwards | 7/7 strict | One contract case for each comparison/host UI bundle, exact `acceptance.json` and `review.md`, valid event JSON, observed requested model, zero tool errors, clean read surface and unchanged copied skill. Planning output is not actual-host UI acceptance. |

The browser sandbox resets on reload. The MCP sandbox is authoritative within
its server process and resets when that process restarts. Neither route connects
to production. Their authority and persistence are labeled independently.

## Visual and interaction critique

The wide investigation uses a selected service, bounded direct topology and
aligned charts instead of attempting to label the entire fleet simultaneously.
Per-column node capacity prevents overlapping labels. Direct-edge counts and
the exact full relationship list expose the omitted scope. At narrow allocated
widths, relationship buttons replace the map; collapsing the directory keeps the
selected context near the top. The directory still searches all 96 services.

The fleet matrix encodes maximum sampled P95 per two-hour bin with a numeric
table. Its full-day context is explicit and the shorter active interval is
outlined. This prevents the overview from appearing to obey a filter it does
not use. The charts share UTC time, keep latency/error units separate, preserve
nulls as gaps, identify comparison style, and expose From/To controls beside
pointer brushing. End-of-day axes say `24:00`.

Review freezes identity, values, evidence interval, expected version and request
ID. A conflict preserves the draft and requires another review. Cancellation
before commit causes no write. Idempotency binds normalized payloads and is
checked again after the asynchronous boundary. Pending commits are not presented
as canceled when a dialog closes. A current-state read supports reconciliation
after an unknown response. In an embedded App, controls are hidden until server
capability negotiation and the initial authoritative state read succeed.

The first actual narrow screenshots and Pi captures were inspected manually.
The final native source repeats the exact-view time scope and metric units on
every page, and aligns the matrix's four-hour labels with two-hour cells. The
strict iframe found that ambient form submission was blocked despite scripts
being allowed. An explicit app action with local constraint validation repaired
the artifact without expanding sandbox permissions.

## Retained failures and corrected trials

- Initial browser run: the pointer brush test used an offscreen target.
  Corrected harness scrolling; the artifact was unchanged for that repair.
- `bridge-final`: ambient form submission blocked the review action in the
  strict iframe. Corrected the artifact and reran the full suite as
  `sandbox-form-fix` (48/48). The fixture also resets the prior document realm,
  preventing a detached previous observer from reporting unrelated null-node
  errors after `setContent`.
- Pi `complex-final`: 5/6 after a literal legend assertion still expected the
  older visible wording. Updated that evaluator literal; unchanged native
  source passed 6/6 as `complex-verified`. The preceding 6/6 capture remains
  available, with its later visual improvements distinguished.
- The initial whole-repository bundle audit was invalidated by seven source
  whitespace edits made during the audit. It is not counted as a pass. Frozen,
  scoped source/runtime/full audits are used for the publication gate instead.

All raw failures, screenshots and reruns remain under ignored project artifacts.
Do not pool these focused runs with the preceding frozen UI evaluation cohort.

## Skill-only validation

All seven changed bundles include their own compact
`references/complex-workspaces.md`, directly linked from their entry point.
The reusable input contract, reconstruction steps, host adaptation, failure
rules and acceptance workflow require no sibling skill or project source.

Each run uses the recorded model exception
`openai-codex/gpt-6.1-sol --thinking medium` after the earlier account-specific
Spark rejection. For each `<skill>` in the comparison router and six host
bundles, the command was:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/complex-ui-<skill>-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output acceptance.json --expect-output review.md --run-id 20261112-complex-ui-<skill>-sol-1 --timeout-seconds 360
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261112-complex-ui-<skill>-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

Independent document checks confirmed the five requested top-level JSON fields
and the review length limit. Manual review inspected actual host mechanisms,
half-open UTC/null semantics, explicit context/detail scope, frozen reviews,
version conflicts, payload-bound idempotency and unknown-result recovery. These
are contract cases with one repetition each; they establish no generalization
rate or deployment-wide certification. All seven skills remain `validating`.

## Remaining host gates

The new server was not added to personal Claude Desktop configuration. Earlier
Claude Chat/XY painting remains separate. The existing Claude Code login and
Desktop Code onboarding gates remain. No registered Gemini Enterprise target
agent was supplied; the earlier API-disabled result is bounded to the configured
project, and no cloud settings were changed. Current app IAB screenshots and
portable Codex loader checks do not establish stock ChatGPT inline App paint.

Repository checks run in the user worktree and in the clean main publication
worktree. Unrelated preserved semantic-skill edits cause authoring-route failures
in the user worktree; they are excluded from this publication and are not
silently repaired. Pattern IDs, independence and payload checks pass there.
The clean publication must pass all four gates, frozen bundle audits and explicit
diff checks before its commit. No new Pages example catalog entry is introduced.
