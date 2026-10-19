# Pi Durable naturalistic forward cohort, subject B — 2026-10-19

Subject B remains below the unchanged release threshold: **strict 1/3, independent 2/3, joint 1/3**, with two joint passes required. The new project helper, options-file planning, deployment configuration, and packaged offline smoke all work in these runs. Two agents still make unrelated filename, JSON-type, or handwritten-verifier errors. Preserve all three attempts; a later subject must receive fresh trials rather than relabeling these results.

The [subject A 0/3 report](naturalistic-20261019.md) and all original failures remain unchanged.

## Frozen inputs

- Runtime skill: `pi-durable`, 23 files, no acceptance fixtures. SHA-256: `6f25c64a9f600c4837a43dde9e9f4c78d23aba46ee320046db78da2a87fc57fa` in every manifest.
- Same [naturalistic prompt](../pi-prompts/pi-durable-naturalistic.md), SHA-256 `cb9db6d235cdd1302c27d3f96e02b147009e3ff548c1a99e00e6320a691dcfc4`; same [independent acceptance contract](acceptance.md), same required outputs and 2/3 joint threshold.
- Observed model: `openai-codex/gpt-5.6-luna`, the existing recorded exception after Spark rejection before tools. High thinking, JSON strict mode, runtime-only payload, 300-second limit.
- Native evidence: Windows 11 build 26200, Node 24.18.0, Pi 0.84.2, Git Bash/MinGW forward shell. No macOS native execution evidence.
- All three trials ran concurrently in separate workspaces. Canonical sources, prompts, and acceptance rules stayed frozen until completion.
- The assigned harness cache stayed at repository-local `evaluations/runs/pi-durable-cache/uv`. npm installation caches were local to each generated project through `service_project.py`.

## Results

| Trial | Pi exit | Duration | Exact outputs / integrity | Tool errors | Independent | Joint |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | 0 | 122.156 s | pass / pass | 2 | pass | fail |
| B2 | 0 | 132.488 s | pass / pass | 2 | fail | fail |
| B3 | 0 | 116.464 s | pass / pass | 0 | pass | pass |

All streams contain valid JSON, show the correct observed model, and satisfy the prompt-first and direct-read policies. No direct read accesses acceptance examples, sibling skills, repository documents, or credentials. B2 additionally ran an unnecessary `git status --short` against the ambient repository after generating its artifacts; it did not use that result as a task dependency. This is retained as a context-hygiene issue. No outside-workspace npm error-log write was observed in this cohort.

All three use `service_project.py` for dependency installation/build, offline smoke, and both platform plans. Their generated projects compile again under the independent evaluator, and their compiled CLI help matches the documented operations. The three saved smoke reports show `passed:true`, `eventJobs:1`, `duplicateJobs:0`, `sameTaskConversation:true`, `humanSubmissionDeduplicated:true`, `reopenProviderCalls:0`, and `nativeServiceRegistered:false`. Scoped native process-table checks found zero residual `serve` processes in all three workspaces.

Evaluator limitation identified before subject C: independent npm rebuilds in this cohort used plain `npm.cmd run build` without an explicit `npm_config_cache`. Successful npm commands can emit default-cache logs, so evaluator cache writes were not fully scoped by environment. No external cache files were removed or modified by cleanup. The forward wrapper used local caches correctly and its recorded failures remain unchanged. Final-cohort independent rebuilds must set the cache explicitly.

## Independent artifact findings

Every config selects service/agent `atlas-reviewer`, allowlisted repository `acme/widgets`, faux provider, PR polling at 60,000 ms, and initial baseline. Private findings have no publishing or merging capability. Both platform plan wrappers contain `executed:false`, complete artifacts and lifecycle actions, and a target `deploymentConfig` with matching service identity and state directory. Their paths match the prompt, including Node paths containing spaces, the macOS Application Support directory, home `/Users/alex`, and `gui/501` LaunchAgent target.

B1's guide correctly applies the platform `deploymentConfig`, quotes Windows PowerShell executable paths with the call operator, gives both platform lifecycles and task/control chats, explains correction versus follow-up, stable message retry IDs, one owner, duplicate events, restart recovery, idle model silence, and awake/login constraints. Its failures occur earlier in the trace, so independent artifact success cannot make it a strict pass.

B2's guide correctly applies deployment configuration and service identity and has useful lifecycle and chat commands. It omits laptop awake/sleep limitations, however, and describes the opened-event semantic key as including a PR revision. The shipped key identifies the opening of the PR by repository and number, without a revision SHA. Retain these as an artifact failure under the existing acceptance contract. Native plan command arrays themselves remain correct.

B3's guide covers platform configuration, properly quoted Windows commands, all lifecycle actions, one owner, saved task chat, busy policies, restart/event deduplication, credentials/database/log paths, idle behavior, and awake/login limits. Its verification includes the observed human submission deduplication and task-conversation recovery from the smoke report. It accurately distinguishes Windows-local smoke and generated plans from native OS service installation and macOS verification. This run meets both the strict and independent gates.

## Exact failures

| Trial | Event call line | Failure | Classification |
| --- | --- | --- | --- |
| B1 | 162 | Reads nonexistent `service/config.example.json`; the generated config is `service/config.json`. | agent |
| B1 | 2903 | Handwritten Python assertion embeds Windows paths as ordinary strings; escapes such as `\a` change the comparison, producing `AssertionError` despite correct generated plan paths. The agent later repairs its assertion using raw strings. | agent |
| B2 | 653 | Writes macOS `userId` as JSON string `"501"`; positive-integer validation rejects it. The agent then changes it to numeric `501`. | agent |
| B2 | 2733 | Handwritten validator looks for `plan.deploymentConfig`; the actual result has sibling properties `plan` and `deploymentConfig`, producing `KeyError`. | agent |

No helper build/smoke failure, MSYS target-path conversion error, model mismatch, missing required output, payload mutation, timeout, unavailable npm package, live GitHub request, service registration, or real review-model invocation was observed. Corrections inside failed trials are retained and do not waive their earlier errors.

## Commands and evidence

The three exact helper invocations use the following command, with `N` equal to `1`, `2`, and `3`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261019-pi-durable-naturalistic-v2-luna-N --expect-output service/config.json --expect-output OPERATIONS.md --expect-output plans.json --timeout-seconds 300
```

Raw evidence remains under `evaluations/runs/20261019-pi-durable-naturalistic-v2-luna-N/`: manifests, event streams, stderr, exact artifacts, skill-integrity checks, strict results, and unchanged generated workspaces. Evaluator findings are recorded in `independent-check.json` and `read-surface-summary.json` in each run folder.

Each stream was independently summarized with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261019-pi-durable-naturalistic-v2-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

B1/B2 summarizers correctly exit one for recorded tool errors; B3 exits zero. The evaluator also rebuilt each generated service with `npm.cmd run build`, executed `node dist/src/cli.js help`, parsed config/plans/smoke JSON, inspected all operations guides and shell commands, and checked the scoped process table. Neither native deployment plan was executed.
