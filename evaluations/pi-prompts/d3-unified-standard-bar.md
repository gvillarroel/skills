Create a deterministic, self-contained D3 bar-chart deliverable using the installed `d3` skill.

Write exactly these non-empty files relative to the workspace root:

- `deliverables/visual.html`
- `deliverables/decision.json`

Use the skill's deterministic contract builder and its required validation workflow. Do not edit either generated file after the builder writes it. The visual contract is:

- kind: `bar`
- route: `d3-bar`
- active palette: `colorset1` (the standard/default palette)
- pattern ID: `d3-release-readiness-bar`
- SVG ID: `release-readiness`
- title: `Release readiness`
- description: `Completed checks by release stage.`
- decision reason: `A bar chart makes ordered stage totals directly comparable.`
- viewBox size: 960 by 540
- unit: `checks`
- bar class: `readiness-bar`
- exact ordered items: `Build=12`, `Verify=9`, `Release=6`
- exact data attributes on the SVG: `data-layout=vertical` and `data-stage=release`

Keep the artifact fully offline and use only exact lowercase six-digit tokens from colorset1. Include D3 data binding in the deliverable and preserve all requested literals exactly. Validate the final generated artifact for self-containment, colorset1 compliance, IDs, class count, attributes, visible labels, values, unit, and item order. Temporary render and report files must stay outside `deliverables/`.
