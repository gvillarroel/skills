#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0"]
# ///
"""Bundle standard CSS name input decoding; these are not authored output colors."""
import json
from pathlib import Path
from PIL import ImageColor
ROOT=Path(__file__).resolve().parents[3]
data={key:value.lower() for key,value in sorted(ImageColor.colormap.items())}
for name in ('mermaid','plantuml-colorset-renderer','echarts-animated-svg'):
    folder=ROOT / 'skills' / name
    (folder / 'assets/palettes/css-named-colors.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    path=folder / 'scripts/palette_paints.py'
    text=path.read_text(encoding='utf-8-sig')
    start=text.index('NAMES = ')
    end=text.index('\n',start)
    text=text[:start]+'''NAMES = json.loads((Path(__file__).resolve().parent.parent / "assets/palettes/css-named-colors.json").read_text(encoding="utf-8"))
TOKEN = re.compile(r"#[0-9a-fA-F]{3,8}\\b|(?:rgba?|hsla?)\\([^)]*\\)|\\b(?:" + "|".join(NAMES) + r")\\b", re.I)'''+text[end:]
    path.write_text(text,encoding='utf-8',newline='\n')
print('Bundled standard CSS name decoding in three paint gates.')
