First action: read this prompt at `../prompt.md`. Then run the two exact commands below, in order. Do not list directories, do not read helper source, do not ask questions, and do not stop after the first command.

Command 1:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/render-state-check-video/artifacts/reviews/prompt-contract-build.json
```

Command 2:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/check_html_render_state.py --html projects/render-state-check-video/src/index.html --video-id render-state-check --duration 12 --samples 6 --width 1280 --height 720 --manifest projects/render-state-check-video/artifacts/reviews/render-state-check.json --expect-state visualPattern=phase-timeline --expect-state riskVisible=true --expect-state gateVisible=true --expect-state handoffVisible=true --expect-state finalVisible=true --min-distinct-state activePhase=4 --min-distinct-state visibleMechanismCount=4
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer scaffold and then validate its browser render state.

Use the `phase-timeline` scaffold.

Required exact scaffold outputs:

- `projects/render-state-check-video/source/source-package.json`
- `projects/render-state-check-video/source/production-notes.md`
- `projects/render-state-check-video/src/index.html`
- `projects/render-state-check-video/src/render.mjs`
- `projects/render-state-check-video/artifacts/video-renders/draft/videos/render-state-check.mp4`
- `projects/render-state-check-video/artifacts/video-renders/draft/review/render-state-check-contact-sheet.jpg`
- `projects/render-state-check-video/artifacts/video-renders/draft/review/render-state-check-contact-sheet.json`
- `projects/render-state-check-video/artifacts/reviews/self-review.md`
- `projects/render-state-check-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output after Command 2:

- `projects/render-state-check-video/artifacts/reviews/render-state-check.json`

Topic: staged validation loop for improving video-generation skills.

Video title: Render-State Gate For Skill Video Iteration

Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.

Preserve these source facts:

- The loop starts from a prompt contract, not from a title-derived filename.
- The scaffold must expose `window.renderConceptFrame`.
- A fast browser-state check should run before a full browser MP4 recapture.
- The state check must prove late mechanisms, not only early motion.
- Passing validation requires exact requested paths plus no missing source anchors.

Preserve these visual anchors:

- prompt contract intake
- phase timeline
- browser render state
- late mechanism reveal
- validation report
- skill improvement loop

Preserve these timeline phases:

- prompt contract
- source package
- scaffold render
- browser state
- critique pass
- skill update
