# Kinetic Glyph Mosaic

- **Pattern ID:** `d3-kinetic-glyph-mosaic`
- **Family:** Text interaction
- **Use when:** Text should look like ordinary bold typography at rest, then reveal that its glyphs are assembled from squares, short line segments, dots, or mixed geometry on hover, keyboard focus, or press.
- **Preferred script:** `scripts/build_kinetic_type.py`
- **Output:** Deterministic, offline HTML with inline SVG, an unchanged bundled D3 runtime, pointer/keyboard/touch interaction, and a reduced-motion state.

## Route Contract

Use this pattern for deconstructed typography, kinetic lettering, particle text, mosaic text, geometric wordmarks, hover-reveal headlines, and requests that describe letters as being built from pieces. Do not substitute `d3-word-cloud`, which lays out weighted words, or `d3-text-tween`, which changes label values. For a static logo whose texture must remain subordinate to a brand wordmark, use the logo route instead.

Run the builder help before constructing an artifact:

```powershell
python "<d3-skill>/scripts/build_kinetic_type.py" --help
```

Generate the four-material showcase:

```powershell
python "<d3-skill>/scripts/build_kinetic_type.py" kinetic-type.html
```

Generate exact custom text and material mappings:

```powershell
python "<d3-skill>/scripts/build_kinetic_type.py" kinetic-type.html `
  --text "BUILD" --variant tiles `
  --text "WITH" --variant lines `
  --text "MOTION" --variant hybrid `
  --motion energetic `
  --colorset colorset1 `
  --seed 73
```

Use `colorset2` only when the user explicitly requests an extended, full-color, or multicolor result. A request for a cool, polished, or colorful-looking interaction does not by itself select colorset2.

## Data Contract

- Preserve every requested text value exactly after whitespace normalization required by the output contract. Never replace words merely because a shorter sample fits more easily.
- Accept one to eight text values of at most 40 characters each. Use one material for every item or map one material to each item in order.
- Supported materials are `tiles`, `lines`, `dots`, and `hybrid`. Custom text defaults to `hybrid` when the user asks for several component kinds without assigning them individually.
- Preserve the selected `colorset`, `motion`, integer seed, title, item order, and exact output path.
- Expose `data-pattern-id="d3-kinetic-glyph-mosaic"`, per-card `data-variant`, and rendered `data-piece-count`, `data-tile-count`, `data-line-count`, and `data-dot-count` hooks.

## Geometry Contract

1. Keep a real SVG `<text>` element as the readable idle layer. This is the semantic and visual fallback; do not replace it with hundreds of pieces at rest.
2. Wait for `document.fonts.ready`, then use the same family, weight, size, alignment, and baseline in an offscreen canvas and the visible SVG text.
3. Rasterize only for alpha sampling. Walk a deterministic grid through the glyph silhouette and keep points whose alpha exceeds the fixed threshold.
4. Bind the retained points through a D3 keyed join. Give every point a stable item-and-ordinal ID and create its SVG geometry beneath a `.piece-layer` group.
5. Keep the component layer unclipped when pieces must break outside the original silhouette. A text clip path is suitable only when motion must remain inside the letterforms.
6. Fit long text by reducing the shared SVG/canvas font size before sampling. Do not stretch glyphs non-uniformly or allow visible text to leave the `viewBox`.

The builder uses the browser's actual glyph rasterization rather than a hand-authored bitmap alphabet. This preserves arbitrary user text and makes the normal text layer align with the sampled component positions in the same browser.

## Material And Motion Contract

- **Tiles:** Use square marks with narrow gaps. Hold the initial glyph state briefly, then apply seeded translation, rotation, and scale so the type fractures into a block mosaic.
- **Lines:** Use short square-capped segments with deterministic angles. Animate translation and dash offset so the letter appears to scan, shear, or sweep.
- **Dots:** Use compact circles. Move them through at least two seeded offset phases so their motion reads as orbital or pulsing rather than as tile rotation.
- **Hybrid:** Assign squares, lines, and dots deterministically within one sampled silhouette. Retain separate classes and keyframes so the materials visibly behave differently.

Derive motion from the stable seed, item index, and piece ordinal. Never call `Math.random()`. Keep the first 10–15% of each activation close to the assembled glyph so viewers understand what is decomposing before the pieces move.

At rest, show the normal text at full opacity and keep `.piece-layer` at zero opacity. On hover, focus, or pinned press, reduce the normal text to a faint registration layer and reveal the components. Reset cleanly when the interaction ends; repeated activation must not append geometry or listeners.

## Interaction And Accessibility

