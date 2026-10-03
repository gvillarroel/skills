Use `$one-bit-dither-svg` from `skills/one-bit-dither-svg/` to complete this task in the isolated workspace.

Create `result/source.svg` as a self-contained 320×180 SVG scene containing all of the following: a dark navy sky, a warm red sun, a pale yellow lighthouse with black windows, a green foreground hill, a blue sea with at least four white wave lines, one translucent cloud, and transparent corners outside a rounded scene frame. Do not read acceptance fixtures or any repository path outside the copied skill and this prompt.

Then use the skill's shipped transformer to create exactly these three outputs from that same source:

- `result/original.svg` in `original` mode.
- `result/custom.svg` in `custom` mode using `#b7410e`.
- `result/regional.svg` in `regional` mode requesting 6 region colors.

Use render size 320×180, cell size 4, matrix size 4, and contrast 1.15 for every output. Also create matching previews and conversion reports at `result/original.png`, `result/original.json`, `result/custom.png`, `result/custom.json`, `result/regional.png`, and `result/regional.json`.

Run the shipped validator on each SVG with the corresponding expected mode and expected custom color where applicable. Write the three validator reports to `result/original-validation.json`, `result/custom-validation.json`, and `result/regional-validation.json`.

Finish only after all three validations pass. Do not modify any file under `skills/one-bit-dither-svg/`.
