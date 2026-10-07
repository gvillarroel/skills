# Dispatch sketch in viewport coordinates

Please turn this dispatch sketch into a local editable Lucidchart import package. Preserve its rendered viewport positions and sizes, the two literal labels, contrasting paints and text formatting, and the rounded corners where supported. Keep the original SVG at `inputs/dispatch.svg`. Write the recovered graph to `outputs/dispatch/graph.json`, the source inspection to `outputs/dispatch/inspection.json`, the source-to-native mapping ledger to `outputs/dispatch/mapping.json`, the package to `outputs/dispatch/diagram.lucid`, and the package's document JSON to `outputs/dispatch/document.json`.

Write `outputs/dispatch/fidelity.md` explaining which concrete source details were recovered, which were adapted, and what still needs visual or live Lucid verification. Identify the coordinate policy and distinguish local package preparation from a completed service import. Do not assign an overall visual-fidelity percentage.

Use only the read-only `skills/lucidchart-svg/` bundle and normal local tools. Keep generated files in this workspace outside that bundle. Work offline: do not use network access, external services, credentials, or a live Lucid session. Save the following source exactly as UTF-8 without a BOM, with LF line endings and one final LF; preserve its bytes thereafter.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="dispatch-canvas" width="800" height="360" viewBox="10 20 400 360" preserveAspectRatio="none" data-title="Dispatch sketch">
  <g id="dispatch-stage" transform="translate(20 30) scale(1 2)">
    <g id="receive-group" data-node-id="receive">
      <rect id="receive-box" x="10" y="20" width="110" height="40" rx="4" fill="#EAF3FA" stroke="#25364A" stroke-width="1"/>
      <text id="receive-label" x="17" y="44" font-family="Georgia" font-size="11" font-weight="bold" fill="#17334D">Receive &amp; classify</text>
    </g>
    <g id="archive-group" data-node-id="archive" transform="matrix(1.5 0 0 1.5 170 65)">
      <rect id="archive-box" x="10" y="5" width="90" height="36" fill="#FFF0D6" stroke="#8B4A18" stroke-width="2" stroke-dasharray="6 2"/>
      <text id="archive-label" x="16" y="27" font-family="Verdana" font-size="10" font-style="italic" fill="#623211">Archive &lt;Q4&gt;</text>
    </g>
  </g>
</svg>
```
