# Semantic modeling skill migration validation — 2026-11-02

The repository migration has deterministic validation evidence, but **isolated agent behavior is not validated in this pass**. Both new skill entries must remain `validating`. Five bounded provider readiness probes failed before a model response or task tool call. None is counted as a successful contract, naturalistic, generalization, or boundary test.

This note covers `curate-semantic-model` and its optional, independently usable companion `extract-ontologies`. The migration moves their canonical sources into `skills/`, translates reusable guidance and user-facing output into English, adopts the repository's `uv` script contract, and keeps acceptance fixtures outside the runtime payload. It does not establish universal semantic equivalence, a global minimum representation, or OWL consistency.

## Deterministic evidence

The primary bundle's regression receipt reports **136 passed**, with zero failures, errors, or skips: 51 core model checks, 45 conflict checks, and 40 ontology coverage checks. All six Python files have Python `>=3.11` `uv` metadata. The core example tests use six fixtures under `assets/examples/semantic-model`, which are excluded from ordinary isolated runtime tests.

The companion's actual pinned validator runs produced the expected three distinct outcomes: positive data `conformant` / exit 0; negative data `nonconformant` / exit 1, with three recorded violations; malformed processor input `error` / exit 2. Versions were RDFLib 7.6.0, pySHACL 0.40.0, and OWL-RL 7.6.2. OWL consistency and OWL profile conformance remained `not_checked`.

Local, ignored receipts are under `evaluations/runs/semantic-migration-deterministic/summary.json` and `evaluations/runs/extract-ontologies-migration-deterministic-final/summary.json`. These deterministic checks verify the shipped machinery. They do not replace isolated agent-use tests.

## Repository integration checks

All final repository gates passed on 2026-11-02:

- `uv run --script scripts/validate-pattern-ids.py`: 1,348 canonical item IDs; no violations.
- `uv run --script scripts/validate-skills.py`: passed, including the two nonvisual output inventory entries.
- `uv run --script scripts/test-skill-independence.py` and `scripts/check-repo-payload.py`: passed.
- `uv run --script scripts/audit-skill-authoring.py --check-bundles --output evaluations/runs/migration-authoring-audit-final.json`: 40 source bundles and 80 actual runtime/full copies; zero issues.
- `uv run --script scripts/test-pi-eval-harness.py`: 17 tests; `scripts/test-bundle-validation.py`: 11 tests; `scripts/test-colorsets.py`: 19 tests; `scripts/test-pages-output.py`: 14 tests. All passed.
- `uv run --script scripts/build-pages.py` and `scripts/validate-pages-pattern-format.py`: built 1,180 files and validated 16 published entries. Synthetic semantic-model cases are registered as unlisted support data, rather than a public gallery.
- `uv run --script scripts/sync-local-skills.py`: refreshed the isolated checkout installation while preserving unrelated installed files. Both new bundles also passed the skill-creator quick validator.

The initial repository validator identified missing reference contents links, dependency records in the executable directory, and missing output inventory entries. Those migration defects were corrected before the final passing run. Dependency records now live in the companion's `references/`; the validator's pinned uv metadata includes the original RDFLib HTML extra. Its final migrated implementation was retested against all three real SHACL controls. No OWL consistency or profile claim was added.

These are static, deterministic and packaging checks. They do not replace the pending isolated agent-use matrix below.

## Provider readiness blocker

Readiness probes ran from separate empty folders under ignored `evaluations/runs/`, with tools, MCP, ambient context, extensions, skill discovery, prompt templates, themes, and session persistence disabled. The only request was `Reply with exactly READY and do not call tools.` Public `pi --list-models` metadata was inspected; credential files and token-printing commands were not accessed.

The default route and deliberate exceptions were recorded in `SKILLS.md`. Attempts were bounded to one per route, in this order:

| Requested route | Observed result | Local raw evidence folder |
|---|---|---|
| `openai-codex/gpt-5.3-codex-spark` | ChatGPT-account route reports that this model is unsupported. | `curate-migration-default-provider-probe-20261102` |
| `openai/gpt-5.3-codex-spark` | HTTP 404, `model_not_found`. | `curate-migration-openai-spark-probe-20261102` |
| `openai-codex/gpt-5.3-codex` | ChatGPT-account route reports that this model is unsupported. | `curate-migration-codex-probe-20261102` |
| `openai/gpt-5.4` | API reports no credits remaining. | `curate-migration-openai-gpt54-probe-20261102` |
| `openai/gpt-5.3-codex` | API reports no credits remaining. | `curate-migration-openai-codex-probe-20261102` |

Every assistant event had `stopReason: error`, empty content, and zero reported input/output tokens. `pi` nevertheless returned process exit 0, so the event content, rather than the process code, determines failure. These are **infrastructure / provider access failures**, not measured skill failures. Each folder retains `events.jsonl`, `stderr.txt`, and `exit-code.txt`. The requested provider/model identity is visible in the assistant event; there was no usable model completion and no task artifact to grade.

The common probe command was:

