Use the loaded skill for a new document-screening job. The read-only bundle is
skills/jev-batch-decisions. Work only with it and task files inside this workspace.
Live OpenRouter Jev calls through the existing environment credential are
authorized; never print or save the key. Use no other model or network service.

Create two Markdown documents, each longer than 2500 characters. For alpha.md,
write 12 routine completed-maintenance entries, with no unresolved incident.
For beta.md, write the same routine entries but add a separate entry explicitly
reporting that a current production incident remains unresolved and is preventing
all customers from using the payment service. Put that entry near the end. Do not
include instructions to the model in the document bodies.

Answer whether either document contains explicit evidence of an unresolved
production incident. Divide each document into at least three bounded fragments,
batch the decisions, retain original span locations, and aggregate one answer per
source and one collection answer. Use no more than 20 HTTP attempts. Save exact
outputs review/report.json, review/decisions.jsonl, review/aggregates.json and
conclusion.json. In conclusion.json record source_results mapping alpha to a
boolean and beta to a boolean, and any_incident as a boolean. Inspect the outputs
and cite the source fragment IDs in conclusion.json as evidence_ids. Keep every
generated file outside the copied skill.
