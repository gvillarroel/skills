# Scene Pattern Recipes

Use this reference when preserving an approved HTML+D3+Anime.js scene pattern from the current project or adapting one into a new concept video. The contracts below are self-contained runtime recipes; do not read the acceptance gallery during normal work.

## Approved Pattern Capture

When a scene works, store the transferable part in the skill before starting the next unrelated beat.

- Name the pattern and source file.
- State the mechanic it explains.
- Identify which shapes, colors, and motions have fixed semantic roles.
- Extract repeated marks into shared helpers when they will appear in more than one beat.
- Keep generated videos and raw frames in `projects/<project-id>/artifacts/`, not in the skill or example source.

## Shared Model Box

Runtime recipe: implement one shared model-box helper with stable geometry, semantic layers, and deterministic animation inputs.

Use when a model, grader, evaluator, or processor should appear as the same visual object across beats.

- Keep box geometry, border, label placement, and internal activation consistent.
- Keep the primary label centered and the internal MLP secondary.
- Animate the internal mechanism instead of adding generic glow.
- Draw incoming or outgoing tokens below the box layer so the box occludes tokens until they cross its boundary.
- Use the helper from each beat instead of locally redrawing the model box.

## Beat Module Split

Runtime recipe: keep one dispatcher, one shared module, and one deterministic module per beat.

Use when a concept needs different visual metaphors across hook, definition, mechanism, handoff, and implication beats.

- Keep one dispatcher that selects the beat renderer from `beat.id`.
- Keep reusable data, timing helpers, labels, model boxes, cards, and motion primitives in a shared module.
- Keep each beat file deterministic from `seconds`, `sceneProgress`, and the passed context.
- Return no wall-clock animation state from beat modules.
- Prefer this split before a renderer file grows into many unrelated subscenes.

## Generic Visual Renderer Gate

Runtime recipe: keep generic visual primitives in one shared module and route to them only when their semantic mechanic matches.

Use the generic renderer only when the new concept shares the same mechanic as the existing pattern.

- Reuse shared palette, row, core, matrix, and ambient-flow helpers only when their semantic roles still match.
- Do not use ambient motion as decoration. Moving packets or lanes must represent transfer, pressure, routing, or accumulation.
- If the concept needs a different causal model, create a dedicated beat module instead.

## Metro Scaffold Hardening

Use when a helper or existing pattern produces technically valid output that still looks like labeled boxes, static panels, padded cards, or disconnected slides.

- Treat helper output as a starter scaffold, not a final Metro video.
- Convert panels into functional zones inside one megacanvas.
- Remove visible title, subtitle, caption, checked-date, and draft/scaffold bands.
- Replace explanatory labels with stateful marks, object-local labels, axes, table cells, route names, or narration-only facts.
- Add camera-driven exploration: overview, zoom or pan to detail, return or transition through a block.
- Add at least three semantic motion systems, such as route motion, matrix fill, queue growth, meter shift, edge draw, table-to-chart transform, or block construction.
- Enforce hard 0-radius blocks, shared 4 px grid edges, no internal padding, and stable grayscale hierarchy.
- Use `visual-density-pattern-bank.md` to select stronger structures before adding text.

Validate hardened output with a contact sheet, Metro audit suite, muted-playback review, and a self-review that names any remaining design defects.

## Cost And Pricing Handoff

Source patterns: LLM billing handoff and implication scenes.

Use when the video needs current pricing or cost comparison without making moving numbers unreadable.

- Keep precise numbers in fixed secondary panels aligned to a table, scorecard, or ledger.
- Let meters, ticks, accumulated blocks, or ranked bars show the mechanic.
- Keep model-entering and model-exiting flows below the model box so enclosure is visible.
- Recheck pricing and product claims from primary sources and record checked dates in the data model.
- Avoid attaching exact prices to moving dots unless the dot itself is the cost object.

## Evaluation Scene Pattern

Runtime recipe: implement evaluation beats as deterministic datasets, candidates, graders, and aggregate-result views that preserve object identity.

Use when the concept is evaluation, grading, pass/fail, pass@k, or benchmark comparison.

- Show evals as datasets plus graders plus measured outcomes.
- Use grids, scorecards, pass/fail traces, or bucketed results before adding explanatory labels.
- Preserve object identity through the loop: prompt/task, candidate output, grader, score, and aggregate result.
- Keep pass-rate or cost charts in stable panels so the viewer can compare endpoints.

## Render Presets

Use the bundled `scripts/capture_html_video.py` renderer. Map the presets below to explicit fps, CRF, device-scale, encoder-preset, frame-retention, and review settings; keep the selected values in the project manifest.

Use explicit presets instead of editing capture settings ad hoc:

- `quick`: storyboard timing only.
- `draft`: visual-shape iteration.
- `motion`: timing/stutter review at 30 fps.
- `fast`: near-final segment preview without slow encoding or contact sheets.
- `final`: approved delivery render with review artifacts.

When the project renderer supports ranges, render only the changed time range unless shared helpers changed across the full video. The bundled capture script renders a complete deterministic duration; use a smaller temporary HTML contract for segment-only smoke tests.

## Validation Checklist

For scene-pattern changes:

- Run the concept content validator.
- Smoke-test representative concepts through `window.renderConceptFrame(conceptId, seconds, { capture: true })`.
- Render a short segment with the cheapest preset that still exercises the changed path.
- Rebuild Pages when the example source changed.
- Verify that no MP4/WebM/raw frames are staged.
