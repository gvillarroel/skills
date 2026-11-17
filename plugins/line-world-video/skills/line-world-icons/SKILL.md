---
name: line-world-icons
description: Selects, exports and verifies coherent monochrome SVG icons for Line World videos, preserving Iconify identity and licenses. Use for meaningful glyphs inside the video plugin with shared stroke weight, neutral paint and parent-controlled motion.
---

# Line World Icons

Read the [video contract](references/video-contract.md). Use an icon only when
its silhouette adds meaning or makes a repeated entity easier to recognize.

1. Prefer one monochrome outline family, initially Lucide. Search the intended
   concepts with the bundled `scripts/iconify.py` helper, inspect actual SVG
   candidates and choose a coherent set. A request for a set authorizes the
   selection; honor an exact requested provider ID.
2. Export the real provider SVG, not an invented technical logo. Keep original
   license text and the helper's receipt. Store outputs in the project.
3. Derive monochrome foreground from the visible face: white text/icons inside
   primary red or dark gray, dark ink on light gray/white. Mark the glyph
   `data-lw-icon="monochrome"`; use the bundled theme's `finish`, reversible
   `focus` and `contrast` helpers so hard-coded strokes adapt too. Keep consistent
   size and a shared optical stroke weight. Keep multicolor brand assets only when their
   identity is actually needed; explain their source colors in the receipt.
4. Remove preview cards, captions, numbered choice badges, shadows and download
   controls before embedding the chosen icon. Keep a short entity label only
   when the symbol alone would be ambiguous. Do not repeat both icon and text
   decoratively beside every mark.
5. Center the combined icon/label block in both axes using actual loaded bounds.
   Give each face its own parent and explicit `data-lw-content`/`data-lw-for`
   when needed. Preserve chart coordinates and outside labels. Use the theme
   audit to reject poor contrast, off-center content and overflow in active and
   inactive states; inspect actual rendered glyph pixels, not just CSS color.
6. Return native bounds, semantic ID, focus port, source ID and license receipt.
   Let the parent clock own motion; avoid spinning or bouncing glyph loops.
   Inspect the silhouette at playback size and beside adjacent charts.

The [producer workflows](references/producer-workflows.md) retain exact search,
download and licensing commands. Their numbered selection galleries and filled
preview chrome belong outside the film.

For meaningful static logos, read [gentle motion](references/gentle-motion.md).
Float complete logo/label groups with slow, small, stable-ID motion.
