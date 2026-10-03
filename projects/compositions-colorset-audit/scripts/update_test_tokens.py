#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retarget valid color fixtures while keeping color-failure oracles explicit."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
allowed = json.loads((ROOT / 'skills/hyperframes-explainer/assets/palettes/colorsets.json').read_text())['colorsets']['colorset2']['allowed']
manual = {'#276bc8':'#007298','#c44646':'#9e1b32','#ffff00':'#ffd332','#77bedb':'#00ace6','#a6c49b':'#45842a','#d5b171':'#f1c319','#c47876':'#9e1b32','#caa86d':'#f1c319','#d6e3cf':'#dbffcc','#eef4ed':'#f7f7f7','#e99a88':'#ff9633','#e9f0fa':'#cdf3ff','#111111':'#1c1c1c','#101010':'#1c1c1c'}
def closest(token):
    token=token.lower()
    if token in manual:return manual[token]
    rgb=[int(token[i:i+2],16) for i in (1,3,5)]
    return min(allowed,key=lambda c:sum((a-int(c[i:i+2],16))**2 for a,i in zip(rgb,(1,3,5))))
for name in ['diagram-composition','usefulcharts-style','video']:
    for path in (ROOT / 'skills' / name / 'scripts').glob('test_*.py'):
        text=path.read_text(encoding='utf-8')
        text=re.sub(r'#[0-9A-Fa-f]{6}(?![0-9A-Fa-f])',lambda m: closest(m.group()) if m.group().lower() not in allowed else m.group(),text)
        if name=='diagram-composition':
            text=text.replace('rgb(39, 107, 200)','rgb(0, 114, 152)')
            text=text.replace('spec["concepts"][0]["color"] = "#b5b5b5"','spec["concepts"][0]["color"] = "#007298"').replace('{"system":"#b5b5b5"}','{"system":"#007298"}')
        path.write_text(text,encoding='utf-8')
print('Updated valid diagram, poster and video test fixtures to the finite palette.')
