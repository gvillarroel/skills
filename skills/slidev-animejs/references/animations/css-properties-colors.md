# CSS Properties, Colors, And Variables

## Use When

Use CSS property animation when the story needs a size, radius, color, or CSS variable to change rather than only position.

## Anime.js Pattern

Animate properties such as `width`, `borderRadius`, `backgroundColor`, and custom properties like `--accent`. Keep the custom property registered in CSS when it drives derived styles.

Select exact paints from [the colorset contract](../colorset-contract.md). Step
categorical color changes while allowing geometry and opacity to interpolate:

```js
import { animate, steps } from 'animejs'
animate(panel, {
  width: '70%',
  backgroundColor: { from: '#ee7f00', to: '#00a58c', ease: steps(1) },
  duration: 1200,
  ease: 'inOutQuad',
})
```

This example deliberately selects colorset2 for independent categories. Use
colorset1's red and neutrals for the default single-emphasis design. Pass the
imported `steps(1)` function to each color property or keyframe; a global geometry
ease would generate intermediate hues, and the string `'steps(1)'` is not the
Anime.js v4 function.

## Slidev Pattern

Use property animation sparingly in Slidev because width and height can affect layout. Constrain the animated target inside a fixed stage.

## Tested Fixture

The `css-properties-colors` slide changes a panel width, radius, color, and CSS variable-driven accent.

## Pitfalls

- Avoid animating parent dimensions that affect neighboring slide content.
- Verify contrast at every discrete color state, including hover, keyframes, and CSS variable-driven accents.
- CSS variables are useful for synchronized child effects, but keep names local to the component.
