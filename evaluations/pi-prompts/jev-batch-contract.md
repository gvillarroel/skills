Use the Jev batch decisions skill. Treat skills/jev-batch-decisions as read-only.
Create job.json by copying its runtime starter template into the workspace, and
create input.jsonl with these two records:

{"id":"a","text":"The service is down for all customers."}
{"id":"b","text":"Please refund my duplicate payment."}

Plan the work offline without calling a model or using a credential. Run this
exact command after creating the inputs:

```sh
uv run --script skills/jev-batch-decisions/scripts/jev_batch.py --job job.json --input input.jsonl --out planned --dry-run
```

Deliver exactly planned/plan.json, planned/report.json, planned/chunks.jsonl and
planned/map-jobs.jsonl. Verify both source records are covered and no HTTP calls
were made. Keep all generated files in this workspace and read only the loaded
skill and task artifacts. Do not inspect parent directories, global settings,
or other skills. Do not modify the copied skill.
