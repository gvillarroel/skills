You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, access the network, or modify bundled
assets.

Use the bundled manifest entry `hilma-primordial-chaos-16` to create one
simplified, editable organic pattern in both bundled palette contracts. Preserve
the source's biomorphic spirals and asymmetric color rhythm; do not replace them
with generic geometric primitives. Use a maximum source dimension of 420 pixels,
no tiling, and these stable pattern IDs:

- `hilma-colorset-contract-cs1` with `colorset1`
- `hilma-colorset-contract-cs2` with `colorset2`

Create exactly these nonempty workspace-relative files:

- `outputs/colorset-pair/base-assets-validation.json`
- `outputs/colorset-pair/hilma-colorset-contract-cs1.svg`
- `outputs/colorset-pair/hilma-colorset-contract-cs1.json`
- `outputs/colorset-pair/hilma-colorset-contract-cs1-validation.json`
- `outputs/colorset-pair/hilma-colorset-contract-cs2.svg`
- `outputs/colorset-pair/hilma-colorset-contract-cs2.json`
- `outputs/colorset-pair/hilma-colorset-contract-cs2-validation.json`

Validate the bundled image manifest before vectorizing. Validate each final SVG
against its sidecar report, exact pattern ID, `organic` mode, `none` tile mode,
expected colorset, at least three editable paths, and no SVG pattern element.
Both outputs must use the same vectorization settings so their ordered path data
and view box remain identical; only palette values and colorset metadata may
differ. Each SVG must contain no raster `<image>`, script, `foreignObject`,
external reference, or visible color outside its selected bundled palette.
Finish only after every required file exists at the exact path.
