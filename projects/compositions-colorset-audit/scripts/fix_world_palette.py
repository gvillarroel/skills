#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep world grouping accents and generated CSS within the active finite set."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
path=ROOT/'skills/compose-synchronized-svg/scripts/scaffold_synchronized_svg.py'
text=path.read_text(encoding='utf-8')
text=re.sub(r'color-mix\(in srgb, var\(--district-accent\) \d+%, var\(--(?:ink|line)\)\)', 'var(--district-accent)',text)
text=text.replace('color-mix(in srgb, var(--accent) 24%, var(--surface))','var(--accent-soft)')
path.write_text(text,encoding='utf-8')
path=ROOT/'skills/compose-synchronized-svg/scripts/compile_synchronized_svg_plan.py'
text=path.read_text(encoding='utf-8')
text=re.sub(r'WORLD_DISTRICT_PALETTE = \[[\s\S]*?\]', 'WORLD_DISTRICT_PALETTE = ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#696969", "#4f4f4f", "#363636"]',text,count=1)
path.write_text(text,encoding='utf-8')
path=ROOT/'skills/compose-synchronized-svg/references/color-and-visual-quality.md';text=path.read_text(encoding='utf-8').replace('Generated tint tokens are opaque, contrast-checked mixes of those roles. Their strength can decrease to preserve the supplied text colors.', 'Generated tint tokens are opaque, contrast-checked discrete palette tokens chosen near the requested mix. Their strength can decrease to preserve the supplied text colors.').replace('"demand": "#4f4f4f",\n      "capacity": "#4f4f4f"','"demand": "#9e1b32",\n      "capacity": "#007298"');path.write_text(text,encoding='utf-8')
print('World accents and opaque CSS mixtures repaired.')
