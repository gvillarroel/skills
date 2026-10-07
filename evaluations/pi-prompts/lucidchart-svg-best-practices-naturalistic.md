# Metadata-bearing SVG conversion

Create `input/source.svg` with exactly the UTF-8 bytes below, including a final newline:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 100 100" data-title="Audit"><defs><marker id="head" orient="auto" markerWidth="3" markerHeight="3" refX="3" refY="1.5"><polygon points="0,0 3,1.5 0,3" fill="#333333"/></marker></defs><g transform="translate(5 0)"><g data-node-id="request"><rect x="0" y="10" width="20" height="30" fill="#ffffff" stroke="#333333" stroke-width="0.5"/><text x="10" y="25" text-anchor="middle" font-family="Arial" font-size="5" fill="#111111">A &amp; B</text></g><g data-node-id="audit"><rect x="60" y="10" width="20" height="30" rx="2" ry="2" fill="#eeeeee" stroke="#333333" stroke-width="0.5" stroke-dasharray="2 1"/><text x="70" y="25" text-anchor="middle" font-family="Arial" font-size="5" fill="#111111">Audit</text></g><path id="e" data-source="request" data-target="audit" d="M20 25 L60 25" fill="none" stroke="#333333" stroke-width="0.5" marker-end="url(#head)"/><text data-edge-id="e" x="40" y="20" text-anchor="middle" font-family="Arial" font-size="5" fill="#111111">yes</text></g></svg>
```

Prepare this diagram for Lucidchart with individually editable shapes and attached connectors, keeping its 300×200 viewport, the letterboxing implied by its viewBox, original meaning and supported style details. Use explicit viewport pixel coordinates. Do not redesign it. There is no authenticated Lucid connection in this evaluation.

Deliver exactly:

- `out/inspection.json`: source inventory.
- `out/mapping.json`: source-to-native feature ledger.
- `out/graph.json`: resolved editable graph.
- `out/diagram.lucid`: Standard Import package.
- `out/document.json`: its document JSON.
- `out/native-report.json`: emitted compatibility decisions.
- `out/changes.md`: concise, factual English account of preserved details, changes and unverified live behavior. Identify which border is dashed, the coordinate mapping, and limitations of dash/marker/text rendering.

Preserve the source bytes and keep all generated files outside the skill resources. Verify the package locally; do not claim an actual Lucid document or overall visual-preservation percentage.
