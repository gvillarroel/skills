#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep the standalone chart templates' CSS input decoding complete."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
names=json.loads((ROOT / 'skills/echarts-animated-svg/assets/palettes/css-named-colors.json').read_text())
for name in ('echarts-animated-svg','slidev-echarts'):
    path=ROOT / 'skills' / name / 'assets/templates/echarts-colorsets.mjs'
    text=path.read_text(encoding='utf-8-sig')
    text=re.sub(r'  const named=\{[^\n]+\}', '  const named='+json.dumps(names,separators=(',',':')),text)
    path.write_text(text,encoding='utf-8',newline='\n')
print('Complete CSS named input decoder added to both self-contained templates.')
