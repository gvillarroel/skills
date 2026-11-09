# Find, discriminate, and resolve contradictions

## Contents

- [Classification](#classify-before-requesting-a-decision)
- [Normalized assertions](#optional-normalized-assertions)
- [Evidence and consequences](#present-evidence-and-consequences)
- [Explicit choices](#record-an-explicit-choice)
- [Apply and verify](#apply-and-verify-the-choice)

Use when comparing sources, integrating additions, or reviewing an existing
model. A conflict queue is a derived review view, not a second source of truth.
Preserve original passages and their interpretations even when an assertion is
removed from the active model.

## Classify before requesting a decision

| Kind | Interpretation |
|---|---|
| `confirmed_conflict` | Reviewed, normalized assertions oppose each other under an explicit rule in comparable scopes. This does not decide which source is true. |
| `possible_conflict` | Apparent opposition needs review of normalization, entity, context, time, version, or unit. |
| `scope_difference` | Explicitly different contexts, versions, or disjoint periods can coexist; do not force a resolution. |
| `constraint_conflict` | A predicate exclusion, DAG, or cardinality rule is violated. The rule or representation may be wrong; this does not prove a source false. |

Do not treat missing information, different classifications, multivalued
properties, or successive versions as contradictions by default. For free text,
look within and across sources; inspect negation, conditions, quantifiers,
exceptions, units, and dates in complete passages. Keep uncertain cases possible.

## Optional normalized assertions

`review_conflicts.py` uses the core model and contract. Assertions extracted from
text may be supplied in an additional file with this structure:

```json
{
  "schema_version": "1",
  "functional_predicates": ["retention_days"],
  "assertions": [{
    "id": "claim:A", "subject": "item:service",
    "predicate": "retention_days", "value": 30, "polarity": "positive",
    "source_ids": ["source:A"],
    "scope": {
      "context": "enterprise", "version": "2.0", "unit": "days",
      "time": {"kind": "all_time"}
    },
    "normalization": {
      "status": "reviewed", "reviewer": "agent:reviewer",
      "rationale": "Interpretation checked against the passage and its scope."
    }
  }]
}
```

Subjects must be existing model nodes; sources must be inventoried. `value` is a
JSON scalar; `null` means unknown, not negation. `polarity` is explicitly
`positive` or `negative`. Different positive values conflict only when the
predicate is in `functional_predicates`. Opposite polarities for the same value
are compared even for a multivalued property. Do not derive semantic equivalence
closure from these values.

`scope` supports `context`, `version`, `unit`, and `time`. Do not fill in unknown
facts. Time can be `all_time`, `unknown`, or an inclusive interval:

```json
{"kind":"interval","from":"2026-01-01","to":"2026-12-31"}
```

Both interval endpoints must be explicit; one may be `null` for an open end,
but at least one must have a date. Touching intervals share that day. Unknown
time yields a possible conflict rather than confirmed overlap. Distinct contexts
or versions, or disjoint periods, support a scope difference. Different units
require an explicit comparison/conversion rule; the helper invents no conversion.

Normalization defaults to `unreviewed`. A declared review is neither independent
certification nor proof of source truth. Classification applies to the supplied
normalized inputs and declared rules.

## Present evidence and consequences

Each card includes stable ID/fingerprint, kind, state, rule/version, all opposing
assertions and IDs, and each assertion's `source_id`, `locator`, and
`original_excerpt`. JSON preserves evidence and Markdown presents both sides by
case. Reciprocal exclusions produce one case per pair. Cycle cards include
witness edges; cardinality cards include the node and implicated relations.
Identifiers remain exact even when they contain slashes or are full IRIs.
A missing contract-required relation review remains an open constraint case.

Add the semantic consequences for questions, selections, required cases, and
coverage. Ask whether the assertions share a scope when its boundary is
uncertain. When they conflict in a shared scope, ask which assertion should
govern and what evidence would justify changing it. When a graph constraint
fails, show the governing rule and the expected and observed result when
available. Keep established scope differences informational and keep blocked
scans distinct from completed scans with no findings. Group a large review for
readability while keeping conflicts in different scopes separate.

## Record an explicit choice

Offer assertion precedence, scope separation, correction, evidence requests,
and deferral. Profile conflicts also allow explicit, versioned rule revision.
Do not silently weaken a rule or preselect an answer as if the user submitted it.
Do not choose automatically by confidence, recency, or vote count; an explicitly
authorized precedence policy may be followed with its evidence recorded.

The decision file contains `schema_version: "1"`, the exact report
`review_revision`, and a `decisions` list. Each entry has `conflict_id`,
`fingerprint`, `choice`, `reviewer`, and `rationale`. Additional fields depend on
choice:

- `prefer_assertion`: `assertion_id` must identify a displayed assertion.
- `separate_scopes`: `proposed_scopes` maps every assertion ID to its proposed
  scope, with an actual context, version, or time difference.
- `correct_assertions`: `replacement` describes the proposed correction.
- `request_evidence` or `defer`: retain the unresolved question and reason.
- `revise_rule`: explain the profile change and justification in `rationale`.

Do not invent decision makers, source dates, or reasons. The helper's timestamp
records when the choice was entered, not a date attributed to the user or source.

```text
uv run --script <skill-dir>/scripts/review_conflicts.py scan --model base.json --addition addition.json --contract contract.json --claims claims.json --report review-v1.json --markdown review-v1.md
uv run --script <skill-dir>/scripts/review_conflicts.py decide --review review-v1.json --decisions user-decisions.json --report choices-v1.json --markdown choices-v1.md
```

The addition is inspected in memory. Outputs are new: no baseline, sources,
existing reports, or previous decisions are overwritten. Stale revisions or
fingerprints fail, preventing a response from being applied to changed assertions.

## Apply and verify the choice

`decide` records `decision_recorded_pending_validation` or `deferred`; it neither
changes the model nor declares `resolved`. For an authorized choice, prepare a
candidate, preserve disputed evidence in history, and update the explicit scope
or representation. Rerun validation, competency questions, and conflict scanning.
If another rule fails, retain the recorded choice and expose the new problem;
do not declare resolution yet. A validation-only request does not itself
authorize applying a choice.

For `scan`/`decide`, exit **0** means no pending cases within implemented checks;
scope differences may remain. Exit **1** means open conflicts, decisions pending
validation, or deferred cases. Exit **2** means invalid input, stale review,
incomplete analysis, or engine/write error. A zero does not prove universal
absence of contradictions or OWL consistency.

Exercise same-scope negation and functional values, contextual and temporal
differences, multivalued properties, unknown values, reciprocal exclusions,
incremental additions, explicit decisions, stale fingerprints, and preservation
of all original files.
