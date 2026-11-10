# Exact quote selectors for reviewed Boolean evidence

An indexed rule can bind an atom with an exact literal, an inclusive
numeric range, or a list that combines both. An exact literal resolves
within the reviewed citation at complete token boundaries. A repeated
literal requires its reviewed one-based start token. The supplied start
must match the literal. The source digest and citation line bounds
remain the basis of the evidence check.

The strict runtime case includes `client.csv` twice in the earlier
source. The quote selector points to the second occurrence, in the
operative rule. The numeric form selects the same tokens. Both forms
produce the same truth fingerprints, evidence fingerprints,
counterexamples and resolved source fragments.

| Check | Result |
| --- | --- |
| Full skill tests | 223/223 passed on Python 3.11 and 3.14 |
| Independent frozen audit | 52 locator cases and 11 rule cases passed across 71 invocations |
| Numeric evidence compatibility | 18 independent reports matched the prior version byte for byte |
| Earlier runtime artifacts | Five reproduced byte for byte |
| Strict isolated GPT-6 Luna low | Two runs reproduced both selector artifacts byte for byte |

| Reviewed artifact | SHA-256 |
| --- | --- |
| Exact-quote comparison | `665e06607a547ea0d2123d9107024d58b02a0197dcd1b26f2a5ab53b39f1722d` |
| Numeric-range comparison | `33ebb99c03b49229d9d70e0eefa9651c26cfc9f34a1178e7db9ff3866a11b12b` |
| Earlier source evidence coverage | `466ba0df66b1e1764709baa2f967ac9d17f19373b3304d1faabe7db1d2f6e825` |
| Later source evidence coverage | `29980e8460639cf336d5e027a05c95029139bc79ed341a46376840a53635ec24` |

The audit includes Unicode, decoded LF across source lines, original
byte-order marks and CRLF digests, punctuation, overlapping occurrences,
invalid starts, mixed selector ordering, and atom coverage collisions.
Source roles and atom identity require review. The same literal can
occur in an example and in an operative rule.

[Evidence binding reference](../skills/curate-semantic-model/references/document-versions.md#bind-reviewed-atoms-by-token-number)
