# Force Networks

- **Data shape:** Use nodes with stable IDs and links that reference source and target IDs. Add group, weight, time, or status fields only when they affect layout or styling.
- **Animation pattern:** Pre-tick the simulation to a deterministic settled state, then animate from grouped, radial, or staged initial coordinates into the final positions. For live HTML, add drag and hover only after the initial settle.
- **Display guidance:** Use when collision, clustering, gravity, or topology change is part of the explanation. Add legends for force groups and keep labels sparse or hover-driven.
- **D3 APIs:** `forceSimulation`, `forceLink`, `forceManyBody`, `forceCollide`, `forceX`, `forceY`, `randomLcg`.
- **Pitfalls:** Unseeded force layouts are not reproducible. Dense labels and hairball links need clustering, filtering, edge bundling, or matrix alternatives.
