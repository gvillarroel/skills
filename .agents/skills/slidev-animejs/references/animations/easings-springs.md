# Easings And Springs

## Use When

Use easing comparison when the slide teaches motion feel or when different objects should communicate different material behavior.

## Anime.js Pattern

Use built-in eases, cubic Bezier, steps, irregular, or spring easing strings/functions. Keep spring examples short and visible because spring duration can differ from fixed-duration curves.

## Slidev Pattern

Place curves side by side with identical start and end positions so the difference comes from easing only.

## Tested Fixture

The `easings-springs` slide moves multiple markers with different easing families in parallel.

## Pitfalls

- Do not mix too many easing families in production slides.
- Label the motion clearly when comparing curves.
- Verify that spring motion settles inside the fixed stage.
