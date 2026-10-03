#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "playwright"]
# ///
"""Build a private, equal-area comparison of references and current posters."""
import base64
import json
import math
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/usefulcharts-style/artifacts/reviews/density-v35"
PAIRS = [
    ("genealogy", "European royal genealogy", "reference-royal", "aurelian-families",
     "https://usefulcharts.com/products/european-royal-family-tree",
     "The 561-person candidate is substantial, but record count does not establish equivalent knowledge. The reference integrates more varied historical roles, places and family context. OCR misses many small reference labels, so its apparent numerical advantage is invalid."),
    ("lineage", "Institutional branching history", "reference-denominations", "atlas-of-inquiry",
     "https://usefulcharts.com/products/christian-denominations-family-tree",
     "The candidate has 141 institutions. Similar recognized character volume does not establish similar knowledge: the reference spreads many shorter records and transitions through later history and adds quantitative and geographic claims. Repeated pictograms count as one encoded quantity, not many facts."),
    ("timeline", "Parallel chronology", "reference-history", "five-regional-histories",
     "https://usefulcharts.com/products/timeline-of-world-history",
     "The candidate's 50 periods and 60 event notes provide visibly less branching and explanatory detail. The reference increases contextual density toward recent centuries. Its richer narrative cannot be replaced with wider colored bands, a backdrop map or smaller text."),
]


def main():
    folder = ART / "comparison"
    folder.mkdir(parents=True, exist_ok=True)
    metrics = {x["id"]: x for x in json.loads((ART/"ocr-tiled/summary.json").read_text())}
    pairs = []
    for family, title, reference, candidate, url, observation in PAIRS:
        entry = {"family": family, "title": title, "url": url, "observation": observation}
        for role, item in (("reference", reference), ("candidate", candidate)):
            path = Path(metrics[item]["path"])
            w,h = Image.open(path).size
            factor = math.sqrt(580*870/(w*h))
            entry[role] = {"id": item, "src": "data:image/png;base64,"+base64.b64encode(path.read_bytes()).decode(),
                           "width": w*factor, "height": h*factor, "metrics": metrics[item]}
        pairs.append(entry)
    html = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>UsefulCharts knowledge-density review</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeeae1;color:#242a30;font:16px/1.5 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:30px;margin:0 0 8px}p{max-width:1150px;margin:8px 0}a{color:#155681}header{background:#fff;padding:22px;border-radius:8px}.controls{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin:18px 0}select,input{font:inherit}select{padding:6px}.panes{display:grid;grid-template-columns:1fr 1fr;gap:20px}.pane{min-width:0;background:#fff;border-radius:8px;padding:14px}.viewport{overflow:auto;max-height:980px;background:#ddd9d0;border:1px solid #b9b4a8;padding:12px}.paper{position:relative;margin:auto;flex-shrink:0}.paper img{width:100%;height:100%;display:block}.guide{display:none;position:absolute;left:0;right:0;border-top:2px dashed #087cb8;pointer-events:none}.show-guides .guide{display:block}.metrics{font-size:14px;margin-top:10px}.warning{background:#fff1ce;border-left:5px solid #a46900;padding:10px 14px}.status{font-weight:650;color:#794813}h2{font-size:19px;margin:0 0 9px}footer{font-size:13px;padding-top:16px}@media(max-width:900px){.panes{grid-template-columns:1fr}main{padding:12px}}
