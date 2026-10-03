Use the loaded skill to classify this support queue with Jev through the
existing OPENROUTER_API_KEY environment variable. The live calls are authorized;
never print or persist the credential. Use only the loaded read-only
skills/jev-batch-decisions bundle, this prompt and your generated workspace files.

Create queue.jsonl with these independent records:
{"id":"t1","text":"I paid twice. Please refund the duplicate charge."}
{"id":"t2","text":"Our integration API returns an error on every call. Please repair the software."}
{"id":"t3","text":"I forgot my password and need to recover access to my account."}
{"id":"t4","text":"I want a refund for the duplicate subscription payment."}
{"id":"t5","text":"All users see a server error when loading the application."}
{"id":"t6","text":"I need to reset my account password."}

Choose a category rubric with billing, technical, account and unknown outcomes.
Also decide whether each record explicitly requests a refund. Process at least
two records per API request and produce category counts and whether any refund
is requested. Preserve an outcome per record. Then resume the same job and
prove it makes no new HTTP calls. Use a finite cap of at most ten HTTP attempts.

Required exact deliverables: results/report.json, results/decisions.jsonl,
results/aggregates.json and audit.json. In audit.json record first_http_attempts,
resumed_http_attempts and no_new_calls as a boolean. Keep all artifacts in this
workspace and do not read external files or modify the copied skill. Inspect
the actual results; do not claim that your own assertion is independent grading.
