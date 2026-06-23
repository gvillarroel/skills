# Stagger Sequences

## Use When

Use stagger for repeated elements: grids, menus, matrices, bullet alternatives, cards, and diagram nodes that should read as a group.

## Anime.js Pattern

Use `stagger(value, parameters)` for delay or value distribution. Grid staggers are useful for Slidev because they can reveal a spatial pattern without hand-authoring every delay.

## Slidev Pattern

Keep list and grid item counts deterministic. Use `$clicks` to change the stagger origin, axis, or direction so the same slide can compare reading orders.

## Tested Fixture

The `stagger-sequences` slide animates a four-by-four grid and changes the origin based on click state.

## Pitfalls

- Staggering hundreds of DOM nodes can hurt presenter responsiveness.
- Use CSS grid dimensions that cannot shift when items scale.
- Keep text outside heavily staggered cells unless each label remains readable during motion.
