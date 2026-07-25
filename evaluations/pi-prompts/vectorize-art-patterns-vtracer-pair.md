You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, access the network, or modify bundled
assets.

Use the bundled manifest entry `hokusai-great-wave` and the bundled VTracer
backend to create one simplified, editable color trace in both palette
contracts. Preserve the wave, boats, and mountain structure. Use `collage`
mode, eight colors, a maximum source dimension of 420 pixels, no tiling, and
these stable pattern IDs:

- `hokusai-vtracer-contract-cs1` with `colorset1`
- `hokusai-vtracer-contract-cs2` with `colorset2`

Create exactly these nonempty workspace-relative files:

- `outputs/vtracer-pair/base-assets-validation.json`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs1.svg`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs1.json`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs1-validation.json`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs2.svg`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs2.json`
- `outputs/vtracer-pair/hokusai-vtracer-contract-cs2-validation.json`

Validate the bundled image manifest before vectorizing. Validate each final SVG
against its sidecar report, exact pattern ID, `collage` mode, `none` tile mode,
expected colorset, at least three editable paths, and no SVG pattern element.
Both outputs must use identical VTracer settings so their ordered path data and
view box remain identical; only palette values and colorset metadata may differ.
Each SVG must contain no raster `<image>`, script, `foreignObject`, external
reference, or visible color outside its selected bundled palette. Finish only
after every required file exists at the exact path.
