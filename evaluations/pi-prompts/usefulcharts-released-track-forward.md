Create a layout for a synthetic museum fleet using the installed poster skill's
measured calendar helper. The x positions are already measured; do not change
any of them or any identity. Return `deliverables/layout.json` and a concise
`deliverables/review.md`. Write all working and output files inside this workspace.

Reuse a terminated branch's horizontal space for a different family while its
long-running sibling continues. Do not reserve the whole first family's
rectangle. Each measured footprint already contains its local family label,
artwork and clearance; there are no separate group headings. Preserve family and
physical-owner identities. Only assign y coordinates; no drawing is requested.

Use this measured input, adding the helper's appropriate layout options:

```json
{
  "mode": "numeric", "width": 1200, "top": 40,
  "gap": 12, "track_gap": 16, "row_gap": 20,
  "groups": [
    {"id": "survey", "members": ["short", "long", "return"]},
    {"id": "freight", "members": ["beta"]},
    {"id": "science", "members": ["gamma", "delta"]}
  ],
  "records": [
    {"id": "short", "owner": "survey-hull", "x0": 60, "x1": 200, "height": 80},
    {"id": "long", "owner": "long-hull", "x0": 80, "x1": 900, "height": 70},
    {"id": "return", "owner": "survey-hull", "x0": 960, "x1": 1150, "height": 60},
    {"id": "beta", "owner": "freighter", "x0": 230, "x1": 440, "height": 90},
    {"id": "gamma", "owner": "science-one", "x0": 470, "x1": 660, "height": 80},
    {"id": "delta", "owner": "science-two", "x0": 500, "x1": 820, "height": 95}
  ]
}
```

Explain the actual handoffs and distinguish six fragments from five physical
ships. State what still needs visual review, including readable family identity
and the association between labels and exact date anchors. Do not claim parity
with a reference poster from a placement-only result.
