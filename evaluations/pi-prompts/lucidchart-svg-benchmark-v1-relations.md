# Preserve a release-routing sketch

Please prepare an editable local Lucidchart import package from this release-routing SVG. Preserve all three nodes, both directed relationships, their attached endpoint positions, the interior route turns, literal node and edge labels, and supported colors and text styles. Keep enough source attribution to trace each resulting object back to its explicit metadata. Use the rendered viewport coordinate system.

Save the exact original to `source/release-route.svg`. Write the recovered graph to `deliver/release/graph.json`, source inspection to `deliver/release/inspection.json`, mapping ledger to `deliver/release/mapping.json`, native package to `deliver/release/native.lucid`, and its document JSON to `deliver/release/document.json`. Write `deliver/release/changes.md` explaining specific route, marker, label-placement, and appearance adaptations and the limits of local verification. The SVG arrow definitions and their rendered size matter to this review. Do not claim a completed Lucid import or an overall visual-fidelity percentage.

Use only the read-only `skills/lucidchart-svg/` bundle and normal local tools. Keep generated files outside the bundle in this workspace. Work offline without network access, credentials, external services, or a live Lucid session. Save the source exactly as UTF-8 without a BOM, with LF line endings and one final LF; preserve its bytes thereafter.

```xml
<svg xmlns="http://www.w3.org/2000/svg" id="release-canvas" width="720" height="300" viewBox="0 0 720 300" data-title="Release routing">
  <defs>
    <marker id="gold-head" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="#946200"/></marker>
    <marker id="blue-head" markerWidth="10" markerHeight="6" refX="10" refY="3" orient="auto"><polygon points="0,0 10,3 0,6" fill="#264E8A"/></marker>
  </defs>
  <g id="intake-card" data-node-id="incoming"><rect x="30" y="30" width="120" height="60" fill="#FFF3D4" stroke="#5F4B20" stroke-width="2"/><text x="42" y="65" font-family="Arial" font-size="14" fill="#332A18">Receive batch</text></g>
  <g id="screen-card" data-node-id="qa"><circle cx="360" cy="180" r="45" fill="#E4F2E8" stroke="#24513A" stroke-width="2"/><text x="329" y="185" font-family="Arial" font-size="14" font-weight="bold" fill="#153A27">QA gate</text></g>
  <g id="release-card" data-node-id="outgoing"><rect x="540" y="30" width="120" height="60" rx="6" fill="#EAF0FC" stroke="#264E8A" stroke-width="2"/><text x="555" y="65" font-family="Arial" font-size="14" fill="#1B355E">Release &lt;R7&gt;</text></g>
  <polyline id="screen-route" data-edge-id="screen-flow" data-source="incoming" data-target="qa" points="150,60 225,60 225,180 315,180" fill="none" stroke="#946200" stroke-width="2" marker-end="url(#gold-head)"/>
  <text id="screen-caption" data-edge-id="screen-flow" x="235" y="120" font-family="Arial" font-size="12" fill="#6B4800">screened</text>
  <polyline id="release-route" data-edge-id="release-flow" data-source="qa" data-target="outgoing" points="405,180 480,180 480,60 540,60" fill="none" stroke="#264E8A" stroke-width="3" stroke-dasharray="5 3" marker-end="url(#blue-head)"/>
  <text id="release-caption" data-edge-id="release-flow" x="488" y="120" font-family="Arial" font-size="12" font-style="italic" fill="#1B355E">approved &amp; queued</text>
</svg>
```
