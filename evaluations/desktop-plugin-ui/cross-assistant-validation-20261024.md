# Cross-assistant UI skill investigation and validation

Date: October 24, 2026, America/New_York. UTC run logs cross into October 25.
The user expanded the original Claude Desktop request to Claude Code,
Claude Desktop, Codex, ChatGPT and GitHub Copilot, required empirical probes,
authorized missing installations and requested minimal Claude/Copilot inference.
All authored skill and evidence documents are English.

## Deliverable and release status

Canonical bundle: `skills/desktop-plugin-ui/`; ignored local installation:
`.agents/skills/desktop-plugin-ui/`. Current v4 source/runtime/full subject:
**16 files**, SHA-256
`2b35617cd80abae02ad208d099c5d328d25d2f85c654fea1c9f10518ecb824ee`.
The bundle contains 12 progressive references and **42 canonical patterns**:
25 original Claude/shared recipes, six Codex, six Copilot and five ChatGPT.
No published example set, Pages output, commit or push was introduced.

Keep status **validating**. The knowledge bundle, static gates, measured host
facts and local installation are usable; required live-host checks remain
pending account/connection gates. Final v4 passes 7/8 strict and independent
checks, but conservative full acceptance is 4/8: contract 1/1, naturalistic
2/3, generalization 1/3, boundary 0/1. The boundary retains execution/format
errors, and some generated answers still overstate untested Codex support or
mislabel unperformed tests. Do not pool passing subsets across payloads or
present this as a clean release.

The entry point routes five assistants and frontends; the surface matrix
requires coverage of content, placement, controls, authority, browser features,
state, lifecycle, deployment, numeric budgets and evidence. Host identity is
distinct from model identity. Untested stock rendering must remain untested;
a custom client is one possible route, not a proven universal requirement.

## Empirical host evidence

| Host/layer | Result | Cost boundary | Durable evidence |
| --- | --- | --- | --- |
| Claude Code 2.1.302 native engine | Strict plugin validation and 57/57 tests; raw HTML, unsupported surface primitives and exact numeric overflows refused | Zero Claude model requests | [Claude findings](../../projects/desktop-plugin-ui/cross-assistant/claude/findings.md) |
| Claude Desktop 3.6556.2 actual Chat, Free account | Local stdio discovery, actual iframe paint, direct 7-to-8 tool action, schema error preserving 8, fullscreen and return to inline, context acknowledgement, download/link consent cancellation | One minimal user-prompted Haiku 5.5 Medium turn; exact tokens not exposed; no further prompted turns | [Live-host report](../../projects/desktop-plugin-ui/cross-assistant/live-host-validation-20261024.md) |
| Codex 0.145.0 app-server | Three policy/opt-in runs, each 18/18 assertions; additional final 18/18 replay; content/resource transport and on-request callbacks work, never auto-declines | No inference for protocol runs | [Codex report](../../projects/desktop-plugin-ui/cross-assistant/codex/validation.md) |
| Codex actual CLI | One authenticated gpt-5.6-luna turn called synthetic card/form and finished; image/resource receipt does not prove pixels or stock widgets | Reported 61,487 input including 45,312 cached; 331 output including 211 reasoning | [Codex report](../../projects/desktop-plugin-ui/cross-assistant/codex/validation.md) |
| Copilot CLI 1.0.75 and task-local 1.0.103 | ACP initializes; invented ui/show refused. Actual 1.0.103 terminal confirm/select/input/Escape returned true/Beta/synthetic/null; bare SDK UI gate refused without callback | Zero model inference; offline synthetic provider request count zero | [Copilot report](../../projects/desktop-plugin-ui/cross-assistant/copilot/validation-20261024.md) |
| VS Code 1.143.1 real extension host | Five final webview checks passed: script permission, bridge, CSP, protected top DOM and disposal | Zero Copilot inference | [Copilot report](../../projects/desktop-plugin-ui/cross-assistant/copilot/validation-20261024.md) |
| ChatGPT signed-in web setup | Custom MCP configuration reached final Connect consent, which remained pending; no live component paint | No model or remote reference tool call | [Live-host report](../../projects/desktop-plugin-ui/cross-assistant/live-host-validation-20261024.md) |

VS Code was installed portably under ignored project artifacts. Copilot CLI
1.0.103 was installed task-locally; existing PATH tools were preserved. The
portable VS Code bundle contains Copilot Chat 0.71.0; an attempted older
Marketplace version was refused. Native webview success is not Copilot chat
MCP Apps acceptance. Negotiated canvases are not painted canvases.

