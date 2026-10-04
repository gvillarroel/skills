#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "Pillow>=11"]
# ///
"""Check dense-overlap data, actual geometry, composited pixels and portable export."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from PIL import Image
from playwright.sync_api import sync_playwright

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import build_dense_task_overlap as builder
import check_palette_contract
import check_self_contained_html
import layout_task_overlap_labels as generator

ARTIFACTS: Path
PAYLOAD: dict
STATES = []
REGION_PAINT = {
    "colorset1": ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c", "#b5b5b5", "#cfcfcf", "#e7e7e7"],
    "colorset2": ["#007298", "#e77204", "#45842a", "#9e1b32", "#652f6c", "#98700c", "#004d66", "#294d19", "#994a00"],
}

INSPECT = r"""options => {
const svg=document.querySelector('svg'), data=options.layout, findings=[];
const parse=v=>{const m=v.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?m.slice(1).map(Number):null;};
const hex=v=>'#'+v.map(n=>Math.round(n).toString(16).padStart(2,'0')).join('');
const luminance=v=>v.map(n=>n/255).map(n=>n<=.04045?n/12.92:((n+.055)/1.055)**2.4).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);
const alpha=el=>{let value=+getComputedStyle(el).fillOpacity;for(let node=el;node&&node!==svg.parentElement;node=node.parentElement)value*=+getComputedStyle(node).opacity;return value;};
const near=(a,b)=>Math.abs(a-b)<.0001;
const regions=[...svg.querySelectorAll('circle.overlap-circle')], dots=[...svg.querySelectorAll('circle.task-dot')], labels=[...svg.querySelectorAll('.task-label-group')], leaders=[...svg.querySelectorAll('.task-leader')];
if(regions.length!==9||dots.length!==100||labels.length!==100||leaders.length!==100)findings.push('Actual item counts differ from9regions/100tasks');
const radii=[];
regions.forEach((region,index)=>{
  const expected=data.circles[index], s=getComputedStyle(region), radius=region.r.baseVal.value;radii.push(radius);
  if(region.dataset.setId!==expected.id||!near(region.cx.baseVal.value,expected.cx)||!near(region.cy.baseVal.value,expected.cy)||!near(radius,expected.r)||!near(region.getBBox().width/2,expected.r))findings.push('Actual region data or painted/base radius changed');
  if(radius<=0||region.dataset.opacityRole!=='semantic'||!near(alpha(region),.28)||s.stroke!=='none'||hex(parse(s.fill))!==options.regionPaint[index])findings.push('Actual region paint is incorrect');
});
dots.forEach((dot,index)=>{
  const expected=data.tasks[index], label=labels[index], face=label.querySelector('rect'), text=label.querySelector('text'), leader=leaders[index];radii.push(dot.r.baseVal.value);
  if(dot.dataset.taskId!==expected.id||dot.dataset.memberships!==expected.memberships.join(' ')||+dot.dataset.membershipCount!==expected.membershipCount||text.textContent!==expected.label) findings.push('Task identity/membership/label changed');
  if(!near(dot.cx.baseVal.value,expected.x)||!near(dot.cy.baseVal.value,expected.y)||!near(dot.r.baseVal.value,data.dotRadius)||!near(dot.getBBox().width/2,data.dotRadius))findings.push('Actual task geometry/base radius changed');
  const endpointX=expected.labelEdgeX??(expected.labelX<expected.x?expected.labelX+expected.labelWidth:expected.labelX),endpointY=expected.labelEdgeY??expected.labelY+expected.labelHeight/2;
  if(!near(leader.x1.baseVal.value,expected.x)||!near(leader.y1.baseVal.value,expected.y)||!near(leader.x2.baseVal.value,endpointX)||!near(leader.y2.baseVal.value,endpointY))findings.push('Leader endpoints changed');
  for(const [key,field] of [['x','labelX'],['y','labelY'],['width','labelWidth'],['height','labelHeight']])if(!near(face[key].baseVal.value,expected[field]))findings.push('Task label face geometry changed');
  if(!near(alpha(dot),1)||!near(alpha(face),1)||getComputedStyle(dot).stroke!=='none'||getComputedStyle(face).stroke!=='none'||label.dataset.textBacking!=='.task-label-bg')findings.push('Task faces lost opaque borderless paint/backing');
});
const paints=[...svg.querySelectorAll('rect,circle')], textItems=[...svg.querySelectorAll('text')];
function inside(element,point){return element.isPointInFill(point.matrixTransform(element.getScreenCTM().inverse()));}
for(const text of textItems){
  const b=text.getBoundingClientRect(), p=new DOMPoint(b.x+b.width/2,b.y+b.height/2);let color=[255,255,255];
  for(const shape of paints){const s=getComputedStyle(shape),fill=parse(s.fill);if(fill&&inside(shape,p)){const a=alpha(shape);color=fill.map((n,i)=>n*a+color[i]*(1-a));}}
  const l=luminance(color),expected=(l+.05)/.05>=1.05/(l+.05)?'#000000':'#ffffff';
  if(hex(parse(getComputedStyle(text).fill))!==expected||getComputedStyle(text).stroke!=='none')findings.push('Label ink is not exact maximum-contrast black/white');
}
const captionCollisions=[];
for(const caption of svg.querySelectorAll('.caption'))for(const label of labels){
  const a=caption.getBoundingClientRect(),b=label.getBoundingClientRect();
  if(Math.min(a.right,b.right)-Math.max(a.x,b.x)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>.5)captionCollisions.push([caption.textContent,label.dataset.taskId]);
}
if(captionCollisions.length)findings.push('Actual caption/task label collision');
const lines=[...svg.querySelectorAll('line')], samples=[], seen=new Set(), clip=(svg.closest('.viz-frame')||svg).getBoundingClientRect();
for(let y=35;y<410;y+=5)for(let x=195;x<700;x+=5){
  const p=new DOMPoint(x,y).matrixTransform(svg.getScreenCTM());
  if(options.visibleOnly&&(p.x<Math.max(clip.x,0)+4||p.x>Math.min(clip.right,innerWidth)-4||p.y<Math.max(clip.y,0)+4||p.y>Math.min(clip.bottom,innerHeight)-4))continue;
  const matches=regions.filter(r=>inside(r,p));
  if(!matches.length||matches.length>3||seen.has(matches.length))continue;
  if(matches.some(r=>Math.abs(Math.hypot(x-r.cx.baseVal.value,y-r.cy.baseVal.value)-r.r.baseVal.value)<5))continue;
  if(dots.some(d=>Math.hypot(x-d.cx.baseVal.value,y-d.cy.baseVal.value)<6))continue;
  if(lines.some(line=>{const a=line.x1.baseVal.value,b=line.y1.baseVal.value,c=line.x2.baseVal.value,d=line.y2.baseVal.value,t=Math.max(0,Math.min(1,((x-a)*(c-a)+(y-b)*(d-b))/((c-a)**2+(d-b)**2)));return Math.hypot(x-a-t*(c-a),y-b-t*(d-b))<4;}))continue;
  if(textItems.some(text=>{const b=text.getBoundingClientRect();return p.x>b.x-3&&p.x<b.right+3&&p.y>b.y-3&&p.y<b.bottom+3;}))continue;
  let color=[255,255,255];for(const r of matches){const fill=parse(getComputedStyle(r).fill);color=fill.map((n,i)=>n*.28+color[i]*.72);}
  samples.push({multiplicity:matches.length,x:p.x,y:p.y,expected:color});seen.add(matches.length);
}
if(![1,2,3].every(n=>seen.has(n)))findings.push('Missing unobstructed single/double/triple intersection samples');
return {findings,radii,samples,captionCollisions,overflow:document.documentElement.scrollWidth>innerWidth+2,
  patternId:svg.dataset.patternId,colorset:svg.dataset.colorset,rootId:svg.id,title:svg.querySelector('title')?.textContent,description:svg.querySelector('desc')?.textContent,
  payloadMatches:!window.D3_TASK_OVERLAP_LAYOUTS||JSON.stringify(window.D3_TASK_OVERLAP_LAYOUTS.saturated)===JSON.stringify(data)};
}"""


class DenseOverlapBuilderTests(unittest.TestCase):
    def test_deterministic_excerpt_offline_runtime_and_static_contracts(self):
        for colorset in REGION_PAINT:
            document = builder.build_document(PAYLOAD, colorset=colorset)
            self.assertEqual(document, builder.build_document(PAYLOAD, colorset=colorset))
            self.assertIn(f'<script id="d3-runtime">{builder.VENDOR.read_text(encoding="utf-8")}</script>', document)
            self.assertIn("function renderAsymmetricTaskOverlapSaturated()", document)
            artifact = ARTIFACTS / colorset / "dense-overlap.html"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(document, encoding="utf-8")
            self.assertEqual(check_self_contained_html.check_file(artifact), [])
            self.assertTrue(check_palette_contract.validate_artifact(artifact, colorset=colorset)["ok"])

    def test_invalid_layout_and_executable_additions_are_rejected(self):
        for mutation in ["radius", "count", "membership", "duplicate", "geometry"]:
            payload = deepcopy(PAYLOAD)
            data = payload["saturated"]
            if mutation == "radius": data["circles"][0]["r"] = 0
            elif mutation == "count": data["tasks"].pop()
            elif mutation == "membership": data["tasks"][0]["memberships"] = ["missing"]
            elif mutation == "duplicate": data["tasks"][1]["id"] = data["tasks"][0]["id"]
            else: data["tasks"][0]["x"] = float("nan")
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): builder.validate_layout(payload)
        bad = ARTIFACTS / "executable-layout.js"
        bad.write_text("window.D3_TASK_OVERLAP_LAYOUTS = {}; window.__unsafe = true;", encoding="utf-8")
        with self.assertRaises(ValueError): builder.load_layout(bad)
        layout = ARTIFACTS / "task-overlap-layouts.js"
        with patch.object(sys, "argv", ["build_dense_task_overlap.py", "--layout", str(layout), "--output", str(SKILL_ROOT / "rejected-overlap.html")]), redirect_stderr(StringIO()):
            self.assertEqual(builder.main(), 1)
        self.assertFalse((SKILL_ROOT / "rejected-overlap.html").exists())

    def test_browser_replay_reduced_motion_geometry_pixels_and_export(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {"channel": "msedge"}))
            for colorset in REGION_PAINT:
                html = ARTIFACTS / colorset / "dense-overlap.html"
                html.parent.mkdir(parents=True, exist_ok=True)
                html.write_text(builder.build_document(PAYLOAD, colorset=colorset), encoding="utf-8")
                svg = html.with_suffix(".svg")
                subprocess.run(["uv", "run", "--script", str(SKILL_ROOT / "scripts/render_d3_svg.py"), str(html), "--output", str(svg), "--viewport", "1440x1100", "--wait-ms", "650"], check=True)
                self.assertTrue(check_palette_contract.validate_artifact(svg, colorset=colorset, require_extended=colorset == "colorset2")["ok"])
                for extension in ["html", "svg"]:
                    for width in [1440, 390]:
                        for motion in ["no-preference", "reduce"]:
                            context = browser.new_context(viewport={"width": width, "height": 1100}, reduced_motion=motion)
                            page = context.new_page()
                            errors, network = [], []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http:", "https:")) else None)
                            page.goto(html.with_suffix("." + extension).as_uri())
                            # Construction must already have all final radius attributes.
                            self.assertEqual(page.locator('.overlap-circle[r="0"],.task-dot[r="0"]').count(), 0)
                            for replay in range(3 if extension == "html" else 1):
                                if replay:
                                    page.get_by_role("button", name="Replay").click()
                                    self.assertEqual(page.locator('.overlap-circle[r="0"],.task-dot[r="0"]').count(), 0)
                                if extension == "html" and width == 390:
                                    page.locator('.viz-frame').evaluate('element=>element.scrollLeft=(element.scrollWidth-element.clientWidth)/2')
                                page.wait_for_timeout(650)
                                result = page.evaluate(INSPECT, dict(layout=PAYLOAD["saturated"], regionPaint=REGION_PAINT[colorset], visibleOnly=extension == "html" and width == 390))
                                self.assertEqual(errors + network + result["findings"], [])
                                self.assertEqual(len(result["radii"]), 109)
                                self.assertTrue(all(radius > 0 for radius in result["radii"]))
                                self.assertTrue(result["payloadMatches"])
                                self.assertEqual(result["rootId"], "task-overlap-dense")
                                self.assertEqual(result["colorset"], colorset)
                                self.assertEqual(result["patternId"], "d3-task-overlap-dense-cs1" if colorset == "colorset1" else "d3-task-overlap-dense-cs2")
                                self.assertTrue(result["title"] and result["description"])
                                if extension == "html": self.assertFalse(result["overflow"])
                                name = f"{extension}-{width}-{motion}-{replay}"
                                png = html.parent / f"{name}.png"
                                capture_box = page.locator('svg').bounding_box() if extension == "svg" else {"x": 0, "y": 0}
                                if extension == "svg": page.locator('svg').screenshot(path=str(png))
                                else: page.screenshot(path=str(png), full_page=False)
                                image = Image.open(png).convert("RGB")
                                for sample in result["samples"]:
                                    pixel = image.getpixel((round(sample["x"] - capture_box["x"]), round(sample["y"] - capture_box["y"])))
                                    sample["actual"] = list(pixel)
                                    sample["error"] = max(abs(a-b) for a, b in zip(pixel, sample["expected"]))
                                    self.assertLessEqual(sample["error"], 5)
                                STATES.append(dict(colorset=colorset, format=extension, width=width, motion=motion, replay=replay, samples=result["samples"], actualRadiusCount=109, captionCollisions=result["captionCollisions"], passed=True))
                            context.close()
            browser.close()


def main():
    global ARTIFACTS, PAYLOAD
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    ARTIFACTS = args.artifacts.resolve()
    if ARTIFACTS.is_relative_to(SKILL_ROOT): parser.error("Artifacts must be outside the skill resource")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    PAYLOAD = generator.build_payload(generator.SEED, 100)
    generator.write_js(PAYLOAD, ARTIFACTS / "task-overlap-layouts.js")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DenseOverlapBuilderTests))
    (ARTIFACTS / "test-report.json").write_text(json.dumps(dict(passed=result.wasSuccessful(), testsRun=result.testsRun, states=STATES), indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__": raise SystemExit(main())
