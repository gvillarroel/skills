# Dense Task Overlap Builder Local Acceptance — 2026-10-03

The deterministic [standalone builder](../../skills/d3/scripts/build_dense_task_overlap.py) passes local acceptance. These checks validate the builder and its deliverables; they do not replace the isolated Pi release gate or change the outcome of prior failed Pi attempts.

- Final runtime script: **201 lines**, SHA256 `528752d9267f59d1c46c6147350b006b3a35c40804bbb4ff0ed6ac7776ff0aa3`.
- Owning [test suite](../../skills/d3/assets/examples/skill-tests/test_build_dense_task_overlap.py): **3/3 tests**, **24 HTML states** and **8 portable SVG states**, all passing. Test SHA256: `61cee9c32e0246dc863c5fb900c4786861a728bf93da40854c4011066bfcfc76`.
- Independent isolated-output inspector: **6/6 states**, zero findings, browser errors, external requests or caption/task-label collisions.
- All **109 region/task circles** have positive actual radius attributes and painted radii immediately at construction and after Replay/export. Source IDs, coordinates, memberships, label faces and leader endpoints match the parsed generated layout.
- Both colorsets retain nine borderless semantic regions at alpha `0.28`, opaque task dots/label faces, local label backing and exact maximum-contrast black/white text. Actual unobstructed single/double/triple intersection pixels pass the existing five-channel-unit tolerance; the largest observed channel error was **0.8656**.
- Root and worker inspected delivered screenshots; root confirmed CS1 desktop/centered mobile and CS2 desktop show clear intersections, external labels/points and a separate caption rail.

## Runtime and standalone layout scope

The builder embeds the unmodified bundled D3 vendor, parses the generator's assignment as JSON, embeds the entire generated payload and reuses the compact JavaScript renderer from the owning pattern reference. It recreates only its necessary helpers and explicit palette roles, then applies `colorset_adapter.adapt_artifact` automatically. It never reads an acceptance gallery during normal use. The root SVG ID is `task-overlap-dense`; canonical style metadata is `d3-task-overlap-dense-cs1` or `d3-task-overlap-dense-cs2`.

Initial HTML is fully settled and animation-free. `grow` sets each final geometry attribute immediately. Replay uses native SVG opacity only, resets/unpauses the SVG clock and leaves every radius attribute unchanged; reduced motion remains settled. The existing production `render_d3_svg.py` exports the initial state, without an alternative exporter or CSS-only radius animation.

The new standalone output retains every source region/task/leader coordinate while placing the footer summary and legend in a separate rail below all task-label faces. For the default layout, the canvas grows from **880×450 to 880×489.85** (approximately 490 pixels high), with readable **10.5-pixel** rail captions. The production SVG preserves the actual `viewBox="0 0 880 489.85"`; it does not round the height to 490. This is a standalone composition improvement. The canonical gallery renderer, its source excerpt, shared paint finalizer and shared exporter were not modified by this builder work. Existing leader/halo paint and endpoint policy is preserved.

Mobile HTML retains the native 880-pixel chart inside its own horizontal scrolling frame, without overflowing the document. Mobile HTML pixel candidates are constrained to the visible centered frame. Portable SVG tests capture the complete SVG locator and use SVG-relative pixel coordinates, preserving its intrinsic canvas rather than requiring all intersections to fit in a cropped 390-pixel viewport.

## Commands

```text
uv run --script skills/d3/scripts/layout_task_overlap_labels.py --output projects/task-overlap-transparency/artifacts/builder/task-overlap-layouts.js
uv run --script skills/d3/scripts/build_dense_task_overlap.py --layout projects/task-overlap-transparency/artifacts/builder/task-overlap-layouts.js --output projects/task-overlap-transparency/artifacts/builder/dense-overlap.html
uv run --script skills/d3/scripts/render_d3_svg.py projects/task-overlap-transparency/artifacts/builder/dense-overlap.html --output projects/task-overlap-transparency/artifacts/builder/dense-overlap.svg --viewport 1440x1100 --wait-ms 650
uv run --script projects/treemap-tones/scripts/inspect_overlap_isolated.py projects/task-overlap-transparency/artifacts/builder --output projects/task-overlap-transparency/artifacts/builder/independent
uv run --script skills/d3/assets/examples/skill-tests/test_build_dense_task_overlap.py --artifacts projects/task-overlap-transparency/artifacts/builder
uv run --script scripts/validate-pattern-ids.py
```

The owning suite covers colorset1/colorset2, widths 1440/390, ordinary/reduced motion, initial state and two HTML Replays, production SVG export, parsed data fidelity, actual base/painted radii, metadata, opacity/contrast, real intersection pixels, caption clearance, offline/palette compliance and rejected invalid/executable layouts or writes into the read-only skill.

## Retained local attempts

Evidence remains locally under `projects/task-overlap-transparency/artifacts/builder/`, outside git:

- `independent/initial-replay-clock-failure.json`: initial HTML/SVG passed; Replay checks failed after the inspector rewound the previously paused SVG clock to the animation start. The builder now resets/unpauses its clock, and the full six-state run passes in `independent/independent-grade.json`.
- `initial-svg-capture-timeout.json`: all 12 CS1 HTML states passed, then Chromium timed out taking a full-page screenshot of a standalone SVG document. The capture method was corrected; runtime was unchanged.
- `partial-svg-viewport-sample-failure.json`: viewport clipping correctly excluded invisible pixels, but the narrow SVG crop could not contain all three overlap multiplicities. The evaluator now captures the complete SVG locator with relative coordinates; runtime was unchanged.
- Final `test-report.json`: 32 passing browser/export states, actual sample RGB values and zero caption collisions. Delivered HTML/SVG files and corresponding screenshots are grouped in `colorset1/` and `colorset2/`.

The runtime script was frozen before the new isolated cohort began. No runtime edits followed the final local acceptance.
