# Author a source-backed glossary

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
