Use skills/jev-batch-decisions as a read-only bundle. Plan an offline workflow for
a JSONL file containing two tiny normal records followed by one 5000-character
record. The job must use chunk_chars=1000. Do not access the network or inspect
credentials. The original records may not be truncated or silently subdivided.

Create input.jsonl and job.json in the workspace. Exercise the bundled planner
and capture its expected rejection without an unhandled shell-tool failure.
Produce exact artifact boundary.json containing rejected as a boolean,
http_attempts as an integer and preserved_long_record as a boolean, plus a brief
English reason. Verify the long input record is unchanged. Only read the prompt,
the loaded skill and task artifacts; do not modify the skill or inspect external
files. An expected nonzero program exit must be handled by your test wrapper.
