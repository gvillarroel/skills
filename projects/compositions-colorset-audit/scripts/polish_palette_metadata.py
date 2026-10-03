#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Declare active output palettes and normalize alpha-token base colors."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
for name in ['explorer.html','pixels.html']:
    path=ROOT/'skills/hierarchy-lens/assets/templates'/name;text=path.read_text(encoding='utf-8').replace('#202b3b1c','#333e481c').replace('%2379b8be','%239e1b32');path.write_text(text,encoding='utf-8')
path=ROOT/'skills/compose-synchronized-svg/scripts/scaffold_synchronized_svg.py';text=path.read_text(encoding='utf-8').replace('data-plan-version="1" data-sync-ready="false"', 'data-plan-version="1" data-colorset="{\'colorset1\' if theme[\'preset\'] in {\'colorset1\', \'editorial\'} else \'colorset2\'}" data-sync-ready="false"');path.write_text(text,encoding='utf-8')
path=ROOT/'skills/diagram-composition/scripts/compose_diagram.py';text=path.read_text(encoding='utf-8').replace('"width": str(c["width"]), "height": str(c["height"]), "role": "img",','"width": str(c["width"]), "height": str(c["height"]), "role": "img", "data-colorset": "colorset2",');path.write_text(text,encoding='utf-8')
print('Active palette metadata and alpha-token colors updated.')
