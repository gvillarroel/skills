# Install Assistant Plugin UI from this repository

`desktop-plugin-ui` is the authoring skill for Claude Desktop, Claude Code,
ChatGPT Desktop, Codex and Pi extensions. It selects supported host controls,
keeps architecture small, applies Nielsen's ten heuristics and validates actual
interactions. The complete independent bundle lives in
[`skills/desktop-plugin-ui/`](../skills/desktop-plugin-ui/SKILL.md).

## Install in Codex

Ask Codex to install the GitHub skill with its built-in installer:

```text
$skill-installer install https://github.com/gvillarroel/skills/tree/main/skills/desktop-plugin-ui
```

The installer copies the entire directory, including references, helper scripts,
palettes and runtime templates. The default destination is
`$CODEX_HOME/skills/desktop-plugin-ui`, or `~/.codex/skills/desktop-plugin-ui`
when `CODEX_HOME` is unset. It refuses an existing destination rather than
overwriting an installed version. The installed skill is available on the next
turn; invoke it as `$desktop-plugin-ui`.

For a repeatable version, replace `main` in the URL with a published commit SHA
or tag. The installer supports both GitHub ZIP download and Git sparse checkout.
If you run its Python helper directly, pass `--method git` to select sparse
checkout and `--dest <skills-directory>` for a separate installation location.
Its local path depends on the Codex installation; invoking `$skill-installer`
avoids assuming a machine-specific script path.

## Install in Pi

Install the repository's skill collection using Pi's native package manager:

```sh
pi install git:github.com/gvillarroel/skills
```

Use `pi install --local git:github.com/gvillarroel/skills` for project scope.
Start a new Pi session, then invoke:

```text
/skill:desktop-plugin-ui Build a small plugin for the selected host.
```

The root package already exposes `./skills`, so no separate manifest or
generated local installation is required. Pi installs the collection; use
`pi config` to narrow enabled resources if desired. Pin a version with
`git:github.com/gvillarroel/skills@<commit-or-tag>`. Remove the package with
`pi remove` and the same source string; use `--local` for a project installation.

## Use a checkout in Codex

For repository maintenance, refresh the ignored project-local installation:

```sh
git clone https://github.com/gvillarroel/skills.git
cd skills
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

Keep edits under `skills/`; `.agents/skills/` is an installed copy. Required
references and templates are inside the skill bundle. Historical evaluation
workspaces, generated PoCs and local artifacts are not installation dependencies.

## Verify the installation

Check that the selected installation contains `SKILL.md`, `agents/openai.yaml`,
`references/`, `scripts/`, both palettes and both runtime template directories.
The current published bundle has 37 files. Its optional Pi readiness helper is
stdlib Python and only checks installed versions:

```sh
python <installed-skill>/scripts/probe_runtime.py --host pi
```

Missing Pi is reported as a diagnostic; Pi is required only for Pi development.
Host-specific tools are needed when building or testing a plugin for that host,
not to install these instructions. The skill does not register a sample plugin,
add an MCP server or activate a host account. Follow the selected host's build
and installation route when creating a plugin.

The [repository installation verification](../evaluations/desktop-plugin-ui/repository-install-20261026.md)
records fresh remote installs, exact bundle comparisons, native Pi discovery
and validation limits. Broader plugin-generation reliability remains
`validating`; installation success does not change those earlier scores.

[Back to the documentation index](README.md).
