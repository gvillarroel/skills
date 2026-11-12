# Evidence repair generalization: v2 Luna

Date: October 25, 2026. Skill: `desktop-plugin-ui`. This is a new frozen
subject and three fresh first attempts using the unchanged
[generalization prompt](../pi-prompts/desktop-plugin-ui-evidence-generalization.md)
and [independent criteria](evidence-repair-review-criteria.md). The
[v1 cohort](evidence-generalization-v1-luna.md) remains separate. All six final
artifacts were read and independently checked; no output was rerun or repaired.

## Results

| Check | Run 1 | Run 2 | Run 3 | Total |
| --- | --- | --- | --- | --- |
| Strict harness | Fail: three tool errors | Fail: read beyond EOF | Fail: default-encoding read | **0/3** |
| Final typed checker | Pass | Pass | Pass | **3/3** |
| Independent content/classification | Pass | Pass | Pass | **3/3** |
| Workspace/action scope | Pass | Pass | Pass | **3/3** |
| Joint strict/manual acceptance | Fail | Fail | Fail | **0/3** |
| Typed records | 19 | 12 | 20 | 51 |
| Exact palette bindings | 23/23 | 18/18 | 17/17 | 58/58 |
| Structured contrast ratios | 7/7 | 10/10 | 9/9 | 26/26 |
| Canonical Nielsen IDs/labels | 10/10 | 10/10 | 10/10 | 30/30 |

The central classification task passes independently in each output, but the
required two joint passes out of three are **not met**. The checker and content
passes do not erase execution failures. Keep release status separate.

All three outputs propose a useful extension-owned HTML panel, with explicit
prerequisites, fallback, server-versus-panel state ownership, reload/reconnect/
failure handling, English Save/Cancel/Explain/export/error copy and the selected
ColorSet 2. Host-owned chrome/permissions and accessibility overrides remain
outside authored-paint claims. Exact identifiers and error tokens are retained.
H1-H10 labels and concrete checks are present; no user study or renderer is
claimed. Run 1 marks some proposal-inspection checks as pass while explicitly
leaving rendered host acceptance remaining; this is not a user-study claim.

The supplied fictional facts retain their correct evidence bases:

- Static chart/export source and the panel contract derive documented,
  execution not-run. No actual handler invocation is invented.
- The human chart report retains its explicitly unknown capture build and
  is untested for automated acceptance.
- Expected rejection of `urgent` and accepted Boolean `false` are passing
  checks. No cancellation is inferred from false.
- `E_UNAVAILABLE` with unchanged revision 11, instead of expected revision 12,
  is the failed save check.
- The unavailable mobile test is untested. Bridge/storage prerequisites are
  conditional; microphone access is a surface-bound explicit exclusion.

Lab UI Host 1.4.2 remains a supplied fictional fixture, not empirical evidence
about a real coding assistant or tests newly performed by this agent. Both
current-task flags remain Boolean false. All final JSON files contain the
protected `evidence_validation` object and normalized typed records.

## Independent validation

All 51 typed records recompute successfully with the frozen copied classifier.
Their references resolve, and final typed-mode checking passes for both exact
artifacts in each run. Run 3 has four exact official URL occurrences; runs 1/2
use source locators and do not need fabricated public URLs. Zero checked URLs
in those cases is not described as certification of factual coverage.

The final Markdown tables match normalized record data. Optional underscore
escaping is normalized before comparison, avoiding a hidden exact-markup
requirement. Run 3 repeats the same ledger twice after an imperfect assembly
repair; both copies agree with the JSON records. This is a verbosity/assembly
caution, not a new evidence-label failure or an unrequested no-duplicate gate.

All 58 claimed token/value bindings match the frozen CS2 asset. Independent
opaque-sRGB calculations match all 26 structured pairs within `1e-9`. Weak
error/gray-focus candidates are rejected or restricted to appropriate uses;
safe text and focus alternatives are specified. The 30 Nielsen ID/label pairs
match the canonical short labels. Arithmetic, proposal inspection and helper
acceptance do not establish rendered accessibility or user acceptance.

