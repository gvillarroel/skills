Use the loaded D3 Animated SVG skill to create a self-contained HTML file named `d3-generalization-cardinality.html` in the current workspace.

The artifact must test whether two D3 SVG patterns generalize to smaller and larger datasets without losing coherence:

- `d3-pattern-force-network`
  - `svg#force-small`: 5 nodes and at least 5 links
  - `svg#force-medium`: 12 nodes and at least 16 links
  - `svg#force-large`: 36 nodes and at least 45 links
- `d3-pattern-beeswarm`
  - `svg#beeswarm-small`: 9 observations
  - `svg#beeswarm-medium`: 30 observations
  - `svg#beeswarm-large`: 90 observations

Use this exact structured contract as the source of truth for IDs, pattern IDs, sizes, and counts. Copy these numeric values exactly; do not round, densify, rebalance, or choose nearby values:

```json
{
  "title": "D3 Cardinality Generalization",
  "subtitle": "Force-network and beeswarm examples scale from small to large while preserving the same visual language.",
  "requireReducedMotion": true,
  "forbidRemote": true,
  "svgs": [
    {
      "id": "force-small",
      "patternId": "d3-pattern-force-network",
      "size": "small",
      "targetCount": 5,
      "marks": {
        "node": { "equals": 5 },
        "link": { "min": 5 }
      }
    },
    {
      "id": "force-medium",
      "patternId": "d3-pattern-force-network",
      "size": "medium",
      "targetCount": 12,
      "marks": {
        "node": { "equals": 12 },
        "link": { "min": 16 }
      }
    },
    {
      "id": "force-large",
      "patternId": "d3-pattern-force-network",
      "size": "large",
      "targetCount": 36,
      "marks": {
        "node": { "equals": 36 },
        "link": { "min": 45 }
      }
    },
    {
      "id": "beeswarm-small",
      "patternId": "d3-pattern-beeswarm",
      "size": "small",
      "targetCount": 9,
      "marks": {
        "dot": { "equals": 9 }
      }
    },
    {
      "id": "beeswarm-medium",
      "patternId": "d3-pattern-beeswarm",
      "size": "medium",
      "targetCount": 30,
      "marks": {
        "dot": { "equals": 30 }
      }
    },
    {
      "id": "beeswarm-large",
      "patternId": "d3-pattern-beeswarm",
      "size": "large",
      "targetCount": 90,
      "marks": {
        "dot": { "equals": 90 }
      }
    }
  ],
  "monotonic": [
    { "ids": ["force-small", "force-medium", "force-large"], "mark": "node" },
    { "ids": ["force-small", "force-medium", "force-large"], "mark": "link" },
    { "ids": ["beeswarm-small", "beeswarm-medium", "beeswarm-large"], "mark": "dot" }
  ]
}
```

Requirements:

- Keep the file fully self-contained: no CDN scripts, remote fonts, remote CSS, remote images, or external runtime imports.
- Use deterministic inline data and final-state SVG geometry.
- Render all six requested SVGs visibly in the HTML.
- Each SVG must include `<title>`, `<desc>`, a stable `viewBox`, explicit SVG text `font-family`, `data-pattern-id`, `data-size`, and `data-target-count`.
- Force-network node marks must use class `node`; link marks must use class `link`.
- Beeswarm observation marks must use class `dot`.
- Use the skill's visual tokens and portable CSS or SVG-native animation.
- Include a reduced-motion fallback that keeps the final state visible.
- Keep labels readable at every dataset size; for large variants, label only representative or grouped marks instead of every mark.
- Treat the copied `skills/d3-animated-svg/` directory as read-only. Do not write into it.
- Do not read files outside the current workspace.

Return only a brief completion note after writing the file.