The original synthetic SDK/browser fixture's 25 assertions remain a separate
layer. The actual Claude Desktop capture verifier passes **14/14** observations,
including exact restoration of the original user configuration. The temporary
server was removed and Claude reopened normally; the loopback HTTP probe was
stopped. Screenshots/private config backups remain ignored, not runtime files.

Actual Desktop access to the immediate MCP-UI Proxy parent differed from the
opaque-origin synthetic browser. References now avoid a blanket parent-DOM
claim and separate immediate wrapper from protected top application access.

## Isolated study and retained failures

Model exception: `openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0. The
default Spark model was rejected by the signed-in account in the earlier
record; this deliberate exception remains in SKILLS.md. No Claude or Copilot
provider was used for forward tests. All task prompts forbid network,
external apps/accounts/configuration and payload writes.

Each cohort uses contract once, naturalistic three times, generalization three
times and boundary once, with the same four versioned cross-assistant prompts
and original independent grader. Exact Markdown/JSON outputs, required false
booleans, observed model, JSON events, tool errors, read surface and unchanged
payload are checked. Manual review adds factual and formatting judgments.

| Cohort | Frozen payload | Result and interpretation |
| --- | --- | --- |
| v1 | `a54a8e1ea5bf4c5ab693557b90b711881cb9600b6df3ff45753eec2947d54fac` | Strict 8/8; original independent artifact checks 4/8. Four outputs omitted literal historical evidence labels. Factual scope was bounded. Retained as format failures. |
| v2 | `455db7f6daee26026e3c3be314406baf2f19a9e3c31c2250f09fc4d978389c05` | Explicit machine-readable evidence rule added. Strict 7/8; contract copied an incorrect MCP domain, source checker caught it and final output was repaired, but one failed CI command violates zero-tool-error. Naturalistic and generalization subsets each pass 3/3; do not pool them into v3. |
| v3 | `1cd3cedbc5124bde59e242b22770eb0505893f65058cb7d438b90f55f79863b3` | Diagnostic-first source repair clarified. Strict and original independent checks 7/8. Contract passes; naturalistic strict 3/3 and conservative manual 2/3; generalization strict 2/3 with final factual/source correctness 3/3; boundary strict/automated pass but explicit field-placement format gap remains. |
| final v4 | `2b35617cd80abae02ad208d099c5d328d25d2f85c654fea1c9f10518ecb824ee` | Strict/new independent 7/8; contract accepted 1/1, naturalistic manual 2/3, generalization manual 1/3, boundary 0/1. Exact outputs, models and integrity pass all eight; boundary retains two edit errors and an empty required sources array. Generated exclusivity/untested-label errors remain manual failures. |

Retained v3 limitations:

- Generalization 1 produced two ambiguous edit errors while repairing a
  duplicated URL. It later repaired both outputs correctly; the strict run
  still fails. No favorable retry or external artifact repair was accepted.
- Naturalistic 2 says a Codex dashboard is only available in an owned frontend.
  This exceeds the evidence, which leaves stock frontend paint untested.
  Later caveats do not erase that semantic failure. Naturalistic 1 has a
  bounded wording caution; run 3 is clean. Conservative acceptance is 2/3.
- Boundary places canonical historical labels in result rather than evidence.
  It preserves factual scope, but violates the explicit field rule. The
  original grader searches the historical array too broadly, so manual
  review correctly prevents treating its automated pass as complete acceptance.
- An evaluator briefly relaxed v1's label criterion, then restored it. The
  altered grade is explicitly withdrawn and retained. A v2 same-payload retry
  was interrupted before an evaluable result and excluded. Neither is a pass.

Reviews: [v1 contract/boundary](cross-v1-contract-boundary.md),
[v1 naturalistic](cross-v1-naturalistic.md),
[v1 generalization](cross-v1-generalization.md),
[v2 contract/boundary](cross-v2-contract-boundary.md),
[v2 naturalistic](cross-v2-naturalistic.md),
[v2 generalization](cross-v2-generalization.md),
[v3 contract/boundary](cross-v3-contract-boundary.md),
[v3 naturalistic](cross-v3-naturalistic.md), and
[v3 generalization](cross-v3-generalization.md).

V4 adds `scripts/check_reports.py`, SHA-256
`68892c9952c6036c2e07cade284280282f4d97f7aef2f04be0395fd3a983e1b2`.
It checks each historical observation's own evidence field and raw/decoded
JSON source strings. Explicit URL mappings replace every exact token; targets
must come from the bundled primary catalog. It never chooses a URL or label
implicitly. JSON preflight, own-bundle protection and atomic writes preserve
BOM and line endings. **33/33 deterministic tests** pass; the original source
checker remains unchanged with **39/39** passing tests.

The separate v4 independent grader was frozen before the cohort, SHA-256
`5014634fcd76e38a3b4aea35390b6d0669fbc52a169fe0cd45d7eb35543a9155`.
Its **21 self-tests** include the prior per-field false negative. It requires
a successful report-helper trace after final writes and independently runs
the copied helper. This strengthens the evidence-field check without relaxing
source, model, tool-error, integrity or factual gates. The original grader
remains unchanged for v1-v3. See [independent helper review](report-checker-v4-review.md).

Final v4 reviews: [contract and boundary](cross-v4-contract-boundary.md),
[naturalistic](cross-v4-naturalistic.md), and
[generalization](cross-v4-generalization.md). The helper diagnosed six misplaced
historical labels in naturalistic 1; the agent repaired them and reran cleanly.
Source and literal-field correctness do not prove factual truth: generalization
1 mislabeled unperformed Copilot chat/canvas paint as a failure; generalization
3 overclaimed on-request/owned-client exclusivity and added a failure label to
successful ChatGPT setup with unperformed later steps. Naturalistic 3 overclaimed
the owned-frontend requirement. No output was repaired, waived or replaced.
Boundary ignored the explicit URL repair helper, produced two edit errors,
then repaired final citations; that repair does not erase its strict failure.

The new metadata-only routing control passes **10/10**: five host positives,
two mechanism/ambiguity positives and three negatives. It receives only the
name/description and has no forced skill or body. This is a metadata decision
control, not automatic product routing certification. See
[routing prompt](cross-routing-prompt.md) and [runner](cross-routing-control.py).

## Reproduction and repository gates

Typical isolated command; substitute the case prompt, repetition ID and its
two exact paths as recorded in the linked reviews:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-cross-v3-naturalistic-luna-1 --expect-output proposal/support-queue.md --expect-output proposal/host-decisions.json --expect-output-json-field proposal/host-decisions.json::host_acceptance_verified=false --expect-output-json-field proposal/host-decisions.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v3- --output evaluations/runs/desktop-ui-cross-v3-independent.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Use `inspect_cross_v4.py` and the v4 prefix for the current cohort; the older
command above reproduces v3 under its original grader. The aggregate inspector
intentionally returns nonzero for a failed cohort.
Raw run folders and exact artifacts remain under ignored `evaluations/runs/`.
An all-case pass is not claimed. The original independent helper's 15 checks
and the new v4 grader's 21 checks pass.

Deterministic/repository commands:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-report-checker.py
uv run --script projects/desktop-plugin-ui/scripts/verify-live-captures.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
```

