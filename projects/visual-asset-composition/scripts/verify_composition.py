#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Check native SVG geometry, reading views, mobile controls, and capture size."""
from __future__ import annotations

import functools
import http.server
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/visual-asset-composition/artifacts/interactions"

GEOMETRY = r"""() => {
  const tags='path,rect,circle,ellipse,line,polyline,polygon,text';
  const records=[];
  for(const svg of document.querySelectorAll('.chart-stage>svg')) {
    for(const animation of svg.getAnimations({subtree:true})) {try{animation.finish()}catch{}}
    const clone=svg.cloneNode(true);
    clone.querySelectorAll('style').forEach(e=>{if(e.textContent.includes('easv-'))e.remove()});
    [clone,...clone.querySelectorAll('*')].forEach(e=>{
      if(e.hasAttribute('class')) e.setAttribute('class', e.getAttribute('class').split(/\s+/).filter(v=>!v.startsWith('easv-')).join(' '));
      e.style.setProperty('animation','none','important');
    });
    const box=svg.getBoundingClientRect();
    Object.assign(clone.style,{position:'fixed',left:'-20000px',top:'0',width:box.width+'px',height:box.height+'px'});
    document.body.append(clone);
    const cb=clone.getBoundingClientRect(), a=[...svg.querySelectorAll(tags)], b=[...clone.querySelectorAll(tags)];
    let maxDelta=0; const mismatches=[];
    a.forEach((e,i)=>{if(e.closest('defs,clipPath,mask,pattern,symbol'))return;
      const x=e.getBoundingClientRect(),y=b[i].getBoundingClientRect();
      if(x.width===0&&x.height===0&&y.width===0&&y.height===0)return;
      const delta=Math.max(Math.abs((x.x-box.x)-(y.x-cb.x)),Math.abs((x.y-box.y)-(y.y-cb.y)),Math.abs(x.width-y.width),Math.abs(x.height-y.height));
      maxDelta=Math.max(maxDelta,delta);if(delta>.15)mismatches.push({tag:e.tagName,text:e.textContent.slice(0,40),delta});
    });
    records.push({id:svg.closest('article').dataset.patternId||svg.closest('article').id,marks:a.length,maxDelta,mismatches});
    clone.remove();
  }
  return records;
}"""

EXPAND = r"""({selector,stageSelector}) => {
  const records=[];
  for(const button of document.querySelectorAll(selector)) {
    const stage=button.closest('article').querySelector(stageSelector),svg=stage.querySelector('svg');
    const before=svg.getBoundingClientRect().width;
    button.click();
    const box=svg.getBoundingClientRect();
    const overflow=Math.max(0,document.documentElement.scrollWidth-innerWidth);
    const expanded=button.getAttribute('aria-pressed')==='true'&&stage.tabIndex===0&&box.width>=639;
    button.click();
    const restored=Math.abs(svg.getBoundingClientRect().width-before)<.2&&button.getAttribute('aria-pressed')==='false';
    records.push({id:button.dataset.expand||button.closest('article').dataset.patternId||button.closest('article').id,width:box.width,height:box.height,expanded,restored,overflow});
  }
  return records;
}"""


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    rows, failures = [], []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", args=["--enable-unsafe-swiftshader"])
            for motion in ["reduce", "no-preference"]:
                page = browser.new_page(viewport={"width":1440,"height":1000}, reduced_motion=motion)
                page.goto(f"http://127.0.0.1:{server.server_port}/dist/pages/examples/echarts-animated-svg/")
                page.wait_for_timeout(250)
                geometry = page.evaluate(GEOMETRY)
                assert len(geometry)==43, len(geometry)
                errors = [r for r in geometry if r["mismatches"]]
                rows.append({"test":"echarts-geometry","motion":motion,"charts":len(geometry),"marks":sum(r["marks"] for r in geometry),"maxDelta":max(r["maxDelta"] for r in geometry),"errors":errors})
                failures.extend(errors)
                page.close()
            for gallery, selector, stage in [
                ("d3-animated-svg","[data-expand]",".viz-frame"),
                ("d3-animated-svg-cs1","[data-expand]",".viz-frame"),
                ("d3-animated-svg-colorset2","[data-expand]",".viz-frame"),
                ("echarts-animated-svg","[data-expand-card]",".chart-stage"),
            ]:
                for width in [1440,390]:
                    page=browser.new_page(viewport={"width":width,"height":1000 if width>600 else 844},has_touch=width<600,reduced_motion="reduce")
                    page.goto(f"http://127.0.0.1:{server.server_port}/dist/pages/examples/{gallery}/")
                    page.locator(selector).first.wait_for()
                    page.locator(selector).first.click()
                    page.screenshot(path=str(OUT/f"{gallery}-{width}-expanded.png"))
                    page.locator(selector).first.click()
                    records=page.evaluate(EXPAND,{"selector":selector,"stageSelector":stage})
                    errors=[r for r in records if not r["expanded"] or not r["restored"] or r["overflow"]>1]
                    if width<600:
                        short=page.locator(selector).evaluate_all("es=>es.filter(e=>e.getBoundingClientRect().height<44).length")
                        if short: errors.append({"shortControls":short})
                    rows.append({"test":"reading-view","gallery":gallery,"width":width,"cards":len(records),"errors":errors})
                    failures.extend(errors)
                    page.close()
            page=browser.new_page(viewport={"width":390,"height":844},has_touch=True)
            page.goto(f"http://127.0.0.1:{server.server_port}/dist/pages/examples/d3-logo-design/")
            layout=page.evaluate("""()=>{const p=document.querySelector('.studio-preview').getBoundingClientRect(),c=document.querySelector('.controls').getBoundingClientRect();return {previewBottom:p.bottom,controlsTop:c.top,overflow:document.documentElement.scrollWidth-innerWidth}}""")
            assert layout["previewBottom"]<=layout["controlsTop"] and layout["previewBottom"]<700 and layout["overflow"]<=1, layout
            rows.append({"test":"mobile-logo-preview",**layout})
            page.goto(f"http://127.0.0.1:{server.server_port}/dist/pages/examples/procedural-svg-animation/")
            disclosure=page.locator('.family-browser')
            assert disclosure.get_attribute('open') is None
            disclosure.locator('summary').click()
            assert disclosure.get_attribute('open') is not None
            rows.append({"test":"procedural-disclosure","passed":True})
            page.goto(f"http://127.0.0.1:{server.server_port}/dist/pages/examples/ai-concept-videos/")
            frames=page.evaluate("""()=>AI_CONCEPTS.map(c=>{renderConceptFrame(c.id,40);const r=document.querySelector('.video-frame').getBoundingClientRect();return {id:c.id,width:r.width,height:r.height,overflow:document.documentElement.scrollWidth-innerWidth}})""")
            assert all(f["width"]<=391 and f["overflow"]<=1 for f in frames), frames
            page.screenshot(path=str(OUT/'video-mobile.png'))
            page.set_viewport_size({"width":1280,"height":720})
            capture=page.evaluate("""()=>{renderConceptFrame(AI_CONCEPTS[0].id,40,{capture:true});const r=document.querySelector('.video-frame').getBoundingClientRect();return {width:r.width,height:r.height}}""")
            assert capture=={"width":1280,"height":720}, capture
            rows.append({"test":"video-preview-and-capture","concepts":len(frames),"capture":capture,"passed":True})
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result={"passed":not failures,"checks":rows,"failures":failures}
    (OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return int(bool(failures))


if __name__=="__main__":
    raise SystemExit(main())
