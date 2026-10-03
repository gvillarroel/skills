# Shared rows on a calendar x axis

## Contents

- [Establish the contract](#establish-the-contract)
- [Measure and pack](#measure-and-pack)
- [Inspect and repair](#inspect-and-repair)

Use this route when several entities should share a family row and time should
run horizontally. Examples include vehicle families, product generations,
officeholders, expeditions and institutions. A family row may contain several
local tracks for simultaneous entities. Avoid one full-page lane per entity.

## Establish the contract

1. Preserve a canonical inventory of physical entities, typed relationships and
   evidence. Distinguish a name successor, replacement object, refit of the same
   object and design comparison. Sharing a row is not evidence of ancestry.
2. Make x a numeric calendar function. Use one function for every family, tick,
   interval, uncertainty band and event. Chronological ordering with equal card
   spacing is not a time axis. If multiple linear windows are necessary, show
   their boundaries, scale changes and omitted years prominently. Do not choose
   a separate scale for each family. Preserve an explicitly requested uniform
   scale instead of introducing windows.
3. Map real event endpoints first. A supported service interval may be solid;
   selected sightings may be dashed, with a legend that disclaims continuity.
   Unknown dates stay unknown. A point must not become a minimum-length bar.
4. Select compact visible fields deliberately: identity, class or role, registry
   or identifier, launch/build date, dated use and fate. Combine these inside a
   measured label block. Preserve required context on the poster; when selection
   is authorized, keep the full source record in an evidence ledger or viewer.
   Report this selection. Hidden details do not count toward poster density.

## Measure and pack

Measure each complete footprint, including labels, date marks, halo, art and
clearance. Labels may sit beside an exact date anchor with a short leader; the
date anchor itself must not move. Prefer rewrapping, alternating label sides and
local subtracks before reducing type. Reserve group headings before packing.

For a long absence or time jump, split the same entity into independently
positioned state fragments with unique fragment IDs and one stable owner ID.
Show their identity explicitly. Do not fill the intervening centuries or count
fragments as new entities. Later activity and museum display are different states.

The helper assigns y tracks while preserving the supplied x footprints:

```sh
uv run --script <skill-dir>/scripts/pack_shared_rows.py measured.json --output packed.json
```

The output contains an unchanged deep copy under `source` and measured placement
under `layout`. Render from `layout.boxes` while retaining the independently
computed date coordinates. The helper does not research facts, measure fonts,
draw SVG or validate calendar semantics. Its implementation need not be read.

Input contract, using a synthetic scale `x = 100 + (year - 2000) * 10`:

```json
{
  "mode": "numeric", "width": 700, "top": 100,
  "gap": 12, "track_gap": 10, "row_gap": 24,
  "compact_groups": false,
  "groups": [
    {"id": "survey", "members": ["alpha", "beta", "gamma"],
     "header_height": 50, "label_width": 180}
  ],
  "records": [
    {"id": "alpha", "owner": "alpha", "x0": 100, "x1": 240, "height": 70},
    {"id": "beta", "owner": "beta", "x0": 265, "x1": 420, "height": 70},
    {"id": "gamma", "owner": "gamma", "x0": 220, "x1": 360, "height": 80}
  ]
}
```

All dimensions are finite canvas units. Footprints satisfy `0 <= x0 < x1 <=
width`. Record and group IDs are unique nonempty strings. Group memberships
partition all fragments exactly once. Nonoverlapping footprints reuse a track;
overlapping footprints require different tracks. Additional source fields are
preserved. The output reports fragment count, group count, track count and
`multi_record_rows`; count unique owners separately.

Set `compact_groups: true` only when separate family pockets may share vertical
space. The helper reserves each group's entire horizontal envelope, including
`label_width`, then finds a free y position among already placed groups. Every
calendar x stays fixed. Draw a local group heading and clear boundary; do not
make independent pockets look like one genealogical chain. Leave it false for
fixed full-width family rows. `header_height` reserves title space above tracks;
`label_height` sets a minimum group height. Never add oversized titles afterwards.

For reuse **inside** a family's former envelope, set `reuse_tracks: true` and
`labels_in_footprints: true`. Include the local family identity in every measured
record; omit group-level `header_height`, `label_height` and `label_width`.
The helper puts all fragments into a shared track pool while retaining their
group and owner IDs. A short branch can release its track to another family even
while a longer branch of the first family continues above it. Local labels and
semantic color must make the handoff visible; do not paint a continuous family
trunk between unrelated records. This mode supersedes `compact_groups` and
reports `cross_group_rows` in addition to `multi_record_rows`.

Reserve the full label, illustration and clearance when deciding whether a track
has ended; its last date alone is insufficient. For a custom compound footprint,
reserve leaders and individual occupied shapes before using pockets below a long
thin wake. Do not reserve a family's maximum rectangle by default, and do not
pack merely for minimum height when it scatters meaningful groups. Labels may
change sides only after remeasurement; actual calendar anchors remain fixed.

An explicitly schematic sequence may instead use measured `width` and `height`
records with the helper's default sequence mode. Never use that mode to satisfy
a request for a numeric time axis.

## Inspect and repair

Render the SVG and inspect both the full composition and its busiest tracks.
Use a browser to measure actual text and illustration boxes; count collisions,
clipping and tiny labels. Validate every event x independently from its year,
not merely from the same coordinates used by the renderer. Compare the complete
typed relationship inventory and verify that separate state fragments resolve
to the same source record in interactive views.

If the page remains sparse, reclaim terminated family pockets and shorten
repeated boilerplate before resizing the page. Source-backed design or context
insets can occupy free pockets, but label them as reference material and separate
them from the time plot. Artwork or duplicated facts do not raise knowledge
density. Measure displayed useful layers and their spatial distribution using
the knowledge-density reference; report missing reference census evidence.

Accept fixed-x fidelity, complete selected information, readable local tracks
and meaningful grouping together. A high number of shared tracks alone does not
prove a good composition or parity with a reference poster.

When the user has not fixed the page dimensions or scale, compare several
**uniform** year-to-x scales at unchanged typography and with the same records.
A narrow page can create an unnecessarily tall stack of neighboring-year labels;
a much wider page can reduce track count while increasing total area. Compare
width times height, readable detail size and the desired aspect ratio together,
not just track count or height. Remeasure the complete footprints for each
candidate, then validate the chosen numeric transform independently.

For a sourced reading guide or contextual inset, search actual empty rectangles:
test the plot top and the bottoms of occupied footprints at the proposed x span,
then select the first candidate that fits with clearance. Taking only the latest
occupied bottom misses usable space above a later record. Label a reference inset
as context, not a time interval, and check it against labels, points, component
bars and leaders. A launch campaign with several vehicles may need separate
component bars in its existing block; do not collapse their distinct end years.
