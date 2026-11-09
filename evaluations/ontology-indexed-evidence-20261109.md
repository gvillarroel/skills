# Indexed evidence for reviewed Boolean rules

The document comparison workflow accepts token ranges for reviewed atoms.
The indexer emits numbered tokens from an exact line span. A rule can
reference a shared predicate and an elided conjunct in separate ranges.
The comparator reconstructs the quote and each range from digest-bound
source bytes. It records character and UTF-8 offsets relative to the
decoded quote.

The indexed form is optional. The published comparator reproduced the
previous result bytes for the original choice and vacuity inputs using
their legacy exact-quote drafts. The indexer verifies the selected line
range, and the comparator verifies the source digest and every atom
reference. Review the meaning and scope of the formula separately.

## Qualification

The full skill suite passed 209 tests. The new tests cover Unicode,
discontiguous anchors, bounds, punctuation, repeated anchors, stale
source digests and output safety. Three strict isolated GPT-6 Luna low
runs invoked the indexer on both revisions and ran the bundled comparison.
The two runs on the same choice produced byte-identical results, including
the resolved fragments. The Unicode case preserved different character
and UTF-8 offsets. A retained earlier Unicode attempt wrote CRLF instead
of the approved LF bytes and the digest check rejected that input.

## Translation experiment

On four authored SHACL and JSON Schema comparisons, indexed extraction
with an open atom vocabulary produced four correct relations in each of
four runs. Repeating the same translation prompt preserved all four
formulas and one full evidence record. Exact ranges and stable logical
labels are separate measurements. The published helper operates on
reviewed pointers. Automatic translation remains a development workflow.

[Indexed evidence instructions](../skills/curate-semantic-model/references/document-versions.md#bind-reviewed-atoms-by-token-number)
