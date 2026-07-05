First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-a-harness-hook/src/index.html --source-package projects/metro-ai-concept-videos/what-is-a-harness-hook/source/source-package.json --output projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `state-machine` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is a Harness Hook.
Video title: What is a Harness Hook.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette or colorset2 unless production notes justify why hook lifecycle states cannot be distinguished with red, neutral, white, black, and gray.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-a-harness-hook/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/src/index.html`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/video-renders/draft/videos/what-is-a-harness-hook.mp4`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/video-renders/draft/review/what-is-a-harness-hook-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/video-renders/draft/review/what-is-a-harness-hook-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-a-harness-hook/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A harness hook is an active interception point in the runtime lifecycle.
- Hooks run custom logic when an important runtime event occurs.
- Hooks are active guardrails because they run during execution, not only before a session begins.
- GitHub Copilot hooks can execute external commands at lifecycle points like session start, prompt submit, tool calls, and agent stop.
- Claude Code hooks can be shell commands, HTTP endpoints, or LLM prompts.
- OpenCode exposes comparable event-driven control through plugin events.
- Typical hook jobs include formatting, validation, secret protection, audit logging, notifications, and narrowing huge data before the model sees it.
- Hooks can lower cost by preprocessing and shrinking context, but they can raise latency or cost if they trigger slow services too often.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: A pulse enters an event timeline and activates runtime interception points.
- 0:15-0:30: The timeline overlays a shield gate to show hooks as active guardrails during execution.
- 0:30-0:45: GitHub-style lifecycle badges appear for session start, prompt submit, tool calls, and agent stop.
- 0:45-1:00: Claude-style hook targets expand as shell command, HTTP endpoint, and LLM prompt branches.
- 1:00-1:15: OpenCode-style plugin events animate before and after tool execution.
- 1:15-1:30: Hook jobs cascade as formatting, validation, secret protection, audit logging, notifications, and preprocessing.
- 1:30-1:45: A cost and latency slider shows context shrinking on one side and slow over-triggering on the other.
- 1:45-2:00: The state machine resolves to clear lifecycle boundaries for enforcement and preprocessing.

Preserve these visual anchors:

- event timeline
- lifecycle pulse
- shield gate overlay
- pre-tool checkpoint
- post-tool checkpoint
- permission request
- session start
- agent stop
- command block
- context shrinking counter
- cost versus latency slider

Preserve these state labels:

- Event
- Precheck
- Command
- Result
- Postcheck

Preserve these guard labels:

- Policy
- Pre-hook
- Post-hook
- Allow
- Ask
- Deny
- Session start
- Prompt submit
- Tool call
- Agent stop
- Audit log
- Context filter

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-a-harness-hook/`; do not write into the copied skill directory.
