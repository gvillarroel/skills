# Cross-assistant metadata routing control

Decide whether the single available skill should be used for each request,
using only its name and description. You are grading applicability, not
answering the requests or testing the products.

Available skill metadata:

```yaml
{{SKILL_METADATA}}
```

Read only this prompt. No skill is loaded, and no skill body is available.
Do not read other files, use the shell, browse, call a provider, or operate an
app/account. Write only `results/routing.json` in this workspace. Do not put
anything in a skill directory.

Return a JSON object with only `decisions`, an array in the exact order below.
Each row has only `id`, `use` (boolean), and `reason` (one concise sentence).
Choose `use:true` when this skill's stated purpose would materially help the
request; otherwise choose false. Do not invent capabilities from the name.

1. `claude-code-native`: "Our Claude Code terminal plugin needs a ticket pane,
   editable priority, keyboard selection, and a chart. Explain supported native
   controls, terminal limits, and the fallback we must keep."
2. `claude-desktop-chat`: "A local stdio plugin in Claude Desktop Chat returns
   HTML but shows no interface. Diagnose its UI resource, host, and rendering
   limits, and explain what evidence would establish a working View."
3. `codex-frontends`: "Compare a plugin's HTML dashboard and priority form in
   Codex CLI, app-server, desktop, and IDE. Which UI assumptions need frontend
   or approval-policy validation?"
4. `chatgpt-entrypoints`: "For our ChatGPT plugin, explain the limits of an
   inline iframe, fullscreen, sidebar entrypoint, file viewer, and optional
   forms or download APIs."
5. `copilot-surfaces`: "We use GitHub Copilot in VS Code and terminal. Explain
   how MCP Apps, extension webviews, canvases, and terminal forms differ and
   what we should actually test."
6. `ambiguous-cloud`: "Can my Cloud Code plugin display an interactive form?
   Identify the product ambiguity and the UI mechanism before asserting that
   a host supports it."
7. `protocol-versus-paint`: "Our MCP tool advertises a UI resource and an editor
   webview test passed. Does that prove the same plugin paints inside an
   assistant chat? Explain the evidence boundary and compatibility check."
8. `standalone-react`: "Build a standalone React support queue web app with
   search, a selected ticket, editable priority, chart, and CSV export."
9. `api-billing`: "Explain how OpenAI API token usage is reflected in a monthly
   invoice and how to estimate the cost of a text summarization batch."
10. `csv-cleanup`: "Use Python to deduplicate a ticket CSV by ticket ID, normalize
    priority values, and save a cleaned CSV plus a count of removed rows."
