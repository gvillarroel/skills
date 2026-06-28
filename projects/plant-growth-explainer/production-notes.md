# Plant Growth Explainer Production Notes

## Output

- Video: `projects/plant-growth-explainer/artifacts/videos/plant-growth-explainer.mp4`
- Duration: 48.000 seconds
- Resolution: 1280x720
- Frame rate: 30 fps
- Audio: silent

## Critique Loop

| Pass | Critique | Change | Result |
| --- | --- | --- | --- |
| Source and contract | Needed a topic-explainer source package instead of coding from memory inside the renderer. | Created `source-package.json`, `storyboard.md`, `shot-contract.json`, `composition-plan.json`, and `transition-plan.json`. | Contracts validate and preserve seed, water, oxygen, roots, light, CO2, sugars, xylem, phloem, new cells, and seeds. |
| Smoke layout | The opening water label and sun rays crossed scene text. | Rendered large SVG labels in a top layer with text halos and moved the water label above the first droplet path. | Scene titles and labels remain readable over rays and moving particles. |
| Growth-zone proof | The cell panels looked like detached UI cards and the cell division appeared too late. | Added magnifier rings, dashed leader paths, earlier cell activation, and route-timed label opacity. | Growth panels now read as connected proof fields tied to shoot and root tips. |
| Transition contract | The shoot-to-leaf plan promised a zoom, but the renderer only showed a generic pulse. | Added an expanding leaf preview during the transition midpoint smoke frame. | The cut now previews the leaf-scale photosynthesis chamber before the next scene lands. |
| Closing frame | The final `cycle continues` label was partially hidden by the lifecycle composition. | Removed the redundant label and let the completed cycle ring carry the meaning. | Final frame is cleaner and the seed return path is readable. |

## Validation

- `npm run validate:contract`
- `npm run validate:composition`
- `npm run validate:transitions`
- `npm run smoke`
- `npm run render:quick`
- `npm run render:motion`
- `npm run render:final`
- `npm run review`
- `uv run --script scripts/run-pi-skill-eval.py scene-composition-director --prompt-file evaluations/pi-prompts/scene-composition-director-shot-plan.md --mode json --run-id scene-composition-director-plant-loop-20260627-json-9 --expect-output composition-plan.json`
- `uv run --script scripts/run-pi-skill-eval.py scene-transition-director --prompt-file evaluations/pi-prompts/scene-transition-director-transition-plan.md --mode json --run-id scene-transition-director-plant-loop-20260627-json-9 --expect-output transition-plan.json`

Final automated review passed again at 2026-06-27T17:26:43.104Z: 48.000 seconds, 1280x720, 30 fps, 1440 frames, zero black segments, and zero freeze segments.
