#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replace unbounded authored color generation with finite palette contracts."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
path = ROOT / 'skills/compose-synchronized-svg/scripts/theme_contract.py'
text = path.read_text(encoding='utf-8')
text = text.replace('import colorsys\n', '').replace('from typing import Mapping, Sequence', 'from typing import Mapping, Sequence\nfrom palette_contract import nearest_color, require_color')
start, end = text.index('_PRESETS ='), text.index('\n\ndef contrast_ratio')
text = text[:start] + '''_PRESETS = {"colorset1", "colorset2", "editorial", "classic"}
_EDITORIAL = {"canvas": "#f7f7f7", "surface": "#ffffff", "ink": "#333e48", "muted": "#696969", "line": "#cfcfcf", "accent": "#9e1b32", "focus": "#6d1222", "warning": "#4f4f4f", "danger": "#9e1b32"}
_CLASSIC = {**_EDITORIAL, "accent": "#007298", "focus": "#004d66", "warning": "#994a00"}
PALETTE = ["#9e1b32", "#007298", "#994a00", "#45842a", "#652f6c", "#98700c", "#333e48", "#004d66", "#6d1222", "#294d19", "#431f47", "#9e00b3", "#e8002a", "#828282", "#696969", "#4f4f4f", "#363636", "#1c1c1c", "#000000"]
RED_NEUTRAL = ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#696969", "#4f4f4f", "#363636", "#1c1c1c", "#000000"]

def color_for_index(index: int) -> str:
    if index < 0:
        raise ValueError("theme validation failure: color index must be nonnegative")
    return PALETTE[index % len(PALETTE)]
''' + text[end:]
text = text.replace('def safe_surface_tint(colors: Mapping[str, str], tint: str, amount: float)', 'def safe_surface_tint(colors: Mapping[str, str], tint: str, amount: float, colorset: str = "colorset2")')
text = text.replace('background = mix_color(tint, colors["surface"], amount * (1 - step / 100))', 'background = nearest_color(mix_color(tint, colors["surface"], amount * (1 - step / 100)), colorset)')
text = text.replace('colors = theme["colors"]\n', 'colors = theme["colors"]\n    colorset = "colorset1" if theme["preset"] in {"editorial", "colorset1"} else "colorset2"\n')
text = re.sub(r'safe_surface_tint\(colors, ([^\n]+?), (0\.\d+)\)', r'safe_surface_tint(colors, \1, \2, colorset)', text)
text = text.replace('secondary = mix_color(colors["ink"], inverse, 0.22)', 'secondary = nearest_color(mix_color(colors["ink"], inverse, 0.22), colorset)')
start, end = text.index('def _editorial_token'), text.index('\n\ndef resolve_theme')
text = text[:start] + 'def _editorial_token(index: int) -> str:\n    return RED_NEUTRAL[index % len(RED_NEUTRAL)]\n' + text[end:]
text = text.replace('colors = dict(_EDITORIAL if preset == "editorial" else _CLASSIC)', 'colorset = "colorset1" if preset in {"editorial", "colorset1"} else "colorset2"\n    colors = dict(_EDITORIAL if colorset == "colorset1" else _CLASSIC)')
text = text.replace('colors[role] = _color(value, f"colors.{role}")', 'colors[role] = _color(value, f"colors.{role}")\n        require_color(colors[role], colorset)')
text = text.replace('color_for_index(value_ids.index(root)) if preset == "classic"', 'color_for_index(index) if colorset == "colorset2"')
text = text.replace('if len(set(concepts.values())) != len(concepts):\n        _fail("every distinct token must resolve to a distinct physical color")', '    require_color(concepts[root], colorset)\n    if len(set(supplied_concepts.values())) != len(supplied_concepts):\n        _fail("explicit overrides must resolve to a distinct physical color")')
path.write_text(text, encoding='utf-8')

path = ROOT / 'skills/hierarchy-lens/assets/templates/pixels.html'
text = path.read_text(encoding='utf-8')
text = re.sub(r"const categorical=.*?;\n", "const categorical=['#9e1b32','#007298','#e77204','#45842a','#652f6c','#f1c319','#004d66','#9e00b3'],thermal=['#1c1c1c','#6d1222','#9e1b32','#e8002a','#e77204','#ff9633','#ffd332','#fff4cc'],background='#f7f7f7',missing=['#828282','#cfcfcf'];\n", text, count=1)
text = text.replace('if(!record.active)c=c.map((v,j)=>Math.round(bg[j]+(v-bg[j])*.2));', "if(!record.active)c=rgb('#e7e7e7');")
text = text.replace('color-scheme:dark', 'color-scheme:light').replace('--bg:#1c1c1c', '--bg:#f7f7f7').replace('--ink:#e7e7e7', '--ink:#333e48').replace('--accent:#cfcfcf', '--accent:#9e1b32')
text = text.replace('background:#1c1c1cf7', 'background:#ffffff').replace('background:#1c1c1c;', 'background:#ffffff;')
path.write_text(text, encoding='utf-8')

path = ROOT / 'skills/hierarchy-lens/assets/templates/explorer.html'
text = path.read_text(encoding='utf-8')
text = re.sub(r"const palette=\[.*?\];", "const palette=['#9e1b32','#007298','#e77204','#45842a','#652f6c','#f1c319','#004d66','#9e00b3'];const numericPalette=['#fff4cc','#ffd332','#ff9633','#e77204','#e8002a','#9e1b32','#6d1222'];", text)
text = re.sub(r"const a=\[227,235,247\],b=\[38,60,134\];return `rgb\(\$\{a\.map\(\(x,i\)=>Math\.round\(x\+\(b\[i\]-x\)\*t\)\)\.join\(', '\)\}\)`;", '', text)
text = re.sub(r"const a=\[227,235,247\],b=\[38,60,134\];return `rgb\(\$\{a\.map\(\(x,i\)=>Math\.round\(x\+\(b\[i\]-x\)\*t\)\)\.join\(','\)\}\)`;", "return numericPalette[Math.min(numericPalette.length-1,Math.max(0,Math.floor(t*numericPalette.length)))];", text)
text = text.replace("gradient.append(element('stop',{offset:0,'stop-color':'#e7e7e7'}),element('stop',{offset:1,'stop-color':'#004d66'}));", "numericPalette.forEach((c,i)=>{gradient.append(element('stop',{offset:i/numericPalette.length,'stop-color':c}),element('stop',{offset:(i+1)/numericPalette.length,'stop-color':c}));});")
path.write_text(text, encoding='utf-8')
print('Finite theme sequences, contrast-safe palette tints and quantized hierarchy maps installed.')
