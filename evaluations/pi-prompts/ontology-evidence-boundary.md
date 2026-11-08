# Review three candidate evidence rows

Use the ontology-authoring skill's evidence-ledger workflow to
check whether each candidate assertion is supported by the supplied
versioned source spans. The `span_id` selects one sufficient span.
Use JSON null when no supplied span is sufficient. Admitting a
candidate requires evidence for its exact owner, property, and
qualifier or for every named enum variant and its value.

## Claims to check

| Claim key | Proposed assertion |
| --- | --- |
| `count` | Individual `dock17` has at least two `hasSensor` values in class `Calibrated`. |
| `variants` | `State` has named variants `Ready`, `Paused`, and `Done` with discriminants 0, 4, and 5 respectively. |
| `guard` | Every `Batch`, including uncertified batches, must have at least two inspectors. |

## Source spans

`a1` from an OWL syntax document:

```text
ObjectMinCardinality( 2 :hasSensor :Calibrated )
```

`a2` from the same revision:

```text
ClassAssertion(
    ObjectMinCardinality( 2 :hasSensor :Calibrated )
    :dock17
)
```

`b1` from a Rust example:

```rust
enum State { Ready, // 0 Paused = 4, // 4 Done, // 5 }
```

`b2` from the same revision:

```rust
enum State {
    Ready, // 0
    Paused = 4, // 4
    Done, // 5
}
```

`c1` from a quality manual:

> A certified Batch must have at least two inspectors.

Write exactly one file named `evidence.json` with the three top-level
keys `count`, `variants`, and `guard`. Each key's value is an object
with exactly `decision` and `span_id`. Use decision `admit` or `hold`.
For admitted claims provide the single source span's ID. For held
claims use null for `span_id`.
