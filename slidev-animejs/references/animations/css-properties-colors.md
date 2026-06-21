# CSS Properties, Colors, And Variables

## Use When

Use CSS property animation when the story needs a size, radius, color, or CSS variable to change rather than only position.

## Anime.js Pattern

Animate properties such as `width`, `borderRadius`, `backgroundColor`, and custom properties like `--accent`. Keep the custom property registered in CSS when it drives derived styles.

## Slidev Pattern

Use property animation sparingly in Slidev because width and height can affect layout. Constrain the animated target inside a fixed stage.

## Tested Fixture

The `css-properties-colors` slide changes a panel width, radius, color, and CSS variable-driven accent.

## Pitfalls

- Avoid animating parent dimensions that affect neighboring slide content.
- Prefer color changes with sufficient contrast in every intermediate state.
- CSS variables are useful for synchronized child effects, but keep names local to the component.
