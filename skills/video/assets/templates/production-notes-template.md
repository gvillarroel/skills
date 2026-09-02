# <Project Title> Production Notes

## Output Contract

- Scene contract:
- Renderer:
- Final MP4:
- Width:
- Height:
- Aspect ratio:
- FPS:
- Duration:
- Audio source:

## Specialist Assets

| Asset ID | Producer skill | Artifact | Producer report | Hash |
| --- | --- | --- | --- | --- |
| <asset-id> | <skill> | <path> | <path> | <sha256> |

## Composition And Interaction

- Element placement and z-order:
- Named ports:
- Shared events and states:
- Interaction windows:
- GIF synchronization mode:
- Transition continuity:
- Known constraints:

## Validation Evidence

- Scene-contract report:
- Renderer-contract report:
- Render-state report:
- Contact sheet:
- Motion report:
- Quality report:
- Video-artifact report:
- Muted-playback review:

## Commands

Command working directory: project root.

```powershell
uv run --script {{SKILL_PATH}}/scripts/validate_scene_contract.py source/scene-contract.json --project-root . --require-files --require-hashes --require-producer-reports --output artifacts/reviews/scene-contract.json --json
uv run --script {{SKILL_PATH}}/scripts/build_composite_scene.py source/scene-contract.json src/index.html --project-root . --require-producer-reports --report artifacts/reviews/compositor-build.json --force --json
uv run --script {{SKILL_PATH}}/scripts/check_renderer_contract.py src/index.html --duration <seconds> --width <width> --height <height> --output artifacts/reviews/renderer-contract.json --json
uv run --script {{SKILL_PATH}}/scripts/render_concept_video.py src/index.html artifacts/videos/final.mp4 --duration <seconds> --fps <fps> --width <width> --height <height> --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --json
uv run --script {{SKILL_PATH}}/scripts/check_video_artifact.py artifacts/videos/final.mp4 --expect-width <width> --expect-height <height> --expect-fps <fps> --expect-duration <seconds> --duration-tolerance 0.1 --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
```

## Final Review

- Exact dimensions and duration verified:
- All specialist assets visibly bound:
- Port alignment and connector continuity verified:
- Cross-element state changes verified:
- GIF/video timing deterministic:
- No clipping, overlap, illegible text, or unsafe crop:
- Muted scene remains understandable:
- Final audio is intentional and synchronized:
