# Lucidchart editor workflows

Checked against official documentation on 2026-10-07. Inspect current controls and entitlement messages rather than assuming an account supports every route.

## Export

1. Open the supplied Lucidchart document with the existing authenticated session. Confirm the document and requested page, not a thumbnail or published preview.
2. Inspect visible layers. SVG reflects synchronized layer visibility; set it only as authorized and record the selection. SVG does not preserve comments, notes, tasks, or interactive layer actions.
3. Open **More** in the top-left, hover **Export**, and select **SVG** (or the observed transparent SVG option when requested). Set crop to content or the requested custom area. Do not assume a page selector exists: inspect the result and export each requested page separately when needed.
4. Capture the download through the supported browser download API/event. The filename may be supplied by the server. Preserve original bytes and save/copy within the user's permitted output directory to the exact requested filename. If the result is a ZIP, inspect member paths before extraction and validate each SVG.
5. Check that the file is actual SVG and inspect it visually. Check full labels, fonts, clipping, line heads, image resolution, and diagram boundaries against the editor. An embedded PNG inside SVG is still raster content.

If no download bytes arrive, inspect the export dialog, account/permission message, browser error, and download history. A successful click or elapsed wait is not a completed download. Retry once when a transient failure is plausible; stop if the same boundary repeats. Do not enable trials or use private signed-object endpoints copied from network traffic as a workaround. A supported download tool may be unavailable even when the website supports export.

The public REST document-image reference currently lists JSON/PNG, not SVG. Use the editor route for SVG unless a current official endpoint explicitly adds it.

## Insert an SVG asset

Use **More shapes → Import Shapes → existing/new custom library → Choose File → Upload**, enable the library, and place the imported shape on the canvas. The custom-library documentation describes SVG import on Individual, Team, and Enterprise plans. Generic image insertion does not establish SVG support: use another control only if the observed UI explicitly accepts SVG. Keep the source aspect ratio, title the document when creating one, and avoid overwriting unrelated canvas content.

An imported SVG/custom shape does not establish that its internal paths, text, and connectors are separate editable native objects. Verify its appearance and report the actual editability. For reusable SVG shapes, use absolute geometry, ordinary path/shape elements, explicit fills/strokes, and self-contained resources where practical. Filters, CSS fonts, `foreignObject` labels, and clipping may need deliberate adaptation. Never silently rasterize when the user requests vector preservation.

Formal SVG import can retain vector properties; drag-and-drop onto the canvas can instead treat it as a regular image. Inspect the observed **Rasterize SVG Imports** choice and keep rasterization disabled when vector preservation is requested. Vector status does not guarantee identical curves, fonts, or overlaps. Use [fidelity.md](fidelity.md) for the comparison and the bundled compiler's explicit style substitutions.

If insertion is unavailable, still provide the checked SVG and inspection report. Do not label local preparation as a completed Lucid upload.

## Native Mermaid route

For a semantic flowchart recovered from SVG, paste supported Mermaid syntax onto the canvas and inspect the preview. If the UI offers **Disconnect from code → Convert to Lucid shapes**, use it when native editing is requested. The **Diagram as code** panel is another code-rendering route; use conversion from that panel only if the observed UI offers it. Some diagram families only render and lack conversion; verify the conversion control for the current family rather than assuming all Mermaid output is editable. Preserve the source Mermaid separately.

Probe native behavior by selecting one shape, editing its label, moving it, and checking attached connectors; then undo. This route normally changes coordinates through automatic layout and does not carry SVG animation or arbitrary artwork.

## Sources

- [Export or print a Lucid document](https://help.lucid.co/hc/en-us/articles/16324571257492-Export-or-print-a-Lucid-document)
- [Shape libraries in Lucidchart](https://help.lucid.co/hc/en-us/articles/14931750819476-Shape-libraries-in-Lucidchart)
- [Get/Export Document: current REST formats](https://developer.lucid.co/reference/getorexportdocument)
- [Diagram as code with Mermaid in Lucidchart](https://help.lucid.co/hc/en-us/articles/29549366940948-Diagram-as-code-with-Mermaid-in-Lucidchart)
- [Official Mermaid canvas-paste and native-conversion update](https://community.lucid.co/community-news-and-announcements-9/copy-paste-mermaid-syntax-for-editable-diagrams-13659)
