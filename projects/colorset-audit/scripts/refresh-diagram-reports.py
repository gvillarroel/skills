#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh artifact hashes/sizes after the reviewed palette-only normalization."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
gallery=ROOT / 'skills/mermaid/assets/examples/mermaid-max-complexity'
path=gallery / 'gallery.json'
data=json.loads(path.read_text())
for item in data['patterns']:
    for artifact, field in [('staticSvg','staticSha256'),('animatedSvg','animatedSha256')]:
        item[field]=hashlib.sha256((gallery / item[artifact]).read_bytes()).hexdigest()
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
for folder in ('plantuml-colorset-renderer','plantuml-colorset-renderer-cs1'):
    base=ROOT / 'skills/plantuml-colorset-renderer/assets/examples' / folder
    report=base / 'render-report.json'
    data=json.loads(report.read_text())
    for item in data['results']:
        for output in item['outputs']:
            output['size_bytes']=(base / output['path']).stat().st_size
            output['palette_normalized']=True
            output['source_media_preserved']=False
    report.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Refreshed 62 Mermaid pairs and two PlantUML artifact reports.')
