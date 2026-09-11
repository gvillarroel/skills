# Visual grammar

## Reference observations

The following are observations from official product preview images inspected on 2026-09-11, not measurements of their production files. They describe transferable layout decisions rather than a tracing recipe.

| Reference | Spatial organization | Connection and color decisions |
| --- | --- | --- |
| [European Royal Family Tree (West)](https://usefulcharts.com/products/european-royal-family-tree) | Tall poster; centered condensed uppercase title; cream field; neighboring dynastic columns; small name/date blocks; occasional larger focal rulers; family labels between generations. | Mostly orthogonal trunks, short sibling bars, long cross-column relationships in reserved gaps; stable branch colors; differentiated line textures; related people often use simpler text-only labels. |
| [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) | Tall branching field; common origins near the top; expanded branches below; compact names; larger anchor institutions; contextual map and pictogram panels occupy upper side space. | Color represents major branches (also explicitly stated by the product page); lines carry those colors; solid and dotted paths distinguish relations; visual size creates hierarchy. |
| [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history) | Vertical time axis; parallel regional columns; interval ribbons; period labels; short contextual annotations; common chronology allows lateral comparisons. | Consistent region/culture colors; tapered or linked transitions where appropriate; dotted cross-region links; time position is meaningful. |
| [Writing Systems of the World](https://usefulcharts.com/products/writing-systems-of-the-world) | Condensed title on dark ground; multiple aligned comparison tables; strong category headers; dense but regular glyph rows. | Color distinguishes type sections rather than relationships; pale alternating rows help comparisons. This matrix family is outside the bundled graph renderer. |

These references include portraits, symbols, and backgrounds that the default renderer does not reproduce. Add factual illustrations only when they improve recognition and their sources permit reuse. Do not substitute decorative fake portraits or meaningless emblems.

## Transferable design decisions

- **Page silhouette:** start around 1600 × 2400 units for a 24 × 36 inch poster. A 100–140-unit title strip anchors the page. Reserve roughly 70–80% of height for the diagram. Keep the outer border thin and the chart field uninterrupted.
- **Hierarchy:** use a bold condensed sans serif title; a small subtitle; short uppercase branch headers; bold node names; smaller dates or role labels. A few focal nodes may use stronger fills. Do not give every label the same visual weight.
- **Placement:** put ancestors or precursors above descendants; place partners side by side and siblings under their joint origin. Keep trunks roughly vertical. Let space express the hierarchy instead of putting everything in equally sized dashboard panels.
- **Connectors:** route behind labels. Attach at visible ports on node boundaries. Reserve horizontal corridors between ranks. Use a dot only at a real junction. A crossing is not a junction. Use a small background-colored bridge/halo when two unrelated paths cross, and check that every line remains traceable.
- **Relationship vocabulary:** a solid line can mean descent or an explicitly defined branch; two short parallel lines mean a partnership in the bundled genealogy recipe; dashed lines mean uncertainty; dotted arrows mean influence. Show every used convention in the legend. Do not silently equate adoption with uncertainty or succession with parentage.
- **Color:** assign 4–7 distinguishable category colors for a dense page; fewer for a small dataset. Reuse the category color on nodes, trunks, and headers. Typical families include coral, sky blue, gold, sage, lilac, and orange. Keep text dark on light fills; derive white/dark text from contrast on custom dark colors. Category labels are the redundant cue for color.
- **Density:** dense should mean many readable relationships, not many unrelated ornaments. Aim for enough nodes to show branching behavior; for a small dataset use a smaller page. Keep labels spacious inside compact boxes. Increase canvas area or split an atlas when labels cannot fit.
- **Context:** add a concise key, dated source note, and a reading note distinguishing time from generation/rank. Keep legal or technical evaluation detail out of the chart itself.

## Practical limits

The bundled title face is unmodified [Barlow Condensed Bold](https://github.com/google/fonts/tree/main/ofl/barlowcondensed), by the Barlow Project Authors, under the [SIL Open Font License](../assets/fonts/OFL.txt). The renderer embeds the font and its license in every SVG so the condensed title does not depend on an installed font. Body text uses Arial or Liberation Sans; validate its measured geometry on the actual rendering system.

At 1600 viewBox units across 24 inches, a 16-unit font is about 17.3 points in print. Screen-fit previews inevitably make dense poster text small; provide zoom and inspect the full-resolution artifact. A 200-node historical chart needs a larger canvas, more authoring, and factual verification than a 40-node synthetic demonstration. Do not imply that a few sample posters validate all genealogies or all writing systems.
