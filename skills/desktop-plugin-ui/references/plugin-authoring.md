# Build the smallest useful plugin

Use this route when asked to create, extend or repair a plugin. Produce working
source and a runnable local workflow; a capability comparison alone does not
complete an authoring request. Snapshot: October 25, 2026. The architecture
choices below are engineering recommendations; linked host contracts establish
the package and API facts. Recheck the requested host's current contract.

## Contents

- [Choose one real host route](#choose-one-real-host-route)
- [Keep multi-host blueprints compact](#keep-multi-host-blueprints-compact)
- [Reduce architecture before adding controls](#reduce-architecture-before-adding-controls)
- [Package the selected host](#package-the-selected-host)
- [Deliver a tested vertical slice](#deliver-a-tested-vertical-slice)

## Choose one real host route

| Requested target | Start with | Add only when needed | Read next |
| --- | --- | --- | --- |
| Claude Desktop ordinary Chat | One local stdio MCP server with useful text/structured tools | An MCP Apps HTML resource for interactions; MCPB for installation | [Chat deployment](distribution.md), [chat patterns](chat-patterns.md), [bridge](bridge-patterns.md) |
| Claude Desktop Code tab / Claude Code terminal | A Claude Code plugin with a native command or skill | A Mod with supported native controls; MCP only for a separate tool service | [Native patterns](native-patterns.md), [surface limits](claude-host-limits.md) |
| ChatGPT Desktop local thread | Portable OpenAI plugin with a packaged stdio MCP server, when tools are needed | MCP Apps UI and documented OpenAI extensions | [ChatGPT](chatgpt-limits.md), [bridge](bridge-patterns.md) |
| Codex desktop / CLI | A supported plugin bundle or direct MCP configuration for the requested workflow | UI only after checking the actual frontend; an owned frontend only when requested | [Current offerings](capability-offerings.md), [Codex](codex-limits.md) |
| Pi | A local TypeScript extension with a command and native terminal UI | A model-facing tool only when the agent must invoke the operation | [Pi extensions](pi-extensions.md) |

Claude Desktop Chat and its Code tab use different extension runtimes. ChatGPT
Desktop local execution and ChatGPT web remote execution also need distinct
transport checks. A shared MCP server does not make the installation packages,
permissions or rendered surfaces interchangeable.

## Keep multi-host blueprints compact

For a plan spanning several hosts, start with this reference's route table and
packaging sections. Read a deeper host or pattern reference only to resolve a
specific API, interaction or support question; do not load every catalog merely
because the plan names several products.

Define the domain logic, draft/commit authority, state transitions and Nielsen
review once. Give each host a short adapter record with required files,
transport, native interaction, conditions, fallback and validation. Reference
the shared contract instead of repeating states, H1-H10 or data in every row.
If both Markdown and JSON are requested, use JSON for the precise contract and
Markdown to explain decisions and tradeoffs, rather than duplicating every field.

A blueprint describes planned implementation and checks. Give host claims a
source/basis note and keep unperformed acceptance explicit. Do not automatically
turn a blueprint or ordinary build notes into a formal evidence study with a
second claim ledger; use that workflow when an evidence/capability report or
claim inventory is actually requested. Preserve requested schemas and factual
scope. A concise blueprint still needs every requested host, runnable validation
steps and a buildable adapter; brevity does not excuse missing requirements.

## Reduce architecture before adding controls

Write one sentence naming the user's job, its input, and a visible successful
result. Choose the smallest vertical slice that completes it. Keep domain logic
in ordinary functions and use a thin host adapter for invocation, presentation
and cancellation. Share domain logic across hosts when that actually reduces
maintenance; package each host's adapter separately.

Use a native dialog for a short choice or bounded input, text for a result that
needs no manipulation, and a supported component for repeated filtering,
selection or inspection. Do not add React, a database, background service,
websocket, local HTTP server, OAuth app or public deployment merely to draw a
form. Add a dependency only for a requirement the simpler route cannot meet.

Implement filtering, selection, validation, formatting, navigation and explicit
button actions directly. Keep model inference for reasoning, generation or
interpretation the task requires. Distinguish a draft from a submitted action;
opening settings, cancelling, retrying a failed direct action and updating a
local selection should not automatically create another model turn. When a
host requires a first model turn to open a component, record it separately from
subsequent direct interactions.

Before implementation, select the relevant Nielsen checks from
[usability-and-color.md](usability-and-color.md), then review all ten against the
finished interaction. Convert each applicable finding into an observable state
or behavior. Keep one primary action per decision, reveal secondary options on
demand, retain entered values after errors, and preserve a useful text fallback.
Avoid extra confirmation for reversible navigation or ordinary settings. Use
host permission controls and confirmation proportionate to the actual action.

## Package the selected host

### Claude Code and Desktop Code

Copy and adapt the tested starter described in
[native-authoring.md](native-authoring.md). Its command registration, execution
event and real native tests prevent a self-consistent mock from hiding a broken
host command. Keep the matching test contract when changing the sample data.

Keep `.claude-plugin/plugin.json` as the plugin's metadata file when metadata is
needed; keep components at the plugin root. A native Mod uses a hooks module,
not an HTML iframe. Build only the necessary component: a skill for model-led
instructions, an explicitly invoked native command for deterministic behavior,
or a pane for persistent interaction. The installed build's declarations and
native tests determine which controls work on terminal, Desktop and VS Code.
[Claude plugin overview](https://code.claude.com/docs/en/plugins),
[manifest reference](https://code.claude.com/docs/en/plugins-reference).

Validate with `claude plugin validate <plugin-dir> --strict --json` and
`claude plugin test <plugin-dir>`. Use a task-owned folder with
`claude --plugin-dir <plugin-dir>` for an authorized local trial. Native engine
tests do not prove visible focus, placement, scrolling or account installation.
Use [native-patterns.md](native-patterns.md) for command registration, draft and
submit state, cancellation and unplaced-pane fallback.

### Claude Desktop Chat

Start with the MCP server and optional app resource. Treat MCPB packaging and
its generated configuration form as a separate deliverable. If an installer is
requested, include the entry point, runtime dependencies and typed `user_config`
actually needed; validate and pack with the current MCPB CLI. Test the extracted
bundle, not just the source directory. Do not package a Claude Code Mod and
claim it adds a panel to ordinary Chat.
[MCPB manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md),
[Claude local MCP Apps](https://claude.com/docs/connectors/building/mcp-apps/getting-started).

### ChatGPT Desktop and Codex

Use [portable-packaging.md](portable-packaging.md) for exact portable schemas,
extracted-bundle checks and the observed old/new Codex loader split. Verify a
tool through the executing host; catalog installation alone is insufficient.

For a new portable package, use root `plugin.json`, optional `skills/`, and
root `mcp.json`. Put OpenAI-specific fields under `extensions.com.openai`.
The supported `.codex-plugin/plugin.json` compatibility format has its own
shape; renaming `.mcp.json` does not convert its schema. UI belongs to the MCP
integration, not the manifest. Package only the requested components and use a
repo-local marketplace for an authorized local catalog trial.
[OpenAI packaging](https://developers.openai.com/plugins/build/plugins).

A packaged local stdio server uses `type: "stdio"`, a command and arguments;
`${PLUGIN_ROOT}` locates bundled files. Include its dependencies and test in a
local thread. Public local-MCP submission has partner eligibility requirements;
that restriction is separate from building and testing a local package.
[Desktop-only plugins](https://developers.openai.com/plugins/deploy/desktop-only).

Direct MCP setup can be shared by Desktop, CLI and IDE clients. Catalog plugin
support and actual UI support remain surface-specific. A direct MCP connection
is a useful transport diagnostic if plugin discovery fails; report that route
change rather than claiming the packaged loader passed.
[MCP setup](https://learn.chatgpt.com/docs/extend/mcp).

## Deliver a tested vertical slice

1. Create sources, dependency metadata/locks, host adapter and exact requested
   output paths inside the authorized workspace. Include concise run, test and
   local loading instructions with the deliverable. Keep credentials external.
2. Build or type-check, validate manifests and packaged paths, initialize the
   protocol if used, and run the main action with synthetic data. Verify an
   extracted/copied package can start without depending on the author's checkout.
3. Exercise idle/loading/success/empty/error/cancel states as applicable. Test
   invalid input, repeated activation and a failed action followed by recovery.
   Closing or cancelling must not submit a draft or lose committed results.
4. Check the actual supported interaction layer: native engine, Pi TUI/RPC,
   MCP bridge fixture or browser component. For a web component, inspect narrow
   and wide layouts, keyboard use, accessible names and contrast. Check real
   host painting separately when the host is available and the action authorized.
5. Revisit the user's job: remove controls, setup steps and dependencies that do
   not improve completion, recovery or clarity. Record unresolved Nielsen issues,
   remaining host checks and inference counts without turning a self-review
   into user-testing evidence.

Keep a compact validation note identifying the exact host/build, command,
expected and actual result, and evidence layer. If only protocol or browser
tests ran, deliver the runnable plugin and state that real-host acceptance is
pending. Preserve failed attempts and diagnose the first failing layer. Stop at
an actual account, trust or permission gate while continuing independent build
and fixture checks; do not change global configuration or publish merely to
complete a local authoring request.
