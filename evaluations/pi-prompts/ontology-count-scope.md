# Validate qualifying and total counts independently

Create `shapes.ttl` and `review.md` from this consumer contract. Use
`urn:count-scope:` as the namespace. Use SHACL Core and validate the
submitted graph without optional inference. The targets include
subclasses represented in that graph. No other record classes are in
scope.

Each rule counts values on the `member` path. A value qualifies when it
belongs to `EligibleA` or `EligibleB`. The two classes may overlap.

| Record class | Requirement |
| --- | --- |
| `Minimum` | At least one qualifying member. Other members are allowed. |
| `OneMatch` | Exactly one qualifying member. Other members are allowed. |
| `OneTotal` | Exactly one member in total. It must qualify. |

Use the stated rule for each class even if the same values give a
different result for another class. In the review, explain the expected
outcome for one qualifying and one nonqualifying member, one member in
both eligible classes, and a subclass record with no member. The
independent evaluator will execute the conformance checks on your
shapes. For an optional local syntax check, use
`uv run --with rdflib==7.6.0 python`.
