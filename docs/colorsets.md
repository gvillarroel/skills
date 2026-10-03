# Colorsets and output coverage

Every authored visual output in this repository must use one active colorset. The exact machine-readable definition is [colorsets.json](colorsets.json). Runtime skills keep their own copy or equivalent finite token definition so an isolated bundle never depends on repository documentation or a sibling skill.

Default to colorset1: solid red and neutral marks on a quiet stage. Use colorset2 when requested or when the output requires simultaneous semantic categories that cannot be distinguished clearly with labels, geometry and neutral/red roles. Record the active colorset in a manifest, SVG attribute or HTML attribute. Keep the choice consistent across panels, previews, exports and video wrappers.

## Solid fills before outline variants

Start filled nodes, cards, bars, cells, badges and 3D objects with one opaque colorset fill and no decorative outline, shadow rim or contrasting edge overlay. A light surface may be useful for layout, but do not make pale fill plus dark border the default semantic style. Preserve connector paths, axes, line drawings, physical mesh structure, licensed source artwork and explicit user style requests.

Assign distinct categories from the active palette's `solidSequence`, excluding the actual canvas color. Base saturated colors come first, followed by dark, bright and neutral solids; soft colors come late. Keep assignments stable across panels, animation states, legends and exports. Similar shades still need direct labels or meaningful geometry. Do not add outlines merely because six semantic base colors have been used: the other usable solid tokens remain available. For a white canvas, colorset1 has 16 usable solid fills and colorset2 has 36; a different canvas excludes that token instead.

For text inside a solid fill, choose exact black `#000000` or white `#ffffff`, whichever has the greater relative-luminance contrast. The palette's `textOnFill` records that decision for every token. Linearize each sRGB channel with `c / 12.92` for `c <= 0.04045`, otherwise `((c + 0.055) / 1.055) ** 2.4`; compute `L = 0.2126 R + 0.7152 G + 0.0722 B`. Compare black contrast `(L + 0.05) / 0.05` with white contrast `1.05 / (L + 0.05)`. Saturation or a simple RGB average is insufficient. Check the actual backing after compositing if transparency is required.

Only after all usable solid fills have assignments, expand the style capacity by cycling those fills with a contrasting palette border color, then border dash and width. Keep the original solid assignments unchanged. Document the overflow mapping and mirror it in legends. A selected or focused interactive control may show a temporary focus indicator; this is an interaction state, not an early categorical style. Light fills with contrasting borders belong to this overflow stage when needed.

Keep overflow borders distinct from their fill and prefer at least 3:1 contrast against it. Use a finite pool of border colors, solid/dashed/dotted traces and widths from 1 to 3 pixels; do not increase widths indefinitely. Once that pool is exhausted, report the limit and use direct labels, geometry or grouping instead of claiming another unique style. On translucent canvases, evaluate text and border contrast against the actual composited backing.

## Arrow paint and terminal placement

Essential arrow shafts and heads must reach at least 3:1 contrast against the actual adjacent paint at readable resting, focus and delivery states. Palette membership alone is insufficient. Include fill paths, regions, shaded 3D backings, alpha compositing and the surface around the terminal. Treat text carried by an arrow as text, using its separate contrast rule. Partial reveal/fade-to-hidden transitions are distinct from an arrow's readable state.

Prefer opaque contrast-safe palette paint and clear route gutters. Keep arrowheads visible outside opaque node silhouettes, aligned to the final path tangent, associated with the intended target port and free of clipping or text overlap. Preserve semantic direction and category meaning. Match marker paint to its edge where the same backing supports it; scope marker variants to that edge when its local backing requires another allowed color. Match `refX`/`refY` to the actual painted tip and account for marker units, transforms, line caps and head size rather than trusting the endpoint attribute alone.

