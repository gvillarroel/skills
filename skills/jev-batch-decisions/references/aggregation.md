# Aggregation recipes

Choose the statistic before splitting. A correct mapper plus a mismatched
reducer can still produce an incorrect answer.

## Record routing and counts

Use complete CSV/JSONL records, a `choice` rubric, and `histogram`. Count each
record once. The result reports accepted categories and review units separately.
It does not assign unknowns to the most common category. In long prose,
histograms count fragments; they must not be described as document counts.

Validate with balanced labeled records, negation, mixed language, ambiguous
requests, and conflicting adjacent items. Compare a single-item control with
the same inputs in batches to detect cross-item contamination. The expanded
question's instructions must name its item's array position and ID; native
question keys alone do not enter Jev inference.

## Find any evidence across long documents

Use an evidence-specific `noul` rubric and `any`, with shared definitions in
`context`. A definite positive dominates; otherwise an unknown keeps the
result unknown. An `all` reducer is the dual: a definite negative dominates;
otherwise unknowns prevent a definite positive. Empty sets do not produce
vacuously true answers. These are three-valued logical reductions, not
probabilistic independence assumptions or calibrated corpus probabilities.

Use per-source aggregates to answer one question per document, then inspect
the matching map spans. Do not average chunk probabilities to answer whether
a single decisive exception exists. If a condition and its exception are
split apart, preserve the complete section as one JSONL record, repeat a
verified shared rule in `context`, or inspect adjacent spans before concluding.
The script never invents missing context or repairs document meaning.

## Rubric maximum and mean

Use `score` and `max` for the worst observed impact, or `mean` for the mean
score of comparable, equally weighted records. Means accumulate all original
leaf values once; do not average means of unequal batches. Unknown leaves
make the complete numerical result null; accepted-only sums and maximum remain
visible for diagnosis. This strict behavior avoids silent denominator changes.

Jev's score is a rubric expectation. Extract and compute actual monetary sums,
dates, or exact numeric totals using a parser; do not ask Jev to replace exact
arithmetic. Text chunk lengths are not valid statistical weights by default.

## Recursive semantic decisions

For a collection-wide decision that depends on relationships among typed
evidence, add a reduce contract. Every level uses the same reduce questions,
so its instructions must accept both map decisions and previous reduce
decisions. Give the reduce output explicit sufficient states (including
unknown) that can be combined without losing a decisive condition.

Example: map a document fragment into one of `blocked`, `clear`, `unknown`.
Use the same choice at reduce levels, with this invariant in `reduce.context`:

> Any blocked child makes the collection blocked. Without a blocked child,
> any unknown/null child makes it unknown. Otherwise it is clear. This rule
> applies identically to fragment decisions and previous collection decisions.

```json
{
  "context": "Apply the stated blocked/unknown/clear rule to every child. Preserve any blocker at every level.",
  "fan_in": 4,
  "max_levels": 12,
  "questions": {
    "release": {
      "type": "choice",
      "instructions": "Combine the children's release decisions using the aggregation rule.",
      "criteria": {
        "blocked": "At least one child says blocked.",
        "unknown": "No blocked child, but some child is unknown or null.",
        "clear": "All children explicitly say clear."
      }
    }
  }
}
```

Place that object under the job's `reduce` key. This example deliberately uses
a verifiable rule to test semantic tree mechanics. Prefer deterministic logic
for production when the rule is this simple. Semantic reduction is useful
when a typed rubric needs judgment, but must be evaluated on rearrangements,
unequal group sizes and contradictory evidence before trusting a deep tree.

The tree packs children by both fan-in and serialized request size, retains
child IDs and leaf counts, refuses nonshrinking or overdeep trees, and carries
review flags upward. `leaf_count` measures covered original units; it is not a
vote. A final review flag is still required even if a later model is confident.
Follow root children through `reduce-nodes.jsonl` to source spans. Use the
hosting agent to compose explanatory prose from those inspected sources.
