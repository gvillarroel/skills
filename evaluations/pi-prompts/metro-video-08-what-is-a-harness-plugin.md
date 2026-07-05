First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-a-harness-plugin/src/index.html --source-package projects/metro-ai-concept-videos/what-is-a-harness-plugin/source/source-package.json --output projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `layered-architecture` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is a Harness Plugin.
Video title: What is a Harness Plugin.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the concept cannot be distinguished with red, neutral, white, black, and gray. If any color set 2 color is used, document the strict reason in production notes.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/src/index.html`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/video-renders/draft/videos/what-is-a-harness-plugin.mp4`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/video-renders/draft/review/what-is-a-harness-plugin-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/video-renders/draft/review/what-is-a-harness-plugin-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-a-harness-plugin/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A harness plugin is a distribution mechanism for reusable harness customization.
- The exact packaging differs by product, but the common pattern is to bundle runtime capabilities for install, sharing, versioning, and governance.
- GitHub Copilot CLI plugins can bundle agents, skills, hooks, and MCP configuration.
- Claude Code plugins can bundle skills, agents, hooks, and MCP servers from marketplaces.
- OpenCode plugins are JavaScript or TypeScript modules loaded locally or from npm to add hooks, tools, and integrations.
- Plugins package multiple runtime behaviors into one installable unit.
- Distribution is governance: plugins standardize the approved way to work across a team.
- Plugins can lower cost with efficient defaults or raise cost by injecting noisy context and expensive tool calls everywhere.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: A harness plugin packages and shares runtime customization as one reusable installed unit.
- 0:15-0:30: The bundle usually contains behavior: skills, hooks, MCP config, special agents, or custom tools.
- 0:30-0:45: GitHub Copilot CLI plugins support reusable agents, skills, hooks, and MCP server configuration.
- 0:45-1:00: Claude Code plugins package skills, agents, hooks, and MCP servers with marketplace and allowlist controls.
- 1:00-1:15: OpenCode plugins are JS or TS modules that subscribe to events and extend behavior.
- 1:15-1:30: Distribution becomes governance when teams install the approved shared way to work.
- 1:30-1:45: Efficient plugins can reduce repeated prompts; noisy plugins can increase context and tool-call costs.
- 1:45-2:00: Define a plugin as packaged harness behavior, policy, and integrations.

Preserve these visual anchors:

- plugin bundle cube
- detachable module blocks
- GitHub plugin manifest card
- Claude marketplace allowlist gate
- OpenCode npm module
- versioning and upgrade arrows
- good plugin versus noisy plugin split
- team-wide install lane

Preserve these layer labels:

- Plugin bundle
- Skills
- Tools
- Apps/connectors
- Hooks
- MCP config
- Agent profile

Preserve these concern labels:

- Policy
- Marketplace
- Install/update
- Versioning
- Governance
- Context cost

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-a-harness-plugin/`; do not write into the copied skill directory.