Results: source checker **39/39**, report checker **33/33**, live captures **14/14**, harness **17/17**;
pattern IDs, repository validator, independence and payload pass. Scoped
authoring audits pass canonical/runtime/full profiles with identical final
16-file digest. Local synchronization and check pass all 16 files. The staged
copy was moved into ignored artifacts after synchronization. No unrelated
pre-existing changes were reverted or staged.

The source checker now validates exact primary hosts and recognized GitHub
owners, rejects lookalike domains and requires exact catalog URLs. A report
retaining an independently verified 404 investigation URL and a newly checked
GitHub SDK repository used explicit allow-url exceptions; neither introduces
a false source claim. The VS Code binary retrieval endpoint is recorded as
host/path metadata with verified HTTP 200, distinct from documentation.

## Pending host gates and next work

Claude CLI auth remains logged out; the requested official login flow is open
and awaits the person's account challenge. Desktop and CLI credentials are
separate. ChatGPT final reference-server connection awaits explicit consent
because the screen grants access to relevant conversation/memory context.
No connection, prompt or remote tool call was sent before consent.

Automatic execution review rejected the proposed public development tunnel
with "blocked by policy" and supplied no more specific reason. It did not
start, was not retried through an equivalent route, and is not counted as a
product incompatibility. The documented private OpenAI tunnel alternative
was researched but not configured.

After those gates, test actual authenticated Claude terminal/native paint,
ChatGPT iframe controls/modes, and signed-in Copilot chat MCP Apps/canvas
rendering. Device permission, actual file delivery, persistence/reopen and
alternate OS/mobile/frontend results remain individually scoped. V4 makes
repeated citation repair deterministic and enforces the evidence field. Verify
fresh forward outputs before accepting all wording and workflow fixes. Current
v4 manual findings above remain open; the skill continues to require factual
review beyond its deterministic helpers.
