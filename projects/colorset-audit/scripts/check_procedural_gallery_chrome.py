#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect full published procedural chrome at default, hover and focus states."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/colorset-audit/artifacts"
GALLERY = ROOT / "skills/procedural-svg-animation/assets/examples/procedural-svg-animation"
ALLOWED = json.loads((ROOT / "skills/procedural-svg-animation/assets/palettes/colorsets.json").read_text())["colorsets"]["colorset1"]["allowed"]
assert "color-mix(" not in (GALLERY / "gallery.css").read_text()
INSPECT = """allowed => {
 const known=new Set(allowed), failures=[], colors=new Set(); let checked=0;
 for(const node of document.querySelectorAll('*')) {
  if(['script','style','object','iframe','img','option','title','desc','metadata'].includes(node.localName))continue;
  const box=node.getBoundingClientRect(); if(box.width<=0||box.height<=0)continue;
  const style=getComputedStyle(node); if(style.display==='none'||style.visibility==='hidden')continue;
  checked++;
  for(const prop of ['color','background-color','border-top-color','border-right-color','border-bottom-color','border-left-color','outline-color','text-decoration-color','box-shadow','text-shadow','background-image']) {
   for(const match of style.getPropertyValue(prop).matchAll(/rgba?\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)(?:\\s*,\\s*([.\\d]+))?\\s*\\)/g)) {
    if(match[4]!==undefined && Number(match[4])===0)continue;
    const color='#'+[match[1],match[2],match[3]].map(v=>Number(v).toString(16).padStart(2,'0')).join('');
    colors.add(color); if(!known.has(color))failures.push({node:node.id||node.className||node.localName,prop,color});
   }
   if(/(?:color-mix|oklch|oklab|color\\()/.test(style.getPropertyValue(prop)))failures.push({node:node.id||node.localName,prop,value:style.getPropertyValue(prop)});
  }
 }
 return {checkedElements:checked,colors:[...colors].sort(),failures};
}"""
results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    for width, height in ((1440, 1100), (390, 844)):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((GALLERY / "index.html").as_uri(), wait_until="load")
        page.wait_for_timeout(250)
        page.locator(".family-browser").evaluate("node=>node.open=true")
        for state in ("default", "family-hover", "family-focus", "button-hover", "button-focus", "input-focus", "select-focus", "link-focus"):
            if state == "family-hover": page.locator(".family-tile").first.hover()
            elif state == "family-focus": page.locator(".family-tile").first.focus()
            elif state == "button-hover": page.locator("#replay-all").hover()
            elif state == "button-focus": page.locator("#pause-all").focus()
            elif state == "input-focus": page.locator("#pattern-search").focus()
            elif state == "select-focus": page.locator("#family-filter").focus()
            elif state == "link-focus": page.locator(".manifest-link").focus()
            if state.endswith("-focus"):
                page.keyboard.press("Shift+Tab")
                page.keyboard.press("Tab")
                outline = page.evaluate("getComputedStyle(document.activeElement).outlineColor")
                assert outline == "rgb(232, 0, 42)", (width, state, outline)
            page.wait_for_timeout(50)
            report = page.evaluate(INSPECT, ALLOWED)
            assert not report["failures"], (width, state, report["failures"][:15])
            results.append({"viewport": [width, height], "state": state, **report})
        for index in range(page.locator(".family-tile").count()):
            tile = page.locator(".family-tile").nth(index)
            tile.hover()
            actual = tile.evaluate("node=>getComputedStyle(node).backgroundColor")
            assert actual == "rgb(54, 54, 54)", actual
        assert not errors, errors
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
        page.screenshot(path=str(OUT / f"images/procedural-gallery-chrome-{width}.png"), full_page=False)
        page.close()
    browser.close()
report_path = OUT / "data/procedural-gallery-chrome.json"
report_path.write_text(json.dumps({"ok": True, "states": len(results), "familyHoverChecks": 22, "results": results}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ok": True, "states": len(results), "familyHoverChecks": 22, "report": str(report_path)}))
