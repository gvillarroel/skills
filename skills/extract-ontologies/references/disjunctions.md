# Model and verify disjunctions

## Contents

- [Establish what the source allows](#establish-what-the-source-allows)
- [Place the choice at the right level](#place-the-choice-at-the-right-level)
- [Count the intended values](#count-the-intended-values)
- [Normalize Boolean forms within a premise](#normalize-boolean-forms-within-a-premise)
- [Test the choice and its scope](#test-the-choice-and-its-scope)

## Establish what the source allows

Record the governing subject, branch conditions, and evidence for inclusion or exclusion. Keep competing interpretations of ambiguous wording as separate unresolved candidates in the evidence ledger. A covering union requires membership in at least one branch. Establish permission for overlap separately within the governed scope.

- For **at least one branch**, use `ObjectUnionOf` for class expressions, `DataUnionOf` for data ranges, or `sh:or` for SHACL branch shapes. This expression admits overlap. Check the source's overlap rule before approving it as the complete choice policy.
- For **exactly one branch**, keep the covering union and prohibit overlap within the governed scope. For two class expressions, use `A ⊑ (B ⊔ C) ⊓ ¬(B ⊓ C)`. Use `DisjointUnion(A B C)` only when the evidence establishes that `A` equals the union and the branches are disjoint everywhere. Use `sh:xone` when the graph contract requires exactly one branch to conform. [OWL 2 class expression semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions) · [OWL 2 class axioms](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expression_Axioms) · [SHACL logical constraints](https://www.w3.org/TR/shacl/#core-components-logical)
- For **at most one of two branches**, prohibit overlap without a covering union. Use `A ⊑ ¬(B ⊓ C)` for class-local exclusion, or a SHACL `sh:not` shape containing `sh:and` over the two branch shapes. A record meeting neither branch can conform.

For three or more branches, **at most one** means zero or one match.
In SHACL Core, use an outer `sh:or` at the governed node or value level.
Its first branch uses `sh:xone` over the full branch list and admits one
match. Its second branch uses `sh:not` around `sh:or` over that same
list and admits zero matches. Reuse named branch shapes by IRI. Negating a conjunction of all
branches only excludes the case where every branch matches.

Build each branch from its complete requirements. A partly satisfied
branch does not count as a match. Keep requirements that apply to every
case on the governed shape, alongside the choice. For three branches,
check all three two-branch combinations as well as all three together.
Include a fully matched branch with partial evidence for another when
partial evidence is allowed.

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

When comparing supplied alternatives, separate the dispositions:

- **No supported option.** State the requirement established by the
  source and the change that rules out each offered bundle.
- **Source interpretation unresolved.** A covering union can preserve
  the supported at-least-one requirement under both inclusive and
  exactly-one readings. If the requested decision is the complete
  policy and the operative evidence establishes neither permission
  nor prohibition of overlap, state the covering requirement as
  the supported part in its own sentence and leave every complete
  option unselected. Distinguish any illustrative example from the
  operative evidence. Ask whether an in-scope case satisfying both
  branches may qualify. For that witness, state expected consistency
  under each competing complete policy and leave the observation
  empty until a check runs. Apply explicit permission or exclusion
  at its own scope.
- **Check unavailable.** Name the construct or input that prevents
  verification and the observation that would close the gap.
- **Context only.** Use an empty axiom bundle when the premise warrants
  no assertion in the requested projection.

Before approving a complete choice, compare each offered bundle with
two named cases in its governed class. Give the first one branch and
explicitly exclude the other. Give the second both branches. If the
source allows one branch alone, reject a bundle that requires both.
Check that the final disposition agrees with the source and those
witness outcomes.

Tie each open decision to its source locator, governed subject and
scope. Phrase a validation item as an expected observation for a
specific case, such as whether an in-scope record satisfying both
branches should conform. In OWL, test whether both memberships are
permitted by checking consistency with the witness's asserted class
and branch memberships. Use entailment for the separate question of
what follows from a consistent ontology. Distinguish both from SHACL
conformance on a graph. Record the observed result only when the check
ran.

For each material difference between the options, give a case in which
their expected outcomes differ. For example, ask whether a record
meeting neither branch qualifies to distinguish an exactly-one rule
from an at-most-one rule. To distinguish a ban scoped to one class
from global disjointness, give an explicitly out-of-scope case with
both memberships. If the proposed cases all produce the same outcome,
add a distinguishing case or leave that comparison open.

Keep checks for shared requirements, a valid in-scope case, and
scope boundaries even when another case separates the options.
Identify the inputs and check method, the facts asserted for the
witness, the expected outcome under each option, and the observed
outcome when executed. In SHACL, verify focus selection separately
from conformance. In OWL, check the base ontology and then check
consistency with the witness. If an option with the witness is
inconsistent, report its consistency result. Interpret entailments
only for a consistent option with those facts.

Make negative facts explicit in an OWL consistency witness. A missing
property assertion leaves room for another filler. To distinguish
a stronger existence requirement, assert zero matching fillers or
check whether each ontology entails the stronger requirement. State
the result of that exact test.

If multiple bundles have verified equivalent meaning in that premise
and retain the same typed vocabulary and evidence, select a stable
representative by content. Use the bundled
[`choose_owl_comparison_bundle.py`](../scripts/choose_owl_comparison_bundle.py)
to sort the canonical OWL Functional Syntax axiom lines in each bundle by
UTF-8 bytes and choose the lexicographically first resulting list. Keep the
renderer and ordering rule fixed.
For the same admitted bundles, changing candidate labels or display
order leaves the selected representation unchanged. Preserve the
original source and axioms alongside any comparison view.

Give the helper one JSON object mapping each premise or review group ID
to its admitted candidate IDs and canonical axiom lists. A group with
zero admitted candidates is `{}` and yields `"NONE"`. A candidate with no
assertions has the list `[]` inside its group. Complete the semantic
and evidence checks, then write the entire input JSON in one operation
with the canonical lines copied verbatim. The helper orders the
admitted candidates and writes their selected IDs.

```bash
uv run --script <skill-dir>/scripts/choose_owl_comparison_bundle.py admitted-options.json --out selected-options.json
```

## Normalize Boolean forms within a premise

When accepted snapshots use different but equivalent Boolean class
axioms, use [`normalize_owl_comparison.py`](../scripts/normalize_owl_comparison.py)
to propose a comparison ledger. It treats class restrictions as atomic
expressions and uses a fixed decision-variable order within each
premise. It can combine subclass implications, class equivalences and
class exclusions. It preserves other axiom types, unresolved premises,
and bundles outside its supported bounds.

For integer ranges, it also joins a direct intersection of one
lower-bound restriction and one upper-bound restriction on
`xsd:integer`. The range must be nonempty, and both boundary
literals must be explicitly typed as `xsd:integer`. The result
preserves each facet's inclusivity and literal spelling.

```bash
uv run --script <skill-dir>/scripts/normalize_owl_comparison.py --ledger ledger.json --comparison-view comparison-ledger.json
```

Retain the source ledger and asserted ontology. For each rewritten
premise, compare the local axioms in both directions with an independent
OWL 2 DL reasoner. Also verify whole-ontology equivalence, consistency,
typed signature, and source ownership before using the proposed view
to compare snapshots. The Boolean helper constructs the proposal.
Keep the source representation when any verification is unresolved.

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
