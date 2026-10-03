Read this prompt first. Treat `skills/usefulcharts-style/` as read-only. Work
inside this isolated workspace. Do not use the network or discover other skills.

I am composing a dense museum timeline with time on the horizontal axis. Please
lay out the following already measured label footprints. Keep their horizontal
positions exactly as given; assign vertical tracks so labels do not collide.
Several vessels should share a family row whenever space permits. Separate
families may occupy the same vertical band when their entire headings and
content fit in different time windows.

The canvas is 1000 units wide and starts at y=90. Require 12 horizontal units
between records, 10 between tracks and 24 between family pockets. Reserve 40
units above each family's records for its heading, which is 160 units wide.
Calendar x = 100 + 10 * (year - 2000); these boxes already include all labels
and clearance. Do not change their dates or x positions.

| Fragment ID | Physical owner | Family | x0 | x1 | Height |
| --- | --- | --- | --- | --- | --- |
| swift-first | swift | couriers | 100 | 250 | 80 |
| swift-return | swift | couriers | 400 | 530 | 80 |
| kestrel | kestrel | couriers | 190 | 330 | 90 |
| atlas | atlas | freighters | 580 | 740 | 85 |
| beacon | beacon | freighters | 765 | 970 | 85 |

Write `deliverables/layout.json` with a `layout` object containing `boxes`
(id, group, x, y, w, h for every fragment) and `groups` (id, x, y, w, h).
Retain the supplied owner identity for every fragment in a `source.records`
array. Explain the layout, the distinction between physical objects and their
separate states, and the remaining visual checks in `deliverables/review.md`.
This is a measured layout task; do not draw a poster or claim that visual
similarity has been tested.
