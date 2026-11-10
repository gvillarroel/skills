---
name: extract-with-ontology
description: "Apply a supplied ontology, controlled vocabulary, or semantic schema to documents or datasets. Extract instances, relations, and attributes with evidence, review mapping gaps, or build a glossary from the existing vocabulary."
---

# Extract with an existing ontology

Populate the supplied semantic model with information from the offered files.
Treat the model as the authority for vocabulary and the files as evidence
for instance claims. Keep proposed vocabulary changes in the review output.

For a glossary-only request, read [glossary.md](references/glossary.md)
and use the supplied vocabulary and any requested source scope directly.
An ontology alone is enough for its vocabulary glossary.

1. Identify the intended ontology version, input files, scope, desired
   fields, and output format. Record ontology and file identities. Use
   only supplied or explicitly authorized input versions and local imports.
   If the ontology or files are unavailable, report which input is needed.
2. Read the relevant class and property definitions, directions, datatypes,
   disjointness, constraints, and identity rules. Decide which assertions
   the task needs. For a local Turtle or N-Triples ontology, the bundled
   vocabulary inspector can produce a deterministic term inventory.
3. Extract candidates with versioned source locators. Use stable IDs for
   exact source units and retain the governing context for negation, dates,
   qualifiers, table headers, and references across passages. Apply the
   mapping and identity rules in [mapping.md](references/mapping.md).
   If the vocabulary depends on explicit source keywords, use
   [keyword witnesses](references/keyword-witnesses.md) to bind exact matches.
4. Emit supported instance assertions under the supplied vocabulary.
   Keep candidates with unresolved mappings, conflicts, missing evidence,
   and unreadable inputs visible for review. Preserve unresolved
   alternatives as a group unless the supplied model can express them
   faithfully. Distinguish asserted facts, derived entailments, and
   validation findings.
5. Verify the output vocabulary, evidence coverage, and requested
   constraints. For pinned UTF-8 text, use the [evidence binder](references/artifacts.md#bind-exact-text-from-selected-lines)
   to turn selected line ranges into exact citations. Run the bundled
   checker for the supported RDF and evidence formats. Compare
   repeated outputs by canonical graph identity and evidence separately.

For RDF tasks, default to `data.ttl`, `evidence.json`, and `review.md`
when the user has not chosen a format. Use the requested structured
format for other semantic schemas. For a combined extraction and
glossary, follow [glossary.md](references/glossary.md) and keep the glossary
separate from the asserted facts.
