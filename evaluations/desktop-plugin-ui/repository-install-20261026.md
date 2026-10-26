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

Published source commit:
[`a7617b60c0d6559faccb8990468054a27af07b48`](https://github.com/gvillarroel/skills/commit/a7617b60c0d6559faccb8990468054a27af07b48).
Fresh remote installations below use this exact ref, not a local source copy.

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

## Verified remote outcomes

| Installation route | Result | Observation |
| --- | --- | --- |
| Codex built-in GitHub installer, ZIP download | Pass, 53.887 seconds | All 37 files exactly match canonical SHA-256 values. Standalone validation and the installed readiness helper pass; installed files stay unchanged. |
| Same installer, Git sparse checkout | Pass, 2.770 seconds | All 37 files exactly match; standalone validation and installed helper execution pass without changing the installed bundle. |
| Initial native Pi install in deep artifact storage | Fail, 33.701 seconds | Git reports `Filename too long` during checkout before skill discovery. Retain this actual failed receipt. |
| Native Pi install with process-local Windows Git long-path support | Pass, 33.849 seconds | Native `pi install` and `pi list` pass. RPC discovers exactly one `skill:desktop-plugin-ui` with `origin: package`, pointing inside the remote cloned package. All 37 files exactly match canonical source. |
| Pi cleanup | Pass | Native `pi remove` exits zero and the isolated settings retain no package registration. RPC process is closed, stderr empty and observed model-start events zero. |

The first combined run is **not** an uninterrupted overall pass: its four Codex
integrity/read-only checks pass, then Pi checkout fails. Retain that summary at
`projects/desktop-plugin-ui/artifacts/repository-install/20261026-published-a7617b60/`.
The narrowly scoped Pi continuation uses the same published source with
`--skip-codex`; its four checks pass under
`20261026-pi-longpaths-a7617b60/`. No already-passing Codex installation is rerun.

The failed Pi run's isolated Git checkout prefix is 155 characters. The longest
tracked repository path is 141 characters; their joined Windows path exceeds
the legacy 260-character limit. The observed normal user Pi prefix is 58
characters, with a maximum joined length of 200. This diagnoses the deep-test
failure, but is not evidence from a real-user global installation. The helper
now sets `core.longpaths=true` using Git's per-process environment only on
Windows. No global Git setting changes. The public guide includes the equivalent
`git -c core.longpaths=true clone` fallback for a long user-selected path.

Actual tools are Python 3.13.12, Node 24.18.0 and Pi 1.4.0 on Windows. Tests use
fresh destinations with spaces. Native discovery uses `get_commands`, without
`--skill`, without executing the skill command and without a model prompt.
Skill resources arrive through the installed package rather than ambient
project configuration. The original read-only 37-file bundle stays unchanged.

## Repository gates

The clean committed source passes all required checks:

```sh
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

ColorSet validation passes 38 published skills, 31 palette copies and 361
artifacts with zero findings. Pattern validation passes 1,348 IDs. The actual
[GitHub workflow](https://github.com/gvillarroel/skills/actions/runs/40322219403)
for the published source completes successfully, including skill validation,
ColorSet tests, standalone authoring tests, bundle audit, payload, Pages build
and deployment. Earlier working-tree and inventory preflight failures remain
recorded above; they are not reported as passing attempts.

Detailed commands, original stdout/stderr, file inventories and RPC responses
remain in ignored project artifacts. This report preserves their compact
outcomes; runtime installation does not depend on these evaluation files.

## Acceptance limits

Remote skill installation and native discovery are separate from a generated
plugin's installation, signed-in Desktop paint and representative-user behavior.
The skill remains `validating` for the retained broader generation failures and
host-specific gaps from the earlier PoC studies. No new inference or isolated
forward generation is needed for publishing unchanged skill bytes.
