First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-a-harness/src/index.html --source-package projects/metro-ai-concept-videos/what-is-a-harness/source/source-package.json --output projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `layered-architecture` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is a Harness.
Video title: What is a Harness.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette or colorset2 unless production notes justify why harness layers cannot be distinguished with red, neutral, white, black, and gray.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-a-harness/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-a-harness/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-a-harness/src/index.html`
- `projects/metro-ai-concept-videos/what-is-a-harness/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/video-renders/draft/videos/what-is-a-harness.mp4`
- `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/video-renders/draft/review/what-is-a-harness-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/video-renders/draft/review/what-is-a-harness-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-a-harness/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A harness is the runtime wrapper that turns a raw model into a usable assistant or agent.
- A harness defines instruction layers, default tools, permissions, model picker, execution loop, approvals, memory behavior, logging, and extensibility surface.
- The model is like the engine; the harness provides steering, brakes, dashboard, and controls.
- Different harnesses feel different even when they can call the same model.
- GitHub Copilot emphasizes GitHub-native workflows and explicit AI-credit accounting.
- Claude Code emphasizes skills, hooks, MCP, and coding autonomy.
- OpenCode emphasizes openness and provider choice.
- Harness defaults affect quality, latency, cost, and risk because they change tools, context, retries, and autonomous loops.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: A comparison grid zooms into a single runtime stack around the model.
- 0:15-0:30: The model engine gains steering, brakes, dashboard, and controls from the harness.
- 0:30-0:45: Instruction layers, tools, permissions, memory, approvals, loop logic, and logging assemble as a stack.
- 0:45-1:00: The same model badge drops into three different harness shells and produces different behavior.
- 1:00-1:15: Copilot, Claude Code, and OpenCode cards show different workflow defaults.
- 1:15-1:30: Tool count, context size, retries, and autonomous loops drive a rising cost meter.
- 1:30-1:45: Feature count fades behind workflow fit, controls, and budget constraints.
- 1:45-2:00: The selection path highlights the harness layers a team should customize first.

Preserve these visual anchors:

- comparison grid
- runtime stack
- model engine
- steering controls
- instruction layers
- default tools
- permission gate
- approval control
- logging surface
- cost meter
- use-case matrix

Preserve these layer labels:

- User
- Instructions
- Model
- Tools
- Files / shell
- Approvals

Preserve these concern labels:

- Logging
- Memory rules
- Execution loop
- Permissions
- GitHub workflow
- Skills / hooks / MCP
- Provider choice
- Cost and risk

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-a-harness/`; do not write into the copied skill directory.
