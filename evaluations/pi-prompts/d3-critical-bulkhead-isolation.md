Create a self-contained standalone HTML file at exactly `bulkhead.html`.

Read this exact pattern reference first: `skills/d3-animated-svg/references/patterns/critical-bulkhead-isolation.md`.

The only valid way to create the artifact is to run the bundled builder:

```powershell
uv run --script skills/d3-animated-svg/scripts/build_critical_bulkhead_isolation.py bulkhead.html
```

Do not hand-author a substitute artifact. Do not create a canvas, CSS-only demo, generic HTML card, or JavaScript-rendered empty SVG. After running the builder, inspect `bulkhead.html` and confirm it contains `<svg id="critical-bulkhead-isolation"` and `data-pattern-id="d3-pattern-critical-bulkhead-isolation"`.

The artifact must use the exact pattern `d3-pattern-critical-bulkhead-isolation` and render one inline SVG showing deterministic clients, router, isolated bulkhead cells, resource pools, pool slots, bulkhead walls, isolation boundary, saturated noisy cell, overflow shed path, utilization trend lines, policy steps, request pulses, and status cards. Use portable SVG animation, title/desc accessibility nodes, stable SVG data attributes, `data-saturated-cell`, `data-shed-rate`, `data-protected-cell-count`, `data-partition-key`, `data-concurrency-limit`, `.bulkhead-client`, `.bulkhead-router`, `.bulkhead-cell`, `.resource-pool`, `.pool-slot`, `.bulkhead-wall`, `.isolation-boundary`, `.bulkhead-flow-path`, `.bulkhead-request-pulse`, `.saturation-wave`, `.shed-path`, `.overflow-shed`, `.cell-health-line`, `.cell-health-point`, `.bulkhead-policy-step`, and `.bulkhead-status-card` classes.

Do not read files outside the current workspace. Do not use CDN scripts, remote fonts, remote images, or external runtime dependencies.
