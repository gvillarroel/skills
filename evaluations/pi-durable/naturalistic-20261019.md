# Pi Durable naturalistic forward cohort — 2026-10-19

Subject A does **not** meet release acceptance: strict 0/3, complete independent 0/3, joint 0/3 against the unchanged minimum of 2/3. All three agents produced the exact requested artifacts and eventually built the generated service, but their traces contain tool errors. Two runs also caused npm to write its default error log outside the workspace. Preserve these attempts as failures; later repairs require a new frozen subject and fresh runs.

## Frozen inputs and environment

- Skill: `pi-durable`, runtime profile, 21 files; acceptance fixtures excluded.
- Runtime payload SHA-256: `d4f3b962268b6b9cea46f1175c9e5547b0e0ae89e627e18e79744b5afe8d02ce` in every run manifest.
- Prompt: [`../pi-prompts/pi-durable-naturalistic.md`](../pi-prompts/pi-durable-naturalistic.md), SHA-256 `cb9db6d235cdd1302c27d3f96e02b147009e3ff548c1a99e00e6320a691dcfc4`.
- Independent contract: [`acceptance.md`](acceptance.md), naturalistic and shared gates, unchanged during this cohort.
- Observed model: `openai-codex/gpt-5.6-luna` for all three runs. This is the backlog-recorded exception after Spark was rejected before tools; strict model verification remains enabled.
- Harness: Pi 0.84.2, high thinking, JSON strict mode, 300-second limit. Native host: Windows 11 build 26200, Node 24.18.0; forward shell: Git Bash/MinGW. No native macOS execution evidence.
- Harness `UV_CACHE_DIR`: repository-local `evaluations/runs/pi-durable-cache/uv`, as explicitly assigned for this evaluation. This inherited harness cache is separate from the accidental default npm-cache writes below.
- N1 ran first; N2 and N3 then ran concurrently in independent workspaces, with the same frozen payload and prompt. Each had its own generated service and npm installation. No source, prompt, or acceptance changes were made during these runs.

## Results

| Repetition | Pi exit | Duration | Exact outputs | Skill unchanged | Tool errors | Artifact grade | Joint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N1 | 0 | 152.446 s | pass | pass | 3 | fail | fail |
| N2 | 0 | 179.378 s | pass | pass | 6 | fail | fail |
| N3 | 0 | 203.226 s | pass | pass | 3 | pass | fail |

All event streams contain valid JSON, show the requested model, begin by reading the task and skill entry point, and avoid forbidden read surfaces. No run read `assets/examples/`, sibling skills, repository documentation, pre-existing credentials, or unrelated project sources. Reads of generated service source remained inside each workspace. Artifact-only acceptance is 1/3; the N3 artifact pass does not waive its tool errors or workspace-write failure. Complete independent acceptance includes the shared scope gate and is 0/3.

The evaluator parsed `service/config.json` and `plans.json` independently in each run, read every operations guide, rebuilt every generated project with `npm.cmd run build`, and ran each compiled CLI's `help`. All three independent builds exited zero. Scoped native process-table checks found no remaining `serve` process in any of the three workspaces. These checks do not imply Windows Task Scheduler or macOS launchd registration was tested.

Evaluator limitation identified before the final subject C cohort: these independent npm rebuilds did not explicitly set `npm_config_cache`. Successful npm commands can also emit default-cache logs, so evaluator cache writes were not fully scoped by command environment. No external cache files were removed or modified by cleanup. This does not alter the retained failed forward-trial grades; final-cohort independent commands must set their workspace-local cache explicitly.

All configurations correctly select `atlas-reviewer`, repository `acme/widgets`, the faux provider, polling every 60,000 ms, and an initial baseline. Their private-review scope stays within allowlisted reads. Both native plan artifact sets use the supplied future project/config/state/Node paths, a Windows per-user logon task, and the macOS user LaunchAgent with UID 501 and `/Users/alex` home. Neither OS plan was executed.

## Failure evidence and classification

### N1

Three strict tool errors occur at event-call lines 796, 977, and 3036:

