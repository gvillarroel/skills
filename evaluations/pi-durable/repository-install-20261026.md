# Repository console installation verification — 2026-10-26

## Scope and result

Verify the existing checkout-to-generated-console installation method on
Windows with Node 24.18.0 and the installed Pi 1.4.0. Generate from the canonical
Pi Durable bundle, install local dependencies, register the generated entry in
isolated Pi settings, exercise actual registered discovery and remove that
registration. No skill/runtime behavior, prior study score or existing agent
configuration changes.

**The installation and native RPC command path pass.** The independent service
factory also passes a plan-only continuation. Preserve the first factory test
fixture's CJS error as a harness failure; do not describe the original combined
helper invocation as an uninterrupted pass.

## Executed checks

| Check | Observation |
|---|---|
| Canonical generation | `scaffold-pi-extension.py` creates the console in `console with spaces/`, including its independent `service-template/` and empty version-1 connection registry. No ignored historical console payload is used. |
| Dependencies | `npm ci --ignore-scripts --no-audit --no-fund` exits zero; npm cache is confined to the private artifact run. |
| Native registration | `pi install <absolute-extension.ts>` and `pi list` exit zero and list the generated entry in the temporary user settings. |
| Registered discovery | Pi RPC runs **without `-e` and without `--no-extensions`**. `get_commands` finds exactly one `durable` and one `durable-chat`, loaded from the installed entry. Pi also exposes its unrelated built-in command. |
| Empty inventory/help | `/durable help` and `/durable list` respond through extension notifications, advertise `/durable new`, and use the explicitly selected empty registry. No actual service is queried. |
| No inference | The complete native trace contains zero `agent_start` or `turn_start` events. There is no model response or agent task execution. |
| Factory resources | Corrected plan-only fixture calls `prepareAgentCreation` with an existing base folder containing spaces, exact requested Sol 6.1/medium fields and installed Pi/npm JavaScript entries. The independent factory payload is accepted; the agent project and base-folder `.pi` directory remain absent. This is preparation, not model availability or execution evidence. |
| Removal and cleanup | `pi remove <same-entry>` exits zero; final `pi list` says `No packages installed.` The harness closes its own persistent RPC process after the commands finish. This does not test service-owner shutdown. |

`PI_CODING_AGENT_DIR` always points inside this project's ignored artifact
workspace. `PI_DURABLE_CONNECTIONS` selects the generated empty JSON explicitly.
`--no-approve` ignores project-local configuration/resources, preventing the
checkout's legacy wrapper from loading alongside the installed console.
`--offline --no-mcp` disables native startup network/MCP connections. The parent
environment is filtered to operating-system essentials for subprocesses; no
provider credential is copied into the generated package or settings.

All package-command writes target the isolated agent directory. Actual user
settings are not command targets. Their hash comparison during the factory
continuation matches, but concurrent tasks may independently change those files;
hash observations alone do not establish ownership or causality. Canonical source
hashes match before/after the continuation, and no canonical source was edited.

## Retained harness failure and continuation

The first bonus factory fixture was named `prepare-only.ts` outside an ES-module
package. The TypeScript runner selected CJS and rejected top-level await before
calling the factory. This is a **harness** failure, not a console installation or
factory runtime failure. Its nonzero process receipt remains unchanged.

Use the same generated console and installed dependencies, copy the fixture to
an explicit `.mts` entry, and rerun only that plan-only step. The continuation
passes without repeating npm installation, package registration, RPC commands or
model calls. The reusable helper now generates `.mts` for future fresh runs.

Private evidence is under
`projects/pi-extension-install/artifacts/native-install-20261026-01/`:
`scaffold.json`, `npm-ci.json`, `install.json`, `installed-list.json`,
`native-rpc.json`, original `factory-prepare.json`, corrected
`factory-prepare-continuation.json`, `remove.json`, `removed-list.json` and
`summary.json`. `summary.json` binds the successful phases and retained failure;
the continuation source snapshot and command receipts are preserved.

## Reproduction

The project-scoped
[verification helper](../../projects/pi-extension-install/scripts/verify-repository-install.py)
requires explicit installed JavaScript CLI paths and an unused private run ID:

```powershell
uv run --script projects/pi-extension-install/scripts/verify-repository-install.py --pi-cli <absolute-Pi-cli.js> --npm-cli <absolute-npm-cli.js> --run-id <unused-run-id>
```

It uses only the canonical skill's scaffolder/resources. All dependency files,
settings, receipts and workspaces stay under the owning project's ignored
artifacts. It refuses an existing run directory. The documented installation
guide is [Pi Durable console setup](../../docs/pi-durable-console.md).

## Limits

This verifies Windows registration and RPC dispatch through the installed entry,
not terminal rendering, native macOS behavior, login registration, actual agent
creation/startup, provider authentication, model inventory, GitHub effects or
service task quality. No real service, registry, durable conversation or system
scheduled task is operated. No isolated LLM forward test is needed for this
documentation-only visibility change; the skill bundle and runtime are unchanged.
