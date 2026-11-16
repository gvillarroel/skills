Build a clean continuous-canvas explanatory film in `film` with a source
table, paired comparisons, histories and a proportional category map. The
primary color is red #9e1b32, secondary fills are grays, and black belongs
among the last color options. Keep titles and banners absent, use complete
frame divisions and preserve the source data. The overall duration is 56
seconds at 1920x1080 and 30 fps. This is illustrative data in items:

| ID | Label | Before | After | History |
| --- | --- | ---: | ---: | --- |
| alpha | Alpha | 12 | 8 | 12,10,8 |
| beta | Beta | 8 | 5 | 8,7,5 |
| gamma | Gamma | 16 | 9 | 16,12,9 |
| delta | Delta | 9 | 6 | 9,8,6 |
| epsilon | Epsilon | 5 | 3 | 5,4,3 |
| zeta | Zeta | 7 | 4 | 7,5,4 |

Use colorset1 and make the first category red, followed by distinguishable
light/medium grays. Keep readable labels. Preserve primary red for the guide
and its changing size. Execute an actual browser audit using screenshot
capture at `review/audit.json`; inspect a category frame and write
`review/notes.md` explaining the color order, quantitative area agreement,
and how to change timing. No MP4 is required. Keep the loaded skill read-only
and use only the focused in-bundle resources needed.

Required: `film/story.json`, `film/story.js`, `film/timing.json`,
`review/audit.json`, `review/notes.md`.
