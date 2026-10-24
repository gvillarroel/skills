Read ../prompt.md first. Use only the supplied pi-durable skill and normal local tools. Treat the copied skill as read-only. Keep generated files and dependency caches inside this workspace. Do not inspect account credentials, global Pi installations, project source outside this workspace, or other skills. Do not start a backend, invoke a nested Pi process, send an agent message, register an extension, or modify files outside this workspace.

Create an offline service connection fixture at exactly `fixtures/service/config.json` with version 1, host `127.0.0.1`, port 4799, and dataDir `./state`. This is only configuration; no service or credential file should be created.

Use the skill's bundled Pi-console generator to create an independent native Pi extension at exactly `outputs/console`, connected to that fixture with service ID `lab`. Do not reimplement or modify the bundled extension. Request acceptance tests when supported, while reporting truthfully whether they were included: the normal runtime skill payload excludes acceptance fixtures, so their absence is expected and is not a failed test. Install dependencies with npm lifecycle scripts disabled and run the generated package's TypeScript check. No Pi account, terminal session, nested agent or running backend is needed for generation and type checking.

Read only the compact skill references or generated files needed to understand the result. Write exactly `outputs/ui-check.json` with these fields:

- `independent`: boolean, indicating whether the generated package runs without the skill bundle.
- `piVersion`: the declared Pi compatibility version.
- `typecheckPassed`: boolean, based on the actual TypeScript check.
- `testsIncluded`: boolean matching the scaffold manifest. Do not invent a test count or claim to have run unavailable tests.
- `connectionFile`: the generated connection file path.
- `tuiInteraction`: describe the persistent custom terminal conversation view, public-only Markdown messages, visible agent/task identity, fixed composer, Enter submission, multiline input, history scrolling and local-close behavior.
- `rpcFallback`: explain which supported UI path applies outside native TUI mode.
- `recovery`: explain preserved drafts and stable request/admission receipt reuse after local cancellation or disconnection, including how to resume and how explicit remote abort differs.
- `commands`: an array with agent listing, interactive chat and task-chat examples using service `lab` and the current durable command namespace.
- `validationLimitations`: state that this offline generation and compilation exercise did not validate a live terminal UI, remote agent response or model execution.

Required exact nonempty artifacts are `fixtures/service/config.json`, `outputs/console/extension.ts`, `outputs/console/src/chat-ui.ts`, `outputs/console/src/chat-data.ts`, `outputs/console/src/display.ts`, `outputs/console/scaffold-manifest.json`, and `outputs/ui-check.json`.
