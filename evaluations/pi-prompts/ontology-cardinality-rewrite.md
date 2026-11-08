# Review an OWL comparison view

Use the supplied ontology-authoring skill to review the proposed
rewrites and test obligations below. These are eight independent
examples. Assume OWL 2 Direct Semantics, a consistent background,
no extra axioms, and distinct names for predicates and classes.
The displayed count notation applies to a single named property.

For each of S01–S05, decide whether the original and proposed
ontology entail each other as a whole, and whether each corresponding
source premise separately entails its proposed translation and the
reverse. Set `publish` to whether the rewrite is safe as a comparison
view that must also preserve attribution.

| ID | Original | Proposal |
| --- | --- | --- |
| S01 | One premise states minimum two and maximum two `hasSensor` values of class `Calibrated` for each `Dock`. | The same premise states exactly two such values. |
| S02 | The first premise states minimum two calibrated `hasSensor` values for `Dock`. The second states maximum two with the same scope and qualifier. | The first premise states exactly two such values. The second contains no axiom. |
| S03 | One premise states minimum two calibrated `hasSensor` values for `Dock` and maximum two total `hasSensor` values for `Dock`. | The same premise states exactly two calibrated `hasSensor` values for `Dock`. |
| S04 | One premise requires minimum two total `hasSensor` values for `InspectedDock` and maximum two total `hasSensor` values for `Dock`. | The same premise states exactly two total `hasSensor` values for `Dock`. |
| S05 | One premise states minimum two and maximum two calibrated `hasSensor` values for the named individual `dock17`. | The same premise states exactly two such values for `dock17`. |

S06 uses two axioms that give `Dock` a minimum of three and a
maximum of two for the same total `hasSensor` count. No instance
of `Dock` is asserted. Determine whether the ontology is
consistent and whether the class is satisfiable.

S07 and S08 define a choice between branches A and B for records
of one declared class. S07 requires exactly one branch. S08 permits
at most one. For each, determine whether an explicitly in-scope
record can satisfy A alone, B alone, both, or neither. In this
question the non-selected branch is explicitly excluded.

Write `reviews.json` as a single JSON object with exactly eight
top-level keys. Each case has its own object and all values within
that object are JSON booleans.

| Top-level key | Fields in its answer object |
| --- | --- |
| `S01` | `whole_equivalent`, `all_premises_equivalent`, `publish` |
| `S02` | `whole_equivalent`, `all_premises_equivalent`, `publish` |
| `S03` | `whole_equivalent`, `all_premises_equivalent`, `publish` |
| `S04` | `whole_equivalent`, `all_premises_equivalent`, `publish` |
| `S05` | `whole_equivalent`, `all_premises_equivalent`, `publish` |
| `S06` | `ontology_consistent`, `class_satisfiable` |
| `S07` | `a_only`, `b_only`, `both`, `neither` |
| `S08` | `a_only`, `b_only`, `both`, `neither` |
