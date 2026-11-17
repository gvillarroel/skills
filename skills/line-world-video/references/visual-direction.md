# Visual direction

Use a white field, charcoal hairlines, small neutral objects and one red attention
dot. At 1920×1080 use roughly 2–3 px mechanism strokes and 24–32 px data labels.
Use no visible titles, subtitles, chapter banners, slogans or generic explanatory
sentences by default. Preserve essential figure labels, values, units and legends.
An explicit request may add one short contextual label in the requested scene;
keep it modest and subordinate to the figures. Accessibility metadata remains
available independently of visible copy. Keep at least 100 px around reading regions. Use
intentional open space, measured labels and a few recognizable silhouettes;
avoid cards, shadows, glossy shapes, persistent chapter bars and ornamental grids.
Separate concepts with spacing and alignment. Do not add a central dividing
line or decorative panel borders; logical frame regions need no painted rule.

Compose the objects before allocating any text zones. Distribute meaningful
geometry across roughly the central 75–90% of the usable width and 60–80% of
the height when the content supports it. Balance visual mass around the frame's
center, keep paired views comparable in size, and avoid a miniature illustration
floating below a vacant headline area. Reclaim space when removing copy. The
overview uses a compact two-by-two world so related islands fill the viewport
in balance; it does not reserve a closing-slogan band. Judge bounds and visual
weight together rather than stretching a small mark to satisfy an area quota.

The user's line-art direction is an explicit style choice: meaningful object
outlines, trajectories, axes and graph edges are appropriate. A line drawing is
not a categorical overflow style. Keep filled data marks opaque and simple.

Start with colorset1 from the bundled exact token file: white `#ffffff`, ink
`#333e48`, dark ink `#1c1c1c`, neutral `#696969`, quiet `#e7e7e7`, primary red
`#9e1b32`, and accent `#e8002a`. The guide always uses primary red `#9e1b32`;
the accent is not its replacement. Red means current attention; do not also make it
mean failure unless the story explicitly relates those meanings.

Order visual priority as primary red, light/medium grays, then dark neutrals.
Keep charcoal for readable labels and fine structural lines. Use black only
as a last contrast or notation choice; avoid large black category blocks.
The private palette sequences enforce this order across the five plugin copies.
Read [color priority](color-priority.md) for fill and imported-asset decisions.

Use labels, shape and position before adding hue. When simultaneous semantic
categories need stronger separation, record the reason for colorset2 in the
story manifest and introduce its blue `#007298`, green `#45842a`, purple `#652f6c`
or orange `#e77204` only where that distinction applies. A colorset2 document
may have earlier red/neutral scenes: those tokens belong to both palettes. Do
not silently change an entity's identity when the camera moves. Use `palette:
"colorset1"` for a completely red/neutral edition of the same film.

Keep one attention guide while allowing additional data points. Enlarge the
guide briefly for a focus or emission, contract it for travel, then settle.
Its radius expresses attention, not a measured quantity. Color emerging points
by a stable semantic mapping and explain their unit in a compact legend. Avoid
idle pulsing, confetti and arbitrary hue changes. Follow
[attention choreography](attention-choreography.md) for the reusable contract.

Treat the world as a map of related ideas. Place islands close enough that a
camera handoff lasts about 2–3 seconds. The attention dot first indicates where
to go; then the camera follows. Ease translation and scale, retain one context
anchor, and settle before readers inspect numbers. Avoid constant zoom, spins,
and travelling text. Dragging changes only the preview camera offset; rendering
resets that offset and uses the authored camera track.

Use deterministic trajectories and partial path reveals; the dot should land on
an actual endpoint, table row or plotted observation. Make final arrowheads at
least 10 px in delivery space, visible against the local surface, and outside
opaque silhouettes. Keep a continuous thin trail when it explains continuity.
