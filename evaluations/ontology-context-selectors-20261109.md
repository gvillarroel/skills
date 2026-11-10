# Context selectors for repeated Boolean evidence

A reviewed exact quote can specify literal text immediately before or
after it. Prefix, suffix and a one-based token start can be combined.
Every supplied selector must match the same occurrence within the
pinned rule citation. The resolved fragment and evidence fingerprint
continue to cover the quote's tokens.

The runtime case repeats the same key in an example after cutover, a
production rule before cutover, and a production rule after cutover.
The production prefix alone matches two occurrences. The after-cutover
suffix also matches two. Together they locate the reviewed rule.

| Check | Result |
| --- | --- |
| Complete skill tests | 227/227 passed on Python 3.11 and 3.14 |
| Independent frozen audit | 50 locator cases and 10 rule cases passed |
| Compatibility with previous exact-quote and numeric selectors | 12 reports reproduced byte for byte |
| Strict isolated GPT-6 Luna low runtime | Two runs reproduced both comparison artifacts |

The contextual and numeric inputs selected identical token spans,
evidence fingerprints, formula fingerprints and consequence results.
The earlier citation's key is at tokens 20–22.

| Reviewed artifact | SHA-256 |
| --- | --- |
| Contextual comparison | `4d2417f021fb7222631c7ff0fc85ff3c781a47dab890aa84609dfbf36a779cf1` |
| Numeric comparison | `9e2629d69e4a07d7eca12989c053c2da04b3877c549e8909fbf87780e690a396` |
| Earlier source evidence coverage | `0e5c87919968e1180d9f76fe94c8c60579ce5023474bf810945c32d489013ab1` |
| Later source evidence coverage | `25a5325458a7335131bbb5a09c86640ce5ebd071599c5b33cf78ef673e1dc8ae` |

Audit controls include disagreement with an explicit start, ambiguity
after filtering, exact spaces, partial-token neighbor text, Unicode,
decoded LF and original BOM/CRLF bytes. A separate review verifies that
the quoted occurrence supports the atom and its role in the rule.

[Evidence binding reference](../skills/curate-semantic-model/references/document-versions.md#bind-reviewed-atoms-by-token-number)
