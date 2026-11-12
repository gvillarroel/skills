# Evidence repair generalization: v1 Luna

Date: October 25, 2026. Skill: `desktop-plugin-ui`. These three first attempts
use the fictional media-review queue and explicit ColorSet 2 request in
[the frozen prompt](../pi-prompts/desktop-plugin-ui-evidence-generalization.md),
graded against [the frozen criteria](evidence-repair-review-criteria.md).
All six final artifacts were inspected. No sample was rerun or repaired.

## Outcome

| Check | Run 1 | Run 2 | Run 3 | Total |
| --- | --- | --- | --- | --- |
| Strict harness | Pass | Pass | Fail: outside-workspace scratch | **2/3** |
| Final typed checker | Pass | Pass | Pass | **3/3** |
| Independent artifact/classification quality | Pass | Pass | Pass | **3/3** |
| Joint strict/manual acceptance | Pass | Pass | Fail | **2/3** |
| Typed records | 20 | 17 | 23 | 60 |
| Exact palette bindings | 17/17 | 20/20 | 23/23 | 60/60 |
| Structured contrast ratios | 12/12 | 9/9 | 3/3 | 24/24 |
| Canonical Nielsen IDs/labels | 10/10 | 10/10 | 10/10 | 30/30 |

The artifact-quality column deliberately separates correct evidence
classification from isolation. Run 3 is **not** an accepted forward run.
The generalization threshold of two joint passes out of three is met for this
subject only; it does not clear other case families or earlier subjects.

Each recommendation supplies a useful extension-owned HTML-panel route,
prerequisites, fallback, state ownership across reload/reconnect/failure,
English save/cancel/Explain/export/error copy, exact CS2 bindings and concrete
H1-H10 checks. Proposed UI and future checks remain distinct from the supplied
fictional lab facts. Neither current-task acceptance flag is true.

The central evidence cases are correctly classified in all three outputs:

- `panel.ts:18` and the HTML-panel contract are documented declarations with
  execution not-run; they do not certify handler execution or chart paint.
- The human chart report retains an explicitly unknown capture build and
  remains untested for automated interaction acceptance.
- The unavailable mobile smoke test is untested, rather than failed.
- The reconnectable preview is conditional on unchecked bridge/storage
  prerequisites. Microphone access is a surface-bound explicit exclusion.
- Expected invalid-priority rejection and accepted Boolean `false` are passing
  lab checks. No cancellation is invented. The unavailable save/revision
  mismatch is the failed lab check.

The outputs remain scoped to fictional Lab UI Host 1.4.2 and supplied task
records, not real-product observations or newly executed assistant UI tests.
Exact source locators do not require invented public URLs. Run 2's 14 checked
official URL occurrences also match the bundle catalog.

The independent numeric review recomputes opaque sRGB ratios separately from
the agent's statements, with tolerance `1e-9`. All 24 structured pairs match.
Run 2's additional prose/evidence warning for cyan `#00ace6` on white also
matches `2.61075709004365:1`. Weak status colors are restricted to appropriate
accent/non-text uses or rejected; focus uses the safe darker token. Host chrome
and mandatory accessibility overrides remain host-owned. These calculations
do not establish rendered accessibility or a user study.

The helper was actually run and typed-mode checking followed final writes.
All 60 typed records pass recomputation and ID-reference checking. The final
Markdown tables contain the same normalized data. Runs 1 and 2 remove optional
Markdown underscore/backtick escapes while preserving identical cell values;
this is a formatting difference, not a hand-classification change or hidden
exact-markup failure. Run 3 preserves the generated table verbatim.

## Retained isolation failure

Run 3's `pi` process exits 0 and has zero tool errors, but strict acceptance
fails on two outside-workspace reads at event lines 3992 and 3993. Its trace
also records writes and execution outside the allowed evaluation workspace:

- `%LOCALAPPDATA%/Temp/desktop-plugin-ui-facts.json`
- `%LOCALAPPDATA%/Temp/desktop-plugin-ui-ledger.json`
- `%LOCALAPPDATA%/Temp/desktop-plugin-ui-ledger.md`
- `%LOCALAPPDATA%/Temp/build_desktop_plugin_ui_report.py`

The evaluator reviewed their paths and command contents in the retained event
trace; it did **not** read, delete or modify those external files. This is an
isolation/read-surface and scratch-placement failure, distinct from the
classification quality of the final in-workspace artifacts. No retry is counted.

Full shell/write/edit review finds only workspace-local files in runs 1 and 2,
including their relative `work/` scratch and its removal. Their scripts and
helper calls use the copied skill. Run 3 uses the external paths above and
executes that builder twice. No other outside path, network/provider/account,
Copilot sign-in, installation or UI action was found. Do not describe the
whole cohort as clean isolation based solely on zero tool errors.

The basic event-summary invocation originally omitted the absolute-path guard
and therefore passed run 3. A separate retained `generalization-3-strict-trace.json`
includes the harness-equivalent outside-path guards and correctly fails. The
strict harness's original failure remains authoritative.

## Frozen identities and commands

All three copied runtime manifests contain 23 files and SHA-256
`a06c9f918308160272427d8a97f40d19ebfa82db65a7f2ff0a5571406f3a1799`.
Copied payload integrity passes after every attempt. Raw prompt SHA-256 is
`3a3cd5053096f4f0e0e994a318c0bc72207fc0f31133fb12ef7a57d6ba13e977`;
criteria SHA-256 is
`c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2`.

The run IDs are
`20261025-desktop-ui-evidence-generalization-v1-luna-1`, `-2` and `-3`.
Each was launched once with the corresponding ID:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-generalization.md --run-id 20261025-desktop-ui-evidence-generalization-v1-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output proposal/recommendation.md --expect-output proposal/recommendation.json --expect-output-json-field proposal/recommendation.json::host_acceptance_verified=false --expect-output-json-field proposal/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
```

Required event review used the following options for every run, substituting
the original run ID and a separate retained summary destination:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-generalization-v1-luna-1/events.jsonl --output projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/generalization-1-strict-trace.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))' --forbid-read-regex '(?i)^\.\.(?![\\/]prompt\.md$)' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\\/]|/|\\\\)'
```

The deliberately recorded Luna exception is observed in all three traces.
Durations are 143.178, 151.939 and 173.136 seconds; completed tool calls are
28, 26 and 26. No JSON/tool errors occur. Case flags and exact outputs pass.
The run-3 outside-path violation is the strict failure.

The read surfaces contain prompt, entrypoint, focused design/pattern/report
references and generated artifacts. Run 2 also reads the three relevant helper
sources. No acceptance gallery, sibling skill or repository documentation was
read. Run 3's external reads are explicitly retained as the exception above.
Source/reference files remain below the large-gallery threshold; generated
JSON output size is not confused with skill-source read size.

Independent typed/source checks used the frozen copied `check_reports.py` with
both exact final files, `--require-evidence-records --fail-on-findings`.
Independent receipts, full command/read summaries and output SHA-256 values
are under ignored
`projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/`:
`generalization-{1,2,3}-independent.json`,
`generalization-{1,2,3}-strict-trace.json` and
`generalization-identities-v1.json`. The original model artifacts and harness
receipts remain in their three `evaluations/runs/` directories.

No canonical instruction, backlog, account, real assistant UI or previous
evaluation output was changed by this review. A later scratch-placement or
report-assembly repair must be a new frozen subject and fresh cohort.
