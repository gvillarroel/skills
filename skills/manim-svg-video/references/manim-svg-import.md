# Manim SVG import

`auto` is the default. Unmarked SVGs use SVGMobject; marker-bearing SVGs use
Chromium to rasterize their actual browser paint, then Manim places ImageMobjects.
Browser rasterization preserves CSS/context-stroke arrowheads that SVGMobject
omits. It flattens editable vector parts into a PNG at the preparation size; the
SVG remains the editable source. Inspect decoded delivery frames for sufficient
shaft width, head size and contrast after scaling and encoding.

For a vector-only workflow, materialize every marker instance as ordinary paths
with its actual transform and source paint, then use `--import-mode svg`. Explicit
vector mode refuses sources still carrying markers instead of losing their heads.
`--import-mode image` rasterizes all assets; it tries Playwright Chromium and then
installed Chrome/Edge. Marker-free images may use installed ImageMagick,
rsvg-convert or Inkscape if the browser fails. Marker-bearing sources require the
browser; conversion failure writes preparation-error.json and stops before rendering.
Install a Chromium browser rather than accepting a silent vector fallback.

Manim does not execute browser CSS or SMIL timelines. The default `--render-source
final` chooses a matching `.static.svg` companion. An animated marker-bearing
source without that companion fails: create a readable static final snapshot.
For an intentional source-time snapshot, select `--render-source animated
--snapshot-seconds <time>`. The browser pauses CSS and SMIL at that exact time;
this is snapshot semantics, not playback of the source timeline. Hidden marked
arrows at that time fail preparation. Inspect the snapshot because script-driven
state or unsupported source behavior may require an authored static companion.

Read [arrow-visibility.md](arrow-visibility.md) and audit the actual chosen source.
Check composition-manifest.json source/render_source/import_mode/prepared_source,
expected asset count and dimensions, then inspect a readable decoded MP4 frame.
Source preservation alone does not repair an already low-contrast source arrow.

For an explicitly preserved original asset, repeat `--preserve-source-media
<original-path>` per selected file. This exact-path policy preserves its existing
paint and width, while the raster sidecar retains every source finding and marks
`authoredQualityPassed: false` when appropriate. The manifest records
`source_media_preserved` per asset and the exact selected paths. This exception
does not report the source as meeting 3:1, recolor it, or exempt other assets.
Default authored sources still fail on low contrast. Missing, covered or hidden
heads, unsupported geometry, unreadable snapshots, conversion errors and vector
marker refusal remain blocking. A typo naming an unselected asset fails explicitly.
Inspect the preserved browser image and decoded frame, and disclose the source's
original contrast/width limitation with the delivery.
