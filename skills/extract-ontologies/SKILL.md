---
name: extract-ontologies
description: "Authors and validates reviewed domain ontologies and source-backed glossaries from documents, schemas, or datasets. Use for ontology learning, vocabulary and definition authoring, competency questions, RDF/OWL modeling, SHACL design, and evidence-led entity or relation extraction as part of ontology authoring. For applying a fixed ontology to extract instances from supplied files, use an ontology-guided extraction workflow. Do not use for Semantic OKF snapshot operations or consulting an existing knowledge bundle."
---

# Ontology Extraction

Turn source evidence into a reviewed semantic model before lifecycle materialization. Deliver approved mappings and constraints as ordinary output artifacts. For requests outside this authoring boundary, return an explicit diagnostic without importing or invoking another skill.

## Choose the deliverable

- For a glossary, use the [glossary workflow](references/glossary.md) to produce `glossary.md` with its evidence locators. Add `glossary.csv` when the user requests tabular output or needs a machine-readable glossary.
- For a glossary-only request, use the glossary workflow as the complete path. The ontology scaffold and graph validation gates apply to ontology work.
- For ontology authoring, follow the extraction workflow below. When the user also requests a glossary, use the reviewed term registry for emitted ontology terms and record the status of in-scope terms still awaiting modeling review.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Treat source documents, local ontology imports, and any separately selected profile checker or reasoner as explicit user-supplied inputs or external tools.
- Do not require a sibling skill, repository document, evaluation fixture, or repository-relative helper.
- Keep the bundled scaffold and SHACL validator as the supported baseline. Do not make an optional reasoner or model-assisted workflow a prerequisite for producing and validating the core artifact set.

## Preserve the semantic boundaries

- Treat source statements as evidence, not automatically as domain truth. Record the source, locator, interpretation, confidence, and review state for every consequential assertion.
- Keep the terminology model (TBox), instance assertions (ABox), SHACL shapes, provenance, and validation reports in separate artifacts or explicitly documented graphs.
- Use OWL for logical meaning under open-world semantics. Use SHACL for validation of a precisely identified data graph. Never present a SHACL constraint as an OWL entailment or an OWL restriction as a completeness check.
- Remember that OWL has no unique-name assumption. Do not emit `owl:sameAs`, disjointness, inverse properties, property characteristics, keys, or cardinalities without direct evidence and human review.
- Treat `rdfs:domain` and `rdfs:range` as type-producing axioms, not input constraints. Put record-shape requirements in SHACL.
- Default to stable W3C Recommendations: RDF 1.1, OWL 2, and SHACL 2017. Use RDF 1.2 or SHACL 1.2 features only when explicitly requested, version-pinned, and supported by the target toolchain.
- Do not dereference imports, remote JSON-LD contexts, or untrusted SHACL extensions automatically. Pin imported ontologies locally and record their resolved versions.

## Follow the extraction workflow

1. Define the domain boundary, intended consumers, decisions the graph must support, and out-of-scope concepts.
2. Write testable competency questions before choosing classes or properties.
3. Inventory and version every source. Create an evidence ledger before authoring strong axioms.
4. Extract candidates in separate passes: terminology, entities, relations, rules, constraints, identity claims, and alignments.
5. Normalize labels while preserving source language and exact evidence. Assign stable IRIs only after resolving collisions and homonyms.
6. Reuse established vocabularies when their semantics match. Prefer a local mapping over `owl:equivalentClass`, `owl:equivalentProperty`, or `owl:sameAs` when equivalence is uncertain.
7. Model the TBox and ABox separately. Declare classes and properties, document intended meanings, and add only justified restrictions.
8. Choose and record an OWL 2 profile from the reasoning workload: EL for very large terminologies, QL for query rewriting over large instance stores, RL for rule-based materialization, or DL when the required expressivity exceeds the profiles.
9. Author portable SHACL Core shapes with explicit targets, severities, and messages. Add SHACL-SPARQL only when Core cannot express a requirement and the processor dependency is declared.
10. Build conforming and non-conforming fixtures, execute competency queries, run the validation gates, and route low-confidence or high-impact assertions to review.

