Use the loaded evaluator skill. Treat `skills/d3/` as read-only. Create exactly `evaluation.md` in the workspace root. Do not write elsewhere and do not inspect parent directories, sibling skills, repository fixtures, or evaluation contracts.

Evaluate radial variant `d3-composition-radial-force-network` from this SVG:

```html
<svg id="d3-composition-radial-force-network" data-composition-id="radial" data-example-id="force-network" data-pattern-id="d3-force-network" data-composition-pattern-id="d3-composition-radial-force-network" viewBox="0 0 360 220">
  <title>Force Network radial network</title>
  <desc>Hub node with peers orbiting.</desc>
  <line x1="180" y1="110" x2="180" y2="40"/>
  <line x1="180" y1="110" x2="252" y2="78"/>
  <line x1="180" y1="110" x2="238" y2="162"/>
  <line x1="180" y1="110" x2="122" y2="162"/>
  <line x1="180" y1="110" x2="108" y2="78"/>
  <circle cx="180" cy="110" r="14"/>
  <circle cx="180" cy="40" r="8"/>
  <circle cx="252" cy="78" r="8"/>
  <circle cx="238" cy="162" r="8"/>
  <circle cx="122" cy="162" r="8"/>
  <circle cx="108" cy="78" r="8"/>
</svg>
```

Start with exactly `Artifact: d3-composition-radial-force-network`. Include `Findings`, `Composition Score`, and `Fixes` sections. Under `Composition Score`, write exactly one score as `Score: N/100`; do not add component scores. Preserve all six nodes and five links, and do not propose adding or removing data entities.
