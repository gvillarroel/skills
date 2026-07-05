# Isolated HTML Video Validation Prompt: Sankey Flow Scaffold

Read this prompt first. Then run this exact command from the isolated workspace root:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/sankey-flow-video/artifacts/reviews/prompt-contract-build.json
```

Do not inspect helper source before running the command. The command must create and validate the exact requested paths below.

Required exact outputs:

- `projects/sankey-flow-video/source/source-package.json`
- `projects/sankey-flow-video/source/production-notes.md`
- `projects/sankey-flow-video/src/index.html`
- `projects/sankey-flow-video/src/render.mjs`
- `projects/sankey-flow-video/artifacts/video-renders/draft/videos/sankey-flow-explainer.mp4`
- `projects/sankey-flow-video/artifacts/video-renders/draft/review/sankey-flow-explainer-contact-sheet.jpg`
- `projects/sankey-flow-video/artifacts/video-renders/draft/review/sankey-flow-explainer-contact-sheet.json`
- `projects/sankey-flow-video/artifacts/reviews/self-review.md`
- `projects/sankey-flow-video/artifacts/reviews/prompt-contract-build.json`

Browser render-state output:

- `projects/sankey-flow-video/artifacts/reviews/render-state-check.json`

Topic: Conversion analysis for video skill iteration

Video title: Sankey Flow Explainer

Checked date: July 4, 2026

## Visual pattern

Use the `sankey-flow` scaffold.

Format: Use 12 seconds, 12 fps, and 1280x720.

## Preserve these source facts

- A conversion video should show retained value and lost value as separate branches.
- A split without a labeled loss branch hides why output shrinks.
- Parallel transforms can recombine into one output while preserving separate causes.
- Bottlenecks should appear before the final output is declared ready.
- Validation must prove flow progression, labels, and final output state, not only MP4 existence.

## Preserve these visual anchors

- input stream
- split branch
- loss branch
- transform lanes
- merge point
- bottleneck
- retained value meter
- final output

## Preserve these flow labels

- prompt intake
- accepted facts
- discarded ambiguity
- contract builder
- visual renderer
- merged evidence
- review bottleneck
- validated video

## Required semantic validation

The wrapper report and browser render-state report must prove:

- `visualPattern=sankey-flow`
- final `activeFlowCount=7`
- final `visibleMechanismCount=6`
- `activeFlowCount` is nondecreasing
- `visibleMechanismCount` is nondecreasing
- split, loss, bottleneck, merge, and output states transition from `false` to `true`
- at least four distinct `activeFlowCount` values
- at least five distinct `visibleMechanismCount` values
- `flowLabels` contains `prompt intake` and `validated video`

After the command completes, verify the wrapper report, contact-sheet manifest, and render-state report. If any exact output path is missing or any report does not pass, fix the generated project outputs and rerun validation.
