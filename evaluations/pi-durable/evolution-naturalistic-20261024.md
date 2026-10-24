# Pi Durable independent worker and requested evolution: naturalistic trials

Date: 2026-10-24. Model: `openai-codex/gpt-5.6-sol`, thinking `high`, using the model exception recorded in `SKILLS.md`. The three fresh trials used the unchanged [naturalistic prompt](../pi-prompts/pi-durable-evolution-naturalistic.md) and [independent acceptance contract](evolution-acceptance-20261024.md). No failures were replaced and no older Pi Durable cohort was pooled with these results.

The frozen runtime payload contained 35 files with SHA-256 `c69bef42a99f4e945408b4ad3808417dbbd9029e50a6877759ad202c6f63395c`. Its corresponding full payload had 43 files and SHA-256 `f42895ef44d0cfeae56c030c7f1a5b349e259b5d83b06f5908df1a99f8825043`. The prompt SHA-256 was `f3026284d85037504c378c9f8e46ed0b51e5dc5fc37f8ddb2acc1fc9a2e110ee`. Each run manifest independently confirms the same runtime file count, payload hash and prompt hash. Later source changes, including any npm cache hardening, form a different subject and cannot change these results.

## Outcome

The cohort failed the fixed release threshold: **0/3 strict passes, 0/3 independent artifact passes, and 0/3 complete joint passes**, against the required minimum of two joint passes. All three agents created the requested improvement input and guide under `worker/`, while the required paths were `improvement-request.json` and `EVOLUTION.md` at the workspace root. The exact-output failures remain failures even though the nested documents were substantive and usable.

| Run suffix | Duration | Strict | Exact artifacts | Complete joint | Additional retained failure |
| --- | ---: | --- | --- | --- | --- |
| `natural-sol-1` | 191.682 s | Fail | Fail | Fail | One shell tool error while checking relocation cleanup; the agent subsequently cleaned up. |
| `natural-sol-2` | 205.637 s | Fail | Fail | Fail | One nonexistent prompt-file read; an unscoped `npm ls --depth=0` also wrote to the default global npm cache. |
| `natural-sol-3` | 171.204 s | Fail | Fail | Fail | No tool errors; the two wrong output paths still fail acceptance. |

All runs have prefix `20261024-pi-durable-evolution-`. Each Pi process exited successfully without timeout. The strict event gate passed only trial 3 because trials 1 and 2 each contained one tool error. Valid JSON/model observation and copied-skill immutability passed in all three runs. These observations distinguish agent execution success, artifact correctness and the complete acceptance result.

## Functional and documentation diagnostics

Independent examination of the files at their actual nested locations found the requested functional configuration in **3/3** trials:

- The agent ID is `reviewer`, the provider is `faux`, and GitHub detection is `off`.
- `instructionsFile` names a real project-local `prompts/pr-reviewer.md`. Importing the generated compiled configuration loader confirmed that the effective instructions equal that file's contents.
- The future request names `reviewer`, permits exactly the active prompt, and names existing `evaluation/local-verifier.mjs` and `evaluation/mechanics-cases.json` files. The fixture points to the same active prompt. Each request uses a positive `minimumImprovement` of `0.01` and bounded `timeoutMs` of `120000`, with no fabricated trace or evaluation IDs.
- Every agent used the generated project's own operation helper for dependency preparation/build, offline smoke and evolution CLI help. No post-generation operation required a skill helper. Every agent additionally demonstrated a relocated project copy and removed its temporary copy.
- Original smoke results report one admitted event, zero duplicate jobs, a retained task conversation, deduplicated human submission, zero provider calls after reopen, `faux`, and no native service registration.
- The independent evaluator rebuilt all three projects, inspected their compiled service/evolution CLI help and reran the packaged smoke with project-local npm caches. All checks exited successfully.

