#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Repair reviewed Mermaid gallery chrome without touching selectors or labels."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'skills/mermaid/scripts'))
from palette_paints import svg_paints
path=ROOT / 'skills/mermaid/assets/examples/mermaid-max-complexity/gallery.css'
root=ET.Element('svg')
style=ET.SubElement(root,'style')
style.text=path.read_text(encoding='utf-8')
changes=svg_paints(root,'colorset1',normalize=True)
if changes: path.write_text(style.text,encoding='utf-8',newline='\n')
print('Gallery base paint remaps:',len(changes))
