# SVG mechanics

Use these references for a specific implementation question. The core design
workflow does not require browsing or downloading external resources.

- [MDN: Paths](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorials/SVG_from_scratch/Paths)
  explains straight segments, curves, and arcs. Prefer a small number of
  intentional curve segments to many tiny line segments approximating a curve.
- [MDN: fill-rule](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/fill-rule)
  describes how compound paths determine inside and outside. Use this to reason
  about actual openings instead of painting a light shape over a dark one.
- [MDN: viewBox](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox)
  explains the drawing coordinate rectangle. Leave enough margin to contain
  strokes and sharp joins while keeping the intended proportions.

For text, choose a generic fallback that the target renderer can resolve. An
SVG can remain editable while its exact typography varies between machines.
Use paths only when exact glyph outlines are legitimately available and the
user's editing requirements allow outlining text.

Keep source material separate from this guide. Do not place purchased artwork,
screenshots, extracted coordinates, encoded images, specimen silhouettes, or
task-specific design reconstructions in the skill bundle.