```powershell
pi --model <recorded-provider/model> --thinking high --mode json --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --no-tools --no-mcp --no-session --print 'Reply with exactly READY and do not call tools.'
```

Do not mark a skill `done` based on these probes. Restore a supported, funded route or record a further deliberate exception before resuming the isolated release matrix. Do not silently substitute a different model or treat an empty error event as success.

## Prepared isolated release matrix

Six compact, reusable prompts are committed with the migration. A separate read-only review found no blocking runtime API or isolation defects. Two minor ambiguities were corrected before any skill run: direct source-record queries may verify original selections, and harmless temporary workspace intermediates are permitted.

| Skill | Case and reusable prompt | Fresh repetitions | Exact required final artifacts |
|---|---|---:|---|
| `curate-semantic-model` | [Typed contract smoke](../pi-prompts/curate-semantic-model-migration-contract.md) | 1 | `model.json`, `contract.json`, `validation.json`, `review.md` |
| `curate-semantic-model` | [Requirements ballot consolidation](../pi-prompts/curate-semantic-model-migration-naturalistic.md) | 3 | `model.json`, `contract.json`, `validation.json`, `review.md` |
| `curate-semantic-model` | [Retention policy generalization](../pi-prompts/curate-semantic-model-migration-generalization.md) | 3 | `model.json`, `contract.json`, `validation.json`, `claims.json`, `conflicts.json`, `conflicts.md`, `review.md` |
| `curate-semantic-model` | [Coverage denominator boundary](../pi-prompts/curate-semantic-model-migration-boundary.md) | 1 | `candidate.json`, `assessments.json`, `coverage.json`, `coverage.md` |
| `extract-ontologies` | [Local RDF validator contract](../pi-prompts/extract-ontologies-migration-contract.md) | 1 | `ontology.ttl`, `data.ttl`, `shapes.ttl`, `validation.json`, `validation-report.ttl`, `scope.md` |
| `extract-ontologies` | [Valid and invalid playbook entries](../pi-prompts/extract-ontologies-migration-naturalistic.md) | 3 | `ontology.ttl`, `data.ttl`, `shapes.ttl`, `validation.json`, `validation-report.ttl`, `invalid-data.ttl`, `invalid-validation.json`, `invalid-report.ttl`, `scope.md` |

**Executed skill-use runs: 0 of the 12 planned runs.** All repetitions remain pending. No naturalistic 2-of-3 threshold, generalization threshold, artifact acceptance criterion, read-surface gate, or runtime integrity gate is claimed as passed. Provider probes were intentionally performed before expensive skill runs, while source translation was being finalized.

Use the repository harness after the static and deterministic gates and a frozen bundle:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/<prompt>.md --model <route-explicitly-recorded-in-SKILLS.md> --thinking high --mode json --strict --profile runtime --run-id <unique-case-repetition-id> --expect-output <first-artifact> --expect-output <each-other-required-artifact>
```

For the two contract cases, add `--require-exact-command-from-prompt`. Do not add it to naturalistic or generalization cases. Add objective JSON field checks for actual status fields where appropriate, such as `--expect-output-json-field validation.json::contract_status=valid` for core validation and `--expect-output-json-field validation.json::status=conformant` for positive SHACL runs.

Keep all failed attempts and repetitions. Use fresh run IDs and workspaces; do not overwrite a failed attempt with a successful retry. Inspect each run's manifest, exact output checks, event checks, and unchanged-payload check. Generate a trace summary with the actual recorded model ID:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model <recorded-model-id> --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!<evaluated-skill>([\\/]|$))'
```

## Independent acceptance checks to complete

For each primary contract or ballot result, parse the actual canonical JSON, independently compare supplied source text, IDs and booleans, inspect every binding, run the validator again, and verify query results. The ballot must keep retrieval, persistence, and learning distinguishable and must not propagate one source's selection to another. An equivalence proposal needs an explicit evidence-based rationale; source metadata remains separately queryable.

For retention policy results, verify the same-scope 30-day/90-day disagreement is visible and unresolved with both evidence locators. The explicitly older version/period and multivalued availability regions must not become unjustified confirmed contradictions. Check actual normalized claims, conflict classifications, actionable choices, and the distinction between source truth, semantic normalization, contract validation, and unperformed OWL checks.

For coverage, recompute the candidate SHA-256, inspect every supplied assessment and denominator, and independently calculate 9/10 fully covered = 90%, 1/10 unknown = 10%, and 0/10 confirmed failures. Reviewed evidence must remain reviewed. Missing ontology conflict and formal checks must be reported as unchecked rather than fabricated passes.

For both companion cases, parse all local RDF artifacts and rerun the pinned validator. The positive data must conform. The naturalistic negative must be rejected for a missing required code without weakening the shape. Inspect the focus node, property path, constraint component, RDF report, inference setting, dependency versions, and explicit limits of OWL claims. Expected exit 1 must be handled in the task shell as an intentional rejection, rather than an unhandled failed tool call.

Only after successful artifact inspection and clean trace/runtime checks should the backlog advance from `validating`. Publication of canonical source to GitHub `main` is distinct from declaring this blocked runtime validation complete.
