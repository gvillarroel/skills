# Color and Visual Quality

Use this reference when authoring, recoloring, or visually reviewing a composition. A passing arithmetic or propagation audit does not prove that a diagram is easy to read.

## Own color in the brief

Set the optional top-level `theme` in the brief, then preflight, compile, compose, and audit again. Newly compiled briefs default to `editorial`, the colorset1 red/neutral alias. `classic` is the colorset2 alias. The explicit `colorset1` and `colorset2` preset names are also supported. Existing full plans without a theme resolve to colorset2. All resolved and derived paints stay inside the selected finite palette.

```json
{
  "theme": {
    "preset": "colorset2",
    "colors": {
      "canvas": "#f7f7f7",
      "surface": "#ffffff",
      "ink": "#1c1c1c",
      "muted": "#696969",
      "accent": "#007298"
    },
    "conceptColors": {
      "demand": "#9e1b32",
      "capacity": "#007298"
    }
  }
}
```

This is a theme fragment, not a complete brief. Replace `demand` and `capacity` with actual canonical value IDs. Omit `conceptColors` to use the deterministic palette. Never invent a separate palette filename, unsupported renderer option, or SVG post-processing step.

Supported fields are exactly `preset`, `colors`, and `conceptColors`. `colors` may override `canvas`, `surface`, `ink`, `muted`, `line`, `accent`, `focus`, `warning`, and `danger`. Supply opaque six-digit hex values; the compiler normalizes case and rejects unsupported fields, CSS expressions, missing token owners, off-palette colors and insufficient contrast. It never silently substitutes a user's brand color. Supply a complete compatible palette for a dark surface; changing the background alone may invalidate the existing foregrounds.

The source of truth is the brief. The compiled plan stores the resolved theme, and the SVG's `composition-theme` style block emits its role and `--concept-*` variables. These generated copies are inspectable outputs, not independently editable authorities. Neutral layout tints remain contrast-checked palette tokens. Category surfaces
use their exact solid color; generated `--on-value-*` tokens choose pure black or
white by maximum WCAG contrast against that fill. In navigable worlds, district accents remain the separate spatial-grouping color contract; do not confuse a district accent with a data identity.

## Preserve semantic identity

Assign color by meaning, not by panel position. Direct references and constant-scaled aliases inherit their ancestor token. Override the owning root in `conceptColors`; an override on an alias is rejected with the root ID. Keep different concepts independently labeled. The full `solidSequence` excludes only the actual canvas. Use every unique fill
before repeating; only then add explicit border color/dash/width variants plus
direct labels to preserve identity. Default category nodes have no border. A repeated paint does not imply a shared token owner. Use `colorSource` only for genuine ancestor identity, never to reduce palette size by making unrelated quantities look equivalent.

Repeat labels, exact values, units, and relevant shape or line cues. Color cannot be the only way to tell a relationship or state apart. A finite palette cannot provide arbitrarily many unique colors, and palette membership does not prove that all categories are perceptually distinguishable. For a busy network, reduce the visible concepts to a coherent causal question, keep required intermediate parents, and use the ledger for exact secondary values.

