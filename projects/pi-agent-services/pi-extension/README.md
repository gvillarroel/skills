# Pi Durable agent console extension

Use this native Pi Coding Agent extension to create durable agents with an
explicit base folder, list existing agents, inspect jobs and public history,
and exchange messages. Each new agent runs in its own independent service;
existing services retain their owners and need no restart. Connections use
authenticated loopback HTTP. Native Windows validation covers Pi 1.4.0 and the
template's pinned 0.84.2 with Node 24. The independent service uses Pi Durable
1.3.0; these are different package versions.

## Load in Pi

From the skills repository, start `pi`. The project loader is
`.pi/extensions/durable-agents.ts`. After Pi trusts the project, it is discovered
normally; use `/reload` in an already running Pi session.

The same loader can be registered for every Pi working directory:

```powershell
pi install C:/Users/villa/dev/skills/.pi/extensions/durable-agents.ts
pi list
```

This user-wide registration references the existing file in place; it does not
copy the implementation or install its dependencies. Install the exact same
loader that project discovery uses. Registering the implementation package or a
different entry alongside this wrapper loads the extension twice, duplicates
`durable_agents`, and can suffix command names. Use `/reload` in an open Pi
session after installation. To remove the user-wide registration:

```powershell
pi remove C:/Users/villa/dev/skills/.pi/extensions/durable-agents.ts
```

Keep this checkout and its installed extension dependencies available. If the
checkout moves, remove the old registration and install the new absolute loader
path. The implementation's adjacent `durable-agents.json` supplies the local
service connection when no project connection file overrides it.

To load explicitly from another working directory:

```powershell
pi -e "C:\Users\villa\dev\skills\projects\pi-agent-services\pi-extension\extension.ts"
```

The commands below run inside the Pi terminal. They are not Codex chat commands.

Commands use the Durable namespace to distinguish these persistent service
agents from the harness's own agents. This extension registers only `/durable`
and `/durable-chat`; it reserves no generic `/agents` or `/agent` aliases.

```text
/durable
/durable new
/durable list
/durable-chat
/durable-chat repo-quality
/durable-chat delivery-watch Explain your role and current limits.
```

`/durable` opens the terminal manager with a visible **Create new agent (choose
base folder)** action. `/durable list` prints registered agents with
service-qualified IDs such as `local/repo-quality`. `/durable-chat` opens a chooser; selecting an agent opens a message
panel with its public conversation history and a fixed message editor. Send a
message and read its answer in the same view. Escape or `/exit` leaves the
panel; it does not abort work.
`/durable-chat <id> <message>` sends a one-shot message and waits for its response.

## Create an agent and choose its folder

Use `/durable new`. The native form collects the name/ID, existing absolute base
folder, purpose, task profile, model policy and optional PR repository. The
folder editor starts with Pi's current working directory; replace it with the
folder you want, including paths with spaces. The task-aware `latest` policy
selects a current model and supported reasoning level before service admission.

The final review shows the exact base folder, project path and model policy.
PgUp/PgDn or Up/Down scroll; Tab or Left/Right selects Cancel/Create and Enter
accepts. Cancel is selected initially. Escape cancels. The review preserves
literal Windows paths and keeps its actions visible in compact terminals.

The new independent project lives at `<base-folder>/.pi/durable/<agent-id>/`.
Its tools can list and read text inside the chosen folder. Shell execution and
file modification are not enabled. Creation installs locked dependencies,
builds, starts a background Node owner and registers the service. Open its chat
from the completion prompt or `/durable-chat <service/agent>`. The process
continues after Pi closes; automatic login startup is a separate action. Its
local `AGENTS.md`, logs and creation receipt explain operation and recovery.

The installed factory resources are a generated, ignored `service-template/`
copy beside this extension. Canonical sources remain under `skills/pi-durable`.
To generate a fresh independent console including these resources, use
`uv run --script skills/pi-durable/scripts/scaffold-pi-extension.py <new-directory>`.
Add `--service-config <config.json>` to connect an existing service; omit it to
create the first agent from Pi. Deploy the entry, source modules and factory
resources together when updating this local installation.

## Agent lifecycle

The `/durable` manager now groups **Owner controls**, **Verification and
evolution**, and **Logs, login and archive**. Stopped managed agents remain
visible. Large inventories page before rendering and keep creation/reconnection
available on every page. `/durable-chat` still opens chat directly.

```text
/durable inspect <service/agent>
/durable start <service/agent>
/durable pause <service/agent>
/durable resume <service/agent>
/durable stop <service/agent>
/durable restart <service/agent>
/durable logs <service/agent>
/durable criteria <service/agent>
/durable verify <service/agent> --submission <id>
/durable evolve <service/agent>
/durable login <service/agent>
/durable archive <service/agent>
/durable connect
```

Stop/restart drain actual event, control, child and background work. A busy
deadline preserves work and leaves admissions paused. The separate
`/durable abort <agent> --background` action explicitly reviews cancellation of
retained background work. A PID alone never proves ownership.

