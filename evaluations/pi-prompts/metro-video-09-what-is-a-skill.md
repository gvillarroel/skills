First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-a-skill/src/index.html --source-package projects/metro-ai-concept-videos/what-is-a-skill/source/source-package.json --output projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `dependency-map` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is a Skill.
Video title: What is a Skill.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the concept cannot be distinguished with red, neutral, white, black, and gray. If any color set 2 color is used, document the strict reason in production notes.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-a-skill/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-a-skill/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-a-skill/src/index.html`
- `projects/metro-ai-concept-videos/what-is-a-skill/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/video-renders/draft/videos/what-is-a-skill.mp4`
- `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/video-renders/draft/review/what-is-a-skill-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/video-renders/draft/review/what-is-a-skill-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-a-skill/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A skill is a reusable capability package for specialized tasks.
- A skill gives the harness structured instructions, scripts, and supporting resources.
- Skills support progressive disclosure because they load when relevant instead of forcing long procedures into every prompt.
- GitHub Copilot describes skills as folders of instructions, scripts, and resources.
- Claude Code says long reference material in a skill costs almost nothing until it is needed.
- OpenCode loads SKILL.md-based skills on demand.
- Skills are useful for deploy checklists, debugging routines, architecture explainers, onboarding flows, and codebase maps.
- The common mistake is making a skill too broad, verbose, or always relevant.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: A skill is a reusable task package that gives the assistant a named specialized workflow.
- 0:15-0:30: Good skills are not giant permanent prompts; they are loaded only when relevant.
- 0:30-0:45: GitHub, Claude, and OpenCode use similar instruction and SKILL.md-based package patterns.
- 0:45-1:00: Progressive disclosure keeps rich procedures available while avoiding constant token cost.
- 1:00-1:15: Skills fit recurring deploy, debugging, architecture, onboarding, and codebase-map workflows.
- 1:15-1:30: A skill can include scripts and approved tool instructions for repeatability and safety.
- 1:30-1:45: The failure mode is a bloated mini novel; keep the workflow sharp, scoped, and reusable.
- 1:45-2:00: Define a skill as on-demand domain expertise for the harness.

Preserve these visual anchors:

- skill card stack
- long prompt wall shrinking into one skill card
- compatible folder structures
- cost meter staying flat until activation
- example skill cards
- tool badges snapping onto the skill card
- bloated card being trimmed down
- progressive disclosure callout

Preserve these dependency labels:

- Trigger
- SKILL.md
- References
- Scripts
- Assets

Preserve these cluster labels:

- Progressive disclosure
- Validation
- Tool instructions
- Runtime load
- Reusable workflow
- Scope boundary
- Cost control

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-a-skill/`; do not write into the copied skill directory.