</style><main><header><h1>Knowledge density: reference minimum</h1>
<p>Private analysis of the official previews and the current original examples. Each poster is displayed at the same total area; aspect ratios remain intact.</p>
<p class="warning">OCR is a screening aid, not a census of knowledge. It misses small names, can read logos and map lettering, and cannot verify factual relevance. None of these posters receives a semantic-density pass from these measurements.</p>
<div class="controls"><label>Reference family <select id="family"></select></label><label>Zoom <input id="zoom" type="range" min="0.6" max="1.6" step="0.1" value="1"></label><label><input id="guides" type="checkbox"> Show body thirds</label><a id="source" target="_blank" rel="noreferrer">Official reference</a></div>
<p id="observation"></p><p class="status">Acceptance remains pending: require a reviewed semantic census, no layer below the reference, and legible whole-page distribution.</p></header>
<div class="panes" style="margin-top:18px"><section class="pane"><h2>Official reference</h2><div class="viewport"><div id="reference" class="paper"></div></div><div id="reference-metrics" class="metrics"></div></section><section class="pane"><h2>Current skill example</h2><div class="viewport"><div id="candidate" class="paper"></div></div><div id="candidate-metrics" class="metrics"></div></section></div>
<footer>Reference images remain private and are not part of the skill payload or published example gallery. Body-screening window: 4.5–98.5% of image height. The initial full-image OCR failure and revised tiled measurements are retained separately.</footer></main>
<script>const pairs=__DATA__;const family=document.getElementById('family');for(const p of pairs){const option=document.createElement('option');option.value=p.family;option.textContent=p.title;family.append(option)}
function render(){const p=pairs.find(p=>p.family===family.value),zoom=+document.getElementById('zoom').value;document.getElementById('source').href=p.url;document.getElementById('observation').textContent=p.observation;document.body.dataset.family=p.family;for(const role of ['reference','candidate']){const data=p[role],paper=document.getElementById(role);paper.style.width=data.width*zoom+'px';paper.style.height=data.height*zoom+'px';paper.replaceChildren();const img=document.createElement('img');img.src=data.src;img.alt=role+' '+p.title;paper.append(img);for(const y of [.045+.94/3,.045+2*.94/3]){const guide=document.createElement('div');guide.className='guide';guide.style.top=y*100+'%';paper.append(guide)}const m=data.metrics;document.getElementById(role+'-metrics').textContent='OCR screening only: '+m.ocr_line_count+' detected lines; '+m.ocr_character_count+' non-space characters. Lines by body third: '+m.bands.map(b=>b.lines).join(' / ')+'.'}document.body.classList.toggle('show-guides',document.getElementById('guides').checked)}
family.onchange=render;document.getElementById('zoom').oninput=render;document.getElementById('guides').onchange=render;render();</script></html>'''.replace("__DATA__", json.dumps(pairs).replace("</", "<\\/"))
    page_path = folder / "index.html"
    page_path.write_text(html, encoding="utf-8")
    checks=[]
    with sync_playwright() as p:
        browser=None
        for options in ({},{"channel":"chrome"},{"channel":"msedge"}):
            try:
                browser=p.chromium.launch(headless=True,**options)
                break
            except Exception:
                continue
        if browser is None:
            raise RuntimeError("No Chromium browser is available for the review.")
        page=browser.new_page(viewport={"width":1600,"height":1200})
        page.goto(page_path.as_uri())
        for pair in pairs:
            page.locator("#family").select_option(pair["family"])
            page.wait_for_function("Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)")
            areas=page.evaluate("['reference','candidate'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return r.width*r.height})")
            assert abs(areas[0]-areas[1])/areas[0]<.0001, areas
            page.screenshot(path=str(folder/f"{pair['family']}-comparison.png"),full_page=True)
            checks.append({"family":pair["family"],"equal_area":True,"areas":areas})
        page.locator("#guides").check()
        assert page.locator(".guide:visible").count()==4
        page.locator("#zoom").evaluate("e=>e.value='1.4'")
        page.locator("#zoom").dispatch_event("input")
        assert page.locator("#candidate img").is_visible()
        page.set_viewport_size({"width":750,"height":1000})
        assert page.locator(".panes").evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length") == 1
        browser.close()
    (folder/"browser-check.json").write_text(json.dumps({"passed":True,"checks":checks,"controls":["family","zoom","thirds","narrow-layout"]},indent=2)+"\n")
    print(json.dumps({"path":str(page_path),"passed":True,"families":3,"controls":4}))


if __name__ == "__main__":
    main()
