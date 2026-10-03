#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect actual authored SVG paints, raw canvas pixels and hierarchy exports."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/compositions-colorset-audit/artifacts/reviews"
OUT.mkdir(parents=True, exist_ok=True)
PALETTES = json.loads((ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json").read_text())
def flatten(value):
    if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return {value.lower()}
    if isinstance(value, dict):
        return set().union(*(flatten(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(flatten(v) for v in value))
    return set()
COLORS = {name: flatten(value) for name, value in PALETTES["colorsets"].items()}
COLORS["colorset2"] |= COLORS["colorset1"]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
origin = f"http://127.0.0.1:{server.server_port}"
reports = []
PAINT_SCAN = r"""() => {
 const tokens=new Set();
 const add=s=>{for(const m of s.matchAll(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([.\d]+))?\)/g)) if(m[4]===undefined||Number(m[4])>0)tokens.add('#'+[m[1],m[2],m[3]].map(v=>Number(v).toString(16).padStart(2,'0')).join(''));};
 for(const e of document.querySelectorAll('svg *')) {const s=getComputedStyle(e);for(const p of ['fill','stroke','color','stopColor'])add(s[p]||'');}
 for(const c of document.querySelectorAll('canvas')) {const a=c.getContext('2d')?.getImageData(0,0,c.width,c.height).data;if(a)for(let i=0;i<a.length;i+=4)if(a[i+3])tokens.add('#'+[a[i],a[i+1],a[i+2]].map(v=>v.toString(16).padStart(2,'0')).join(''));}
 return [...tokens].sort();
}"""
def inspect(page, label, palette):
    tokens = page.evaluate(PAINT_SCAN)
    bad = sorted(set(tokens) - COLORS[palette])
    reports.append({"state": label, "palette": palette, "paintCount": len(tokens), "offPalette": bad})
    assert not bad, (label, bad)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1080}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    for filename in ("analytical.html", "radial.html", "organic.html", "index.html"):
        page.goto(f"{origin}/skills/hierarchy-lens/assets/examples/hierarchy-lens/{filename}")
        page.wait_for_function("document.documentElement.dataset.ready==='true'")
        keys = page.locator("#lenses button").evaluate_all("es=>es.map(e=>e.dataset.key)")
        for key in keys:
            page.locator(f'#lenses button[data-key="{key}"]').click()
            inspect(page, f"hierarchy/{filename}/{key}", "colorset2")
            # Exercise all numeric scales and both scopes through the public controls.
            numeric = page.locator("#scope").is_visible()
            if not numeric and filename != "analytical.html" and not page.locator("#drawer").is_visible():
                page.locator("#info").click()
                numeric = page.locator("#scope").is_visible()
            if numeric:
                scopes = page.locator("#scope option").evaluate_all("es=>es.filter(e=>!e.disabled).map(e=>e.value)")
                scales = page.locator("#scale option").evaluate_all("es=>es.map(e=>e.value)")
                for scope in scopes:
                    page.locator("#scope").select_option(scope)
                    for scale in scales:
                        page.locator("#scale").select_option(scale)
                        inspect(page, f"hierarchy/{filename}/{key}/{scope}/{scale}", "colorset2")
            svg = page.evaluate("(window.hierarchyLens || window.hierarchyPixels).exportSvg()")
            bad = sorted(set(re.findall(r"#[0-9a-fA-F]{6}\b", svg.lower())) - COLORS["colorset2"])
            reports.append({"state": f"hierarchy-export/{filename}/{key}", "palette": "colorset2", "offPalette": bad})
            assert not bad, (filename, key, bad)
            (OUT / f"hierarchy-{filename.removesuffix('.html')}-{key}.svg").write_text(svg, encoding="utf-8")
        page.screenshot(path=str(OUT / f"hierarchy-{filename}.png"))
    for name in ("inference-pulse", "heatwave-tree"):
        page.goto(f"{origin}/skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/{name}.svg")
        page.wait_for_function("typeof window.svgSync==='object'")
        api_name = "svgSync"
        scenarios = page.evaluate(f"window.{api_name}.getPlan().scenarios.map(s=>s.id)")
        for scenario in scenarios:
            page.evaluate(f"id=>window.{api_name}.applyScenario(id)", scenario)
            inspect(page, f"composition/{name}/{scenario}", "colorset1")
        page.screenshot(path=str(OUT / f"composition-{name}.png"))
    for name in ("aurelian-families", "atlas-of-inquiry", "five-regional-histories"):
        page.goto(f"{origin}/skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}.svg")
        inspect(page, f"poster/{name}", "colorset2")
        page.screenshot(path=str(OUT / f"poster-{name}.png"))
    page.goto(f"{origin}/skills/video/assets/examples/ai-concept-videos/index.html?autoplay=0")
    page.wait_for_function("typeof window.renderConceptFrame==='function'")
    concepts = page.evaluate("window.AI_CONCEPTS.map(c=>c.id)")
    for concept in concepts:
        for second in (0, 20, 40, 60, 80, 100, 119.5):
            page.evaluate("p=>window.renderConceptFrame(p[0],p[1])", [concept, second])
            inspect(page, f"video-gallery/{concept}/{second}", "colorset2")
    page.screenshot(path=str(OUT / "video-gallery.png"))
    page.goto(f"{origin}/evaluations/runs/colorset-hyperframes-explainer-20261002-3/workspace/output/project/index.html")
    page.wait_for_function("typeof window.explainer==='object'")
    duration = page.evaluate("window.explainer.brief.output.duration")
    for fraction in (0, 0.125, 0.25, 0.5, 0.75, 1):
        page.evaluate("t=>window.explainer.seek(t)", fraction * duration)
        inspect(page, f"hyperframes/starter/{fraction}", "colorset1")
    page.screenshot(path=str(OUT / "hyperframes-starter.png"))
    assert not errors, errors
    browser.close()
server.shutdown()
result = {"ok": True, "stateCount": len(reports), "pageErrors": errors, "checks": reports}
(OUT / "browser-palette-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ok": True, "states": len(reports), "report": str(OUT / "browser-palette-audit.json")}))
