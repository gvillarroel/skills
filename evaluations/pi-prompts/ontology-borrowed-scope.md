# Verify the scope of three ontology rewrites

Use the ontology-authoring skill. In each case compare the original
and revised axioms under OWL 2 Direct Semantics. Assume no other
domain axioms. Use open-world semantics, under which different
individual names may denote the same object.

The whole graph contains both premises. An isolated premise contains
only the axioms linked to it. Check equivalence in both scopes.
A count refers to distinct object values. The condition that a value
has a specified string means that the property has at least that
`xsd:string` value. The condition permits other values of the property.

## Case K01

- P01 states that every `links` value of a `Record` is a `Link`.
- P02 states that each `Record` has at most one `links` value with
  the string `type` as a `kind` value.
- The rewrite counts only `links` values that are both a `Link` and
  have the string `type` as a `kind` value. It keeps P01.

## Case K02

- P01 states that each `Beta` is a `Peer`.
- P02 states both that every `links` value of a `Record` is a `Link`
  and that each `Record` has at most one `links` value with the string
  `type` as a `kind` value.
- The rewrite keeps P01 and the P02 all-values type axiom. It counts
  only `links` values that are both a `Link` and have the string
  `type` as a `kind` value.

## Case K03

- P01 states that every `config` value of a `Record` is a `Descriptor`.
- P02 states that a `Record` with a `config` value that has the string
  `empty` as a `mediaType` value must have an `artifactType` value of
  type `xsd:string`.
- In the rewrite, the guard applies when at least one `config` value
  is both a `Descriptor` and has the string `empty` as a `mediaType`
  value. The rewrite keeps the P02 requirement for `artifactType`
  and keeps P01.

Write `scope-review.json` as one JSON object. It has exactly
the top-level keys `K01`, `K02`, and `K03`. Each has exactly
the three boolean fields below.

- `whole_equivalent` checks bidirectional entailment of the whole graph.
- `p02_equivalent` checks bidirectional entailment using P02 alone.
- `safe_comparison_view` is true when both checks succeed.
