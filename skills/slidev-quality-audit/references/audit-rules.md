# Slidev Quality Audit Rules

## Contents

- [Default Interpretation](#default-interpretation)
- [Rules and Recommended Fixes](#rules-and-recommended-fixes)
- [Threshold Tuning](#threshold-tuning)
- [Validation Pattern](#validation-pattern)
- [Readable Compactness Trial](#readable-compactness-trial)
- [Native SVG Typography and Metadata](#native-svg-typography-and-metadata)
- [Solid Category Treatment](#solid-category-treatment)

Use this reference when interpreting `scripts/audit-slidev-quality.ts` reports or tuning thresholds.

## Default Interpretation

Treat error-level findings as likely presentation defects unless the slide intentionally uses bleed art, hidden alternate states, or constrained scroll regions. Treat warning-level findings as review prompts that often improve final screenshots and video output, but can be acceptable when the deck has a deliberate dense or technical style.

Prefer fixing layout structure before suppressing findings. Use exception markers only for content that is intentionally outside the normal readable slide surface.

## Rules and Recommended Fixes

For marked SVG connections, [the arrow audit](arrow-audit.md) defines `arrow-low-contrast` and `arrowhead-covered`. These rules inspect shafts, actual referenced head instances, alpha composites, and filled path backings at a minimum of 3:1 non-text contrast.

| Rule | What It Detects | Recommended Improvement |
| --- | --- | --- |
| `layout-missing` | No visible `.slidev-layout` was found. | Fix the Slidev route, server startup, or slide rendering error before judging visual quality. |
| `blank-slide` | The active slide has almost no visible text, media, canvas, SVG, or elements. | Restore the missing component, wait for data, or remove the empty slide. |
| `viewport-overflow` | The page or active slide creates horizontal or vertical overflow. | Constrain containers with `max-width`, `min-width: 0`, stable grid tracks, and `overflow: hidden` only for decorative art. |
| `off-slide-element` | A visible element extends beyond the slide frame. | Resize, wrap, or reposition it; mark only intentional bleed/crop content with `data-allow-overflow`. |
| `clipped-text` | A text element has scroll dimensions larger than its visible box. | Increase the container, reduce copy, lower the local font size, or allow wrapping. |
| `hidden-final-text` | Text remains hidden after the final detected click state. | Remove stale hidden content, add the missing click step, or mark intentional alternates with `data-allow-hidden`. |
| `overlapping-text` | Two visible text blocks intersect significantly. | Adjust grid/flex constraints, add gap, reduce text, or fix absolute positioning. |
| `covered-content` | The center of every rendered fragment of a visible text/media element is covered by another element. | Move the overlay, lower z-index, add padding, or make the overlay non-covering. |
| `low-contrast-text` | Computed foreground/background contrast falls below the configured threshold. | Darken the text, lighten the background, or add a solid text backing behind image/gradient areas. |
| `off-palette-paint` | A visible authored CSS/SVG base paint is outside the selected exact colorset. | Replace it with an exact token from the in-bundle palette; rerun every click state using `--colorset colorset1` or a justified `colorset2`. |
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

The default palette is colorset1. Pass `--colorset colorset2` for a deck that
deliberately assigns full-color categorical roles. The rule checks computed text,
background, visible borders, outlines, and SVG fill/stroke/stop paints, preserving
alpha. Mark only the imported source-media element with `data-source-media` when
source pixels or a verified brand logo must retain their identity; do not mark a
slide, panel, or chart wrapper containing authored chrome.

The computed-style check cannot prove Canvas drawing colors, every pseudo-element,
or every gradient endpoint. Inspect editable chart options and Canvas/SVG exports
alongside the report, and sample animation states when authored color properties
change between clicks. Anti-aliasing and compression pixels are derived output,
not additional authored palette tokens. Follow [the colorset contract](colorset-contract.md).

Use threshold flags when a deck has a deliberate house style:

- `--min-font-size 11` for dense technical appendix slides.
- `--min-contrast 3.5` for large display text, while keeping body text at 4.5 or higher when possible.
- `--max-words 120` for instructional decks that intentionally include more copy.
- `--safe-margin 12` for edge-to-edge visual systems that still keep text readable.
- `--overflow-tolerance 8` for animated decks where subpixel transforms create small false positives.

Do not lower thresholds globally when only one decorative or animated element is intentional. Add a local exception marker instead. Use `data-allow-overflow` for deliberate bleed, crop, or split-text wrapper clipping.

Line-wrapped inline text can have a bounding box whose geometric center falls in
another inline token even though the painted fragments do not overlap. Probe the
centers returned by `getClientRects()` and report `covered-content` only when no
rendered fragment resolves to the text node, one of its descendants, or an
ancestor. Do not suppress a whole code block to work around this geometry case.

## Validation Pattern

1. Run a diagnostic audit without `--strict` and with `--screenshots all`, saving the report and native captures in a before directory under `projects/<project-id>/artifacts/reports/`.
2. Fix the highest-severity real issues first.
3. Re-run with the same viewport and thresholds in a separate after directory; use `--strict --screenshots all` for the final resolved-state gate.
4. Confirm that the affected rule counts dropped and no new findings appeared on nearby slides.
5. Open the exact `states[].screenshot` paths recorded in JSON and preserve both before/after reports and captures. The auditor's native Chromium screenshots satisfy ordinary browser review; preserve any capture referenced by a delivered report.
## Readable compactness trial

For connected explanatory diagrams, perform this trial before final acceptance.
After restoring a readable baseline, create and natively render at least one
actual tighter geometry candidate at the same viewport with the same full labels
and readable type/head/stroke dimensions. Reduce surplus padding, rank gaps or
route detours first. Preserve the baseline and candidate source/native captures;
a hypothetical gap change or a written rejection alone is not a trial.

Compare occupied node/route bounds or repeated gap/run measurements, then inspect
all full labels, visible heads/shafts, source/target attachment, separate unrelated
lanes and applicable click/motion envelopes. Accept the smaller candidate when
these checks pass. Reject it only for a specific observed overlap, clipping,
obscured head, ambiguous attachment/route or lost motion/readability clearance.
Vague breathing room, occupancy or unchanged comprehension is insufficient.
Optionally try one further local refinement, then keep the tightest inspected
passing candidate. Record actual native image paths, dimensions and acceptance
or concrete rejection evidence; do not claim globally optimal packing. Preserve
quantitative chart scales, axes, legends and useful information dimensions.

## Native SVG typography and metadata

Automated DOM bounds can miss painted SVG text failures even with zero findings.
Inspect the actual native text/arrow image before accepting an audit.
Inline SVG presentation attributes can lose to a Slidev theme's CSS. If the
browser capture shows oversized or displaced text despite a declared `font-size`,
set an explicit local text style or a scoped SVG text rule at the intended size;
retain full labels and compare the next native capture. Use a `foreignObject`
label only when the deck actually needs HTML layout, rather than lowering type
or accepting clipping.

SVG `title`, `desc`, and `metadata` are nonvisual accessibility/authoring content.
They do not count as hidden presentation text. An ordinary hidden paragraph,
label, or click-state explanation remains subject to `hidden-final-text`.

For a NEW scratch fixture, run from its task workspace:

```powershell
uv run --script <skill-root>/scripts/prepare-audit-deck.py --deck ./deck
```

The helper validates the package before any install, creates the tested package
only when absent, and passes the resolved deck prefix to npm. It retains existing
packages and uses an existing lock with npm ci. Write the supplied slides next,
then run npm --prefix /path/to/deck run build before the first native audit.
Preserve supplied projects' existing setup workflow, locks and dependency choices.
The bundled template records a dependency set exercised by native browser validation. A FloatingVue/twoslash console error
is a runtime problem, not a reason to suppress browser-console findings; use a
compatible dependency override and rerun the audit.

## Solid category treatment

Mark authored category shapes with `data-category-id` so the browser audit can distinguish decoration from axes, class compartments, chart whiskers and connectors. The audit reports `premature-category-outline` when a visible marked shape has a border before the selected palette's usable unique solid colors are exhausted. An overflow outline requires `data-colorset-overflow`; an explicit meaningful data boundary or user-requested outline uses the narrow `data-allow-category-outline` exception. This gate sees the current visible state; independently check a category allocation manifest when categories are paginated, hidden, or distributed across scenes. The existing contrast rule remains required for black/white inside labels, and Canvas category boundaries require source/option inspection.

When maintaining this bundle, validate native capture defaults and metadata classification with
`uv run --script <skill-root>/scripts/test_audit_capture.py --work-dir <work-dir>`
after installing the scratch template dependencies in `<work-dir>/deck`. The
regression retains a clean-state screenshot, reports actual hidden paragraph
copy, preserves explicit issues-only capture, and verifies scratch setup ownership
and existing-package preservation. Native captures and source geometry are the
ordinary review surface; do not add ad hoc pixel analysis or undeclared Pillow use.
