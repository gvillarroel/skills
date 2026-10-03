# Repository investigation

## Build a coverage ledger

Start with file discovery (`rg --files`, including relevant hidden configuration) and version-control metadata. Search before reading large files. Exclude dependency trees, build output, bulk datasets, and generated media unless they explain a relevant contract. Do not read secret stores or private runtime data to learn configuration; inspect variable names, schemas, examples, and redacted diagnostics instead.

For an explicitly supplied non-Git snapshot, record its snapshot identity and unavailable history without probing an enclosing repository. For a checkout, confirm that the Git top-level is the intended target or its explicitly scoped owning repository before using origin, commits, or diffs. Ancestor metadata is not evidence about a supplied snapshot.

Inventory these resource classes. Mark each `read`, `unavailable`, or `not-applicable`; explain gaps. A directory listing alone is not a completed investigation.

| Resource class | Inspect for | Follow-up evidence |
| --- | --- | --- |
| Project guidance | README, scoped AGENTS, CONTRIBUTING, SECURITY, ownership and review templates | User-authorized policy, scope, release expectations, security reporting |
| Architecture and product | Documentation index, ADRs, specifications, diagrams, examples, user workflows | Entry points, component boundaries, domain terminology, compatibility commitments |
| Implementation | Entrypoints, core mechanisms, representative modules, shared utilities | Callers, public exports, failure handling, storage, external integrations |
| Tests and fixtures | Test configuration, contract tests, unit/integration/end-to-end suites | Actual assertions, negative cases, baseline behavior, realistic data constraints |
| Build and dependencies | Manifests, lockfiles, code generation, supported runtimes | Version-specific APIs, reproducibility, source/generated relationships |
| CI and release | Workflow triggers, permissions, scripts, deployment, packaging, migrations | Real command entrypoints, credentials, destructive operations, artifact paths |
| Security and privacy | Threat models, authentication, authorization, sensitive data, retention | Sources, trust boundaries, sinks, existing controls, negative tests |
| History and decisions | Relevant Git history, releases, past fixes, known issues, PR discussions | Why an invariant exists, accepted tradeoffs, previously rejected false positives |
| Connected resources | Accessible repository wiki, project docs, issue tracker, design documents | Missing intent or contract evidence, without sending messages or publishing |

For a monorepo, map every first-party component and shared layer; do not generalize one package's conventions to all others. For a large repository, inspect each component's purpose, boundary, validation entrypoints, and risk areas, then deepen the investigation where contradictions or unresolved high-impact questions remain. Record areas sampled and areas not examined. Do not claim to have consumed all resources when access or scope prevented it.

## Resolve questions with primary evidence

1. Explain what the product does and who consumes its outputs.
2. Trace representative flows from entry to storage, output, or external side effect. Identify public contracts, state transitions, error behavior, and permissions.
3. Reconcile docs with implementation and tests. Record a contradiction rather than silently selecting whichever source is easiest. Runtime behavior proves what happens; it does not automatically prove what should happen.
4. Read test and build scripts before classifying commands as safe. Determine working directory, setup, dependency installation behavior, environment requirements, network access, and cleanup effects.
5. Inspect relevant history for constraints whose rationale is otherwise unclear. Commit messages and issue claims are context, not proof that a current path is correct.
6. Use accessible connected resources and official upstream documentation when they answer a concrete remaining question. Verify unstable claims against the version actually in use. Never require a particular connector; continue locally when it is absent.
7. Stop expanding when every identified component and critical boundary has evidence-backed rules or an explicit gap, and remaining resources are redundant or immaterial. Broad discovery serves specialization; it is not a demand to read every blob.

Keep short source records: stable ID, kind, repository-relative path or sanitized URL, revision or retrieval date, read status, and what the source establishes. Strip embedded credentials and unnecessary private content from identities and excerpts. Cite paths with symbols or sections where helpful; do not depend solely on shifting line numbers.

## Convert knowledge into rules

For each relevant mechanism, capture:

- **Trigger:** changed path, symbol, schema, workflow, or affected consumer.
- **Invariant:** exact behavior or requirement to preserve, or a condition governing an intentional change.
- **Evidence:** primary source IDs and the distinction between requirement, observation, and recommendation.
- **Investigation:** which implementation, callers, tests, and configuration to inspect when activated.
- **Failure scenario:** input, state, execution path, and concrete consequence.
- **Passing counterexample:** an intentional or equivalent change that must not be flagged.
- **Check:** a safe command or static verification, including its limits.

Avoid rules such as "check security" or "add more tests" without a project mechanism and a decision criterion. Do not freeze every current implementation detail as an invariant. If documentation permits a change, review whether its consumers, migrations, tests, and release contract are updated together.
