---
name: curate-semantic-model
description: "Minimize semantic models while preserving sources and competency answers; model taxonomies and ontologies, validate typed additions, expose contradictions for user resolution, and compare candidate ontologies by case coverage and explicit gaps. Use for concept unification or maintained typed knowledge, not an ordinary text summary without a reusable model."
---

# Curate a minimal semantic model

Build the smallest representation that answers the required questions and
supports the required decisions without losing meaning or provenance. Start
with typed records; add facets, hierarchy, or axioms only when they provide a
needed capability. Compare parsimony only among models that meet these duties.

## 1. Select the needed capabilities

- Use this skill's self-contained JSON workflow for source inventory, typed
  modeling, conservative reduction, conflict review, and coverage reporting.
- If source acquisition or synchronization is needed, optionally select `know`
  from the available skill catalog. Its provenance registry does not establish
  concept identity. Files already supplied can be inventoried directly.
- If formal RDF, OWL, or SHACL engineering is needed, optionally select
  `extract-ontologies` from the available catalog, or use an available formal
  processor. Keep the core JSON workflow usable without either companion.
  Report unavailable formal checks as not checked.
- Run the bundled standard-library helpers with Python 3.11 or later through
  `uv run --script`. In commands below, replace `<skill-dir>` with this skill's
  actual directory; write task inputs and outputs outside that directory.
- Produce only the requested deliverables. Keep one authoritative model and
  derive tables, graphs, spreadsheets, or reports from it when useful.

## 2. Define preservation obligations

Inventory the original source units with stable IDs and locators. Preserve
their wording, votes, selected flags, weights, required status, and provenance.
Distinguish inventoried evidence from concepts extracted from that evidence.

Choose the least expressive sufficient representation: typed records, facets,
taxonomy, then ontology as needed. Do not force every stage into every task.
Declare types, allowed relations, attributes, cardinalities, endpoint rules,
open or closed attribute policy, and any predicate-specific cycle restriction.
Define meaningful competency questions and expected answers before reduction.

Read [methodology.md](references/methodology.md) for semantic distinctions and
[model-contract.md](references/model-contract.md) for the executable contract,
inline input examples, supported operators, and diagnostics. Acceptance fixtures
are maintenance resources, not required runtime inputs.

## 3. Propose and minimize conservatively

Separate retrieval similarity from identity. Distinguish aliases, equivalent
acceptance criteria, shared topics, ALL/ANY composition, part relations,
subclasses, and instances. Check homonyms and both directions of any proposed
merge; overlap or a shared parent does not establish transitive equivalence.
For example, retrieving, storing, and learning skills may remain separate
capabilities even when they share a topic.

Reuse an existing concept when its definition and acceptance scope really fit.
Retain distinctions needed by queries, voters, required cases, or partial product
support. Preserve original selections through explicit source-to-concept maps;
do not transfer approval to unrelated children or count a composite and its
components twice without an explicit scoring policy.

Compare candidate representations by preserved answers, source coverage,
exceptions, complexity, and review effort. State when reduction is a local
heuristic; do not claim a formal MDL optimum or globally minimal ontology.
The helper only removes exact duplicate assertions and explicitly permitted
transitive materialization, retaining audit history. It does not merge nodes or
simplify definitions. `skos:broader` is not transitive by default.

## 4. Validate complete proposed states

```text
uv run --script <skill-dir>/scripts/semantic_model.py validate --model model.json --contract contract.json --report validation.json
uv run --script <skill-dir>/scripts/semantic_model.py stage --base model.json --addition addition.json --contract contract.json --candidate candidate.json --report staging.json
uv run --script <skill-dir>/scripts/semantic_model.py reduce --model model.json --contract contract.json --candidate reduced.json --report reduction.json
```

Validate the baseline, then the entire candidate, including interactions with
existing nodes. Do not overwrite inputs or existing candidates, silently weaken
rules, or repair source wording to obtain a pass. Follow the user's existing
authorization when applying a valid change; a request for validation alone does
not authorize integration. Routine checks do not require another approval.

