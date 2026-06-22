# Scene Pattern Recipes

Use this reference when preserving an approved HTML+D3+Anime.js scene pattern from `examples/ai-concept-videos` or adapting one into a new concept video.

## Approved Pattern Capture

When a scene works, store the transferable part in the skill before starting the next unrelated beat.

- Name the pattern and source file.
- State the mechanic it explains.
- Identify which shapes, colors, and motions have fixed semantic roles.
- Extract repeated marks into shared helpers when they will appear in more than one beat.
- Keep generated videos and raw frames in `output/`, not in the skill or example source.

## Shared Model Box

Source helper: `examples/ai-concept-videos/scenes/llm-model-box.js`.

Use when a model, grader, evaluator, or processor should appear as the same visual object across beats.

- Keep box geometry, border, label placement, and internal activation consistent.
- Keep the primary label centered and the internal MLP secondary.
- Animate the internal mechanism instead of adding generic glow.
- Draw incoming or outgoing tokens below the box layer so the box occludes tokens until they cross its boundary.
- Use the helper from each beat instead of locally redrawing the model box.

## Beat Module Split

Source pattern: `examples/ai-concept-videos/scenes/evaluation.js` plus one file per beat and `evaluation-shared.js`.

Use when a concept needs different visual metaphors across hook, definition, mechanism, handoff, and implication beats.

- Keep one dispatcher that selects the beat renderer from `beat.id`.
- Keep reusable data, timing helpers, labels, model boxes, cards, and motion primitives in a shared module.
- Keep each beat file deterministic from `seconds`, `sceneProgress`, and the passed context.
- Return no wall-clock animation state from beat modules.
- Prefer this split before a renderer file grows into many unrelated subscenes.

## Generic Visual Renderer Gate

Source pattern: `examples/ai-concept-videos/scenes/generic-visuals.js`.

Use the generic renderer only when the new concept shares the same mechanic as the existing pattern.

- Reuse shared palette, row, core, matrix, and ambient-flow helpers only when their semantic roles still match.
- Do not use ambient motion as decoration. Moving packets or lanes must represent transfer, pressure, routing, or accumulation.
- If the concept needs a different causal model, create a dedicated beat module instead.

## Cost And Pricing Handoff

Source patterns: LLM billing handoff and implication scenes.

Use when the video needs current pricing or cost comparison without making moving numbers unreadable.

- Keep precise numbers in fixed secondary panels aligned to a table, scorecard, or ledger.
- Let meters, ticks, accumulated blocks, or ranked bars show the mechanic.
- Keep model-entering and model-exiting flows below the model box so enclosure is visible.
- Recheck pricing and product claims from primary sources and record checked dates in the data model.
- Avoid attaching exact prices to moving dots unless the dot itself is the cost object.

## Evaluation Scene Pattern

Source pattern: `examples/ai-concept-videos/scenes/evaluation-*.js`.

Use when the concept is evaluation, grading, pass/fail, pass@k, or benchmark comparison.

- Show evals as datasets plus graders plus measured outcomes.
- Use grids, scorecards, pass/fail traces, or bucketed results before adding explanatory labels.
- Preserve object identity through the loop: prompt/task, candidate output, grader, score, and aggregate result.
- Keep pass-rate or cost charts in stable panels so the viewer can compare endpoints.

## Render Presets

Source script: `examples/ai-concept-videos/scripts/render-videos.mjs`.

Use explicit presets instead of editing capture settings ad hoc:

- `quick`: storyboard timing only.
- `draft`: visual-shape iteration.
- `motion`: timing/stutter review at 30 fps.
- `fast`: near-final segment preview without slow encoding or contact sheets.
- `final`: approved delivery render with review artifacts.

Render only the changed time range with `--start` and `--duration` unless shared helpers changed across the full video.

## Validation Checklist

For scene-pattern changes:

- Run the concept content validator.
- Smoke-test representative concepts through `window.renderConceptFrame(conceptId, seconds, { capture: true })`.
- Render a short segment with the cheapest preset that still exercises the changed path.
- Rebuild Pages when the example source changed.
- Verify that no MP4/WebM/raw frames are staged.
