# Tool-contract guidance promoted during evo10 — 2026-10-25

## Scope and frozen subject

Promote one reusable lesson to the canonical Pi Durable skill: evolving a tool's
execution evidence must preserve the existing capability/API contract and its
historical consumers. This is independent of the custodian's frozen ten-attempt
study. No study evaluator, driver, case, candidate, live project, permission or
score was modified by this guidance revision.

Only two canonical files changed: the existing agent-evolution reference gains
a compact tool-contract section and contents link; the generated application
runbook gains twelve self-contained procedural lines. The runbook needs the
rule locally because generated applications operate without the skill.

| Payload | Files | SHA-256 |
| --- | ---: | --- |
| Runtime | 103 | f903a640804e3a27dc6b32ddcd0e64f5aa4ab48c98dbb067b3216ae8e426f3be |
| Full | 135 | ea44941d25f80987bacd9250211c62e16b01605e4d7fc20d996861eccd144763 |

All four new forward runs use the same immutable runtime subject. The existing
evolution reference is 11,355 bytes after the addition; it contains the complete
independent evolution procedure and the new conditional compatibility check.
Focused reads are justified by this review task; no gallery or acceptance
fixture is needed.

## Transferable rule

Inventory and preserve existing fields, types, status meanings, null/unknown
behavior and bounded errors. Identify consumers in prompts, consoles/reports,
watchdogs and retained conversations. Prefer additive execution receipts without
erasing configured capability observations: a configured command list and its
execution receipts answer different questions.

Exercise unchanged consumers against baseline and candidate, including no-op,
blocked, failed and partial observations. Reject an incompatible candidate even
when its aggregate producer score improves. Check baseline compatibility too;
an incompatible baseline is not automatically releasable. A deliberate break
needs a separately scoped version/adapter, consumer migration, recovery and
rollback. Do not rewrite a frozen verifier to accommodate a preferred version.

This is authoring/operator guidance, not a new automatic runtime API gate. It
does not establish the compatibility or quality of any evo10 candidate.

## Isolated validation

The user's Sol 6.1 preference continues the recorded model exception:
openai-codex/gpt-6.1-sol with medium effort. Runtime-only workspaces disable
ambient context, extensions, other skills, themes and prompt templates. No
dependencies, builds, services, installed agents, credentials, external services
or nested models are used. The only model is the isolated authoring harness.

| Run suffix after pi-durable-evo10-compatibility-20261025- | Strict | Independent artifact/manual | Duration |
| --- | --- | --- | ---: |
| contract | Pass | Pass | 77.803 s |
| natural-1 | Pass | Pass | 113.192 s |
| natural-2 | Pass | Pass | 97.988 s |
| natural-3 | Pass | Pass | 85.904 s |

The contract case identifies the three dropped legacy inspect fields,
distinguishes configured commands from execution receipts, rejects the
incompatible replacement and plans old-consumer/recovery checks. The three
natural cases transfer the same principle to discovery, permission metadata,
warnings and saved pagination cursors. Each rejects automatic release of both
the incompatible replacement and an old version with an unresolved defect.

Every JSON artifact passes seven independent structural/contract checks; the
complete Markdown and JSON outputs pass manual review for capability/execution
separation, historical consumers, honest unknowns, deliberate migration/rollback,
and no fabricated execution or new permissions. These are plan-review outcomes,
not actual implementation or task-quality measurements.

Exact contract command:

    uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evo10-compatibility-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-evo10-compatibility-20261025-contract --expect-output outputs/compatibility-review.json --expect-output outputs/review-plan.md --timeout-seconds 420

Naturalistic command, repeated in fresh workspaces with natural-1, natural-2
and natural-3:

    uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evo10-compatibility-naturalistic.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-evo10-compatibility-20261025-natural-1 --expect-output outputs/review.json --expect-output outputs/compatibility-plan.md --timeout-seconds 420

For each run:

    uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-evo10-compatibility-20261025-contract/events.jsonl --output evaluations/runs/pi-durable-evo10-compatibility-20261025-contract/read-surface.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error

All four have valid JSON, zero tool errors, the exact observed model and
unchanged copied bundles. Read surfaces contain only the prompt, skill
entrypoint, focused own evolution/evidence references, one relevant version
reference and generated review outputs. There are no Bash calls, outside
context, sibling skills or acceptance-fixture reads. Prior subjects and study
attempts remain separate; there are no new failed runs or rerolls in this cohort.

Required pattern, skill structure, independence and payload checks pass, as does
the scoped skill validator and diff check. No script/runtime build was needed
because the outputs are review plans. Raw runs and independent checks remain in
their ignored run folders; the compact combined inventory/read-surface record
is projects/pi-custodian-evolution-10/artifacts/compatibility-guidance-summary.json.
SKILLS and installation refresh are left to the parent task.
