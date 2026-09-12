#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Verify original poster gallery navigation, responsive layout, and zoom controls."""

import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gallery",type=Path)
    parser.add_argument("--artifacts",type=Path,required=True)
    args=parser.parse_args();args.artifacts.mkdir(parents=True,exist_ok=True)
    checks=[]
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":1440,"height":1100},device_scale_factor=1)
        errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
        for width in (1440,390):
            page.set_viewport_size({"width":width,"height":1000})
            page.goto((args.gallery/"index.html").resolve().as_uri())
            page.wait_for_function("[...document.images].every(i=>i.complete&&i.naturalWidth>0)")
            state=page.evaluate("""()=>({cards:document.querySelectorAll('article[data-pattern-id]').length,ids:[...document.querySelectorAll('article')].map(a=>a.id),overflow:document.documentElement.scrollWidth>innerWidth+1})""")
            assert state["cards"]==3 and len(set(state["ids"]))==3 and not state["overflow"],state
            page.screenshot(path=str(args.artifacts/f"gallery-{width}.png"),full_page=True)
            checks.append({"width":width,**state})
        for name in ("aurelian-families","atlas-of-inquiry","five-regional-histories"):
            page.set_viewport_size({"width":1280,"height":1000})
            page.goto((args.gallery/f"{name}.html").resolve().as_uri());page.evaluate("document.fonts.ready")
            initial=page.locator("#paper").bounding_box()["width"]
            page.locator("#plus").click();zoom=page.locator("#paper").bounding_box()["width"]
            assert zoom>initial
            page.locator("#full").click();full=page.locator("#paper").bounding_box()["width"]
            assert full==1800
            image_sizes=page.evaluate("""()=>[...document.querySelectorAll('#paper svg svg')].map(s=>({declared:Number(s.getAttribute('width')),actual:s.getBoundingClientRect().width}))""")
            assert all(abs(s['actual']-s['declared'])<.1 for s in image_sizes),image_sizes
            page.locator("#fit").click();assert page.locator("#paper").bounding_box()["width"]==initial
            page.screenshot(path=str(args.artifacts/f"viewer-{name}.png"))
            # Capture a dense part from the actual SVG at full resolution.
            page.goto((args.gallery/f"{name}.svg").resolve().as_uri());page.evaluate("document.fonts.ready")
            page.set_viewport_size({"width":1800,"height":2700})
            page.screenshot(path=str(args.artifacts/f"detail-{name}.png"),clip={"x":600,"y":700,"width":1000,"height":650})
            checks.append({"viewer":name,"fit_width":initial,"zoom_width":zoom,"full_width":full,"embedded_images_checked":len(image_sizes)})
        assert not errors,errors
        browser.close()
    report={"status":"pass","checks":checks,"page_errors":errors}
    (args.artifacts/"gallery-audit.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))


if __name__=="__main__":
    main()
