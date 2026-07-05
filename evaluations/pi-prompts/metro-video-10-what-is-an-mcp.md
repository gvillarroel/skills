First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-an-mcp/src/index.html --source-package projects/metro-ai-concept-videos/what-is-an-mcp/source/source-package.json --output projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `systems-flow` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is an MCP.
Video title: What is an MCP.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the concept cannot be distinguished with red, neutral, white, black, and gray. If any color set 2 color is used, document the strict reason in production notes.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-an-mcp/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-an-mcp/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-an-mcp/src/index.html`
- `projects/metro-ai-concept-videos/what-is-an-mcp/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/video-renders/draft/videos/what-is-an-mcp.mp4`
- `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/video-renders/draft/review/what-is-an-mcp-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/video-renders/draft/review/what-is-an-mcp-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-an-mcp/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- MCP stands for Model Context Protocol.
- MCP is an open standard for connecting AI clients to external systems such as tools, resources, and prompts.
- MCP gives clients and servers a shared protocol instead of requiring one custom integration per assistant.
- An MCP server can expose tools, resources, and prompts.
- MCP is supported across major clients including Claude, ChatGPT-related ecosystems, VS Code, and GitHub Copilot.
- Authentication and authorization matter because MCP can expose real systems.
- Registries, allowlists, and approval policies help govern MCP access.
- MCP can affect cost because tool discovery, tool descriptions, tool calls, and downstream APIs add context or external spend.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: MCP is an open standard for connecting AI applications to external systems.
- 0:15-0:30: A shared protocol replaces one custom integration per assistant.
- 0:30-0:45: MCP servers expose tools, resources, and prompts for data, actions, and workflows.
- 0:45-1:00: Major clients connect to the same bus through neutral protocol ports.
- 1:00-1:15: Authentication and authorization gate real downstream systems.
- 1:15-1:30: Registries, allowlists, and approval policies control which servers and writes are allowed.
- 1:30-1:45: Tool discovery and tool calls add context pressure and downstream API cost.
- 1:45-2:00: Define MCP as standard plumbing with strict permissions and narrow tool design.

Preserve these visual anchors:

- MCP bus
- messy point-to-point integrations becoming one protocol bus
- tools resources prompts lanes
- neutral client cards
- lock icons on bus
- registry gate
- approval shield
- context meter and external billing icons

Preserve these system labels:

- Client
- MCP bus
- Tools
- Resources
- Prompts
- Auth
- Registry
- Approval
- Downstream API
- Cost/context
- Read data
- Execute action
- Structured workflow
- Least privilege

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-an-mcp/`; do not write into the copied skill directory.
