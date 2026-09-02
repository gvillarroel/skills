# Accessible Title and Description Metadata

Use this reference for newly authored Mermaid diagrams, authorized source edits that add accessible naming, or release checks that must prove the final SVG metadata. This gate verifies a useful accessible name and description; it does not claim that every diagram relationship becomes structurally navigable to screen readers.

## Author the source directives

Place both directives immediately after the declaration and optional direction:

```mermaid
flowchart LR
  accTitle: Order request validation
  accDescr: Web and mobile requests pass through token validation before permitted orders are written to storage; invalid tokens return to the gateway.
```

- Keep `accTitle` short and specific.
- Write `accDescr` as a content summary or conclusion. Describe facts, states, direction, and outcomes that matter; do not narrate coordinates, colors, or every shape.
- Preserve supplied terminology, factual uncertainty, identifiers, and units.
- Use the multiline `accDescr { ... }` form when one line would become hard to maintain.
- When source editing is prohibited or the meaning is unclear, report missing directives instead of inventing them.

## Gate source and rendered output

First verify the Mermaid source:

```powershell
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --check --require-accessibility --report mermaid-check.json
```

Then gate the SVG generated from that source:

```powershell
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.svg --static-output diagram.static.svg --animation none --require-accessibility
```

The rendered gate requires:

- an actual `<svg>` document root;
- a non-empty direct-child `<title>` with an ID referenced by root `aria-labelledby`;
- a non-empty direct-child `<desc>` with an ID referenced by root `aria-describedby`;
- document-wide unique element IDs and unambiguous ARIA ID references;
- no Mermaid error marker.

Inspect the description against the settled frame. Reject metadata that is present but contradicts the visible conclusion or omits a load-bearing state, count, boundary, or outcome.

## Scope of the claim

Describe the result as a Mermaid diagram with verified accessible title and description metadata. Do not call the entire diagram accessible solely because this gate passes. More complete accessibility may require an adjacent text explanation, data table, or application-specific interaction model.

## Sources

Mermaid documents `accTitle` and `accDescr` as the accessibility directives for all diagram types in its [Accessibility documentation](https://mermaid.js.org/config/accessibility.html). The content-oriented naming and static-first release checks also adapt transferable guidance from [Cathryn Lavery's Diagram Design repository](https://github.com/cathrynlavery/diagram-design) at commit `f3622cf66a3c557cb2ead57b687a3c1ff63f5a2b` (MIT).
