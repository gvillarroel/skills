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

This is a deterministic command-contract smoke. After reading the skill, run
the following command block exactly from the isolated workspace root. Do not
add exploratory directory probes or substitute filenames.

```bash
mkdir -p outputs/contract
uv run --script skills/vectorize-art-patterns/scripts/validate_open_assets.py skills/vectorize-art-patterns/assets/base-images/manifest.json --output-report outputs/contract/base-assets-validation.json
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py skills/vectorize-art-patterns/assets/base-images/hilma-primordial-chaos-16.jpg outputs/contract/hilma-organic-mirror.svg --mode organic --max-dimension 480 --tile mirror --pattern-id hilma-organic-mirror-contract --variation-seed 16016 --source-manifest skills/vectorize-art-patterns/assets/base-images/manifest.json --source-id hilma-primordial-chaos-16 --report outputs/contract/hilma-organic-mirror.json
uv run --script skills/vectorize-art-patterns/scripts/validate_art_svg.py outputs/contract/hilma-organic-mirror.svg --report outputs/contract/hilma-organic-mirror.json --expected-pattern-id hilma-organic-mirror-contract --expected-mode organic --expected-tile mirror --require-pattern --min-paths 3 --output-report outputs/contract/hilma-organic-mirror-validation.json
test -s outputs/contract/base-assets-validation.json && test -s outputs/contract/hilma-organic-mirror.svg && test -s outputs/contract/hilma-organic-mirror.json && test -s outputs/contract/hilma-organic-mirror-validation.json
```
