#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Review isolated outputs independently and bind evidence to final payloads."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/custom-solid-style/artifacts"
spec = importlib.util.spec_from_file_location("harness", ROOT / "scripts/run-pi-skill-eval.py")
HARNESS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(HARNESS)
SKILLS = ("d3", "threejs-animated-3d", "procedural-svg-animation", "svg-brief-design", "vectorize-art-patterns")
NS = "{http://www.w3.org/2000/svg}"


def current_payload(skill):
    snapshot = HARNESS.snapshot_tree(ROOT / "skills" / skill)
    snapshot = {key: value for key, value in snapshot.items() if not any(part in HARNESS.COPY_IGNORE for part in Path(key).parts) and not key.startswith("assets/examples/")}
    return {"fileCount": len(snapshot), "payloadSha256": HARNESS.snapshot_digest(snapshot)}


def invoke(arguments):
    result = subprocess.run(["uv", "run", "--script", *arguments], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


payloads = {skill: current_payload(skill) for skill in SKILLS}
records = []
with sync_playwright() as engine:
    browser = engine.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    for folder in sorted((ROOT / "evaluations/runs").glob("custom-solid-*-20261003-luna-*")):
        if not (folder / "evaluation-result.json").is_file():
            continue
        manifest = json.loads((folder / "run-manifest.json").read_text(encoding="utf-8"))
        skill = manifest["skill"]["name"]
        workspace = folder / "workspace"
        result = json.loads((folder / "evaluation-result.json").read_text(encoding="utf-8"))
        record = {"runId": folder.name, "skill": skill, "strictPassed": result["passed"], "matchesFinalPayload": manifest["skill"]["payloadSha256"] == payloads[skill]["payloadSha256"], "payloadSha256": manifest["skill"]["payloadSha256"], "artifactPassed": False}
        try:
            if skill == "d3":
                source = workspace / ("workflow.html" if "naturalistic" in folder.name else "flow.html")
                page.goto(source.as_uri())
                page.wait_for_timeout(1600)
                marks = page.locator("g.flow-node rect").evaluate_all("es=>es.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke}))")
                labels = page.locator(".flow-node-label").evaluate_all("es=>es.map(e=>({text:e.textContent,fill:getComputedStyle(e).fill}))")
                assert len(marks) == (6 if "naturalistic" in folder.name else 3)
                assert all(mark["stroke"] == "none" for mark in marks), marks
                assert len({mark["fill"] for mark in marks}) == len(marks)
                assert all(label["fill"] in {"rgb(255, 255, 255)", "rgb(0, 0, 0)"} for label in labels)
                contrast = page.locator("g.flow-node").evaluate_all('''es=>es.map(node=>{const fill=getComputedStyle(node.querySelector('rect')).fill;const channels=fill.match(/\\d+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);const lum=channels.reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);const expected=(lum+.05)/.05>=1.05/(lum+.05)?'rgb(0, 0, 0)':'rgb(255, 255, 255)';return [...node.querySelectorAll('text')].every(t=>getComputedStyle(t).fill===expected);})''')
                assert all(contrast), contrast
                vendor = (workspace / "skills/d3/assets/vendor/d3.v7.9.0.min.js").read_text(encoding="utf-8")
                embedded_vendor = page.locator("script#d3-runtime").text_content()
                record["vendorRuntimePreserved"] = embedded_vendor.endswith(vendor)
                if record["matchesFinalPayload"]:
                    assert record["vendorRuntimePreserved"], "Final artifact changed immutable D3 vendor bytes"
                record["marks"] = marks
                record["labels"] = labels
            elif skill == "threejs-animated-3d":
                source = workspace / ("roles.html" if "naturalistic" in folder.name else "orbit.html")
                page.goto(source.as_uri())
                page.wait_for_function("window.__threeRuntimeSceneReady === true")
                observed = page.evaluate("window.__threeRuntimeScene.inspect()")
                assert observed["tokenCount"] == (18 if "naturalistic" in folder.name else 5)
                assert observed["decorativeOutlineCount"] == 0
                assert all(value == "#ffffff" for value in observed["lightColors"])
                assert "new THREE.EdgesGeometry" not in source.read_text(encoding="utf-8")
                record["materials"] = observed["materialColors"]
            elif skill == "svg-brief-design":
                names = ("maroon.svg", "yellow.svg") if "naturalistic" in folder.name else ("flow.svg",)
                for name in names:
                    page.goto((workspace / name).as_uri())
                    marks = page.locator('rect[id^="node-"]').evaluate_all("es=>es.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke}))")
                    labels = page.locator("text").evaluate_all("es=>es.map(e=>getComputedStyle(e).fill)")
                    assert len(marks) == 3 and all(mark["stroke"] == "none" for mark in marks)
                    expected = "rgb(0, 0, 0)" if name == "yellow.svg" else "rgb(255, 255, 255)"
                    assert all(label == expected for label in labels), labels
                record["variants"] = list(names)
            elif skill == "procedural-svg-animation":
                names = ("clock.svg", "clock-static.svg") if "naturalistic" in folder.name else ("sequencer.svg",)
                invoke(["skills/procedural-svg-animation/scripts/validate_procedural_svg.py", *[str(workspace / name) for name in names], "--expect-palette", "colorset2", "--json"])
                for name in names:
                    root = ET.parse(workspace / name).getroot()
                    assert root.get("data-fill-style") == "solid-first"
                    assert root.get("data-pattern-id") == "procedural-svg-state-sequencer"
                    assert all(element.get("stroke", "none") == "none" for element in root.iter(NS + "circle") if element.get("fill") not in {None, "none"})
                    page.goto((workspace / name).as_uri())
                    for timestamp in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5):
                        page.evaluate("time=>document.querySelector('svg').setCurrentTime(time)", timestamp)
                        page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
                        contrast = page.evaluate(r'''() => {
                          const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value};
                          const rgb=color=>[1,3,5].map(i=>parseInt(color.slice(i,i+2),16));
                          const lum=channels=>channels.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
                          return [...document.querySelectorAll('.psvg-node-label')].filter(t=>t.getBoundingClientRect().width).map(t=>{
                            const tx=+t.getAttribute('x'),ty=+t.getAttribute('y')-3;
                            const circle=[...t.parentNode.querySelectorAll(':scope > circle')].find(c=>Math.abs(+c.getAttribute('cx')-tx)<1&&Math.abs(+c.getAttribute('cy')-ty)<6);
                            if(!circle)return {text:t.textContent,error:'missing circle'};
                            const cs=getComputedStyle(circle),alpha=+cs.opacity*(+cs.fillOpacity),base=rgb(hex(cs.fill));
                            const level=lum(base.map(v=>Math.round(v*alpha+255*(1-alpha))));
                            const expected=(level+.05)/.05>=1.05/(level+.05)?'#000000':'#ffffff';
                            return {text:t.textContent,expected,actual:hex(getComputedStyle(t).fill)};
                          });
                        }''')
                        assert contrast and all(item.get("expected") == item.get("actual") for item in contrast), {"time": timestamp, "contrast": contrast}
                record["variants"] = list(names)
            else:
                names = ("artwork-cs1.svg", "artwork-cs2.svg") if "naturalistic" in folder.name else ("bailly.svg",)
                geometry = []
                for name in names:
                    active = "colorset2" if "cs2" in name else "colorset1"
                    invoke(["skills/vectorize-art-patterns/scripts/validate_art_svg.py", str(workspace / name), "--report", str(workspace / Path(name).with_suffix(".json")), "--expected-colorset", active])
                    root = ET.parse(workspace / name).getroot()
                    paths = list(root.iter(NS + "path"))
                    assert paths and all(path.get("stroke") in {None, "none"} for path in paths)
                    geometry.append([path.get("d") for path in paths])
                if len(geometry) == 2:
                    assert geometry[0] == geometry[1]
                record["variants"] = list(names)
            record["artifactPassed"] = True
        except Exception as error:
            record["artifactError"] = str(error)
        records.append(record)
    browser.close()
summary = {"finalPayloads": payloads, "attempts": records, "strictPasses": sum(record["strictPassed"] for record in records), "artifactPasses": sum(record["artifactPassed"] for record in records), "jointFinalPasses": sum(record["strictPassed"] and record["matchesFinalPayload"] and record["artifactPassed"] for record in records)}
(OUT / "data/pi-artifact-review.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key != "attempts"}, indent=2))
for record in records:
    print(json.dumps({key: value for key, value in record.items() if key not in {"materials", "marks", "labels", "variants"}}))
