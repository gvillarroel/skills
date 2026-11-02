# Validate a new catalog entry

We are creating a small reusable vocabulary from this supplied policy: every reusable playbook has exactly one textual code; playbook `alpha` has code `PB-01`. Preserve that evidence and give us a local, machine-checkable ontology bundle. Use namespace `urn:playbooks:`. Keep the model small and explain the difference between schema axioms and data-quality constraints.

Work only in this workspace and keep the copied skill read-only. Use only `SKILL.md` and compact runtime references or scripts needed for the task. Do not read hidden files, repository or sibling content, acceptance examples, credentials, or remote sources. Installing the script's declared pinned dependencies through `uv` is permitted. No external ontology imports, IRI dereferencing, or network knowledge lookup.

Write exactly `ontology.ttl`, `data.ttl`, `shapes.ttl`, `validation.json`, `validation-report.ttl`, `invalid-data.ttl`, `invalid-validation.json`, `invalid-report.ttl`, and `scope.md` in the workspace root. Create an ontology class for playbooks and a code property, the valid alpha instance, and a local SHACL shape that enforces the policy. The negative data must contain a playbook `beta` with its required code absent. Actually validate both data files with the copied deterministic validator using no inference. Keep stdout as the respective JSON files and the real RDF reports at the exact paths above.

The positive run must conform. The negative run must be nonconformant with a diagnostic identifying the missing code. Handle the documented expected negative exit status within the shell command so an intentional rejection is not an unhandled failed tool call. Do not weaken the shape to accept beta. In `scope.md`, record the evidence, competency question, observed validation results, pinned dependency versions, and unperformed formal checks. Do not claim OWL consistency or profile certification from SHACL alone.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