## Retained tool failures

All three `pi` processes exit 0, exact outputs and task flags pass, and copied
payloads remain unchanged. Strict event acceptance nevertheless fails:

| Run | Event line | Failure |
| --- | --- | --- |
| 1 | 14502 | Exact-text edit could not find an old-text segment in `work/facts.json`. |
| 1 | 15140 | Exact-text edit matched two occurrences rather than one. |
| 1 | 16068 | A CI-mode helper invocation receives malformed edited JSON: expected a comma at line 393. |
| 2 | 11942 | Read requested offset 165 beyond the then-current 116-line Markdown file. |
| 3 | 9564 | Hand-written `json.load(open('work/ledger.json'))` uses Windows cp1252 instead of explicit UTF-8 and raises `UnicodeDecodeError`. |

The model later recovers its final files, but the original strict failures
remain. The default-encoding failure occurs in the model's inspection command,
not the helper's explicit UTF-8 artifact reader. None of these is evidence
that a real assistant UI or the typed classification itself is unsupported.

## Scope and read-surface review

The evaluator inspected **complete shell command strings plus all read, write
and edit paths**, rather than relying only on read guards. All three runs use
relative workspace `work/` scratch and `proposal/` outputs. No external-Temp
read/write/cleanup is found in this cohort, and no account, Copilot sign-in,
additional provider/model, network, installation or actual UI action is found.
Helper temporary files stay beside their requested outputs.

The prior v1 external-Temp failure remains intact and is not reclassified.
The evaluator did not inspect or clean any external file from that earlier run.

Read surfaces include the prompt, copied skill, relevant report/design/pattern
references, helper sources where needed, and generated artifacts. No sibling
skill, acceptance gallery, repository documentation or outside-workspace
artifact is read. Required independent trace summaries correctly fail on the
retained tool errors; they do not weaken strict policy to count a pass.

## Frozen identities and commands

All three actual copied manifests contain **23 files**, SHA-256
`ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
Raw prompt hash remains
`3a3cd5053096f4f0e0e994a318c0bc72207fc0f31133fb12ef7a57d6ba13e977`;
criteria hash remains
`c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2`.
Both were rechecked after completion. Output identities are retained separately.

Run IDs are `20261025-desktop-ui-evidence-generalization-v2-luna-1`, `-2` and
`-3`, each launched once. Representative original command:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-generalization.md --run-id 20261025-desktop-ui-evidence-generalization-v2-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output proposal/recommendation.md --expect-output proposal/recommendation.json --expect-output-json-field proposal/recommendation.json::host_acceptance_verified=false --expect-output-json-field proposal/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
```

Each independent event summary uses the corresponding original run ID and
separate destination, with the required model, tool/error/JSON/read checks:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-generalization-v2-luna-1/events.jsonl --output projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/generalization-v2-1-strict-trace.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))' --forbid-read-regex '(?i)^\.\.(?![\\/]prompt\.md$)' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\\/]|/|\\\\)'
```

Durations are 220.590, 146.217 and 156.053 seconds. Completed tool calls are
46, 34 and 27; observed Luna assistant records are 36, 23 and 23. The deliberate
Luna model exception is observed in every trace. JSON events, exact artifacts,
false flags and payload integrity pass. No run is silently retried.

Independent final checking uses each frozen copied `check_reports.py` with
both final paths and `--require-evidence-records --fail-on-findings`. Detailed
numeric/token/table checks, complete command/path audits, trace summaries and
output hashes are retained under ignored
`projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/` as
`generalization-v2-{1,2,3}-independent.json`,
`generalization-v2-{1,2,3}-strict-trace.json` and
`generalization-identities-v2.json`.

Only this durable evaluation note and ignored evaluator receipts were added.
No canonical source, backlog, account, real host or earlier evaluation output
was edited by the review. A different model or subject requires a separate
cohort; none of these Luna failures may be pooled away.
