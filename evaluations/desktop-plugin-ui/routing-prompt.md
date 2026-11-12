Choose whether the catalog skill should be used for each request below. Make a metadata decision only; do not execute any request or claim real product skill selection. No skill is loaded. Use only the catalog name and description below. Do not inspect the repository, read a skill body, discover tools, access the network, or run shell commands. This prompt is the only file you may read.

Write the exact workspace-relative file `results/routing.json` as an object with one `decisions` array. Include exactly one object per request, preserving order, with fields `id` (the request ID), `use` (JSON true or false), and `reason` (a short English explanation based on the catalog metadata). Do not create other artifacts.

Catalog:

```json
{
  "name": "desktop-plugin-ui",
  "description": "Explain, select, and investigate plugin UI methods for Claude Desktop, including MCP Apps in chat, MCPB configuration, and native Claude Code Mods. Use for capability questions, interface pattern selection, and evidence-based compatibility diagnosis; identify ambiguous names such as Cloud Desktop before claiming host support."
}
```

Requests:

```json
[
  {"id": "chat-view-diagnosis", "request": "My Claude Desktop MCP connector returns useful tool text, but its interactive chart never appears. Help me work out which integration layer is failing and what evidence to collect."},
  {"id": "chat-surface-choice", "request": "We are adding plugin UI to Claude Desktop. Should a short approval and a detailed analysis editor use inline cards, a carousel, or fullscreen? Explain the relevant pattern rules."},
  {"id": "extension-configuration", "request": "For a Claude Desktop extension, can MCPB collect an API key and directory setting, and is that settings form the same thing as the plugin's runtime UI?"},
  {"id": "code-native-pane", "request": "Our Claude Desktop Code-tab plugin needs an interactive settings pane. Compare native Claude Code Mods with the HTML UI used by MCP Apps in Chat, including their limits."},
  {"id": "remote-route", "request": "Our remote MCP connector URL works from my laptop, but Claude Desktop cannot connect when the server is behind our VPN. Diagnose the route and distinguish it from a local Desktop extension."},
  {"id": "ambiguous-product", "request": "What kinds of UI can plugins show in Cloud Desktop? I may have the product name wrong; establish the host before recommending APIs or claiming something works."},
  {"id": "generic-react-app", "request": "Build a React admin page with a searchable customer table for our ordinary browser website. No AI host or plugin integration is involved."},
  {"id": "openai-billing", "request": "Explain how OpenAI API billing and prepaid credits work, and where I can check my usage invoice."},
  {"id": "static-matplotlib", "request": "Use Matplotlib to make a publication-ready static PNG chart from these CSV measurements, with error bars and a figure caption."},
  {"id": "word-edit", "request": "Edit this Word document to fix spelling and apply consistent paragraph spacing, then export a PDF."}
]
```
