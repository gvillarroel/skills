# Engine Controls

## Use When

Use engine controls when a deck needs global speed adjustment, paused preview states, custom frame rate, or deterministic timing experiments.

## Anime.js Pattern

Use the Anime.js `engine` object for global timing parameters and methods such as `pause()` and `resume()`. Prefer temporary changes that are restored during cleanup.

## Slidev Pattern

Use engine controls only in isolated demo slides or intentionally global deck settings. Restore engine state before leaving the component.

## Tested Fixture

The `engine-controls` slide changes engine speed from click state, demonstrates pause and resume, and restores the previous setting on cleanup.

## Pitfalls

- Engine settings are global, so isolate and restore them.
- Global speed changes can affect other active Slidev components.
- Avoid using engine controls as a substitute for per-animation duration and easing choices.
