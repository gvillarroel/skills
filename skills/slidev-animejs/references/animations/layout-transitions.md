# Layout Transitions

## Use When

Use layout animation when the DOM structure or CSS layout changes: sorting cards, switching columns to rows, moving an item between groups, or showing before-after organization.

## Anime.js Pattern

Use `createLayout(root)` and either `layout.record()` plus `layout.animate()` or `layout.update(() => changeDomState())`. In Vue, prefer `record()`, update reactive state, wait for `nextTick()`, then animate when the DOM change is framework-owned.

## Slidev Pattern

Keep the layout root fixed in size. Let Anime.js animate child geometry while the slide frame stays stable. Use `$clicks` to switch a class, ordering, or parent container.

## Tested Fixture

The `layout-transitions` slide changes a tile group between grid and row arrangements and animates the transition.

## Pitfalls

- Layout animation needs real element boxes, so run it after mount and after the target is visible.
- Avoid hidden `display: none` ancestors during measurement.
- Keep labels short so moving tiles do not overlap.
