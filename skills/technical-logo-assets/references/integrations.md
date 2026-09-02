# Logo integration patterns

Read this reference after selecting an exact logo when the target medium affects variant choice, embedding, or handoff. Always export into the deliverable first; consumers must not depend on the skill's installation path.

## Portable handoff contract

For every selected logo, retain these three sibling files:

```text
logo.svg
logo.provenance.json
logo.license.txt
```

Keep filenames stable after embedding. Store sidecars beside the SVG or in an adjacent rights/provenance folder when the target package has a prescribed media layout. Do not expose the catalog's internal directory structure as a public dependency.

Use the same rendered box and `preserveAspectRatio="xMidYMid meet"` behavior for peer logos. Add layout whitespace outside the SVG rather than cropping its normalized padding. Validate the final render on its actual background.

## HTML, SVG, and D3

For a fixed-color or provider-color asset, external image use is portable:

```html
<img src="assets/logos/python.svg" width="48" height="48" alt="Python">
```

An adaptive SVG inherits `currentColor` only when its SVG element is inlined into the document or parent SVG. External `<img>`, SVG `<image>`, CSS `background-image`, and data loaded as a separate document do not inherit the surrounding page color. For those modes, export the adaptive choice with a literal `--color` value.

When inlining the same adaptive SVG more than once, namespace internal IDs per copy if the artwork contains referenced masks, clips, gradients, or filters. Preserve the exported SVG as the canonical master even if a build step inlines it.

## PlantUML and other diagram renderers

Export selected SVGs into a directory resolved from the diagram source or renderer working directory. Prefer paths without spaces and use the same scale for peer marks:

```plantuml
rectangle "<img:assets/logos/lambda.svg{scale=0.25}>\nAWS Lambda" as lambda
rectangle "<img:assets/logos/cloud-run.svg{scale=0.25}>\nCloud Run" as run
```

PlantUML image markup treats the SVG as an external document, so bake custom colors during export. Other diagram formats vary in image support and security settings; when a renderer cannot embed local SVG safely, use a labeled shape rather than substituting another brand. Confirm that the rendered artifact includes the images and remains portable from a clean working directory.

## Markdown, documents, and presentations

Markdown image syntax and office-document imports behave like external images. Use `color`, `mono-black`, `mono-white`, or a fixed custom-color export rather than relying on adaptive inheritance. Prefer SVG when the target preserves vector media. If the target requires raster input, keep the SVG master and render a PNG at the final physical size or larger; do not stretch a low-resolution raster derivative.

Keep accessible text separate from the artwork: use meaningful alt text, captions, or nearby labels. Do not encode a long product name inside the logo or alter its geometry to make it serve as a label.

## Video and raster pipelines

Import the SVG directly when the compositor supports it. Otherwise rasterize from the exported SVG at the intended frame size with transparency preserved, then inspect at 100% scale against the final background. Retain the SVG and sidecars in the project assets even when only a raster derivative ships in the encoded video.

For animation, animate position, scale, opacity, or surrounding layout. Do not morph, trace, recolor, or disassemble restricted artwork; keep aspect ratio constant and avoid motion that implies endorsement or changes brand meaning.