If one color cannot contrast with all crossed surfaces, first reroute or add a small documented terminal clearance. Use a scoped contrast-safe paint change only when the meaningful crossing is unavoidable. Preserve solid borderless nodes instead of adding outlines or general halos to compensate. Imported source arrows retain their source-fidelity contract; authored wrappers and newly generated arrows use this rule.

Validate both shaft and actual referenced head geometry over their real local backings, including paths and transparent regions. Check both palettes, direction reversals, zoom/focus, reduced motion, final export scale and video/3D views when relevant. Retain explicit classifications for ordinary diagram lines and source glyphs so a broad path scan does not invent arrows. The 3:1 graphical-object target follows [WCAG non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html); marker placement follows the [SVG marker model](https://www.w3.org/TR/SVG2/painting.html#Markers). This rule is a design and verification target, not a claim of complete accessibility conformance.

| Role | Colorset1 | Colorset2 additions |
| --- | --- | --- |
| Stage / surface | `#f7f7f7` / `#ffffff` | Same |
| Labels / strong structure | `#333e48` / `#1c1c1c` | Same |
| Primary / dark primary | `#9e1b32` / `#6d1222` | Same |
| Emphasis | `#e8002a` | Same |
| Secondary | Neutral or redundant geometry | `#007298`, dark `#004d66`, bright `#00ace6`, soft `#cdf3ff` |
| Positive | Neutral or direct label | `#45842a`, dark `#294d19`, bright `#36b300`, soft `#dbffcc` |
| Special | Neutral or direct label | `#652f6c`, dark `#431f47`, bright `#9e00b3`, soft `#f9ccff` |
| Orange category | Neutral or direct label | `#e77204`, dark `#994a00`, bright `#ff9633`, soft `#ffe5cc` |
| Attention | Red or direct label | `#f1c319`, dark `#98700c`, bright `#ffd332`, soft `#fff4cc` |
| Quiet solids / overflow borders | `#cfcfcf` / `#e7e7e7` | Same |

Pink `#ffccd5` is available in both sets but is a last-resort extra category, not the default secondary fill. Exact membership does not establish contrast; inspect small labels, saturated backings, thin lines and animation states independently.

Apply the contract to authored base paint: CSS, SVG fill/stroke, gradient stops, chart options, canvas colors, material/vertex colors, terminal presentation themes and video wrapper/canvas. Alpha compositing, antialiasing, physical shading and lossy codec pixels can produce derived tones; they must not be misrepresented as additional authored palette tokens. Technical categorical marks should switch among discrete tokens instead of synthesizing unrelated hues.

Preserve source fidelity explicitly. Downloaded photos, videos, textures/HDRIs, original brand artwork, embedded source artwork and requested exact-RGB conversion modes keep their original colors and provenance. Their authored frame, controls, captions and diagrams still follow a colorset. Resolve `currentColor` at the consuming surface. Do not claim these original pixels satisfy the authored contract or silently modify source identity.

The [34-skill output inventory](../evaluations/colorset-audit/coverage.json) records formats and paths, including nonvisual data/report outputs and source-fidelity boundaries. The [original audit](../evaluations/colorset-audit/validation-20261002.md) records output coverage; the [solid presentation revision](../evaluations/solid-colorset-style/validation-20261003.md) records the preceding renderer, isolated-runtime, contrast and publication checks. The [arrow revision](../evaluations/arrow-contrast/validation-20261003.md) records arrow-specific geometry, paint, export and final-payload verification. Run:

```powershell
uv run --script scripts/validate-colorsets.py
uv run --script scripts/validate-colorsets.py --input path/to/output.svg --colorset colorset1
uv run --script scripts/test-colorsets.py
```

The repository checker verifies complete inventory, canonical palette copies and declared artifact paint. For HTML it checks actual CSS and inline SVG; embedded vendor/decoder/source-color tables are input data, so dynamic script output requires browser inspection. It is a static gate, not a substitute for inspecting computed browser/canvas/WebGL state, raster/video output, meaningful semantic roles or user-requested behavior. Keep those checks in the owning renderer and its independent evaluation.
