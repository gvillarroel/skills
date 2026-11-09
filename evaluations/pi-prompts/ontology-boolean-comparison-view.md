# Prepare three source-owned Boolean comparison ledgers

Use the ontology-authoring skill and its bundled Boolean comparison
workflow. Preserve the three source ledgers and write the comparison
views as separate files. The comparison step is a proposal. The
evaluation will separately check whole and premise-local semantics.

Write `left-source.json` with these exact axiom strings and source rows.

```json
{"premises":[{"id":"p01","gap":null,"axioms":["SubClassOf(:Flagged :Candidate)","SubClassOf(:Flagged :Eligible)","SubClassOf(ObjectIntersectionOf(:Candidate :Eligible) :Flagged)"]},{"id":"p02","gap":null,"axioms":["SubClassOf(:Eligible :Audited)","ClassAssertion(:Audited :item)"]}]}
```

Write `right-source.json` with these exact axiom strings and source rows.

```json
{"premises":[{"id":"p01","gap":null,"axioms":["EquivalentClasses(:Flagged ObjectIntersectionOf(:Candidate :Eligible))","SubClassOf(:Flagged :Candidate)"]},{"id":"p02","gap":null,"axioms":["SubClassOf(:Eligible :Audited)","ClassAssertion(:Audited :item)"]}]}
```

Write `shifted-source.json` with these exact axiom strings and source
rows.

```json
{"premises":[{"id":"p01","gap":null,"axioms":["EquivalentClasses(:Flagged ObjectIntersectionOf(:Candidate :Eligible))","SubClassOf(:Flagged :Candidate)","SubClassOf(:Eligible :Audited)"]},{"id":"p02","gap":null,"axioms":["ClassAssertion(:Audited :item)"]}]}
```

Run the bundled comparison utility on each supplied ledger. Write
`left-view.json`, `right-view.json`, and `shifted-view.json` in the
workspace. Keep the source rows and any unsupported axioms. The three
view files and three original source ledgers are the deliverables.
