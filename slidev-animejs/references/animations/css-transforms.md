# CSS Transforms

## Use When

Use transform and opacity animation for ordinary Slidev interface marks: cards, annotations, process markers, callouts, and lightweight diagram emphasis.

## Anime.js Pattern

Use `animate(targets, parameters)` with DOM targets and transform aliases such as `x`, `y`, `scale`, and `rotate`. Combine with `opacity` when the motion needs an entrance or emphasis beat.

## Slidev Pattern

Keep the target inside a fixed-size component stage. Animate descendants from a component root ref or from a `createScope({ root })` selector. Do not animate the outer slide container.

## Tested Fixture

The `css-transforms` slide moves and rotates a foreground card while secondary dots pulse through a scoped selector.

## Pitfalls

- Prefer transforms over layout-changing properties for repeated motion.
- Avoid global selectors because Slidev keeps adjacent slides in the DOM.
- Use stable dimensions so hover, click, and animation states do not reflow the slide.
