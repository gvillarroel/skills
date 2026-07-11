# Palette Contract

Use one active colorset per logo render. Resolve every visible color through `assets/palettes/colorsets.json`; that machine-readable file is authoritative.

## Non-negotiable rules

- Permit only exact six-digit lowercase hex tokens from the active colorset.
- Permit `none`, `currentColor`, `url(#...)`, and opacity as non-color SVG values. Resolve `currentColor` to an active token.
- Reject named colors, three/eight-digit hex, RGB/RGBA, HSL/HSLA, LCH/OKLCH, CSS gradients, sampled image colors, and user-supplied arbitrary paint values.
- Do not interpolate colors. Animate geometry, masks, dash offsets, opacity, transforms, or discrete token changes instead.
- Use filters only for alpha or geometry. Never display raw noise/filter RGB output.
- Keep the background and text colors inside the active colorset too; palette safety applies to the entire logo artifact, not just the mark.

## Colorset1

Use for restrained, institutional, technical, editorial, or monochrome-like identity work. It contains 17 exact tokens:

`#000000`, `#1c1c1c`, `#333e48`, `#363636`, `#4f4f4f`, `#696969`, `#6d1222`, `#828282`, `#9c9c9c`, `#9e1b32`, `#b5b5b5`, `#cfcfcf`, `#e7e7e7`, `#e8002a`, `#f7f7f7`, `#ffccd5`, `#ffffff`.

Make `#9e1b32` the primary brand accent, `#333e48` the default ink, and grayscale tokens the supporting hierarchy. Reserve `#e8002a` for a small high-energy cue.

## Colorset2

Use only when categorical or expressive multi-hue differentiation is part of the concept. It contains 37 exact tokens:

`#000000`, `#004d66`, `#007298`, `#00ace6`, `#1c1c1c`, `#294d19`, `#333e48`, `#363636`, `#36b300`, `#431f47`, `#45842a`, `#4f4f4f`, `#652f6c`, `#696969`, `#6d1222`, `#828282`, `#98700c`, `#994a00`, `#9c9c9c`, `#9e00b3`, `#9e1b32`, `#b5b5b5`, `#cdf3ff`, `#cfcfcf`, `#dbffcc`, `#e77204`, `#e7e7e7`, `#e8002a`, `#f1c319`, `#f7f7f7`, `#f9ccff`, `#ff9633`, `#ffccd5`, `#ffd332`, `#ffe5cc`, `#fff4cc`, `#ffffff`.

Start from red, blue, orange, green, purple, and yellow only when the mark needs multiple roles. Prefer one dominant hue plus neutrals over rainbow allocation.

## Contrast and small-size gate

Use `#1c1c1c` or `#333e48` on light surfaces and `#ffffff` on dark or saturated surfaces. At a 96 px-wide preview, the brand name must remain recognizable without relying on texture. If it does not, simplify geometry, increase negative space, reduce texture strength, or switch to colorset1.