Verification requires concrete configured assertions and produces passed,
failed, inconclusive or unconfigured receipts bound to actual admissions,
versions and output/contract hashes. Completed work is not automatically
verified. Requested evolution keeps reflection drafts and candidates inactive
until paired evaluation passes; drained promotion/rollback rebuild and smoke
the project before an explicit restart. Native login installation has its own
owned plan/review. Archive removes a stopped registration while retaining all
project/state files for reconnection.

Full lifecycle writes apply to projects with a matching console-managed
descriptor. Legacy/custom services keep chat and read-only status through their
existing owner; this update does not rewrite their code. A newly generated
project carries its own `dist/src/console/control-cli.js`, verification CLI and
evolution CLI, so operation does not depend on this extension or skill.

## Conversation panel

The header identifies the service/agent, control chat or selected task,
conversation and model. The transcript renders public Markdown with role
labels; the composer stays visible while the response arrives. Only progress
for the selected submission appears, including public partial text and bounded
tool names. Thinking and raw tool inputs/results stay hidden.

| Key | Action |
|---|---|
| Enter | Send the current message |
| Shift+Enter | Add a line; backslash followed by Enter also works |
| PgUp / PgDn | Browse the transcript |
| Ctrl+End | Return to the latest reply |
| Ctrl+C | Pause local waiting while the agent continues |
| Ctrl+R | Resume the same paused request without admitting it twice |
| Escape | Return to Pi; retain the draft and pending receipt in this session |

You can prepare the next message while the agent responds. Enter while busy
keeps that draft. A failed or paused request retains its stable ID and receipt;
resume it before sending another message in that panel. Reopening a completed
request reloads durable history instead of duplicating its final answer.
Unsent drafts are local to the current Pi session. RPC clients keep the simpler
structured-editor workflow because custom terminal components require TUI mode.

The terminal composition is checked with the pinned Pi 0.84.2 and installed
Pi 1.4.0 on Windows; native macOS UI behavior remains unverified.

## Commands

| Command | Purpose |
|---|---|
| `/durable services` | List configured service connections |
| `/durable status` | Show service model, owner and queue status where supported |
| `/durable jobs repo-quality` | List recent jobs and their exact IDs |
| `/durable read repo-quality --job <id>` | Read the selected task's public history |
| `/durable chat repo-quality --job <id>` | Open interactive chat for that task |
| `/durable send repo-quality --job <id> <message>` | Queue a follow-up on that task |
| `/durable steer repo-quality --job <id> <message>` | Send a correction to active task work |
| `/durable traces repo-quality` | Show bounded public evidence |
| `/durable wait repo-quality <submission-id>` | Reconnect to an already admitted message |
| `/durable cancel` | Cancel local polling/waiting; remote work continues |
| `/durable abort repo-quality --job <id>` | Explicitly abort that remote conversation |
| `/durable help` | Display the complete command help |

Without `--job`, conversation operations use the agent's control chat. A task ID
keeps its own context and transcript. The service's current IDs contain no
spaces. Use `service/agent` when different services have the same agent ID.

An ambiguous admission is retried once with the same request ID. If both
attempts fail, preserve the displayed request ID and retry the same message via
`/durable send <agent> --request-id <id> <same-message>`. If a submission ID was
returned, use `wait` instead of sending the message again. A timeout or cancelled
wait never sends the remote abort request.

## Connect multiple services

Configuration discovery checks `PI_DURABLE_CONNECTIONS`, the nearest ancestor
`.pi/durable-agents.json`, and finally `durable-agents.json` beside the extension.
Each connection points to a service config. The client resolves its loopback port
and state directory, then reads the local console token on every request.

```json
{
  "version": 1,
  "services": [
    {"id": "local", "configPath": "../projects/pi-agent-services/app/config.local.json"},
    {"id": "another", "configPath": "../another-service/config.json"}
  ]
}
```

Paths are relative to the connections file. They may also be absolute for local
deployment. The example assumes a connection file under the checkout's `.pi/`.
Configure only services the user owns or is authorized to access. Connections
must use `127.0.0.1`; embedded credentials, remote URLs and redirects are rejected.
Console tokens stay in their service state files and are never copied into
connection configuration, Pi session cards, or tool results.

The bundled `durable_agents` tool lets the outer Pi model inspect agents and
communicate when the user requests it. Slash commands operate directly without
an outer model turn. Console cards use custom session entries outside the outer
model context. History displays text blocks only, omitting provider thinking.
Explicit tool results participate in their normal model context as untrusted
external data.

## Validate and move the extension

Require Pi 0.84.2 and Node 24. The source loads directly with Pi's TypeScript
loader. For a production dependency installation, run
`npm ci --omit=dev --ignore-scripts --no-audit --no-fund` from this directory;
the Pi runtime supplies its own extension/TUI API. For development checks, use
the complete `npm ci --ignore-scripts --no-audit --no-fund`, `npm run check`, and
`npm test`. The npm cache stays under this package's `.cache/`.

Keep `extension.ts`, `src/`, package metadata/lock, and a local connections file
together when moving it. It does not import the original skill or service
source. A service must already be running; an unreachable service is reported
alongside other reachable services. Native macOS UI loading remains untested.

The [extension validation record](../extension-validation.md) separates offline
client/command tests, actual Pi runtime behavior and real Sol 6.1 responses.
