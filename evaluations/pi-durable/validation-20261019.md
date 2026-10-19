# Pi Durable skill validation, 2026-10-19

The reusable skill and service template are implemented and installed in the repository-local skill directory. Keep the backlog status **`validating`**: the deterministic template checks pass, but the final isolated authoring cohort does not meet the unchanged naturalistic and generalization thresholds. This is usable implementation evidence with explicit release limits, not a claim that every agent workflow or native deployment is certified. The later [publication review](publication-20261019.md) records a separate polling-timeout repair, the new frozen subject, 48 passing checks, and its retained scoped forward-test failure. The A/B/C results below remain historical evidence for their exact hashes.

## Delivered scope

The canonical bundle is [pi-durable](../../skills/pi-durable/SKILL.md). Six focused references cover runtime selection, event-service architecture, GitHub events, native lifecycle, template operations, and release compatibility. The bundle includes a standalone scaffolder, a portable project helper, a pinned TypeScript service template, aligned UI metadata, and four acceptance-test sources.

The service provides named-agent discovery, a durable event/job catalog, per-agent Pi Harness storage, stable job-to-conversation mapping, request deduplication, private task chat, control chat, steering, visible failures, and recovery after process interruption. GitHub polling supports baseline/catch-up and checkpoint boundaries; webhooks verify raw-body signatures before admission. Idle waiting belongs to the host and does not require model generation. The included worker exposes a repository-allowlisted GitHub read tool.

Windows deployment uses a per-user Scheduled Task. macOS uses a per-user LaunchAgent. Plans include install/start/stop/status/uninstall actions, state/log paths, ownership checks, and quoted arguments. They start at login and cannot provide continuous availability while the user is logged out or the laptop is asleep. The shipped console is the service's own CLI/API; arbitrary insertion of Pi conversations into the Codex sidebar requires a supported bridge that this bundle does not implement. A local CI-file adapter is an extension design, not an existing GitHub-adapter capability.

## Frozen subjects and model exceptions

| Subject | Runtime files | Runtime SHA-256 | Change boundary |
|---|---:|---|---|
| A | 21 | `d4f3b962268b6b9cea46f1175c9e5547b0e0ae89e627e18e79744b5afe8d02ce` | Initial runnable bundle |
| B | 23 | `6f25c64a9f600c4837a43dde9e9f4c78d23aba46ee320046db78da2a87fc57fa` | Portable prepare/smoke/JSON-plan helpers and operations guidance |
| C, final | 23 | `b6fa474c26b9a3dfc3ae3920b3a4edcb145ad132e0028ba23e0c8dc4f267590d` | Narrow offline compatibility-evidence and authorized-search guidance |

The full source contains 27 files: the 23-file runtime plus four acceptance sources under `assets/examples/service-acceptance/`. Normal forward tests excluded those examples. No canonical source changed during the C cohort. The later publication correction has a separately identified hash and is not pooled with C.

The mandated Spark attempt `20261019-pi-durable-contract-spark-2` was rejected before tools because the model is unsupported with this ChatGPT-account provider. An earlier Spark preflight attempt did not reach the model and is not runtime evidence. The deliberate first exception was `openai-codex/gpt-5.6-luna`. After its retained workflow failures, the final complex deployment-authoring exception was `openai-codex/gpt-5.6-sol`, available in the local Pi catalog. Both exceptions are recorded in `SKILLS.md`. Model and subject results are separate; no threshold was lowered and no unsuccessful repetition was replaced.

## Deterministic and native Windows evidence

The generated development project at `evaluations/runs/pi-durable-development/workspace/` compiles and passes **44/44 tests**, zero failures or skips. The final test log is `workspace/test-subject-b.log`; C changed only compatibility prose after this code/test freeze.

| Area | Checks | Evidence exercised |
|---|---:|---|
| GitHub adapter | 21 | Real local HTTP, pagination, baseline/catch-up, partial failures, retry timing, ETag, semantic deduplication, signed webhook admission |
| Service manager | 15 | Windows/macOS plan content, owned lifecycle mocks, collision/symlink refusal, native PowerShell AST and XML parsing, actual Windows Node runner with difficult paths, logs and exit code |
| Server/runtime | 7 | Real Pi Harness and SQLite, duplicate receipt/submission, authentication, atomic rollback, owner exclusion, older task chat, process-kill/reopen recovery |
| CLI | 1 | Both foreign-target JSON plans and matching deployment configuration |

The first development run had one invalid synthetic webhook fixture; its correction and failed log remain retained. The packaged offline smoke also passed from the development workspace: no idle model calls, one job for duplicate admission, human-request deduplication, and reopen of the saved thread. It uses the official faux provider, not a live model.

Representative commands, with npm cache scoped to the generated workspace:

```powershell
uv run --script skills/pi-durable/scripts/scaffold.py evaluations/runs/pi-durable-development/workspace --with-tests
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pi-durable-development/workspace prepare
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pi-durable-development/workspace smoke
# Run inside the generated project, with npm_config_cache set to its local cache:
npm test
```

These commands describe recreation in an empty destination; the scaffolder deliberately refuses an existing nonempty directory. No real Task Scheduler job or LaunchAgent was registered. Windows runner execution is narrower evidence than native scheduler installation/login behavior. Native macOS execution, live GitHub delivery, authenticated provider behavior, review quality, and external-console integration remain unverified.

## Final isolated authoring results

