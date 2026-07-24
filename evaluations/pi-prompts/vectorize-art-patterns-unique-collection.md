You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, access the network, or modify bundled
assets.

Use the bundled public-domain source `hilma-primordial-chaos-16` to create six
independent, editable, non-tiled organic SVG patterns. They must preserve
biomorphic, asymmetric movement and must not introduce generic geometric shape
kits. Use these exact IDs, colorsets, and variation seeds:

| Pattern ID | Colorset | Variation seed |
| --- | --- | ---: |
| `chaos-current-01-cs1` | `colorset1` | 61001 |
| `chaos-current-02-cs2` | `colorset2` | 61002 |
| `chaos-current-03-cs1` | `colorset1` | 61003 |
| `chaos-current-04-cs2` | `colorset2` | 61004 |
| `chaos-current-05-cs1` | `colorset1` | 61005 |
| `chaos-current-06-cs2` | `colorset2` | 61006 |

Vary crop scale and position, rotation, flow strength, flow frequency, and at
least two tracing controls across the six members. Keep every crop scale
between 0.60 and 0.86, rotation between -18 and 18 degrees, flow strength
between 4 and 14, and flow frequency between 1.4 and 3.4. Use a maximum source
dimension no greater than 360 pixels.

Create exactly these nonempty workspace-relative files:

- `outputs/unique-collection/base-assets-validation.json`
- `outputs/unique-collection/chaos-current-01-cs1.svg`
- `outputs/unique-collection/chaos-current-01-cs1.json`
- `outputs/unique-collection/chaos-current-01-cs1-validation.json`
- `outputs/unique-collection/chaos-current-02-cs2.svg`
- `outputs/unique-collection/chaos-current-02-cs2.json`
- `outputs/unique-collection/chaos-current-02-cs2-validation.json`
- `outputs/unique-collection/chaos-current-03-cs1.svg`
- `outputs/unique-collection/chaos-current-03-cs1.json`
- `outputs/unique-collection/chaos-current-03-cs1-validation.json`
- `outputs/unique-collection/chaos-current-04-cs2.svg`
- `outputs/unique-collection/chaos-current-04-cs2.json`
- `outputs/unique-collection/chaos-current-04-cs2-validation.json`
- `outputs/unique-collection/chaos-current-05-cs1.svg`
- `outputs/unique-collection/chaos-current-05-cs1.json`
- `outputs/unique-collection/chaos-current-05-cs1-validation.json`
- `outputs/unique-collection/chaos-current-06-cs2.svg`
- `outputs/unique-collection/chaos-current-06-cs2.json`
- `outputs/unique-collection/chaos-current-06-cs2-validation.json`
- `outputs/unique-collection/collection-manifest.json`

Validate the bundled base-image manifest first. Validate every SVG against its
sidecar report, exact ID, `organic` mode, `none` tile mode, expected colorset,
and expected variation seed. Every SVG must contain editable path data and no
`pattern`, `use`, raster `image`, script, `foreignObject`, or external
reference.

Write `collection-manifest.json` with the six IDs, source hash, colorset,
variation seed, composition SHA-256, complete-geometry SHA-256, and every
normalized path-data SHA-256. Include aggregate counts. Fail instead of
finishing if any composition, complete geometry, or individual path signature
is reused. A colorset change alone does not count as a unique member.
