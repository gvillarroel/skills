Choose whether each request should activate the candidate skill using only this metadata:

Name: hierarchy-lens
Description: Build offline interactive radial hierarchies, including text-free pixel-art heatmaps, with fixed geometry and switchable categorical or numeric color lenses. Use for organizational maps, reporting structures, portfolios, or taxonomies that need one visual object with multiple attribute views, branch exploration, and exact record lookup.

Requests:

1. Turn 2,000 employees and their reporting lines into a radial map; let me color the same blocks by role, contract, or monthly tokens.
2. Create a text-free pixel-art image of a research hierarchy, with the root centered, levels going outward, and switchable status and expenditure colors.
3. Plot daily temperature over a year as a line chart.
4. Show a dense social graph where every person can connect to several unrelated people; preserve all edges.
5. Convert this existing landscape photograph into retro pixel art.
6. Make a radial heatmap of biological classifications with switchable conservation status and recorded sightings, keeping the structure fixed.
7. Make a PNG company logo shaped like a ring, with a pixel-art aesthetic.
8. Create a conventional labeled sunburst of my organizational hierarchy with branch lookup and selectable role colors.

Write routing.json as an array of objects with request (integer), useSkill (boolean), and reason (string). Do not build a visualization. No skill is explicitly loaded, and ambient skill discovery is disabled. Do not read external files or services. Keep the output in the current workspace.
