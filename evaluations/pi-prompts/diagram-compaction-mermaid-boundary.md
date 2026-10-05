Style and render a small synthetic Mermaid flow diagram while preserving my explicit geometry. Save this exact starting source at `override.mmd`:

```text
---
config:
  flowchart:
    padding: 18
    nodeSpacing: 42
    rankSpacing: 90
---
flowchart TB
  accTitle: Synthetic records review with preserved spacing
  accDescr: A regional conservation office sends complete records to independent review and then to the approved public archive.
  A["Regional Conservation Office for Manuscript Records"] -->|complete records retained| B["Independent Preservation and Access Review"]
  B -->|approved with provenance| C["Public Archive and Research Collection"]
```

Use standard colors and keep the complete text, heads and relation labels visible. My padding and spacing are intentional; compactness must preserve these values. Create exact outputs `override.mmd`, `override.svg`, `style.json`, `check.json`, and `review.md`. State which layout constraints were retained and what could actually be verified. Keep `skills/mermaid/` read-only and all generated or comparison files in the workspace. Do not read galleries or other skills.