1. Git Bash converts the `/Users/...` arguments of a macOS CLI planning call before native Node receives them. The planner reports `projectDir must be an absolute path without control characters`.
2. The attempted workaround omits `cd service`, so Node cannot find `workspace/dist/src/cli.js`.
3. An improvised offline smoke script assumes the jobs endpoint returns an array. The actual shape is `{jobs:[...]}`; the script exits one before the agent repairs it.

The final guide's lifecycle examples omit `--name atlas-reviewer`, selecting the template's default service name `pi-agent-service` instead. Its macOS examples also omit the target state directory while the deployed config is left described as `./state`, diverging from the requested Application Support state and logs. Laptop sleep limits are absent. These are artifact failures despite valid plan JSON and a successful build.

Classification: agent command/cwd/API-shape errors, with a reusable skill portability/documentation gap around cross-platform arguments and preserving deployment identity.

### N2

Six strict tool errors occur at lines 573, 604, 978, 1140, 1572, and 2899:

1. npm is invoked from the workspace root, where there is no `package.json`. The npm error reports a log under `C:\Users\villa\AppData\Local\npm-cache\_logs\`, outside the workspace. The evaluator did not alter or remove that external file.
2. A build is attempted before dependencies are installed in the service, producing `tsc is not recognized`.
3. Three attempts fail the macOS absolute-path check after MSYS conversion, including a direct `createServicePlan` evaluation.
4. A custom offline smoke check mishandles the returned job data and exits two after correctly observing one initial receipt and an empty duplicate receipt.

The final guide carries the service name and explains the macOS config state override and laptop limits. Its Windows lifecycle commands start with an unquoted `C:\Program Files\nodejs\node.exe`, however, so those concrete shell instructions do not invoke the requested executable. The generated plan's structured command arrays remain correctly quoted at their own execution boundaries.

Classification: agent working-directory, sequencing, quoting, and response-shape errors; the common MSYS issue is a skill portability gap. The external npm-cache log is a shared-gate write-scope failure, not package infrastructure unavailability.

### N3

Three strict tool errors occur at lines 506, 869, and 1249:

1. npm is invoked from the wrong working directory and writes its reported default error log outside the workspace, as in N2.
2. Two macOS planning commands fail after MSYS path conversion.

The final artifacts satisfy the naturalistic artifact criteria: correctly quoted Windows cmd examples, consistent service name, explicit target macOS `dataDir` adjustment, complete lifecycle plans, job chat and busy-policy commands, stable IDs, one owner, restart recovery, login/awake limits, credential/database/log paths, and an honest Windows-only verification record. The artifact pass does not erase earlier workflow errors or the external npm-cache write.

Classification: agent working-directory/write-scope failure plus the shared skill portability gap. No external service failure or unavailable npm dependency was observed.

## Commands and retained evidence

Run the following exact helper command with `N` replaced by `1`, `2`, and `3` for the three recorded run IDs. The executions used the same arguments and environment shown here:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261019-pi-durable-naturalistic-luna-N --expect-output service/config.json --expect-output OPERATIONS.md --expect-output plans.json --timeout-seconds 300
```

Every raw run is retained under `evaluations/runs/20261019-pi-durable-naturalistic-luna-N/`, including `run-manifest.json`, `events.jsonl`, stderr, artifact/event/integrity checks, and `evaluation-result.json`. Evaluator evidence is added as `independent-check.json` and `read-surface-summary.json`; the three generated workspaces remain intact.

The event summarizer was executed for each raw stream:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261019-pi-durable-naturalistic-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

All three summarizer invocations correctly exit nonzero for recorded tool errors. Expected outputs remain exactly `service/config.json`, `OPERATIONS.md`, and `plans.json`. No acceptance threshold, output path, scope rule, or zero-error gate was relaxed.

## Transferable repair targets

Before another frozen cohort, reduce the amount of shell and API improvisation required: accept target options from a local JSON file, preserve service identity and target `dataDir` in generated deployment guidance, document per-platform executable quoting, and provide an offline smoke helper that understands the API's object envelopes. Make installation/build commands explicitly project-scoped and keep every npm invocation's cache inside its workspace. Validate a new subject with fresh repetitions; never relabel these three attempts as passes.