The contract checks `ink`, `muted`, `accent`, `warning`, and `danger` at a minimum 4.5:1 against both canvas and surface; `focus` at 3:1. Solid category fills carry direct black/white labels; a thin
meaningful colored line still needs visible contrast against its local canvas. `line` is decorative. These numerical checks follow [W3C text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) criteria for the intended roles. They do not certify all color-vision conditions. Retain the redundant cues required by [Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

## Pair text with its actual surface

- Decide the background behind the letters before selecting their foreground: canvas, card, colored mark, badge, or inverse navigation panel. A foreground that passes on white can fail on another panel in the same SVG. Avoid brightness guesses and unconditional white-on-accent rules.
- Keep small text at 4.5:1 or better, without rounding a failing ratio upward. Prefer extra margin for small or thin labels. The generator checks all text conservatively at 4.5:1, including large headings. Never reuse a mark's 3:1 allowance for a numeric label.
- Generated `--text-value-*` tokens keep the concept color when readable on the generated neutral surfaces and otherwise use readable ink. The canonical `--concept-*` paint remains exact for solid marks. Use
`--on-value-*` on category surfaces and keep decorative borders absent. For inverse panels, use the generated `--on-ink` and `--on-ink-muted` pair; navigation text and focus borders must be checked against the HUD fill.
- Keep essential label backgrounds opaque during focus. Dim marks without making a text backplate translucent. Reserve a caption band above flows and room below waterfall bars so ribbons, baselines, and card edges do not become the text's background. Use labels beside bars in dense rows. Respect renderer-specific font sizes and size text backplates for those fonts; a global font-size override can spill letters onto colored edges.
- For custom fragments, calculate solid-color pairs with `readable_text(backgrounds, preferred)` from `scripts/theme_contract.py`. If no foreground passes every background under a gradient or image, put the label on an opaque surface or move it outside the mark. Do not change supplied brand paints to conceal an unreadable pairing. Let SVG presentation fills inherit normally; a global `text { fill: ... }` rule can override an explicit label fill.

The bundled browser audit now measures actual background pixels under visible glyphs, using browser-resolved foreground colors and alpha rather than antialiased letter edges. It checks the initial scenario, named scenarios, focused and unfocused text, outer controls, navigation anchor views, reduced motion, and the script-free view. Background gradients and transparent shapes are sampled locally; a majority background color is insufficient.

Inspect `textContrastCheckCount`, `textContrastLabelCount`, and `textContrastIssueCount`. Failed checks name the text, module, local background, and measured ratio. Mixed-color text runs, text strokes/halos, masks, group-opacity compositing, unsupported filters, or more than 961 simultaneously visible text runs remain incomplete and need a simpler text surface or focused manual verification. Hidden, disabled, clipped, or unpainted text is counted separately; small overview text can require a detail view. Passing sampled states does not prove every animation frame or every custom fragment.

## Compose for a reader

- Give each module an optional short `title` naming its subject, such as `Water allocation` or `Capacity pressure`. The title replaces the renderer-name kicker; `assetType` still selects and records the renderer. Keep titles around 28 characters so they fit beside focus controls.
- Write the question as a short sentence and the claim as a concrete interpretation. Keep long methodology in the handoff. Do not fill panels with renderer jargon or repeatedly state that the data are synchronized.
- Use hue for data identity and a restrained accent for controls. Keep panel surfaces neutral so the marks carry the story. Check explanatory text at the intended viewing size, not only in a zoomed crop.
- In a dependency network, inspect arrowheads and incoming/outgoing ports. Separate ports clarify converging paths but cannot guarantee a crossing-free graph. If a long dependency crosses intervening nodes, simplify the selected causal view or choose an explicit connected diagram.
- Inspect the whitespace between copy and marks. Large empty areas beside tiny charts signal a weak module choice or too little content for the allocated space. Prefer a better question and encoding over filler copy.
- Cross-module lines must have visible endpoints and a truthful key. Keep long routes out of title bands and essential marks. A thin line in a gutter can still look like an accidental seam at overview size.

## Close the generation–critique loop

1. Freeze the input brief and capture the initial scenario, a materially changed scenario, and the relevant module crops. Keep all failures and exact output paths.
2. Critique hierarchy, semantic color consistency, readability, spacing, connector clarity, and encoding honesty separately. Cite a visible element or region for every finding. Do not infer numeric correctness or interaction behavior from a screenshot alone.
3. Change the smallest responsible source: brief for content/palette choices; owning renderer or theme contract for a repeatable generation defect. Regenerate from the same brief for a controlled visual comparison. Do not hand-polish only the resulting SVG.
4. Re-run static and browser gates, then review the new evidence. A visual gain cannot excuse an arithmetic, clipping, interaction, or accessibility regression.
5. Test a fresh topic or brand palette with only the updated skill. Treat this as a generalization check and retain unsuccessful attempts. Do not call it a sealed holdout if its feedback helped choose the changes.

When the task explicitly requests a model, record that model for generation and critique. Keep the reviewer unaware of the desired winner when comparing artifacts where practical. Treat preference judgments as observations tied to the reviewed cases, not as universal quality scores.
