# Ontology coverage, residual gaps, and contradictions

## Contents

- [Evidence](#establish-evidence-before-percentages)
- [Input](#supported-input)
- [Residual percentages](#report-the-residual-percentage-accurately)
- [Internal contradictions](#inspect-contradictions-inside-the-ontology)
- [Consistency and adoption](#separate-formal-consistency-from-adoption)
- [Progress and regression](#preserve-progress-and-detect-regression)

Use to decide whether to reuse, extend, combine, or reject a candidate ontology.
The unit is an acceptance case, query, or constraint with an explicit expected
result, not a class count, similar term, or lexical mapping.

## Establish evidence before percentages

Freeze the common suite before comparison: ID/version, stable case IDs, expected
answers, method, scope, required status, and optional weights. Record each
candidate's IRI, version, artifact/hash, resolved imports, and inference settings.
Acquire and pin actual ontology artifacts when the evaluation needs them.

Execute cases with suitable tools: competency queries, core checks, SPARQL,
SHACL, or a reasoner. Retain results and tool versions. Semantic review may
justify an assessment, but identify it as `reviewed`, separately from `executed`
evidence. A status written by an agent does not prove that execution occurred.

`ontology_coverage.py` aggregates supplied results and verifies local hashes.
It is not a query runner, reasoner, or validator of an observation's truth.
Execute or review the cases before constructing its input. Formal tools, and
optionally the available `extract-ontologies` skill, can supplement this workflow;
missing tools must leave the corresponding formal check not checked.

## Supported input

Root fields are `schema_version: "1"`, `suite`, and `candidates`.
`suite` contains `id`, `version`, and `cases`. Each case has:

- Nonempty strings `id`, `title`, `expected`, and `method`.
- Optional nonempty `kind` for breakdowns, for example `competency_question`,
  `requirement`, `structural_constraint`, or `consistency`.
- Boolean `required` (default false), and positive finite `weight` (default 1).
- Boolean `applicable` (default true). Exclusion needs `exclusion_reason`, applies
  to every candidate, and cannot exclude a required case. A candidate cannot
  remove its own failures from the denominator.

Nonrepresentable weight totals produce a structured `NUMERIC_OVERFLOW` error,
never a non-finite percentage or an empty report.

Each candidate contains `id`, `label`, `ontology`, `assessments`, and optionally
`conflict_review` and `formal_checks`. Candidate structure, with descriptive
hash text that must be replaced by the actual artifact's SHA-256:

```json
{
  "id": "candidate:A", "label": "Candidate ontology A",
  "ontology": {
    "iri": "https://example.org/ontology/A", "version": "1.0",
    "artifact": "ontology.ttl", "sha256": "actual file SHA-256"
  },
  "assessments": []
}
```

Artifact paths are local, absolute or relative to the input file. File contents
and SHA-256 are checked; URLs and ontology imports are not downloaded.

Each case assessment declares `case_id`, `status`, `observed`, `reason`,
`ontology_sha256`, and as needed `evidence_mode`, `evidence`, `result_artifact`,
`result_sha256`, `conflict_ids`, and `next_action`.

Statuses are `pass`, `fail`, `partial`, `unknown`, and `error`. Missing assessments
become `unknown` and remain in the denominator. Pass/fail/partial require nonempty
evidence and mode `executed` or `reviewed`; each evidence entry contains `locator`
and `observation`. Executed mode requires a result artifact and its hash. Other
statuses may use `not_provided` evidence mode. Every non-pass needs a next action.
Per-assessment ontology hashes prevent accidental reuse across changed artifacts.

Only a case whose expected result concerns names or labels can pass on that
basis. Lexical similarity does not establish another semantic capability. The
helper cannot detect a falsely labeled review; preserve method, evidence, scope,
and provenance so it can be audited.

## Report the residual percentage accurately

Strict coverage is effective fully passed cases divided by all applicable cases.
Show numerator and denominator. Partial cases get no automatic half credit;
report them separately. Label weighted coverage separately rather than replacing
coverage by case count.

| Results across ten cases | Correct interpretation |
|---|---|
| 9 pass + 1 fail | 90% fully covered; 10% observed failure. |
| 9 pass + 1 unknown | 90% fully covered; 10% unverified; 0% demonstrated failure. |
| 8 pass + 1 partial + 1 error | 80% fully covered; 10% partial; 10% error. |
| No applicable cases | Null/not evaluable percentage, never 100%. |

Not fully covered means fail + partial + unknown + error + conflicted. Do not
call that entire residual confirmed noncompliance. For every residual case,
show expected and observed result, evidence, reason, related conflicts, required
status, and a proposed extension, correction, or additional check.

## Inspect contradictions inside the ontology

Review axioms, IRIs, types, ranges, exclusions, identity rules, constraints, and
queries. Record locators in the original ontology: triple, axiom, query, or
fragment. When normalizing these into the core model, retain mappings to the
artifact and do not invent axioms. Formal engineering and reasoning can be
performed with an available processor or optional companion skill.

A `conflict_review` binds the JSON produced by `review_conflicts.py` to the
current ontology. Replace descriptive hashes with actual SHA-256 values:

```json
{
  "artifact": "conflicts.json", "sha256": "actual review SHA-256",
  "ontology_sha256": "actual ontology SHA-256"
}
```

Produce that binding from the correct artifacts. Hashes detect changes, but do
not prove normalization quality. The review retains fingerprints, assertions,
evidence, and decision choices. Do not relink an old report to a new ontology
without repeating the check.

If a raw pass cites `conflict_ids` that remain open, deferred, or pending
validation, retain the raw result and set effective status to `conflicted`.
Count a case once even when several conflicts affect it. `scope_difference`
does not itself block a case. Show global conflicts that are not linked to
specific cases; they do not disappear at 90% coverage. An absent scan is
`not_provided`, not zero contradictions.

After applying and checking a resolution, generate new review and case results.
An old conflict ID missing from the current review is stale evidence and an
error, not a silent pass.

## Separate formal consistency from adoption

`formal_checks` can contain `owl_consistency` and `shacl`, each with `status`.
OWL statuses: `not_checked`, `consistent`, `inconsistent`, `error`. SHACL statuses:
`not_checked`, `conformant`, `nonconformant`, `error`. Every status other than
not_checked needs `tool`, `version`, `artifact`, `sha256`, and `ontology_sha256`.
Its report should identify the graph/import closure and inference regime.

Unsatisfiable classes are not necessarily inconsistency of the entire ontology.
SHACL nonconformity is not OWL inconsistency. The helper does not interpret every
reasoner's output: it retains the declared result and pinned evidence.

`readiness` distinguishes no evaluable cases, formal-check blocks, conflicts,
required-case blocks, absent conflict review, candidates with gaps, and full
coverage on this suite. None certifies universal suitability. A 90% candidate
may be a useful base with concrete extensions while still being blocked by a
required failure. The user decides which residual gaps and conflicts to accept.

## Preserve progress and detect regression

Keep a snapshot of suite, ontology, evidence, and conflicts for every delivery.
With `--previous`, deltas are calculated only when suite fingerprints match.
Show newly covered cases, regressions, and remaining gaps. A different case
universe is `not_comparable`; do not claim a percentage improvement from it.

Version contract and case changes explicitly. Do not remove a difficult or
required case, or redefine an expectation, merely to raise the score. Evaluate
combined ontologies as a new candidate on the same suite: percentages cannot
be added, and combined axioms can create new conflicts.

```text
uv run --script <skill-dir>/scripts/ontology_coverage.py --input assessments.json --report coverage.json --markdown coverage.md
uv run --script <skill-dir>/scripts/ontology_coverage.py --input reassessment.json --previous coverage.json --report coverage-v2.json
```

Exit **0** means the report was computed, even with 90% or less coverage; it is
not approval. Exit **2** means invalid input, stale hashes, processing errors,
or output collisions. Inputs and existing reports are not overwritten. Normal
runtime tasks construct their own case evidence; acceptance fixtures are not
required inputs.
