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

The isolated environment does not provide Pillow. Use this evaluator-supplied,
standard-library-only setup block exactly to create the input fixture; the
generalization being evaluated is the subsequent vectorization, not dependency
discovery or raster authoring:

```bash
python - <<'PY'
from pathlib import Path
import math

width, height = 240, 180
paper = (236, 215, 179)
masses = (
    (66, 72, 54, 38, (177, 77, 43), 0.88),
    (116, 109, 67, 46, (205, 137, 55), 0.82),
    (174, 67, 48, 55, (161, 70, 42), 0.78),
    (190, 131, 58, 34, (218, 155, 67), 0.72),
)

def mix(base, paint, amount):
    return tuple(round(a * (1 - amount) + b * amount) for a, b in zip(base, paint))

rows = []
for y in range(height):
    row = []
    for x in range(width):
        grain = ((x * 17 + y * 29 + (x * y) % 13) % 9) - 4
        color = tuple(max(0, min(255, channel + grain)) for channel in paper)
        wave_y = 91 + 25 * math.sin(x / 27) + 9 * math.sin(x / 8.5 + 0.7)
        wave_half_width = 19 + 5 * math.sin(x / 19 + 1.1)
        distance = abs(y - wave_y)
        if distance < wave_half_width:
            color = mix(color, (38, 115, 111), 0.88 * (1 - distance / wave_half_width))
        for cx, cy, rx, ry, paint, strength in masses:
            wobble_x = cx + 8 * math.sin(y / 17 + cx)
            wobble_y = cy + 7 * math.sin(x / 21 + cy)
            radius = ((x - wobble_x) / rx) ** 2 + ((y - wobble_y) / ry) ** 2
            if radius < 1:
                color = mix(color, paint, strength * (1 - radius) ** 0.45)
        for index in range(5):
            ink_y = 27 + index * 29 + 8 * math.sin(x / (10 + index * 1.7) + index)
            if abs(y - ink_y) < 1.4:
                color = mix(color, (49, 43, 39), 0.86)
        row.append(color)
    rows.append(row)

path = Path('inputs/biomorphic-source.ppm')
path.parent.mkdir(parents=True, exist_ok=True)
with path.open('w', encoding='ascii', newline='\n') as stream:
    stream.write(f'P3\n{width} {height}\n255\n')
    for row in rows:
        stream.write(' '.join(f'{r} {g} {b}' for r, g, b in row) + '\n')
print(path)
PY
```

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
