Use `$one-bit-dither-svg` from `skills/one-bit-dither-svg/` to complete this task in the isolated workspace.

Do not read acceptance fixtures or any repository path outside the copied skill and this prompt. Do not modify any file under `skills/one-bit-dither-svg/`.

Use `uv run --with Pillow python` for any source-generation or inspection snippet that imports Pillow; do not use the ambient `python`. Keep every generated inspection frame inside the workspace under `result/review/`. Do not write or read `/tmp`, an absolute path, or any location outside this isolated workspace.

Create `result/source.gif`, a self-contained 12-frame, 320×180 animated GIF with a 100 ms duration per frame and infinite looping. The scene must have a pale background, a dark lighthouse on the right, three thin wave lines, and a large orange circle that moves unmistakably from left to right over the animation. Make every frame visibly distinct and keep the animation opaque.

Transform the complete animation—not one selected frame—to `result/styled.gif` in `custom` mode with exactly `#283845` plus white. Use the `detailed` quality profile, exact 1280×720 output dimensions, 10 fps, a two-color encoding palette, and infinite looping. Also create:

- `result/styled-contact.png`
- `result/styled.json`

Run the shipped animated-GIF validator. Require custom mode with exact color `#283845`, 1280×720 dimensions, approximately 10 fps, loop value 0, at least 10 frames, and no more than two colors. Supply the conversion manifest and use the validator's `--json-report result/styled-validation.json` option.

After validation, inspect the contact sheet and the GIF directly with the image-reading tool. Confirm visually that the circle changes position across the timeline and that the lighthouse and waves remain recognizable; rely on the validator for the exact two-color palette. Do not run custom pixel-coordinate, color-segmentation, motion-metric, or assertion scripts after the validator: ordered dither intentionally distributes the ink color through light backgrounds, so naive global color-coordinate checks are invalid. Once direct visual inspection, the shipped validator, and the five exact output paths pass, stop without further shell experiments.
