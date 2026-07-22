# Manim SVG Import Notes

Manim can use SVG content in two practical ways:

- `svg` import mode: load SVGs through `SVGMobject`. This is the portable default and keeps vector geometry editable by Manim, but text nodes, CSS, markers, filters, and animation elements may be ignored or simplified.
- `image` import mode: rasterize SVGs to PNG first, then animate `ImageMobject`s. Use this only when ImageMagick, `rsvg-convert`, or Inkscape is available on PATH. It can preserve text and visual styling better than `SVGMobject`.

## Animated SVGs

Manim does not execute browser-native CSS or SMIL animation embedded inside SVG files. Treat `.animated.svg` files as source assets for selection and metadata, then let Manim animate their appearance, pulse, scale, and placement in the shared video timeline.

When the SVG's final visual state matters, prefer a `.static.svg` companion as `render_source`. The compositor does this automatically when it can find one.

## Failure Handling

Rasterization can fail when a system converter is unavailable or when an SVG depends on unsupported browser-only CSS or malformed generated markup. The compositor records the failure in `composition-manifest.json` and falls back to SVG import so long showcase renders can continue.

After rendering, inspect:

- `asset_count` versus expected SVG count.
- `conversion_error` fields.
- The first and final frames or the MP4 itself for nonblank content and readable overall composition.
