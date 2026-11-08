# Verify the scope of three ontology rewrites

Use the ontology-authoring skill. In each case compare the original
and revised axioms under OWL 2 Direct Semantics. All terms are distinct
unless the rules imply otherwise. Assume no other domain axioms.

The whole graph contains both premises. An isolated premise contains
only the axioms linked to it. The comparison view must preserve both.
Treat the count as a count of distinct object values.

## Case K01

- P01 states that every `links` value of a `Record` is a `Link`.
- P02 states that each `Record` has at most one `links` value whose
  `kind` includes the string `type`. P02 counts all values with that
  `kind`.
- The proposed rewrite of P02 counts only values that are a `Link`
  and have that `kind`. The rewrite keeps P01.

## Case K02

- P01 defines an unrelated record classification.
- P02 states both that every `links` value of a `Record` is a `Link`
  and that at most one `links` value has `kind` equal to `type`.
- The proposed rewrite keeps the P02 all-values type axiom and counts
  only values that are a `Link` and have that `kind`.

## Case K03

- P01 states that every `config` value of a `Record` is a `Descriptor`.
- P02 states that a `Record` with a `config` value whose `mediaType`
  includes `empty` must have an `artifactType` value.
- The proposed rewrite additionally requires the qualifying
  `config` value to be a `Descriptor` for the guard to activate.
  It keeps P01.

Write `scope-review.json` as one JSON object. It has exactly
the top-level keys `K01`, `K02`, and `K03`. Each has exactly
the three boolean fields below.

- `whole_equivalent` checks bidirectional entailment of the whole graph.
- `p02_equivalent` checks bidirectional entailment using P02 alone.
- `safe_comparison_view` is true when both checks succeed.
