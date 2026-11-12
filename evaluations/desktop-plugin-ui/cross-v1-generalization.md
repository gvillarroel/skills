# Cross-v1 generalization validation

Date: October 24, 2026, America/New_York; raw UTC timestamps are October 25.
Skill: `desktop-plugin-ui`. Case: restricted incident-response surfaces.
Prompt: [desktop-plugin-ui-cross-generalization.md](../pi-prompts/desktop-plugin-ui-cross-generalization.md).
Model: `openai-codex/gpt-5.6-luna`, using the continuing model exception selected
by the parent task. Runtime: Pi 1.4.0, Windows 11, Python 3.13.12.

**Outcome: 3/3 strict runs passed; 2/3 passed the original structured-evidence
grader; 3/3 passed manual factual-content review. The v1 case is not an aggregate
release pass.** Run 3 omitted canonical empirical labels from its historical
JSON observations. Its narratives are factually scoped, but this does not
satisfy the machine-readable evidence contract; the format failure is retained.
No application, provider account, or actual host session was used in these
forward tests. The tested task explicitly required planning from the supplied
read-only snapshot; both task-level booleans remained false in all outputs.

## Frozen inputs and command

All three runs copied the same 15-file runtime payload, excluding examples and
dependencies. Before and after payload digest:
`a54a8e1ea5bf4c5ab693557b90b711881cb9600b6df3ff45753eec2947d54fac`.
Prompt digest: `45d19d83b245ed31d9e0307b2da37910addb2cef0179670f91d44c5e52458a89`.
No skill source was changed during these runs. They ran concurrently once;
there were no failed attempts, retries, or discarded outputs in this case.

