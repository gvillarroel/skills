Create one Mermaid visualization from the data below. No diagram family is specified: choose the family that most truthfully communicates both hierarchy and quantitative magnitude. Use the extended/full-color palette.

Dataset: API capacity in requests per second.

- Platform
  - Primary
    - Search: 480
    - Checkout: 260
  - Specialized
    - Fraud screening: 42
    - Tax calculation: 18

Create exactly these non-empty outputs relative to the workspace root:

1. `deliverables/capacity.mmd`
2. `deliverables/capacity.svg`
3. `deliverables/decision.json`

Requirements:

- Preserve every supplied label and exact numeric value. Do not aggregate, invent, translate, or omit data.
- Make all four leaf labels and values visibly legible in the rendered SVG, including the two smallest leaves.
- Include the supplied unit in the visible title.
- Apply colorset2 because extended/full-color styling is explicit. The rendered data regions must visibly use extended palette colors; metadata alone is insufficient.
- `decision.json` must be a JSON object with exactly four string fields: `selectedFamily`, `declaration`, `colorset`, and a concise non-empty `reason`. Use the canonical family ID and the declaration actually present in the source.
- Use the bundled styler in write mode and then check mode. Render with the bundled renderer and inspect the resulting SVG for Mermaid error elements, required visible terms, clipping, and palette colors.
- Keep generated files outside the copied skill directory.
