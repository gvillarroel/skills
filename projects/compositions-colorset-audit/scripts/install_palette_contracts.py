#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install identical, self-contained finite palette helpers in owned bundles."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = '''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finite authored-paint contract; imported source media stays producer-owned."""
import json
from pathlib import Path

COLORSETS = json.loads((Path(__file__).resolve().parent.parent / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]

def require_color(value, colorset="colorset2"):
    if not isinstance(value, str) or value.lower() not in COLORSETS[colorset]["allowed"]:
        raise ValueError(f"Authored color {value!r} must be an exact {colorset} token")
    return value.lower()

def nearest_color(value, colorset="colorset2"):
    """Snap an intentional generated tint to the selected finite token set."""
    channels = [int(value[i:i + 2], 16) for i in (1, 3, 5)]
    return min(COLORSETS[colorset]["allowed"], key=lambda c: sum((x - int(c[i:i + 2], 16)) ** 2 for x, i in zip(channels, (1, 3, 5))))
'''
for name in ['compose-synchronized-svg', 'diagram-composition', 'usefulcharts-style', 'manim-svg-video', 'video']:
    (ROOT / 'skills' / name / 'scripts/palette_contract.py').write_text(CONTENT, encoding='utf-8')
print('Installed five self-contained palette helpers.')
