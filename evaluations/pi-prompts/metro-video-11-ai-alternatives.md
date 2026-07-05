First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/ai-alternatives/src/index.html --source-package projects/metro-ai-concept-videos/ai-alternatives/source/source-package.json --output projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `comparison-matrix` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: AI alternatives.
Video title: What AI alternatives we have.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the comparison cannot be distinguished with red, neutral, white, black, and gray. If any color set 2 color is used, document the strict reason in production notes.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/ai-alternatives/source/source-package.json`
- `projects/metro-ai-concept-videos/ai-alternatives/source/production-notes.md`
- `projects/metro-ai-concept-videos/ai-alternatives/src/index.html`
- `projects/metro-ai-concept-videos/ai-alternatives/src/render.mjs`
- `projects/metro-ai-concept-videos/ai-alternatives/artifacts/video-renders/draft/videos/ai-alternatives.mp4`
- `projects/metro-ai-concept-videos/ai-alternatives/artifacts/video-renders/draft/review/ai-alternatives-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/ai-alternatives/artifacts/video-renders/draft/review/ai-alternatives-contact-sheet.json`
- `projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/ai-alternatives/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- The named alternatives map to different home bases for AI work.
- Atlassian Rovo is strongest for organizational knowledge across Jira, Confluence, and connected tools.
- Gemini App is a consumer and prosumer assistant with subscription tiers and deep Google ecosystem ties.
- GitHub Copilot is strongest as a coding harness inside developer workflows.
- Claude Desktop and Claude Code are strong for coding and research workflows with connectors, skills, hooks, plugins, and MCP.
- Rovo ships in paid Atlassian cloud subscriptions and Rovo Dev uses a credit model per developer.
- Copilot has Free through Enterprise plans and AI-credit billing.
- Claude blends subscriptions with API-style usage, while Gemini uses plan tiers and region-dependent availability.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: Compare AI assistants by where they live and what work they want to own.
- 0:15-0:30: Rovo lives in organizational knowledge and workflow across Atlassian systems.
- 0:30-0:45: Gemini App is the broad personal assistant option in the Google ecosystem.
- 0:45-1:00: GitHub Copilot is the GitHub-native coding harness across IDE, cloud agent, CLI, review, skills, hooks, and MCP.
- 1:00-1:15: Claude Desktop and Claude Code combine desktop, terminal, connectors, skills, hooks, plugins, and MCP.
- 1:15-1:30: The better selection question is workflow center of gravity, not a single smartest model.
- 1:30-1:45: Cost models differ across Rovo credits, Copilot AI credits, Gemini subscription tiers, and Claude subscriptions plus API usage.
- 1:45-2:00: Choose by workflow home, then add guardrails, permissions, and observability.

Preserve these visual anchors:

- comparison grid
- Atlassian suite knowledge graph feeding Rovo
- Gemini plan cards
- Copilot runtime stack
- Claude desktop to terminal transition
- use-case quadrants
- four cost meters
- choose by workflow gravity selector

Preserve these option labels:

- Rovo
- Gemini App
- GitHub Copilot
- Claude Desktop/Code

Preserve these criterion labels:

- Knowledge home
- Coding workflow
- Extensibility
- Budget model
- Permissions
- Observability
- Workflow gravity
- Plan tiers

If the comparison-matrix helper supports only three options, choose Rovo, GitHub Copilot, and Claude Desktop/Code as the matrix options; preserve Gemini App as a source fact, visual anchor, and side tile.

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/ai-alternatives/`; do not write into the copied skill directory.
