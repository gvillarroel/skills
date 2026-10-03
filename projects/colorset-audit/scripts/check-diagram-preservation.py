#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare published diagram geometry, identities, and labels with the Git baseline."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'skills/mermaid/scripts'))
from palette_paints import PAINT_KEYS
def facts(node):
    tag=node.tag.rsplit('}',1)[-1]
    attrs={key:value for key,value in node.attrib.items() if key not in PAINT_KEYS | {'style','data-colorset','data-palette-normalization'}}
    # Inline style contains paint overrides; geometry lives in dedicated SVG attributes in these fixtures.
    return [tag,attrs,'' if tag=='style' else (node.text or '').strip(),[facts(child) for child in node]]
checked=[]
for skill in ['mermaid','plantuml-colorset-renderer']:
    for path in (ROOT / 'skills' / skill / 'assets/examples').rglob('*.svg'):
        if 'node_modules' in path.parts: continue
        relative=path.relative_to(ROOT).as_posix()
        result=subprocess.run(['git','show','HEAD:'+relative],cwd=ROOT,capture_output=True)
        if result.returncode: continue
        assert facts(ET.fromstring(result.stdout))==facts(ET.parse(path).getroot()),relative
        checked.append(relative)
output=ROOT / 'projects/colorset-audit/artifacts/reviews/diagram-preservation.json'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'ok':True,'checkedSvgCount':len(checked),'scope':'SVG geometry attributes, hierarchy, IDs, text and source image references; paint, inline style and added palette metadata excluded','paths':checked},indent=2)+'\n',encoding='utf-8')
print(f'{len(checked)} SVG artifacts retain geometry attributes, identities, labels, hierarchy, and source image references.')
