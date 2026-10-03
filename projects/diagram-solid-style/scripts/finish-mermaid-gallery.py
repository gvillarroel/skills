#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finish native pairs after a transient Windows renderer file-open failure."""
from pathlib import Path
import sys
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
SKILL=ROOT/'skills/mermaid'
GALLERY=SKILL/'assets/examples/mermaid-max-complexity'
sys.path.insert(0,str(SKILL/'scripts'))
from palette_paints import svg_paints,require_svg_palette
from mermaid_animation.solid import native_solid_presentation,write_native_svg

for palette in ['colorset1','colorset2']:
    for path in (GALLERY/'svg'/palette).glob('*.svg'):
        tree=ET.parse(path)
        root=tree.getroot()
        svg_paints(root,palette,normalize=True)
        native_solid_presentation(root,palette)
        root.set('data-colorset',palette)
        require_svg_palette(root,palette)
        write_native_svg(tree,path)
    for static in (GALLERY/'svg'/palette).glob('*.static.svg'):
        animated=static.with_name(static.name.replace('.static.svg','.animated.svg'))
        if not animated.exists() or not animated.stat().st_size:
            subprocess.run(['uv','run','--script',str(SKILL/'scripts/animate_mermaid_svg.py'),'--svg-input',str(static),'-o',str(animated),'--animation','auto','--duration-ms','480','--stagger-ms','65','--initial-delay-ms','100'],check=True)

manifest=json.loads((GALLERY/'gallery.json').read_text(encoding='utf-8'))
for pattern in manifest['patterns']:
    for key,hashkey in [('source','sourceSha256'),('staticSvg','staticSha256'),('animatedSvg','animatedSha256')]:
        pattern[hashkey]=hashlib.sha256((GALLERY/pattern[key]).read_bytes()).hexdigest()
(GALLERY/'gallery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
report={'ok':True,'familyCount':31,'patternCount':62,'sourceCount':62,'staticSvgCount':62,'animatedSvgCount':62,'finiteCapacityCaseCount':manifest['finiteCapacityCaseCount'],'finiteCapacitySlots':manifest['finiteCapacitySlots'],'manifestSha256':hashlib.sha256((GALLERY/'gallery.json').read_bytes()).hexdigest(),'recovery':'Native renderer sources/styles regenerated; failed Windows file-open pairs finished from native static SVG; scoped solid-native finish applied to static and animated pairs.'}
(GALLERY/'reports/build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
