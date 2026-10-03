#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from pathlib import Path
import json
import shutil
import re
ROOT=Path(__file__).resolve().parents[3]
for mode in [1,2]:
    source=ROOT/f'projects/diagram-solid-style/artifacts/plantuml-cs{mode}'
    gallery=ROOT/'skills/plantuml-colorset-renderer/assets/examples'/('plantuml-colorset-renderer-cs1' if mode==1 else 'plantuml-colorset-renderer')
    report=json.loads((source/'report.json').read_text(encoding='utf-8'))
    report['theme']=f'assets/themes/cs{mode}.puml'
    report['coverageManifest']='references/diagram-types.json'
    for item in report['results']:
        for output in item['outputs']:
            src=source/output['path'];dest=gallery/output['path']
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dest)
    (gallery/'render-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
for file in [ROOT/'skills/mermaid/assets/examples/mermaid-max-complexity/gallery.css',ROOT/'skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/plantuml-gallery.css']:
    t=file.read_text(encoding='utf-8')
    t=re.sub(r'border(?:-(?:top|bottom|left|right))?:\s*[^;]+;', 'border: 0;',t)
    t=t.replace('var(--#e8002a)','var(--red)')
    file.write_text(t,encoding='utf-8')
p=ROOT/'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs'
t=p.read_text(encoding='utf-8')
t=t.replace('border: 1px solid var(--brand-gray-20);','border: 0;').replace('border-bottom: 1px solid var(--brand-gray-10);','border-bottom: 0;')
t=t.replace('background: #fff;\n  color: var(--brand-neutral);','background: var(--brand-primary);\n  color: #ffffff;')
t=t.replace('button:hover { border-color: var(--brand-link); background: var(--brand-highlight-blue); color: var(--brand-link-hover); }','button:hover { background: #6d1222; color: #ffffff; }')
p.write_text(t,encoding='utf-8')
print('Copied 56 PlantUML published output assets and updated borderless gallery chrome.')
