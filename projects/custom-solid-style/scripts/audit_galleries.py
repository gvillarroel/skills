#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Inspect all published custom SVG cards plus the 24-scene Three.js fixture."""
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/custom-solid-style/artifacts"
REPORT_JS = r'''() => {
  const svgs = [...document.querySelectorAll('[data-example] svg')];
  const filled = [], violations = [], labels = [], alphaViolations=[];
  const cssHex = value => {const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value;};
  svgs.forEach(svg=>{
    const id=svg.dataset.patternId;
    svg.querySelectorAll('rect,circle,ellipse,polygon,path').forEach(shape=>{
      if(shape.closest('defs,mask,clipPath,pattern,[data-outline-tier="overflow"],[data-paint-mode="source"],[data-paint-mode="line-art"]'))return;
      const s=getComputedStyle(shape); if(s.fill==='none'||s.display==='none'||s.visibility==='hidden')return;
      if(shape.localName==='path'&&!/[zZ]\s*$/.test(shape.getAttribute('d')||''))return;
      filled.push({id,tag:shape.localName});
      if(!shape.closest('[data-opacity-role="semantic"],[data-opacity-role="reveal"]')){
        const lineage=[];for(let node=shape;node&&node!==svg.parentElement;node=node.parentElement)lineage.push(node);
        for(const node of lineage){const style=getComputedStyle(node),frames=node.getAnimations().flatMap(animation=>animation.effect?.getKeyframes()||[]);
          const reveals=!!node.querySelector('animate[attributeName="opacity"],animate[attributeName="fill-opacity"]')||frames.some(frame=>'opacity'in frame||'fillOpacity'in frame);
          if(!reveals&&((+style.opacity>0&&+style.opacity<.999)||node===shape&&(+style.fillOpacity>0&&+style.fillOpacity<.999)))alphaViolations.push({id,tag:node.localName,class:node.getAttribute('class'),opacity:style.opacity,fillOpacity:style.fillOpacity});
        }
      }
      if(s.stroke!=='none'&&+s.strokeOpacity>0&&+s.strokeWidth>0)violations.push({id,tag:shape.localName,fill:s.fill,stroke:s.stroke});
    });
    svg.querySelectorAll('text,tspan').forEach(t=>{const s=getComputedStyle(t), b=t.getBoundingClientRect();if(b.width&&b.height&&s.display!=='none'&&s.visibility!=='hidden')labels.push({id,fill:cssHex(s.fill),html:t.outerHTML.slice(0,500)});});
  });
  return {cardCount:svgs.length,solidStyleCount:svgs.filter(s=>s.dataset.fillStyle==='solid-first').length,filledCount:filled.length,outlineViolations:violations,staticAlphaViolations:alphaViolations,textPaints:[...new Set(labels.map(l=>l.fill))],textExceptions:labels.filter(l=>!['#000000','#ffffff'].includes(l.fill))};
}'''

results = []
with sync_playwright() as engine:
    browser = engine.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    for relative in ("d3-animated-svg-cs1", "d3-animated-svg-colorset2"):
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        source = ROOT / f"skills/d3/assets/examples/{relative}/index.html"
        page.goto(source.as_uri(), wait_until="domcontentloaded")
        page.wait_for_function("document.querySelectorAll('[data-example] svg[data-fill-style=\"solid-first\"]').length > 200", timeout=120000)
        page.wait_for_timeout(5000)
        result = page.evaluate(REPORT_JS)
        assert result["cardCount"] == result["solidStyleCount"] and result["cardCount"] >= 200, result
        assert not result["outlineViolations"], result["outlineViolations"][:8]
        assert not result["staticAlphaViolations"],result["staticAlphaViolations"][:8]
        category=page.locator('[data-example="category-burst"]')
        assert category.locator('circle[fill="none"],[filter]').count()==0
        assert category.locator('.category-burst-link').count()==8
        assert set(result["textPaints"]) <= {"#000000", "#ffffff"}, result["textExceptions"][:6]
        await_two_frames = "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
        page.evaluate(await_two_frames)
        for pattern in ("category-burst", "task-overlap", "moe-router-capacity", "speculative-decoding"):
            card = page.locator(f'[data-example="{pattern}"]')
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(250)
            page.evaluate(await_two_frames)
            card.screenshot(path=str(OUT / "screenshots" / f"{relative}-{pattern}.png"))
        result.update(gallery=relative, pageErrors=errors, passed=not errors)
        results.append(result)
    for skill, relative in (("procedural-svg-animation", "procedural-svg-animation"), ("vectorize-art-patterns", "vectorize-art-patterns"), ("vectorize-art-patterns", "vectorize-abstract-world-maps")):
        source = ROOT / f"skills/{skill}/assets/examples/{relative}/index.html"
        page.goto(source.as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(300)
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        page.screenshot(path=str(OUT / "screenshots" / f"{relative}-gallery.png"))
        record = {"gallery": relative, "passed": True}
        if skill == "vectorize-art-patterns":
            records = []
            for viewport in ({"width": 1440, "height": 1100}, {"width": 390, "height": 844}):
                page.set_viewport_size(viewport)
                page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
                borders = page.evaluate('''() => [...document.querySelectorAll('.masthead,.hero,.hero-stats,.hero-stats div,.method-grid,.controls,button,input,select,.artwork-card,.image-link,.card-data,.card-data div,.actions a,.empty-state,footer,.topbar,.palette span,.stats,.study,.preview')].filter(e=>{const s=getComputedStyle(e);return e.getBoundingClientRect().width&&['Top','Right','Bottom','Left'].some(side=>+s['border'+side+'Width'].replace('px','')>0&&s['border'+side+'Style']!=='none');}).map(e=>e.className||e.localName)''')
                assert not borders, {"gallery": relative, "viewport": viewport, "borders": borders}
                records.append({"viewport": viewport, "decorativeBorderCount": len(borders)})
            checked_paths = 0
            for path in source.parent.glob("svgs/*.svg"):
                for element in ET.parse(path).getroot().iter():
                    if element.tag.rsplit("}", 1)[-1] == "path" and element.get("fill") not in {"none", None}:
                        assert element.get("stroke") in {None, "none"}, {"path": str(path), "id": element.get("id")}
                        checked_paths += 1
            record.update(browserChecks=records, borderlessFilledPaths=checked_paths)
            page.screenshot(path=str(OUT / "screenshots" / f"{relative}-mobile.png"))
            page.set_viewport_size({"width": 1440, "height": 1100})
        results.append(record)
    browser.close()

report = {"passed": all(result["passed"] for result in results), "galleries": results}
(OUT / "data/gallery-style-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