The three guides correctly describe persistent public evidence, concise decisions with retrievable supporting IDs, feedback, secret/private-thinking boundaries, an explicit trusted request, inactive reflection and proposals, paired baseline/candidate checks using frozen fixtures, stale-source rejection, stopped/drained activation, rebuild/smoke before restart, interrupted recovery and exact rollback. They distinguish a stored conversation's earlier prompt version from the current host's tool implementation. They do not claim that reflection or a faux run proves improved review decisions.

The guides accurately limit the bundled verifier to literal prompt-contract mechanics. They call for application-specific review-quality evidence such as expert-labeled PR/diff cases, missed-defect and false-positive measures, severity/location accuracy, security regressions, tool-use/cost measures, held-out cases and intended-provider comparisons. These strong diagnostics do not override wrong output paths or workflow-scope failures.

## Trace and scope review

The separate JSONL summarizer confirms valid event JSON and the requested observed model in all trials. Trial 1's shell error came from checking that a temporary relocation directory had been removed after a shell trap used a changed working directory; an explicit cleanup fixed the local residue. Trial 2 initially probed `worker/prompts/reviewer.md`, which does not exist, before using the actual prompt path.

Trial 2 later ran raw `cd worker && npm ls --depth=0` without a local cache argument/environment. Read-only inspection attributed `C:/Users/villa/AppData/Local/npm-cache/_logs/2026-10-24T13_46_45_602Z-debug-0.log` to that exact trial's worker directory. This is a real write outside the requested workspace and an agent workflow/scope failure, separate from its strict tool and artifact failures. No external npm files were modified or removed by the evaluator. Other global npm logs observed during the same time window belonged to the concurrently evaluated contract case and are not pooled into this cohort.

The principal dependency/build/smoke commands used project-local helper caches in all three trials. Trace review found no live GitHub requests, target-agent real-model calls, native registration, candidate execution or promotion. Target applications remained faux/off. Authoring itself used the recorded Pi model as intended by the test harness. An owned-process ancestry audit and a final command-line audit found no remaining trial processes. No service cleanup or process killing was needed.

## Commands and retained evidence

Each repetition used this command, substituting `N` with `1`, `2`, or `3`; the deadline and outputs were fixed before execution:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evolution-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-sol --timeout-seconds 420 --run-id 20261024-pi-durable-evolution-natural-sol-N --expect-output worker/config.json --expect-output worker/AGENTS.md --expect-output improvement-request.json --expect-output EVOLUTION.md
```

Each event file was then independently summarized:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-pi-durable-evolution-natural-sol-N/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-pi-durable-evolution-natural-sol-N/read-surface.json
```

The summarizer exited nonzero for trials 1 and 2 because of their retained tool errors, and zero for trial 3. Independent build/help/smoke checks ran from each generated `worker/` directory with `npm_config_cache` set to that worker's `.cache/npm` and an evaluator UV cache inside the workspace:

```powershell
uv run --script scripts/project.py prepare --skip-install
node dist/src/cli.js help
uv run --script scripts/project.py evolve -- --help
uv run --script scripts/project.py smoke
```

Raw evidence stays under ignored `evaluations/runs/20261024-pi-durable-evolution-natural-sol-N/`: `run-manifest.json`, `events.jsonl`, `event-check.json`, `artifact-check.json`, `skill-integrity-check.json`, `evaluation-result.json`, `read-surface.json` and `independent-check.json`. Each workspace retains the original agent smoke receipt as `agent-smoke-result.json`, the independent configuration-loader receipt, and independent build/help/smoke logs. Wrong-path artifacts remain in place rather than being repaired by the evaluator.

Evaluator scripts, npm-cache attribution and process-audit receipts are retained under ignored `evaluations/runs/pi-durable-evolution-dev/`. This cohort establishes useful offline functional diagnostics while explicitly failing the requested authoring contract. Native macOS lifecycle, real-provider reflection and useful review-quality improvement remain unverified by these trials.