For each `N` in 1, 2, 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-generalization.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v1-generalization-luna-N --expect-output handoff/restricted-surfaces.md --expect-output handoff/recovery-plan.json --expect-output-json-field handoff/recovery-plan.json::host_acceptance_verified=false --expect-output-json-field handoff/recovery-plan.json::task_empirical_tests_performed=false
```

Both exact nonempty paths were created in each isolated workspace. Harness
artifact, JSON-field, event, requested-model, prompt-first, clean-read-surface,
zero-tool-error, and unchanged-payload gates all passed.

## Trace review

The required summarizer ran separately for every trace:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v1-generalization-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

| Run suffix | Duration | Observed model records | Read/write/bash calls | Strict outcome | Independent source check |
| --- | ---: | ---: | --- | --- | --- |
| `luna-1` | 75.042 s | 7 | 14 / 2 / 1 | Passed | 49 official URLs checked; no findings |
| `luna-2` | 77.121 s | 7 | 14 / 2 / 1 | Passed | 38 official URLs checked; no findings |
| `luna-3` | 76.713 s | 8 | 14 / 2 / 2 | Passed | 45 official URLs checked; no findings |

Every model record reported exactly `openai-codex` / `gpt-5.6-luna`. All traces
had zero invalid JSON lines, invalid event records, tool errors, and policy
findings. Each read the task prompt, SKILL.md, and the twelve applicable compact
references. This broad read is justified by a task spanning all five assistants,
native/browser mechanisms, deployment, and recovery. No examples, project
artifacts, sibling skills, repository documentation, or external sources were
read. Bash calls only listed the bundled source catalog or checked the two
completed outputs; no network, installation, host UI, or account commands ran.

Pi-reported usage, kept separate from the historical application probes:

| Run | Input | Output | Cache read | Total tokens |
| --- | ---: | ---: | ---: | ---: |
| 1 | 35,630 | 10,744 | 96,640 | 143,014 |
| 2 | 37,308 | 10,748 | 95,232 | 143,288 |
| 3 | 37,788 | 10,413 | 122,112 | 170,313 |

These are evaluation-model tokens, not Claude or Copilot model usage. The
observed model-record count is not an inference HTTP-request counter.

## Manual artifact review

All three handoffs correctly rejected a universal HTML panel and selected
usable routes for the actual constraints:

- Claude Code terminal uses native Mod controls and transcript fallback;
  engine acceptance is separated from actual terminal painting. Raw HTML and
  terminal Svg rejection are retained without excluding supported Image/Raster
  validation or desktop Svg.
- Copilot terminal uses negotiated experimental native forms, with explicit
  false/null/cancel handling. Image-input and canvas flags are not treated as
  HTML painting. The tested VS Code webview remains separate from Copilot chat
  MCP Apps and canvas acceptance.
- Headless Codex under `never` continues with tool text/data after automatic
  form/URL decline. The future `on-request` custom client must implement its
  own callback presentation and matching request IDs. App-server bytes and
  MCP Apps method rejection do not become a universal frontend exclusion.
- Claude Desktop Chat's prior real local paint, app-only action, state after
  error, and fullscreen are preserved at their signed-in-chat layer. Host
  elicitation, file delivery/navigation, remote, mobile, and this task's
  acceptance remain distinct.
- ChatGPT's setup-to-consent evidence is retained without claiming a completed
  connection or widget paint. Local stdio is not universally forbidden: the
  authorized HTTPS/Secure MCP Tunnel deployment distinction is preserved.
- All plans cover capability negotiation, policy, accept/decline/cancel,
  native versus browser contracts, image input versus output/display, local
  versus remote transport, server authority, state recovery, lifecycle and
  staged future acceptance. Local/version/protocol/control tests precede model
  work; Copilot's soft credit cap is not described as a zero-cost guarantee.

Each JSON contains every required host-row and historical-observation field,
all five unique host IDs, valid canonical pattern IDs, `snapshot_date`, checks,
and both false booleans. Runs 1/2/3 selected 28/12/8 canonical patterns and
retained 8/10/6 historical observation rows respectively. The varying selected
pattern count is appropriate to task selection; it does not change the number
of patterns available in the skill.

One nonblocking phrasing issue remains in run 2: its ChatGPT setup history row
uses `result: "untested"` while the evidence text says the setup reached final
consent and only completion/paint was not performed. The corresponding host
row and Markdown correctly call setup observed and paint untested. This is a
conservative label ambiguity, not an invented renderer success. No generated
artifact was edited to remove it.

The original `inspect_cross_runs.py` grader subsequently identified a separate,
blocking format issue in run 3: historical observations describe outcomes but
do not preserve literal `observed-working` or `observed-failed` labels anywhere
in that array. Runs 1 and 2 preserve the required labels. The reviewer initially
assessed semantics separately; the original grader's stricter serialized-evidence
requirement controls release status. No criteria were relaxed, and run 3 was
not repaired in place. See `cross-v1-generalization-structure.json`.

The bundled source checker was run by each forward agent on both outputs,
its `passed:true` response was inspected, and the independent review reran it
with `--fail-on-findings`. Exact links and factual scope were reviewed manually;
catalog membership alone was not treated as remote factual verification.

## Artifact digests and retention

All bulky evidence is retained under
`evaluations/runs/20261024-desktop-ui-cross-v1-generalization-luna-{1,2,3}/`,
including raw events/stderr, manifests, artifacts, all harness checks,
`model-trace-summary.json`, and `source-check-independent.json`.

| Run | Restricted-surfaces Markdown SHA-256 | Recovery-plan JSON SHA-256 |
| --- | --- | --- |
| 1 | `cc791732dc2aabd437edaae59809b7e6b2e651aeba47c7c3604fccfc47167523` | `880de6222efcdc80e49980b66ab85825a174c613d5f10d7ac413450560cda782` |
| 2 | `50f925f6ca885fac34f2b1423cdcc78c2297c1d1941d3806a32eb0badf32c3bc` | `48636d411b47c7b765b078c3d73fd5f4b8c44028837f0c79f978c8c4a8012430` |
| 3 | `190e46514af31f4675480c6d157bc79279fa7a256f083e59f3f3eb0de17a5ee7` | `b8fae130e8942a5cf26fb3ea3390a458fc9478baa2e1b1bd7f6fe30b0a0be907` |

The latest root matrix/live-Claude references were also independently reread.
The earlier historical-fixture versus live-host ambiguity and host-elicitation
scope issues are corrected. No new factual blocker was found. This case proves
skill-only planning/generalization, not new empirical host acceptance.
