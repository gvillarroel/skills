# Plugin authoring metadata routing control

Decide whether the single available skill should be used for each request,
using only its name and description. Grade applicability; do not answer the
requests or test any product.

Available skill metadata:

```yaml
{{SKILL_METADATA}}
```

Read only this prompt. No skill is loaded and no skill body is available.
Do not read other files, use a shell, browse, call another provider or operate
an app/account. Write only `results/routing.json` in this workspace.

Return a JSON object with only `decisions`, an array in the exact order below.
Each row has only `id`, `use` (boolean), and `reason` (one concise English
sentence). Choose true when the skill's stated purpose would materially help
the request; otherwise choose false. Do not invent capabilities from the name.

1. `claude-desktop-build`: "Create a local Claude Desktop Chat plugin that
   shows a folder's build results, with native installation settings, a small
   interactive result view and usable recovery when a tool fails."
2. `chatgpt-desktop-build`: "Build a ChatGPT Desktop plugin for local CSV
   exploration. Keep setup simple, choose the supported local transport and
   implement a table with filtering and a text fallback."
3. `codex-build`: "Create a Codex plugin that runs a deterministic repository
   report and lets me inspect the result. Choose the simplest supported
   interaction and validate the desktop versus CLI boundary."
4. `pi-extension-build`: "Create a Pi extension with a slash command and
   terminal selector for a workspace preference, with cancellation and a
   no-interface argument fallback, without a model turn for each choice."
5. `claude-code-build`: "Build a Claude Code plugin with a native command and
   small status pane. Use host controls, keep deterministic actions local and
   test invalid input, cancellation and recovery."
6. `plugin-host-compatibility`: "Our plugin's MCP resource loads in a protocol
   probe, but its HTML controls do not appear in the assistant. Diagnose
   compatibility across Claude Desktop, ChatGPT Desktop and Codex."
7. `plugin-nielsen-review`: "Review our assistant plugin's interactions using
   Nielsen's ten heuristics. Remove unnecessary setup and controls, improve
   feedback and recovery, and validate the affected paths."
8. `generic-website`: "Create a standalone restaurant website with a menu,
   reservation form and responsive layout. It will run in a normal browser
   and has no assistant integration."
9. `general-nielsen-review`: "Evaluate a standalone mobile banking app's
   navigation against Nielsen's ten usability heuristics. There are no
   assistant plugins, extensions or MCP integrations."
10. `api-pricing`: "Find current OpenAI API model prices and estimate the
    monthly cost of a text summarization workload."
