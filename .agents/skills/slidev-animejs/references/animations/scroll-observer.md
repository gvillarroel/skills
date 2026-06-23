# Scroll Observer

## Use When

Use scroll synchronization for scrollable code panes, long diagrams, walkthrough panels, or embedded page sections inside a Slidev slide.

## Anime.js Pattern

Use `onScroll(parameters)` as `autoplay` for timers, animations, or timelines. Provide an explicit `container` when the scroll area is inside the slide.

## Slidev Pattern

Prefer an internal scroll panel over page scroll. Slidev controls navigation with keyboard and wheel events, so a contained panel avoids fighting slide navigation.

## Tested Fixture

The `scroll-observer` slide uses an internal scroll container and a target card whose animation is driven by `onScroll`.

## Pitfalls

- Do not rely on document scrolling inside Slidev.
- Refresh observers if the container size changes after a click.
- Disable debug overlays in polished decks unless the slide is explicitly teaching the API.
