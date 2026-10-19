Create a runnable Pi Durable service starter at exactly `service/` in this workspace. Use this exact scaffolding command:

```text
uv run --script skills/pi-durable/scripts/scaffold.py service
```

Keep `skills/pi-durable/` read-only. Configure an offline named agent `contract-reviewer` with GitHub detection disabled. Install its declared npm dependencies, build it, and use its documented CLI to generate a dry-run service plan for the current native platform. Save that CLI JSON output, without a prose wrapper, to exactly `plan.json`. Leave the generated configuration at exactly `service/config.json` and retain `service/package.json`.

Write exactly `verification.md` explaining the commands you ran, their outcomes, the observed native platform, what the plan would register, how to start/list/chat/stop it, and which checks remain unexecuted. Do not install or register any operating-system service and do not leave a process running. Do not contact GitHub, use live credentials, or call a real model. Network access is allowed only for installing declared package dependencies. Generated files, dependency caches, logs, and state must remain inside this workspace; do not write to the skill directory or any other user/system locations. A rendered plan may mention future native installation paths but must not create them.
