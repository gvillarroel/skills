# Starships with a shared calendar x axis

Date: 2026-09-12. Application authored and visually reviewed by the main agent.
This is a local project deliverable, not a published Pages example or a claim
of indistinguishability from UsefulCharts.

## User requirement and result

The user requested a denser left-to-right fleet chart, several vessels sharing
the same line, an actual time x axis, and reuse of space after a line no longer
needs it. The final numeric edition contains 79 physical spacecraft in 13 family
groups. Twenty local tracks contain multiple spacecraft; up to four vessels
share a track. Earth pioneers, early Starfleet and later explorers also reuse
one vertical band in disjoint calendar windows. Group headings and complete
record envelopes remain separated.

All dated marks use one piecewise-linear calendar function. The 2360–2385 window
is expanded, adjacent scale changes are labeled, and three double-slash gaps
identify omitted years. Equal widths in different windows do not represent equal
elapsed time. Every displayed year nevertheless has the same x coordinate in
every family. The user did not require one uniform scale for the whole span.

The chart is 5200 × 4611 pixels. Compared with the prior 3600 × 7760 space edition,
the same physical inventory occupies 14.17% less area, or 16.51% more physical
records per unit area. This is a geometric comparison only. The poster now
selects compact identity, registry, class, construction/launch, use and fate facts;
all original narrative notes and credits remain in the offline viewer and
evidence ledger. Six source-bound design profiles retain their complete notes
and credits on the poster. Hidden viewer prose is not counted as poster density.

## Preserved distinctions

- 29 established launch/commission/build dates and 50 unstated launch dates.
- Four records with construction evidence; Columbia's construction in 2153 and
  launch in 2154 are separate facts and marks.
- Seven supported service intervals, dotted observations and two uncertain
  ranges. A last displayed observation is not an invented retirement date.
- Eleven additional state fragments show 14 events of the same physical hulls.
  They are not eleven new ships and do not fill long gaps with a service bar.
  The Defiant's Mirror-universe arrival is explicitly identified.
- Twenty-one typed links distinguish name succession, development, sister ships,
  replacement hulls and same-hull renaming. Comparative families do not imply
  descent merely because they share space.
- Six accepted photographic-reference-guided image assets are reused at eighteen
  placements, twelve at calendar endpoints and six in the design inset. Artwork
  identifies a design family and is not a literal size/registry specification.

## Review and repairs

The retained schematic shared-row prototype was rejected after the explicit
time-axis instruction: chronological ordering alone was insufficient. Numeric
v1 fixed x correctly but produced a sparse 6800 × 7564 page and 24 text collisions.
Numeric v2 reused disjoint family pockets, removed header/name collisions and
measured all labels before placement. Numeric v3 reclaimed a large early-period
pocket for a clearly framed, non-temporal design/relationship inset.

Final review inspected the full PNG, the crowded Defiant group, the PDF proof
and the offline viewer. An expanded contrast check painted the complete backdrop
without text, including actual wakes and panel fills. It detected wake glow
under thirteen name envelopes and then a marker near one state heading. Moving
the wake within its reserved block and increasing secondary heading clearance
resolved both failures. The final audit passes over every complete text box.

The composition remains sparse in some calendar regions. The enlarged interval
and source distribution make those gaps visible; no invented ships fill them.
The small reference illustrations do not establish camera or visual parity with
a branded poster. A complete semantic reference census remains pending.

## Independent verification

Final SVG SHA-256:
`4e873c00d139be662d9eb526f9c813f146edfc1eacb3baf85226778b041be1f2`.
Unchanged source SHA-256:
`6a71ba662c7e9c3f1da59f37ff6d99baf738eaeb4d643911f3ef89f058cbdef8`.

The independent verifier uses a literal calendar contract, not the builder's
mapping function. It passes 157 exact date marks (maximum error 0.003864 px),
41 temporal spans, 79 primary identities, 14 additional state events, 21 links,
twenty shared tracks, and disjoint family reuse. Browser checks report 444 text
nodes, no outside text, no label-envelope overflow, no text/text collision and
no illustration/text collision. Minimum actual-background contrast is 6.77:1.

The PDF has one 52 × 46.11 inch page, embedded font resources and 79 correctly
positioned source links. Offline search, operator and date filters, state-fragment
selection, source details, related-vessel navigation, keyboard selection, zoom,
family navigation, compact layout and relative downloads pass. No browser errors
or HTTP requests occur during the offline checks.

```powershell
uv run --script projects/star-trek-starships/scripts/build_numeric_atlas.py
uv run --script projects/star-trek-starships/scripts/render_atlas.py --numeric --version final --pdf
uv run --script projects/star-trek-starships/scripts/audit_space_art.py --numeric
uv run --script projects/star-trek-starships/scripts/verify_numeric_atlas.py
uv run --script projects/star-trek-starships/scripts/package_atlas.py --numeric
```

Artifacts are under `projects/star-trek-starships/artifacts/numeric-edition/`:
editable SVG, full PNG, preview, PDF, offline HTML, original JSON/CSV, source
ledger, final verification and ZIP. The original cream, space and rejected
schematic prototypes are retained independently.

The generalized measured-layout route is recorded in
[shared time row validation](shared-time-rows-20260912.md). Passing this direct
application does not prove autonomous end-to-end illustration or reference
knowledge-density parity.
