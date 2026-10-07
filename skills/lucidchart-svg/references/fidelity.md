# SVG fidelity by route

Use this reference when appearance matters or the user asks what survives a conversion. Preserve the source, inspect its rendered state, and separate logical content, drawing details, native editability, and vector storage. These properties are independent.

## Select and qualify the route

| Route | What it can preserve | What to qualify |
| --- | --- | --- |
| Formal custom-shape SVG import, without rasterization | Vector artwork and scalable geometry | No guarantee of identical SVG rendering or separate editable internal objects; compare fonts, curves, overlaps, clipping, filters, and embedded images |
| Canvas drag-and-drop or rasterized SVG import | A static picture of the drawing | Vector storage and resolution independence are lost; inspect enlargement at the intended display/print size |
| SVG image in Standard Import | Static image appearance, subject to conversion | Lucid converts SVG images to PNG; embedded artwork is not a native graph |
| Native Mermaid reconstruction | Recovered labels, directions, topology, broad shape categories | Automatic layout, paths, dimensions, styling, and text metrics can change; SVG artwork and animation do not transfer |
| Bundled extraction and native graph compilation | Explicit metadata, supported geometry/style, documented semantic types, labels and attachments | Bounded mapping profile; declared adaptations, unresolved source features, live parser/rendering checks |
| Bundled data-backed generation | Supplied hierarchy records, sequence markup or selected graph objects | Generated layout replaces coordinates; grammar and editing behavior require live verification |

Lucid staff distinguish formal vector import from drag-and-drop image handling. The current editor can offer **Rasterize SVG Imports**. Inspect that choice rather than inferring vector status from the filename. The formal import route is the appropriate candidate for preserving scalable artwork; verify each actual SVG before calling its appearance preserved. Custom-library availability depends on the current account.

## Bundled native compiler substitutions

The compiler consumes recovered graph JSON, not SVG XML or computed CSS. Preserve a supported attribute only when it has actually been extracted into the graph; defaults are not source fidelity.

| Detail | Current compiler behavior |
| --- | --- |
| Position and size | Emits explicit graph boxes and supported rotation; extraction composes positive scale/translation and the selected root viewport mapping; unsupported transforms are blocked |
| Node label | HTML-escapes the supplied literal string; no source text outline recovery or per-span formatting |
| Text styling | Explicit size/color/family, emphasis and documented alignment; generic defaults are centered black14px Liberation Sans; cloud types retain library defaults. Declaration preservation does not establish glyph metrics, baseline, wrapping or font availability |
| Shape paint | Six-digit solid fill/stroke, integer width, solid/dashed/dotted style and whole object opacity; generic defaults whitefill/black1pxsolid. No exact arbitrary dash array, fractional width, per-paint opacity or SVG `fill:none` |
| Shape geometry | Documented catalog types, bounded polygons and rounding (twice radius); `ellipse` aliases `circle`; arbitrary paths/holes or non-square-circle rendering are not certified |
| Connector | Explicit endpoints, all22 documented markers, straight/elbow/curved family and supported controls; generic defaults black1pxsolid destinationarrow. Exact Bézier or SVG marker geometry is not represented |
| Connector label | Multiple literal labels, positions/sides/color/font/emphasis; generic defaults black14px midpoint/top; source text placement may be recentered |
| Stack and page | Explicit stack/group/layer/finite page settings; default page derives node extent plus32px and does not measure text/stroke/absolute-line overflow. Transparent page output is outside the current solid-color profile |
| Rich SVG features | Artwork/hybrid route for gradients, masks, clips, filters, images, text paths, animation, accessibility metadata and arbitrary attributes; XML inventory does not validate their rendered/native preservation |

Distinguish recovery mistakes from compiler limitations and Lucid rendering differences. A source attribute absent from the graph was already lost before compilation. A known preset substitution is a local change, even when no authenticated service import is available.

Use the extractor ledger and builder `--report` as evidence for the narrative. Count each source and target border separately; do not describe both as dashed when only one emitted that style. Inspect actual emitted defaults rather than copying a general preset sentence. Read [svg-mapping.md](svg-mapping.md) for unsupported feature decisions and [generated-layouts.md](generated-layouts.md) for reflow policies.

The inspector report inventories SVG-namespace elements and literal text, including text in definitions or hidden declarations. It preserves `xml:space` inventory and lists rich-feature declarations with bounded samples; it does not compute stylesheet cascade, validate arbitrary path grammar or identify all visible content. Foreign-namespace elements are counted separately. `ready_for_upload` is resource/XML preflight eligibility, not native mapping or visual acceptance.

Check inherited/computed SVG styles when identifying visible edges. A path with neither an explicit nor inherited stroke has no visible stroke, because SVG defaults to `stroke: none`; inspect its fill separately. Semantic `data-source` metadata alone does not create a visible line. Adding a native black arrow preserves an interpreted relationship but introduces artwork. Count semantic endpoints and visible source paths separately.

## Measure and report

Preserve the source's deliberate reading order and semantic colors. Do not redesign its notation while converting unless requested. For an authorized redesign, use the smallest layout that keeps every label complete, every endpoint traceable and every marker inside the page. Use lanes/regions for explicit ownership; groups for collective editing. Separate parallel edges and branch labels so they remain attributable. Avoid routing through unrelated nodes or placing crossings where readers could infer a junction. Use explicit ports and orthogonal routes only when the source relationships support them.

Keep full labels rather than shrinking or truncating text to fit a structural box. Check actual font availability, wrapping, baseline and padding in the live result; copied font declarations cannot determine those metrics offline. Preserve text/color hierarchy where known and inspect readability at the intended zoom/print scale. Do not assume a table's supplied row heights or an icon's bounding box establishes text fit. Preserve symbol/marker scale and compare head-to-shaft attachment when enlarging an SVG asset. If editable text is overlaid on artwork, disclose the hybrid representation and check overlap/alignment after shape movement.

Use visible containers to communicate established boundaries and tables to preserve ER/UML compartments. Native family types can render their own internal geometry and defaults; inspect them after import instead of claiming identical outlines from matching boxes. Align and compact only within the user's layout intent. Generated or smart routes deliberately trade fixed positions for adaptive layout, and their source-coordinate comparison is not a fidelity score. These rules derive from the documented editing/layout mechanisms and source notation; they are presentation guidance, not service-render guarantees. [Native line routing](https://lucid.readme.io/docs/lines-si), [containers](https://lucid.readme.io/docs/container-library-si), [tables](https://lucid.readme.io/docs/table-library-si), [flowchart reading direction](https://lucid.co/diagram/flowchart/how-to-make-a-flowchart).

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
