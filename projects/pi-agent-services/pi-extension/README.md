# Pi Durable agent console extension

Use this native Pi Coding Agent extension to list local durable agents, inspect
jobs and public history, and exchange messages with a selected agent. It talks
to the existing service over authenticated loopback HTTP; it does not own or
restart the service. The tested extension API is Pi Coding Agent 0.84.2 on
Windows with Node 24. The independent service uses Pi Durable 1.3.0; these are
different package versions.

## Load in Pi

From the skills repository, start `pi`. The project loader is
`.pi/extensions/durable-agents.ts`. After Pi trusts the project, it is discovered
normally; use `/reload` in an already running Pi session. This installs nothing
in the global Pi account directory.

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
/durable-chat
/durable-chat repo-quality
/durable-chat delivery-watch Explain your role and current limits.
```

`/durable` lists registered agents with service-qualified IDs such as
`local/repo-quality`. `/durable-chat` opens a chooser; selecting an agent opens a message
editor and displays its public conversation history. Send a message, read its
answer, and continue. Escape or `/exit` leaves the editor; it does not abort work.
`/durable-chat <id> <message>` sends a one-shot message and waits for its response.

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
