# Harbor dataset authoring skill installation

Date: 2026-09-02

## Scope

The canonical `harbor-author-evaluation-datasets` bundle was installed under
`skills/harbor-author-evaluation-datasets/`. Its deterministic planner
separates semantic families across discovery, development, sealed validation,
and optional holdout cohorts. Its aggregate report consolidator consumes
sanitized native Harbor `final-report.json` files and writes:

- `comparison-report.json`
- `comparison-report.md`
- `quality-comparison.svg`
- `resource-comparison.svg`
- `efficiency-frontier.svg`

The two functional Python scripts use this repository's uv/PEP 723 header.
Functional behavior otherwise remains aligned with the source bundle.

## Deterministic validation

| Check | Result |
| --- | --- |
| Skill Creator quick validation | Passed |
| Python compilation for both functional scripts and both black-box test scripts | Passed |
| Planner `--help` | Passed |
| Consolidator `--help` | Passed |
| Planner black-box tests | 5/5 passed |
| Consolidator black-box tests | 4/4 passed |
| Absolute `skill-arena` Node test | 12/12 passed |
| Pattern ID validator | Passed: 1,160 canonical IDs |
| Repository skill validator | Passed |
| Skill-independence validator regressions | Passed |
| Repository payload check | Passed |
| Targeted local skill synchronization and drift check | Passed |
| Git whitespace check | Passed |

The absolute source test command was:

```powershell
node --test C:\Users\villa\dev\skill-arena\test\harbor-author-evaluation-datasets.test.js
```

The Node suite exercises deterministic planning, split disjointness, coverage
requirements, task-keyed variation stability, supported response modes,
ambiguous-lineage rejection, no-overwrite behavior, tamper detection, CLI
surface, deterministic aggregate reporting, accessible SVG output, and
fail-closed token accounting. The additional regressions cover private source
locator redaction, hostile Markdown/SVG labels, invalid timestamps and counts,
partial metric coverage labels, null per-trial efficiency deltas, and exclusion
of incompletely covered spend from the Pareto frontier.

## Consolidator audit corrections

The black-box audit found that native `harbor-run-results` reports in this
repository use timezone-naive `startedAt` and `finishedAt` values for jobs even
though their report-level `generatedAt` value is timezone-aware. The initial
consolidator rejected those valid native artifacts. The parser now accepts a
matching naive pair or a matching timezone-aware pair, while rejecting mixed
awareness, invalid timestamps, and a finish before its start.

The same audit tightened the publication boundary:

- input paths are represented only as neutral `input-N` locators;
- Markdown-controlled characters in report labels and titles are escaped;
- partial reward, token, cost, and agent-time aggregates visibly state their
  observation coverage, while incomplete token, cost, and agent-time totals do
  not produce per-trial deltas or enter Pareto/frontier calculations;
- report-level and caller-supplied publication timestamps must be valid ISO
  8601 values with a timezone;
- aggregate observation counts cannot exceed completed trials; and
- non-finite, overflowing, negative, double-counted, or internally
  inconsistent resource accounting fails closed before output is created.

The branch-integration audit added two further fail-closed guarantees. Every
token alias is now validated as a finite non-negative number before aliases
are compared, so malformed arrays or objects return the documented CLI error
instead of an uncaught `TypeError`. Resource charts draw colored token stacks
only when total and component coverage are complete and mutually consistent;
partial coverage uses a bounded gray total bar that cannot overflow its panel.
The runtime trigger metadata was also aligned with the finalized schema-v1
report-consolidation workflow.

The Python consolidator suite additionally injects sealed task, prompt,
answer, and local-path sentinels into trial records, then proves that none
appears in JSON, Markdown, or SVG output. It parses every SVG as XML and checks
`role="img"`, `aria-labelledby`, `title`, `desc`, and the absence of script,
raster-image, foreign-object, and external-reference elements. A direct smoke
run also consolidated the repository's two released D3 Harbor reports into all
five expected artifacts without exposing their per-trial fields.

## Source-coordination note

The skill instructions, authoring contract, planner metadata, consolidator,
and initial planner regressions arrived as concurrent local changes between
19:58 and 20:05 on 2026-09-02. This audit preserved those changes and applied
only additive tests plus narrowly scoped consolidator compatibility and
publication-safety corrections against the then-current bytes. The later
branch-integration audit updated routing text and recorded the verified test
counts, without modifying sealed evaluation evidence.

## Release status

The skill remains `validating`. Run isolated naturalistic forward tests and a
routing control under the repository's normal Pi policy before changing the
backlog status to `done`. Those future runs must use development evidence
only for adaptation and must not reveal sealed validation or holdout content.

The prepared strict forward-test prompt is
`evaluations/pi-prompts/harbor-author-evaluation-datasets-runtime-contract.md`.
It was not executed on 2026-09-02 because the configured Spark provider quota
was exhausted; deterministic and black-box evidence must not be mislabeled as
an isolated agent-runtime pass.
