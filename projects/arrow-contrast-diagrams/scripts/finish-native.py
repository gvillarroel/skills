#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate native arrow finishing and matching published fixture metadata."""
import hashlib
import importlib.util
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/mermaid/scripts'))
from arrow_contrast import finish_native_arrows
gallery=ROOT/'skills/mermaid/assets/examples/mermaid-max-complexity'
def save_bytes(file, data):
    if file.exists() and file.read_bytes() == data: return
    temporary=file.with_name(file.name+'.arrow-tmp')
    temporary.write_bytes(data)
    for attempt in range(30):
        try:
            temporary.replace(file)
            return
        except OSError:
            if attempt == 29: raise
            time.sleep(.1)
def save_svg(file, root):
    save_bytes(file,ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n')
for cs in ['colorset1','colorset2']:
    for file in (gallery/'svg'/cs).glob('*.svg'):
        tree=ET.parse(file)
        finish_native_arrows(tree.getroot(),cs)
        save_svg(file,tree.getroot())
manifest=json.loads((gallery/'gallery.json').read_text())
for item in manifest['patterns']:
    item['sourceSha256']=hashlib.sha256((gallery/item['source']).read_bytes()).hexdigest()
    for path,hashkey in [('staticSvg','staticSha256'),('animatedSvg','animatedSha256')]:
        item[hashkey]=hashlib.sha256((gallery/item[path]).read_bytes()).hexdigest()
save_bytes(gallery/'gallery.json',(json.dumps(manifest,indent=2)+'\n').encode())
report_path=gallery/'reports/build-report.json'
report=json.loads(report_path.read_text());report['manifestSha256']=hashlib.sha256((gallery/'gallery.json').read_bytes()).hexdigest()
manifest_hash=report['manifestSha256']
save_bytes(report_path,(json.dumps(report,indent=2)+'\n').encode())
for folder,cs in [('plantuml-colorset-renderer','colorset2'),('plantuml-colorset-renderer-cs1','colorset1')]:
    base=ROOT/'skills/plantuml-colorset-renderer/assets/examples'/folder
    for file in (base/'svg').glob('*.svg'):
        tree=ET.parse(file);finish_native_arrows(tree.getroot(),cs,'plantuml')
        save_svg(file,tree.getroot())
    report_path=base/'render-report.json';report=json.loads(report_path.read_text())
    for result in report.get('results',[]):
        for output in result.get('outputs',[]):
            file=base/output['path']
            if file.exists():output['size_bytes']=file.stat().st_size
    save_bytes(report_path,(json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({'mermaidSvgs':124,'plantumlSvgs':54,'manifestSha256':manifest_hash}))
