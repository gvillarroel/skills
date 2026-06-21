# Text Split

## Use When

Use split text animation for title reveals, word-by-word emphasis, code phrase callouts, and compact typography moments.

## Anime.js Pattern

Use `splitText(target, options)` to create lines, words, or chars, then animate the returned groups with `animate()` and optionally `stagger()`.

## Slidev Pattern

Call `splitText()` after mount and revert it before reruns or unmounts. Keep accessibility enabled unless a custom accessible fallback is provided.

## Tested Fixture

The `text-split` slide splits a heading into characters and reveals them with staggered vertical motion.

## Pitfalls

- Repeatedly splitting without `revert()` creates nested wrappers.
- Do not split long paragraphs; it creates too many DOM nodes for presentation mode.
- Check line wrapping at the target viewport before final export.