The [independent acceptance contract](acceptance.md) was fixed before the cohorts. Naturalistic and generalization each require two complete joint passes out of three fresh repetitions; contract and boundary run once. Exact outputs, strict JSON, observed model, zero tool errors, immutable copied payload, bounded reads/writes, independent artifact review, and platform honesty remain required.

| Final C / Sol case | Strict harness | Independent result | Joint result |
|---|---:|---|---:|
| Contract | 1/1 | 1/1 | 1/1 |
| Naturalistic deployment | 1/3 | 2/3 complete; all three artifact sets pass | 0/3 |
| Generalization to CI files | 0/3 within 240 s | Full acceptance not awarded after timeout; JSON parses 3/3 and literal fixture accepted 2/3 | 0/3 |
| Version/recovery boundary | 1/1 | 1/1 | 1/1 |

Contract run `20261019-pi-durable-contract-v3-sol-1` used the exact scaffolder, offline `contract-reviewer`, exact 1.3.0 dependency pins, and a compiled native Windows dry-run plan with `executed: false`. An evaluator-side rebuild and CLI-help execution passed. The author did not run the optional offline smoke and stated that limit accurately. Boundary run `20261019-pi-durable-boundary-v3-sol-1` correctly rejects all four absent 1.3.0 APIs (`runtime.sleepUntil`, `harness.wake`, `restartLimit`, `harness.retryTask`), gives available alternatives, and bounds offline evidence to the copied bundle. Both have root-owned `independent-check.json` and clean read-surface summaries in their raw run folders.

In the [final naturalistic cohort](naturalistic-v3-20261019.md), repetitions 1 and 3 produced correct artifacts but failed strict mode through repeated overescaped handwritten Windows-path assertions. Repetition 2 passed strict mode but a redundant raw npm build created a global npm log outside the authorized workspace, so independent scope review failed it. All three generated projects rebuilt successfully with evaluator-scoped caches, and all packaged smokes and deployment plans passed. These are retained agent-workflow failures, not passing release trials.

In the [final generalization cohort](design-cases-v3-20261019.md), all three helpers recorded timeouts at the configured 240-second limit. All requested files exist, captured trace summaries pass, and payloads are unchanged. Repetition 3 also invented a minimum-seven-character SHA rule that rejects the task's supplied six-character fixture; classify that separately as an agent artifact defect. Two Windows `pi.cmd` timeouts left verified owned Node children holding capture pipes; scoped cleanup released them. Delayed process-tree cleanup is a harness limitation. The available traces do not establish why execution exceeded its deadline or a provider outage. Completed agent-settlement events do not override the failed launcher deadline.

Earlier cohorts remain available in [initial naturalistic](naturalistic-20261019.md), [revised naturalistic](naturalistic-v2-20261019.md), [initial design](design-cases-20261019.md), and [revised design](design-cases-v2-20261019.md). A/Luna contract passed, naturalistic joint was 0/3, generalization 3/3, and boundary failed with timeout/outside-workspace discovery. B/Luna contract passed, naturalistic joint was 1/3, generalization 1/3, and boundary failed with tool errors/outside searches. Two exploratory B/Sol contract/boundary runs passed strict checks; they do not count toward C's release results. No cohorts are pooled.

Observed reusable difficulties were promoted before the final freeze: explicit project working directories and local dependency caches; native subprocess argv with target paths kept in JSON to avoid MSYS path rewriting; a packaged smoke with the real CLI response shapes; and bounded offline compatibility evidence when installed declarations are unavailable. Remaining final workflow failures are documented, not waived.

## Commands and retained evidence

The four unchanged prompts are under `evaluations/pi-prompts/pi-durable-{contract,naturalistic,generalization,boundary}.md`. Every raw manifest records the exact command, prompt hash, model, payload hash, expected paths, platform, tool versions, and dirty Git context. Case reports list all repetitions and their evaluator diagnostics.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-contract.md --mode json --strict --model openai-codex/gpt-5.6-sol --run-id 20261019-pi-durable-contract-v3-sol-1 --expect-output service/package.json --expect-output service/config.json --expect-output plan.json --expect-output verification.md --timeout-seconds 300
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261019-pi-durable-contract-v3-sol-1/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261019-pi-durable-contract-v3-sol-1/read-surface.json
```

Naturalistic trials use a 300-second deadline; design/boundary cases use 240 seconds. Raw runs, timeout captures, unchanged source copies, independent checks, cache-scoped rebuilds, and failed assertions remain under ignored `evaluations/runs/`. No generated output was repaired to turn a trial into a pass.

The separate [metadata routing smoke](source-routing-review-20261019.md) passes 10/10 positive/negative cases with Luna, no forced skill and no tools. This is bounded routing evidence, not a substitute for task effectiveness.

## Repository and bundle gates

These final commands pass:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
git diff --check
```

The evaluation harness regression passes 17 tests. Focused authoring audits of source, runtime copy, and full copy each report zero issues in `evaluations/runs/pi-durable-development/focused-authoring-audit.json`. Earlier global audits overlapped source edits and reported one `source-changed` diagnostic; retain them as preliminary evidence, not final passes. The local installation matches canonical source. No Pages example was published and no live service was installed.

Follow-up validation must address the retained isolated workflow failures with a newly frozen subject, preserve the earlier attempts, and verify native macOS and any requested live integration before expanding platform or provider claims.
