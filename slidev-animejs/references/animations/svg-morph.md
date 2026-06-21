# SVG Morph

## Use When

Use SVG morphing when the story changes one shape into another: state transitions, before-after icons, changing product states, or conceptual transformations.

## Anime.js Pattern

Use `svg.morphTo(shapeTarget, precision)` as the target value for `d` or `points`. Keep the source and target as path, polygon, or polyline elements.

## Slidev Pattern

Place the visible source and hidden target in the same SVG. Use `$clicks` to choose morph direction or target, but keep shapes deterministic.

## Tested Fixture

The `svg-morph` slide morphs a blob-like path into a sharper target path and alternates the transition.

## Pitfalls

- Complex paths can create surprising interpolation; simplify shapes for slides.
- Keep fill and stroke consistent unless color change is part of the story.
- Verify morph output in browser because build success does not prove the interpolated shape is readable.
