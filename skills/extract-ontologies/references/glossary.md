# Author a source-backed glossary

## Contents

- [Write reviewed glossary entries](#write-reviewed-glossary-entries)
- [Compile proposals before assigning identity](#compile-proposals-before-assigning-identity)
- [Compile and review documents independently](#compile-and-review-documents-independently)

## Write reviewed glossary entries

Use a glossary to explain the terminology in scope. Record the source
versions and the vocabulary or language coverage at the top of
`glossary.md`. Start with the user's term list when supplied. For
discovery, choose terms supported by the material in scope. For each
term, include the preferred term, stable IRI or
scoped identifier, kind, language, definition and its status, supported
aliases, and source locators. Use the authored ontology's IRI for an
emitted term. A stable local glossary identifier can anchor a term that
has no IRI yet.

- Use `source-backed` for a definition stated by the source or faithfully
  paraphrased from it. Preserve qualifiers, exceptions, and the applicable
  version. Cite the operative source and any evidence that establishes
  its scope. Mark direct quotations as quotations.
- Use `working` when the user asks for proposed definitions and the
  available evidence supports a provisional interpretation. Keep the
  evidence and the open question visible.
- Use `missing` with an empty definition when a usable definition is
  unavailable. Cite a term occurrence as evidence of its use and mark
  the locator as an attestation. If a requested term has no occurrence,
  record that gap in Markdown and leave the source locator empty.
- Record aliases only when the evidence supports their use for that
  same term. Preserve alias language and cite the evidence in the
  entry. Keep homonyms and narrower or broader concepts separate.
  Flag conflicting definitions with their distinct source scopes and
  locators in Markdown. Apply a precedence rule only when the source or
  user establishes it. If the conflict leaves the requested scope
  without a usable definition, keep the primary definition empty and
  record the conflict alongside its `missing` status.
- Keep classes, object properties, data properties, individuals, and
  other concepts distinct. Put the declared semantic kind alone in the
  kind field. Put catalog labels such as “index entry” in the evidence
  note or source locator. Use separate rows for language variants where
  needed and identify translations explicitly.

When emitting `glossary.csv`, derive it from the same entries. Use one
row per identifier, kind, and language, sorted by those fields. Use
the following header.

```csv
id,term,kind,language,definition,definition_status,aliases,source_locator
```

Write aliases in the row's language as a JSON array of strings inside
the CSV cell and use an empty array when there are none. Use standard
CSV quoting and UTF-8.
Make the source locator point to an exact versioned passage or to a
resolvable evidence ledger record. In Markdown, retain scope notes and
other review details alongside the same core fields. Glossary wording
is documentation. Use the ontology authoring workflow to review any
corresponding formal axiom.

## Compile proposals before assigning identity

When extracting a glossary from raw UTF-8 text, use the proposal
ledger to validate the source pointers before reviewing the entries.
Read the source and draft candidate definitions, aliases and
attestations. Copy the exact term and value. Keep cases that only
mention a term as attestations when those occurrences are needed.
Review whether each passage defines the term in the requested scope.

The draft has the raw file's `source_sha256` and a `proposals` array.
Each row supplies `kind`, `lane`, `term`, `value`, and `evidence`.
Use kinds `definition`, `alias`, and `attestation`. Use the
`entity`, `predicate`, or `unspecified` lane. These proposal lanes
organize the review. Assign the glossary entry's reviewed semantic
kind separately.

~~~json
{
  "source_sha256": "<lowercase raw-file SHA-256>",
  "proposals": [
    {
      "kind": "definition",
      "lane": "entity",
      "term": {"quote": "X7"},
      "value": {"quote": "the gateway device"},
      "evidence": {"start_line": 1, "end_line": 1}
    }
  ]
}
~~~

For an alias, copy the two lexical forms in the order given by the
source. Review which form is preferred separately. An attestation has
a null value.
The term and value must occupy separate, whole-token spans in the
same cited window. Line bounds are inclusive and one-based. A window
can cover up to eleven lines. If a quote repeats inside that window,
add `first_char` with its zero-based character offset within the
decoded citation. Preserve case, spaces, punctuation and Unicode
code points. The decoded citation uses LF line endings and omits
a UTF-8 byte-order mark.

~~~text
uv run --script SKILL/scripts/compile_glossary_proposals.py --source document.txt --draft proposals.json --output proposal-ledger.json
~~~

Replace SKILL with this skill's directory. The compiler pins the raw
source and draft bytes, reconstructs each citation, and sorts the
candidate entries by source occurrence. Resolved start and end offsets
are zero-based and end-exclusive in the normalized document. The
ledger retains competing passages and keeps entity and predicate
uses separate. Review the candidates and establish identity before
assigning glossary IDs or carrying bindings across source versions.

## Compile and review documents independently

For several raw files, pin the expected documents before drafting
proposals. Create `manifest.json` with a `documents` object. Each key
is an ID beginning with an ASCII letter and containing up to 100 ASCII
letters, digits, underscores, hyphens or dots. Each value has `path`
(relative to the manifest directory) and `sha256` (the lowercase
digest of the exact source bytes).

Write one physical line per document in a UTF-8 records file. Start
each line with the document ID and a literal tab, then write the same
JSON object used for a single draft. Keep newlines inside JSON strings
escaped. A reviewed document with no proposals still needs a record
with its digest and an empty `proposals` array.

~~~text
uv run --script SKILL/scripts/compile_glossary_batch.py --manifest manifest.json --records drafts.txt --output batch-ledger.json
~~~

Exit 0 means every expected document compiled. Exit 1 writes a
`partial` ledger with successful documents and diagnostics. Exit 2
reports a manifest or input/output error. A duplicate ID keeps that
document out of the ledger, even if one of its rows has invalid JSON.
A malformed or missing row, a stale source, or an invalid draft is
reported separately from successfully compiled documents. Review
unrecognized rows as well as missing IDs. Use a fresh output path for
each run.

Treat each compiled document as a collection of source-backed
candidates. In a partial batch, state which documents were unavailable
before describing the glossary's coverage. For conflicting definitions
or aliases, put the term and its scope first, then list each distinct
reading with the source locator and the decision it would change.
Phrase the review question so the reviewer can check the evidence.
Separate what each source says from the choice the reviewer needs to
make. For example, cite the inventory's device and the API guide's
service, then ask whether an authoritative passage ties these two uses
of `gateway` to the same glossary identity. Until that distinction
is resolved, keep their identities separate.
