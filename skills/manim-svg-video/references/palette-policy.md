# Authored colorset contract

Use the exact tokens in [colorsets.json](../assets/palettes/colorsets.json) for every authored stage, mark, label, connector, control, annotation and export. Prefer colorset1 for red and neutral explanations. Use colorset2 for simultaneous categories or numeric color bands that need additional semantic separation, and record the category/encoding reason. Pick one active set; colorset1 tokens are a subset of colorset2.

Do not generate new hues or opaque RGB tints. Use allowed discrete tokens, geometry, direct labels, dash patterns and opacity for emphasis. Numeric hierarchy lenses use fixed palette bands with an explicit legend; selected states keep those bands and use neutral tokens for inactive cells. Rasterization, antialiasing, shadows and video compression can introduce intermediate display pixels; validate authored paints and exact canvas cells rather than claiming that every encoded MP4 pixel is an exact token.

Preserve producer-owned photographs, portraits, maps, screenshots, brand artwork and imported SVG or video when source fidelity is requested. Those pixels are source material, not authored palette compliance. Report imported source preservation separately from wrapper compliance. To claim that the entire result fits a colorset, obtain or author an explicitly restyled producer asset and validate it before composition; never silently recolor factual source imagery.

Check actual exported SVG paint, computed browser paint or canvas RGB values at initial, changed and highlighted states. Keep essential text at 4.5:1 contrast against its actual backing. A declaration in metadata or unused CSS does not establish compliance.
