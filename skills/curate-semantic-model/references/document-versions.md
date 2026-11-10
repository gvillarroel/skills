# Compare reviewed versions of a document

## Contents

- [Compile reviewed observations](#compile-reviewed-observations)
- [Compare reviewed typed inventories](#compare-reviewed-typed-inventories)
- [Compare reviewed Boolean rules](#compare-reviewed-boolean-rules)
- [Check a reviewed Boolean consequence](#check-a-reviewed-boolean-consequence)
- [Bind reviewed atoms by token number or exact quote](#bind-reviewed-atoms-by-token-number)

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

## Compare reviewed Boolean rules

Use `--boolean-pair` after a reviewer has fixed the atom identities
and translated each source rule into the bounded Boolean syntax. The
comparator evaluates those formulas and reports counterexample assignments.

The pair contains lowercase raw-byte SHA-256 digests in `source_sha256`,
one to ten stable IDs with reviewed meanings in `atoms`, and `base`
and `head` rule arrays.
Each array contains one to twenty rows with a `rule` and exact `evidence`
citation. A rule is `[mode, outcome, guard]`. Expressions
are atom IDs or prefix arrays such as `["and", "A", ["not", "B"]]`
and `["or", "A", "B"]`. `and`, `or`, and `exactly-one` take two to
ten arguments. `not` takes one. An expression may be nested at most
twelve times.

Use inclusive `or` when one or more branches may hold. Use
`["exactly-one", "A", "B", "C"]` when exactly one branch must hold.
Each child is a separate branch occurrence. Review repetitions against
the source because repeated branches contribute separately. Keep nested
choices grouped at their stated scope.

To review a two-branch choice, check A alone, B alone, both, and
neither while holding the surrounding conditions fixed. With more than
two branches, check each branch alone and include assignments with two
or more active branches. Three simultaneously true branches fail an
`exactly-one` choice. If the source leaves overlap unresolved, record
the competing readings for review.

- `if` requires the outcome when the guard is true.
- `only-if` requires the guard when the outcome is true.
- `iff` requires both directions.
- `unless` requires the outcome when the guard is false. A true guard leaves the outcome open.
- `plain` asserts the outcome alone and requires a null guard.

Rules on each side are conjoined. Every row's citation must exactly match up to
eleven in-bounds source lines, and each supplied digest must match the
current source bytes.

~~~json
{
  "source_sha256": {"base": "<64 lowercase hex>", "head": "<64 lowercase hex>"},
  "atoms": {"A": "reviewed meaning of A", "B": "reviewed meaning of B"},
  "base": [{"rule": ["if", "A", "B"], "evidence": {"start_line": 2, "end_line": 2, "quote": "Exact base line."}}],
  "head": [{"rule": ["iff", "A", "B"], "evidence": {"start_line": 3, "end_line": 3, "quote": "Exact head line."}}]
}
~~~

~~~text
uv run --script SKILL/scripts/compare_document_versions.py --base old.txt --head new.txt --boolean-pair reviewed-rules.json --output rule-comparison.json
~~~

The output classifies the pair as `same`, `base-implies-head`,
`head-implies-base`, `different`, or `hold`. It reports one
assignment for each nonempty region of the truth table. The two directional
counterexamples show when only one side's rules hold. The `both` and
`neither` witnesses show when the two sides succeed or fail together.
An inconsistent or tautological side yields `hold`.

The result carries the reviewed atom meanings, rules, citations, and
source digests. Each side's fingerprint uses the sorted IDs of the atoms
that can change its truth value and the corresponding truth table.
Equivalent syntax and irrelevant atoms yield the same fingerprint when
the reviewed atom IDs and their meanings are stable. Review the
translation and atom identities separately from the Boolean result.

## Check a reviewed Boolean consequence

Use the same reviewed Boolean pair format. The `base` rows are the
premises and the `head` rows form the candidate. Each side's rows are
conjoined. Pin both source files and review the common atom meanings
before running the check. A candidate can be a proposed relationship
written in its own source file. Its citation identifies the proposal.

~~~text
uv run --script SKILL/scripts/compare_document_versions.py --base premises.txt --head candidate.txt --boolean-consequence reviewed-rules.json --output consequence.json
~~~

| Classification | Result under the reviewed premises |
| --- | --- |
| `entailed` | Every assignment satisfying the premises also satisfies the candidate. |
| `refuted` | Every assignment satisfying the premises falsifies the candidate. |
| `independent` | There is an assignment supporting the candidate and another falsifying it. |
| `inconsistent-premises` | No assignment satisfies the premises. The status is `hold`. |

Inspect `counterexamples.base_not_head` for an assignment that
satisfies the premises and falsifies the candidate.
`region_witnesses.both` gives a satisfying example when one exists.
For an independent candidate, inspect both assignments to identify
which additional assumption would require review. Read the
`premise_profile` and `candidate_profile` to distinguish a
tautology, a contradiction and a contingent formula. For example,
consistent premises entail a tautological candidate, which needs no
domain-specific assumption. Inconsistent premises take precedence over
the candidate's profile.

The result retains the pinned citations, reviewed atom IDs and truth
fingerprints. The calculation is exhaustive over the reviewed atom
inventory. Review the source-to-formula translation and the cross-source
identity of atoms before using the classification.

## Bind reviewed atoms by token number

Run the indexer on the cited excerpt from each source. Its output includes
the raw source digest, the exact decoded quote, and numbered tokens.

~~~text
uv run --script SKILL/scripts/index_rule_evidence.py --source new.txt --start-line 1 --end-line 1 --output head-index.json
~~~

An indexed row supplies `atom_refs` for every atom in its rule. Each atom
uses one to three increasing, non-overlapping ranges of up to eight tokens.
The endpoints are inclusive and token numbering starts at one within the
selected line span. A shared predicate and a separated conjunct can be
represented by two ranges.

~~~json
{
  "rule": ["iff", "P", ["or", "A", "B"]],
  "evidence": {"start_line": 1, "end_line": 1},
  "atom_refs": {"P": [[2, 3]], "A": [[7, 8], [12, 13]], "B": [[7, 10]]}
}
~~~

A fragment can also be an exact quote selector such as
`{"quote": "security key"}`. The quote must start and end at indexed
token boundaries inside that rule's selected line span. Case,
whitespace, punctuation and Unicode code points must match the decoded
citation. Its line breaks are LF. When the quote occurs more than once,
add `first_token` with the one-based start of the reviewed occurrence,
for example `{"quote": "security key", "first_token": 8}`. The
selector must match at a supplied start. A missing match or an
unresolved repeat produces a validation error.

You can combine quote selectors and numeric ranges in one atom's
fragment list. They share the same count, length, ordering and overlap
rules. The result records the original selectors and resolved evidence.
When the two forms cover the same tokens in the same source and line
span, they produce the same evidence fingerprint.

Use the indexer's source digest in `source_sha256` for the corresponding
side. The comparator restores the citation and records each fragment
in `atom_evidence`. The character and UTF-8 byte offsets are zero-based
and end-exclusive within the decoded citation quote. The raw file digest
also covers any byte-order mark and original line endings.

Review each atom's identity, the scope of negation, and the complete rule
against the citation. A token range can identify an exact fragment while
leaving the surrounding predicate or connective for the reviewer.

For an indexed rule, `atom_evidence_sha256` binds the source digest,
cited line bounds, reviewed atom IDs, and the exact token positions
covered by each atom. Splitting a range into adjacent valid pieces preserves
this fingerprint and the output keeps the submitted fragments.
Different coverage changes the fingerprint. Distinct atoms may share
tokens when their complete coverage differs. Compare this fingerprint
only within the same source version and reviewed atom vocabulary.
