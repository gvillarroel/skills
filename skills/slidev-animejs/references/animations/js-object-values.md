# JavaScript Object Values

## Use When

Use JavaScript object animation for counters, meters, synthetic data values, and computed presentation state that is not itself a DOM style property.

## Anime.js Pattern

Animate a plain object with `animate(object, { value })` and render changes in `onUpdate`. This keeps Vue state simple while Anime.js owns the interpolation.

## Slidev Pattern

Keep the rendered value deterministic for screenshot and export workflows. Use the object state to update text, CSS custom properties, SVG attributes, or Vue refs.

## Tested Fixture

The `js-object-values` slide animates a numeric score and a progress meter from a JavaScript object, with click states changing the target value.

## Pitfalls

- Always update visible DOM in `onUpdate`; object animation alone has no visible output.
- Clamp numbers before rendering them into narrow labels.
- Avoid random counters in acceptance decks.
