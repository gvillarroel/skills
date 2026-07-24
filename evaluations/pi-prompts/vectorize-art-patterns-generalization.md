You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, or access the network.

Create a small original raster fixture at
`inputs/biomorphic-source.ppm`. It represents artwork owned by the requester:
use a warm paper background, one broad irregular blue-green wave, overlapping
rust and ochre organic masses, and several thin undulating dark marks. The
silhouettes must be visibly asymmetrical and hand-shaped rather than circles,
rectangles, polygons, or a regular geometric grid.

Turn that fixture into a simplified standalone SVG using the `organic` mode,
no tiling, a maximum dimension of 320 pixels, the rights basis `user-owned`,
and the stable pattern ID `biomorphic-user-owned`. Preserve the flowing visual
rhythm while reducing the raster to a small number of editable color masses.

Create exactly these nonempty workspace-relative files:

- `inputs/biomorphic-source.ppm`
- `outputs/generalization/biomorphic-user-owned.svg`
- `outputs/generalization/biomorphic-user-owned.json`
- `outputs/generalization/biomorphic-user-owned-validation.json`

Validate the SVG against its report, expected ID, `organic` mode, and `none`
tile mode, requiring at least three editable paths. It must contain no embedded
raster, script, `foreignObject`, or external reference. Finish only after every
required file exists at the exact path.
