---
name: lucidchart-svg
description: Exports Lucidchart diagrams to SVG, inserts SVG artwork into Lucidchart, and reconstructs SVG diagrams as editable Lucid shapes and connectors. Use for Lucidchart SVG downloads, uploads, conversions, and fidelity checks.
---

# Lucidchart SVG

## Choose the result

Identify the document or SVG source, requested output path, pages, and whether the user needs visual fidelity or individually editable shapes. Preserve existing authorization; do not require a second confirmation for an already requested download or creation.

| Request | Route | Result |
| --- | --- | --- |
| Download a Lucidchart diagram as SVG | Editor export | SVG file from the selected document/page |
| Place SVG artwork in Lucidchart | SVG/custom-shape import | A visual asset; internal labels and connectors are not established as native objects |
| Create editable shapes from an SVG diagram | Recover semantic nodes/edges, then native Mermaid conversion or Standard Import | Reconstructed shapes and attached connectors, with declared changes/losses |

Do not infer topology from path proximity alone. Prefer original graph data, stable SVG IDs, labels, and explicit endpoint metadata. A screenshot, SVG image, `.lucid` package, and successfully created Lucid document are different deliverables; report the one actually produced.

For fidelity reviews or appearance-sensitive conversions, read [fidelity.md](references/fidelity.md). Compare visual details and semantic content separately; node counts do not measure drawing fidelity.

For diagram transformations, read [shape-selection.md](references/shape-selection.md) to select elements from explicit roles and [diagram-families.md](references/diagram-families.md) for Flowchart, BPMN, ER/UML, lanes, hierarchy/sequence and cloud choices. Query `scripts/native_catalog.py --type <type>` or `--cloud-class <literal>` for a compact checked contract. Do not read the entire source catalog during normal use.

## Export Lucidchart to SVG

Read [editor-workflows.md](references/editor-workflows.md). Use an existing signed-in browser or connected tool, inspect the current UI, select the requested page, then **More → Export → SVG → Download**. Check crop, background, and layer visibility. Follow observed labels if the UI differs.

Capture the browser download using the available tool and save it to the exact requested path. If the tool cannot retrieve download bytes, report that boundary and preserve the document link and export settings; do not claim a download or scrape the editor canvas as a replacement. The currently documented REST document-image endpoint does not offer SVG; do not invent an `Accept: image/svg+xml` route.

Inspect the downloaded file:

```sh
uv run --script <skill-dir>/scripts/inspect_svg.py inspect diagram.svg --report inspection.json
```

Confirm SVG XML rather than an HTML login/error response, dimensions, expected labels, vector elements, and embedded images. The report is a literal XML/resource inventory, including definitions/hidden text; it does not compute rendering, CSS cascade or native mapping eligibility. Lucid exports can outline text as paths; missing `<text>` elements alone do not prove missing visible labels. Render a local copy with the available browser/renderer after checking active content and external references. Inspect clipping, fonts, arrowheads, and page coverage. Keep the original bytes; any repaired derivative needs its own filename and a change note.

## Create Lucidchart content from SVG

Inspect the source with the same command and save its report once. Check `ready_for_upload` before preparation. If false, use the existing diagnostic to plan deliberate repairs; do not retry a blocked preparation unchanged. For an eligible visual asset, read [editor-workflows.md](references/editor-workflows.md), prepare a checked byte-preserving copy, then import through the SVG/custom-shape controls available in the account:

```sh
uv run --script <skill-dir>/scripts/inspect_svg.py prepare source.svg --output upload.svg
```

`prepare` blocks detected active content, external dependencies, and `foreignObject` content needing review. Its static inspection is conservative, not a browser sandbox. Warnings such as filters or embedded raster images still require visual checking. It does not simplify paths, flatten CSS, or guarantee Lucid parser acceptance. Correct incompatibilities deliberately in a separate derivative; preserve labels when replacing `foreignObject` with SVG text.

For editable content, read [native-reconstruction.md](references/native-reconstruction.md). Reconstruct the semantic diagram from SVG/source data; retain labels, directions, branch labels and endpoints. For explicit SVG metadata, read [svg-mapping.md](references/svg-mapping.md) and use its bounded extraction profile:

```sh
uv run --script <skill-dir>/scripts/extract_native.py source.svg --coordinates viewport-pixels --output graph.json --report mapping.json
```

Choose the coordinate mode explicitly. If the saved inspection already has blocking resource/active-content flags, stop reconstruction of that unchanged source and deliver the existing diagnostic; repair a separate derivative before extracting. A blocked extraction produces a ledger and no graph. Do not infer missing topology or silently discard rich artwork. Use native Mermaid when the current family is supported and automatic layout is acceptable. For fixed positions, compile supplied/recovered graph data:

```sh
uv run --script <skill-dir>/scripts/build_native.py graph.json --output diagram.lucid --document-json document.json --report native-report.json
```

Read [standard-import.md](references/standard-import.md) only for this package/API route. Submit a new document through an already authorized authenticated integration, or deliver the package and explain the missing prerequisite. SVG images embedded in Standard Import are converted to PNG; use native primitives for editable reconstruction.

For explicit org-chart/mind-map data, sequence markup or assisted layout, read [generated-layouts.md](references/generated-layouts.md) and use `scripts/build_generated.py`. This checked route preserves supplied data/markup while Lucid generates geometry. Use it only when reflow is acceptable.

After live creation/import, inspect the returned document, edit one label, move one shape, confirm attached connectors follow, and undo the probe edits. Match node/edge counts and inspect visual losses. A local compiler pass proves the documented subset and package structure, not upstream acceptance.

## Deliver

Provide exact paths and/or the actual Lucid link, page coverage, route, editability, validation and material changes/omissions. Base fidelity notes on source inspection, extraction ledger, emitted compiler report and rendered evidence; never turn structural counts into an overall visual percentage. Distinguish local preparation from live verification. Check official sources before relying on current entitlements or UI/API behavior. Do not start a paid trial, create credentials or change sharing as a workaround.
