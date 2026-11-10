# Reviewed exactly-one Boolean choices

The document comparison mode accepts `["exactly-one", "A", "B", "C"]`
for a policy in which exactly one branch occurrence must evaluate to
true. It accepts two to ten branches. Nested choices retain their own
scope, and repeated branches each contribute to the count.

| Active branches | Inclusive `or` | `exactly-one` | Odd parity |
| ---: | --- | --- | --- |
| 0 | false | false | false |
| 1 | true | true | true |
| 2 | true | false | false |
| 3 | true | false | true |

The difference is visible in a version comparison. If the earlier
version requires exactly one authentication method and the later
version permits one or more, an assignment with two accepted methods
satisfies the later rule alone.

## Validation

- The full 214-test suite passed on Python 3.11 and 3.14.
- An independent audit verified 31 source-bound comparisons and 1,052
  assignments across widths 2, 3, 4 and 10. The operator matched a
  complete expansion using the existing operators, including truth
  fingerprints, evidence fingerprints, and counterexamples.
- The audit rejected eight malformed, out-of-bounds, or unsupported
  operator inputs. It checked repeated and nested branches, vacuity,
  directional conditions and reordered vocabulary.
- Two isolated strict GPT-6 Luna low runs reproduced the same
  three-branch comparison artifact. Four assignments met only the
  inclusive rule, three met both rules, and one met neither. The
  artifact SHA-256 was
  `94b8d36bf3b465b8db8620f26b6a60b3f3db8b6e2fdf6f2f93aff0884297c9f0`.
- The initial runtime prompt yielded the same artifact in both runs.
  One failed strict workflow acceptance after combining input setup
  and the required comparison command in one shell call. The final
  prompt required a dedicated comparison call and passed twice.

The checks qualify the reviewed comparator. Independent extraction of
the operator and source evidence is evaluated separately.

[Reviewed Boolean comparison reference](../skills/curate-semantic-model/references/document-versions.md#compare-reviewed-boolean-rules)
