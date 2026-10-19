# Pi Durable naturalistic forward cohort, subject C — 2026-10-19

The final frozen cohort does **not** meet the unchanged requirement of 2/3 joint passes: **strict 1/3, artifact quality 3/3, complete independent acceptance 2/3, joint 0/3**. The only strict pass fails the independent workspace-write gate. Keep the skill `validating`; deterministic source tests and usable generated artifacts do not replace the required isolated-workflow result.

This is model-specific evidence for `openai-codex/gpt-5.6-sol`. Do not pool it with the earlier Luna cohorts or claim Luna certification. The [subject A](naturalistic-20261019.md) and [subject B](naturalistic-v2-20261019.md) reports and all their original failures remain retained.

## Frozen protocol

- Runtime skill: `pi-durable`, 23 files, no acceptance fixtures; SHA-256 `b6fa474c26b9a3dfc3ae3920b3a4edcb145ad132e0028ba23e0c8dc4f267590d` in all three manifests.
- Unchanged [prompt](../pi-prompts/pi-durable-naturalistic.md), SHA-256 `cb9db6d235cdd1302c27d3f96e02b147009e3ff548c1a99e00e6320a691dcfc4`, and [acceptance criteria](acceptance.md).
- Observed model: `openai-codex/gpt-5.6-sol`, high thinking. The backlog records this final authoring-model exception after Spark rejection before tools and the retained Luna workflow failures.
- JSON strict mode, runtime-only profile, exact outputs `service/config.json`, `OPERATIONS.md`, and `plans.json`, 300-second limit, unchanged 2/3 joint threshold.
- Native host: Windows 11 build 26200, Node 24.18.0, Pi 0.84.2, Git Bash/MinGW forward shell. No native macOS lifecycle evidence.
- Three fresh concurrent workspaces. No source, prompt, acceptance, or output repair during the cohort. Assigned harness uv cache: repository-local `evaluations/runs/pi-durable-cache/uv`.

## Results

| Trial | Pi exit | Duration | Strict | Tool errors | Artifact quality | Independent | Joint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 0 | 262.631 s | fail | 2 | pass | pass | fail |
| C2 | 0 | 249.648 s | pass | 0 | pass | fail: cache scope | fail |
| C3 | 0 | 219.974 s | fail | 2 | pass | pass | fail |

All exact outputs are present, all copied payloads remain unchanged, all streams contain valid JSON, and all show the requested model. Prompt-first and direct-read policies pass. No trial reads acceptance fixtures, sibling skills, repository documentation, or existing credentials. No live GitHub request, native service registration, executed deployment plan, or real review-provider invocation appears in the traces. All three use the scoped helper for their initial prepare, smoke, and platform-plan operations.

Every generated config correctly selects `atlas-reviewer`, `acme/widgets`, faux provider, PR polling at 60,000 ms, and an initial baseline. Both plan wrappers have `executed:false`, correct Windows/macOS mechanisms, complete lifecycle arrays and artifacts, and deployment configurations matching the requested target state and service identity. The target Windows state is exactly `C:\PiAgents\atlas\state`; the two failed agents' handwritten comparisons do not expose a generated-path defect.

All three guides cover private read-only findings; both platform lifecycles; control and saved-job chats; correcting active work and queueing follow-ups; durable event/message identity; one owner; restart recovery; baseline versus restart; credentials, databases and logs; idle model silence; and login/sleep/logout limits. Their verification distinguishes the Windows-local smoke and generated plans from unperformed native Windows/macOS installation. The evaluator accepts all three artifacts under the original criteria.

The evaluator rebuilt every generated project with an explicit `npm_config_cache` inside that project's `service/.cache/npm`, ran each compiled CLI's help, independently parsed config/plans/smoke JSON, inspected guides and shell commands, and checked the native process table. All independent builds pass; zero scoped residual `serve` processes were found. Saved smoke reports show one event job, zero duplicate jobs, the same task conversation after reopen, deduplicated human submission, zero reopen provider calls, and no native registration.

## Exact failures

**C1, agent workflow failure:** event-call lines 3782 and 4309 execute handwritten Node assertions with overescaped Windows path literals. Both print `config:true`, `windows:false`, `macos:true`, `operations:true`, and `smoke:true`, then exit one. Independent JSON comparison confirms the actual generated Windows state path is correct. The agent later switches to structural path checks, but earlier tool errors remain failures.

**C3, agent workflow failure:** event-call lines 3018 and 3491 execute the same overescaped Windows-state assertion twice and throw `Error: windows state`. The agent later uses a correct raw-string comparison. The final files are correct; the two recorded tool errors still fail strict acceptance.

**C2, independent write-scope failure:** after successful helper use, the agent additionally runs raw `cd service && npm run build` without a workspace cache override. npm succeeds, so strict tool checks pass, but it creates the default-cache log `C:\Users\villa\AppData\Local\npm-cache\_logs\2026-10-19T12_52_18_379Z-debug-0.log` outside the workspace. Read-only metadata and that specific log's title/argv/cwd fields confirm `npm run build` with cwd pointing to this trial's `workspace/service`. The evaluator did not delete or modify the external file. This is an observed agent write-scope violation, not hypothetical risk or unavailable infrastructure; it prevents a joint pass.

No helper-runtime defect, model mismatch, missing exact output, payload mutation, invalid event JSON, timeout, or dependency-install infrastructure failure was observed. The joint threshold and zero-error/write-scope rules are unchanged. No further trials were run after this final cohort.

## Reproduction and evidence

The three exact commands use `N` equal to `1`, `2`, and `3`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-sol --run-id 20261019-pi-durable-naturalistic-v3-sol-N --expect-output service/config.json --expect-output OPERATIONS.md --expect-output plans.json --timeout-seconds 300
```

Raw runs remain under `evaluations/runs/20261019-pi-durable-naturalistic-v3-sol-N/`, including manifests, events, stderr, strict checks, integrity checks, evaluation results, and untouched generated workspaces. Each folder also contains evaluator `independent-check.json` and `read-surface-summary.json`. C2 additionally contains `scope-check.json` documenting the minimal read-only log attribution.

Every stream was summarized with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261019-pi-durable-naturalistic-v3-sol-N/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

C1/C3 correctly exit one for tool errors; C2 exits zero while failing the separate independent scope gate. Independent build commands explicitly set the cache before running npm:

```powershell
# Working directory: the trial's workspace/service
$env:npm_config_cache = Join-Path (Get-Location) '.cache/npm'
npm.cmd run build
node dist/src/cli.js help
```
