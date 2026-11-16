# Frame-area balance diagnostic

Use only the loaded read-only skill and normal local tools. Follow its current
white/grayscale/red area policy. Read only the compact references needed for
this task; execute the supplied helper without reading its implementation unless
an actual failure requires it. Write exactly the paths below.

Create two small white-background diagnostic PNGs, not a production film:
`frames/balanced.png` with roughly 72% white, 19% gray and 9% primary red;
and `frames/excess-red.png` with roughly 50% white, 20% gray and 30% primary red.
Use plain contiguous bands so the rendered areas are independently measurable.
The intentional unlabelled bands test the color mechanism, not narrative quality.
Use a neutral gray and the style's primary red; do not use pink backgrounds.

Run the bundled area checker on both images, writing respectively
`reports/balanced.json` and `reports/excess-red.json`. Accept a diagnostic
exit 2 for the second image only after asserting the actual stored white/red
overages. Use the documented report structure. An expected negative is test
data; do not leave a failing assertion or tool error in the harness.
Repeat the unchanged balanced check and record actual reuse in `reports/reuse.json`.

Write `notes.md` explaining the measured area shares, minimum white and upper
gray/red budgets, why a sparse scene need not fill exact quotas, when colorset2
is justified, how other hues in portraits/logos are interpreted, and what this
checker cannot establish about content presence or readability. Do not claim
a Google Vids export or general aesthetic approval for these diagnostic images.

Required outputs: frames/balanced.png, frames/excess-red.png,
reports/balanced.json, reports/excess-red.json, reports/reuse.json, notes.md.
