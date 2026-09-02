# <Title>

Promise: <one-sentence viewer promise>

Audience: <specific viewer and prior knowledge>

Format: <video form and pacing>

Runtime: <M:SS or seconds>

Output: <exact width>x<exact height> at <fps> fps

## Source Contract

- Facts and anchors:
- Required output paths:
- Source links and rights:
- Constraints and omissions:

## Timed Beat Table

| Time | Beat ID | Scene ID | Script purpose | Specialist assets | Composition | Interaction | Transition | Audio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0:00-0:05 | b01 | s01 | <purpose> | <producer and artifact> | <focal layout> | <ports/state/event> | <handoff> | <cue> |

## Producer Routes

| Asset ID | Producer skill | Output path | Ports/states | Validation report |
| --- | --- | --- | --- | --- |
| <asset-id> | <skill> | <project-relative path> | <semantic contract> | <passing JSON report> |

## Scene Composition

- Canvas, ratio, and safe areas:
- Element bounds and z-order:
- Crop/fit rules:
- Shared state and master clock:
- Cross-element interactions:
- Reduced-motion or static-state behavior:

## Voiceover Draft

- 0:00-0:05: <one spoken line>

## Audio

- Voiceover:
- Music bed and ducking:
- SFX and transition cues:

## Validation

```powershell
uv run --script $env:VIDEO_SKILL/scripts/check_video_brief.py path/to/brief.md --require-voiceover --json
uv run --script $env:VIDEO_SKILL/scripts/validate_scene_contract.py source/scene-contract.json --project-root . --require-files --require-hashes --require-producer-reports --json
uv run --script $env:VIDEO_SKILL/scripts/build_composite_scene.py source/scene-contract.json src/index.html --project-root . --require-producer-reports --force --json
uv run --script $env:VIDEO_SKILL/scripts/render_concept_video.py src/index.html artifacts/videos/final.mp4 --duration <seconds> --fps <fps> --width <width> --height <height> --force --json
uv run --script $env:VIDEO_SKILL/scripts/check_video_artifact.py artifacts/videos/final.mp4 --expect-width <width> --expect-height <height> --expect-fps <fps> --expect-duration <seconds> --json
```
