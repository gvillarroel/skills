Create a small offline acceptance figure for semantic icons and readable active
objects. Use only the copied `skills/line-world-video/` bundle and normal local
tools. Keep the bundle read-only. Do not use network, live browser sessions,
sibling skills, repository docs or acceptance galleries. A local headless browser
for the authored figure is allowed. Do not read or run the skill's unit tests.

Make a clean white 1920x1080 figure with three simple borderless item containers.
Use three synthetic glyph fixtures: an inline SVG group with hard-coded gray
strokes, a symbol referenced by use with hard-coded gray strokes, and an
external SVG image with hard-coded gray strokes. Keep holes transparent. Label
the objects briefly. Center each combined icon/label block horizontally and
vertically using actual loaded bounds. Put one container under a nonuniformly
scaled parent. Start some glyphs deliberately off-center to demonstrate that
the reusable alignment helper corrects them. No visible title or UI chrome.

At second 2 emphasize the first object in primary red, at second 5 emphasize the
second, and at second 8 emphasize the third. Inactive faces should be light gray.
Use the actual bundled theme to make internal text and glyph strokes white on
red and dark on light gray, including when returning to earlier times. Preserve
all three silhouettes. Use a deterministic renderAt(seconds) and load all needed
assets locally. Use the skill's audit utility to review all three supplied times.

Produce exactly:

- `film/index.html` and `film/theme.js`: editable standalone preview and actual
  copied reusable theme runtime. Keep other needed files beside them.
- `review/items.json`: actual browser observations for seconds 2,5,8, no findings.
- `review/hero.png`: actual 1920x1080 reading frame with a white glyph on red.
- `review/checks.json`: independent verification of both-axis centering within
  two CSS pixels, white visible glyph pixels on each red face, dark inactive
  strokes, containment, correct text foreground and deterministic return seeking.
  Include explicit booleans, sampled pixel counts and top-level ok.

Check actual screenshot pixels for all three glyphs; CSS color alone does not
prove symbol or external SVG paint changed. State honestly that these are local
synthetic fixtures, not provider assets or a Google Vids export.