Keep `contract_status`, `semantic_status`, and `engine_status` distinct. Core exit
codes are 0 for conformity, 1 for data violations, and 2 for unsupported contracts,
malformed input, processor errors, or I/O errors. Core semantic review remains
`not_run` even when the JSON contract passes. A missing formal processor is not
a semantic pass. For RDF workflows, pin the ontology/imports, processor version,
and inference regime; report SHACL conformity and OWL reasoning separately.

## 5. Expose contradictions for a user decision

Normalize subject, predicate, value, polarity, context, version, time, and unit
without inventing missing facts. Absence is not negation; different values are
not contradictory unless the predicate is exclusive in comparable scopes.
Inspect free-text conditions, quantifiers, exceptions, and evidence as well as
the typed graph. A conflict may reveal a bad rule or representation.

Create review cards showing both assertions, source passages and locators,
the applicable rule/version, uncertainty, and consequences for queries,
selections, and coverage. Distinguish confirmed conflicts, possible conflicts,
scope differences, and constraint conflicts. Read
[contradiction-review.md](references/contradiction-review.md).

```text
uv run --script <skill-dir>/scripts/review_conflicts.py scan --model model.json --contract contract.json --claims claims.json --report review.json --markdown review.md
uv run --script <skill-dir>/scripts/review_conflicts.py scan --model model.json --contract contract.json --addition addition.json --report addition-review.json
uv run --script <skill-dir>/scripts/review_conflicts.py decide --review review.json --decisions decisions.json --report decisions-report.json --markdown decisions-report.md
```

The addition is inspected in memory. These checks are bounded; they do not
claim exhaustive natural-language contradiction detection or OWL reasoning.
Offer concrete choices: prefer an assertion, separate scopes, correct wording,
request evidence, or defer; offer explicit rule revision when appropriate.
Do not resolve automatically by recency, confidence, or votes. A user-approved
precedence policy may be applied with its provenance. Bind decisions to the
review revision and conflict fingerprint. Recorded decisions remain pending
validation: apply an authorized candidate, preserve evidence, rerun checks, and
rescan before declaring the conflict resolved.

## 6. Compare ontologies by cases and residual gaps

Inspect candidate ontology classes, axioms, relations, identity rules, and
constraints for internal contradictions, not just disagreement with external
documents. Preserve ontology IRI, version, artifact hash, imports, and inference
configuration. Freeze a shared suite of cases, expected answers, methods,
required flags, and weights. Read
[ontology-coverage.md](references/ontology-coverage.md).

```text
uv run --script <skill-dir>/scripts/ontology_coverage.py --input coverage-input.json --report coverage.json --markdown coverage.md
uv run --script <skill-dir>/scripts/ontology_coverage.py --input coverage-input.json --previous previous-coverage.json --report coverage.json
```

This helper aggregates supplied evidence; it does not run queries or reasoners.
Report full passes over all applicable cases, the denominator, and every
residual failure, partial result, unknown, engine error, or conflicted result.
Nine passes and one unknown mean 90% covered and 10% unverified, not a proved
10% failure. Keep weighted coverage separate and expose required-case failures.
Keep SHACL and OWL statuses distinct. An adoption threshold is not permission
to ignore required cases or unresolved contradictions. Test a composition as
a new candidate; do not add coverage percentages. Compare progress only for
the same frozen suite, and let the user decide which residual gaps to accept.

## 7. Verify and deliver

Exercise meaningful positive and invalid cases for important rules. During
skill maintenance, run the bundled helper tests; normal runtime tasks can
create their own small inputs without reading acceptance fixtures. Deliver the
canonical model, contract, source map, changes and competency results, together
with actionable errors, conflict choices, coverage denominators, and remaining
uncertainty as the task requires. Derive only useful views and avoid a broad
benchmark for every small update. Use the user's requested delivery language.
