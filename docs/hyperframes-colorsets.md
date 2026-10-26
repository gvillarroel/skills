# HyperFrames plugin with colorsets

The canonical plugin package lives in
[`projects/hyperframes-colorsets/plugin`](../projects/hyperframes-colorsets/plugin/README-COLORSETS.md).
It contains the original HyperFrames **0.8.199** manifests, launcher and four core
skills, plus the small native `colorsets` style skill. The upstream source is
[`heygen-com/hyperframes`, release v0.8.199](https://github.com/heygen-com/hyperframes/tree/v0.8.199),
commit `42b84632a8d06cf86bd72633d03b38a7a8371a89`.

## Use

Select `colorset1` for the original red and neutral palette, or `colorset2` for
the extended palette. Both preserve Open Sans and the source YAML values.

```text
Use $colorsets and HyperFrames to create a video with colorset1.
Use $colorsets and HyperFrames to create a video with colorset2.
```

The plugin's instructions, metadata and examples are in English. The requested
video language remains a task choice. The colorsets are native `FRAME.md` design
specifications; the original authoring and rendering workflow remains unchanged.

Check the bundled official launcher from the repository root:

```powershell
node ./projects/hyperframes-colorsets/plugin/skills/hyperframes/scripts/plugin-cli.mjs --version
```

For authoring and rendering, resolve the launcher's absolute path and run it from
the video project directory, as described in the bundled plugin execution rules.

## Install in Codex from a repository checkout

The versioned catalog at
[`projects/hyperframes-colorsets/.agents/plugins/marketplace.json`](../projects/hyperframes-colorsets/.agents/plugins/marketplace.json)
makes this project a portable marketplace root. Its `hyperframes` entry resolves
`./plugin` relative to `projects/hyperframes-colorsets`.

From the skills repository root, register the catalog with a Codex CLI that
supports plugins:

```powershell
codex plugin marketplace add ./projects/hyperframes-colorsets
```

Open the plugin manager, select **HyperFrames Colorsets**, and install
**HyperFrames by HeyGen**. Marketplace files alone do not confirm desktop
installation or activation.

The developer's ignored repository-root catalog also points to this package and
preserves its existing Reflex XY entry. It is local configuration and is not
required by the portable catalog.

## Install in Claude

The project also provides a native Claude marketplace at
[`projects/hyperframes-colorsets/.claude-plugin/marketplace.json`](../projects/hyperframes-colorsets/.claude-plugin/marketplace.json).
The plugin includes the exact official HyperFrames 0.8.199 Claude manifest.
From the repository root:

```powershell
claude plugin marketplace add ./projects/hyperframes-colorsets
claude plugin install hyperframes@hyperframes-colorsets-local
```

In Claude Code, invoke `/hyperframes:colorsets` and
`/hyperframes:hyperframes`. A session-only alternative avoids installation:

```powershell
claude --plugin-dir ./projects/hyperframes-colorsets/plugin
```

After choosing a palette, use the normal HyperFrames workflow. The original
launcher reads the plugin release from its manifest, resolves its own installed
location, and retains version 0.8.199.

For the web/Desktop Chat/Cowork **Upload plugin** flow, use the plugin-only ZIP
at `projects/hyperframes-colorsets/artifacts/packages/hyperframes-0.8.199-colorsets-claude.zip`.
It contains `.claude-plugin/plugin.json` at its root. The Codex marketplace ZIP
contains a catalog and a nested plugin, so it is not the Claude upload artifact.

Claude's documentation describes skill availability across Chat, Cowork and
Claude Code. Rendering a local video additionally requires a host with Node.js,
Chromium and FFmpeg. The terminal installation checks below establish native
Claude Code package discovery and execution, not an observed web/Desktop/Cowork
session. Follow the account and environment capabilities of the selected surface.

References: [Claude plugin manifest](https://code.claude.com/docs/en/plugins-reference),
[Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), and
[using plugins across Claude surfaces](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

### Native Claude regression

```powershell
uv run --script projects/hyperframes-colorsets/scripts/verify_claude.py
```

The probe creates a fresh `CLAUDE_CONFIG_DIR` and workspace under the project's
ignored artifacts directory. It performs no model calls or account login. It
checks strict plugin and marketplace validation, actual marketplace registration
and installation, the enabled installation inventory, the five discovered skills,
the original launcher version from the installed cache, and both cached preset
and YAML pairs. It checks source and global Claude-state hashes before and after.

On 2026-10-25, two fresh runs passed with Claude Code **2.1.302**: all eight native
commands exited successfully, exactly five skills were discovered, HyperFrames
resolved to **0.8.199**, and the source and global state were unchanged. A separate
session-only load of the plugin-only Claude ZIP also discovered the same five
skills. Reports and logs are under `projects/hyperframes-colorsets/artifacts/claude/`.

The probe requires a recognized, non-null manifest. An exit code of zero from
`claude plugin validate` alone is insufficient: this Claude build returned success
with `manifest: null` when the Claude manifest was missing. Component discovery
is verified separately with the native inventory.

These are native installation and execution-path checks. They do not claim that
a Claude model generated a video, nor that the web/Desktop/Cowork interface was
observed. The plugin's existing video-generation workflow and palette behavior
are unchanged.

Two additional renderer probes used the original launcher from the actual
installed Claude cache. Each mounted a native sub-composition, used its cached
colorset preset and Open Sans, and passed lint and browser check with zero errors
or warnings. Both exported and fully decoded 2-second H.264 videos at 1280×720,
30 fps, with 60 frames. Native PNGs visibly used the selected red `#9e1b32` or
blue `#007298` token; the cache and canonical plugin stayed unchanged. These
integration fixtures and their exact commands are kept locally under
`projects/hyperframes-colorsets/artifacts/claude/render-smoke/`.

The former copy under `personal/plugins/hyperframes` was moved to this project.
Its old marketplace entry was removed. Previous generated videos remain separate
from the reusable plugin source.

## Install in Pi

The enclosing project has a native Pi
[`package.json`](../projects/hyperframes-colorsets/package.json) whose `pi.skills`
field points to `./plugin/skills`. It exposes the same five skills without a
custom extension, duplicate runtime or alternative renderer.

From the skills repository root, install it for that checkout:

```powershell
pi install --local ./projects/hyperframes-colorsets
```

For a separate video project, run `pi install --local` from that directory and
give the absolute path to `projects/hyperframes-colorsets`. Local packages are
referenced in place, so keep the checkout at a stable path. Normal Pi project
trust applies before project packages load.

For a single session, load the package explicitly instead of registering it:

```powershell
pi -e ./projects/hyperframes-colorsets
```

Use the native skill commands:

```text
/skill:colorsets Create a video with colorset1.
/skill:hyperframes Create a video with the selected native style.
```

Use `colorset2` explicitly for the extended palette. Pi resolves supporting files
inside the same package, and the original launcher still reads HyperFrames
0.8.199 from the plugin manifest.

The repository root is a monorepo rather than this Pi package root. Clone the
repository and install the subdirectory locally; a Git installation of the whole
repository is not a substitute for selecting this package.

References: [Pi 1.4.0 packages](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/packages.md)
and [Pi skills and invocation](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/skills.md).

### Native Pi regression

```powershell
uv run --script projects/hyperframes-colorsets/scripts/verify_pi.py
```

The probe copies only the package manifest and plugin payload into a fresh local
workspace and isolates `PI_CODING_AGENT_DIR` with offline startup. It runs native
local installation, package listing and repeat installation, then uses Pi's
`DefaultResourceLoader` on the explicit package with ambient discovery disabled.
It verifies the five skill paths, diagnostics, both preset/YAML pairs, and the
original launcher version from the resolved package. It does not construct a
model session or read authentication data.

On 2026-10-25, Pi **1.4.0** on Node **24.18.0** passed the native package probe:
exactly five skills, no diagnostics, no duplicate declaration after reinstall,
HyperFrames **0.8.199**, unchanged source and unchanged global Pi settings.
The evidence is kept under `projects/hyperframes-colorsets/artifacts/pi/`.

Two additional renderer probes used the package root resolved by native Pi.
Both colorsets passed original HyperFrames lint and browser checks without
errors or warnings, then exported and fully decoded 2-second H.264 videos at
1280×720, 30 fps and 60 frames. Open Sans loaded, and the native PNGs contained
the selected red `#9e1b32` and blue `#007298` tokens. The resolved package and
canonical plugin stayed unchanged. The reports, exact commands and frames are
under `projects/hyperframes-colorsets/artifacts/pi/render-smoke/`.

Native project-local installation requires project trust. The isolated test uses
`--approve` for its fresh disposable workspace; add that flag for a deliberate
noninteractive install into a workspace you intend to trust.

## Verification

The relocation checks compare all 234 moved files against their pre-move hashes,
verify the original upstream files, check both palette definitions and invoke
the original launcher's version command. Local reports are stored under
`projects/hyperframes-colorsets/artifacts/validation/`.

On 2026-10-25, all 234 relocated file hashes matched, the original launcher
reported `0.8.199`, both palette YAML files matched their repository sources,
and all four repository gates passed. The refreshed English distribution ZIP
is kept locally at
`projects/hyperframes-colorsets/artifacts/packages/hyperframes-0.8.199-colorsets.zip`.

Repository validation commands:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

This is a package relocation and documentation translation. It adds no standalone
canonical skill or new video-generation behavior, so it does not create a new
isolated model-evaluation subject.
