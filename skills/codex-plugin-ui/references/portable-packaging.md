# Portable package and real loader checks

Use when building a local OpenAI plugin, checking an archive, or diagnosing a
catalog entry that has no tools. Snapshot: October 25, 2026. These are package
contracts and bounded runtime observations, not frontend paint guarantees.

## Contents

- [Declare both portable schemas](#declare-both-portable-schemas)
- [Build a minimal distributable](#build-a-minimal-distributable)
- [Check the executing host version](#check-the-executing-host-version)

## Declare both portable schemas

The root files have different schemas:

- [plugin.json schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
  declares identity and optional client extensions. Do not add unsupported
  top-level host fields; use `extensions.com.openai` for OpenAI metadata.
- [mcp.json schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json)
  declares `mcpServers`. Each local server requires `type: "stdio"` and
  `command`; use plugin-rooted paths for bundled arguments and working directory.

Minimal files, after producing a bundled `dist/server.js`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "local-tools",
  "version": "0.1.0",
  "description": "Run bounded local tools."
}
```

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "local-tools": {
      "type": "stdio",
      "command": "node",
      "args": ["${PLUGIN_ROOT}/dist/server.js"],
      "cwd": "${PLUGIN_ROOT}"
    }
  }
}
```

Validate the actual JSON against the fetched primary schemas and check paths
independently. Schema validity does not prove filesystem containment, runtime
startup or host support. Keep the fetched schema URL, version and digest with
validation evidence. The source checker recognizes the exact `agent-plugins.org`
host; it still requires a bundled exact URL or independently verified explicit
allowance. A spoofed host or unknown path remains untrusted.

## Build a minimal distributable

Bundle server dependencies and the UI when practical; keep editable sources
and locked development dependencies available separately. Extract the actual
archive to a fresh folder with no `node_modules`, then start the declared entry
with its real working directory and substitutions. Require initialize, tool
discovery and an exact useful result from that copy. Exclude caches, secrets,
personal settings and build-only dependency trees from runtime archives.

A source directory working beside `node_modules` does not prove a portable
bundle. Relative runtime imports, asset paths and dynamic dependency loading
must also work after extraction. For stdio, reserve stdout for protocol JSON.

Prefer an archive library for cross-platform packaging. An observed Windows
`tar` invocation treated a drive-letter archive path as a remote destination.
Use literal paths with a suitable library or verify the selected tool's local
path behavior; successful source-tree tests do not repair a failed archive.

Use bundler dependency metadata plus execution to check runtime externals.
For esbuild, write a metafile with `--metafile=<workspace-path>.json` and inspect
the emitted entry's imports. Distinguish allowed Node built-ins from external
packages that must be bundled or shipped. A grep for `import`, `require`, a
package name or a URL inside bundled text is not an executable dependency
analysis: SDKs contain those strings in helpers, messages and schema identifiers.
An observed PoC's regex check rejected valid bundled SDK text while its clean
extracted runtime worked. Preserve the failed check, repair the validator and
test the unchanged archive; do not distort the runtime to satisfy the grep.

## Check the executing host version

Identify the exact executable that loads the plugin. In a task-local home,
test catalog discovery, installation, MCP startup and a real tool call as
separate layers. Use `codex plugin list --available --json` before installation;
plain installed-only listing can legitimately omit an available entry.

Observed with the same generated portable package and isolated homes:

| Core | Catalog and task-local install | Plugin MCP discovery/tool |
| --- | --- | --- |
| npm Codex 0.145.0 | Succeeded | No servers were returned in the tested app-server thread. |
| Desktop-bundled Codex 0.164.0-alpha.11.1 | Succeeded | Connected plugin server and exact direct tool result passed. |

Do not generalize this split into a universal version cutoff. Recheck a fresh
build and configuration. An older executable's successful catalog/install exit
does not establish that it understood root `mcp.json`. If compatibility is
needed, verify the installed host's `.codex-plugin/plugin.json` / `.mcp.json`
contract explicitly and build a distinct adapter; do not rename portable files
or silently change the original package to make the test appear to pass.

Current documented packaging and local marketplace procedures are in
[OpenAI packaging](https://developers.openai.com/plugins/build/plugins).
For backend checks, initialize the actual app-server, start an ephemeral
synthetic thread, inspect `mcpServerStatus/list`, then call
`mcpServer/tool/call` for the discovered server. Do not start a model turn merely
to test discovery. Host cache/network activity is separate from inference and
from the plugin's own runtime network use. Keep a direct MCP launch as an
explicit transport fallback, not evidence that the packaged loader succeeded.

Actual native form or component pixels, focus and account installation require
their own host checks. A successful backend callback is not a painted dialog.
