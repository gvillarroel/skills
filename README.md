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
