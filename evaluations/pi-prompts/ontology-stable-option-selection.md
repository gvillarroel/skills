# Select source-bound alternatives across presentations

Use the ontology-authoring skill to review the supplied OWL 2 DL
alternatives. All named classes, properties, and individuals used in
the options are declared, and there are no background axioms. Each numbered
premise owns its assertions. Verify the disjunction and its scope.
If several options for one premise are admissible, apply the skill's
rule for selecting a stable comparison representation. Treat the
displayed Functional Syntax axiom lines as the canonical form for
this exercise.

## Inclusive requirement

Every access request has the emergency flag, the staff flag, or both.
Represent flags as class membership. The first presentation is A1.

- `a14` has `SubClassOf(:AccessRequest ObjectUnionOf(:EmergencyFlag :StaffFlag))`.
- `a82` has `SubClassOf(:AccessRequest ObjectComplementOf(ObjectIntersectionOf(ObjectComplementOf(:EmergencyFlag) ObjectComplementOf(:StaffFlag))))`.
- `a02` has `SubClassOf(:AccessRequest ObjectIntersectionOf(:EmergencyFlag :StaffFlag))`.

The second presentation, A2, offers the same options with new labels
and in a different order. `z03` has the bundle previously labeled
`a14`. `z14` has the bundle previously labeled `a02`. `z21` has
the bundle previously labeled `a82`.

## Exactly one format under a guard

Every submitted delivery uses exactly one format, electronic or paper.
A submission in neither or both formats fails. The two format classes
can overlap for items outside the submission requirement. B1 offers
these bundles.

- `b13` has
  `SubClassOf(:SubmittedDelivery ObjectIntersectionOf(ObjectUnionOf(:Electronic :Paper) ObjectComplementOf(ObjectIntersectionOf(:Electronic :Paper))))`.
- `b76` has both
  `SubClassOf(:SubmittedDelivery ObjectUnionOf(:Electronic :Paper))`
  and
  `SubClassOf(:SubmittedDelivery ObjectComplementOf(ObjectIntersectionOf(:Electronic :Paper)))`.
- `b02` has
  `SubClassOf(:SubmittedDelivery ObjectUnionOf(:Electronic :Paper))`
  and `DisjointClasses(:Electronic :Paper)`.

B2 offers the same options with new labels and in a different order.
`y02` has the bundle previously labeled `b76`. `y95` has the bundle
previously labeled `b02`. `y14` has the bundle previously labeled
`b13`.

## Coverage and context

Project named assertions for the calibration record. Preserve the
specified datatype and exclude display details.

- C1 says that the calibration record has integer level 7.
  `c10` has `DataPropertyAssertion(:level :calibration "8"^^xsd:integer)`.
  `c70` has `DataPropertyAssertion(:level :calibration "7"^^xsd:string)`.
  `c05` is an empty bundle.
- C2 says that the calibration record's display uses a large heading.
  `c43` is an empty bundle. `c11` has
  `ClassAssertion(:CalibratedRecord :calibration)`.

Write `selected-options.json` as one JSON object with exactly the keys
`A1`, `A2`, `B1`, `B2`, `C1`, and `C2`. Each value is the selected
option ID string for that presentation or `NONE` if no option is
supported. Do not add fields.
