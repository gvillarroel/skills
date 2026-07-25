# Pipeline Selection

Choose the pipeline from the source's visual structure, not from its art-historical label.

## Mode Matrix

| Mode | Best for | Processing signature | Avoid when |
| --- | --- | --- | --- |
| `organic` | Biomorphic abstraction, foliage, wood grain, flowing paint, soft Cubist collage | Bilateral smoothing, deterministic palette reduction, elliptical morphology, curved compound paths | Hairline drawings or intentionally sharp torn-paper edges |
| `ink` | Charcoal, automatic drawing, calligraphic meshes, engraving, brush marks | Grayscale blur, adaptive threshold, elliptical cleanup, one editable dark path | Color relationships carry the subject |
| `stain` | Watercolor, soak-stain painting, clouds, marbling, soft abstract fields | Strong edge-preserving smoothing, Gaussian merging, small palette, broad curved paths | Crisp typography or small symbolic details matter |
| `collage` | Synthetic Cubism, pasted paper, posterized art, rough cut-paper silhouettes | Mild median filtering, palette reduction, low smoothing, irregular compound paths | The user wants fluid or biomorphic boundaries |

`organic` is the default for non-geometric pattern work. Use `collage` for Cubist material language without forcing the result into triangular facets.

## Parameter Heuristics

- Start at 5–8 colors. Use 3–5 for a very simplified emblem and 9–12 only when distinct color masses disappear.
- Keep the default `max-coverage` palette for `organic` and `stain` when small accent colors carry the composition. Try `--palette-method median-cut` when those modes overemphasize rare noise. `collage` defaults to median cut for balanced paper-like masses.
- Increase `--smoothing` when tiny texture produces too many islands. Reduce it when facial, instrument, or botanical contours lose identity.
- Increase `--detail` to retain smaller contour changes. Reduce it to lower SVG size, but inspect for polygonal or distorted silhouettes.
- Raise `--min-area` to remove specks. Lower it when calligraphic marks or small collage fragments vanish.
- Use `--tile mirror` for a seamless-looking field. Use `repeat` only when opposite edges already agree or a visible repeat is intentional.
- Add a light `--outline` only when adjacent color layers merge. Do not outline every region by default.

## Preserve an Organic Result

- Prefer elliptical morphological kernels and curved paths.
- Simplify color masses before simplifying contour coordinates.
- Preserve a few large asymmetric contours instead of many equal-size marks.
- Keep irregular spacing and variable contour weight.
- Avoid square kernels, hard grids, high contour-approximation tolerances, and decorative polygons unless the user explicitly requests geometry.
- For Cubist-derived work, retain torn edges, faux wood or paper texture, interrupted typography, silhouettes, and overlapping objects rather than reproducing analytical-Cubist facets.

## Failure Recovery

| Finding | Adjustment |
| --- | --- |
| Thousands of tiny regions | Increase smoothing and `--min-area`; reduce colors |
| Flat, unrecognizable result | Increase colors or detail; reduce smoothing |
| Angular organic boundaries | Increase detail and use `organic` or `stain` |
| Missing ink strokes | Lower `--min-area`, increase detail, reduce ink smoothing |
| Visible tile seams | Switch from `repeat` to `mirror`; crop to a stronger source region if necessary |
| SVG is larger than the raster | Reduce colors and detail, raise `--min-area`, and inspect whether vectorization is still the right deliverable |
| Text became meaningless fragments | Remove it, replace it with user-provided text, or keep only its abstract rhythm; do not invent source quotations |

## Technique Research

Research a new pipeline only when the four shipped modes do not preserve the source's defining structure. Prefer primary technical documentation and record the chosen parameters in the output report.

For backend selection, color autotracing, and binary silhouette tools, read
`vectorizer-selection.md`.

- OpenCV image filtering and morphology: <https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html>
- OpenCV thresholding: <https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html>
- OpenCV contour approximation: <https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html>
- OpenCV color quantization with k-means: <https://docs.opencv.org/4.x/d6/de2/tutorial_py_table_of_contents_ml.html>
- SVG `fill-rule` for compound paths and holes: <https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/fill-rule>
- SVG tiled patterns: <https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/pattern>

If adding a reusable technique, provide a deterministic script path, stable parameters, a compact trigger description, a visual fixture, and an adversarial validation case.
