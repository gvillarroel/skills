Use `$one-bit-dither-svg` from `skills/one-bit-dither-svg/` to complete this task in the isolated workspace.

Create two self-contained local SVG sources without reading any repository path outside the copied skill and this prompt:

1. `result/fine-source.svg`: a 640×360 technical panel with a transparent outer canvas, at least six labeled rows, multiple 1–2 px strokes, small numeric labels, circles at line endpoints, and a restrained dark-red/navy palette. Give it a title and description.
2. `result/broad-source.svg`: a 640×360 abstract badge made from several large flat geometric shapes in at least five saturated colors, with no visible text and a transparent outer canvas. Give it a title and description.

Use the skill's named profiles rather than manually restating their preset values:

- Transform `fine-source.svg` to `result/fine-original.svg` in `original` mode with `--quality-profile detailed`.
- Transform `fine-source.svg` to `result/fine-custom.svg` in `custom` mode with color `#284b63` and `--quality-profile detailed`.
- Transform `broad-source.svg` to `result/broad-regional.svg` in `regional` mode with `--quality-profile compact`.

For every transformed SVG, create a matching PNG preview and conversion JSON report using the same basename. Run the shipped validator with the corresponding expected mode and the expected custom color where applicable. Write validator reports as `result/fine-original-validation.json`, `result/fine-custom-validation.json`, and `result/broad-regional-validation.json`.

Inspect the previews. The fine-detail outputs must retain all six row lines, endpoint circles, and readable row distinctions; the broad regional output must retain recognizable large color zones. Finish only after all three validators pass. Do not modify any file under `skills/one-bit-dither-svg/`.
