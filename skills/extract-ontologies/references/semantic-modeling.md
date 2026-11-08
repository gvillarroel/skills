# RDF, OWL 2, and SHACL Modeling Guide

## Contents

1. [RDF graph policy](#1-rdf-graph-policy)
2. [OWL and SHACL boundary](#2-owl-and-shacl-boundary)
3. [OWL 2 profile selection](#3-owl-2-profile-selection)
4. [Modeling hazards](#4-modeling-hazards)
   - [Reconcile axioms across extraction modules](#reconcile-axioms-across-extraction-modules)
5. [Versioning and imports](#5-versioning-and-imports)
6. [Provenance](#6-provenance)
7. [Validation interpretation](#7-validation-interpretation)

## 1. RDF graph policy

Use absolute IRIs for durable resources. Treat prefix declarations and relative IRIs only as serialization conveniences. Use blank nodes for local structures, not identifiers that must survive file boundaries or repeated extraction.

An RDF graph is a set of triples: order and duplicate serialization carry no meaning. An RDF dataset contains one default graph and zero or more named graphs. Document what the default graph means and how validation selects or unions graphs. A graph name alone does not establish provenance, endorsement, or truth.

Keep these layers distinct unless the consumer contract requires a documented union:

- accepted source assertions;
- ontology axioms;
- machine-inferred triples;
- unreviewed candidates;
- SHACL shapes;
- validation reports;
- provenance metadata.

## 2. OWL and SHACL boundary

| Concern | OWL 2 | SHACL |
|---|---|---|
| Primary purpose | Logical meaning and entailment | Validation of a selected data graph |
| Missing property | May be unknown or supplied by an unnamed model element | `sh:minCount` can report it |
| Too many values | May imply value equality under a maximum cardinality or functional property | `sh:maxCount` reports graph values |
| Domain/range | Infers types from property use | `sh:class`, `sh:datatype`, and node shapes validate values |
| Closed records | Open world by default | `sh:closed true` with explicit ignored properties |
| Different IRIs | May denote the same individual | Normally distinct RDF terms for graph validation |
| Result | Entailments or consistency judgment | Validation report over focus nodes |

Do not mechanically copy cardinalities between OWL and SHACL. Add both only when both the domain semantics and data contract independently require them.

Model an exact RDF datatype separately from a value bound. If ordinary `xsd:integer` literals are allowed and their values must be nonnegative, combine `sh:datatype xsd:integer` with `sh:minInclusive 0`. Requiring `xsd:nonNegativeInteger` instead checks that specific datatype IRI and can reject conforming data.

Check that the target still selects the record after removing a required assertion. A shape scoped with `sh:targetClass` can miss a record whose only qualifying `rdf:type` triple was removed. Use an independently supported target or record the detection limit in the evidence ledger. When a condition compares an RDF term, exercise it with the actual term kind, such as a role IRI in `sh:hasValue`.

## 3. OWL 2 profile selection

| Profile | Prefer when | Common caution |
|---|---|---|
| OWL 2 EL | The terminology has very many classes/properties and needs scalable classification | Limited negation, disjunction, and universal/cardinality constructs |
| OWL 2 QL | Instance data is large and queries must be rewritten to a relational store | Expressivity is intentionally narrow; cardinality restrictions are excluded |
| OWL 2 RL | Rule-based materialization over RDF is the deployment model | Rule closure is not a complete OWL 2 DL consistency/profile certification |
| OWL 2 DL | Required semantics exceed the profiles and a DL reasoner is available | Respect structural and global restrictions; reasoning cost can be high |

The three profiles are independent; none is a subset of another. Record the profile and confirm it with a profile-aware checker after serialization.

## 4. Modeling hazards

- `rdfs:domain` and `rdfs:range` infer types. They do not reject a subject or object with an absent type.
- `owl:sameAs` is global logical equality. Prefer a local match record, SKOS mapping, or candidate alignment when substitutability is not proven.
- A functional property with two values can entail that the values are equal; it is not a data-quality violation by itself.
- `owl:allValuesFrom` constrains known and possible values but does not require a value. Pair it with an existential restriction only when the domain meaning requires existence.
- Minimum cardinality can be satisfied by unnamed individuals. It does not prove that the serialized record contains that many values.
- Class disjointness can make an ontology inconsistent. Use it only for impossible overlap, not for a user-interface category choice.
- Property chains, transitivity, symmetry, and inverses can create many implicit assertions. Test them on adversarial fixtures.
- OWL annotations carry documentation and provenance but do not affect OWL 2 Direct Semantics.
- Recursive SHACL shapes are not portable under the 2017 Recommendation. Prefer acyclic Core shapes.
- Warning and info severities still produce validation results under SHACL 2017; processor options that ignore them change the conformance policy and must be recorded.

### Reconcile axioms across extraction modules

Bind taxonomy, property, and restriction proposals to the same versioned
term registry before assembly. Keep each module's evidence and its
scope. When the modules propose several domains or ranges for one
property, review their conjunction and confirm that it is intended.
Retain each supported domain and range as a separate axiom and evidence
row. Ingest and compare the two sets independently, including properties
that declare only one side. Read [disjunctions.md](disjunctions.md) when
the source specifies alternatives or when the scope of a choice needs
validation.
Review inherited disjointness and restrictions against the assembled
hierarchy before accepting the merged graph.

To distinguish a class-scoped target from a property-wide range,
probe the target rule with a subject explicitly outside the class.
First check that the link by itself is possible. An independent
domain may already force the subject into the class. Then add a
filler explicitly outside the target type. Run the contrast on the
isolated premise if other axioms could confound it. When checking
optionality, explicitly require zero successors. A missing asserted
link still allows a successor under open-world semantics.

Record unresolved proposals separately from emitted axioms. Compare the
complete declarations and axiom sets across independent runs. Equal axiom
sets can coexist with different declared vocabularies.

Keep the original asserted graph when producing a normalized comparison view. In OWL, a union on the left of a subclass axiom or an intersection on the right can be split into separate subclass axioms. An intersection on the left is a joint condition. A normalization that splits it changes the meaning. Verify mutual entailment and the same typed signature for the normalized view, and report its RDF identity separately.

For an OWL comparison view, normalize qualified object minimum one to
an existential over the same property and filler. Normalize qualified
object maximum zero to an all-values restriction over the same
property with the original filler complemented. Keep the governing
class, property direction, and premise attribution. Recheck the
profile and mutual entailment for the whole graph and each changed
premise. [OWL 2 Direct Semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions)

## 5. Versioning and imports

Give an ontology series one stable ontology IRI and each immutable release a distinct version IRI. Keep old version IRIs retrievable. Use imported version IRIs when reproducibility is more important than automatically following the current release.

Resolve imports before profile checking, consistency checking, or reasoning. Imports are transitive. Build a manifest that records:

- requested import IRI;
- resolved local file;
- ontology IRI and version IRI found in that file;
- content digest;
- retrieval date;
- license;
- compatibility decision.

Do not load two versions of one ontology series into a closure unless the combination has been reviewed. Treat `owl:priorVersion`, `owl:backwardCompatibleWith`, and `owl:incompatibleWith` as annotations that still require tests.

## 6. Provenance

Use PROV-O for lineage: source and generated artifacts as `prov:Entity`, extraction and validation runs as `prov:Activity`, and software or operators as agents. Link them with `prov:used`, `prov:wasGeneratedBy`, `prov:wasDerivedFrom`, and `prov:wasAssociatedWith`.

Use OWL axiom annotations to attach evidence to asserted OWL axioms. Under RDF 1.1, use RDF reification for an unasserted candidate claim; remember that reifying a triple neither asserts it nor follows from asserting it. Use Web Annotation selectors for exact text positions or quotes in versioned sources.

Define confidence in a project namespace, including its scale and reviewer meaning. PROV-O does not define a confidence probability.

## 7. Validation interpretation

Record three distinct outcomes:

1. **Conformant** — validation completed and `sh:conforms` is true.
2. **Non-conformant** — validation completed and produced results.
3. **Processor failure** — validation could not complete because inputs, shapes, entailment, recursion, resources, or features were invalid or unsupported.

Never report processor failure as ordinary non-conformance. Keep the data and shapes immutable and serialize the validation report separately. Compare reports only when graph construction, shapes, entailment, processor, and configuration are equivalent.

For an OWL competency question, record whether the expected result is an asserted fact, an entailment, or a non-entailment. Compare a positive fixture with a near-counterexample that removes or changes one premise. For example, one observed certified value does not establish an all-values restriction under the open-world assumption. When a source explicitly warrants the named individual's closure, test the classification with that local premise and test non-entailment on a comparable individual without it.

For an intentionally inconsistent test ontology, check the expected contradiction and the consistency of a minimal repaired sibling. Use asserted-axiom checks for the inconsistent artifact. Unrestricted entailment from an inconsistent theory cannot establish that its intended ontology was recovered.
