# Tool Routing and Ownership

## Producer contract

Request only the artifacts needed by the scene. Every producer handoff must include:

- `assetId`: stable lowercase hyphen-case ID.
- `producerSkill`: exact owning skill name.
- `path`: project-relative output path.
- `kind`: `svg`, `gif`, `raster`, `html`, `video`, or `audio`.
- `sha256`: digest of the finished artifact.
- `intrinsic`: width/height or SVG `viewBox`.
- `background`: transparent, opaque color, or renderer-owned.
- `ports`: semantic connection points with stable IDs and normalized coordinates or selectors.
- `states`: controllable semantic states and the mechanism used to select them.
- `clock`: `static`, `master`, or `autonomous`; finished deterministic work rejects autonomous motion without an adapter.
- `validationReport`: project-relative passing report created by the producer.
- `provenance`: origin and rights/attribution status.

Do not accept screenshots of vector diagrams when the SVG is available. Do not accept an HTML chart when the scene requires selector-level SVG interaction unless the producer also exposes a frame adapter and semantic ports.

## Selection table

| Need | Producer | Preferred handoff |
| --- | --- | --- |
| Custom data geometry, topology, simulation, linked states | `d3` | Inline-safe SVG or deterministic HTML with ports |
| Conventional chart and chart grammar | `echarts-animated-svg` | Static SVG plus animated SVG and replay/state metadata |
| UML, architecture, deployment, cloud notation | `plantuml-colorset-renderer` | SVG plus source and render report |
| Flow, sequence, state, ER, journey, schedule, relationship diagram | `mermaid` | Accessible SVG plus source and render report |
| Depth, particles, camera, materials, WebGL | `threejs-animated-3d` | Self-contained HTML with a master-time adapter |
| Raster illustration, texture, cutout, plate | `imagegen` | PNG/WebP with crop and transparency metadata |
| Animated SVG to GIF | `animated-svg-to-gif` | GIF and conversion manifest |
| SVG-only sequence or Manim render | `manim-svg-video` | MP4 and composition manifest |
| Slidev component choreography | `slidev-animejs` | Built deck; record through this skill |
| Slidev chart story | `slidev-echarts` | Built deck; record through this skill |

## Routing decisions

1. Choose by semantic responsibility, not by the easiest available renderer.
2. Give each asset exactly one producer owner.
3. Require a producer report before marking an asset ready.
4. Preserve the producer output unchanged under `artifacts/`; apply crop, scale, ID namespacing, and composition in the video renderer.
5. When two producers can satisfy the request, prefer the one whose native grammar matches the facts. Use D3 only when custom geometry or interaction is material.
6. Record a fallback reason when the preferred skill is unavailable. The fallback must still emit the same handoff fields.

## Interaction capability levels

- `opaque`: the video can position, crop, transform, reveal, hide, and connect to external normalized ports.
- `selector`: inline SVG or same-origin HTML exposes stable selectors for internal anchors and emphasis.
- `stateful`: the producer exposes named states controlled by the master clock or scene bus.
- `bidirectional`: pointer or scene events can update the producer state and the producer can emit semantic events. Use only for interactive deliverables; deterministic video capture must replay a recorded event sequence.

Declare the lowest sufficient level. Do not claim selector or stateful control for a raster image or ordinary GIF.
