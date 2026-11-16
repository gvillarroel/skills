# OpenAI plugin compatibility — 2026-11-15

The unchanged Line World Video 0.8.1 release is an OpenAI-compatible portable
plugin. It has root `plugin.json` with the Agent Plugins 1.0.0 schema, root
`skills/`, and the supported `.codex-plugin/plugin.json` compatibility overlay.
The overlay declares `skills: "./skills/"`. This is a skills-based plugin;
there is no bundled MCP server to configure.

The current [OpenAI packaging documentation](https://developers.openai.com/plugins/build/plugins)
confirms portable skill discovery from root `skills/` and support for the
Codex compatibility overlay. The actual installed loader was codex-cli 0.167.0.

## Actual archive and host checks

Run:

```text
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

The verifier extracts the actual marketplace ZIP to a fresh project-owned
directory, validates portable schema/identity and the Codex skill root, checks
the exact six-skill set, and compares both distributed archives. The 100 primary
runtime files and 16 Google Vids files match canonical source hashes. All five
visual producers contain the current shared focus runtime. Focus inspection,
word-cue alignment and resumable native production utilities are included.

Native marketplace discovery, installation and enabled-plugin listing pass in
a fresh task-local CODEX_HOME. Every installed file matches the actual ZIP.
The executing Codex app-server's `skills/list` independently returns all six
enabled skills from that installed plugin cache:

- `line-world-video:line-world-video`
- `line-world-video:line-world-d3`
- `line-world-video:line-world-mermaid`
- `line-world-video:line-world-icons`
- `line-world-video:line-world-hyperframes`
- `line-world-video:line-world-google-vids`

The packaged `test_focus.py` and `test_narration_cues.py` pass 16 tests from the
installed copy. A removed mandatory focus runtime is rejected by the content
checker and restored before installation. No model turn or inference call is
used for these checks.

Retain the first verification as a validator failure: all six skills were
already discovered, but the initial assertion expected unqualified names.
The corrected assertion uses each actual installed SKILL.md path; native
plugin-qualified names remain recorded. The initial and final workspaces and
receipts are preserved under
`projects/line-world-video/artifacts/host-checks/openai-0.8.1/`.

## Deliverables and scope

- Portable ZIP: `line-world-video-0.8.1.zip`, SHA-256
  `4f29f4b6aeaa0ef8d7184d1e1fce10edf11e35a24810b115e77144cd2af4c336`.
- Codex marketplace ZIP: `line-world-video-0.8.1-marketplace.zip`, SHA-256
  `cb50e37282ceda462aa558a9bac0400e28b4b8b37d8330db9ff64e7aa0bf3a14`.
- Latest machine receipt:
  `projects/line-world-video/artifacts/host-checks/openai-0.8.1/verification.json`.

No archive or skill behavior changed, so this is package/loader validation of
the existing release rather than a new skill forward-test cohort. Existing
visual-generation limitations remain recorded separately. The checks do not
claim global installation, activation in the user's desktop account, or
publication/certification in OpenAI's public directory.
