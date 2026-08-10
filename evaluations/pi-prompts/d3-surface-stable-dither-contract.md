Use $d3 to prove both dithering paths work in an isolated workspace.

The copied `skills/d3/` directory is read-only. Do not modify it. Do not inspect repository files, sibling skills, `assets/examples/`, or the network. Write generated files only under `outputs/`.

Create exactly these non-empty artifacts:

- `outputs/source.html`
- `outputs/dithered.svg`
- `outputs/dither-report.json`
- `outputs/fractal-validation.json`

Requirements:

1. Create `outputs/source.html` as a self-contained offline page with one visible `svg#source` measuring 320 by 180 CSS pixels. Give it a white background and a deterministic mix of smooth gray shading, one dark curved path, three gray circles, and one red rectangle. Use only inline HTML/SVG/CSS and no remote dependency.
2. Use the skill's bundled static dithering tool to capture `svg#source` and write `outputs/dithered.svg` with ordered dithering, a 4x4 Bayer matrix, 4-pixel cells, the two-color palette `#000000,#ffffff`, and animation enabled. Run this exact command from the workspace root:

   ```bash
   uv run --script skills/d3/scripts/dither_d3_output.py outputs/source.html -o outputs/dithered.svg --selector "svg#source" --algorithm ordered --matrix-size 4 --cell-size 4 --palette "#000000,#ffffff" --animate --wait-ms 100 --timeout-ms 15000 --json-report outputs/dither-report.json
   ```

3. Execute the bundled surface-stable fractal helper's zoom-sequence validation and write its complete result as formatted JSON to `outputs/fractal-validation.json`. Do not reimplement or paraphrase this validation. Run this exact command from the workspace root:

   ```bash
   node -e "const fs=require('fs'); const helper=require('./skills/d3/assets/templates/surface-stable-fractal-dither.js'); const report=helper.validateZoomSequence(); fs.writeFileSync('outputs/fractal-validation.json', JSON.stringify(report, null, 2)+'\n'); if(!report.ok || !report.steps.every(step=>step.retained) || report.boundary.beforeCount!==report.boundary.afterCount) process.exit(1)"
   ```
4. Confirm before finishing that the static report has `ok: true`, `algorithm: "ordered"`, `matrixSize: 4`, `cellSize: 4`, positive grid dimensions and run count, and no browser errors. Confirm that the fractal report has `ok: true`, every step retains all earlier point IDs, and the 2x boundary reports equal before/after counts.

Do not create alternate filenames or write any output inside the skill directory.
Do not use shell heredocs and do not run additional shell validation commands after the two exact commands above. Read the two JSON reports directly, confirm their fields, and finish.
