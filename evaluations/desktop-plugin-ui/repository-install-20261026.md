# Desktop Plugin UI repository installation — 2026-10-26

## Scope

Publish the existing independent `desktop-plugin-ui` bundle and document actual
installation from `gvillarroel/skills`. This change does not alter skill behavior
or the earlier plugin-generation acceptance scores. The source bundle remains
37 files, 279,492 bytes, SHA-256
`0b5d593f560a76a07c7b2775c40f4ca0f0adc99770859e13ad99542926abe4ae`.

The [installation guide](../../docs/desktop-plugin-ui.md) gives Codex's built-in
installer, Pi's native Git package installation and checkout synchronization.
The root Pi manifest already exposes `./skills`; no new runtime manifest,
MCP service or global configuration is required.

## Before publication

The GitHub contents endpoint returns HTTP 404 for
`skills/desktop-plugin-ui` at the observed pre-publication `main`. The working
directory contains all 37 files, but none is tracked in the current commit.
That local-only state cannot be installed from the public repository.

The actual installed Codex GitHub installer is run against the pinned
pre-publication commit `5b9432d9222f9febc421b181c60ba838fad0dfe0`, using Git sparse
checkout and an isolated destination. It fails to find the selected skill, as
expected. The failed receipt is retained under
`projects/desktop-plugin-ui/artifacts/repository-install/20261026-before-publication/`.
It is a real pre-publication failure, not a passing installation.

## Publication and remote verification

Track the canonical 37-file bundle, the installation guide, a focused backlog
entry and the project verification helper. Preserve unrelated working-tree and
staged changes. Historical local evaluation workspaces and generated PoC
artifacts are not part of the distributable runtime.

A clean committed-checkout preflight exposes one missing repository integration:
the versioned ColorSet output inventory lacks the newly tracked skill. Add only
this skill's authored/host-owned paint entry and preserve unrelated local
inventory changes. The complete working tree also briefly contains an unrelated
incomplete `knowledge-catalog-curator` directory; do not repair or publish that
other task to pass this installation check. Validate the clean committed source
instead. Keep both initial validator findings as preflight failures.

After publication, use fresh isolated directories to test both official Codex
installer transports and native Pi registration/discovery. Record their actual
outcomes below after executing the published source. Do not substitute a local
copy for a remote installation.

The [verification helper](../../projects/desktop-plugin-ui/scripts/verify-repository-install.py)
uses an explicit GitHub ref, a read-only installed Codex installer and optional
installed Pi JavaScript CLI. Every destination, temporary directory, Pi setting,
cache and receipt stays inside the owning project's ignored artifact tree.
It refuses an existing run ID. It compares all installed files with canonical
source, validates standalone copies, executes the installed version-only probe
and checks actual native Pi package discovery without invoking a skill/model
task. Pi registration is removed after discovery.

```powershell
uv run --script projects/desktop-plugin-ui/scripts/verify-repository-install.py --run-id <fresh-id> --ref <published-ref> --installer <installed-Codex-GitHub-installer.py> --pi-cli <installed-Pi-cli.js>
```

Global Codex/Pi settings are not installation targets. The helper filters
provider/account credentials from its subprocess environment. Installation
requires GitHub network access and normal Python/Git/Node/Pi tools as applicable;
it does not start a model task or activate any generated sample plugin.

## Acceptance limits

Remote skill installation and native discovery are separate from a generated
plugin's installation, signed-in Desktop paint and representative-user behavior.
The skill remains `validating` for the retained broader generation failures and
host-specific gaps from the earlier PoC studies. No new inference or isolated
forward generation is needed for publishing unchanged skill bytes.
