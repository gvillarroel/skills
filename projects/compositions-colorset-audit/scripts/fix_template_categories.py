#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep independent poster categories distinct after finite-token migration."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sequence=['#9e1b32','#007298','#e77204','#45842a','#652f6c','#f1c319','#004d66','#9e00b3']
for path in (ROOT/'skills/usefulcharts-style/assets/templates').glob('*.json'):
    data=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data,dict) and data.get('groups'):
        for i,group in enumerate(data['groups']):group['color']=sequence[i]
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
path=ROOT/'skills/compose-synchronized-svg/references/color-and-visual-quality.md';text=path.read_text(encoding='utf-8')
text=text.replace('Newly compiled briefs default to `editorial`, a quiet neutral surface with dark qualitative marks. `classic` retains the earlier saturated concept sequence with contrast-checked interface colors. Existing full plans without a theme keep the classic concept sequence.', 'Newly compiled briefs default to `editorial`, the colorset1 red/neutral alias. `classic` is the colorset2 alias. The explicit `colorset1` and `colorset2` preset names are also supported. Existing full plans without a theme resolve to colorset2. All resolved and derived paints stay inside the selected finite palette.')
text=text.replace('"preset": "editorial"','"preset": "colorset2"')
text=text.replace('duplicate concept colors, and insufficient contrast','off-palette colors and insufficient contrast')
text=text.replace('Different concepts need distinct physical colors.', 'Keep different concepts independently labeled. The finite token sequence repeats when its contrast-safe colors are exhausted; use shapes, dash styles and direct labels to preserve identity. A repeated paint does not imply a shared token owner.')
text=text.replace('A palette with 24 unique hex values does not prove that 24 categories are perceptually distinguishable.', 'A finite palette cannot provide arbitrarily many unique colors, and palette membership does not prove that all categories are perceptually distinguishable.')
path.write_text(text,encoding='utf-8')
print('Poster template categories and synchronized-theme instructions repaired.')
