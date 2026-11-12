# Cross-v4 generalization validation

Date: October 24, 2026, America/New_York; UTC logs are October 25.
Skill: `desktop-plugin-ui`. Model: `openai-codex/gpt-5.6-luna`, under the
continuing recorded model exception. The task prompt was unchanged.

**Result: strict 3/3, required v4 structural/report-checker gate 3/3, manual
content review 1/3. This cohort is not an aggregate release pass.** Run 1
mislabels an explicitly unexercised Copilot paint action as `observed-failed`.
Run 3 makes an overly exclusive Codex `on-request` claim and also adds a failure
label to ChatGPT setup without a failed completion attempt. Run 2 is the clean
generalization result. Preserve all three; do not pool earlier v1/v2/v3 cohorts,
reroll failures, repair artifacts externally, or reinterpret the frozen criteria.

## Frozen contract

All three runs used the 16-file runtime payload SHA-256
`2b35617cd80abae02ad208d099c5d328d25d2f85c654fea1c9f10518ecb824ee`.
The unchanged [generalization prompt](../pi-prompts/desktop-plugin-ui-cross-generalization.md)
has SHA-256 `45d19d83b245ed31d9e0307b2da37910addb2cef0179670f91d44c5e52458a89`.
The frozen bundled `check_reports.py` has SHA-256
`68892c9952c6036c2e07cade284280282f4d97f7aef2f04be0395fd3a983e1b2`.
The separate required [v4 grader](inspect_cross_v4.py) has SHA-256
`5014634fcd76e38a3b4aea35390b6d0669fbc52a169fe0cd45d7eb35543a9155`.
No skill, prompt, runtime copy, or grader was changed during these runs.

For each `N` in 1, 2, 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-generalization.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v4-generalization-luna-N --expect-output handoff/restricted-surfaces.md --expect-output handoff/recovery-plan.json --expect-output-json-field handoff/recovery-plan.json::host_acceptance_verified=false --expect-output-json-field handoff/recovery-plan.json::task_empirical_tests_performed=false
```

The mandatory event summarizer ran on every trace with
`--require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error`.
All three summaries passed: the observed provider/model is exclusively
`openai-codex` / `gpt-5.6-luna`, event JSON is valid, no tool error occurred,
all exact output paths exist, both task booleans remain false, and skill
integrity and read-surface gates passed. A diagnostic `passed:false` response
that exits zero is retained as a finding, not falsely counted as a tool error.

| Run suffix | Duration | Model records | Strict | Required v4 grader | Manual | Independent final checker |
| --- | ---: | ---: | --- | --- | --- | --- |
| `luna-1` | 85.023 s | 10 | Passed | Passed | Failed: untested action relabeled as failed | Passed, 44 URLs / 14 historical rows |
| `luna-2` | 67.819 s | 7 | Passed | Passed | Passed | Passed, 39 URLs / 10 historical rows |
| `luna-3` | 87.133 s | 12 | Passed | Passed | Failed: Codex exclusivity and setup failure label | Passed, 43 URLs / 10 historical rows |

The [v4 structural result](cross-v4-generalization-structure.json) records
identical payloads, final artifact hashes, correct post-final-write report
checker coverage of both files, and no structural findings. The 42 canonical
pattern headings were available; the runs selected 18, 29, and 18 IDs. The
generalization task has no independent minimum-pattern-count requirement.
The legacy grader was preserved and was not used as a substitute for v4.

## Manual failures

Review followed the [criteria prepared before the freeze](cross-v4-generalization-review-criteria.md).
Structural labels and exact citations cannot prove factual evidence semantics.

Run 1's `handoff/recovery-plan.json`, `historical_observations[13]`, describes
Copilot chat MCP Apps/native canvas paint as not exercised. Its final evidence
at line 291 nevertheless reads:

> observed-failed; no visual acceptance result was obtained because the paint action was not exercised; capability or documentation is not paint acceptance

This is an untested action, not an observed failure. The trace retains the
mechanism: the first report check at event lines 8275–8276 found the missing
literal empirical label in this row; a successful edit changed the evidence
to `observed-failed`, after which the checker passed at lines 8440–8441. The
correct response would have retained uncertainty outside the historical
executed-observations list, rather than inventing a failure to satisfy the
field validator. Other rows and the host summary correctly call paint
untested, which does not repair this row's false empirical label.

Run 3's `handoff/restricted-surfaces.md`, line 27, says that `on-request` is
“suitable only for an owned client” that presents the request and returns its
ID. This policy section generalizes the restriction beyond the observed
custom app-server connection. A future custom frontend is one applicable
route, while stock desktop/IDE paint remains untested. Adjacent custom-client
recommendations and the JSON's explicit untested desktop/IDE caveat are useful,
but do not sufficiently bound the literal exclusivity claim. The parent
reviewer independently reached the same conservative judgment under the
pre-run Codex-scope criterion.

Run 3 additionally labels its successful ChatGPT setup-to-consent observation
`observed-working and observed-failed` at JSON line 250. The result explicitly
says connection completion and widget paint were not performed; there is no
failed completion attempt in that observation to support `observed-failed`.
Keep this as an evidence-label defect rather than a ChatGPT product failure.

No artifacts were altered after review. These manual failures do not change
the separately true strict/structural/checker outcomes.

## Factual review and trace limits

Run 2 preserves the applicable routes and evidence layers: Claude native
engine controls without claiming terminal paint; observed Claude Desktop Chat
local paint/actions/error/fullscreen without remote or elicitation acceptance;
Copilot terminal forms versus a separately tested VS Code extension webview;
Codex `never` automatic decline versus a future owned `on-request` client;
and ChatGPT setup/fixture evidence without widget acceptance. Image input,
result bytes, native validation, pixels, and interactive canvas are distinct.
Cancellation does not establish permission, file delivery, navigation, or auth.
Deployment, negotiated capabilities, accessible fallback, server validation,
state retention, and budget-first stages are actionable.

Both final artifacts were independently checked from each copied bundle with
`check_reports.py ... --fail-on-findings`; all three returned `passed:true`,
no source/evidence-field findings, and no replacements. Exact sources are
from the bundled catalog; this closed-book cohort did not freshly fetch them.
Manual review still found the semantic defects above. No broad all-Codex
exclusion was found in run 2.

All three traces read the task prompt, `SKILL.md`, and the twelve relevant
runtime references. They used the bundled catalog/checker, then wrote and
checked the requested reports. They did not read acceptance galleries,
repository docs, project evidence, sibling skills, or external accounts. The
only repairs were within their own generated reports. No host app was opened,
no external provider model was invoked, and no new host acceptance is claimed.

Pi evaluation-model usage is separate from product-provider empirical probes:

| Run | Input | Output | Cache read | Total tokens |
| --- | ---: | ---: | ---: | ---: |
| 1 | 37,624 | 10,542 | 196,352 | 244,518 |
| 2 | 35,564 | 9,124 | 93,312 | 138,000 |
| 3 | 39,756 | 10,886 | 238,848 | 289,490 |

Raw events/stderr, manifests, artifacts, strict checks,
`model-trace-summary.json`, and `report-check-independent.json` remain under
`evaluations/runs/20261024-desktop-ui-cross-v4-generalization-luna-{1,2,3}/`.
Prior cohort reports and failures remain separate and unchanged.
