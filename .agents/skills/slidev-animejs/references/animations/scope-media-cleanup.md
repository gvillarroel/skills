# Scope, Media Queries, And Cleanup

## Use When

Use scopes for every nontrivial Slidev Vue component that owns Anime.js animations. Use media queries when slide motion should adapt to size or reduced-motion preferences.

## Anime.js Pattern

Use `createScope({ root, defaults, mediaQueries }).add((self) => { ... })`. Read `self.matches` for media query state and call `scope.revert()` on cleanup.

## Slidev Pattern

Treat scope as the component boundary. Use it to prevent selectors from matching other slides and to centralize cleanup when the same slide is revisited.

## Tested Fixture

The `scope-media-cleanup` slide uses scoped defaults and a reduced-motion media query to animate only local targets.

## Pitfalls

- Scope does not replace explicit cleanup for external event listeners.
- Keep selectors simple and local.
- Do not set global Anime.js defaults when component-local defaults are enough.
