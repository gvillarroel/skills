#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Check opaque defaults, explicit alpha, hidden/reveal states and gallery text."""
import importlib.util
import json
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT / "projects/custom-solid-style/artifacts"


def load(relative):
    spec=importlib.util.spec_from_file_location("review_module",ROOT / relative)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


adapter=load("skills/d3/scripts/colorset_adapter.py")
gallery=load("skills/procedural-svg-animation/scripts/build_procedural_gallery.py")
families=json.loads(gallery.CATALOG_PATH.read_text(encoding="utf-8"))["families"]
source='''<html><body><svg viewBox="0 0 800 200" width="1000">
<rect id="ordinary" x="10" y="20" width="60" height="60" fill="#9e1b32" fill-opacity=".86" opacity=".8"/>
<rect id="semantic" data-opacity-role="semantic" x="100" y="20" width="60" height="60" fill="#9e1b32" fill-opacity=".3"/>
<rect id="hidden" x="190" y="20" width="60" height="60" fill="#9e1b32" opacity="0"/>
<rect id="hidden-fill" x="270" y="20" width="60" height="60" fill="#9e1b32" fill-opacity="0"/>
<rect id="reveal" data-opacity-role="reveal" x="350" y="20" width="60" height="60" fill="#9e1b32" opacity="0"/>
<rect id="smil" x="430" y="20" width="60" height="60" fill="#9e1b32" fill-opacity=".8" opacity="0"><animate attributeName="opacity" values="0;1" begin="2s" dur="2s" fill="freeze"/></rect>
<rect id="css" x="510" y="20" width="60" height="60" fill="#9e1b32" opacity="0" style="animation:reveal 2s linear 2s forwards"/>
<rect id="transition" x="590" y="20" width="60" height="60" fill="#9e1b32" opacity="0" style="transition:opacity 2s linear"/>
<rect id="focus" tabindex="0" x="660" y="20" width="60" height="60" fill="#9e1b32" opacity=".8" fill-opacity=".86"/>
<g><rect id="paint-cycle" x="10" y="120" width="100" height="60" fill="#9e1b32"><animate attributeName="fill" values="#9e1b32;#f1c319;#9e1b32" keyTimes="0;.5;1" dur="3s" repeatCount="indefinite"/></rect><text id="paint-label" x="60" y="156" text-anchor="middle">Paint<animate attributeName="fill" values="#e7e7e7;#333e48;#e7e7e7" keyTimes="0;.5;1" dur="3s" repeatCount="indefinite"/></text></g>
</svg><style>@keyframes reveal{from{opacity:0}to{opacity:1}}#focus:focus{opacity:.25;fill-opacity:.4}</style></body></html>'''
test=OUT / "data/alpha-cases.html"
test.write_text(adapter.adapt_artifact(source,"colorset2"),encoding="utf-8")
checks=[]
with sync_playwright() as engine:
    browser=engine.chromium.launch(channel="msedge")
    page=browser.new_page()
    page.goto(test.as_uri())
    page.wait_for_timeout(180)
    first=page.locator("rect").evaluate_all("es=>Object.fromEntries(es.map(e=>[e.id,{opacity:+getComputedStyle(e).opacity,fillOpacity:+getComputedStyle(e).fillOpacity}]))")
    assert first["ordinary"]=={"opacity":1,"fillOpacity":1},first
    assert first["semantic"]["fillOpacity"]==.3,first
    assert all(first[name]["opacity"]==0 for name in ("hidden","reveal","smil","css","transition")),first
    assert first["hidden-fill"]["fillOpacity"]==0,first
    # An ordinary reveal may retain its opacity animation while its paint is opaque.
    assert first["smil"]["fillOpacity"]==1,first
    assert first["focus"]=={"opacity":1,"fillOpacity":1},first
    page.locator("#focus").focus()
    page.wait_for_timeout(100)
    focus=page.locator("#focus").evaluate("e=>({opacity:+getComputedStyle(e).opacity,fillOpacity:+getComputedStyle(e).fillOpacity})")
    assert focus=={"opacity":.25,"fillOpacity":.4},focus
    page.locator("#focus").evaluate("e=>e.blur()")
    page.wait_for_timeout(100)
    blur=page.locator("#focus").evaluate("e=>({opacity:+getComputedStyle(e).opacity,fillOpacity:+getComputedStyle(e).fillOpacity})")
    assert blur=={"opacity":1,"fillOpacity":1},blur
    page.evaluate("document.querySelector('#reveal').setAttribute('opacity','.25');document.querySelector('#transition').setAttribute('opacity','1');")
    page.wait_for_timeout(100)
    second=page.locator("#reveal,#transition").evaluate_all("es=>Object.fromEntries(es.map(e=>[e.id,+getComputedStyle(e).opacity]))")
    assert second["reveal"]==.25 and 0<second["transition"]<1,second
    checks.append({"case":"d3-alpha-states","passed":True,"initial":first,"revealed":second,"focus":focus,"blur":blur})
    timeline=[]
    for moment in (.2,.8,1.49,1.51,2.2,2.99):
        page.evaluate("time=>{const svg=document.querySelector('svg');svg.pauseAnimations();svg.setCurrentTime(time)}",moment)
        page.evaluate("()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
        paint=page.locator("#paint-label").evaluate("e=>({actual:getComputedStyle(e).fill,textTiming:e.querySelector('animate').getAttribute('calcMode'),markTiming:document.querySelector('#paint-cycle animate').getAttribute('calcMode')})")
        assert paint["actual"]==("rgb(255, 255, 255)" if moment<1.5 else "rgb(0, 0, 0)"),paint
        assert paint["textTiming"]==paint["markTiming"]=="discrete",paint
        timeline.append({"seconds":moment,**paint})
    checks.append({"case":"d3-smil-discrete-text","passed":True,"timeline":timeline})
    for colorset in ("colorset1","colorset2"):
        css=gallery.render_gallery_css(families,colorset)
        html='<html><head><style>'+css+'</style></head><body><div class="family-grid">'+''.join(f'<button class="family-tile" data-family-filter="{family["id"]}" aria-pressed="false"><span class="family-count">06</span><strong>Family</strong><small>Meaning</small></button>' for family in families)+'</div><button class="button primary" id="primary">Replay</button><article class="pattern-card"><ul class="metadata-list"><li>Normal</li><li class="diagnostic-pill">Diagnostic</li></ul><pre class="signature">Signature</pre><div class="card-controls"><button class="button">Play</button></div></article></body></html>'
        path=OUT / "data" / f"procedural-chrome-{colorset}.html"
        path.write_text(html,encoding="utf-8")
        page.goto(path.as_uri())
        rows=page.evaluate(r'''() => {
          const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value};
          return [...document.querySelectorAll('.family-tile,.family-count,.family-tile strong,.family-tile small,#primary,.metadata-list li,.signature,.card-controls .button')].map(e=>{
            const style=getComputedStyle(e);let bg=style.backgroundColor;let parent=e.parentElement;while(bg==='rgba(0, 0, 0, 0)'&&parent){bg=getComputedStyle(parent).backgroundColor;parent=parent.parentElement;}
            const rgb=bg.match(/\d+/g).slice(0,3).map(Number),lum=rgb.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
            const expected=(lum+.05)/.05>=1.05/(lum+.05)?'#000000':'#ffffff';return {tag:e.className||e.id,fill:hex(bg),expected,actual:hex(style.color),border:style.borderTopWidth};
          });
        }''')
        assert all(row["expected"]==row["actual"] and row["border"]=="0px" for row in rows),rows
        family_fills=page.locator(".family-tile").evaluate_all("es=>es.map(e=>getComputedStyle(e).backgroundColor)")
        assert len(family_fills)==len(set(family_fills))==11,family_fills
        page.locator("#primary").hover()
        hover=page.locator("#primary").evaluate("e=>({fill:getComputedStyle(e).backgroundColor,text:getComputedStyle(e).color})")
        assert hover["text"]=="rgb(255, 255, 255)",hover
        page.screenshot(path=str(OUT / "screenshots" / f"procedural-chrome-{colorset}.png"))
        checks.append({"case":"procedural-chrome","colorset":colorset,"passed":True,"textCheckCount":len(rows),"uniqueFamilyFills":11,"rows":rows,"hover":hover})
    browser.close()
report={"passed":True,"checks":checks}
(OUT / "data/alpha-chrome-check.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"passed":True,"cases":len(checks),"textChecks":sum(item.get("textCheckCount",0) for item in checks)}))
