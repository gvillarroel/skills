# Codex Skills Repository

A maintained collection of reusable skills, compact references, deterministic helpers, and acceptance examples. Canonical bundles live in `skills/`; the backlog and validation status live in `SKILLS.md`.

A skill must work as an independent bundle. Repository documentation and example galleries support maintenance but must not become hidden runtime dependencies.

## Get started

Install the collection directly from GitHub in Pi, including HyperFrames and both
colorsets:

```sh
pi install git:github.com/gvillarroel/skills
```

Add `--local` to install for the current project. The
[HyperFrames guide](docs/hyperframes-colorsets.md#install-in-pi) covers invocation
and installation of the video package alone from a checkout.

### Install the Pi Durable agent console

The agent console is a Pi extension. From this checkout, generate its complete
standalone package beside the repository, then install it in Pi:

```sh
uv run --script skills/pi-durable/scripts/scaffold-pi-extension.py ../pi-durable-console
cd ../pi-durable-console
npm ci --ignore-scripts --no-audit --no-fund
pi install ./extension.ts
pi
```

Requires Node 24+, Pi, uv and Git. In Pi, use `/durable`, `/durable new` to choose
an agent's base folder, or `/durable-chat`. See the
[console installation guide](docs/pi-durable-console.md) for project-only scope,
existing registrations, verification and removal. Installing skills alone does
not register these console commands.

### Validate the repository

Use uv to inspect and validate the repository.

```sh
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
```

The [usage and maintenance guide](docs/getting-started.md) covers local installation, examples, and isolated forward tests.

## Documentation

- [Documentation index](docs/README.md)
- [Usage and operations](docs/getting-started.md)
- [Repository layout and validation](docs/repository-guide.md)
- [Skill backlog and validation status](SKILLS.md)
- [Evaluation methodology](evaluations/README.md)
- [AGENTS.md](AGENTS.md)
