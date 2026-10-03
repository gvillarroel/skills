#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Independently review the built Pages catalog and representative visual outputs."""
from functools import partial
import hashlib
import importlib.util
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / "dist/pages"
OUT = ROOT / "projects/solid-colorset-style/artifacts"
EVIDENCE = ROOT / "evaluations/solid-colorset-style"
(OUT / "screenshots/pages").mkdir(parents=True, exist_ok=True)
(OUT / "reviews").mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
spec=importlib.util.spec_from_file_location("pages_builder",ROOT / "scripts/build-pages.py")
BUILDER=importlib.util.module_from_spec(spec)
spec.loader.exec_module(BUILDER)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(PAGES)))
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"
FRAMES = "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
SVG_PAINT = r'''() => {
  const violations=[],filled=[],labels=[];
  const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value};
  document.querySelectorAll('svg').forEach(svg=>{
    svg.querySelectorAll('rect,circle,ellipse,polygon,path').forEach(shape=>{
      if(shape.closest('defs,mask,clipPath,pattern,[data-outline-tier="overflow"],[data-paint-mode="source"],[data-paint-mode="line-art"]'))return;
      const s=getComputedStyle(shape); if(s.fill==='none'||s.display==='none'||s.visibility==='hidden')return;
      if(shape.localName==='path'&&!/[zZ]\s*$/.test(shape.getAttribute('d')||''))return;
      filled.push(shape);
      if(s.stroke!=='none'&&+s.strokeOpacity>0&&+s.strokeWidth>0)violations.push({id:shape.id,pattern:svg.dataset.patternId,fill:s.fill,stroke:s.stroke});
    });
    svg.querySelectorAll('text,tspan').forEach(t=>{const s=getComputedStyle(t),b=t.getBoundingClientRect();if(b.width&&b.height&&s.display!=='none'&&s.visibility!=='hidden')labels.push({text:t.textContent.slice(0,60),paint:hex(s.fill)});});
  });
  return {svgCount:document.querySelectorAll('svg').length,eligibleFilledMarkCount:filled.length,decorativeOutlineCount:violations.length,outlineExamples:violations.slice(0,6),labelPaints:[...new Set(labels.map(t=>t.paint))],nonBlackWhiteLabels:labels.filter(t=>!['#000000','#ffffff'].includes(t.paint)).slice(0,6)};
}'''
CONTROL_CONTRAST = r'''selectors=>[...document.querySelectorAll(selectors)].filter(e=>e.getBoundingClientRect().width).map(e=>{
  const s=getComputedStyle(e);
  const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value};
  const layers=[];for(let node=e;node;node=node.parentElement){const numbers=getComputedStyle(node).backgroundColor.match(/[\d.]+/g);if(numbers)layers.push({rgb:numbers.slice(0,3).map(Number),alpha:numbers.length===4?+numbers[3]:1});}
  const rgb=layers.reverse().reduce((bg,layer)=>layer.rgb.map((value,index)=>value*layer.alpha+bg[index]*(1-layer.alpha)),[255,255,255]);
  const lum=rgb.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  const expected=(lum+.05)/.05>=1.05/(lum+.05)?'#000000':'#ffffff';
  const actual=hex(s.color);return {selector:e.id?'#'+e.id:'.'+e.className.trim().replace(/\s+/g,'.'),text:e.textContent.trim().slice(0,50),background:'#'+rgb.map(v=>Math.round(v).toString(16).padStart(2,'0')).join(''),expected,actual,passed:actual===expected};
}).filter(Boolean)'''
records=[]
findings=[]
copies=[]


def source_copy(source: Path, built: Path):
    same = source.is_file() and built.is_file() and source.read_bytes() == built.read_bytes()
    equivalence="exact-bytes"
    if not same and source.is_file() and built.is_file():
        expected=source.read_text(encoding="utf-8")
        example_id=built.relative_to(PAGES).parts[1]
        if source.suffix==".html" and example_id.startswith("d3-animated-svg"):
            expected=expected.replace("../d3-animated-svg/node_modules/d3/dist/d3.min.js","https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js").replace("../d3-animated-svg/node_modules/d3-sankey/dist/d3-sankey.min.js","https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js")
            expected=expected.replace("./node_modules/d3/dist/d3.min.js","https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js").replace("./node_modules/d3-sankey/dist/d3-sankey.min.js","https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js")
        elif source.name=="index.html":
            if example_id.startswith("d3-animated-svg"):
                expected=expected.replace("../d3-animated-svg/node_modules/d3/dist/d3.min.js","https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js").replace("../d3-animated-svg/node_modules/d3-sankey/dist/d3-sankey.min.js","https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js")
            expected=BUILDER.ensure_html_head_meta(expected,example_id)
            expected=BUILDER.ensure_html_favicon(expected)
            for name,value in {"data-example-id":example_id,"data-pattern-id":example_id,"data-pattern-page":"true"}.items():
                expected=BUILDER.ensure_body_attribute(expected,name,value)
        lines=[line.rstrip(" \t") for line in expected.splitlines()]
        while lines and not lines[-1]:
            lines.pop()
        expected="\n".join(lines)+"\n"
        same=expected==built.read_text(encoding="utf-8")
        equivalence="documented-build-transforms"
    copies.append({"source":source.relative_to(ROOT).as_posix(),"built":built.relative_to(ROOT).as_posix(),"passed":same,"equivalence":equivalence})
    if not same:
        findings.append({"severity":"error","kind":"source-copy","built":built.relative_to(ROOT).as_posix()})


