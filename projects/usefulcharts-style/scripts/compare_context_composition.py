#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Build a private equal-width comparison and preserve source/geometry invariants."""

import hashlib
import html
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32'
CANONICAL=ROOT/'skills/usefulcharts-style/assets/examples/usefulcharts-style'
BASELINE=ART/'baseline-gallery'
NS={'s':'http://www.w3.org/2000/svg'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ART/'comparison';output.mkdir(exist_ok=True)
    BASELINE.mkdir(exist_ok=True)
    for name in ('atlas-of-inquiry','aurelian-families','five-regional-histories'):
        for suffix in ('.svg','.json'):
            target=BASELINE/(name+suffix)
            if not target.exists():shutil.copyfile(CANONICAL/(name+suffix),target)
    families=[('lineage','atlas-of-inquiry','denominations','Institutional histories',
               'The revised symbols now distinguish their subjects. Five large families still persist through most of the page; the reference has more major subdivisions, shifts of emphasis and local visual identities. Routing is preserved, so the emblem change alone cannot establish composition parity.'),
              ('genealogy','aurelian-families','royal','Genealogy',
               'The opening fan, compact nameplates and selected portraits give a recognizable family-tree structure. Much of the middle still repeats similar-sized boxes and small names. The retained synthetic genealogy has fewer varied contextual anchors than the reference. This revision does not change its composition.'),
              ('timeline','five-regional-histories','history','Parallel chronology',
               'Mixed stems and bands preserve the numeric scale and make important periods visible. The five regional histories remain more regular than the reference and several vertical labels dominate their adjoining prose. This revision does not change their composition.')]
    records=[]
    for mode,name,ref,title,critique in families:
        old=BASELINE/(name+'.svg');new=ART/'gallery-candidate'/(name+'.svg')
        old_root=ET.parse(old).getroot();new_root=ET.parse(new).getroot()
        text=lambda root:[''.join(n.itertext()) for n in root.findall('.//s:text',NS)]
        edges=lambda root:[dict(n.attrib) for n in root.findall('.//s:path[@data-edge-id]',NS)]
        same_source=sha(BASELINE/(name+'.json'))==sha(ART/'gallery-candidate'/(name+'.json'))
        same_text=text(old_root)==text(new_root);same_edges=edges(old_root)==edges(new_root)
        assert same_source and same_text and same_edges
        records.append(dict(id=name,source_unchanged=same_source,text_unchanged=same_text,edge_geometry_unchanged=same_edges,
                            old_svg_sha256=sha(old),new_svg_sha256=sha(new),svg_changed=sha(old)!=sha(new),critique=critique))
    style='''<style>*{box-sizing:border-box}body{font:17px/1.5 Arial;margin:24px;background:#eee9dc;color:#242722}h1{font-size:29px}h2{font-size:21px}p{max-width:1250px}.controls{display:flex;gap:12px;flex-wrap:wrap;position:sticky;top:0;padding:12px;background:#eee9dc}button,a{font:inherit}button{padding:8px 14px;cursor:pointer}button[aria-pressed=true]{background:#902f29;color:white}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}figure{margin:0}img{display:block;width:100%;height:auto}.two{grid-template-columns:repeat(2,minmax(0,1fr))}section[hidden]{display:none}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style>'''
    figures=lambda items:''.join('<figure><h2>'+html.escape(label)+'</h2><img src="'+path.as_uri()+'"></figure>' for label,path in items)
    sections=[]
    for mode,name,ref,title,critique in families:
        sections.append('<section id="'+mode+'" '+('hidden' if mode!='lineage' else '')+'><h2>'+title+'</h2><p>'+critique+'</p><div class="grid">'+figures([
            ('UsefulCharts reference',ROOT/f'projects/usefulcharts-style/artifacts/images/reference-{ref}.png'),
            ('Published baseline',BASELINE/(name+'.svg')),
            ('Revised candidate',ART/'gallery-candidate'/(name+'.svg'))])+'</div></section>')
    sections.append('<section id="publishing" hidden><h2>New contextual opening and shorter education branch</h2><p>Disclosed fictional development source: all 70 records and 97 typed relationships are retained. Eleven education records move as a local group; their content, type and colors remain unchanged. The opening adds an illustrated source-backed paragraph and counts of the institutions shown. The page still has long dotted cross-family paths; this is a local improvement, not parity evidence.</p><div class="grid two">'+figures([
        ('Before',ROOT/'projects/usefulcharts-style/artifacts/reviews/local-stories-v31/publishing-final/poster.png'),
        ('After',ART/'native-context-frozen/poster.png')])+'</div></section>')
    tabs=[(f[0],f[3]) for f in families]+[('publishing','Publishing case')]
    page=output/'index.html'
    page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reference and composition review</title>'+style+
        '<h1>Reference and composition review</h1><p>Private author comparison at equal display widths. UsefulCharts previews remain local reference material. The goal is equivalent quality and composition; these observations are unblinded and do not prove indistinguishability.</p><p><a href="../emblems-first/comparison.html">Compare the fourteen emblem subjects at actual panel sizes</a></p><nav class="controls">'+
        ''.join('<button data-tab="'+key+'" aria-pressed="'+str(key=='lineage').lower()+'">'+label+'</button>' for key,label in tabs)+'</nav>'+''.join(sections)+
        '<script>document.querySelectorAll("button[data-tab]").forEach(b=>b.onclick=()=>{document.querySelectorAll("section").forEach(s=>s.hidden=s.id!==b.dataset.tab);document.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));});</script></html>',encoding='utf-8')
    captures=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();tab=browser.new_page(viewport={'width':2000,'height':1100})
        tab.goto(page.as_uri());tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        for key,_ in tabs:
            tab.locator('[data-tab="'+key+'"]').click()
            assert tab.locator('section:not([hidden])').get_attribute('id')==key
            png=output/(key+'.png');tab.screenshot(path=str(png),full_page=True)
            captures.append(dict(id=key,png_sha256=sha(png)))
        browser.close()
    report=dict(status='pass',scope='Private unblinded author comparison; no aesthetic parity score.',families=records,captures=captures)
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
