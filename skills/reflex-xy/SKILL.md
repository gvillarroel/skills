---
name: reflex-xy
description: Builds, customizes, troubleshoots, and exports Python charts with reflex-dev/xy, including large-data views, notebook widgets, xy.pyplot migration, and Reflex integration. Use when the user names XY, reflex-xy, reflex_xy, or this library's repository; do not substitute React Flow's xyflow.
---

# Reflex XY

Use the Python package `xy` from [reflex-dev/xy](https://github.com/reflex-dev/xy).
Build an editable Python source and the requested chart artifacts. Keep generated
files outside this skill bundle.

## Establish the environment

1. Inspect the existing project's Python environment and dependency manager.
   In an unknown environment, `importlib.util.find_spec("xy")` safely detects
   absence before calling `importlib.metadata.version("xy")`. Preserve a
   working dependency pin.
   The tested baseline is **XY 0.0.8, Python 3.11+**, checked on 2026-10-24.
   For a new project, use `uv add "xy==0.0.8"` or an equivalent explicit pin;
   check current official release metadata when the user requests a newer version.
   For a standalone script, copy the template's PEP 723 metadata declaring
   `xy==0.0.8` and run `uv run --script app.py` in its declared environment.
2. Use core `xy` for scripts and notebooks. Add `xy[reflex]` only for a Reflex
   application; its Python adapter is imported as `reflex_xy`.
3. Verify actual construction and export, not only `import xy`: the import is
   lazy and can succeed with a missing native core or render-client asset.
   Run the diagnostic below when installation or output behavior is uncertain.
4. Check the installed signatures before using an unfamiliar factory or an
   API from newer documentation. The public API composes `Chart` objects from
   marks and components; `xy.Figure` is not public in the tested release.

## Build for the requested host

- For a script or portable interactive deliverable, call `chart.to_html(path)`.
  The file embeds its data and client; browser hover/pan/zoom work locally.
- For a notebook, leave `chart` as the last expression or display
  `chart.widget()`. `chart.show()` returns a widget; it does not launch a browser.
- For images, use `chart.write_image(path)` or the explicit exporters. Read
  [outputs-and-validation.md](references/outputs-and-validation.md) for engine,
  CSS, dimensions, and snapshot behavior.
- For Reflex or Matplotlib migration, read
  [reflex-and-pyplot.md](references/reflex-and-pyplot.md). Choose the static,
  fixed-data live, or state-dependent tier before wiring backend events.

Read [chart-recipes.md](references/chart-recipes.md) for arrays, named columns,
multiple series, categorical bars, heatmaps, and facets. Start from
[chart.py](assets/templates/chart.py) when an editable, reproducible script is
useful. Preserve supplied data and missing-value semantics; label axes and units.
Prefer `xy.chart(...)` for mixed marks and a family factory for a single family.

## Apply the selected colorset

Read [colorsets.md](references/colorsets.md) before authoring chart paint.
Default to `colorset1`; select `colorset2` when requested or when several
independent categories need full color. Use the bundled helper and exact
[palette contract](assets/palettes/colorsets.json) for marks, text, axes,
backgrounds, legends, tooltips and controls. Apply the helper's `theme()` to
the chart and `css()` to HTML export. Keep explicit user style when requested.

Assign stable category identities to opaque solid fills, with no decorative
outline. Place the legend explicitly in verified empty space; XY's default
upper-right legend can cover a high endpoint. Use colorset1's primary red followed by its interleaved neutral
sequence; exhaust usable solids before adding another visual encoding. For
numeric color, bin values into exact palette colors while retaining the raw
measurements. Native XY colormaps interpolate, so exact palette stops alone
do not establish an exact-paint result. Inspect rendered HTML and native
exports; antialiasing and alpha compositing are derived pixel effects.

Use the six paired [published examples](https://gvillarroel.github.io/skills/examples/reflex-xy-colorsets/)
for visual reference. The reusable recipe is in the compact reference above;
normal runtime work does not need to read the acceptance gallery source.
Read [the compact pattern recipes](references/pattern-recipes.md) to recreate
a mechanism with new data while keeping the palette contract.

## Preserve data and interaction semantics

- Bind aligned one-dimensional columns or documented grid inputs. A mark's
  `data=` overrides chart-level `data=`. Convert row-record lists to a mapping
  of column names to arrays before using named channels. Valid CSS color strings are constants;
  other strings can resolve to data columns. Use one line mark per series;
  a line's color is a constant, not a categorical channel.
- Use real datetime-like values for time axes. Canonical time is milliseconds;
  do not promise preservation of nanosecond distinctions. Retain NaN gaps in
  lines rather than silently interpolating or deleting observations.
- For large arrays, density, streaming, selection, or exact row readout, read
  [large-data-and-live.md](references/large-data-and-live.md). Density is an
  aggregate representation; do not describe each bin as an exact source point.
- Standalone HTML is an interactive snapshot. Python callbacks and future
  `append()` calls require a live widget or framework connection. Explain that
  boundary when the requested delivery mode cannot perform a backend action.
- Treat the installed API and a matching release's source as evidence when
  web guides conflict. Read [sources.md](references/sources.md) for the verified
  upstream identities and the known stale installation guide.

## Diagnose and verify

Replace `<skill-dir>` with this bundle's path. The `uv` form runs the pinned
baseline; run the same script with the project's Python to diagnose its installed
version. Outputs include real HTML, SVG, PNG, hashes, and a JSON result.

```sh
uv run --script <skill-dir>/scripts/diagnose.py --output-dir artifacts/xy-probe --report artifacts/xy-environment.json
```

Run the final source in the intended environment. Confirm every requested path,
parse image dimensions, and inspect the rendered chart for legible labels,
correct series, missing-value gaps, and clipping. For interactive HTML, open it
with the bundled browser verifier, then inspect its screenshot and exercise any
additional requested interaction. It blocks network requests, checks canvas
paint and console errors, and uses an installed Edge/Chrome or Playwright Chromium:

```sh
uv run --script <skill-dir>/scripts/verify_html.py --html results/chart.html --report artifacts/browser.json --screenshot artifacts/browser.png --label "Chart title"
```

Replace paths and labels with the actual outputs; repeat `--label` for expected
case-sensitive DOM text such as title, axis or legend fragments. Inspect canvas
annotations in the screenshot; they need not exist as DOM text. In Windows
shells, prefer ASCII label fragments because Unicode command arguments can be
transcoded; retain the intended Unicode in source files. A successful file
write alone does not establish rendering.
Report which host, package version, output engine, and interactions were verified;
distinguish untested integration or performance claims from measured results.
