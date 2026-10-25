# Pi Durable evidence-collection guidance — 2026-10-25

## Scope and subject

Add actionable authoring/operator guidance for collecting useful task evidence
and judging whether it can support a requested improvement. This revision adds
no deterministic runtime sufficiency gate or automatic verification scheduler.
It updates the skill entrypoint, a compact evidence-readiness reference, the
independent evolution reference, the generated application runbook and the
default PR-reviewer prompt. Custom agent prompts still need task-specific
adaptation; the Durable model does not automatically read `AGENTS.md`.

Current frozen subjects:

| Payload | Files | SHA-256 |
| --- | ---: | --- |
| Runtime | 103 | `bdf685cd38e6d0f79689219df387f9a371094324060d7555f3d6fb4631375c89` |
| Full | 135 | `32ee55904c85920bfb113d80ce9936951202f7d7f0dea5964779159f0969b750` |

The runtime subject is identical in all four forward-test manifests. Full
includes acceptance fixtures; runtime excludes them. Historical lifecycle
subjects and failures remain in [the lifecycle record](lifecycle-20261025.md).

## Promoted guidance

- Choose prospective observable duty criteria and arrange actual verification.
  Explicitly disclose the disabled default contract and operator responsibility.
- Link input/goal, agent/task/conversation/submission, source/prompt/model version,
  relevant actions, material public decisions, actual outcomes, receipt IDs,
  feedback and observed resources. Missing observations stay unknown.
- Preserve successes, failures and labeled negative controls. Separate task/tool
  defects from authentication, network, OS and evaluator problems.
- Judge readiness against the claim: insufficient, bounded reproduction, or ready
  for a bounded comparison. A narrow reproducible defect and a general policy
  improvement require different coverage; no universal sample count is claimed.
- Inspect the actual bounded pack: latest 1000 records scanned, up to 20 selected
  within 100 KB. Stop proposals with essential omitted evidence. Do not fabricate
  citations, hand-edit sealed requests or imply a custom selector exists.
- Permit an inactive null reflection candidate. Require frozen meaningful paired
  evaluation, bounded quality claims, post-release verification and rollback.
- Keep all generated operational guidance independent of this skill, and place
  appropriate task-facing instructions in the active prompt. Reuse host telemetry;
  do not add idle model calls or capture private thinking/credentials.

## Validation

Forward tests use the user's requested `openai-codex/gpt-6.1-sol` with medium
effort, continuing the recorded model exception. All run from fresh isolated
runtime-only workspaces with ambient context, extensions, other skills, themes
and prompt templates disabled. The payload is read-only. The only model calls
are the forward-test harness; no generated agent or nested reflector runs.

| Run ID suffix after `pi-durable-evidence-guidance-20261025-` | Strict | Independent artifacts | Manual review |
| --- | --- | --- | --- |
| `contract` | Pass | 58/58 | Pass |
| `natural-1` | Pass | 12/12 | Pass |
| `natural-2` | Pass | 12/12 | Pass |
| `natural-3` | Pass | 12/12 | Pass |

Contract command:

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evidence-guidance-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-evidence-guidance-20261025-contract --expect-output outputs/agent/scaffold-manifest.json --expect-output outputs/agent/AGENTS.md --expect-output outputs/agent/prompts/pr-reviewer.md --expect-output outputs/handoff.md --timeout-seconds 600
```

Naturalistic commands (fresh workspace for each `1`, `2`, `3`):

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evidence-guidance-naturalistic.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-evidence-guidance-20261025-natural-1 --expect-output outputs/readiness.json --expect-output outputs/agent-instructions.md --expect-output outputs/operations.md --timeout-seconds 600
```

The contract scaffolds exact output paths without installing dependencies or
starting services. Independent checks compare every initial manifest hash and
the transferred runbook/prompt to the frozen template. All naturalistic runs
classify lifecycle-only records as insufficient, the concrete path-script defect
as a bounded reproduction, and a lifecycle-only export as insufficient despite
private completed reviews. Their guidance preserves permissions, actual version
uncertainty and untested platform/generalization limits.

For each run, execute the evaluator-owned check and event summary (use
`--kind naturalistic` for natural runs):

```powershell
uv run --script evaluations/contracts/pi-durable-evidence-guidance.py evaluations/runs/pi-durable-evidence-guidance-20261025-contract --kind contract --output evaluations/runs/pi-durable-evidence-guidance-20261025-contract/independent-artifact-check.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-evidence-guidance-20261025-contract/events.jsonl --output evaluations/runs/pi-durable-evidence-guidance-20261025-contract/read-surface.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error
```

All four traces contain valid JSON, the exact requested model, zero tool errors
and unchanged skill payloads. Read-surface inspection finds the entrypoint and
focused evidence/evolution references; additional contract reads are the generated
runbook, prompt, config, verification contract and manifest. No
acceptance fixtures, sibling skills, outside context, credentials or live service
state are read. Commands only scaffold and inspect/validate workspace artifacts.
An independent agent reviewed the source guidance and all generated prose; 4/4
manual artifact reviews pass without unsupported automation or quality claims.

Repository checks pass:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script skills/pi-durable/scripts/test-scaffold-profiles.py
```

Scaffolding checks cover all four service/specialist profiles, fresh hashes and
nonempty destination refusal. Canonical files are synchronized to the local
skill installation. The installed console's frozen service factory receives
only the changed runbook/default prompt; user connection registries and existing
agent projects retain their state and prompts.

## Limits

These results validate guidance use and independent template transfer. They do
not measure improvement on real PR reviews, force every custom agent to record
decisions, guarantee a representative sample or add automatic selection of
complete task chains. No OS login job, native macOS launch or live generated
agent is exercised in this revision. Keep the broader skill `validating` for the
previously recorded platform, operational and authoring gaps.
