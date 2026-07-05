# Run now without asking questions or listing directories: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/swimlane-handoff-video/artifacts/reviews/prompt-contract-build.json`.

# Isolated HTML Video Validation Prompt: Swimlane Handoff Scaffold

Read this prompt first. Then run this exact command from the isolated workspace root:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/swimlane-handoff-video/artifacts/reviews/prompt-contract-build.json
```

Do not inspect helper source before running the command. The command must create and validate the exact requested paths below.

Required exact outputs:

- `projects/swimlane-handoff-video/source/source-package.json`
- `projects/swimlane-handoff-video/source/production-notes.md`
- `projects/swimlane-handoff-video/src/index.html`
- `projects/swimlane-handoff-video/src/render.mjs`
- `projects/swimlane-handoff-video/artifacts/video-renders/draft/videos/swimlane-handoff-explainer.mp4`
- `projects/swimlane-handoff-video/artifacts/video-renders/draft/review/swimlane-handoff-explainer-contact-sheet.jpg`
- `projects/swimlane-handoff-video/artifacts/video-renders/draft/review/swimlane-handoff-explainer-contact-sheet.json`
- `projects/swimlane-handoff-video/artifacts/reviews/self-review.md`
- `projects/swimlane-handoff-video/artifacts/reviews/prompt-contract-build.json`

Browser render-state output:

- `projects/swimlane-handoff-video/artifacts/reviews/render-state-check.json`

Topic: Cross-team workflow handoff validation

Video title: Swimlane Handoff Explainer

Checked date: July 4, 2026

## Visual pattern

Use the `swimlane-handoff` scaffold.

Format: Use 12 seconds, 12 fps, and 1280x720.

## Preserve these source facts

- A workflow handoff video should show who owns each step, not only what state the work is in.
- SLA pressure should become visible before approval or completion claims appear.
- Rework needs a visible return route so quality failures are not hidden inside the happy path.
- Escalation should branch from the responsible owner lane instead of appearing as a generic warning.
- Validation must prove handoff progression, owner labels, exception routes, and final completion state.

## Preserve these visual anchors

- owner lanes
- request intake
- handoff path
- SLA pressure
- approval gate
- rework loop
- escalation path
- completion lane

## Preserve these lane labels

- customer request
- operations intake
- quality review
- release owner

## Preserve these handoff labels

- submit request
- triage ticket
- analyze scope
- approve change
- rework finding
- escalate blocker
- release package
- close loop

## Required semantic validation

The wrapper report and browser render-state report must prove:

- `visualPattern=swimlane-handoff`
- final `activeHandoffCount=8`
- final `visibleMechanismCount=6`
- `activeHandoffCount` is nondecreasing
- `visibleMechanismCount` is nondecreasing
- SLA, rework, approval, escalation, and completion states transition from `false` to `true`
- at least four distinct `activeHandoffCount` values
- at least five distinct `visibleMechanismCount` values
- `laneLabels` contains `customer request` and `release owner`
- `handoffLabels` contains `submit request` and `close loop`

After the command completes, verify the wrapper report, contact-sheet manifest, and render-state report. If any exact output path is missing or any report does not pass, fix the generated project outputs and rerun validation.
