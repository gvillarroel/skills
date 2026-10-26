# Install the Pi Durable console in Pi

The console adds `/durable`, `/durable new` and `/durable-chat` to Pi Coding
Agent. It creates independent agents, lets you choose their base folders, lists
their state and connects to their chats. You do not need an existing Durable
service to install the console or open the new-agent form.

The `pi-durable` skill supplies instructions and templates. The console is a
separate extension: installing the skill collection does not register its
commands. The canonical installation procedure uses the skill's generator to
include the service factory needed by `/durable new`.

## Prerequisites

- Node.js 24 or newer, npm, Git and uv on PATH.
- Pi Coding Agent already installed. Check with `pi --version`.
- A new or empty destination for the generated console. Keep it outside
  `skills/pi-durable/`, which is a read-only source bundle.

The shell commands below work in PowerShell and macOS shells. Native installation
checks are recorded separately from platform support claims; see
[the repository-install validation record](../evaluations/pi-durable/repository-install-20261026.md).

## Install from GitHub or an existing checkout

For a new checkout:

```sh
git clone https://github.com/gvillarroel/skills.git
cd skills
```

From the repository root, generate a complete console beside the checkout:

```sh
uv run --script skills/pi-durable/scripts/scaffold-pi-extension.py ../pi-durable-console
cd ../pi-durable-console
npm ci --ignore-scripts --no-audit --no-fund
```

The generator copies the console and its independent `service-template/`, writes
an empty service registry and records a provenance manifest. It refuses a
nonempty destination. `npm ci` installs the console's own dependencies; it does
not start an agent or service. Keep this generated directory after installation.

Add its entry to your user-wide Pi installation:

```sh
pi install ./extension.ts
pi list
pi
```

`pi list` should show the generated `extension.ts`. A local-file installation
references that file in place; Pi does not copy it or run `npm ci` for you. Open
Pi from the generated console or your own project, outside the skills checkout.
Use `/reload` if Pi was already open.

The template folder at
`skills/pi-durable/assets/templates/pi-extension/` is not a complete ready-made
console: the generator adds its service factory. Installing that folder directly
can leave commands visible while creation fails from missing resources.

## First use

In Pi, run:

```text
/durable
/durable new
```

The manager includes a create action. The new-agent form asks for an agent name,
ID, absolute base folder, task and model, and reviews the plan before creation.
Provider-backed work needs an appropriate configured account; an installed
console alone does not start model work.

Useful commands after creating or connecting an agent:

```text
/durable list
/durable inspect my-agent
/durable-chat my-agent Explain your current task
```

Use `service/agent` when an ID is ambiguous. The names deliberately avoid the
generic `/agents` command used by some harnesses. See the complete
[console reference](../skills/pi-durable/references/pi-extension.md) for task
chat, lifecycle, evidence and evolution commands.

## Project-only installation or a one-session preview

For a preview, from the generated console directory:

```sh
pi -e ./extension.ts
```

For project-only installation, run `pi install --local` from your actual project,
passing the generated entry's absolute path. For example, when the project and
console are sibling directories:

```sh
cd ../my-project
pi install --local ../pi-durable-console/extension.ts
pi
```

This registers the extension in that project's Pi settings rather than user-wide
settings. Normal project trust still applies. Choose one registration scope and
entry rather than installing several copies.

## Existing installations and the development checkout

Run `pi list` before adding a second console. This repository contains a
development wrapper at `.pi/extensions/durable-agents.ts`; opening Pi inside a
trusted checkout can load it automatically. A previous user-wide installation
may already reference that exact wrapper.

If that wrapper is already installed and working, use `/reload` and `/durable`.
Do not also register the generated entry without deliberately replacing the
previous registration. Loading different entries for the same console can
duplicate `durable_agents` and suffix command names.

For a clean new installation, follow the standalone steps above and open Pi
outside the checkout. The project's `.pi/durable-agents.json` can also override
the generated console's adjacent empty registry when running inside the checkout.
Connection discovery uses `PI_DURABLE_CONNECTIONS`, then the nearest project
registry, then the console's adjacent registry. Keep tokens in service state,
not in these connection files.

The generated console and its created agents retain their own source and
resources. They do not need the original skill or checkout to operate.

## Remove the registration

From the generated console directory, for a user-wide installation:

```sh
pi remove ./extension.ts
pi list
```

For a project-local installation, run `pi remove --local` from the same project,
using the same entry path. Removal unregisters the console; it does not delete
agent projects/state or stop their independent services. Keep service lifecycle
management separate from console installation.

## Troubleshooting

| Symptom | Check |
|---|---|
| `/durable` is unknown | Confirm `pi list` contains the intended entry; run `/reload` or restart Pi. |
| A dependency cannot be imported | Run `npm ci --ignore-scripts --no-audit --no-fund` inside the generated console directory. |
| New-agent creation reports a missing template | Regenerate a complete console with the helper; do not install only the raw extension template. |
| Commands or tools appear twice | Inspect user/project registrations and checkout auto-discovery; retain one intended entry. |
| The initial list is empty | This is expected for a new registry. Use `/durable new` or `/durable connect`. |
| A custom existing service is unreachable | Check its owner/configuration separately; installing the console does not start existing services. |

[Back to the documentation index](README.md).
