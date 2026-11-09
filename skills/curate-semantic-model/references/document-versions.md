# Compare reviewed versions of a document

Pin both source files and record their byte digests and revision identifiers.
Use complete UTF-8 files or explicitly scoped excerpts. Keep reviewed values,
assertions and source evidence tied to the same scope and vocabulary.

## Compile reviewed observations

Give each observation a stable ID. Its before and after states contain a
typed JSON value and inclusive one-based line ranges in the corresponding
source. Use null for absence when the review vocabulary defines it that way.
A present value needs at least one source range. Ranges cannot overlap.

~~~json
{
  "observations": [
    {
      "id": "renewal-period",
      "before": {"value": {"days": 30}, "lines": [[3, 3]]},
      "after": {"value": {"days": 45}, "lines": [[5, 5]]}
    }
  ]
}
~~~

~~~text
uv run --script SKILL/scripts/compare_document_versions.py --base old.txt --head new.txt --draft observations.json --output delta.json
~~~

Replace SKILL with this skill's directory. The result copies exact
line text and computes added, removed, modified or unchanged from the
reviewed values. It keeps JSON types distinct and arrays ordered.
It treats object key order as immaterial and rejects decimal precision
loss before comparing values. Line evidence uses decoded
UTF-8 text with normalized line endings and no byte-order mark.

## Compare reviewed typed inventories

~~~text
uv run --script SKILL/scripts/compare_document_versions.py --base old.txt --head new.txt --snapshot-pair pair.json --output delta.json
~~~

Pass a JSON object with base and head inventories. Each has four arrays.

| Collection | Fields besides evidence |
| --- | --- |
| classes | id, label |
| subclasses | child, parent |
| relations | subject, predicate, object |
| constraints | subject, predicate, object, kind, value |

Endpoints use revision-local class IDs. Every evidence object contains
start_line, end_line and quote. The two coordinates are inclusive
and one-based. The quote must match the selected source lines.
Constraint kinds required and forbidden take true. The kinds
min-cardinality, max-cardinality and exact-cardinality take a
nonnegative integer.

The comparator matches labels and predicate names after NFC and
whitespace normalization, preserving case. It reports operations by
collection and zero-based input row index. A unique replacement in
one directed constraint slot and kind family is modified. Evidence
movement and changes to local IDs do not change matched assertions.

When two reviewed classes have different labels, optionally use
--class-identity identities.json with --snapshot-pair. This file holds
pairs of local class IDs in objects with base and head keys, a
source_sha256 object with the base and head raw-byte digests, and a
snapshot_pair_sha256 digest over pair.json. Use lowercase SHA-256.
Each ID can occur once per side. Existing literal matches take
precedence. The bridge must be approved against the exact versions
before use.

For an unresolved comparison, the caller can give pair.json a review
object with a reason and base and head arrays of exact evidence objects.
The output records abstain and leaves the operation lists empty.

An exact source citation establishes where the text occurs. Verify
separately that the passage and any governing context support the
whole proposition, including its conditions, polarity, role and
alternatives. Compare deterministic results using the same reviewed
inputs, source bytes and helper version. Write each result to a new
path outside the input files.