- Put each kinetic word inside a native `<button type="button">` so pointer, keyboard, and touch activation share one target.
- Use hover and `:focus-visible` as transient reveals. Use press/click to toggle a persistent `.is-pinned` state and keep `aria-pressed` synchronized.
- Give every SVG a direct `<title>`, direct `<desc>`, stable `viewBox`, explicit font family, and active-colorset metadata.
- Keep the exact readable word in the normal SVG text layer even while component geometry has `aria-hidden="true"`.
- Under `prefers-reduced-motion: reduce`, reveal the static component construction on activation but disable all component animation. Do not hide either the idle word or the active component state.
- Preserve a strong non-color focus outline and pair color changes with the visible geometry change.

## Minimal Manual Recipe

If the builder cannot express a required live-page contract, recreate only this compact mechanism instead of reading a gallery fixture:

1. Author the accessible SVG base text and an empty `.piece-layer`.
2. Inline the bundled D3 runtime unchanged inside `<script id="d3-runtime">`.
3. Wait for fonts, fit the text to the SVG width, and paint the exact word into an offscreen canvas.
4. Sample alpha on a fixed grid, derive stable piece records, and use `selection.data(records, d => d.id).join(...)` to build geometry.
5. Store deterministic motion values in CSS custom properties and select material-specific keyframes with stable classes.
6. Reveal via hover/focus/pinned selectors, add click state with D3, and implement the reduced-motion static reveal.
7. Publish diagnostics only as stable metadata or a small `window.__kineticTypeDiagnostics` object; do not expose the canvas or rely on it as the visible output.

## Validation

Run only the shipped runtime checks after the final write. Replace `kinetic-type.html`
with the exact requested output path and replace the count, metadata, and ordered
text values with the requested contract:

```powershell
python "<d3-skill>/scripts/check_self_contained_html.py" kinetic-type.html
python "<d3-skill>/scripts/check_palette_contract.py" kinetic-type.html --colorset colorset1
python "<d3-skill>/scripts/check_visual_contract.py" kinetic-type.html --require-class "kinetic-word:4" --require-attribute "data-pattern-id=d3-kinetic-glyph-mosaic" --require-attribute "data-colorset=colorset1" --require-attribute "data-motion=energetic" --require-attribute "data-seed=73" --ordered-text "BUILD" --ordered-text "WITH" --ordered-text "MOTION"
python "<d3-skill>/scripts/render_d3_svg.py" kinetic-type.html --selector "svg#kinetic-word-1" --output kinetic-type-idle.svg --screenshot kinetic-type-idle.png --wait-ms 1200
```

Run `check_visual_contract.py` against the HTML, because the page-level metadata
and complete card set do not survive extraction of one selected SVG. The rendered
SVG and screenshot are visual-inspection evidence, not the input to that HTML
contract check. Acceptance-fixture tests under `assets/examples/` are maintainer
checks and are intentionally absent from a normal runtime payload; never probe for
or invoke them unless the task explicitly supplies a full maintenance payload.

Use the matching colorset2 palette check with `--require-extended` only for an explicit colorset2 artifact. Browser verification must also prove:

- `body[data-render-state="ready"]` and diagnostics report the requested card count;
- every card has a nontrivial piece count and each material exposes only its expected shapes, while `hybrid` exposes all three;
- the idle base text is visible and the component layer is hidden;
- hover and focus reveal components and reduce the base layer;
- two samples taken during active full motion have different piece transforms;
- click toggles `aria-pressed` and a persistent reveal without duplicating pieces;
- reduced motion reveals components but keeps their transforms stable;
- desktop and mobile screenshots keep words, material labels, and focus outlines inside their cards.

## Known Pitfalls

- A canvas/SVG font mismatch produces a visible jump. Use the same font stack and weight and wait for font readiness before both fitting and sampling.
- A text clip path prevents pieces from visibly leaving the glyph. Use sampling plus unmasked SVG marks for deconstruction motion.
- Large per-letter particle counts can make hover sluggish. Prefer an 8–10 px sampling step and simplify motion before increasing density.
- CSS animation on an element can override its SVG `transform` attribute. Anchor every piece in a positioned parent `<g>` and animate the child geometry.
- Remote fonts, CDN D3, generated functional colors, and `Math.random()` break the offline, palette, or deterministic contract.
- An extracted settled SVG preserves the geometry but not the live HTML click behavior. Deliver the HTML when hover/focus/touch interaction is part of the request.

## Isolated Workspace Notes

The script resolves the palette and vendored D3 runtime relative to its own skill directory and writes only to the requested output path. It does not require a repository root, sibling skill, gallery source, package install, network request, or acceptance fixture. Generated artifacts must be written outside the copied skill bundle during isolated validation.
