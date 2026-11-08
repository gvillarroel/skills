# Glossary for an existing ontology

Select terms from the supplied ontology and the mapped source scope.
Identify the ontology version and included files. For an extraction,
default to the terms needed to understand it. For an ontology-only
glossary, cover the supplied vocabulary or the requested subset.
For local Turtle or N-Triples, the `inventory` command described in
[artifacts.md](artifacts.md) provides declared terms and supported
label, alias, and definition annotations with their exact predicates.

For each entry record the canonical IRI or schema ID, preferred term,
kind, language, definition, definition status, supported aliases, and
definition source. Cite the ontology file and annotation predicate, or
give the source file and locator. Keep entries for distinct ontology IDs
even if their labels coincide. Use one row per ID, in-scope kind and
language. For example, an IRI declared as both a SKOS concept and an OWL
named individual has one concept row in a glossary limited to concepts.
Use the requested language tag for translations, mark them as translations,
and cite the original.

Use these definition statuses:

- `source-backed` for a definition supported by a cited ontology
  annotation or a passage that defines the same concept. A label,
  example, domain, range, or mention alone establishes less than a definition.
- `working` for a clearly marked provisional synthesis when the
  task calls for proposing definitions. Cite its basis.
- `missing` when no definition has been established. Leave the
  definition field empty in tabular output.

Use the ontology's supplied definition for the canonical entry. Use an
explicit source definition to fill a gap only after confirming the
mapping to that exact ID and scope. Where source usage differs, cite it
in a separate usage note. If equally authoritative definitions disagree,
record the alternatives and citations for review. Apply a precedence
rule when established by the supplied inputs or the user. Add an alias
only when the evidence supports equivalence for that ID and language.
Place unmapped terms in a separate candidate section. Mark any identifiers
assigned to those terms as local proposals.

Write `glossary.md` with readable entries or a table. If CSV is
requested, use the same entries and the header
`id,term,kind,language,definition,definition_status,aliases,source_locator`.
Write aliases as a JSON array in the CSV field and keep their language
consistent with the entry. Use stable ordering by ID, kind, then
language.
