#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a local before/after catalog review from the recorded browser audits."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / 'projects/visual-asset-composition/artifacts'


def main():
    baseline=json.loads((ARTIFACTS/'baseline/audit.json').read_text())
    final=json.loads((ARTIFACTS/'final/audit.json').read_text())
    old={(p['id'],p['width']):p for p in baseline['pages']}
    rows=[]
    cards=[]
    preferred=['d3-logo-design','echarts-animated-svg','procedural-svg-animation',
               'usefulcharts-style','mermaid-max-complexity','plantuml-colorset-renderer',
               'ai-concept-videos']
    pairs=sorted((p for p in final['pages'] if (p['id'],p['width']) in old),
                 key=lambda p:(preferred.index(p['id']) if p['id'] in preferred else 99,p['id'],p['width']))
    for p in pairs:
        b=old[p['id'],p['width']]
        def header(v): return v['header']['height'] if v.get('header') else 0
        def first(v): return v['cards'][0]['y'] if v.get('cards') else None
        row={'page':p['id'],'width':p['width'],'headerBefore':header(b),'headerAfter':header(p),
             'firstCardBefore':first(b),'firstCardAfter':first(p),'overflowBefore':b.get('overflowX'),
             'overflowAfter':p.get('overflowX'),'smallSvgTextAfter':len(p.get('smallSvgText',[])),
             'shortControlsAfter':len(p.get('shortControls',[]))}
        rows.append(row)
        metrics=f"Header: {header(b):.0f} → {header(p):.0f} px · Horizontal overflow: {b.get('overflowX',0)} → {p.get('overflowX',0)} px"
        if first(b) is not None: metrics+=f" · First card: {first(b):.0f} → {first(p):.0f} px from page top"
        cards.append(f'''<article data-page="{p['id']}" data-width="{p['width']}">
<h2>{html.escape(p['id'])} <small>{p['width']} px</small></h2><p>{metrics}</p>
<div class="pair"><figure><figcaption>Before</figcaption><a href="../baseline/{p['id']}-{p['width']}.png"><img loading="lazy" src="../baseline/{p['id']}-{p['width']}.png" alt="Before: {p['id']}"></a></figure><figure><figcaption>After</figcaption><a href="../final/{p['id']}-{p['width']}.png"><img loading="lazy" src="../final/{p['id']}-{p['width']}.png" alt="After: {p['id']}"></a></figure></div></article>''')
    options=''.join(f'<option value="{name}">{name}</option>' for name in sorted({p['id'] for p in pairs}))
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Visual asset composition review</title>
<style>:root{font:16px/1.5 Arial,sans-serif;color:#333e48;background:#f7f7f7}*{box-sizing:border-box}body{margin:0;padding:16px}main{max-width:1500px;margin:auto}h1{font-size:clamp(24px,4vw,38px);margin:0 0 8px}header{border-left:5px solid #9e1b32;padding:4px 12px}p{margin:8px 0}nav{position:sticky;top:0;background:#f7f7f7;padding:12px 0;display:flex;gap:12px;flex-wrap:wrap;z-index:2}label{display:grid;gap:4px}select{min-height:44px;font:inherit;max-width:100%}article{background:white;border:1px solid #cfcfcf;margin:12px 0;padding:12px}article[hidden]{display:none}h2{margin:0;font-size:20px}small{color:#696969;font-size:14px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}figure{margin:0}figcaption{font-weight:bold;padding:4px 0;color:#9e1b32}img{display:block;max-width:100%;height:auto;border:1px solid #e7e7e7}a{color:#9e1b32}details{margin:12px 0}summary{cursor:pointer;min-height:44px}@media(max-width:650px){body{padding:8px}.pair{gap:6px}article{padding:8px}h2{overflow-wrap:anywhere}}</style>
<main><header><h1>Visual asset composition review</h1><p>Before and after at matching viewport sizes. Select a catalog and viewport; open a capture for its original resolution.</p></header>
<details><summary>Scope and reading notes</summary><p>The automated audit covers 46 page/viewport combinations across 26 skill bundles. These screenshots sample page composition; dense diagrams remain thumbnails until expanded or opened as SVG. The review preserves native artwork, fixed capture dimensions, and authored brand padding.</p><p>ECharts geometry: 43 charts in normal and reduced motion, maximum coordinate deviation 0.002px. D3/ECharts expansion: 1,436 card/viewport checks. Slidev: 66 slides, 222 states, zero findings. PlantUML: 56 published renders and an explicit padding-override check. Technical logos: 1,960 normalized originals.</p><p><a href="measurements.json">Measured differences</a> · <a href="../interactions/report.json">Interaction checks</a></p></details>
<nav><label>Catalog<select id="catalog"><option value="all">All catalogs</option>'''+options+'''</select></label><label>Viewport<select id="width"><option value="390">Phone · 390px</option><option value="1440">Desktop · 1440px</option><option value="all">Both</option></select></label></nav>
'''+''.join(cards)+'''</main><script>const c=document.querySelector('#catalog'),w=document.querySelector('#width');c.value='d3-logo-design';function filter(){document.querySelectorAll('article').forEach(e=>e.hidden=!((c.value==='all'||e.dataset.page===c.value)&&(w.value==='all'||e.dataset.width===w.value)))}c.addEventListener('change',filter);w.addEventListener('change',filter);filter();</script></html>'''
    out=ARTIFACTS/'review'
    out.mkdir(parents=True,exist_ok=True)
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'measurements.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    print(f'Created {len(rows)} before/after comparisons in {out}')


if __name__=='__main__': main()
