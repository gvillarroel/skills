Run the installed `reflex-xy` skill's deterministic diagnostic from this workspace:

```bash
uv run --script skills/reflex-xy/scripts/diagnose.py --output-dir artifacts/probe --report artifacts/probe.json
```

The command must succeed and produce non-empty `artifacts/probe/chart.html`,
`artifacts/probe/chart.svg`, `artifacts/probe/chart.png`, and `artifacts/probe.json`.
The JSON report must have `passed: true` and accurately describe the diagnostic
results. Inspect the report and at least one rendered artifact. Do not replace a
failed native render with a hand-drawn chart or mark an unexecuted check as passing.

Treat all of `skills/reflex-xy/` as read-only. Write generated files only in this
workspace outside `skills/`. Do not inspect other skills, parent directories,
acceptance examples, or repository documentation. Registry access for declared
dependencies is allowed; do not publish files or start a deployment.