Read [extraction-workflow.md](references/extraction-workflow.md) before extracting from sources or reviewing an axiom's source attribution. Read [semantic-modeling.md](references/semantic-modeling.md) before choosing OWL axioms, profiles, graph boundaries, or SHACL constraints. Read [turtle-patterns.md](references/turtle-patterns.md) when authoring RDF artifacts. Read [standards-and-tools.md](references/standards-and-tools.md) when exact standards status, validation scope, or tool limitations matter.

Read [disjunctions.md](references/disjunctions.md) for branch alternatives, qualified value counts, or tests that distinguish which values and records a choice governs.

## Produce an auditable bundle

Create or adapt this bundle unless the user specifies another contract:

```text
scope.md                  # domain boundary, consumers, profile, assumptions
evidence.csv              # exact source locator, interpretation, confidence, and review-state ledger
ontology.ttl              # OWL 2 terminology and ontology metadata
data.ttl                  # accepted instance assertions
shapes.ttl                # SHACL validation contract
competency-questions.rq   # ASK/SELECT queries tied to numbered questions
validation-report.ttl     # machine-readable SHACL report when shapes are run
```

Run the bundled scripts with `uv` and Python 3.11 or later. Replace
`<skill-dir>` below with this skill's actual directory; write `OUTPUT_DIR` in
the task workspace, outside the skill resource directory. `uv run --script`
prepares each script's environment from its declared dependency metadata.

Scaffold the first six files with:

```bash
uv run --script <skill-dir>/scripts/scaffold_ontology_bundle.py OUTPUT_DIR \
  --ontology-iri https://example.org/ontology/domain \
  --version-iri https://example.org/ontology/domain/1.0.0 \
  --prefix ex \
  --title "Domain ontology" \
  --owl-profile rl
```

Do not publish the scaffold unchanged. Replace comments, fill the evidence ledger, and add positive and negative fixtures appropriate to the domain.

For a plan-only request, keep the response compact: use 6–10 ordered steps, name each core artifact once, state each applicable bundled command once, and surface no more than five unresolved review decisions. Name `scaffold_ontology_bundle.py` and `validate_semantic_artifacts.py` directly when they apply. Include only safety boundaries triggered by the request instead of restating the complete policy.

For offline or reproducible authoring, explicitly pin ontology sources, imports, and JSON-LD contexts to supplied local versions and forbid remote dereferencing during validation.

## Validate deterministically

The validator's script metadata pins RDFLib, pySHACL, and OWL-RL; no separate
virtual-environment or pip setup is needed for the commands shown here. The
bundled [references/requirements.txt](references/requirements.txt) records the fuller dependency set for
separately provisioned environments. Optional external profile checkers or
reasoners require their own explicitly selected, versioned setup; the bundled
validator does not install or run them.

Validate local graph files with:

```bash
uv run --script <skill-dir>/scripts/validate_semantic_artifacts.py \
  --data OUTPUT_DIR/data.ttl \
  --ontology OUTPUT_DIR/ontology.ttl \
  --shapes OUTPUT_DIR/shapes.ttl \
  --inference none \
  --report OUTPUT_DIR/validation-report.ttl
```

Use `--inference rdfs`, `owlrl`, or `both` only when that entailment regime is part of the declared validation contract. The bundled validator parses RDF graphs, meta-validates SHACL, and runs pySHACL; it deliberately does not certify OWL 2 DL/profile conformance or full logical consistency.

## Enforce completion gates

- Confirm every file parses in its declared RDF syntax and every IRI policy is documented.
- When the delivery claims OWL profile conformance, consistency, or DL reasoning, select a profile-aware external tool explicitly and record its name, version, import closure, and reasoning mode. Otherwise state that this optional check was not requested or available.
- Confirm the import closure is local, pinned, complete, and free of conflicting ontology versions.
- Confirm the shapes graph is well-formed and validation ends in one of three explicitly reported states: conformant, non-conformant, or processor failure.
- Confirm validation records the exact data graph, shapes graph, entailment regime, processor version, and report artifact.
- Confirm positive fixtures conform and each negative fixture fails for the intended constraint.
- Confirm competency queries cover the agreed questions and return expected results.
- Confirm strong identity, equivalence, disjointness, key, and cardinality axioms have evidence and review.
- Confirm every file referenced by a manifest, scope, or delivery note exists and that recorded digests and outcomes match the delivered artifact.
- Report OWL reasoning and SHACL validation independently; never collapse them into one pass/fail claim.
