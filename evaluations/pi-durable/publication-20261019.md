# Pi Durable publication review, 2026-10-19

Publish the skill with status **`validating`**. This review adds a concrete polling robustness correction and reruns the machinery checks; it does not waive the retained isolated authoring failures or certify native macOS/live integrations. The [earlier validation record](validation-20261019.md) preserves subjects A/B/C and their original results.

## Completeness review and correction

Two independent source reviews checked the 27-file canonical skill for missing dependencies/resources, runtime reads outside the bundle, event admission and crash-recovery mapping, task-chat routing, authentication, native lifecycle ownership, and unsupported platform/console claims. No additional required bundle resource was missing.

The runtime review identified one defect: the serial repository polling loop could remain occupied indefinitely when GitHub sent headers but did not finish its response body. The adapter now applies a **30-second whole-repository deadline**, including all pages and success/error body reads. It combines that deadline with caller shutdown, clears the timer, reports retryable `poll_timeout` / HTTP 504, and leaves the existing checkpoint unchanged. Caller cancellation preserves its original reason. Adapter callers can supply a deliberate finite positive `timeoutMs`; the reusable polling reference documents the contract.

Four regressions cover a stalled later-page body followed by successful recovery, a stalled error body, shutdown after headers, and invalid deadlines. The focused GitHub suite passes **25/25**. The complete suite passes **48/48**, zero failures/skips. The generated project builds, its packaged offline smoke passes, and Windows runner/native parser checks remain included.

Seven documentation links targeted ignored SVG/PNG/JSON artifacts. They now identify reproducible local paths without broken GitHub links. The authored Mermaid sources, commands, project notes, pinned manifests, and probe sources are included with the guide. No generated media, database, cache, credentials, installed skill, or bulky evaluation run is part of publication.

## New frozen publication subject

- Runtime: 23 files, SHA-256 `de124d7c96c4c342d0618f57307c54fe0be3f890e987e438427decf3a8013966`.
- Full bundle: 27 files, SHA-256 `2dfaf157163ac6cf8e8009aca80f793f2dc1b19e2bf5e524c4d3546fb21daf51`.
- Differences from C: `src/github.ts`, the GitHub acceptance test, and `references/github-events.md` only.
- Native development platform: Windows 11, Node 24.18.0.
- Focused source/runtime/full authoring checks: all pass, zero issues.

The fresh runtime-only isolated contract attempt `20261019-pi-durable-contract-publication-sol-1` uses the unchanged prompt, its four exact output paths, strict JSON, and the already recorded `openai-codex/gpt-5.6-sol` exception. It completes in 139.110 seconds with unchanged payload and all exact outputs, but **fails strict acceptance** because one agent-written assertion uses `plan.platform` instead of the documented wrapper's `plan.plan.platform`. The agent later corrects its check; the original tool error remains a failure. There was no reroll or output repair.

Independent evaluation confirms exact dependency pins, offline configuration, coherent native Windows dry-run plan, current source bytes, successful rebuild/CLI help, and the saved smoke's event/message deduplication and task-thread recovery. Artifact quality passes. Full independent workspace-write acceptance was not awarded after the strict failure; the trace also contains raw `npm ls` without a workspace cache override. No actual external-cache write is inferred without attribution. The requested model is observed, event JSON is valid, the copied skill is unchanged, and direct reads remain limited to the prompt, focused skill references, and generated project/plan files.

This single scoped check does not replace the earlier naturalistic/generalization cohorts or establish passing release thresholds for the changed subject. Keep `validating`. Native macOS startup, real Task Scheduler installation/login, live GitHub, provider quality, and a Codex sidebar bridge remain outside the evidence.

## Commands and evidence

From the repository root, use an empty generated destination:

```powershell
uv run --script skills/pi-durable/scripts/scaffold.py evaluations/runs/pi-durable-publication/workspace --with-tests
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pi-durable-publication/workspace prepare
uv run --script skills/pi-durable/scripts/service_project.py evaluations/runs/pi-durable-publication/workspace smoke
# Inside the generated workspace, with npm_config_cache set to .cache/npm:
npm test
```

The publication workspace contains the passing build, `tests-repaired.log`, focused GitHub run, and `workspace/.cache/smoke-result.json`. The new isolated run retains manifests, the exact prompt, event capture, strict failure, immutable copied payload, generated artifacts, root-owned `independent-check.json`, and `read-surface.json` under ignored `evaluations/runs/`.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-contract.md --mode json --strict --model openai-codex/gpt-5.6-sol --run-id 20261019-pi-durable-contract-publication-sol-1 --expect-output service/package.json --expect-output service/config.json --expect-output plan.json --expect-output verification.md --timeout-seconds 300
```

Final repository checks pass: `validate-pattern-ids.py`, `validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`, `test-colorsets.py`, the 17-test evaluation-harness regression, focused source/runtime/full audits, and local skill sync/check. Publication documentation is checked for missing or ignored local-link targets. Stage only Pi Durable changes in shared backlog/coverage files and preserve unrelated dirty work.
