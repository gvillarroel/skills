#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find contradictory legacy categorical tier prose in runtime skill resources."""
from pathlib import Path
import json
import os
import re

ROOT = Path(__file__).resolve().parents[3]
patterns = [re.compile(r'grays?\s*[,→]\s*black', re.I), re.compile(r'grays?\s*,?\s+then\s+black', re.I)]
rows = []
for current, directories, files in os.walk(ROOT / 'skills'):
    directories[:] = [d for d in directories if d not in {'node_modules','examples','__pycache__','dist','.git'}]
    for name in files:
        path = Path(current) / name
        if path.suffix.lower() not in {'.md','.py','.js','.mjs','.ts','.puml'}:
            continue
        text = path.read_text(encoding='utf-8',errors='replace')
        for pattern in patterns:
            for match in pattern.finditer(text):
                rows.append({'path':path.relative_to(ROOT).as_posix(),'line':text.count('\n',0,match.start())+1,
                             'context':text[max(0,match.start()-80):match.end()+100]})
out = ROOT / 'projects/grayscale-interleave/artifacts/manifests/legacy-prose.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))
