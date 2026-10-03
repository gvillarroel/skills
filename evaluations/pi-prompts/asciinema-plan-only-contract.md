Use the loaded `asciinema-real-command-video` skill to initialize and validate
one future non-interactive recording plan. This is plan preparation only; do
not install tools, run preflight, launch a target, record, render, or upload.

Work only in this isolated workspace. Treat
`skills/asciinema-real-command-video/` as read-only. Do not read acceptance
examples, helper source, sibling skills, repository documentation, parent
directories, or the network. Use the entry point and task-relevant references.

Run these two commands in order from the workspace root:

```bash
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py init-video outputs/planned-demo --template direct-argv --json
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-plan outputs/planned-demo/session-plan.json --json > outputs/plan-validation.json
```

Leave the initialized plan unchanged. Require these exact non-empty outputs:

- `outputs/planned-demo/session-plan.json`
- `outputs/plan-validation.json`

The plan must validate as a real direct-argv Python command. The video
directory must contain only its plan. Report the two paths and stop.
