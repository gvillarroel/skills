# Local ontology validator contract

Use the copied skill to produce a tiny local RDF/OWL/SHACL bundle for a catalog item. Work only inside this workspace; keep the copied skill read-only. Read only `SKILL.md` and necessary compact runtime references or scripts. Do not inspect hidden files, repository or sibling content, acceptance examples, credentials, or external ontologies. Dependency installation through the declared pinned `uv` script metadata is permitted; do not browse or dereference ontology IRIs.

Supplied evidence: `source:1`, locator `provided:catalog:1`, text `Every catalog item must have exactly one textual identifier. The item named alpha has identifier A-1.`

Use namespace `urn:catalog:`. Write exactly `ontology.ttl`, `data.ttl`, `shapes.ttl`, `validation.json`, `validation-report.ttl`, and `scope.md` in the workspace root. Use one `CatalogItem` class, one identifier property, the alpha individual, and a local SHACL shape enforcing exactly one `xsd:string` identifier. Keep evidence and the competency question in `scope.md`.

Run this actual validation command, keeping its stdout JSON as `validation.json`:

```bash
uv run --script skills/extract-ontologies/scripts/validate_semantic_artifacts.py --data data.ttl --ontology ontology.ttl --shapes shapes.ttl --inference none --output-format json --report validation-report.ttl > validation.json
```

Record validation scope and dependency versions from the real result. State OWL consistency and OWL profile checking as not checked unless actually executed with a suitable local checker. Do not equate SHACL conformance with an OWL consistency proof.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
