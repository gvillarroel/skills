# Compact connected layouts

Use this workflow for UML and non-UML diagrams that explain linked concepts. Make the composition as compact as its actual labels, semantic glyphs and routes safely allow. Treat readability and source fidelity as hard constraints; optimize space and connector length only among passing layouts.

Preserve all required concepts, relationships, literal labels, arrow/diamond/cardinality semantics, explicit user spacing and geometry. Do not remove information, shrink type, scale the entire image down or clip content to obtain smaller bounds. Quantitative plots, numeric timelines and proportional Gantt schedules keep their measurement scales and information dimensions; do not squeeze their plotted positions using diagram packing.

## Pack and route

1. Start from the bundled native padding of 6 and render the complete source. Inspect the whole diagram and the busiest junction at the intended display size. Keep a last passing render and source while comparing changes.
2. Reclaim unnecessary outer margins and oversized node interiors first. Then move related concepts nearer, balance connected groups, choose an orientation suited to the labels and reuse pockets left by shorter branches. Preserve required event order in sequences and chronology in schedules.
3. Use native source layout controls supported by the selected family to shorten detours and reduce excessive peer/rank gaps. Change one crowded neighborhood at a time. A universal smaller rank gap is unsafe: class compartments, relation labels, message text and endpoint glyphs need different room. Start labeled component graphs with native curved routing; do not impose `linetype ortho` as a compactness default, because a short orthogonal path can place its label across a body or crowd a return route. Use a different line type only when its rendered text and heads clear the actual shapes. Do not edit generated SVG path geometry to hide an unresolved source layout.
4. Reserve complete text and marker envelopes before reducing the adjacent gap. Give each connector a visible departure and approach so the source, target and direction remain evident. Keep unrelated routes distinguishable; do not collapse them into a common painted trunk or create a false junction. Prefer fewer bends and crossings when equally readable layouts are available.
5. Render each proposed revision and run the existing report validator. Compare at the same display width, then inspect full-size detail. Retain a smaller canvas or shorter route only when it introduces no fidelity or readability regression.

## Readability release gate

- Every label is complete, readable and associated with the correct element. Text does not overlap text, paths, heads or unrelated shapes.
- Shafts and complete semantic heads are visible with required contrast against all actual backings. A short edge still has room for its label and every endpoint glyph; inspect the final SVG and PNG rather than relying on the configured gap.
- Trace each relation from its source to its target. Adjacent edges remain independent, crossings are distinguishable from joins and no route appears to attach to an unrelated element.
- Group titles, compartments, notes, ports, cardinalities and endpoint clearances remain intact. Check the longest label, shortest arrow, busiest crossing and most crowded group.
- Remaining empty space serves readable grouping, routing or explicit user requirements. Smaller raw bounds alone do not establish a better composition.

Restore the last passing geometry when a reduction fails, then try moving the specific neighboring group or shortening another route. Stop when no concrete safe reduction remains. Report actual compared bounds or routes when useful; do not claim mathematical global optimality. The render-report validator checks formats, paint and tagged contrast, not every overlap or route ambiguity, so direct visual review remains necessary. Use [native arrow contrast and clearance](arrow-contrast.md) for the complete head-envelope checks.
