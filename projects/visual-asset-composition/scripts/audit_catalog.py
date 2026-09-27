#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Measure published visual surfaces without changing authored geometry."""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import importlib.util
import json
import subprocess
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/visual-asset-composition/artifacts"
MEASURE = r"""() => {
  const visible = e => {const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0};
  const round = n => Math.round(n*100)/100;
  const name = e => e.dataset.patternId || e.dataset.exampleId || e.id || e.querySelector('h2,h3')?.textContent.trim() || e.className?.baseVal || String(e.className).slice(0,100) || e.tagName;
  const bounds = e => {const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {name:name(e),x:round(r.x),y:round(r.y+scrollY),width:round(r.width),height:round(r.height),padding:[s.paddingTop,s.paddingRight,s.paddingBottom,s.paddingLeft],fontSize:s.fontSize,overflowX:s.overflowX,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth}};
  const texts = [...document.querySelectorAll('svg text')].filter(visible).map(e=>{const m=e.getScreenCTM(),font=parseFloat(getComputedStyle(e).fontSize),size=m?font*Math.hypot(m.a,m.b):font;return {text:e.textContent.trim().slice(0,90),size:round(size),owner:name(e.closest('[data-pattern-id],article,section')||e.ownerSVGElement)}});
  const surfaces=[...document.querySelectorAll('main>svg,article svg,article canvas,.chart-stage,.viz-frame,.scene-stage,.stage,.studio-preview,.map-panel,.card-header,.card-head,.controls,.toolbar')].filter(visible).map(bounds);
  const cards=[...document.querySelectorAll('article,.chart-card,.scene-card,.logo-card,.pattern-card')].filter(visible).map(bounds);
  const images=[...document.images].filter(visible);
  const controls=[...document.querySelectorAll('button,select,input:not([type=hidden])')].filter(visible);
  const header=document.querySelector('main>header,body>header,.page-header,.hero,header');
  return {title:document.title,width:innerWidth,height:innerHeight,documentWidth:document.documentElement.scrollWidth,documentHeight:document.documentElement.scrollHeight,overflowX:Math.max(0,document.documentElement.scrollWidth-innerWidth),header:header?bounds(header):null,cards,surfaces,svgCount:document.querySelectorAll('svg').length,canvasCount:document.querySelectorAll('canvas').length,imageCount:images.length,brokenImages:images.filter(e=>!e.complete||e.naturalWidth===0).map(e=>e.getAttribute('src')),svgTextCount:texts.length,smallSvgText:texts.filter(t=>t.size<10),controlCount:controls.length,shortControls:controls.filter(e=>e.getBoundingClientRect().height<(matchMedia('(pointer:coarse)').matches?44:30)).map(bounds)};
}"""


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def sources() -> tuple[list[dict], list[dict]]:
    files = subprocess.check_output(["rg", "--files", "skills"], cwd=ROOT, text=True).splitlines()
    inventory = []
    for skill in sorted((ROOT / "skills").iterdir()):
        if not (skill / "SKILL.md").exists():
            continue
        owned = [Path(p) for p in files if Path(p).parts[1] == skill.name]
        inventory.append({"skill": skill.name, "files": len(owned), "templates": sum("templates" in p.parts for p in owned), "exampleFiles": sum("examples" in p.parts for p in owned), "visualSources": sum(p.suffix in {".html", ".svg", ".css", ".vue", ".mmd", ".puml"} for p in owned)})
    spec = importlib.util.spec_from_file_location("pages", ROOT / "scripts/build-pages.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pages = [{"id": "catalog", "path": "dist/pages/index.html"}]
    for key in module.EXAMPLE_SOURCES:
        path = ROOT / "dist/pages/examples" / key / "index.html"
        if path.exists() and key not in {"plantuml-colorset-renderer-base", "mermaid-max-elements", "plantuml-colorset-renderer-cs1"}:
            pages.append({"id": key, "path": path.relative_to(ROOT).as_posix()})
    for filename in ["analytical.html", "radial.html", "organic.html"]:
        path = ROOT / "dist/pages/examples/hierarchy-lens" / filename
        if path.exists():
            pages.append({"id": "hierarchy-" + path.stem, "path": path.relative_to(ROOT).as_posix()})
    return inventory, pages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    destination = ARTIFACTS / args.label
    destination.mkdir(parents=True, exist_ok=True)
    inventory, pages = sources()
    if args.only:
        pages = [p for p in pages if p["id"] in args.only]
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", args=["--enable-unsafe-swiftshader"])
            for item in pages:
                for width, height in [(1440, 1000), (390, 844)]:
                    context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 600, reduced_motion="reduce")
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    try:
                        page.goto(f"http://127.0.0.1:{server.server_port}/{item['path']}", wait_until="domcontentloaded", timeout=60000)
                        page.wait_for_timeout(1800)
                        # Load offscreen lazy images before classifying missing assets.
                        page.evaluate("""async () => {
                          const images = [...document.images];
                          for (const image of images) image.loading = 'eager';
                          await Promise.all(images.map(image => image.decode().catch(() => {})));
                        }""")
                        result = page.evaluate(MEASURE)
                        screenshot = destination / f"{item['id']}-{width}.png"
                        page.screenshot(path=str(screenshot), animations="disabled")
                        result.update(item, errors=errors, screenshot=screenshot.relative_to(ROOT).as_posix(), screenshotSha256=hashlib.sha256(screenshot.read_bytes()).hexdigest())
                    except Exception as error:
                        result = {**item, "width": width, "error": str(error), "errors": errors}
                    results.append(result)
                    context.close()
                    print(json.dumps({"page": item["id"], "width": width, "overflowX": result.get("overflowX"), "smallText": len(result.get("smallSvgText", [])), "errors": len(errors), "error": result.get("error")}), flush=True)
                    (destination / "audit.json").write_text(json.dumps({"inventory": inventory, "pages": results}, indent=2), encoding="utf-8")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f"Audited {len(results)} page/viewport combinations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
