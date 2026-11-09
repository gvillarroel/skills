# Plan reuse for two approved OWL revisions

Use the ontology skill's reviewed premise-reuse workflow. The approved
ledger and both dependency reviews below are provided as trusted inputs
for this task. Preserve each source and the approved ledger. The only
required derived deliverable is the bundled planner's unmodified
reuse-plan.json.

Write before.json.

    {"id":"archive-policy","namespace":"https://example.invalid/archive#","ontology_iri":"https://example.invalid/archive","scope":"Project export and audit policies.","segments":[{"id":"term-registry","text":"Export: Export (class)\nPermitted: Permitted (class)\nAudited: Audited (class)"},{"id":"p01","text":"Exports are permitted by default unless an applicable hold overrides this rule."},{"id":"p02","text":"Every export is audited."}]}

Write after.json.

    {"id":"archive-policy","namespace":"https://example.invalid/archive#","ontology_iri":"https://example.invalid/archive","scope":"Project export and audit policies.","segments":[{"id":"term-registry","text":"Export: Export (class)\nPermitted: Permitted (class)\nAudited: Audited (class)"},{"id":"p01","text":"Exports are permitted by default unless an applicable hold overrides this rule."},{"id":"p02","text":"Every export is audited."},{"id":"p03","text":"A legal hold overrides the default permission."}]}

Write approved.json.

    {"premises":[{"id":"p01","axioms":["SubClassOf(:Export :Permitted)"],"gap":null},{"id":"p02","axioms":["SubClassOf(:Export :Audited)"],"gap":null}]}

Write review.json using the exact SHA-256 of the three files you wrote
for before_source_sha256, after_source_sha256 and approved_ledger_sha256.
Set both profile digests to the 64-character lowercase string
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.
Use the object below for dependencies.

    {"before":{"rows":{"p01":{"complete":true,"reads":[],"watches":["holds"]},"p02":{"complete":true,"reads":[],"watches":[]}},"selectors":{"holds":{"complete":true,"members":[]}}},"after":{"rows":{"p01":{"complete":true,"reads":[],"watches":["holds"]},"p02":{"complete":true,"reads":[],"watches":[]},"p03":{"complete":true,"reads":[],"watches":[]}},"selectors":{"holds":{"complete":true,"members":["p03"]}}}}

Run the bundled planner using these files. In your brief reply explain
why the old wording alone does not establish reuse. Keep the planning
result separate from an ontology validity or approval claim.
