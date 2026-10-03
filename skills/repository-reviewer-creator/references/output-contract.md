# Generated reviewer contract

## Required output

Create this small standalone bundle at the requested directory:

```text
<repository-slug>-reviewer/
  SKILL.md
  references/
    repository-profile.json
    review-rules.md
    safety-and-checks.md
```

The frontmatter contains only `name` and `description`, without duplicate keys. The name matches the directory, uses lowercase letters, digits and hyphens, is shorter than 64 characters, and contains neither `anthropic` nor `claude`. Name the target, actual review scope and trigger in a description of at most 1,024 characters, without XML tags or first- or second-person address. Open descriptively in third person, such as "Reviews changes to Tenant Catalog", rather than "Review changes". Write Markdown and JSON as UTF-8 and specify that encoding when reading generated text for validation. Keep the procedural entrypoint below 500 lines and references compact. Link each reference directly from `SKILL.md`; add linked contents near the top of any reference exceeding 100 lines. Use forward slashes in paths and commands. Optional `agents/openai.yaml` should name the reviewer and include its `$skill-name` invocation. Optional scripts must be safe, self-contained, and tested; do not copy the target's test runner into the skill just to make it seem standalone.

The skill may inspect the target checkout using repository-relative paths recorded as **evidence locations**, not links to required out-of-bundle instructions. Its operative guidance, fallback, report rules, and safety policy must live in its own bundle. Never require this generator or its validation script at reviewer runtime. Record missing evidence in the profile and explain how it limits reviews.

## Profile

Adapt the bundled JSON template. Preserve this schema:

| Field | Required content |
| --- | --- |
| `schema_version` | Integer `1` |
| `repository` | `name`, sanitized stable `identity`, `revision` or explicitly named snapshot, `inspected_at` date, and nonempty repository-relative `fingerprint_paths` |
| `sources` | Records with unique `id`, `kind`, `location`, `status` (`read`, `unavailable`, `not-applicable`), and `note`; rules, components, and executable checks cite only `read` IDs; an `unavailable` check may also cite the corresponding unavailability record |
| `components` | Records with `name`, nonempty `paths`, `purpose`, and nonempty `evidence` source IDs |
| `rules` | Records with unique `id`, `kind` (`requirement`, `observed-contract`, `recommendation`), nonempty `paths`, `when`, `invariant`, `failure`, `pass_case`, and nonempty `evidence` |
| `checks` | Records with `name`, `command` or a concrete static procedure, repository-relative `cwd` (`.` is allowed), `execution` (`safe-local`, `isolated-only`, `manual-only`, `unavailable`), `purpose`, `side_effects`, and nonempty `evidence` |
| `coverage_gaps` | List of strings; empty only if there are no known gaps |

Use `paths` for routing hints, including globs where useful, and `when` for semantic activation. Validate fresh evidence instead of treating recorded snapshots as permanent truth. A recommendation is not a mandatory contract unless adopted by the project; a reachable correctness or security failure still deserves analysis on its own merits.

Classify `safe-local` only for reviewed inspection with trusted tools that does not execute target code. Use `isolated-only` for repository code, including unit tests: imports, bytecode caches, setup, and subprocesses can write or execute code even when tests use synthetic data. Run these in a disposable copy, identify actual side effects, and reinspect changed commands before use. Use `manual-only` for a static procedure that is not a literal executable command, and `unavailable` for a blocked or missing check. A safety label is a routing decision, not permission to execute.

`repository-profile.json` is a compact evidence and routing index. `review-rules.md` explains project mechanisms, intent, investigation, counterexamples, and decision criteria by rule ID. `safety-and-checks.md` describes project-specific execution protections, safe check selection, blocked operations, and output behavior. Avoid duplicating complete docs or embedding source archives. Split component details into linked references if a document grows beyond roughly 10 KB.

## Ordered entrypoint for the reviewer

Write all of these steps explicitly in the generated `SKILL.md`, specialized to the target:

1. **Identity and freshness.** Read the bundled profile and essential safety guidance. Verify the user-selected checkout with origin/project identity and fingerprint paths; tolerate legitimate forks and relocation. Compare the current source and trusted policies with the recorded revision. Refresh rules affected by drift; do not silently apply them to another project or rewrite the skill during a review.
2. **Scope and comparison.** Identify requested PR, commit range, staged changes, or working tree. Freeze relevant revision IDs and note dirty state. For PR/branch review, use the merge-base against the actual target branch, not an assumed `main`; for explicit ranges use the requested semantics. Include untracked, staged, and unstaged files only when requested scope includes them. If the baseline is ambiguous, resolve from reliable metadata or request the missing value; proceed with unaffected analysis.
3. **Intent and inventory.** Read the change description as context, then inspect the complete diff, renames, deletions, new files, generated/source pairs, lockfile changes, and binary metadata. Handle pagination and truncated diffs. Describe incomplete coverage. Determine intended behavior from contracts and tests; a PR narrative alone cannot bless a regression.
4. **Rule selection.** Use paths and semantics to select affected rule IDs and components. Trace shared helpers, callers, tests, configuration, public consumers, schemas, and deployment paths across files or packages. Read only the relevant component references, plus essential safety guidance.
5. **Investigation and checks.** Compare baseline and proposed behavior, including boundaries, failure modes, and approved intentional changes. Reinspect changed test commands and hooks before execution. Bind each command to a verified checkout or disposable-copy directory; a recorded `cwd: .` means that repository root, not the shell's initial workspace. Put disposable copies and temporary artifacts under an explicit parent inside the authorized writable workspace; verify resolved cleanup targets before deleting anything. Run only relevant checks there, recording outcomes and limits. Carry an explicit expected-status adapter into the generated entrypoint or safety reference: preserve diagnostics and the real child status, but complete the shell tool successfully for a documented expected comparison/search/regression result. Do not propagate an expected `diff`/regression status with `exit "$status"`. Distinguish unexpected setup/execution failures and never use an unconditional success suffix. Compare a failure with the baseline or equivalent evidence when possible. Never call an unrun check passed.
6. **Findings gate.** Require introduced or worsened behavior, reachable impact, supporting evidence, actionability, and verified absence of compensating controls. Suppress baseline debt, stylistic preferences, duplicate symptoms, and speculative findings. Allow zero findings. State uncertainty in coverage notes.
7. **Report.** Follow the user's requested schema or the verified project convention; otherwise use concise findings ordered by severity. Each finding states priority, file and smallest accurate line range, triggering condition, consequence, evidence, and correction direction. Prefer a changed hunk; for deletions use the baseline location and label it. Add scope/revisions, checks actually run, and coverage limits. Summarize the outcome without falsely claiming complete approval. Publishing, messaging, or editing requires separate user authorization.

For an explicitly requested whole-repository audit, label the different scope and permit existing defects as audit findings. Do not turn ordinary change review into an audit.

## Delivery

Explain where the reviewer was written, which resources support it, its coverage gaps, what validation ran, and how to invoke it. Keep test results attributable to the exact bundle and target snapshot. Do not claim installation outside the user-authorized writable scope.
