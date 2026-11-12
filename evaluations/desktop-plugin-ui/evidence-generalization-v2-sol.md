# Evidence repair generalization: GPT-6.1 Sol

Date: October 25, 2026. This is a separate cross-model cohort on the unchanged
v2 `desktop-plugin-ui` payload. The [generalization prompt](../pi-prompts/desktop-plugin-ui-evidence-generalization.md)
is unchanged; [Sol criteria](evidence-repair-sol-review-criteria.md) differ from
the Luna criteria only in the declared evaluator model and header/context.
Semantic standards and thresholds are unchanged. Preserve the
[v1 Luna](evidence-generalization-v1-luna.md) and
[v2 Luna](evidence-generalization-v2-luna.md) failures separately.

## Results

All six final artifacts were inspected. No first attempt was rerun or repaired.

| Check | Sol 1 | Sol 2 | Sol 3 | Total |
| --- | --- | --- | --- | --- |
| Strict harness | Pass | Fail: missing scratch directory | Pass | **2/3** |
| Final typed checker | Pass | Pass | Pass | **3/3** |
| Independent content/classification | Pass | Pass | Pass | **3/3** |
| Workspace/action scope | Pass | Pass | Pass | **3/3** |
| Joint strict/manual acceptance | Pass | Fail | Pass | **2/3** |
| Typed records | 18 | 19 | 17 | 54 |
| Exact selected palette bindings | 17/17 | 15/15 | 14/14 | 46/46 |
| Unrounded contrast assertions | 16/16 | 15/15 | 11/11 | 42/42 |
| Canonical Nielsen IDs/labels | 10/10 | 10/10 | 10/10 | 30/30 |

This cohort meets the generalization requirement of at least two joint passes
out of three. That result is model-, prompt- and payload-bound; it does not
erase Luna failures, certify every model or establish actual assistant paint.

Each output recommends the contract-supported extension-owned HTML panel and
provides practical search/selection, staged editing, chart/table, refresh,
Explain and selected export routes. Actual registration, messaging, security,
authorization and storage interfaces remain prerequisites; another host's
MCP Apps, Claude or VS Code APIs are not imported as fictional Lab facts.
Read-only/text fallback and optional reconnect behavior are appropriately
conditional. Service authority, transient panel state, drafts and verified
durable checkpointing remain distinct across reload/reconnect/failure.

All authored copy is English and complete for Save, Cancel, Explain, export,
recovery and errors. Sample `M-204 / high / pending` content is explicitly
illustrative/brief-required, rather than falsely attributed to a probe.
Success, unchanged-state, copied and delivered messages are receipt-gated.
All H1-H10 IDs/short labels and concrete checks are present; the proposed
rendered workflows remain untested, and no user study is claimed.

## Evidence classification and coverage

All three outputs correctly preserve the supplied fictional lab scope:

- Source mounts/handlers and the panel contract are documented, not executed
  chart/export interactions. Source and missing-receipt claims have distinct
  basis/context rather than invented callback observations.
- The human chart report retains its unknown capture build and is untested
  for agent interaction acceptance. It is not rebound to Lab build 1.4.2.
- Expected `E_INVALID_PRIORITY` with saved `high` unchanged passes. Accepted
  Boolean false also passes, without becoming cancellation or missing data.
- The save check fails: expectation revision 12, actual `E_UNAVAILABLE` and
  revision 11. Its known unchanged-state result is not generalized to every
  timeout or unknown outcome.
- Unperformed mobile, chart/export and cancellation checks remain untested.
  Reconnect prerequisites remain conditional. Microphone exclusion is explicit
  and limited to the supplied contract/surface.

All 54 typed rows recompute successfully. Evidence IDs resolve, both final
paths receive inspected typed-mode checking, and the generated ledger tables
match their normalized records. Structural checker success is not used as a
substitute for the independent claim/basis/coverage review. No public URLs
are invented for supplied lab locators; these outputs need no official-URL
occurrences to certify the fictional facts.

