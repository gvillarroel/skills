# WAAPI Animations

## Use When

Use WAAPI-powered Anime.js animations for lightweight transform and opacity motion where hardware acceleration and small runtime size matter more than full JavaScript-engine features.

## Anime.js Pattern

Use `waapi.animate(targets, parameters)` for Web Animations API-backed motion. It supports many Anime.js conveniences, but not every JavaScript-engine feature.

## Slidev Pattern

Use WAAPI for repetitive decorative motion, simple transitions, and effects that should remain smooth during presentation. Use the JavaScript engine for SVG morphing, drawables, text helpers, layout, or advanced callbacks.

## Tested Fixture

The `waapi-animations` slide animates multiple pills with WAAPI-backed transforms and opacity changes.

## Pitfalls

- Confirm the feature is supported in the target browser/export path.
- Do not assume every Anime.js JavaScript feature exists in WAAPI mode.
- Keep explicit cleanup for WAAPI animations if they are created outside a scope.
