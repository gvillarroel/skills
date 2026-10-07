# SVG fidelity by route

Use this reference when appearance matters or the user asks what survives a conversion. Preserve the source, inspect its rendered state, and separate logical content, drawing details, native editability, and vector storage. These properties are independent.

## Select and qualify the route

| Route | What it can preserve | What to qualify |
| --- | --- | --- |
| Formal custom-shape SVG import, without rasterization | Vector artwork and scalable geometry | No guarantee of identical SVG rendering or separate editable internal objects; compare fonts, curves, overlaps, clipping, filters, and embedded images |
| Canvas drag-and-drop or rasterized SVG import | A static picture of the drawing | Vector storage and resolution independence are lost; inspect enlargement at the intended display/print size |
| SVG image in Standard Import | Static image appearance, subject to conversion | Lucid converts SVG images to PNG; embedded artwork is not a native graph |
| Native Mermaid reconstruction | Recovered labels, directions, topology, broad shape categories | Automatic layout, paths, dimensions, styling, and text metrics can change; SVG artwork and animation do not transfer |
| Bundled `build_native.py` graph compiler | Explicit boxes, supported solid node colors, labels, ports, graph endpoints | Only the documented primitive subset; presets below replace unrepresented SVG details; live parser and rendering still need verification |

Lucid staff distinguish formal vector import from drag-and-drop image handling. The current editor can offer **Rasterize SVG Imports**. Inspect that choice rather than inferring vector status from the filename. The formal import route is the appropriate candidate for preserving scalable artwork; verify each actual SVG before calling its appearance preserved. Custom-library availability depends on the current account.

## Bundled native compiler substitutions

The compiler consumes recovered graph JSON, not SVG XML or computed CSS. Preserve a supported attribute only when it has actually been extracted into the graph; defaults are not source fidelity.

| Detail | Current compiler behavior |
| --- | --- |
| Position and size | Emits axis-aligned `x`, `y`, `width`, `height` from the graph; resolve ancestor transforms and viewBox origin first |
| Node label | HTML-escapes the supplied literal string; no source text outline recovery or per-span formatting |
| Text styling | Liberation Sans and centered alignment; graph `font_size` and `text_color` are accepted, otherwise 14 px and `#000000`; source anchors, baselines, weight, and family are not represented |
| Shape paint | Six-digit solid `fill`/`stroke` colors from the graph; defaults are white fill and `#000000` stroke; stroke is always 1 px solid |
| Shape geometry | Rectangle, diamond, text, and `ellipse` mapped to documented `circle`; rectangle corner radii and arbitrary path outlines are not represented; non-square circle rendering needs live checking |
| Connector | Straight, black, 1 px solid, no source marker, destination arrow; explicit relative ports or right-center to left-center defaults |
| Connector label | Black 14 px, midpoint/top preset; no source label position, family, weight, or color |
| Stack and page | Shapes at z-index 1, lines at 0; tight inferred white page; source groups, layer order, page margins, and transparent backgrounds are not represented |
| Rich SVG features | No graph fields for gradients, opacity, dash patterns, masks, clip paths, filters, images, animation, accessibility metadata, or arbitrary SVG attributes |

Distinguish recovery mistakes from compiler limitations and Lucid rendering differences. A source attribute absent from the graph was already lost before compilation. A known preset substitution is a local change, even when no authenticated service import is available.

Check inherited/computed SVG styles when identifying visible edges. A path with neither an explicit nor inherited stroke has no visible stroke, because SVG defaults to `stroke: none`; inspect its fill separately. Semantic `data-source` metadata alone does not create a visible line. Adding a native black arrow preserves an interpreted relationship but introduces artwork. Count semantic endpoints and visible source paths separately.

## Measure and report

Compare literal labels, node/edge counts, direction, branch labels, positions/sizes, fills/strokes, text metrics, path geometry/heads, stacking, crop, and rich SVG features. Report exact bounded counts only for what was inspected, such as seven of seven relationships. Do not turn those counts into an overall visual percentage.

For a live imported result, inspect at fit-to-page and enlarged scale. Confirm independent object selection, a label edit, and attached connectors following a moved shape when native editing is required; undo probe edits. Compare rendered source and imported output with compatible crop/scale before any image metric. Do not assign SSIM or a pixel-fidelity score to screenshots at different zooms or a locally simulated preview.

If live access is unavailable, label the result as local package/source analysis or dated saved editor evidence. Identify the exact route used in saved evidence; a semantic-source-to-Mermaid test does not verify uploading an SVG file.

For Lucid-to-SVG export, support confirmed in July 2025 that labels are rendered as vector paths rather than live text. Inspect the actual current download: outlined labels can preserve appearance while losing text editing, extraction, and source semantics. A `<text>` count of zero is not a visual-label failure. Check raster `<image>` content separately, since an SVG container does not prove vector-only output.

## Primary sources

Checked 2026-10-07; support statements describe their dated product behavior, not an untested file-specific guarantee.

- [Shape-library SVG import and account availability](https://help.lucid.co/hc/en-us/articles/14931750819476-Shape-libraries-in-Lucidchart)
- [Lucid staff: vector import, drag-and-drop, and Rasterize SVG Imports](https://community.lucid.co/product-questions-3/how-can-i-scale-svgs-while-retaining-quality-7004/index2.html)
- [Standard Import images: SVG conversion to PNG](https://lucid.readme.io/docs/images-si)
- [Lucid support: SVG export outlines text](https://community.lucid.co/ideas/exporting-a-lucid-document-as-a-svg-with-editable-text-2974)
