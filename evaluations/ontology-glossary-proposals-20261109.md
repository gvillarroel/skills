# Source-pinned glossary proposal ledger

The glossary compiler verifies exact term and value spans within a
reviewed source citation. It emits definitions, aliases and
attestations as candidates. The ledger separates entity and
predicate proposals and retains competing definitions from
different occurrences. Identity and glossary status are reviewed
after evidence compilation.

| Check | Result |
| --- | --- |
| Compiler unit and CLI tests | 5/5 on Python 3.11 and 3.14 |
| Independent source audit | 40 valid drafts, 60 anchored proposals and 20 additional CLI controls |
| Strict isolated GPT-6 Luna low | Two runs reproduced the same ledger byte for byte |

The strict runtime case retains two definitions of the same local
term, an explicit alias and an attestation without a definition.
An explicit character offset identifies the requested occurrence
inside a repeated attestation. Both source and draft SHA-256
digests are recorded. The resulting ledger SHA-256 is
`2b5df6c360dafc9457467ae544fe27ddd8bcd6b30210411afaf55c1a6731cb1b`.

The independent controls cover stale bytes beyond the cited
window, exact Unicode and line normalization, duplicate absolute
occurrences, distinct repeated occurrences, and preservation of
an existing output. An exact quotation can still play the wrong
semantic role. The ledger provides the evidence needed to review
that distinction.

[Glossary proposal workflow](../skills/extract-ontologies/references/glossary.md#compile-proposals-before-assigning-identity)
