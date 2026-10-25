Read ../prompt.md first. Use only the supplied pi-durable skill and ordinary local tools. The copied skills/pi-durable directory is read-only. Keep every generated file and cache inside this workspace. Do not inspect credentials, global Pi installations, other skills, source repositories or files outside this workspace. Do not start services, run nested Pi, invoke model reflection, register native services, activate candidates or send messages.

Generate an independent project at exactly outputs/team with the bundled command:

uv run --script skills/pi-durable/scripts/scaffold-evolution.py outputs/team --strategy pareto --profile review-refine

Do not modify or reimplement generated application code or its initial manifest. Do not install dependencies: this contract checks template generation; native execution is tested separately. Inspect only the compact instructions and generated files needed to understand the result. Run the generated study runner's --help without opening a study or any model connection.

Write exactly outputs/check.json as an object describing the observed profile, configured agent ID, specialist roles, default provider, live example model, enforced child limits, evolution strategy, initial manifest hash verification, automatic activation policy and validation limitations. Hash every file listed in the generated scaffold-manifest.json and report whether all match.

Write exactly outputs/notes.md with commands for the generated project to build, run the offline subagent smoke, start the supervisor, chat with it, prepare a requested evolution study and perform a stopped-service release/rollback. Explain when parallel delegation versus an author/reviewer/refiner chain is useful. Explain why the default visible synthetic fixtures establish mechanics only, how one-way curator validation differs from development ranking, and which budgets are actually enforced. Do not claim live quality, token-cost limits or native macOS execution from this generation-only exercise.

Required nonempty artifacts: outputs/team/config.json, outputs/team/config.codex.example.json, outputs/team/src/subagents.ts, outputs/team/src/subagents-smoke.ts, outputs/team/evolution-plans/study.py, outputs/team/evolution-plans/plan.json, outputs/team/scaffold-manifest.json, outputs/check.json and outputs/notes.md.
