# Reconcile policy evidence without choosing a winner

We need a compact model and a review queue for our retention policy evidence. Use only the supplied records below. Work inside the workspace and keep the copied skill read-only. Do not read hidden files, repository or sibling content, acceptance examples, or external sources. Use compact runtime references and bundled deterministic helpers as needed. No network services or formal reasoner are available.

| ID | Locator | Original statement |
|---|---|---|
| `s:a` | `policy:A:4` | For AuditBox Enterprise version 2, customer event records have a retention period of 30 days throughout 2026. |
| `s:b` | `policy:B:9` | For AuditBox Enterprise version 2, customer event records have a retention period of 90 days throughout 2026. |
| `s:c` | `policy:C:3` | For AuditBox Enterprise version 1, customer event records have a retention period of 90 days throughout 2025. |
| `s:d` | `policy:D:2` | AuditBox Enterprise version 2 is available in both the US and EU regions throughout 2026. |

For this task, retention period is single-valued for the same product, edition, version, record kind, and overlapping period; availability regions can have multiple values. These are task rules, not claims that either policy source is true. Do not automatically prioritize a source, resolve the disagreement, or fabricate a user decision. Different explicit versions or disjoint periods can coexist.

Write exactly `model.json`, `contract.json`, `validation.json`, `claims.json`, `conflicts.json`, `conflicts.md`, and `review.md` in the workspace root. Preserve all original evidence and stable bindings. Build the least expressive sufficient model; run the actual type validator and conflict scanner. If the conflict scanner returns its documented expected pending-conflict exit status, handle that as the expected test result inside the shell command rather than a failed tool invocation. Use only supported constraints and record the real engine statuses.

The review queue must expose the conflicting evidence side by side with locators, scope, rule, and concrete choices a user could make. Keep unresolved items visible. Explain how the old-version evidence and multivalued regions were classified and identify any missing data without inventing it. State the effects on a retention query and distinguish structural validation from semantic normalization and OWL consistency.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
