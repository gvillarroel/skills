# Minutes: adding contributor portraits and circular company logos

Date: November 15, 2026. Scope: the CUDA/AlexNet video and future Line World
productions. Keep this note with the editable source bundle.

## Decisions

Show real, verified faces where the story introduces the relevant work:
Ian Buck with CUDA, Fei-Fei Li and Jia Deng with ImageNet, and Alex Krizhevsky,
Ilya Sutskever and Geoffrey Hinton with AlexNet. This is a selected narrative
cast, not an exhaustive ranking of contributors. CUDA architecture and the
ImageNet dataset involved larger teams, including John Nickolls and the other
coauthors of the original papers. Retain those paper citations in production
notes. Do not substitute today's employer logo for an affiliation in 2012.

Keep the existing native narration and scene budgets. Add separate measured
name cues for the three AlexNet authors. Reserve the full image/name rectangle
as an obstacle; place the primary-red guide beside it. Use short factual names
as entity labels, with no title strip. Keep the diagrams as the main explanation.

The selected NVIDIA logo is real vector artwork from the pinned Lobe Icons
source exported by technical-logo-assets. The circular support is a separate
white disk: the original NVIDIA mark remains complete, centered and unchanged.
The green is source brand color, not a new explanatory category color. Keep
primary-red focus and dark-gray comparison semantics unchanged.

## Adding another logo

1. Find an official brand kit or an exact available technical-logo-assets ID.
   Prefer a true SVG with paths. A vector SVG embedded in a data-URI SVG wrapper
   is still vector; a PNG embedded in SVG is raster and must be identified as such.
2. Export only the selected mark into `artifacts/sources/logos/`. Keep its
   provenance and license sidecars. Do not trace a screenshot, deform the mark,
   recolor a protected variant or cut a wordmark to make it fit a circle.
3. Add a reviewed `logo` entry to `artifacts/data/media-request.json`, with a
   stable ID, exact label, local source path, source page, identity/contribution
   evidence, creator, license and credit. `scripts/prepare_media.py` is this
   project's reviewed request builder; update it when changing the selection.
4. Run the bundled `media_assets.py build --request ... --output ... --png`.
   It produces a 256 by 256 SVG viewport and a 512 by 512 transparent PNG. Logo
   artwork uses `meet` scaling inside an inset square; its corners remain inside
   the circular support. Keep the complete source and its SHA-256.
5. Inspect SVG and PNG on light and dark backgrounds. Confirm that every letter
   and symbol is visible, proportions match, corners are transparent, and small
   sizes remain readable. Prefer a permitted symbol variant when a wordmark is
   too wide to read; do not crop it. Use PNG when the target cannot render SVG.
6. Use `graph-nodes.json` as the graph handoff. Paths are relative to the media
   directory. The `nvidia` node uses `nvidia.circle.svg`; its PNG fallback is
   `nvidia.circle.png`. Copy the media directory and credits with the graph.

For D3/SVG, render the already circular file with an `<image>` element. Do not
apply an additional crop to a logo:

```javascript
node.append('image')
  .attr('href', d => mediaBase + d.image)
  .attr('x', -radius).attr('y', -radius)
  .attr('width', radius * 2).attr('height', radius * 2)
  .attr('preserveAspectRatio', 'xMidYMid meet');
```

For a single standalone SVG, use a data URL containing the local asset bytes;
do not leave a remote image hotlink. D3, HTML and graph importers have different
image-node APIs, so preserve the manifest rather than assuming one host format.

## Portrait sources and rights

The actual downloaded images were inspected. A public aggregator merged an
unrelated ASOCS namesake into an Alex Krizhevsky profile; that portrait was
rejected. The selected Alex portrait is the image attached to Quartz's interview
about the Toronto researcher. Ian Buck is sourced from NVIDIA speaker material,
Jia Deng from his Princeton faculty homepage, and the remaining portraits from
named Wikimedia Commons files. These are representative portraits from different
dates; they are not claimed to be photographs taken during the 2012 competition.

The media manifest and `credits.md` retain the exact source, photographer when
known, license, digest and circular presentation changes. The Commons files
carry CC BY/CC BY-SA terms. NVIDIA's, Princeton's and Quartz's photographs do
not advertise an open license in the reviewed material; this project does not
grant unrestricted redistribution rights to them. Keep that distinction when
reusing the asset pack. Brand licensing does not imply endorsement.

## Editing and validation

Run `scripts/prepare_media.py` after changing the reviewed request builder,
then `scripts/prepare_project.py` and the visual audit. Adjust each portrait's
normalized `focus` and optional `zoom` after checking hair, eyes and chin.
An unchanged media build reuses local files without redownloading. The final
video requires a new native export after replacement visuals are inserted;
preserve the original Nyla voice tracks and recheck scene extents and joins.
