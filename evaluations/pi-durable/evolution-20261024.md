# Independent agents and requested evolution validation, 2026-10-24

The skill now generates a complete independent application and an executable requested-improvement workflow. Keep status **`validating`**: deterministic implementation checks pass, while the scoped naturalistic authoring cohort retains workflow/output failures and native macOS/live-provider quality remain unverified. The [October 19 publication](publication-20261019.md) is separate historical evidence.

## Delivered behavior

The generated application carries source, pinned dependencies/lockfile, its own `AGENTS.md`, prompt files, build/smoke/service/chat/evidence/evolution commands, a project-local operations helper and portable initial SHA-256 provenance. Its runtime does not load this skill, the originating repository, or an original chat. A move test copies only current application files to a path with spaces and operates it from an unrelated working directory. Ordinary npm commands use the project's `.npmrc` cache.

`state/evidence.sqlite` stores append-only public operational records: IDs, timestamps, jobs/submissions, tool successes/failures, public model outputs, user feedback, explicit brief decision summaries and supporting references. Raw tool outputs are hashed/summarized. Thinking blocks are excluded and supported credential forms are redacted. Full source/prompt/tool/dependency manifests are stored once under `state/versions/`, with compact references in traces. `list_evidence` makes real conversation-scoped IDs available to the model before `record_decision` uses them. These are observable summaries, not access to private reasoning.

`npm run evolve -- ...` implements a trusted request, bounded selected evidence and source pack, optional no-tool model reflection, inactive proposal import, paired baseline/candidate builds and a frozen verifier/fixture comparison, source promotion, interrupted activation recovery and exact rollback. Requests and subsequent artifacts bind configuration/source/evidence/verifier hashes and exact file preimages. Evaluation checks copied sources and separate verifier/fixture copies before and after both sides. Activation rejects a live owner, pending catalog jobs and unfinished pinned-1.3.0 durable tasks/control submissions. Management/security/validation files are outside the candidate surface.

Promotion changes source and reports `buildRequired`; rebuild and smoke before restarting. Existing conversations can keep earlier prompt configuration while tool implementations resolve from the current host, so compatibility and deliberate migration remain required. Rollback restores source, not past remote effects or compiled JavaScript. Normal host code execution and best-effort process-tree cleanup are explicitly described; separate workspaces are not a security sandbox.

The optional `reflect --generate` uses the configured provider in a separate durable conversation with no tools, stable request IDs and inactive complete bounded draft files. Faux produces a clearly marked demonstration with no candidate. The bundled verifier measures literal prompt contracts only; its passing score does not establish improved model decisions. Real usefulness needs application-specific held-out cases and intended-provider measurements. Improvement is never triggered by ordinary PR text or idle waiting.

## Frozen subjects

| Subject | Runtime | Full bundle | Role |
|---|---|---|---|
| Evolution A | 35 files, `c69bef42a99f4e945408b4ad3808417dbbd9029e50a6877759ad202c6f63395c` | 43 files, `f42895ef44d0cfeae56c030c7f1a5b349e259b5d83b06f5908df1a99f8825043` | First scoped contract and three naturalistic runs |
| Evolution B, final | 36 files, `9f09964e7a8a476ad8c466008701bcf51be77cab3a06d5804456676fb5337c4a` | 44 files, `2323fff441dca39169e087119d0892b0c497042144a960bb63e374c9b770ffa2` | Adds project `.npmrc` and verifies its cache after relocation |

The B change addresses an observed pattern: successful raw npm commands can create default-cache logs outside an otherwise isolated workspace even after an earlier install used `--cache`. Helpers already set a local cache; the project setting also covers subsequent ordinary npm operations. A/B results are not pooled and failures are not waived.

The forward model is the existing documented `openai-codex/gpt-5.6-sol` exception after the retained Spark account/provider rejection and unsuccessful Luna workflows. No authentication or model catalog was modified. The independent [scope contract](evolution-acceptance-20261024.md), exact outputs, zero-error/isolation/integrity gates and 420-second deadline were fixed before these runs.

## Deterministic evidence

Final B compiles and passes **70/70 tests**, zero failures/skips, in a fresh scaffold. The packaged smoke passes. The source/runtime/full authoring audits report zero issues. The evaluator independently verifies all **33 initial application-file hashes**, including acceptance sources, and verifies the initial provenance contains no absolute generation destination.

