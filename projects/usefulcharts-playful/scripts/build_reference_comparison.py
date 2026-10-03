#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Build and inspect a private comparison using intact reference and project PNGs."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
from playwright.sync_api import sync_playwright

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
OUT = PROJECT / "artifacts/reference-comparison"
REFERENCES = [
    ("royal", "European Royal Family Tree (West)", "european-royal-family-tree"),
    ("denominations", "Christian Denominations Family Tree", "christian-denominations-family-tree"),
    ("history", "Timeline of World History", "timeline-of-world-history"),
    ("writing", "Writing Systems of the World", "writing-systems-of-the-world"),
]
CANDIDATES = [
    ("instruments", "How instruments make sound", "writing"),
    ("bsd", "UNIX and the BSD family", "denominations"),
    ("mars", "The long road to Mars", "history"),
    ("civilizations", "Star Trek: civilizations and wars", "history"),
    ("starships", "Star Trek: the fleet through time", "history"),
]
FOCUS = {
    "royal": (.31, .53), "denominations": (.37, .39),
    "history": (.35, .52), "writing": (.14, .22),
    "instruments": (.04, .12), "bsd": (.32, .39),
    "mars": (.33, .14), "civilizations": (.01, .14),
    "starships": (.01, .52),
}

HTML = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UsefulCharts reference comparison</title><style>
*{box-sizing:border-box}body{margin:0;background:#e8e7e3;color:#172932;font:15px system-ui,sans-serif}header{padding:20px 24px;background:#142831;color:#fff}h1{font-size:25px;margin:0 0 10px}p{line-height:1.5;margin:9px 0}header p{max-width:1050px}nav{display:flex;gap:14px;flex-wrap:wrap;padding:16px 24px;background:#fff}label{display:grid;gap:5px;font-size:13px}select,input,button{font:inherit;padding:8px;border:1px solid #9babb2;border-radius:4px;background:#fff;color:#172932}button{cursor:pointer;align-self:end}main{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:18px 24px;align-items:start}article{min-width:0}h2{font-size:17px;min-height:42px;margin:0 0 7px}.meta{font-size:12px;min-height:35px}.viewport{overflow:auto;background:#c9caca;padding:10px;max-height:78vh}.paper{margin:0 auto}.paper svg{display:block;width:100%;height:auto}a{color:#176581}.note{margin:0 24px 20px;padding:14px;background:#fff}.capture .viewport{max-height:none;overflow:visible}.capture nav,.capture .note{display:none}.capture header{padding:10px 24px}.capture header p{display:none}.capture main{padding:10px 24px}.capture .meta{min-height:0}.capture h2{min-height:0}.capture .paper{max-width:none}@media(max-width:760px){main{grid-template-columns:1fr;padding:12px}nav{padding:12px}header{padding:16px}.note{margin:0 12px 15px}.viewport{max-height:75vh}}
</style><header><h1>What makes the poster rewarding to explore?</h1><p>Four original UsefulCharts references and five illustrated revisions. This is an informed visual comparison across related design tasks, not a blinded authorship test or a semantic density census.</p></header>
<nav><label>UsefulCharts reference<select id="reference"></select></label><label>Our illustrated revision<select id="candidate"></select></label><label>Comparison basis<select id="mode"><option value="width">Whole poster · same width</option><option value="area">Whole poster · same area</option><option value="body">Body · same relative crop</option><option value="detail">Detail · same relative crop</option></select></label><label>Zoom<input id="zoom" type="range" min="65" max="200" value="100"></label><button id="reset">Reset view</button></nav>
<main><article id="left"><h2></h2><p class="meta"></p><div class="viewport"><div class="paper"></div></div></article><article id="right"><h2></h2><p class="meta"></p><div class="viewport"><div class="paper"></div></div></article></main>
<p class="note">Follow a connection, identify the fact attached to an image, and compare how many visual lookups each task needs. Check both the full composition and the local detail. Body crops omit the top 10% and bottom 4%; detail crops show 45% of the width and 24% of the height at a common source-relative scale. Crop positions differ to inspect relevant neighborhoods. Different subjects and chronology directions are not defects. Public preview resolution limits fine-text inspection; no factual count is inferred from pixels.</p>
<script>const data=__DATA__;const qs=s=>document.querySelector(s);for(const [selector,items]of [['#reference',data.references],['#candidate',data.candidates]])for(const n of items){const o=document.createElement('option');o.value=n.id;o.textContent=n.title;qs(selector).append(o)}
qs('#reference').value='history';qs('#candidate').value='civilizations';
function draw(){const a=data.references.find(n=>n.id===qs('#reference').value),b=data.candidates.find(n=>n.id===qs('#candidate').value),mode=qs('#mode').value,z=+qs('#zoom').value/100,base=document.body.classList.contains('capture')?650:Math.min(700,qs('#left .viewport').clientWidth-20);for(const [side,n]of [['left',a],['right',b]]){const article=qs('#'+side);article.querySelector('h2').textContent=(side==='left'?'UsefulCharts · ':'Our revision · ')+n.title;article.querySelector('.meta').innerHTML=`<a href="${n.source}" target="_blank" rel="noopener">${side==='left'?'Official product page':'Open PDF'}</a> · ${n.width} × ${n.height} source pixels`;let box=[0,0,n.width,n.height];if(mode==='body')box=[.025*n.width,.1*n.height,.95*n.width,.86*n.height];if(mode==='detail')box=[n.focus[0]*n.width,n.focus[1]*n.height,.45*n.width,.24*n.height];const width=mode==='area'?Math.sqrt(base*base*(n.width/n.height)/Math.max(1,a.width/a.height,b.width/b.height)):base;const paper=article.querySelector('.paper');paper.style.width=width*z+'px';paper.dataset.width=width*z;paper.dataset.height=width*z*box[3]/box[2];paper.innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.join(' ')}" width="${box[2]}" height="${box[3]}" role="img" aria-label="${n.title}"><image href="${n.image}" x="0" y="0" width="${n.width}" height="${n.height}"/></svg>`;}}
qs('#candidate').onchange=()=>{qs('#reference').value=data.candidates.find(n=>n.id===qs('#candidate').value).reference;draw()};for(const id of ['reference','mode','zoom'])qs('#'+id).oninput=draw;qs('#reset').onclick=()=>{qs('#zoom').value=100;qs('#mode').value='width';draw();document.querySelectorAll('.viewport').forEach(e=>e.scrollTo(0,0))};window.addEventListener('resize',draw);draw();
</script></html>'''


def metadata(path):
    blob = path.read_bytes()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Expected PNG: {path}")
    width, height = struct.unpack(">II", blob[16:24])
    return dict(width=width, height=height, sha256=hashlib.sha256(blob).hexdigest())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "references").mkdir(exist_ok=True)
    data = dict(references=[], candidates=[])
    for ident, title, slug in REFERENCES:
        path = REPO / f"projects/usefulcharts-style/artifacts/images/reference-{ident}.png"
        target = OUT / f"references/{ident}.png"
        shutil.copy2(path, target)
        data["references"].append(dict(id=ident, title=title, image=f"references/{ident}.png", source=f"https://usefulcharts.com/products/{slug}", focus=FOCUS[ident], **metadata(path)))
    for ident, title, reference in CANDIDATES:
        path = PROJECT / f"artifacts/revision-2/{ident}/poster.png"
        data["candidates"].append(dict(id=ident, title=title, reference=reference, image=f"../revision-2/{ident}/poster.png", source=f"../revision-2/{ident}/poster.pdf", focus=FOCUS[ident], **metadata(path)))
    (OUT / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(HTML.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=dict(width=1480, height=1000))
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("**/*", lambda route: route.abort() if route.request.url.startswith(("http://", "https://")) else route.continue_())
        page.goto((OUT / "index.html").as_uri())
        page.evaluate("document.body.classList.add('capture');draw()")
        for ident, _, _ in CANDIDATES:
            page.select_option("#candidate", ident, force=True)
            for mode in ["width", "area", "body", "detail"]:
                page.select_option("#mode", mode, force=True)
                page.evaluate("""async()=>{await Promise.all([...document.querySelectorAll('image')].map(e=>new Promise((resolve,reject)=>{const i=new Image();i.onload=resolve;i.onerror=reject;i.src=e.getAttribute('href')})))}""")
                sizes = page.locator(".paper").evaluate_all("es=>es.map(e=>({w:+e.dataset.width,h:+e.dataset.height}))")
                if mode == "area":
                    assert abs(sizes[0]["w"] * sizes[0]["h"] - sizes[1]["w"] * sizes[1]["h"]) < 1
                else:
                    assert abs(sizes[0]["w"] - sizes[1]["w"]) < .1
                page.screenshot(path=str(OUT / f"{ident}-{mode}.png"), full_page=True)
                checks.append(dict(case=ident, mode=mode, sizes=sizes, status="pass"))
        page.evaluate("document.body.classList.remove('capture');draw()")
        page.set_viewport_size(dict(width=390, height=844))
        page.locator("#reset").click()
        assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+1")
        page.locator("#zoom").fill("175")
        page.locator("#zoom").dispatch_event("input")
        assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+1")
        page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
        assert not errors, errors
        browser.close()
    result = dict(status="pass", offline=True, mobile=True, errors=errors, checks=checks)
    (OUT / "browser-checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status="pass", comparisons=len(checks), output=str(OUT / "index.html"))))


if __name__ == "__main__":
    main()
