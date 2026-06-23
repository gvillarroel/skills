# Draggable Interactions

## Use When

Use draggable animation for live prioritization, spatial sorting, interactive affordances, or presenter-controlled demos where moving an object clarifies a point.

## Anime.js Pattern

Use `createDraggable(target, parameters)` with an explicit `container` for Slidev stages. Add snap, axis, or release settings when the interaction needs constraints.

## Slidev Pattern

Keep draggable targets large enough for pointer use and inside a visible bounded container. Provide an initial automated nudge if the deck will be validated without manual interaction.

## Tested Fixture

The `draggable-interactions` slide creates a draggable card inside a bounded zone and nudges it automatically so browser verification can see motion.

## Pitfalls

- Pointer interactions can conflict with Slidev drawing or navigation tools; test in presenter mode.
- Always revert draggable instances on unmount.
- Avoid placing draggable targets over speaker notes or navigation controls.
