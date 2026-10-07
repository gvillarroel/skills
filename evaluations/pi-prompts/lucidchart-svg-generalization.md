# Vertical SVG incident workflow

Use the read-only skill at `skills/lucidchart-svg/`. Write all task files in this isolated workspace. Work offline; no service mutation is available.

Reconstruct this SVG incident workflow into a locally prepared Lucidchart native package. Preserve the four objects' labels, colors where applicable, positions after resolving the translation, and the two arrows' explicit endpoints. Write `deliver/incident.lucid`, `deliver/document.json`, `deliver/graph.json`, and `deliver/changes.md`. Explain any approximation and whether Lucid accepted the package. The note object is native text; it has no fill or stroke. Use top/bottom connection ports for the vertical workflow.

Create `source/incident.svg` from:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500"><g transform="translate(10 20)"><g data-node-id="alert" id="alert"><ellipse cx="170" cy="50" rx="70" ry="30" fill="#ffeecc" stroke="#333333"/><text x="170" y="55">Alert &amp; triage</text></g><g data-node-id="resolve" id="resolve"><rect x="100" y="170" width="140" height="60" fill="#ffffff" stroke="#333333"/><text x="170" y="205">Resolve &lt;P1&gt;</text></g><g data-node-id="close" id="close"><rect x="100" y="320" width="140" height="60" fill="#eeeeee" stroke="#333333"/><text x="170" y="355">Close</text></g><text id="note" data-node-id="note" data-box="250 180 130 40" x="250" y="205" fill="#111111">SLA: 30 min</text><path id="e-triage" data-source="alert" data-target="resolve" d="M170 80L170 170"/><path id="e-close" data-source="resolve" data-target="close" d="M170 230L170 320"/></g></svg>
```
