# Text Scramble

## Use When

Use scramble text for decoding, status changes, security themes, or dramatic replacement of a short phrase.

## Anime.js Pattern

Use `scrambleText(parameters)` as a function-based tween value for `innerHTML` in `animate()`. `innerHTML` is preferred because the helper uses nonbreaking spaces internally.

## Slidev Pattern

Use short phrases and deterministic target text. Trigger the phrase choice from `$clicks` when the slide compares states.

## Tested Fixture

The `text-scramble` slide reveals a short message and changes the target phrase based on click state.

## Pitfalls

- Scrambling long copy is hard to read and noisy in recordings.
- Keep monospaced or tabular styling if character width changes cause visible jitter.
- Avoid using it for essential accessibility-only content.
