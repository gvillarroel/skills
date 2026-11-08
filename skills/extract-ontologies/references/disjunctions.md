# Model and verify disjunctions

## Establish what the source allows

Record the governing subject, branch conditions, and evidence for inclusion or exclusion. Keep competing interpretations of ambiguous wording as separate unresolved candidates in the evidence ledger. A union axiom asserts that the domain admits the alternatives, so emit it only when the source supports that reading.

- For **at least one branch**, use `ObjectUnionOf` for class expressions, `DataUnionOf` for data ranges, or `sh:or` for SHACL branch shapes. Both branches may hold.
- For **exactly one branch**, keep the covering union and prohibit overlap within the governed scope. For two class expressions, use `A ⊑ (B ⊔ C) ⊓ ¬(B ⊓ C)`. Use `DisjointUnion(A B C)` only when the evidence establishes that `A` equals the union and the branches are disjoint everywhere. Use `sh:xone` when the graph contract requires exactly one branch to conform. [OWL 2 class expression semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions) · [OWL 2 class axioms](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expression_Axioms) · [SHACL logical constraints](https://www.w3.org/TR/shacl/#core-components-logical)
- For **at most one of two branches**, prohibit overlap without a covering union. Use `A ⊑ ¬(B ⊓ C)` for class-local exclusion, or a SHACL `sh:not` shape containing `sh:and` over the two branch shapes. A record meeting neither branch can conform.

## Place the choice at the right level

| Source requirement | OWL domain semantics | SHACL graph validation |
| --- | --- | --- |
| Every value of `p` is a `B` or `C`. Values may mix. | `A ⊑ ∀p.(B ⊔ C)` | Put `sh:or` on the property shape with value-level branch shapes. |
| At least one value of `p` is a `B` or `C`. Other values may exist. | `A ⊑ ∃p.(B ⊔ C)` | Put `sh:or` inside `sh:qualifiedValueShape` and set `sh:qualifiedMinCount 1` on the property shape. |
| All values of `p` follow the same branch. | `A ⊑ (∀p.B ⊔ ∀p.C)` | Put `sh:or` on the node shape. Each branch tests the entire `p` property with its own value restriction. |
| The record meets one of two sets of requirements. | Put the union between the complete branch expressions. Keep each branch's conjunction and restrictions inside that branch. | Put `sh:or` or `sh:xone` on the node shape. Put each branch's required fields, value restrictions, and counts inside its shape. |

All-values checks can succeed with zero values. Add an existence requirement when the source requires a value. On a property shape, `sh:xone` counts successful branches separately for each value. To count qualifying values across the property, use a qualified value count. [OWL 2 class expression semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions) · [SHACL value nodes](https://www.w3.org/TR/shacl/#value-nodes) · [SHACL qualified cardinality](https://www.w3.org/TR/shacl/#QualifiedValueShapeConstraintComponent)

For a choice between fields, test the fields in distinct branches. Counting values of an alternative path can merge identical RDF values reached through two fields and miss a double selection.

## Count the intended values

For each count, identify the property, the values being counted, and
whether other values may occur. For a composite record, specify whether
the projection includes only the existence of each component or also
its uniqueness. A bound on one component applies to that slot.

| Requirement on values of `p` | OWL restriction | SHACL property shape |
| --- | --- | --- |
| At least one qualifying value | `∃p.(B ⊔ C)` | Use `sh:qualifiedMinCount 1` with a qualified `sh:or` shape. |
| Exactly one qualifying value, with other values allowed | `=1 p.(B ⊔ C)` | Add `sh:qualifiedMaxCount 1` to the same qualified shape. |
| Exactly one value in total, which must qualify | `(=1 p.⊤) ⊓ ∀p.(B ⊔ C)` | Use `sh:minCount 1`, `sh:maxCount 1`, and `sh:or` over the value shapes. |

A value satisfying both alternatives counts once in their union.
Test zero qualifying values, one, two distinct qualifying values,
and one qualifying value plus a nonqualifying one. In OWL, explicitly
distinguish the two individuals and explicitly assert a zero count when
testing a missing required successor. In SHACL, count the RDF values
of the selected path under the chosen inference policy. [OWL 2
cardinality semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions)
and [SHACL qualified counts](https://www.w3.org/TR/shacl/#QualifiedValueShapeConstraintComponent).

For an OWL comparison view, combine equal lower and upper bounds into
an exact count only when they govern the same class or individual,
property, qualifying expression, and source premise. A minimum of one
has the same meaning as an existential restriction with the same
property and qualifier. Keep the original axioms and their evidence.
Verify mutual entailment for the whole ontology and for each changed
premise separately. Test a different guard or qualifier and bounds
from independently cited premises before accepting the rewrite.

When a lower bound exceeds its upper bound for the same count, test
whether the governed class is satisfiable as well as whether the
ontology is consistent. A consistent ontology can require that class
to be empty. [OWL 2 cardinality and inference problems](https://www.w3.org/TR/owl2-direct-semantics/#Inference_Problems)

## Test the choice and its scope

- Test each branch alone, both branches, and neither branch. Inclusive choice admits both. Exactly one rejects both. A required SHACL choice fails when the selected graph satisfies neither branch.
- Test a record with mixed values and an empty property when value scope matters. Use nonoverlapping value types in the mixed fixture to distinguish a per-value choice from a single choice for the whole property. Check that the no-value fixture remains targeted and fails only when existence is required.
- Include an otherwise comparable out-of-target record. For SHACL, verify whether the record is selected before interpreting a clean report. For an OWL class-scoped rule, explicitly place the test individual outside the governing class and check consistency with a counterexample to the scoped condition.
- If the contract selects only an exact asserted type, test a subclass
  instance as well. `sh:targetClass` follows the subclass hierarchy in
  the data graph even when optional inference is disabled. Use an
  explicit target selection when that behavior exceeds the contract.
  [SHACL class targets](https://www.w3.org/TR/shacl/#targetClass)
- Test unknown separately from explicitly ruled out. An OWL covering union can entail membership in the union without entailing either branch by itself. Test that unknown membership remains consistent and neither named branch is entailed. Explicitly excluding every branch for an in-scope individual contradicts the axiom. SHACL checks the selected graph and inference policy, so missing branch evidence can fail its conformance check while the domain fact remains unknown. [OWL 2 inference problems](https://www.w3.org/TR/owl2-direct-semantics/#Inference_Problems) · [SHACL validation](https://www.w3.org/TR/shacl/#validation)
