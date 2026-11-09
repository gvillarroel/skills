# Select exact keyword witnesses

When the supplied vocabulary depends on exact keywords, such as explicit
normative modals, use the [keyword index](../scripts/index_source_keywords.py)
on governed text units. Select a witness by ID. Keep a compound phrase
such as MUST NOT together across line breaks. Verify that the selected
phrase governs the intended subject, action and conditions. Consult the
whole unit when the local context leaves that unclear. An index match
only locates a phrase. The source role determines whether it supports an
assertion, a quotation, an example, or a proposal.

Run `uv run --script SKILL/scripts/index_source_keywords.py --source source.txt --plan plan.json --output witnesses.json`.
Replace SKILL with this skill's path. The plan contains the exact
`source_sha256`, an array of `keywords` such as `["MUST NOT", "MUST", "MAY"]`,
and disjoint `units` with `id`, `start`, and `end`. Use zero-based Unicode
character offsets with an exclusive end into the decoded UTF-8 bytes.
Choose units within the same snapshot and exclude non-source material
before indexing. A witness ID is local to its index. Resolve it against
the matching source digest before writing the evidence ledger.
