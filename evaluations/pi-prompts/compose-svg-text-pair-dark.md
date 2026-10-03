Create a standalone SVG for a municipal water operations dashboard. Use a dark
canvas of exactly `#101820` and card surfaces of exactly `#18242f`. Choose readable
text and compatible concept colors. Keep the palette centrally editable and
make every number legible on its own background, including scenario and focus
controls. Use English labels and visibly identify the data as illustrative.

Use only the loaded `compose-synchronized-svg` skill and normal local tools.
Treat `skills/compose-synchronized-svg/` as read-only. Keep all outputs in this
workspace; do not read examples, sibling skills, parent directories, repository
documents, or the network. Regenerate from the brief rather than patching an SVG.

Use six useful modules: operating dependencies, water allocation, demand against
capacity, leakage share, demand/capacity comparison, and an exact ledger. Choose
truthful encodings and meaningful relationships. Use scenario controls with no
autoplay timeline. Canonical inputs are daily demand and treatment capacity in
ML/day, plus leakage fraction. Normal values are 120, 150, and 0.15; peak values
are 180, 150, and 0.20; repair values are 180, 150, and 0.08.

Processed water is min(demand, capacity); leakage is processed times leakage
fraction; delivery is processed minus leakage; unmet demand is demand minus
processed; load is demand divided by capacity. Demand must equal delivery plus
leakage plus unmet demand. Include legal domains with zero demand, demand up to
240, capacity 80 to 220, and leakage 0 to 0.35. Peak to repair changes only
leakage and delivery among these outputs. A load over 100% must be shown honestly.

Create these exact outputs:

- `outputs/dark/brief.json`
- `outputs/dark/plan.json`
- `outputs/dark/dashboard.svg`
- `outputs/dark/static.json`
- `outputs/dark/browser.json`
- `outputs/dark/overview.png`
- `outputs/dark/color-editing.md`

Use normal skill generation and both bundled validators. The static and compact
browser reports must have `ok: true`. Inspect the overview and document how to
change colors and regenerate. Retain useful script-free and reduced-motion
states and accessible controls. Report any remaining quality issue honestly.
