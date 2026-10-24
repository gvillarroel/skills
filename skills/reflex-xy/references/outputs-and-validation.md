# Outputs and validation

## Contents

- [Host and output engine](#choose-the-host-and-output-engine)
- [Interactive snapshots](#interactive-snapshot-boundary)
- [Observable verification](#verify-observable-results)
- [Common failures](#diagnose-common-failures)

## Choose the host and output engine

| Need | API | Contract |
| --- | --- | --- |
| Offline browser chart | `chart.to_html("chart.html")` | Bundled data, client and styles; no CDN or Python callback |
| Live notebook | `chart.widget()` or final expression `chart` | AnyWidget frontend and a running kernel |
| Vector image | `chart.to_svg("chart.svg")` | Native; reduced/density layers can contain raster images |
| Native raster | `chart.to_png("chart.png", scale=2)` | Browser-free default; pixel dimensions multiply by scale |
| Inferred image format | `chart.write_image("chart.pdf")` | Native by default; extension selects format |
| Browser CSS fidelity | `chart.write_image("chart.png", engine=xy.Engine.chromium, custom_css=css)` | Needs locally installed Chrome/Chromium/Edge |

`to_html()`/`to_svg()` return strings; `to_png()`/`to_image()` return bytes.
Supplying a supported path also writes the file. `write_image()` infers PNG,
JPEG, WebP, SVG, PDF, or HTML from the extension and returns written bytes.
Create output parents explicitly and preserve exact user-requested paths.

```python
from pathlib import Path
import xy

out = Path("results")
out.mkdir(parents=True, exist_ok=True)
chart.to_html(out / "chart.html")
chart.write_image(out / "chart.svg", width=1000, height=560)
chart.write_image(out / "chart.png", width=1000, height=560, scale=2)
xy.write_images(figures=[chart, chart],
                files=[str(out / "chart.pdf"), str(out / "chart.webp")])
```

`Engine.auto` chooses native output unless custom CSS requires Chromium;
explicit `to_png()` defaults to `Engine.default`, so pass `Engine.chromium`
with `custom_css`. SVG always uses the native vector path. Chromium is optional:
do not install or require it for ordinary native export. Set `XY_BROWSER` to
a known browser executable if discovery fails. Retain the browser sandbox.

Native WebP is lossless with alpha; native JPEG flattens alpha and requires an
opaque background. JPEG rejects `background="transparent"`. SVG/PDF can embed
bounded raster layers for density/heatmaps; call them hybrid when that matters.
Native exports use supported chart styles, not an arbitrary browser CSS cascade.

Use integer logical dimensions and an explicit raster scale for reproducibility.
For example, 800×450 with scale 2 produces 1600×900 pixels. Responsive charts can
export with fallback dimensions; do not rely on that when dimensions are specified.
For facets, configure panel dimensions at construction rather than passing
unsupported per-call `to_svg(width=...)` options.

## Interactive snapshot boundary

HTML keeps client-side interactions and built-in export controls, but its data
is a snapshot. Re-export after mutation or choose a live host when the browser
must invoke Python. A dense standalone view may refine through a retained sample;
it cannot fetch arbitrary full-resolution source rows from an absent kernel.

The standalone document uses inline scripts/styles and blob workers. Its embedded
CSP blocks external connections. For a host with nonce/hash-only CSP, use a
host-aware wrapper rather than promising that unchanged standalone HTML meets it.
Embedding source data in an HTML deliverable makes that embedded data available
to its recipient; respect the requested data scope when sharing artifacts.

## Verify observable results

1. Execute the final script with its declared environment. Check each exact file,
   image dimensions, expected title, axes, series, and the intended missing gaps.
2. Parse SVG as XML and inspect PNG headers or use an image library. Inspect a
   rendered export for cropping, tiny text, misplaced legends, and empty plots.
3. Open HTML in a browser at the intended viewport. Wait for the canvas, check
   nonblank chart pixels and console/page errors, then exercise hover/zoom or the
   requested selection. Check responsive layout if that is part of the task.
4. Verify live backend events with the actual widget/Reflex host when requested;
   an HTML screenshot does not prove callback delivery.

For an independent browser check, use the available browser automation tool or
the bundled `scripts/verify_html.py` command shown in the entrypoint. It provides
an offline load, canvas paint/error checks, labels, a screenshot, and basic input
dispatch; inspect the screenshot and test exact hover/selection semantics when
the task requires them. A URL string inside bundled JavaScript or an SVG namespace
does not establish a network dependency. Check actual requests and external
resource references rather than asserting that the HTML contains no `http` text.

On Windows, Playwright can use an installed
Edge/Chrome channel; software WebGL may need `--use-angle=swiftshader` in a
headless environment. Check errors before changing launch flags. The diagnostic
script validates real exports and metadata; it does not perform browser QA.

## Diagnose common failures

- Import succeeds but export fails: verify the native library and bundled client
  from the same wheel; a source build can need Rust and Node/npm for client assets.
- Blank widget: restart the notebook kernel after installation and try the raw
  widget. In WASM notebooks, host/frontend support differs; inspect matching docs.
- Collapsed responsive chart: set a defined parent and chart height.
- Invalid color/shape/channel: fix the named argument; do not suppress validation
  or silently coerce invalid source values.
- Several dashboard canvases go blank: investigate the browser's WebGL context
  budget and reduce simultaneous mounts.
- File remains unchanged after append: exported files need a new export.

Report actual versions, Python/platform, dimensions and engine, exception text,
and a minimal constructor when a failure remains unresolved.
