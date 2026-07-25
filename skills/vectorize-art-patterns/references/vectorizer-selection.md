# OSS Vectorizer Selection

Choose a tracer from the source structure and the intended editability. Do not
default to one backend for every image.

## Backend Matrix

| Backend | Use when | Avoid when |
| --- | --- | --- |
| Bundled OpenCV contour pipeline | Soft stains, broad organic masses, ink cleanup, seeded crop or flow variation, and repeat tiles | A detailed painting needs many nested color regions |
| VTracer | Color paintings, woodcuts, posters, and complex illustrations need compact editable paths | The source is already a clean binary silhouette or deliberately soft stain |
| Potrace | A thresholded black-and-white bitmap needs smooth Bézier contours | Color relationships or layered regions matter |
| Inkscape Trace Bitmap | A person needs an interactive desktop workflow and manual cleanup | A deterministic batch build or strict provenance report is required |
| SVGcode | A browser-only Potrace workflow is useful and GPL-2.0 is acceptable for the application context | Color autotracing or a Python batch pipeline is required |

Primary references:

- [VTracer repository and usage](https://github.com/visioncortex/vtracer)
- [Potrace algorithm and manual](https://potrace.sourceforge.net/potrace.pdf)
- [Inkscape tracing guide](https://inkscape-manuals.readthedocs.io/en/1.1/tracing-an-image.html)
- [SVGcode repository](https://github.com/tomayac/SVGcode)

## VTracer Workflow

Use `scripts/vectorize_with_vtracer.py` for detailed color sources. It:

1. verifies the source against the rights manifest;
2. performs deterministic source-space filtering and quantization;
3. traces the same quantized raster for either Colorset;
4. maps VTracer fills back to source clusters and exact palette tokens;
5. embeds source rights, hashes, parameters, accessibility text, and backend
   version;
6. writes a JSON report beside the SVG.

Trace before applying the Colorset. Tracing two independently recolored rasters
can change region boundaries and break geometry locking.

Start with 7–10 colors, `filter-speckle` between 8 and 20, and `max-dimension`
between 480 and 700. Increase colors before reducing speckle when a recognizable
object disappears. Increase speckle before lowering colors when the SVG contains
many tiny fragments.

## Evaluation Gate

Test at least one representative source and one adversarial source. Compare:

- recognizable silhouette and internal structure;
- thumbnail readability;
- path count and SVG byte size;
- isolated specks and accidental holes;
- deterministic repeat output;
- Colorset token compliance;
- geometry equality between paired variants.

Prefer VTracer for detailed color works only when it preserves important
structure better than the bundled contour pipeline. Prefer the contour pipeline
for stains when VTracer converts soft transitions into distracting nested
islands. Prefer Potrace or Inkscape for binary silhouettes because color
autotracing adds unnecessary layers.
