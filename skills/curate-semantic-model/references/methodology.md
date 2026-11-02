# Minimal semantic representation methodology

## Contents

- [Preservation](#preserve-obligations-before-minimizing-structure)
- [Expressive power](#choose-only-the-needed-expressive-power)
- [Unification](#classify-a-proposed-unification-before-applying-it)
- [Relation semantics](#keep-formal-relation-semantics-explicit)
- [Reduction](#reduce-with-evidence-and-regression-checks)
- [Typed additions](#validate-additions-by-declared-type)
- [Optional capabilities](#compose-optional-capabilities-without-a-dependency)
- [Semantic references](#semantic-references)

## Preserve obligations before minimizing structure

Define what the model must preserve: original evidence and its selected flags,
votes and weights; distinctions that change acceptance; answers to competency
questions; and the ability to validate future additions. Use one authoritative
representation and derive useful views from it. A smaller raw-text archive is
not a sufficient structured model if it cannot answer these questions.

Count nodes, relations, predicates, constraints, exceptions, and maintenance
burden, but compare complexity only among models that satisfy those obligations.
Counts support a parsimony argument; they are not a formal minimum-description-
length calculation or proof of a globally minimal ontology. Describe any local
heuristic and the alternatives it rejected.

## Choose only the needed expressive power

| Representation | Use when | Avoid assuming |
|---|---|---|
| Typed records | Fields and validation answer the questions. | A graph is necessary merely because records are related. |
| Facets | Independent dimensions such as domain, maturity, or source improve retrieval. | Every facet value must become a class or parent. |
| Taxonomy | Broader/narrower navigation and reusable concept scope are needed. | Every parent means a logical superclass, or every term has one parent. |
| Ontology | Typed relations, logical definitions, identity, restrictions, or inference are required. | More axioms automatically improve fidelity or coverage. |

These are capabilities, not mandatory sequential deliverables. Use typed
records with a few relations if they suffice. Introduce a formal ontology only
for obligations that need its semantics.

## Classify a proposed unification before applying it

| Relationship | Treatment |
|---|---|
| Alias | One concept, multiple labels; preserve language and source wording. |
| Equivalent acceptance scope | Consider one canonical concept only after reviewing both directions and exceptions. |
| Shared topic or retrieval similarity | Link or group for navigation; keep distinct acceptance criteria. |
| Broader/narrower concept | Keep distinct nodes and define the hierarchy's meaning. |
| Subclass (`is_a`, `rdfs:subClassOf`) | Every instance of the child satisfies the parent's definition. |
| ALL composition | All component criteria are required; preserve each component's evidence and support. |
| ANY composition | Alternatives satisfy an explicitly stated condition; do not silently treat them as ALL. |
| Part relation | A component is part of something; this does not make it a subclass. |
| Instance-of | A particular entity instantiates a type; do not confuse it with a subclass. |

An OWL intersection is a logical class expression, not a generic parts list.
An editorial grouping node becomes a logical class only after defining what
membership means. Shared parents, similar names, and overlapping extensions do
not prove identity or acceptance equivalence. Pairwise similarity is not a
transitive equivalence relation. Check homonyms, scope, negation, quantifiers,
exceptions, time, and units before combining concepts.

For skills requirements, retrieving, storing, and learning skills can remain
three different acceptance tests. A parent that requires retrieving AND storing
must preserve both tests. Selection of that parent does not imply approval of
learning, and partial product support must remain visible. Avoid counting both
the parent and its components unless an explicit scoring policy requires it.

## Keep formal relation semantics explicit

- `skos:broader` expresses a direct semantic relation and is not itself
  transitive. `skos:broaderTransitive` supports the transitive hierarchy.
- `skos:closeMatch` is not transitive. `skos:exactMatch` is transitive, but a
  retrieval mapping is not automatically `owl:sameAs` or equivalent acceptance.
- A directed acyclic graph is an application choice for a specified predicate.
  A cycle is not automatically an OWL inconsistency, and multiple parents are
  not automatically an error.
- SHACL's data-graph constraints and OWL's open-world logical semantics answer
  different questions. Do not infer falsity from a missing OWL assertion.

## Reduce with evidence and regression checks

1. Freeze source IDs, original wording and marks, scope, contract version, and
   meaningful competency questions with expected answers.
2. Generate candidates using lexical and semantic retrieval if helpful. Treat
   retrieval scores as review priorities, not identity proofs.
3. Classify candidate relations using the distinctions above. Record evidence
   for and against merging and explain why a retained difference matters.
4. Compare a proposed representation against the baseline. Preserve source
   bindings, independent selection/weight information, required status, partial
   support, and query answers. Review both directions of an equivalence claim.
5. Validate the complete candidate and inspect new conflicts, not just the
   added fragment. Keep rejected alternatives and removed assertions in audit
   history where needed; a smaller active graph may use more serialized bytes.
6. Measure preserved coverage and reduced complexity. If simplification loses
   an obligated answer or hides a residual case, reject or revise it.

Do not compute equivalence closure from overlapping concepts or a shared
parent. The bundled reducer performs only exact-assertion deduplication and
explicitly permitted transitive-edge reduction, preserving all sources and
nodes. It does not establish semantic equivalence, simplify definitions, or
merge concepts. Direct-edge queries and reachability queries are different:
removing an edge may preserve reachability but change a direct-edge answer.

## Validate additions by declared type

Declare required fields, attribute values, endpoint types, cardinalities,
allowed predicates, provenance, and any predicate-specific cycle rule.
State whether unknown attributes are tolerated or rejected. An application
record contract may require data to be present; do not describe that check as
OWL entailment or assume a unique-name principle for real-world entities.

Keep contract conformity, semantic review, and engine execution separate.
Unsupported rules and failed processors are not passes. Errors should identify
the entity, rule/version, location, expected and actual values, severity, and
an actionable repair. Exercise a valid case and a meaningful invalid mutation
for each important constraint; avoid tests that merely repeat implementation.

Source inventory, extracted concepts, source-to-concept bindings, and correct
answers are separate evidence layers. A registered source does not prove that
its meaning was extracted. A binding proves only an explicit link unless the
semantic alignment was reviewed. Report experimental counts within their
actual scope; do not generalize one corpus's reduction ratio to all domains.

## Compose optional capabilities without a dependency

The local JSON contract, conflict queue, and coverage reports work without
other skills. If available and useful, select `know` from the skill catalog for
source management, or `extract-ontologies` for evidence-led RDF/OWL/SHACL work.
Neither a source registry nor a formal serializer replaces semantic review.
If a needed formal processor is unavailable, name the unperformed check and
continue the supported workflow without claiming a formal pass.

## Semantic references

Use [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/) for SKOS relation
semantics, [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) for logical modeling,
and [SHACL](https://www.w3.org/TR/shacl/) for data-graph validation. Pin the
processor and supported standard version when using formal checks. A newer
working draft, such as SHACL 1.2, does not imply support in an installed engine.
For the distinction between a parsimony heuristic and formal description-length
model selection, see [Minimum Description Length](https://arxiv.org/abs/1908.08484).
