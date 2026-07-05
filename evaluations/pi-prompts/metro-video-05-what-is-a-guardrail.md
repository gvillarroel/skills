First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-a-guardrail/src/index.html --source-package projects/metro-ai-concept-videos/what-is-a-guardrail/source/source-package.json --output projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `risk-bowtie` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is a Guardrail.
Video title: What is a Guardrail.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette or colorset2 unless production notes justify why the guardrail risk states cannot be distinguished with red, neutral, white, black, and gray.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-a-guardrail/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/src/index.html`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/video-renders/draft/videos/what-is-a-guardrail.mp4`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/video-renders/draft/review/what-is-a-guardrail-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/video-renders/draft/review/what-is-a-guardrail-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-a-guardrail/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A guardrail is a control layer around an agent, input, output, or tool action.
- A guardrail decides whether a task should proceed, pause, be changed, or stop.
- Guardrails can inspect user prompts, model outputs, and tool calls.
- Guardrail actions include block, redact, route, and escalate.
- A prompt suggests behavior, while a guardrail enforces a policy.
- Google Model Armor can screen prompts and responses for prompt injection, jailbreaks, sensitive data, malicious URLs, and related risks.
- OpenAI-style guidance uses automatic checks plus human review before sensitive or high-impact work continues.
- For code assistants, common guardrails protect secrets, production systems, and destructive commands.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: A guardrail closes around the agent loop and decides whether work should proceed.
- 0:15-0:30: Input, output, and action gates inspect prompts, generated text, and tool calls.
- 0:30-0:45: The prompt bubble remains advisory while the policy gate becomes an enforceable barrier.
- 0:45-1:00: Model Armor-style filters fan out for prompt injection, jailbreak, sensitive data, and malicious URL risks.
- 1:00-1:15: Automatic checks run first, then a human approval step pauses risky work before continuation.
- 1:15-1:30: Code-assistant guardrails light up around secrets, destructive commands, and production deploys.
- 1:30-1:45: The bowtie shows reduced residual risk on one side and false-positive friction on the other.
- 1:45-2:00: The system resolves to enforceable policy checks over input, output, and actions.

Preserve these visual anchors:

- shield gate around agent loop
- input gate
- output gate
- action gate
- prompt bubble versus hard gate
- Model Armor filter fan-out
- human approval control
- secrets and destructive command warnings
- safety versus friction balance
- residual risk block

Preserve these threat labels:

- Unsafe request
- Prompt injection
- Sensitive data
- Destructive command

Preserve these barrier labels:

- Preventive barrier
- Policy gate
- Top event
- Allow
- Block
- Redact
- Escalate
- Human approval
- Mitigative barrier

Preserve these consequence labels:

- Consequence
- False positive friction
- Residual risk

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-a-guardrail/`; do not write into the copied skill directory.