| Checks | Count | Main exercised behavior |
|---|---:|---|
| Existing service/adapter/lifecycle | 48 | Real Harness/SQLite, process death/reopen, queue/chat deduplication, HMAC/polling/deadline, owner exclusion, native Windows wrapper |
| Evidence | 6 | Append-only durability, redaction/bounds, portable versions, real visible decision IDs and tool success/failure hooks, historical prompt identity |
| Evolution engine | 11 | Explicit request, inactive import, paired measurement, stale/tampered/failed refusal, owner/jobs/control gate, interrupted multi-file journal, exact rollback, copied verifier integrity, bounded process execution and evidence selection |
| Integrated configuration/reflection/API | 4 | Relative prompt configuration, real no-tool faux reflection/reacquisition, complete long script drafts, private-field exclusion, authenticated feedback and no-request model silence |
| Relocation | 1 | Current application copied without skill, project-local build/smoke/plan/evolution help, paths with spaces, local npm cache |

An earlier integration run passed 69/70: the model-reflection SQLite path exceeded the observed Windows path tolerance. The correction uses a short hash-derived filename with a separate full-digest identity check. The failing log remains at `evaluations/runs/pi-durable-evolution-20261024/tests.log`; repaired and fresh final runs are retained. Static drafts also exposed missing contents formatting and a generated-path reference that needed an in-bundle link; these were fixed before forward-test freezes.

Final raw implementation evidence is under `evaluations/runs/pde-20261024-cache/`: `prepare.log`, `smoke.log`, `tests.log`, `authoring-audit.json`, and gate/sync logs. The original pre-cache final run remains under `pde-20261024-final/`. Additional focused test logs from the independent owners remain in `pi-durable-evolution-dev/` and `pi-durable-evolution-engine/`.

## Isolated authoring evidence

Evolution A contract `20261024-pi-durable-independent-contract-sol-1` passed strict JSON/model/output/integrity gates and produced a correct moved project, proof and operations guide. It completed in 136.095 seconds. Independent scope review nevertheless attributed global npm logs to its raw `npm run build`, `npm run smoke` and `npm run evolve -- --help` commands. It therefore does not receive a complete joint pass. No outside logs were deleted or modified.

The [three A naturalistic runs](evolution-naturalistic-20261024.md) have **0/3 complete joint passes**. Every agent placed `improvement-request.json` and `EVOLUTION.md` inside `worker/` instead of the exact workspace-root paths. Two runs also have retained tool errors; one has an attributed raw-npm external-cache write. All three generated worker configurations and substantive guides pass separate functional inspection, and independent local builds/CLI help/smokes pass 3/3. Functional diagnostics do not override the fixed exact-output/workflow gate.

Evolution B contract `20261024-pi-durable-independent-cache-sol-1` completed in 176.360 seconds with every exact output, correct artifacts, immutable payload, passed independent rebuild/CLI/smoke review and passed cache/process scope audit. It still **fails strict acceptance** because the agent invoked the unsupported service-CLI `--help` form instead of its documented `help` command. This single tool error remains an agent failure; no reroll was performed. The generated project helper and evolution `--help` worked. The final scope receipt confirms no default global npm-log modifications during the exact run window and no residual task/service processes. An initial evaluator date-parsing receipt is retained and explicitly superseded by its corrected UTC-only scope check; it does not alter the recorded strict failure.

No naturalistic B cohort was silently substituted for A, and no old platform or model-quality result was promoted to current evidence. The changed skill remains `validating`.

## Reproduction and limits

```powershell
uv run --script skills/pi-durable/scripts/scaffold.py evaluations/runs/pde-20261024-cache/workspace --with-tests
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pde-20261024-cache/workspace prepare
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pde-20261024-cache/workspace smoke
# Run npm test inside the generated project, with its local cache.

uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-independent-contract.md --mode json --strict --model openai-codex/gpt-5.6-sol --run-id 20261024-pi-durable-independent-cache-sol-1 --expect-output agent/scaffold-manifest.json --expect-output agent/scripts/project.py --expect-output agent/src/evolution.ts --expect-output proof.json --expect-output OPERATIONS.md --timeout-seconds 420
```

Use an empty destination for recreation. The naturalistic report lists every repetition and exact command. Event captures, independent receipts, failed outputs and copied immutable payloads remain in ignored `evaluations/runs/`.

Repository checks cover skill metadata/resources, independence, payload, pattern IDs and the evaluation harness. Local installation sync/check is required after source changes. Native macOS startup, real provider reflection/review quality, live GitHub, production promotion, arbitrary orphan-process containment and Codex-sidebar integration are not established by these offline tests.
