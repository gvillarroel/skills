# Coverage denominator boundary

Please produce an auditable coverage report from ten supplied human-reviewed acceptance observations. This is an aggregation task, not a request to execute or invent query results. Work only in this workspace, leave the copied skill unchanged, and use only its runtime instructions and compact references or scripts. Do not read hidden files, repository or sibling content, acceptance examples, or external sources; no network services.

Create `candidate.json` containing exactly `{"id":"local-catalog","version":"1.0","purpose":"test artifact for supplied reviewed observations"}` followed by a newline. Pin its actual SHA-256 in the assessment input. The candidate IRI is `urn:local:catalog`, version `1.0`.

The fixed suite is `catalog-acceptance`, version `1.0`, with ten equally weighted applicable cases `q01` through `q10`. Each asks whether the catalog represents a distinct behavior numbered 1 through 10. All cases are optional. The supplied reviewer observations are: cases `q01` through `q09` fully satisfy their respective expected behavior; the evidence locator for each is `provided-review:<case-id>` and the observation is `Human review confirmed behavior <number>.` Case `q10` has not been reviewed; there is no observed failure. Treat the first nine as `reviewed`, not `executed`. Do not claim that any ontology-internal conflict scan, SHACL check, OWL consistency check, or query engine ran.

Write exactly `candidate.json`, `assessments.json`, `coverage.json`, and `coverage.md`. Use the bundled coverage aggregator for the actual report. Preserve the full denominator, identify the unverified case and next action, and show numerators and denominators. Report confirmed failures separately from unknown coverage. Missing conflict and formal checks must remain visibly unchecked; a successful aggregation must not imply release approval or universal ontology suitability.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
