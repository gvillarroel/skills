#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52", "pillow>=11"]
# ///
"""Independently verify paint defaults, palette exhaustion and browser rendering."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/custom-solid-style/artifacts"
OUT.mkdir(parents=True, exist_ok=True)


def module(relative):
    path = ROOT / relative
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(*arguments):
    subprocess.run(["uv", "run", "--script", *arguments], cwd=ROOT, check=True, capture_output=True, text=True)


adapter = module("skills/d3/scripts/colorset_adapter.py")
contract = json.loads(adapter.CONTRACT.read_text(encoding="utf-8"))["colorsets"]
checks = []
with sync_playwright() as engine:
    browser = engine.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1100, "height": 740})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    for active in ("colorset1", "colorset2"):
        source = '''<html><body><svg viewBox="0 0 560 200" width="840"><rect width="560" height="200" fill="#ffffff"/>
<g><rect id="dark" x="20" y="40" width="120" height="70" fill="#ffccd5" stroke="#9e1b32" stroke-width="2"/><text x="80" y="82" text-anchor="middle">Dark</text></g>
<g><rect id="light" x="180" y="40" width="120" height="70" fill="#f1c319" stroke="#333e48" stroke-width="2"/><text x="240" y="82" text-anchor="middle">Light</text></g>
<path id="connector" d="M140 75 L180 75" fill="none" stroke="#333e48"/><circle id="ring" cx="350" cy="75" r="25" fill="none" stroke="#333e48"/>
<g data-outline-tier="overflow"><rect id="overflow" x="400" y="40" width="120" height="70" fill="#e7e7e7" stroke="#333e48"/></g>
</svg></body></html>'''
        html = adapter.adapt_artifact(source, active)
        path = OUT / "data" / f"test-{active}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        page.goto(path.as_uri())
        page.wait_for_timeout(200)
        observed = page.evaluate('''() => {
          const paint=id=>{const style=getComputedStyle(document.getElementById(id));return {fill:style.fill,stroke:style.stroke}};
          return {dark:paint('dark'),light:paint('light'),connector:paint('connector'),ring:paint('ring'),overflow:paint('overflow'),texts:[...document.querySelectorAll('text')].map(t=>getComputedStyle(t).fill),
          allocation: Object.keys(D3_SOLID_PALETTES).map(cs=>{const p=D3_SOLID_PALETTES[cs];const count=p.allowed.filter(c=>c!=='#ffffff').length;return {cs,count,styles:Array.from({length:count+2},(_,i)=>D3SolidStyle.categoryStyle(i,cs,'#ffffff'))}})};
        }''')
        assert observed["dark"]["stroke"] == observed["light"]["stroke"] == "none", observed
        assert observed["dark"]["fill"] == "rgb(158, 27, 50)", observed
        assert observed["connector"]["stroke"] != "none" and observed["ring"]["stroke"] != "none", observed
        assert observed["overflow"]["stroke"] != "none", observed
        assert observed["texts"][0] == "rgb(255, 255, 255)", observed
        if active == "colorset2":
            assert observed["texts"][1] == "rgb(0, 0, 0)", observed
        for item in observed["allocation"]:
            count = item["count"]
            assert len({style["fill"] for style in item["styles"][:count]}) == count
            assert all(style["stroke"] == "none" for style in item["styles"][:count])
            assert all(style["stroke"] != "none" for style in item["styles"][count:])
        page.screenshot(path=str(OUT / "screenshots" / f"d3-solid-{active}.png"))
        checks.append({"route": "d3-runtime", "colorset": active, "passed": True, **observed})

    run("skills/d3/scripts/build_contract_artifact.py", "--kind", "flow", "--output", str(OUT / "data/flow.html"), "--decision-output", str(OUT / "data/flow.json"), "--title", "Delivery workflow", "--description", "Source to publish", "--route", "flow", "--colorset", "colorset2", "--pattern-id", "d3-delivery-workflow", "--svg-id", "workflow", "--reason", "Stages and transfer", "--flow-node", "Capture", "--flow-node", "Review", "--flow-node", "Publish", "--link", "Capture->Review", "--link", "Review->Publish", "--link-value", "8", "--link-value", "6", "--force")
    page.goto((OUT / "data/flow.html").as_uri())
    page.wait_for_timeout(1200)
    marks = page.locator("g.flow-node rect").evaluate_all("elements=>elements.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke}))")
    assert len(marks) == 3 and all(mark["stroke"] == "none" for mark in marks), marks
    assert len({mark["fill"] for mark in marks}) == 3, marks
    page.screenshot(path=str(OUT / "screenshots/d3-flow.png"))
    checks.append({"route": "d3-contract-flow", "passed": True, "marks": marks})

    category = module("skills/d3/scripts/build_category_burst.py")
    for active in ("colorset1", "colorset2"):
        output = OUT / "data" / f"category-burst-{active}.html"
        output.write_text(category.build_html(colorset=active), encoding="utf-8")
        page.goto(output.as_uri())
        page.wait_for_timeout(3500)
        category_marks = page.locator('.category-burst-root>circle,.category-burst-node>circle').evaluate_all("es=>es.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke}))")
        assert len(category_marks) == len({mark["fill"] for mark in category_marks}) == 9,category_marks
        assert all(mark["stroke"] == "none" for mark in category_marks),category_marks
        assert page.locator('circle[fill="none"],[filter]').count() == 0
        assert page.locator('.category-burst-link[fill="none"]').count() == 8
        page.evaluate("()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
        page.screenshot(path=str(OUT / "screenshots" / f"category-burst-{active}.png"))
        checks.append({"route":"category-burst-borderless","colorset":active,"passed":True,"marks":category_marks,"preservedSpokes":8})

    run("skills/threejs-animated-3d/scripts/build_standalone_threejs.py", str(OUT / "data/orbit.html"), "--colorset", "colorset2", "--token-count", "24", "--force")
    page.goto((OUT / "data/orbit.html").as_uri())
    page.wait_for_function("window.__threeRuntimeSceneReady === true")
    observed = page.evaluate("window.__threeRuntimeScene.inspect()")
    assert observed["decorativeOutlineCount"] == 0
    assert len(set(observed["materialColors"])) == 25, observed["materialColors"]
    assert set(observed["materialColors"]) <= set(contract["colorset2"]["allowed"])
    page.screenshot(path=str(OUT / "screenshots/threejs-orbit.png"))
    checks.append({"route": "threejs-orbit-24", "passed": True, "materials": observed["materialColors"]})
    browser.close()
    assert not errors, errors

scaffold = module("skills/svg-brief-design/scripts/scaffold.py")
for active in ("colorset1", "colorset2"):
    for color in contract[active]["allowed"]:
        recipe = scaffold.defaults("flow")
        recipe["style"].update(colorset=active, color=color)
        root = ET.fromstring(scaffold.build(recipe))
        rectangles = list(root.iter("{http://www.w3.org/2000/svg}rect"))
        labels = list(root.iter("{http://www.w3.org/2000/svg}text"))
        assert all(rect.get("stroke") == "none" for rect in rectangles)
        assert all(label.get("fill") == contract[active]["textOnFill"][color] for label in labels)
checks.append({"route": "svg-scaffold-all-token-contrast", "passed": True, "tokenCount": sum(len(p["allowed"]) for p in contract.values())})
proc = module("skills/procedural-svg-animation/scripts/solid_style.py")
for active in ("colorset1", "colorset2"):
    source = '<svg xmlns="http://www.w3.org/2000/svg"><g><rect x="0" y="0" width="100" height="60" fill="#ffccd5" stroke="#9e1b32"/><text x="50" y="30">Stage</text><path d="M100 30 L130 30" fill="none" stroke="#333e48"/></g></svg>'
    root = ET.fromstring(proc.finalize_svg(source, {"surface": "#ffffff"}))
    assert next(root.iter("{http://www.w3.org/2000/svg}rect")).get("stroke") == "none"
    assert next(root.iter("{http://www.w3.org/2000/svg}text")).get("fill") == "#ffffff"
    assert next(root.iter("{http://www.w3.org/2000/svg}path")).get("stroke") == "#333e48"
checks.append({"route": "procedural-finalizer", "passed": True})
assert (ROOT / "skills/d3/assets/templates/solid-style.js").read_bytes() == (ROOT / "skills/d3/assets/examples/d3-animated-svg/solid-style.js").read_bytes()
result = {"passed": all(item["passed"] for item in checks), "checks": checks}
(OUT / "data/deterministic-style-check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
