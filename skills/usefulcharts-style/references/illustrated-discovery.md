# Illustrated discovery

Treat generated specimen sheets as organic layouts until inspected. Equal requested cells do not guarantee equal object bounds. Measure safe per-object SVG viewports from the actual sheet; check each placed crop for a neighboring fragment, clipped ear, tip, wing or instrument neck. Keep the original bitmap intact and record crop coordinates in the placement manifest. Match the viewport aspect ratio to the crop to prevent letterbox leakage. Target the root SVG explicitly when exporting a composition with nested SVG viewports.

Use for an explicitly playful, inviting or illustrated educational poster. Keep
the complete selected inventory and the separate reference-density requirement.
This guide does not make playful styling mandatory for sober technical requests.

## Make images part of the explanation

Before coordinates, identify the major families and choose recognizable objects
or scenes that help distinguish them. Bind every subject image to record or group
IDs. Distinguish an exact object, an illustrative example and a thematic archetype
in the caption and provenance. Do not imply that an invented machine, vehicle or
portrait is a verified historical specimen. Research exact subjects as needed;
use inspected source photographs or reference-guided generated assets. Follow
the available image tool's workflow and retain the selected files locally.

Design at two scales: a clear visual invitation at page scale and informative
details at reading scale. Put imagery inside the diagram body near its facts,
not exclusively in the title or a disconnected gallery. Different families need
distinguishable subjects; repeat a design only where the source supports the
same class or mechanism. Inspect each image at its actual placement size.

Useful approaches include a specimen beside a classification branch, a pair of
objects with a mechanism annotation, an illustrated scene at a turning point,
or a vehicle beside its exact endpoint. For a specimen sheet, use separate SVG
viewports to compose the inspected cells; retain the original raster and cell
provenance. Inspect cell boundaries and silhouettes for accidental clipping.

Build discovery from the data: invite the reader to trace a named branch, compare
two illustrated mechanisms or find the separately plotted stages of one object.
Make the answer available in the chart. Two or three specific invitations often
serve better than many repeated badges. Interactive search, focus and reveal
controls may help, but the exported poster must retain the explanation.

For reference-level exploratory composition, read [visible discovery](visible-discovery.md).
Body-image coverage is only the first gate. A caption pointing to a distant code,
a generic period machine or a separate silhouette gallery can pass coverage
while still failing the requested composition. Recompose the graph when needed;
do not preserve a list layout merely because its geometry already passes.

Reserve the full art, caption and connector footprint. Use released pockets and
vary local placement before enlarging the page. Keep numeric x positions fixed.
Measure total area and retained readable facts after adding artwork. Images do
not count as extra factual records or compensate for omitted notes.

## Evaluate without averaging away a failure

Inspect the whole final image and at least one representative dense detail. Keep
those paths and SHA-256 hashes in the working review. Score these dimensions
individually, with a concrete visible observation for each:

| Dimension | 1: weak | 3: good | 4: exceptional |
| --- | --- | --- | --- |
| `composition` | Repetitive list or disconnected tiles. | A clear entrance and coherent, varied local groups. | Strong flow and even useful density across the complete field. |
| `image_usefulness` | Banner, generic decoration or unrecognizable miniatures. | Recognizable body images explain their bound subjects. | Image comparisons reveal details the text alone makes difficult. |
| `image_integration` | Floating pictures, mismatched mats or confusing ownership. | Image, its specific fact and its relationship are visually associated without a distant lookup. | Artwork, labels and connections form an integrated visual explanation. |
| `playful_discovery` | Static catalog with ornamental color. | A reader can follow visible relationships or aligned comparisons to discover an answer in the poster. | Several levels of discovery work naturally at page and detail scales. |
| `legibility` | Crowded text or weak contrast. | Comfortable reading and unobstructed relationships. | Rich hierarchy remains clear in the busiest region. |

Zero means absent or broken; two means usable with visible issues. Require at
least three in every dimension for the declared illustrated brief. Averages are
not acceptance criteria. State concrete unresolved defects and revise them.
Treat unresolved content, geometry or image-identity defects as independent
failures regardless of these scores. A missing reference census stays pending.

Use the [review template](../assets/templates/illustrated-review.json) and run:

```sh
uv run --script <skill-dir>/scripts/assess_illustrated_review.py review.json --output assessment.json
```

Paths in the review resolve relative to the review file. Each `body_images` entry
needs a unique `placement_id`, a reusable `asset_id`, existing `anchors`, a
`region` (`upper`, `middle` or `lower`), the asset path, a concrete explanation
and `recognized_at_placed_size: true`. `required_groups` declares the major
families the brief needs illustrated; each image lists its `groups`. A large
multi-family poster should normally reach two or three body regions; declare
`minimum_body_regions` explicitly, rather than treating pixel coverage as quality.
Atmospheric backgrounds and title illustrations are excluded from `body_images`.

The helper checks review completeness, artifact hashes, declared coverage and
non-compensating scores. It cannot see images or prove that review statements
are true. Inspect the real SVG image geometry, visible captions and actual PNG
independently. Never describe the helper's result as an objective aesthetic pass.

Before revising, retain the current preview and three visible weaknesses. After
revising, reopen the new whole image and detail, explain the actual improvement
and any tradeoff, and rerun factual and geometry checks. Keep rejected assets and
attempts in the local evidence. If image input is unavailable, leave the visual
review pending; metadata and geometry are not substitutes for seeing the art.
