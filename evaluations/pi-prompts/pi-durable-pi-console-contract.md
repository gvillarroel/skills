Read ../prompt.md first. Use only the supplied pi-durable skill and normal local tools. Treat the copied skill as read-only. Keep generated files and dependency caches within this workspace. Do not inspect account credentials, send an agent message, start a model, register a global extension, or change files outside this workspace.

Create a service connection fixture at exactly `fixtures/service/config.json`, containing version 1, host `127.0.0.1`, port 4799, and dataDir `./state`. It is an offline configuration fixture, not a running service.

Use the skill's Pi-console generation capability to create an independent native Pi extension at exactly `outputs/pi-console`, with service ID `lab` pointing to that fixture. Do not reimplement the bundled extension. Install the package dependencies with lifecycle scripts disabled and run its TypeScript check. Acceptance fixtures may be absent from the runtime skill payload; do not treat that as a test failure or invent test results. No running backend or Pi account is needed for generation and type checking.

Write exactly `outputs/console-check.json` with fields `independent` (boolean), `piVersion`, `typecheckPassed` (boolean), `testsIncluded` (boolean matching generation), `commands` (an array with agent listing, one-shot message, and task-chat examples using service `lab`), `connectionFile`, and `cancellationBehavior` (explain local wait cancellation versus explicit remote abort). Do not claim any live message, UI or model validation.

Required exact nonempty artifacts are `fixtures/service/config.json`, `outputs/pi-console/extension.ts`, `outputs/pi-console/src/client.ts`, `outputs/pi-console/durable-agents.json`, `outputs/pi-console/scaffold-manifest.json`, and `outputs/console-check.json`.
