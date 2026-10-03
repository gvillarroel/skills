#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect authored computed paint in every D3 gallery SVG and palette overrides."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'projects/colorset-audit/artifacts'
palettes = json.loads((ROOT / 'skills/d3/assets/palettes/colorsets.json').read_text())['colorsets']
pages = [
    ('d3-animated-svg/index.html','colorset2',225),
    ('d3-animated-svg-cs1/index.html','colorset1',225),
    ('d3-animated-svg-colorset2/index.html','colorset2',225),
    ('d3-animated-svg/composition-sheets.html','colorset2',None),
    ('d3-logo-design/index.html','colorset2',None),
    ('d3-logo-textures/index.html','colorset2',40),
]
results=[]
with sync_playwright() as playwright:
    browser=playwright.chromium.launch()
    try:
        for relative,active,count in pages:
            page=browser.new_page(viewport={'width':1440,'height':1100})
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto((ROOT / 'skills/d3/assets/examples' / relative).as_uri(),wait_until='load')
            page.wait_for_timeout(2400)
            evidence=page.evaluate('''allowed => {
              const known=new Set(allowed), failures=[], svgs=[];
              function canonical(value) {
                const m=value.match(/^rgba?\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)(?:\\s*,\\s*([.\\d]+))?\\s*\\)$/);
                if(!m) return null;
                if(m[4]!==undefined && Number(m[4])===0) return null;
                return '#'+[m[1],m[2],m[3]].map(n=>Number(n).toString(16).padStart(2,'0')).join('');
              }
              for(const svg of document.querySelectorAll('svg')) {
                const colors=new Set();
                for(const node of [svg,...svg.querySelectorAll('*')]) {
                  if(['image','metadata','title','desc','script'].includes(node.localName))continue;
                  const style=getComputedStyle(node);
                  for(const key of ['fill','stroke','stop-color','flood-color','lighting-color']) {
                    const value=canonical(style.getPropertyValue(key));
                    if(value) {colors.add(value);if(!known.has(value))failures.push({id:svg.id,node:node.localName,key,value});}
                  }
                }
                svgs.push({id:svg.id,patternId:svg.getAttribute('data-pattern-id'),colors:[...colors].sort()});
              }
              return {svgCount:svgs.length,svgs,failures};
            }''',palettes[active]['allowed'])
            if errors or evidence['failures'] or (count is not None and evidence['svgCount']!=count):
                raise RuntimeError(f'{relative}: {errors}, {evidence["failures"][:8]}, SVG count {evidence["svgCount"]}')
            results.append({'page':relative,'colorset':active,'ok':True,**evidence})
            page.close()
        for mutation in ('override','allowed-list'):
            page=browser.new_page()
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            config={'colorSet':'colorset1'}
            config['paletteOverrides' if mutation=='override' else 'allowedColors'] = {'red':'#123456'} if mutation=='override' else ['#123456']
            page.add_init_script('window.D3_GALLERY_STYLE_CONFIG='+json.dumps(config))
            page.goto((ROOT / 'skills/d3/assets/examples/d3-animated-svg/index.html').as_uri(),wait_until='load')
            page.wait_for_timeout(300)
            if not any('off-palette' in error.lower() for error in errors):
                raise RuntimeError(f'{mutation} was not rejected: {errors}')
            results.append({'mutation':mutation,'rejected':True,'errors':errors})
            page.close()
    finally:browser.close()
report=OUT / 'data/custom-browser-coverage.json'
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps({'ok':True,'results':results},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'pages':len(pages),'svgs':sum(r.get('svgCount',0) for r in results),'negativeCases':2,'report':str(report)}))
