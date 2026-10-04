# Visual Tokens

Use these defaults for Three.js materials, lighting, HTML panels, and controls.
Preserve explicit spacing and existing semantic roles. Map requested colors to
exact tokens in `assets/palettes/colorsets.json`; every authored color input must
belong to one selected colorset, including vertex attributes, emissive paint,
fog, CSS, texture annotations and exported scene metadata. Use quantized token
bands for data colors; do not generate arbitrary vertex hues with `lerpColors`
or `setHSL`. Imported source photography can retain its immutable colors while
authored scene chrome follows the active contract.

## Palette selection

Use **colorset1 by default**. Use colorset2 only for an explicit extended,
expanded, multicolor, or full-color request; record it in `data-colorset`.

| Colorset1 role | Token |
| --- | --- |
| Page / surface | `#f7f7f7` / `#ffffff` |
| Ink / dark ink / black | `#333e48` / `#1c1c1c` / `#000000` |
| Main emphasis / active emphasis / critical | `#9e1b32` / `#6d1222` / `#e8002a` |
| Gray structure, dark to light | `#363636`, `#4f4f4f`, `#696969`, `#828282`, `#9c9c9c`, `#b5b5b5`, `#cfcfcf`, `#e7e7e7` |

Allocate distinct category materials from the bundled `solidSequence`: start
with primary red `#9e1b32`, then grays, black, white, and the remaining colors.
Exclude only the actual canvas token. Reuse colors for objects with the same
semantic role; preserve explicit status meanings and ordered-value scales. Use
geometry, position, texture, and direct labels alongside color. Keep filled
meshes free of decorative `EdgesGeometry`, wireframes, or silhouette overlays.

Pink `#ffccd5` is a **last-resort category**, after usable reds, grays, black,
and white cannot distinguish an additional meaningful category. It is also
available for an explicit pink request. Record the reason; do not automatically
use pink as the second material, a soft background, replay fill, or focus color.
Use a solid red material, position, motion or a direct label for selection.
An outline is a documented overflow option after the full usable solid palette.

Colorset2 adds blue `#007298`, orange `#e77204`, green `#45842a`, purple
`#652f6c`, and yellow `#f1c319`. Use additions for meaningful categories.
The standalone builder accepts `--colorset colorset2` to select this explicitly.

## Lighting and color management

Use neutral white lights by default, including rim lights and environment maps.
A colored light can tint every gray material and defeat colorset1. Keep
`THREE.ColorManagement` enabled, enter material tokens as sRGB hex colors, and
set `renderer.outputColorSpace = THREE.SRGBColorSpace`. Use
`THREE.NoToneMapping` for the simple baseline; review any later tone mapping,
exposure, emissive material, bloom, or tinted environment in the rendered image.

Lit pixels naturally differ from source hex values because of shading. Validate
the material and light inputs, then inspect the image for hue balance, readable
silhouettes, and washed-out red highlights. Do not demand exact palette RGB
equality from every antialiased or lit pixel. Use an unlit material or a flat
legend swatch where exact color identification is essential.

Primary references: [Three.js color management](https://threejs.org/manual/pages/color-management.html)
and [responsive design](https://threejs.org/manual/pages/responsive.html).

## Compact layout

| Element | Default |
| --- | --- |
| Page/panel padding | 12 px |
| Toolbar gap / bottom space | 8 px / 8 px |
| Button padding / minimum height | 4 px vertical, 10 px horizontal / 32 px |
| Coarse-pointer button | At least 44 px high |
| Status padding | 4 px vertical, 8 px horizontal |
| Standalone stage | 16:9 aspect ratio, 200 px minimum height |

Do not reduce font sizes, meaningful 3D distances, object scale, or camera
clearance to simulate less padding. Recompute camera aspect and fit the complete
motion envelope when the container changes. Compact panel geometry and readable
scene framing are separate decisions. Let long headings wrap; keep status text
inside the stage without covering focal objects. Preserve explicit dimensions.

The builder defaults to `--density compact`; `--density comfortable` retains a
320 px stage minimum, 16 px outer spacing, and larger button padding when asked.

## Typography and interaction

- Use `"Open Sans", Arial, sans-serif`; allow the local fallback in offline HTML.
- Use Material Symbols Rounded when already available locally; otherwise use
  labeled controls or inline SVG icons, without network font dependencies.
- Use the bundled `textOnFill` mapping: choose exactly black or white by maximum
  WCAG contrast against the actual material swatch or HTML surface.
- Pair interaction states with labels, solid fills, or shape changes.
- Use a visible red focus outline and an accessible name for every icon control.
- Verify desktop/mobile framing, contrast, label fit, replay, and pointer input.
