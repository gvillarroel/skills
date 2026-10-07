# SVG to editable approval flow

Use the read-only skill at `skills/lucidchart-svg/`. Create task files only in this isolated workspace. No browser, network, account credentials, or service upload is available.

I have this SVG approval flow. Prepare it for Lucidchart as both an unchanged SVG asset and an editable native diagram package. Keep all labels, directions, and these coordinates. Use plain native boxes and a decision diamond. Write exact outputs: `out/upload.svg`, `out/inspection.json`, `out/graph.json`, `out/approval.lucid`, `out/document.json`, and `out/mapping.md`. Explain actual delivery, editability, and any changes in the mapping note. A local package is useful even though no authenticated import can be made here.

Create `input/approval.svg` from these exact SVG bytes (a trailing newline is allowed):

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="180" viewBox="0 0 500 180"><g id="n-request" data-node-id="request"><rect x="20" y="50" width="110" height="60" fill="#ffffff" stroke="#333333"/><text x="75" y="85">Request &amp; review</text></g><g id="n-check" data-node-id="check"><polygon points="250,40 300,80 250,120 200,80" fill="#ffffff" stroke="#333333"/><text x="250" y="85">Approved?</text></g><g id="n-publish" data-node-id="publish"><rect x="370" y="50" width="110" height="60" fill="#ffffff" stroke="#333333"/><text x="425" y="85">Publish</text></g><path id="e-review" data-source="request" data-target="check" d="M130 80 L200 80"/><path id="e-yes" data-source="check" data-target="publish" d="M300 80 L370 80"/><text data-edge-id="e-yes" x="330" y="70">yes</text></svg>
```
