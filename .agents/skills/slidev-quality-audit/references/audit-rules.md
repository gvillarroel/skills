# Slidev Quality Audit Rules

Use this reference when interpreting `scripts/audit-slidev-quality.ts` reports or tuning thresholds.

## Default Interpretation

Treat error-level findings as likely presentation defects unless the slide intentionally uses bleed art, hidden alternate states, or constrained scroll regions. Treat warning-level findings as review prompts that often improve final screenshots and video output, but can be acceptable when the deck has a deliberate dense or technical style.

Prefer fixing layout structure before suppressing findings. Use exception markers only for content that is intentionally outside the normal readable slide surface.

## Rules and Recommended Fixes

| Rule | What It Detects | Recommended Improvement |
| --- | --- | --- |
| `layout-missing` | No visible `.slidev-layout` was found. | Fix the Slidev route, server startup, or slide rendering error before judging visual quality. |
| `blank-slide` | The active slide has almost no visible text, media, canvas, SVG, or elements. | Restore the missing component, wait for data, or remove the empty slide. |
| `viewport-overflow` | The page or active slide creates horizontal or vertical overflow. | Constrain containers with `max-width`, `min-width: 0`, stable grid tracks, and `overflow: hidden` only for decorative art. |
| `off-slide-element` | A visible element extends beyond the slide frame. | Resize, wrap, or reposition it; mark only intentional bleed/crop content with `data-allow-overflow`. |
| `clipped-text` | A text element has scroll dimensions larger than its visible box. | Increase the container, reduce copy, lower the local font size, or allow wrapping. |
| `hidden-final-text` | Text remains hidden after the final detected click state. | Remove stale hidden content, add the missing click step, or mark intentional alternates with `data-allow-hidden`. |
| `overlapping-text` | Two visible text blocks intersect significantly. | Adjust grid/flex constraints, add gap, reduce text, or fix absolute positioning. |
| `covered-content` | The center of a visible text/media element is covered by another element. | Move the overlay, lower z-index, add padding, or make the overlay non-covering. |
| `low-contrast-text` | Computed foreground/background contrast falls below the configured threshold. | Darken the text, lighten the background, or add a solid text backing behind image/gradient areas. |
| `tiny-text` | Visible text is below the configured minimum font size. | Use larger type, fewer words, or split content across slides. |
| `zero-size-media` | Canvas, SVG, image, video, iframe, object, or embed surfaces render too small. | Give the container stable dimensions and verify hidden Slidev slides resize after activation. |
| `broken-media` | Images or videos report failed intrinsic loading. | Fix the asset path, bundler import, public directory location, or network dependency. |
| `blank-canvas` | A visible canvas samples as blank or nearly blank. | Wait for chart initialization, verify data and renderer setup, and resize after the slide becomes visible. |
| `blank-svg` | A visible SVG has no meaningful graphic or text content. | Fix SVG generation, viewBox, child elements, or component conditions. |
| `distorted-media` | Rendered media aspect ratio differs materially from its intrinsic ratio. | Use `object-fit`, preserve aspect ratio, or crop intentionally with an exception marker. |
| `unchanged-click-state` | A slide with click states does not visibly change while advancing clicks. | Bind `$clicks`, fix `<v-clicks>` structure, or remove click instructions that do not alter the visual. |
| `dense-slide` | The slide exceeds the word-count or text-block thresholds. | Split the content, replace prose with a diagram, or move details to speaker notes. |
| `unsafe-margin` | Important text sits too close to the slide frame edge. | Add padding or move text inward so exported screenshots and videos do not feel cropped. |
| `browser-console-error` | The browser emitted console errors. | Fix runtime errors before treating the deck as visually validated. |
| `page-error` | Playwright observed an uncaught page error. | Fix the exception and rerun the audit. |

## Threshold Tuning

Use threshold flags when a deck has a deliberate house style:

- `--min-font-size 11` for dense technical appendix slides.
- `--min-contrast 3.5` for large display text, while keeping body text at 4.5 or higher when possible.
- `--max-words 120` for instructional decks that intentionally include more copy.
- `--safe-margin 12` for edge-to-edge visual systems that still keep text readable.
- `--overflow-tolerance 8` for animated decks where subpixel transforms create small false positives.

Do not lower thresholds globally when only one decorative or animated element is intentional. Add a local exception marker instead. Use `data-allow-overflow` for deliberate bleed, crop, or split-text wrapper clipping.

## Validation Pattern

1. Run the audit on the current deck and save the report under `projects/<project-id>/artifacts/reports/`.
2. Fix the highest-severity real issues first.
3. Re-run the same command.
4. Confirm that the affected rule counts dropped and no new findings appeared on nearby slides.
5. Keep the before/after reports only under `projects/<project-id>/artifacts/reports/` when they are useful validation artifacts.
