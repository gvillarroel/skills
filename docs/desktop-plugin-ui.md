# Install Assistant Plugin UI from this repository

`desktop-plugin-ui` is the authoring skill for Claude Desktop, Claude Code,
ChatGPT Desktop, Codex and Pi extensions. It selects supported host controls,
keeps architecture small, applies Nielsen's ten heuristics and validates actual
interactions. The complete independent bundle lives in
[`skills/desktop-plugin-ui/`](../skills/desktop-plugin-ui/SKILL.md).

## Install only this skill

From your project, select the skill and target agent explicitly:

```sh
npx skills add gvillarroel/skills --skill desktop-plugin-ui --agent pi --copy --yes
```

This installs only `desktop-plugin-ui` into `.agents/skills/desktop-plugin-ui/`
for Pi. All references, helpers, palettes and templates are included. `--copy`
avoids symlink permissions, and `--yes` skips the selection prompts because both
the skill and agent are already explicit. No collection-wide Pi package is
registered. Requires Node 22.20+ and Git.

Add `--global` to install in `~/.agents/skills/desktop-plugin-ui/` for all your
projects. For Codex or Claude Code, replace `--agent pi` with `--agent codex`
or `--agent claude-code`. Agent-specific installation paths follow the
[Skills CLI agent table](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).
The [CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
defines skill selection, copying and project/global scope.

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

Use the single-skill command above. Start Pi in the project and approve its
project resources when prompted, then invoke:

```text
/skill:desktop-plugin-ui Build a small plugin for the selected host.
```

Pi discovers the copied skill automatically from `.agents/skills/`; there is
no extension registration or `--skill` startup flag. A file-based skill does
not appear as a package in `pi list`. To remove it, use
`npx skills remove desktop-plugin-ui --agent pi --yes` from the same project;
include `--global` if that was the installation scope.

If you previously installed the full repository with `pi install`, remove that
package using `pi remove git:github.com/gvillarroel/skills` before choosing this
standalone route. Match its original pinned source string and `--local` scope
when applicable. This prevents the collection from loading alongside the
selected copied skill.

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
