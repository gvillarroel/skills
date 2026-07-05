# Run now without asking questions or listing directories: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/risk-bowtie-video/artifacts/reviews/prompt-contract-build.json`.

# Isolated HTML Video Validation Prompt: Risk Bowtie Scaffold

Read this prompt first. Then run this exact command from the isolated workspace root:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/risk-bowtie-video/artifacts/reviews/prompt-contract-build.json
```

Do not inspect helper source before running the command. The command must create and validate the exact requested paths below.

Required exact outputs:

- `projects/risk-bowtie-video/source/source-package.json`
- `projects/risk-bowtie-video/source/production-notes.md`
- `projects/risk-bowtie-video/src/index.html`
- `projects/risk-bowtie-video/src/render.mjs`
- `projects/risk-bowtie-video/artifacts/video-renders/draft/videos/risk-bowtie-explainer.mp4`
- `projects/risk-bowtie-video/artifacts/video-renders/draft/review/risk-bowtie-explainer-contact-sheet.jpg`
- `projects/risk-bowtie-video/artifacts/video-renders/draft/review/risk-bowtie-explainer-contact-sheet.json`
- `projects/risk-bowtie-video/artifacts/reviews/self-review.md`
- `projects/risk-bowtie-video/artifacts/reviews/prompt-contract-build.json`

Browser render-state output:

- `projects/risk-bowtie-video/artifacts/reviews/render-state-check.json`

Topic: Control assurance risk bowtie validation

Video title: Risk Bowtie Explainer

Checked date: July 4, 2026

## Visual pattern

Use the `risk-bowtie` scaffold.

Format: Use 12 seconds, 12 fps, and 1280x720.

## Preserve these source facts

- A risk bowtie video should separate threats from consequences with a visible top event.
- Preventive barriers belong before the top event; mitigative barriers belong after it.
- Degraded controls should stay visible so the viewer can see the assurance gap.
- Repair action should target the weakest barrier rather than only labeling the consequence.
- Validation must prove threat progression, barrier labels, consequences, degraded control, and final repair action state.

## Preserve these visual anchors

- threat set
- preventive barriers
- top event
- mitigative barriers
- consequence set
- degraded barrier
- residual risk meter
- repair action

## Preserve these threat labels

- unsafe input
- missing review
- stale policy
- overloaded owner

## Preserve these barrier labels

- detect drift
- validate policy
- isolate change
- contain blast radius
- recover service
- learn control gap

## Preserve these consequence labels

- quality escape
- customer impact
- compliance exposure
- recovery cost

## Required semantic validation

The wrapper report and browser render-state report must prove:

- `visualPattern=risk-bowtie`
- final `activeThreatCount=4`
- final `visibleMechanismCount=7`
- `activeThreatCount` is nondecreasing
- `visibleMechanismCount` is nondecreasing
- preventive, top-event, mitigative, consequence, degraded, and action states transition from `false` to `true`
- at least three distinct `activeThreatCount` values
- at least five distinct `visibleMechanismCount` values
- `threatLabels` contains `unsafe input` and `overloaded owner`
- `barrierLabels` contains `detect drift` and `learn control gap`
- `consequenceLabels` contains `quality escape` and `recovery cost`

After the command completes, verify the wrapper report, contact-sheet manifest, and render-state report. If any exact output path is missing or any report does not pass, fix the generated project outputs and rerun validation.
