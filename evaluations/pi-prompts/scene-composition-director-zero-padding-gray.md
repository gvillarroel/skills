Write `projects/zero-padding-composition/composition-plan.json`.

Create a validation-ready composition plan for one scene:

- Scene ID: `s01-zero-padding-board`
- Format: 1280x720
- Style: hard-edge Metro grid, 0-radius rectangles, no internal padding inside boxes
- Hierarchy: use distinct grayscale levels for primary, secondary, and tertiary levels
- Required anchors: `zero internal padding`, `grayscale hierarchy levels`, `0-radius rectangular panels`

The scene should show a modular board with three hierarchy levels. Use external gutters only; do not use padded cards, inset bars, padded chips, or nested panels.

After writing the JSON, validate it with:

```powershell
uv run --script skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan projects/zero-padding-composition/composition-plan.json --expect-scenes 1 --require-anchor "zero internal padding" --require-anchor "grayscale hierarchy levels" --require-anchor "0-radius rectangular panels" --require-strict-alignment --require-square-edges --require-zero-box-padding --require-grayscale-hierarchy --require-validation-contract
```
