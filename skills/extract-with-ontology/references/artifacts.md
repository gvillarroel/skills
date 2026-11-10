# Artifacts and mechanical checks

## Contents

- [RDF and evidence](#rdf-and-evidence)
- [Bind exact text from selected lines](#bind-exact-text-from-selected-lines)
- [Review output](#review-output)

Keep a separate instance graph, evidence ledger, and review queue.
Keep the original ontology available by version and digest. Record
the effective local import closure and the ontology format used.

## RDF and evidence

The bundled helper accepts local Turtle (`.ttl`) and N-Triples (`.nt`).
It recognizes explicitly declared named OWL or RDFS classes, OWL object,
datatype and annotation properties, and generic RDF properties. The
inventory also includes explicitly declared OWL named individuals and
SKOS concepts. The helper lists unresolved import IRIs and reads only
the file you pass. For other
formats or vocabularies, use a suitable local processor or check the
mapping against the supplied schema directly. Identify which checks ran.

```text
uv run --script SKILL/scripts/check_extraction.py inventory --ontology schema.ttl --output vocabulary.json
uv run --script SKILL/scripts/check_extraction.py check --ontology schema.ttl --data data.ttl --evidence evidence.json --source-root . --output checks.json
```

Replace `SKILL` with this skill's directory. The `check` command uses
the selected effective ontology file, named RDF subjects and objects,
and UTF-8 text source snapshots. Use the original text or CSV when
available. For PDFs, DOCX or spreadsheets, keep a versioned text
snapshot with its original page, section, row, or cell locators.
Keep original-file and snapshot provenance together. The helper
checks the cited snapshot. Review the snapshot against the original
when OCR, rendering or normalization affects evidence.

Use this evidence JSON structure with the SHA-256 values of the exact
ontology and source snapshot bytes. Use workspace-relative source
paths and absolute IRIs or an explicit absolute RDF base. A relative
IRI with an implicit file base can change meaning if the file moves.

```json
{
  "ontology_sha256": "<ontology SHA-256>",
  "sources": [
    {"id": "register", "path": "sources/register.txt", "sha256": "<source SHA-256>"}
  ],
  "assertions": [
    {
      "subject": "urn:records:permit-17",
      "predicate": "urn:example:issuedBy",
      "object": {"iri": "urn:records:office-5"},
      "source_id": "register",
      "locator": "row 12",
      "quote": "Office 5 issued permit 17."
    }
  ]
}
```

For a literal, use `{"value":"012","datatype":"http://www.w3.org/2001/XMLSchema#string"}`,
`{"value":"solicitud","language":"es"}`, or `{"value":"text"}`.
Use the exact lexical value and the same datatype or language as the
asserted RDF term. For matching and fingerprinting, the checker treats
bare strings as equivalent to explicit `xsd:string` and lowercases
language tags. It preserves the lexical form of the literal. Repeat an
assertion row for each independent source fragment. The helper checks
a free-form locator for presence. Supply
optional `start` and `end` to bind the quote to a specific occurrence.
These are zero-based Unicode character offsets into the decoded snapshot
with an exclusive end.

The check binds evidence to actual asserted triples, detects missing
or extra evidence rows, and checks literal quotes against pinned source
bytes. It checks the local declared vocabulary and basic object versus
literal kind. It emits an order-independent asserted-graph fingerprint
for named-node data. Exit 0 means these mechanical checks passed. Exit 1
means the report contains violations. Exit 2 means an input or I/O error
prevented checking. Inspect the JSON status and findings.

Review whether each quote and its surrounding context actually warrant
the assertion. Check identity, ontology meaning, completeness, and
SHACL or OWL reasoning separately. A literal quote, declared predicate,
or matching fingerprint establishes only the corresponding mechanical
property.

## Bind exact text from selected lines

For UTF-8 source files with line locators, draft the asserted graph and
a selection JSON file. Use the evidence format's `sources` array and
an `assertions` array. For each assertion supply `subject`,
`predicate`, `object`, `source_id`, `start_line`, and `end_line`.
Use inclusive one-based LF line numbers and the smallest passage that
supports the assertion. Cite multiple passages separately when needed.

```text
uv run --script SKILL/scripts/check_extraction.py bind --ontology schema.ttl --data data.ttl --selection selections.json --source-root . --output evidence.json
```

Use `python3 SKILL/scripts/check_extraction.py bind` with the same
arguments when the declared RDFLib dependency is already installed.

The binder checks the pinned sources and builds exact quotes, offsets
and locators from the selected lines. It writes the evidence ledger
after checking the asserted graph and every citation. Preserve the
selection file with the review when reproducing the extraction.

## Review output

In `review.md`, include the source roster and scope, counts of accepted
and held assertions, unmapped terms or relationships, identity
ambiguities, conflicting claims, and missing or unreadable evidence.
Include source locators and enough surrounding context for a reviewer to
decide each item. Report both the checks performed and their scope.
For an unresolved alternative, group its candidate assertions and
source locators. State what the evidence establishes and ask for the
specific information that would change the disposition.

- For an uncertain fact, ask which action, value, or identity the
  source actually records for the named subject and scope. Preserve
  any assertion that all supported readings share.
- For an established fact without a supported mapping, retain the
  fact in review and ask which term or authorized expression in the
  supplied model represents it.
- For an open policy, describe a record for which the readings
  produce different outcomes and ask which outcome applies.

For a settled policy question, give the governing rule and its scope.
Raise a representation gap separately when the requested output
depends on an expression the supplied model lacks.

A pending value leaves other supported claims about the record
eligible for extraction, including its established type. Give each
retained assertion its own evidence row when using the checker.

A contextual passage that contributes no instance claim needs no
decision.

For a validation item, identify the pinned inputs, check method,
and expected outcome for the named record or witness. Record the
observed result when the check ran. For SHACL, distinguish focus
selection from conformance and include the shape, constraint
component, and affected path or value when present. If a check is
blocked, identify the missing input or unsupported construct and the
specific observation it prevents. When confirmed values violate a
constraint, keep the values and ask for the authorized resolution
of the violation. Keep any later correction tied to new evidence.