try:
    with sync_playwright() as engine:
        browser=engine.chromium.launch(channel="msedge")
        for route in ("", "d3-animated-svg-cs1", "d3-animated-svg-colorset2", "threejs-animated-3d", "procedural-svg-animation", "vectorize-art-patterns", "vectorize-abstract-world-maps"):
            page=browser.new_page(viewport={"width":1440,"height":1050})
            errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            url=BASE + (f"/examples/{route}/" if route else "/")
            page.goto(url,wait_until="domcontentloaded")
            if route.startswith("d3-animated"):
                page.wait_for_function("document.querySelectorAll('svg[data-fill-style=\"solid-first\"]').length>200",timeout=120000)
                page.wait_for_timeout(1600)
            if route=="threejs-animated-3d":
                page.wait_for_function("window.__threeGalleryReady===true",timeout=60000)
                page.wait_for_timeout(1200)
            page.evaluate(FRAMES)
            record={"page":route or "catalog","pageErrors":errors,"viewports":[]}
            if route.startswith("d3-animated"):
                record.update(page.evaluate(SVG_PAINT))
                record["cartogram"]=page.locator('[data-example="non-contiguous-cartogram"] svg').evaluate("svg=>{const shapes=[...svg.querySelectorAll('path')].filter(e=>/[zZ]\\s*$/.test(e.getAttribute('d')||''));return {fillCount:new Set(shapes.map(e=>getComputedStyle(e).fill)).size,markCount:shapes.length,opaque:shapes.every(e=>+getComputedStyle(e).fillOpacity===1),borderless:shapes.every(e=>getComputedStyle(e).stroke==='none')}}")
                assert record["cartogram"]==dict(fillCount=5,markCount=5,opaque=True,borderless=True),record["cartogram"]
                record["categoryBurst"]=page.locator('[data-example="category-burst"] svg').evaluate("svg=>{const nodes=[...svg.querySelectorAll('.category-burst-root>circle,.category-burst-node>circle')];return {nodeCount:nodes.length,distinctFills:new Set(nodes.map(e=>getComputedStyle(e).fill)).size,separateRimCount:svg.querySelectorAll('circle[fill=\"none\"]').length,filterCount:svg.querySelectorAll('[filter]').length,spokeCount:svg.querySelectorAll('.category-burst-link').length}}")
                assert record["categoryBurst"]==dict(nodeCount=9,distinctFills=9,separateRimCount=0,filterCount=0,spokeCount=8),record["categoryBurst"]
                if record["decorativeOutlineCount"] or record["nonBlackWhiteLabels"]:
                    findings.append({"severity":"error","kind":"svg-paint","page":route,"outlineCount":record["decorativeOutlineCount"],"text":record["nonBlackWhiteLabels"]})
                for item in ("task-overlap", "category-burst", "speculative-decoding"):
                    card=page.locator(f'[data-example="{item}"]')
                    card.scroll_into_view_if_needed()
                    page.evaluate(FRAMES)
                    card.screenshot(path=str(OUT / "screenshots/pages" / f"{route}-{item}.png"))
                page.evaluate("window.scrollTo(0,0)")
            if route=="threejs-animated-3d":
                record["sceneCount"]=page.locator("canvas.three-canvas").count()
                record["controls"]=page.evaluate(CONTROL_CONTRAST,".card-replay-button,#replay-all")
                # The compiled gallery is compared to the exact Vite output below;
                # both removed edge overlays are also checked in authored source.
                source=(ROOT / "skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js").read_text(encoding="utf-8")
                record["authoredEdgesGeometryCount"]=source.count("new THREE.EdgesGeometry")
                first=page.locator(".example-card").first
                before=first.get_attribute("data-replay-count")
                first.locator(".card-replay-button").click()
                record["replayWorks"]=first.get_attribute("data-replay-count")!=before
                first.screenshot(path=str(OUT / "screenshots/pages/threejs-first-card.png"))
            if route=="procedural-svg-animation":
                record["patternCount"]=page.locator(".pattern-card").count()
                page.locator(".family-browser>summary").click()
                record["controls"]=page.evaluate(CONTROL_CONTRAST,".family-tile,.family-count,.family-tile strong,.family-tile small,#replay-all,.metadata-list li,.signature,.card-controls .button")
                # Expanded counts are category fills, not drawing background.
                failures=[entry for entry in record["controls"] if not entry["passed"]]
                if failures:
                    findings.append({"severity":"style","kind":"control-contrast","page":route,"count":len(failures),"examples":failures})
                page.locator(".family-browser").screenshot(path=str(OUT / "screenshots/pages/procedural-family-counts.png"))
                page.locator(".family-browser>summary").click()
            if not route:
                record["cardCount"]=page.locator(".card").count()
                record["badges"]=page.evaluate(CONTROL_CONTRAST,".kind")
                record["borderCount"]=page.locator(".card").evaluate_all("es=>es.filter(e=>+getComputedStyle(e).borderTopWidth.replace('px','')>0).length")
            for width,height in ((1440,1050),(390,844)):
                page.set_viewport_size({"width":width,"height":height})
                page.evaluate("window.scrollTo(0,0)")
                page.evaluate(FRAMES)
                overflow=page.evaluate("Math.max(document.body.scrollWidth,document.documentElement.scrollWidth)-window.innerWidth")
                record["viewports"].append({"width":width,"horizontalOverflowPx":overflow})
                if overflow>1:
                    findings.append({"severity":"layout","kind":"horizontal-overflow","page":route or "catalog","width":width,"pixels":overflow})
                page.screenshot(path=str(OUT / "screenshots/pages" / f"{route or 'catalog'}-{width}.png"))
            if errors:
                findings.append({"severity":"error","kind":"page-error","page":route or "catalog","errors":errors})
            records.append(record)
            page.close()
        # Direct browser rendering of actual published SVGs, not source fixtures.
        for pattern in ("state-sequencer", "multistrata-field", "stagger-wave"):
            path=PAGES / f"examples/procedural-svg-animation/patterns/procedural-svg-{pattern}.svg"
            if not path.is_file():
                continue
            page=browser.new_page(viewport={"width":1000,"height":660})
            page.goto(BASE+"/"+path.relative_to(PAGES).as_posix())
            page.evaluate(FRAMES)
            report=page.evaluate(SVG_PAINT)
            report["page"]="procedural-svg-"+pattern
            if report["decorativeOutlineCount"] or report["nonBlackWhiteLabels"]:
                findings.append({"severity":"error","kind":"svg-paint","page":report["page"],"report":report})
            page.screenshot(path=str(OUT / "screenshots/pages" / f"procedural-svg-{pattern}.png"))
            records.append(report)
            page.close()
        browser.close()
    # Source preservation is independent of the renderer's computed paint.
    for skill,example in (("d3","d3-animated-svg-cs1"),("d3","d3-animated-svg-colorset2"),("d3","d3-logo-design"),("vectorize-art-patterns","vectorize-art-patterns"),("vectorize-art-patterns","vectorize-abstract-world-maps"),("procedural-svg-animation","procedural-svg-animation")):
        source=ROOT / f"skills/{skill}/assets/examples/{example}"
        for path in source.rglob("*"):
            if path.is_file() and path.suffix in {".svg",".json",".html",".css"}:
                source_copy(path,PAGES / "examples" / example / path.relative_to(source))
    source_copy(ROOT / "skills/d3/assets/examples/d3-animated-svg/solid-style.js",PAGES / "examples/d3-animated-svg/solid-style.js")
    source_copy(ROOT / "skills/d3/assets/examples/d3-animated-svg/gallery.js",PAGES / "examples/d3-animated-svg/gallery.js")
    source_copy(ROOT / "skills/d3/assets/examples/d3-animated-svg/composition-sheets.html",PAGES / "examples/d3-animated-svg/composition-sheets.html")
    three_build=ROOT / "skills/threejs-animated-3d/assets/examples/threejs-animated-3d/dist"
    for path in three_build.rglob("*"):
        if path.is_file():
            source_copy(path,PAGES / "examples/threejs-animated-3d" / path.relative_to(three_build))
    logo=(PAGES / "examples/d3-logo-design/index.html").read_text(encoding="utf-8")
    vendor=(ROOT / "skills/d3/assets/vendor/d3.v7.9.0.min.js").read_text(encoding="utf-8")
    vendor_preserved=vendor in logo
    if not vendor_preserved:
        findings.append({"severity":"error","kind":"logo-vendor-bytes"})
finally:
    server.shutdown()
summary={"date":"2026-10-03","method":"Playwright Microsoft Edge against a local HTTP server rooted in dist/pages; two animation frames before screenshots","pages":records,"copyCheckCount":len(copies),"copyMismatchCount":sum(not item["passed"] for item in copies),"logoVendorBytesPreserved":vendor_preserved,"findings":findings,"passed":not findings}
(OUT / "reviews/pages-review-20261003.json").write_text(json.dumps({**summary,"copyChecks":copies},indent=2)+"\n",encoding="utf-8")
summary["pages"]=[{**{key:value for key,value in record.items() if key not in {"controls","badges"}},**{key:{"checkCount":len(record[key]),"passedCount":sum(row["passed"] for row in record[key]),"failures":[row for row in record[key] if not row["passed"]]} for key in ("controls","badges") if key in record}} for record in records]
(EVIDENCE / "pages-review-20261003.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
