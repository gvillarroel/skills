# Run now without asking questions or listing directories: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/scenario-tree-video/artifacts/reviews/prompt-contract-build.json`.

# Isolated HTML Video Validation Prompt: Scenario Tree Scaffold

Read this prompt first. Then run this exact command from the isolated workspace root:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/scenario-tree-video/artifacts/reviews/prompt-contract-build.json
```

Do not inspect helper source before running the command. The command must create and validate the exact requested paths below.

Required exact outputs:

- `projects/scenario-tree-video/source/source-package.json`
- `projects/scenario-tree-video/source/production-notes.md`
- `projects/scenario-tree-video/src/index.html`
- `projects/scenario-tree-video/src/render.mjs`
- `projects/scenario-tree-video/artifacts/video-renders/draft/videos/scenario-tree-explainer.mp4`
- `projects/scenario-tree-video/artifacts/video-renders/draft/review/scenario-tree-explainer-contact-sheet.jpg`
- `projects/scenario-tree-video/artifacts/video-renders/draft/review/scenario-tree-explainer-contact-sheet.json`
- `projects/scenario-tree-video/artifacts/reviews/self-review.md`
- `projects/scenario-tree-video/artifacts/reviews/prompt-contract-build.json`

Browser render-state output:

- `projects/scenario-tree-video/artifacts/reviews/render-state-check.json`

Topic: Branching scenario strategy validation

Video title: Scenario Tree Explainer

Checked date: July 4, 2026

## Visual pattern

Use the `scenario-tree` scaffold.

Format: Use 12 seconds, 12 fps, and 1280x720.

## Preserve these source facts

- A scenario-tree video should start from one decision point and then branch into plausible futures.
- Probability or evidence labels should appear before the decision gate.
- Risk and upside branches need separate visible routes so the outcome is not a static recommendation.
- A fallback route should stay visible as a real alternative, not only a caveat.
- Validation must prove scenario progression, probability labels, fallback, decision gate, and selected outcome state.

## Preserve these visual anchors

- decision point
- scenario branches
- probability labels
- evidence weight
- upside branch
- risk branch
- fallback route
- selected outcome

## Preserve these scenario labels

- choose scope
- base adoption
- accelerated adoption
- delayed adoption
- stable delivery
- expansion outcome
- fallback outcome

## Preserve these probability labels

- 55 percent base
- 25 percent upside
- 20 percent downside
- fallback reserve

## Required semantic validation

The wrapper report and browser render-state report must prove:

- `visualPattern=scenario-tree`
- final `activeScenarioCount=7`
- final `visibleMechanismCount=7`
- `activeScenarioCount` is nondecreasing
- `visibleMechanismCount` is nondecreasing
- probability, risk, upside, decision, fallback, and outcome states transition from `false` to `true`
- at least four distinct `activeScenarioCount` values
- at least five distinct `visibleMechanismCount` values
- `scenarioLabels` contains `choose scope` and `fallback outcome`
- `probabilityLabels` contains `55 percent base` and `fallback reserve`

After the command completes, verify the wrapper report, contact-sheet manifest, and render-state report. If any exact output path is missing or any report does not pass, fix the generated project outputs and rerun validation.
