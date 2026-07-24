You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, access the network, or modify bundled
assets.

Use the bundled manifest entry `hilma-primordial-chaos-16` to make a simplified,
editable organic mirror pattern. Preserve the source's biomorphic spirals and
color rhythm; do not replace them with generic geometric primitives. Use a
maximum source dimension of 480 pixels and the stable pattern ID
`hilma-organic-mirror-contract`.

Create exactly these nonempty workspace-relative files:

- `outputs/contract/base-assets-validation.json`
- `outputs/contract/hilma-organic-mirror.svg`
- `outputs/contract/hilma-organic-mirror.json`
- `outputs/contract/hilma-organic-mirror-validation.json`

Validate the bundled image manifest before vectorizing. Validate the final SVG
against its sidecar report, expected pattern ID, `organic` mode, `mirror` tile
mode, at least three editable paths, and a required SVG pattern element. The
SVG must contain no raster `<image>`, script, `foreignObject`, or external
reference. Finish only after every required file exists at the exact path.
