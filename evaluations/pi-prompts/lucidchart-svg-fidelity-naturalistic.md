# Appearance-sensitive SVG reconstruction

Use only the read-only skill at `skills/lucidchart-svg/` and normal local tools. Work offline in this workspace. No Lucid session, API credentials, import result, or service screenshot is available.

Prepare this SVG for both artwork insertion and editable native reconstruction. Preserve the source in `input/styled.svg`, make a byte-preserving upload candidate at `deliver/artwork.svg`, and write its inspection to `deliver/inspection.json`. Recover the two explicitly identified nodes and the directed relationship into `deliver/graph.json`, then prepare `deliver/native.lucid` and `deliver/document.json` with the bundled compiler. Preserve the supplied node bounds, literal labels, solid fills/border/text colors, and explicit horizontal connection ports where the compiler supports them.

Write `deliver/fidelity.md` reviewing what this SVG's actual details retain or lose in the chosen routes, what was verified locally, what needs a live Lucid check, and whether the artifacts qualify as a completed upload. Include enough concrete source-versus-output detail to guide someone deciding between editable objects and preserved artwork. Do not give an unsupported overall visual percentage. Do not modify the skill bundle.

Use this source verbatim:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="180" viewBox="0 0 400 180">
  <defs><marker id="head" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#AA1133"/></marker></defs>
  <g id="source-group"><g id="request" data-node-id="request"><rect x="20" y="50" width="120" height="60" rx="12" fill="#FFEEEE" stroke="#333333" stroke-width="3" stroke-dasharray="5 3"/><text x="28" y="83" font-family="Georgia" font-size="20" font-weight="bold" fill="#223344">Request &amp; check</text></g>
  <g id="store" data-node-id="store"><rect x="220" y="50" width="140" height="60" rx="8" fill="#DDEEFF" stroke="#445566" stroke-width="2"/><text x="228" y="83" font-family="Georgia" font-size="20" font-style="italic" fill="#223344">Store &lt;P1&gt;</text></g>
  <path id="submit" data-source="request" data-target="store" d="M140 80C160 20 200 140 220 80" fill="none" stroke="#AA1133" stroke-width="2.5" stroke-dasharray="4 2" marker-end="url(#head)"/></g>
</svg>
```
