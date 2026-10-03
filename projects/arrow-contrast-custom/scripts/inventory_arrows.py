#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Inventory actual custom arrow producers and rendered palette defects."""
import importlib.util
import json
from pathlib import Path
import re
import argparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT / "projects/arrow-contrast-custom/artifacts"
EVIDENCE=ROOT / "evaluations/arrow-contrast-custom"
parser=argparse.ArgumentParser()
parser.add_argument('--phase',default='after',choices=('before','after'))
args=parser.parse_args()
for path in (OUT / "data",OUT / "screenshots",EVIDENCE):path.mkdir(parents=True,exist_ok=True)
skills=("d3","threejs-animated-3d","procedural-svg-animation","svg-brief-design","vectorize-art-patterns")
pattern=re.compile(r'marker-end|marker-start|<marker\b|ArrowHelper|ConeGeometry|def arrow\(|arrowhead|addArrowMarker')
sources=[]
for skill in skills:
    for path in (ROOT / "skills" / skill).rglob('*'):
        if not path.is_file() or path.suffix not in {'.py','.js','.svg','.html','.md'} or any(part in {'node_modules','vendor','dist'} for part in path.parts):continue
        if path.name.endswith('.min.js'):continue
        text=path.read_text(encoding='utf-8')
        matches=[{'line':index,'snippet':line.strip()[:180]} for index,line in enumerate(text.splitlines(),1) if pattern.search(line)]
        if matches:sources.append({'skill':skill,'path':path.relative_to(ROOT).as_posix(),'matches':matches})

spec=importlib.util.spec_from_file_location('scaffold',ROOT / 'skills/svg-brief-design/scripts/scaffold.py')
scaffold=importlib.util.module_from_spec(spec);spec.loader.exec_module(scaffold)
rendered=[]
with sync_playwright() as engine:
    browser=engine.chromium.launch(channel='msedge')
    page=browser.new_page(viewport={'width':1440,'height':1100})
    for gallery in ('d3-animated-svg-cs1','d3-animated-svg-colorset2'):
        path=ROOT / 'skills/d3/assets/examples' / gallery / 'index.html'
        page.goto(path.as_uri(),wait_until='domcontentloaded')
        page.wait_for_function("document.querySelectorAll('svg[data-fill-style=\"solid-first\"]').length>200")
        page.wait_for_timeout(4500)
        page.add_script_tag(path=str(Path(__file__).with_name('arrow_audit.ts')))
        arrows=page.evaluate('window.auditRenderedArrows()')
        page.evaluate(Path(__file__).with_name('glyph_audit.ts').read_text(encoding='utf-8'))
        glyphs=page.evaluate('window.auditDirectionalGlyphs()')
        for item in ('state-machine','flowchart-dag','sequence-lifelines','process-control-loop','bowtie-barriers','vector-field'):
            card=page.locator(f'[data-example="{item}"]')
            if not card.count():continue
            card.scroll_into_view_if_needed();page.evaluate("()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
            card.screenshot(path=str(OUT / 'screenshots' / f'{gallery}-{item}-{args.phase}.png'))
        ports=[row['targetPortAudit'] for row in arrows if row['targetPortAudit']]
        rendered.append({'gallery':gallery,'markerArrowCount':len(arrows),'directionGlyphCount':len(glyphs),'directionGlyphLowCount':sum(min(row.get('contrast',21),row.get('headContrast',21),row.get('shaftContrast',21))<3 for row in glyphs),'headOcclusionCount':sum(row['headHidden'] for row in arrows),'headLowContrastCount':sum(row['headContrast'] is None or row['headContrast']<3 for row in arrows),'shaftLowContrastCount':sum(row['shaftMinimumContrast']<3 for row in arrows),'markerMismatchCount':sum(row['markerMismatch'] for row in arrows),'unresolvedCount':len(page.locator('[data-arrow-unresolved]').all()),'targetPorts':ports,'targetPortFailureCount':sum(not p['passed'] for p in ports),'arrows':arrows,'glyphs':glyphs})
    for colorset,palette in scaffold.PALETTES.items():
        for color in palette['allowed']:
            recipe=scaffold.defaults('flow');recipe['style'].update(colorset=colorset,color=color)
            source=OUT / 'data' / f'flow-{colorset}-{color[1:]}.svg';source.write_text(scaffold.build(recipe),encoding='utf-8')
            page.goto(source.as_uri())
            arrows=page.locator('[id$="-shaft"],[id$="-head"]').evaluate_all("es=>es.map(e=>({id:e.id,stroke:getComputedStyle(e).stroke,fill:getComputedStyle(e).fill}))")
            rgb=[int(color[index:index+2],16) for index in (1,3,5)]
            linear=[value/255/12.92 if value/255<=.04045 else ((value/255+.055)/1.055)**2.4 for value in rgb]
            contrast=21.0 if all(row['stroke'] == 'rgb(0, 0, 0)' for row in arrows) else 1.05/(sum(v*w for v,w in zip(linear,(.2126,.7152,.0722)))+.05)
            rendered.append({'route':'svg-brief-flow','colorset':colorset,'color':color,'arrowCount':len(arrows)//2,'whiteCanvasContrast':contrast,'arrowPaint':arrows,'passes':contrast>=3})
    browser.close()
report={'phase':args.phase,'date':'2026-10-03','producerFiles':sources,'rendered':rendered}
(OUT / f'data/inventory-{args.phase}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
compact={'phase':report['phase'],'date':report['date'],'producerFileCount':len(sources),'producerFiles':[{'skill':r['skill'],'path':r['path'],'matchCount':len(r['matches'])} for r in sources],
         'galleries':[{k:v for k,v in record.items() if k not in ('arrows','glyphs')} for record in rendered if 'gallery' in record],
         'svgBriefFailingTokens':[{'colorset':r['colorset'],'color':r['color'],'contrast':r['whiteCanvasContrast']} for r in rendered if r.get('route')=='svg-brief-flow' and not r['passes']]}
(EVIDENCE / f'inventory-{args.phase}-20261003.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'producerFileCount':len(sources),'galleries':compact['galleries'],'svgBriefFailingTokenCount':len(compact['svgBriefFailingTokens'])},indent=2))