The 46 selected token/value bindings independently match the frozen CS2 asset.
All 42 unrounded contrast assertions independently match opaque sRGB arithmetic
within `1e-9`. Runs 1/2 explicitly round Markdown values for readability while
preserving full JSON precision and unrounded threshold decisions; their display
rounding is consistent. Weak red-on-pink ordinary text is rejected or avoided,
focus/essential-border pairs are safe, and colored controls are constrained to
their checked backgrounds/separation gaps. All three retain non-color cues,
host-owned chrome/permissions, and mandatory accessibility overrides. Palette
arithmetic remains distinct from measured paint or full accessibility.

## Retained failure and scope audit

Sol 2 exits `pi` successfully and later produces correct exact artifacts, but
its first bash call at event line 587 redirects to `work/design-values.json`
before creating `work/`. The shell reports “No such file or directory.” The
later `mkdir -p work` recovery does not remove this strict tool error. Its
original failed attempt remains; no retry is counted as a new sample.

The complete shell commands and all read/write/edit paths were inspected.
Explicit scratch/report operations stay within each isolated workspace.
Run 2's `work/format_markdown.py` reads only its proposal JSON and generated
ledger and writes the final Markdown; its source is retained in the event
trace even after workspace-local scratch cleanup. No external-Temp access,
global/account configuration, Copilot sign-in, network, extra provider/model,
installation, prototype or actual host/UI action is found. No external files
from the prior Luna violation were inspected or cleaned.

Read surfaces use the prompt, copied entrypoint, focused report/design/chat
references, relevant helpers and generated local artifacts. No acceptance
gallery, sibling skill, repository documentation or external artifact is used.
Required strict summaries correctly pass runs 1/3 and fail run 2. All JSON
events are valid, both flags are Boolean false, and copied payload integrity
passes for all three; the scope pass does not erase run 2's execution failure.

## Frozen identities and reproduction

Every actual manifest contains **23 runtime files** with payload SHA-256
`ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
Raw prompt SHA-256 remains
`3a3cd5053096f4f0e0e994a318c0bc72207fc0f31133fb12ef7a57d6ba13e977`.
Sol criteria SHA-256 is
`0a94fd291070d026215d42b19ef816fad4b6b0e2e8aab55de87e35ce63f4a3db`.
These identities were checked before and after the runs. The model event
records verify `openai-codex/gpt-6.1-sol`, not merely the requested setting.

Run IDs are `20261025-desktop-ui-evidence-generalization-v2-sol-1`, `-2` and
`-3`, each launched once. Representative original command:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-generalization.md --run-id 20261025-desktop-ui-evidence-generalization-v2-sol-1 --model openai-codex/gpt-6.1-sol --mode json --strict --expect-output proposal/recommendation.md --expect-output proposal/recommendation.json --expect-output-json-field proposal/recommendation.json::host_acceptance_verified=false --expect-output-json-field proposal/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
```

The required independent summary uses the corresponding run ID and a separate
retained destination for each sample:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-generalization-v2-sol-1/events.jsonl --output projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/generalization-v2-sol-1-strict-trace.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))' --forbid-read-regex '(?i)^\.\.(?![\\/]prompt\.md$)' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\\/]|/|\\\\)'
```

Durations are 378.704, 432.284 and 460.628 seconds; completed tool calls are
23, 29 and 29. Model records are 16, 22 and 23. Exact artifacts, false task
flags and unchanged payload gates pass in each attempt. The single run-2
tool error is the strict failure.

Independent final checking invokes the frozen copied `check_reports.py` on
both exact output paths with `--require-evidence-records --fail-on-findings`.
Detailed claim/table/token/ratio checks, full command/path audits, strict trace
summaries and all six output hashes are retained under ignored
`projects/desktop-plugin-ui/artifacts/evidence-repair-20261025/` as
`generalization-v2-sol-{1,2,3}-independent.json`,
`generalization-v2-sol-{1,2,3}-strict-trace.json` and
`generalization-identities-v2-sol.json`. Original artifacts and harness receipts
remain in their three `evaluations/runs/` directories.

This review adds only the durable report and ignored evaluator receipts. It
changes no canonical source, backlog, account, real host or earlier evaluation.
Sol results are reported separately from every Luna subject and failure.
