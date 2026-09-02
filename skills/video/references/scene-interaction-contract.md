# Mixed-Media Scene Interaction Contract

## Model

Use four layers:

1. `canvas`: exact output geometry and master clock.
2. `elements`: specialist-produced assets placed in normalized scene coordinates.
3. `tracks`: deterministic property changes driven by master time or named events.
4. `interactions`: semantic relationships between element ports.

The scene contract is the integration boundary. Producer artifacts never import or call one another.

Start from `../assets/templates/scene-contract.json`. It is a complete worked contract with one selector-addressable SVG, one decoded GIF, both port forms, a state track, an opacity track, an event, and a visible cross-producer handoff. Replace or extend those objects without dropping their required fields. Do not read validator implementation code to reconstruct this schema.

Use exact `producerSkill` IDs: `animated-svg-to-gif`, `browser:control-in-app-browser`, `d3`, `echarts-animated-svg`, `imagegen`, `mermaid`, `plantuml-colorset-renderer`, `playwright`, `repo-native`, `slidev-animejs`, `slidev-echarts`, `threejs-animated-3d`, or `user-provided`. Do not shorten `plantuml-colorset-renderer` to `plantuml`. For an unavailable specialist or project-authored video overlay, use `repo-native` or `user-provided` plus a concrete `fallbackReason`.

## Elements

Each element declares:

- stable `id`, `assetId`, `producerSkill`, `kind`, and project-relative `src`;
- normalized `bounds` (`x`, `y`, `width`, `height`), `zIndex`, `fit`, and `overflow`;
- `intrinsic`, `background`, and `clock` behavior;
- named `ports`, using normalized element-local coordinates or a selector plus anchor;
- optional named `states` exposed by the producer adapter.

Use normalized ports for opaque raster/GIF assets. Use selectors only inside inline SVG or same-origin HTML. Namespace SVG IDs in the composed renderer while keeping the original source unchanged.

## Tracks

A track targets an element and one supported property: `opacity`, `translateX`, `translateY`, `scale`, `rotate`, or `state`. Keyframes carry `at`, `value`, and optional easing. Numeric properties interpolate; state properties step at the keyframe.

Keep geometry tracks separate from semantic state tracks. This makes a handoff auditable: the connector can move while the target diagram independently enters a named state.

## Interactions

An interaction declares:

- stable `id` and semantic `type`;
- `source` and `target` with element and port IDs;
- `start` and `end` times or a named trigger event;
- `channel`: `signal`, `highlight`, `reveal`, `handoff`, `camera-follow`, or `data-state`;
- visual connector rules when geometry is visible;
- `emits` and `consumes` event names when state changes are involved;
- a plain-language `meaning` and at least one validation check.

Require both source and target ports to exist. Require interaction windows to fit the scene duration. Reject direct references to another producer's implementation functions.

## GIF behavior

GIFs have no controllable internal DOM. Use one of these modes:

- `decoded`: decode frames during compositor build and select the frame from master time. Prefer this for deterministic MP4 capture.
- `container`: allow the GIF to run, but interact only with its wrapper through opacity, transform, crop, or connectors. Use only when exact internal timing is not evidence-bearing.

Do not claim that a diagram node reacts to a GIF frame unless the GIF is replaced by a state-addressable source.

## Example: PlantUML + Mermaid + two GIFs

- PlantUML exports an architecture SVG with port `service-out`.
- Mermaid exports a state diagram SVG with port `queue-in` and states `idle` and `processing`.
- GIF A exposes external port `result-center`; GIF B exposes `alert-center`; both use decoded timing.
- The video scene bus draws a signal from `service-out` to `queue-in`, emits `job-arrived`, changes Mermaid to `processing`, reveals GIF A, and later hands off to GIF B.
- PlantUML and Mermaid remain unaware of each other. Their only shared surface is the scene contract.

## Review

Sample before, during, and after every interaction. Verify port alignment, occlusion, z-order, connector continuity, state arrival, deterministic replay, and silent comprehension.
