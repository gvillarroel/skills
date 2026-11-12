# Choose and install an assistant UI skill

Use the skill matching the actual host. Each bundle contains its own required
instructions, references, palettes, helpers, and relevant runtime templates.
It does not depend on the comparison skill or another host bundle.

| Target | Skill | Scope |
| --- | --- | --- |
| Claude Desktop Chat | [desktop-chat-plugin-ui](../skills/desktop-chat-plugin-ui/SKILL.md) | MCP Apps and optional MCPB installation; ordinary Chat. |
| Claude Code | [code-native-plugin-ui](../skills/code-native-plugin-ui/SKILL.md) | Native commands/Mods for terminal, Desktop Code, and VS Code. |
| Pi | [pi-extension-ui](../skills/pi-extension-ui/SKILL.md) | Native commands/dialogs/widgets, mode-aware TUI/RPC, stateful actions. |
| Codex | [codex-plugin-ui](../skills/codex-plugin-ui/SKILL.md) | Plugins/MCP with loader, frontend, and policy-specific validation. |
| ChatGPT Desktop | [chatgpt-desktop-plugin-ui](../skills/chatgpt-desktop-plugin-ui/SKILL.md) | Local-thread packages, remote connections, and MCP Apps. |
| Gemini Enterprise | [gemini-enterprise-ui](../skills/gemini-enterprise-ui/SKILL.md) | Google Cloud A2UI catalogs over A2A and registration preparation. |
| Cross-host comparison | [desktop-plugin-ui](../skills/desktop-plugin-ui/SKILL.md) | Surface selection, shared-domain adapters, and capability studies. |

For example, select `--skill pi-extension-ui` in the installation command below
to install only Pi authoring. Select the host where the generated interface
will run; the agent executing these instructions can be different.
For a bundle that is still local to this checkout, use the checkout/sync
workflow below. Remote installation requires a published revision containing
the selected bundle.
Gemini Enterprise here means the Google Cloud app, with documented host-bound
A2UI versions; it does not mean Gemini CLI, Code Assist, or consumer Gemini.
See the [host-split validation record](../evaluations/desktop-plugin-ui/host-split-20261111.md)
for current validation and host acceptance limits.

For rich graphs, charts and linked workspaces, see the
[local interface lab](plugin-ui-rich-interfaces.md). It contains six host routes,
pixel critiques, runnable project sources and the exact scope of protocol,
native-engine, schema and actual-host checks.

## Install the comparison skill

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
The comparison bundle retains its historical resources. Its optional Pi readiness helper is
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
