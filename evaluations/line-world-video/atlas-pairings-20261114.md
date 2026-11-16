# Line World atlas: coverage and pairing review

Reviewed November 14, 2026 against the rendered 185-second film and full-size
reading frames. These are editorial decisions from the actual artifacts, not
measured audience-study results or claims that every supported form belongs
in one production narrative.

## Coverage and sources

The atlas contains 16 scene compositions and 46 distinct producer views:
20 native Mermaid families and 26 D3 forms. The bundled Mermaid inventory
lists 31 families, so the selection covers 20/31 of that specific inventory.
It does not claim coverage of all future Mermaid releases or every possible
D3 construction. The D3 count is an explicit form inventory, not a percentage
of the D3 API.

Mermaid families: flowchart, sequence, state, mindmap, treemap, Sankey, ER,
class, Gantt, timeline, quadrant, radar, XY, journey, Kanban, Git, requirement,
block, architecture and pie. Omitted from the bundled 31-family inventory:
swimlane, C4, ZenUML, packet, event modeling, Venn, Ishikawa, Wardley, Cynefin,
tree view and railroad. The omission keeps the comparison readable and avoids
forcing unrelated notations into this illustrative dataset.

D3 forms: seeded network, scatter, histogram, stacked area, event raster,
radial tree, circle pack, sunburst, treemap, directed chord, adjacency matrix,
linked table/bars, bump, intervals, streamgraph, lines, parallel coordinates,
boxplot, dumbbell, orthographic globe, donut, lollipop, Voronoi, Delaunay,
density contours and beeswarm. The globe uses genuine city coordinates and a
graticule, without inventing land shapes; deployment relationships are synthetic.

The implementation choices follow the actual roles described in the
[D3 hierarchy API](https://d3js.org/d3-hierarchy),
[D3 Delaunay/Voronoi API](https://d3js.org/d3-delaunay),
[Mermaid Sankey syntax](https://mermaid.js.org/syntax/sankey.html),
[Mermaid radar syntax](https://mermaid.js.org/syntax/radar.html) and
[Mermaid treemap syntax](https://mermaid.js.org/syntax/treemap.html).
The selected renderer is pinned to Mermaid CLI 11.16.0, rather than assuming
that the current public website's version is identical.

## Decisions after visual review

| Scene / reading frame | Combination | Editorial decision |
| --- | --- | --- |
| Process / 5.5 s | Native flowchart + seeded network | Useful for showing a change of graph layout and stable identities. For a concise production story, process + measured timings adds more information. |
| Interactions / 16.1 s | Sequence + scatter + histogram | Strong: message order, individual latency and its distribution answer different questions. Keep aggregate distributions distinct from row-level measurements. |
| States / 26.5 s | State machine + stacked stage histories + observation raster | Useful with explicit units. This fixture plots days and observation positions; a legal transition does not establish frequency or occupancy. |
| Hierarchy / 37.1 s | Mindmap + radial tree + circle pack | Comparison control: mindmap/tree overlap in purpose. Keep one structural view and packing when branch magnitude matters. |
| Parts / 48.1 s | Native treemap + D3 sunburst + D3 treemap | Comparison control. The full-width native strip improves reading size. Prefer one partition with a table or selected detail in production. |
| Flows / 60.2 s | Sankey + directed chord + matrix | Sankey + matrix is the best default pair here. Chord is an alternative overview when many reciprocal links matter. Do not imply mass conservation from an arbitrary transfer matrix. |
| Records / 73.7 s | ER + class contract + linked table/bars | Strongest source-to-mark example. Choose the schema notation relevant to the audience; keep both only to compare the contracts. |
| Schedule / 86.1 s | Gantt + rank history + actual intervals | Gantt + intervals is clear. This fixture's ranks stay fixed, making the bump view a control; use bump when ranks actually change. Rank is not duration. |
| History / 97.1 s | Timeline + streamgraph + directly labeled lines | Timeline + lines is the best default. Streamgraph is conditional because its moving baseline makes absolute readings harder. |
| Tradeoffs / 108.1 s | Quadrant + parallel coordinates + boxplot | Useful when a decision uses effort/impact, several dimensions and variability. Use explicit units and avoid inventing a shared metric. |
| Profiles / 119.1 s | Radar + XY + dumbbell | Dumbbell is clearest for precise before/after comparison. Radar is a compact shape comparison with dashed/solid series, not the precision view. |
| Experience / 129.5 s | Journey + Kanban | The full-width stacked sections fit these wide notations better than portrait halves. Use only when actors/tasks refer to the same workflow. |
| Contracts / 140.1 s | Git history + requirement + block | Conditional: a useful cross-layer explanation if the revision, constraint and implementing component are actually linked. |
| Deployment / 151.1 s | Architecture + projected city coordinates | Strong: topology and location add distinct facts. Keep technical glyphs consistent and avoid decorative map shapes. |
| Shares / 161.5 s | Pie + donut + lollipop | Deliberate control. Pie/donut repeat the same proportion; lollipop makes differences and exact values easier to compare in this dataset. |
| Space / 172.6 s | Voronoi + Delaunay + density + x projection | Strong geometric comparison using the same seeded samples. State that beeswarm projects one dimension and density aggregates points. |

## Style and timing conclusions

Every scene partitions the complete frame with margins inside its sections.
Wide strips work better for time/process-history notations; tall sections work
for compact state chains and schemas. An overview follows readable full-size
holds, and the sixteen-cell world fills the final frame exactly.

Use colorset1 here: white surfaces, charcoal/gray geometry and red attention.
Extra hue is unnecessary for these comparisons. Colorset2 remains available
for actual simultaneous category distinctions, with a reason and stable mapping.
Keep the visible text to entity names, values, axes, units and useful legends.
The family names, review notes and transport controls remain outside the film.

The final browser audit records 34 states with zero findings and zero small-label
warnings, including pairwise label clearance. Native HyperFrames checks pass;
its one retained rotation-pivot warning is reviewed separately as fixed native
axis labels moving with the world camera. The full MP4 decode verifies all
5,550 frames, exact duration/fps/dimensions and visible motion.
