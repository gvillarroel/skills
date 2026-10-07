# Reconstruct an SVG diagram as native objects

## Recover meaning first

SVG is a drawing format, not a graph schema. Rounded paths can depict a box, icon, background, or several nodes. Crossing lines may have no semantic connection. Text converted to outlines may have no recoverable label. Preserve the source and identify which interpretations are evidenced and which remain uncertain.

Prefer, in order: original graph/diagram data supplied by the user; explicit `data-*` node/edge metadata and IDs; visible labels and geometry confirmed against a rendered source. If topology remains ambiguous, ask a focused question and continue independent preparation. Do not invent connections merely to make a diagram importable.

Create a mapping/loss ledger alongside the outputs: source element/group ID; native node/edge ID; recovered label/type/endpoint; preserved geometry/style; adaptations and unsupported content. Include node and edge counts. Native conversion is a reconstruction, not lossless SVG round-tripping.

## Choose a native route

- Use Mermaid for a flowchart when labels/topology matter more than original coordinates. Supported Lucid editor conversion can create native shapes without a REST integration, but availability varies by diagram family. Inspect the actual conversion control and verify native editing.
- Use Standard Import for explicit positions and ports. The compiler below intentionally accepts a small documented primitive subset. Rebuild complex domain shapes only when their semantics are known; disclose approximation by rectangles/text instead of claiming native UML/ER/BPMN semantics.
- For artwork, photos, gradients, arbitrary Bézier paths, or animated content, use SVG asset insertion if that satisfies the request. Do not substitute an image for an explicitly editable diagram.

## Compiler input contract

Pass a JSON object with optional `title`, required `nodes`, and optional `edges`. Coordinates are SVG user-space positions mapped to Lucid pixel coordinates; resolve SVG transforms and subtract the viewBox origin before writing this graph. The compiler does not parse SVG, scale transforms, infer endpoints, or assign automatic layout.

Resolve transforms on every ancestor group, not just the shape itself. For an ellipse inside `translate(tx ty)`, top-left bounds are `(cx - rx + tx, cy - ry + ty, 2*rx, 2*ry)`. For example, `cx=80, cy=60, rx=30, ry=20` under `translate(12 18)` becomes `(62,58,60,40)`. A translated rectangle adds the same `tx,ty` to its `x,y`. Transform text bounds and line endpoints too, then check them against the recovered node ports. For nested/general transforms, compose the affine matrices in SVG order and apply them to source points; do not simply add translations across scaling or rotation. Record unsupported rotation/skew as an adaptation because the compiler has axis-aligned boxes only.

```json
{
  "title": "Approval flow",
  "nodes": [
    {"id": "request", "type": "rectangle", "x": 20, "y": 40, "width": 150, "height": 60, "label": "Request", "fill": "#FFFFFF", "stroke": "#333333", "text_color": "#111111", "font_size": 16},
    {"id": "approved", "type": "diamond", "x": 240, "y": 30, "width": 120, "height": 80, "label": "Approved?"}
  ],
  "edges": [
    {"id": "check", "source": "request", "target": "approved", "label": "review", "source_port": {"x": 1, "y": 0.5}, "target_port": {"x": 0, "y": 0.5}}
  ]
}
```

Supported node types: `rectangle`, `ellipse`, `diamond`, `text`. `ellipse` compiles to the documented `circle` shape with a non-square bounding box; disclose this approximation and inspect its live rendering. Labels are plain strings; the compiler escapes them for Lucid formatted text. Text nodes support `text_color` and `font_size`, but reject `fill` and `stroke` because the documented text shape does not accept shape style. IDs must be globally unique, 1–36 characters; colors use `#RRGGBB`. Boxes must be finite, positive in size, nonnegative in position, and contained within 20,000 × 20,000 pixels. Resolve negative SVG origins before compilation.

Ports use normalized coordinates from 0 to 1 within a node's bounds. Defaults connect the right-center source to left-center target. Each edge uses a straight attached native connector with a destination arrow. Choose ports explicitly for other directions and inspect routing after import. Native shapes can overlap or have long labels even when the package is structurally valid; the agent must inspect layout.

```sh
uv run --script <skill-dir>/scripts/build_native.py graph.json --output native.lucid --document-json native-document.json
```

The `.lucid` output is a deterministic ZIP containing root `document.json`. Generated output paths must be outside the read-only skill bundle. Read [standard-import.md](standard-import.md) for submission and authentication.

## Acceptance

Compare all literal labels and node/edge counts. Check edge direction, branch labels, bounding boxes, markers, and blank/omitted artwork. After service import, inspect native object selection, label editing, and attached connectors following a moved shape; undo probe edits. Record which SVG features changed: coordinates/layout, fonts, clipping, filters, animation, group semantics, or domain-specific ports/cardinalities. Keep local package validation and live acceptance separate.
