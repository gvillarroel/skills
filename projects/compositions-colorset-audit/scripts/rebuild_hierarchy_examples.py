#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh all published hierarchy views while preserving their navigation chrome."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/hierarchy-lens/scripts'))
from build_explorer import build
directory=ROOT/'skills/hierarchy-lens/assets/examples/hierarchy-lens'
source=json.loads((directory/'organization.json').read_text(encoding='utf-8'))
for file,view in [('analytical.html','analytical'),('radial.html','pixel'),('organic.html','organic'),('index.html','decision')]:
    destination=directory/file
    old=destination.read_text(encoding='utf-8')
    # Keep the published example-set metadata and authored view navigation.
    lines=[line for line in old.splitlines() if 'meta name="example-' in line]
    if view=='decision':source['composition']=json.loads((directory/'composition.json').read_text())
    result=build(source,destination,view=view)
    text=destination.read_text(encoding='utf-8').replace('%2379b8be','%239e1b32').replace('%2379b8be','%239e1b32')
    if lines:text=text.replace('</head>','\n'.join(lines)+'\n</head>')
    links='<nav data-gallery-navigation="true" aria-label="Compare hierarchy views">'+''.join(f'<p><a style="color:#9e1b32" href="{target}#{pattern}">{label}</a></p>' for target,pattern,label in [('index.html','hierarchy-decision-growth','Decision growth'),('organic.html','hierarchy-organic-pixels','Organic pixels'),('radial.html','hierarchy-radial-pixels','Radial pixels'),('analytical.html','hierarchy-radial-lenses','Analytical hierarchy')] if target!=file)+'</nav>'
    text=text.replace('</aside>',links+'</aside>') if view!='analytical' else text.replace('</footer>',links+'</footer>')
    destination.write_text(text,encoding='utf-8')
    print(json.dumps(result))
