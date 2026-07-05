Create a complete standalone HTML video package for a Metro Minimal Tonal Motion systems-flow explainer. First action: read `../prompt.md` directly with the file-reading tool, not a shell command. Run the prompt-contract wrapper path; do not inspect helper script source.

Use this exact command after reading the prompt:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-square-composition-validation/artifacts/reviews/prompt-contract-build.json --metro-style-manifest projects/metro-square-composition-validation/artifacts/reviews/metro-style-audit.json --metro-composition-manifest projects/metro-square-composition-validation/artifacts/reviews/metro-composition-audit.json
```

Do not ask clarifying questions, do not run directory listings or shell probes before reading the prompt, and do not write into the copied skill directory. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash.

Required exact video package outputs:

- `projects/metro-square-composition-validation/source/source-package.json`
- `projects/metro-square-composition-validation/source/production-notes.md`
- `projects/metro-square-composition-validation/src/index.html`
- `projects/metro-square-composition-validation/src/render.mjs`
- `projects/metro-square-composition-validation/artifacts/video-renders/draft/videos/metro-square-composition.mp4`
- `projects/metro-square-composition-validation/artifacts/video-renders/draft/review/metro-square-composition-contact-sheet.jpg`
- `projects/metro-square-composition-validation/artifacts/video-renders/draft/review/metro-square-composition-contact-sheet.json`
- `projects/metro-square-composition-validation/artifacts/reviews/self-review.md`

Required exact validation outputs:

- `projects/metro-square-composition-validation/artifacts/reviews/prompt-contract-build.json`
- `projects/metro-square-composition-validation/artifacts/reviews/render-state-check.json`
- `projects/metro-square-composition-validation/artifacts/reviews/metro-style-audit.json`
- `projects/metro-square-composition-validation/artifacts/reviews/metro-composition-audit.json`

Topic: aligned queue pressure and retry control in an event pipeline.

Video title: Metro Square Composition Validation.

Checked date: July 4, 2026.

Use the `systems-flow` scaffold.

Style constraints:

- Metro Minimal Tonal Motion.
- Use colorset1 only unless the audit requires a reasoned exception.
- Use square, hard-edge, 0-radius panels and masks.
- Align major rectangles to a 4 px grid with shared baselines.
- Do not render rounded cards, pills, soft panels, title bands, checked-date bands, draft/scaffold labels, progress rails, or decorative UI chrome.

Preserve these source facts:

- Three event sources enter one intake contract.
- Queue pressure is the visible bottleneck before worker saturation.
- Retry policy must branch separately from dead-letter inspection.
- Feedback throttle reduces intake only after queue pressure rises.
- The final state must show output continuing after throttling.

Preserve these visual anchors:

- square intake cells
- event bus
- bounded queue
- worker pool
- retry branch
- dead-letter branch
- feedback throttle gate
- output stream

Preserve these system components:

- source A
- source B
- source C
- event bus
- bounded queue
- worker pool
- output stream
- retry control
- dead-letter inspection
- queue pressure metric
- feedback throttle gate

Use 6 seconds, 6 fps, and 1280x720.
