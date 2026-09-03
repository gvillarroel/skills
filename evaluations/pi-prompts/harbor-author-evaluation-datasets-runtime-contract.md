Use the provided `harbor-author-evaluation-datasets` skill to create and verify
a deterministic, group-disjoint authoring plan, then publish a sanitized
aggregate comparison from two synthetic Harbor final reports.

Treat `skills/harbor-author-evaluation-datasets/` as read-only. Write every
task input and generated artifact outside the copied skill directory. Do not
inspect repository-level files, sibling skills, acceptance fixtures, or the
network.

Create a schema-version-1 blueprint at `inputs/blueprint.json` for a synthetic
dataset named `isolated-authoring-contract-v1`. It must contain four semantic
families, each with a different `familyId`, `sourceId`, and `templateId`; two
cases per family; equal `development` and `validation` split weights; and
coverage requirements that require at least one family, two tasks, both
`single_file` and `structured` response modes, and one realized family in each
of the `capability`, `domain`, `difficulty`, and `resourceClass` strata for
both splits. Give every task at least two choices for `input_root`,
`output_name`, and `output_root`.

Create `private/seeds.json` with schema version 1 and three distinct synthetic
64-character lowercase hexadecimal seeds: one partition seed and one variant
seed for each declared split. These are test-only fixtures, not production
secrets.

Use the bundled planner to write the exact directory `outputs/authoring-plan`.
Then run its strong verification form with the original blueprint and seeds,
and save the command's JSON stdout exactly at
`outputs/plan-verification.json`. Do not copy raw seeds into any output.

Create two valid schema-version-1 Harbor `final-report.json` fixtures under
`private/reports/baseline/` and `private/reports/candidate/`. Each report must
contain one complete two-trial job with internally consistent pass counts,
reward, input/cached-input/output/total token accounting, reported USD cost,
agent latency, and start/finish timestamps. Include the literal sentinel
`SEALED-CASE-DETAIL-MUST-NOT-LEAK` only in per-trial fields that the
consolidator must omit. Use naive but valid job timestamps in one report and
timezone-aware job timestamps in the other.

Use the bundled consolidator with the baseline job selected explicitly, the
fixed generated timestamp `2026-09-02T20:00:00+00:00`, and the exact output
directory `outputs/publication`. Do not manually reimplement either bundled
script.

Required outputs:

- `outputs/authoring-plan/plan.private.json`
- `outputs/authoring-plan/summary.redacted.json`
- `outputs/plan-verification.json`
- `outputs/publication/comparison-report.json`
- `outputs/publication/comparison-report.md`
- `outputs/publication/quality-comparison.svg`
- `outputs/publication/resource-comparison.svg`
- `outputs/publication/efficiency-frontier.svg`

Acceptance criteria:

- Strong verification reports `ok: true` and `sourceInputsReproduced: true`.
- Whole families are assigned to exactly one split, and both development and
  validation are non-empty and meet the declared coverage minima.
- Neither raw test seed nor individual seed commitments appear in
  `summary.redacted.json`.
- The comparison contains exactly two aggregate runs, preserves cached input
  as a subset rather than adding it twice, and records SHA-256 commitments for
  both input reports.
- No publication artifact contains
  `SEALED-CASE-DETAIL-MUST-NOT-LEAK`, a raw input path, a task name, a prompt,
  an answer, or per-case diagnostics.
- All three SVGs are standalone XML with `role="img"`, an accessible `title`
  and `desc`, no scripts, no raster images, no external references, and
  legible textual labels and units.
