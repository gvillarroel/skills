Create a deterministic, self-contained D3 radial-wedge logo using the installed `d3` skill.

Write exactly these non-empty files relative to the workspace root:

- `deliverables/extended-logo.html`
- `deliverables/extended-logo-decision.json`

Use the skill's deterministic contract builder and its required validation workflow. Do not edit either generated file after the builder writes it. The public contract is:

- kind: `logo`
- route: `d3-logo`
- active palette: `colorset2` (explicit extended/full-color mode)
- pattern ID: `d3-signal-works-wedges`
- SVG ID: `signal-works-logo`
- title: `Signal Works radial identity`
- description: `A deterministic extended-color radial identity.`
- decision reason: `Radial wedges express coordinated signal channels around one center.`
- viewBox size: 900 by 520
- brand: `Signal Works`
- tagline: `Clarity in motion`
- logo mode: `wedges`
- wedge count: `16`
- logo mark class: `signal-logo-mark`
- wedge class: `signal-wedge`
- brand class: `signal-brand`
- tagline class: `signal-tagline`
- exact SVG attribute: `data-identity=signal-works`

Preserve every literal exactly. The visible wedges must use colorset2's blue, orange, green, and purple groups, while all paint remains inside the colorset2 palette. Keep the artifact offline, accessible, deterministic, and browser-readable. Validate self-containment, required extended palette influence, IDs, classes, attribute, brand, tagline, and wedge count. Keep temporary render and report files outside `deliverables/`.
