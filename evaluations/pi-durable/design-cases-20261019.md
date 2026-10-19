# Pi Durable design cases: initial subject, 2026-10-19

The initial frozen runtime bundle passed **3/3 generalization runs**. Its boundary run did not pass: it searched outside the isolated workspace for another run's installed package, produced no required outputs, and exceeded its configured timeout. Preserve this result separately from the later revised bundle.

## Subject and method

- Skill: `pi-durable`, runtime payload, 21 files, excluding `assets/examples/`.
- Payload SHA-256: `d4f3b962268b6b9cea46f1175c9e5547b0e0ae89e627e18e79744b5afe8d02ce`.
- Model: observed `openai-codex/gpt-5.6-luna`, thinking `high`, strict JSON mode, fresh workspace per run.
- Model exception: the preceding retained `20261019-pi-durable-contract-spark-2` run was rejected by the provider before any tool call because Spark was unavailable for the account. The deliberate Luna exception is recorded in `SKILLS.md`. The rejected Spark run is not a skill pass.
- Host: Windows 11 build 26200; Node 24.18.0; Pi 0.84.2. No native macOS execution.
- Acceptance: [independent acceptance contract](acceptance.md), unchanged during grading.

## Results

| Run ID | Strict result | Independent artifact/read review | Duration |
|---|---|---|---|
| `20261019-pi-durable-generalization-luna-1` | Pass | Pass | 76.772 s |
| `20261019-pi-durable-generalization-luna-2` | Pass | Pass | 84.861 s |
| `20261019-pi-durable-generalization-luna-3` | Pass | Pass | 69.906 s |
| `20261019-pi-durable-boundary-luna-1` | Incomplete, timeout | Fail: isolation violation; missing outputs | 353.003 s wall time including timeout cleanup |

All three generalization runs produced exact nonempty `adapter-contract.json` and `operations.md` files. An independent PowerShell `ConvertFrom-Json` parse succeeded for every contract. Manual artifact review confirmed the six CI fields, failed-event selection, delivery-versus-build identity, one investigation for the supplied duplicate deliveries, a separate build-101 investigation, durable admission before acknowledgement, saved Pi mapping/request IDs, restart reconciliation, bounded log access, same-conversation chat and busy policies, idle behavior without model calls, and feasible per-user lifecycle choices.

Each output assessed the existing Codex console destination honestly: a local registry/chat host is feasible, while native Codex task/sidebar registration needs another supported integration. No output claimed that the custom CI adapter, that bridge, or either operating-system service had been implemented or activated.

Generalization traces used 11, 12, and 11 tool calls respectively, with zero reported tool errors. Their read surfaces were the prompt, `SKILL.md`, and five focused references: event-service architecture, service lifecycle, version compatibility, runtime decisions, and template operations. They did not read template source, acceptance fixtures, sibling skills, or repository documentation. Bash calls observed the platform, validated generated JSON, and in two cases queried Git status for explicit generated paths. Strict checks confirmed exact paths and unchanged skill payloads. Each retained run has a passing `read-surface.json` summary.

## Boundary failure and cleanup

The boundary run read the bundled compatibility information but continued looking for installed declarations. Its captured command enumerated `/c/Users/villa/dev/skills/evaluations` and returned declaration paths from the sibling contract run's `node_modules`. This constitutes an independent isolation failure even though shell-level reads are not fully represented by read-tool path checks. It produced neither `compatibility.json` nor `operations.md`.

The 240-second subprocess timeout killed the `pi.cmd` parent while its Node descendant retained capture-pipe handles, preventing the helper from finishing timeout reporting. Only the verified owned descendant was stopped: PID 17776, creation time matching this run, parent PID 20688 already absent, and the expected Pi/Luna command line. That released the helper and retained its partial JSON events, manifest, unchanged-payload result, and `evaluation-result.json` with `timedOut: true`. The independent isolation failure is classified **agent**; the delayed Windows process-tree timeout cleanup is a separate **harness** limitation. The evidence does not establish a model/provider outage.

## Reproduction commands

Set the cache within the repository and run from its root:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-generalization.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261019-pi-durable-generalization-luna-1 --expect-output adapter-contract.json --expect-output operations.md --timeout-seconds 240
```

The second and third generalization commands differed only in the final run-ID repetition. The boundary command used `evaluations/pi-prompts/pi-durable-boundary.md`, run ID `20261019-pi-durable-boundary-luna-1`, and exact outputs `compatibility.json` and `operations.md`, with the same remaining flags.

For each completed generalization run, the evaluator executed:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!pi-durable([\\/]|$))'
Get-Content -Raw evaluations/runs/<run-id>/workspace/adapter-contract.json | ConvertFrom-Json
```

Raw runs remain under ignored `evaluations/runs/<run-id>/`, including manifests, artifact hashes, traces, integrity checks, and generated artifacts. These design cases establish isolated selection and transfer of instructions; they do not establish native lifecycle behavior, live-provider review quality, or a working custom file adapter.
