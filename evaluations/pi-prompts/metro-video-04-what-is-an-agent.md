First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root, in order. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-an-agent/src/index.html --source-package projects/metro-ai-concept-videos/what-is-an-agent/source/source-package.json --output projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `state-machine` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is an Agent.
Video title: What is an Agent.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, guard labels, tool labels, or environment blocks.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the production notes justify why the red, neutral, white, black, and gray palette cannot distinguish the required states.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-an-agent/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-an-agent/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-an-agent/src/index.html`
- `projects/metro-ai-concept-videos/what-is-an-agent/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/video-renders/draft/videos/what-is-an-agent.mp4`
- `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/video-renders/draft/review/what-is-an-agent-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/video-renders/draft/review/what-is-an-agent-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-an-agent/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- An agentic system combines a model with tools, state or memory, and orchestration.
- An agent does more than answer once: it can observe context, take actions, inspect results, and continue in a loop.
- A minimal teaching decomposition is context, environment, actions, and a loop or policy.
- Context can include chat history, files, instructions, memory, and tool outputs.
- Environment is the system the agent can inspect or affect, such as a repo, terminal, browser, ticket system, docs, or database.
- Actions can include reading files, running tests, searching docs, calling APIs, or asking for approval.
- The loop or policy decides whether to keep exploring, execute a tool, or stop.
- A workflow follows predefined steps, while an agent adapts based on what it finds.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: Show an agent loop that observes context, acts, checks results, and continues.
- 0:15-0:30: Build the four minimum pieces: context, environment, actions, and policy.
- 0:30-0:45: Fill the context state with chat history, files, instructions, memory, and tool outputs.
- 0:45-1:00: Transform the environment surface through repo, terminal, browser, ticket system, docs, and database.
- 1:00-1:15: Animate allowed actions around the loop: read files, run tests, search docs, call APIs, and ask approval.
- 1:15-1:30: Pause at the policy fork where the runtime chooses explore, execute tool, or stop.
- 1:30-1:45: Contrast a fixed workflow lane with an adaptive agent loop.
- 1:45-2:00: End on the state-machine recap: model, tools, state, and loop.

Preserve these visual anchors:

- agent loop ring
- Observe / Act / Check / Continue loop
- four labeled component cards
- stacked context panes
- environment blocks for repo, terminal, browser, tickets, docs, and database
- tool icons around the loop
- policy decision fork
- fixed workflow lane
- adaptive agent lane
- final Model + Tools + State + Loop badge

Preserve these state labels:

- observe
- context
- action
- check
- continue
- stop

Preserve these guard labels:

- tool permission
- state memory
- environment result

The state-machine render-state check must prove `visualPattern=state-machine`, preserved state labels, preserved guard labels, final active-state progression, monotonic active-state or mechanism progression, and visible observe, context, action, check, continue, permission, memory, environment result, and stop mechanics across the full 120 seconds.

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-an-agent/`; do not write into the copied skill directory.
