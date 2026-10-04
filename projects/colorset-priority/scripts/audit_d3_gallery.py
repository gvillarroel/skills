#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "pillow>=11.0.0"]
# ///
"""Audit actual local or published D3 CS1 gallery paint, geometry, text and arrows."""

from __future__ import annotations

import argparse
from io import BytesIO
import json
import math
from pathlib import Path
import re

from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SITE = "https://gvillarroel.github.io/skills/"
EXPECTED = ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c",
            "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7", "#1c1c1c",
            "#000000", "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]
IDS = ["treemap", "circle-pack", "radial-hierarchy", "task-overlap-dense", "streamgraph", "voronoi",
       "icicle", "chord", "sunburst", "mirrored-beeswarm", "flowchart-dag", "state-machine", "er-schema",
       "tangled-tree", "tanglegram", "task-overlap", "venn-3", "venn-5", "venn-7",
       "overlap-3-rosette", "overlap-5-rosette", "overlap-7-flower", "overlap-3-chain", "overlap-5-cluster", "overlap-7-bridge"]


def ring(ids: list[str], center: tuple[int, int], radius: int, circle_radius: int) -> list[tuple]:
    return [(identity, center[0] + math.cos(-math.pi / 2 + index * math.tau / len(ids)) * radius,
             center[1] + math.sin(-math.pi / 2 + index * math.tau / len(ids)) * radius, circle_radius)
            for index, identity in enumerate(ids)]


# Independent fixture identities and geometry, not values derived from rendered paint.
VENN = {
    "venn-3": (.34, [("prompt", 232, 174, 92), ("data", 328, 174, 92), ("model", 280, 252, 92)]),
    "venn-5": (.3, ring(["data", "model", "eval", "product", "policy"], (280, 210), 64, 98)),
    "venn-7": (.25, ring(["prompting", "retrieval", "memory", "tooling", "evals", "safety", "product"], (280, 206), 75, 85)),
    "overlap-3-rosette": (.33, ring(["syntax", "semantics", "context"], (280, 210), 56, 108)),
    "overlap-5-rosette": (.3, ring(["product", "research", "infra", "design", "risk"], (280, 210), 66, 96)),
    "overlap-7-flower": (.27, [("core", 280, 210, 82)] + ring(["input", "embed", "attend", "route", "decode", "eval"], (280, 210), 82, 82)),
    "overlap-3-chain": (.34, [("source", 184, 214, 84), ("bridge", 280, 214, 84), ("target", 376, 214, 84)]),
    "overlap-5-cluster": (.32, [("prompt", 190, 178, 78), ("model", 268, 166, 82), ("data", 236, 252, 80), ("eval", 334, 244, 72), ("policy", 390, 168, 64)]),
    "overlap-7-bridge": (.31, [("left-a", 158, 176, 66), ("left-b", 214, 144, 66), ("left-c", 214, 226, 66), ("bridge", 280, 202, 66), ("right-a", 346, 144, 66), ("right-b", 402, 176, 66), ("right-c", 346, 226, 66)])
}

INSPECT = r'''options => {
const findings=[], states={};
const bounds=node=>{const r=node.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
const containment=[];
if(document.documentElement.scrollWidth>innerWidth+1)findings.push('gallery: horizontal viewport overflow');
const hex=v=>{const m=v.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):v;};
const luminance=paint=>[1,3,5].map(i=>parseInt(paint.slice(i,i+2),16)/255).map(n=>n<=.04045?n/12.92:((n+.055)/1.055)**2.4).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);
const bw=paint=>(luminance(paint)+.05)/.05>=1.05/(luminance(paint)+.05)?'#000000':'#ffffff';
// SVG length accessors expose float32 rounding for fractional task coordinates.
const near=(a,b)=>Math.abs(a-b)<.0001;
for(const id of options.ids){
  const svg=document.getElementById(id);
  if(!svg){findings.push(`${id}: missing SVG`);continue;}
  const card=svg.closest('article'),frame=svg.closest('.viz-frame');
  const mounted={id,svg:bounds(svg),card:bounds(card),frame:bounds(frame),viewportWidth:innerWidth};
  containment.push(mounted);
  if(mounted.card.x<-.5||mounted.card.right>innerWidth+.5||mounted.svg.x<mounted.card.x-.5||mounted.svg.right>mounted.card.right+.5||mounted.svg.x<mounted.frame.x-.5||mounted.svg.right>mounted.frame.right+.5||mounted.svg.y<mounted.frame.y-.5||mounted.svg.bottom>mounted.frame.bottom+.5)findings.push(`${id}: resting SVG/card/viewport containment`);
  svg.pauseAnimations?.();svg.setCurrentTime?.(10);window.D3SolidStyle?.normalize(svg);
  if(svg.dataset.patternId!==`d3-${id}-cs1`)findings.push(`${id}: pattern ID changed (${svg.dataset.patternId})`);
  if(!(svg.dataset.colorset==='colorset1'||svg.dataset.colorSet==='colorset1'))findings.push(`${id}: missing CS1 metadata`);
  const ink=[...svg.querySelectorAll('text')];
  for(const text of ink){
    const style=getComputedStyle(text),fill=hex(style.fill);
    if(!['#000000','#ffffff'].includes(fill)||style.stroke!=='none')findings.push(`${id}: non-BW or outlined label`);
    const scope=text.closest('[data-text-backing]'),face=scope?.querySelector(scope.dataset.textBacking);
    if(face&&getComputedStyle(face).fillOpacity==='1'&&fill!==bw(hex(getComputedStyle(face).fill)))findings.push(`${id}: label contrast on its declared face`);
  }
  const solids=[...svg.querySelectorAll('rect,circle,ellipse,polygon,path')].filter(node=>!node.closest('defs')&&node.dataset.fillStyle==='solid'&&getComputedStyle(node).fill!=='none');
  for(const node of solids){
    const style=getComputedStyle(node),semantic=node.closest('[data-opacity-role="semantic"]');
    if(node.closest('[data-outline-tier="overflow"]'))continue;
    if(style.stroke!=='none')findings.push(`${id}: early body outline`);
    if(!semantic&&(+style.fillOpacity!==1||+style.opacity!==1))findings.push(`${id}: decorative body alpha`);
  }
  const arrows=[...svg.querySelectorAll('[data-arrow-contrast]')].map(node=>({contrast:+node.dataset.arrowContrast,clearance:+node.dataset.arrowClearance,unresolved:node.dataset.arrowUnresolved??null}));
  if(arrows.some(arrow=>arrow.contrast<3||arrow.unresolved))findings.push(`${id}: unresolved arrow paint or insufficient contrast`);
  states[id]={patternId:svg.dataset.patternId,textCount:ink.length,bodyCount:solids.length,arrows,
    headers:[...svg.querySelectorAll('.treemap-branch-header')].map(node=>hex(getComputedStyle(node).fill)),
    layers:[...svg.querySelectorAll(':scope > g > path')].filter(node=>getComputedStyle(node).fill!=='none').map(node=>hex(getComputedStyle(node).fill)),
    leaves:[...svg.querySelectorAll('.treemap-leaf-cell')].map(node=>({branch:node.parentElement.dataset.branch,fill:hex(getComputedStyle(node).fill)})),
    families:[...svg.querySelectorAll('circle')].filter(node=>node.__data__?.depth===1).map(node=>({branch:node.__data__.data.name,fill:hex(getComputedStyle(node).fill)}))};
  states[id].roots=[...svg.querySelectorAll('circle')].filter(node=>node.__data__?.depth===0).map(node=>hex(getComputedStyle(node).fill));
  if(id==='circle-pack')states[id].children=[...svg.querySelectorAll('circle')].filter(node=>node.__data__?.depth>1).map(node=>({branch:node.__data__.parent.data.name,fill:hex(getComputedStyle(node).fill)}));
  if(id==='mirrored-beeswarm')states[id].samples=[...svg.querySelectorAll('circle')].map(node=>({id:node.__data__.id,side:node.__data__.side,value:node.__data__.value,fill:hex(getComputedStyle(node).fill)}));
  if(id==='tangled-tree'||id==='tanglegram')states[id].nodes=[...svg.querySelectorAll(id==='tangled-tree'?'g > rect':'g > circle')].filter(node=>node.__data__?.id).map(node=>({id:node.__data__.id,parent:node.__data__.parent??null,layer:node.__data__.layer??null,fill:hex(getComputedStyle(node).fill),transform:node.parentElement.getAttribute('transform')}));
  if(id==='task-overlap'){
    states[id].regions=[...svg.querySelectorAll('.overlap-circle')].map(node=>({id:node.dataset.setId,cx:node.cx.baseVal.value,cy:node.cy.baseVal.value,r:node.r.baseVal.value,fill:hex(getComputedStyle(node).fill)}));
    states[id].tasks=[...svg.querySelectorAll('.task-dot')].map(node=>({id:node.dataset.taskId,memberships:node.dataset.memberships,count:+node.dataset.membershipCount,x:node.cx.baseVal.value,y:node.cy.baseVal.value,fill:hex(getComputedStyle(node).fill)}));
  }
  if(id in options.venn){
    const circles=[...svg.querySelectorAll('.venn-circle')];
    const expected=options.venn[id],pane=svg.querySelector(':scope > rect:nth-of-type(2)')??svg.querySelector(':scope > rect');
    states[id].sets=circles.map(node=>({id:node.dataset.setId,code:node.dataset.setCode,cx:node.cx.baseVal.value,cy:node.cy.baseVal.value,r:node.r.baseVal.value,fill:hex(getComputedStyle(node).fill),alpha:+getComputedStyle(node).fillOpacity,blend:getComputedStyle(node).mixBlendMode,semantic:node.dataset.opacityRole}));
    states[id].background=hex(getComputedStyle(pane).fill);
    const obstacles=[...svg.querySelectorAll('text,.venn-core-label circle,.venn-label-layer circle,.venn-label-layer rect')];
    const guide=[...svg.querySelectorAll('circle')].filter(node=>!node.classList.contains('venn-circle')&&getComputedStyle(node).fill==='none');
    const samples={};
    for(let y=54;y<346;y+=7)for(let x=42;x<518;x+=7){
      const point=new DOMPoint(x,y).matrixTransform(svg.getScreenCTM());
      if(obstacles.some(node=>{const b=node.getBoundingClientRect();return point.x>b.left-5&&point.x<b.right+5&&point.y>b.top-5&&point.y<b.bottom+5;}))continue;
      if(guide.some(node=>Math.abs(Math.hypot(x-node.cx.baseVal.value,y-node.cy.baseVal.value)-node.r.baseVal.value)<5))continue;
      if(circles.some(node=>Math.abs(Math.hypot(x-node.cx.baseVal.value,y-node.cy.baseVal.value)-node.r.baseVal.value)<5))continue;
      const members=circles.map((node,index)=>Math.hypot(x-node.cx.baseVal.value,y-node.cy.baseVal.value)<node.r.baseVal.value?index:null).filter(index=>index!==null);
      if(!members.length||members.length>3||samples[members.length])continue;
      // Screenshot-relative point is recomputed after locator scrolling in Python.
      samples[members.length]={x,y,members};
    }
    states[id].intersectionSamples=Object.values(samples);
    for(const [index,node] of circles.entries()){
      const wanted=expected[1][index],style=getComputedStyle(node);
      if(node.dataset.setId!==wanted[0]||!near(node.cx.baseVal.value,wanted[1])||!near(node.cy.baseVal.value,wanted[2])||!near(node.r.baseVal.value,wanted[3]))findings.push(`${id}: set identity/geometry changed`);
      if(hex(style.fill)!==options.solids[index]||+style.fillOpacity!==expected[0]||style.stroke!=='none'||style.mixBlendMode!=='multiply'||node.dataset.opacityRole!=='semantic')findings.push(`${id}: set priority or semantic blend changed`);
    }
    if(!samples[1]||!samples[2])findings.push(`${id}: missing distinguishable single/shared sample regions`);
  }
}
const svg=document.getElementById('task-overlap-dense'), layout=options.layout;
const regions=[...svg.querySelectorAll('.overlap-circle')],dots=[...svg.querySelectorAll('.task-dot')],labels=[...svg.querySelectorAll('.task-label-group')],leaders=[...svg.querySelectorAll('.task-leader')];
if(regions.length!==9||dots.length!==100||labels.length!==100||leaders.length!==100)findings.push('dense: actual counts changed');
regions.forEach((node,index)=>{
  const expected=layout.circles[index],style=getComputedStyle(node);
  if(node.dataset.setId!==expected.id||!near(node.cx.baseVal.value,expected.cx)||!near(node.cy.baseVal.value,expected.cy)||!near(node.r.baseVal.value,expected.r))findings.push('dense: region identity or geometry changed');
  if(hex(style.fill)!==options.solids[index]||+style.fillOpacity!==.28||style.stroke!=='none')findings.push('dense: region priority/semantic alpha changed');
});
dots.forEach((node,index)=>{
  const expected=layout.tasks[index],label=labels[index],face=label.querySelector('rect'),text=label.querySelector('text'),leader=leaders[index];
  if(node.dataset.taskId!==expected.id||node.dataset.memberships!==expected.memberships.join(' ')||+node.dataset.membershipCount!==expected.membershipCount||text.textContent!==expected.label)findings.push('dense: task identity/membership/text changed');
  if(!near(node.cx.baseVal.value,expected.x)||!near(node.cy.baseVal.value,expected.y)||!near(node.r.baseVal.value,layout.dotRadius))findings.push('dense: task geometry changed');
  for(const [attribute,key] of [['x','labelX'],['y','labelY'],['width','labelWidth'],['height','labelHeight']])if(!near(face[attribute].baseVal.value,expected[key]))findings.push('dense: label face geometry changed');
  const edgeX=expected.labelEdgeX??(expected.labelX<expected.x?expected.labelX+expected.labelWidth:expected.labelX),edgeY=expected.labelEdgeY??expected.labelY+expected.labelHeight/2;
  if(!near(leader.x1.baseVal.value,expected.x)||!near(leader.y1.baseVal.value,expected.y)||!near(leader.x2.baseVal.value,edgeX)||!near(leader.y2.baseVal.value,edgeY))findings.push('dense: leader endpoints changed');
});
const collisions=[];
for(const caption of svg.querySelectorAll('.caption'))for(const label of labels){const a=caption.getBoundingClientRect(),b=label.getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.x,b.x)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>.5)collisions.push([caption.textContent,label.dataset.taskId]);}
if(collisions.length)findings.push('dense: caption/task-label collision');
states['task-overlap-dense'].regions=regions.map(node=>({fill:hex(getComputedStyle(node).fill),alpha:+getComputedStyle(node).fillOpacity}));
states['task-overlap-dense'].dataCounts={regions:regions.length,tasks:dots.length,labels:labels.length,leaders:leaders.length};
states['task-overlap-dense'].captionCollisions=collisions;
states['task-overlap-dense'].captionRail=+svg.dataset.captionRailY;
return {findings,states,containment};
}'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", nargs="?", const=DEFAULT_SITE, help="Audit the deployed Pages base URL; omit to audit canonical local sources")
    parser.add_argument("--source-root", type=Path, help="Audit a built Pages root such as dist/pages")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "projects/colorset-priority/artifacts/d3-gallery")
    parser.add_argument("--viewport", choices=["desktop", "mobile"], default="desktop", help="Use desktop 1440x1100 or mobile 390x844; run both for publication")
    args = parser.parse_args()
    artifacts = args.artifacts.resolve()
    if not artifacts.is_relative_to(ROOT) or artifacts.is_relative_to(ROOT / "skills"):
        parser.error("Artifacts must be inside this repository and outside skill bundles")
    artifacts.mkdir(parents=True, exist_ok=True)
    gallery = ROOT / "skills/d3/assets/examples/d3-animated-svg-cs1/index.html"
    if args.published:
        url = args.published.rstrip('/') + "/examples/d3-animated-svg-cs1/"
    elif args.source_root:
        url = (args.source_root.resolve() / "examples/d3-animated-svg-cs1/index.html").as_uri()
    else:
        url = gallery.as_uri()
    data = (ROOT / "skills/d3/assets/examples/d3-animated-svg/task-overlap-layouts.js").read_text(encoding="utf-8")
    match = re.search(r"window\.D3_TASK_OVERLAP_LAYOUTS\s*=\s*(\{[\s\S]*\})\s*;", data)
    layout = json.loads(match[1])["saturated"]
    solids = [paint for paint in EXPECTED if paint != "#ffffff"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {"channel": "msedge"}))
        viewport = {"width": 390, "height": 844} if args.viewport == "mobile" else {"width": 1440, "height": 1100}
        page = browser.new_page(viewport=viewport, reduced_motion="reduce")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="load", timeout=120000)
        page.wait_for_timeout(650)
        result = page.evaluate(INSPECT, {"ids": IDS, "layout": layout, "solids": solids, "venn": VENN})
        resting_states = json.loads(json.dumps(result["states"]))
        (artifacts / "resting-inspection.json").write_text(json.dumps({"url": url, "viewport": viewport, **result}, indent=2) + "\n", encoding="utf-8")
        states = result["states"]
        assert states["treemap"]["headers"] == solids[:3], states["treemap"]
        assert [family["fill"] for family in states["circle-pack"]["families"]] == solids[:3], states["circle-pack"]
        family_fills = {family["branch"]: family["fill"] for family in states["circle-pack"]["families"]}
        assert all(child["fill"] != family_fills[child["branch"]] for child in states["circle-pack"]["children"])
        assert states["radial-hierarchy"]["roots"] == solids[:1], states["radial-hierarchy"]
        assert all(family["fill"] == solids[1] for family in states["radial-hierarchy"]["families"])
        assert states["streamgraph"]["layers"] == solids[:4], states["streamgraph"]
        assert states["voronoi"]["layers"][:11] == solids[:11], states["voronoi"]
        samples = states["mirrored-beeswarm"]["samples"]
        assert len(samples) == 54 and all(sample["id"] == index and sample["value"] == 22 + ((index * 17) % 66) for index, sample in enumerate(samples))
        assert all(sample["fill"] == (solids[0] if sample["side"] == "Current" else solids[1]) for sample in samples)
        assert len(states["tangled-tree"]["nodes"]) == 10
        assert all(node["fill"] == solids[node["layer"]] for node in states["tangled-tree"]["nodes"])
        assert len(states["tanglegram"]["nodes"]) == 14
        assert all(node["fill"] == solids[1 if node["parent"] else 0] for node in states["tanglegram"]["nodes"])
        scopes = states["task-overlap"]["regions"]
        assert [scope["fill"] for scope in scopes] == solids[:9]
        assert [(scope["id"], scope["cx"], scope["cy"], scope["r"]) for scope in scopes] == [
            ("backlog",150,135,74),("ux",232,100,66),("api",326,135,76),("security",414,100,58),
            ("docs",96,215,62),("data",232,206,86),("qa",344,228,74),("release",160,280,68),("ops",420,290,60)]
        tasks = states["task-overlap"]["tasks"]
        assert len(tasks) == 20 and all(task["id"] == f"T{index+1:02}" for index,task in enumerate(tasks))
        assert all(task["fill"] == solids[min(task["count"],3)-1] for task in tasks)
        assert errors + result["findings"] == [], errors + result["findings"]
        for identity in VENN:
            locator = page.locator(f"svg#{identity}")
            png = locator.screenshot(path=str(artifacts / f"{identity}-cs1.png"))
            pixels = Image.open(BytesIO(png)).convert("RGB")
            screen = locator.evaluate("svg => {const b=svg.getBoundingClientRect(),m=svg.getScreenCTM();return {a:m.a,b:m.b,c:m.c,d:m.d,e:m.e-b.x,f:m.f-b.y};}")
            state = states[identity]
            background = tuple(int(state["background"][i:i+2],16) for i in (1,3,5))
            for sample in state["intersectionSamples"]:
                x,y=sample["x"],sample["y"]
                actual=pixels.getpixel((round(screen["a"]*x+screen["c"]*y+screen["e"]),round(screen["b"]*x+screen["d"]*y+screen["f"])))
                expected=list(background)
                for index in sample["members"]:
                    category=state["sets"][index]
                    paint=tuple(int(category["fill"][i:i+2],16) for i in (1,3,5))
                    expected=[value*((1-category["alpha"])+category["alpha"]*channel/255) for value,channel in zip(expected,paint)]
                assert max(abs(a-b) for a,b in zip(actual,expected)) <= 5, (identity,sample,actual,expected)
                sample["actualRGB"]=actual
                sample["expectedRGB"]=[round(value) for value in expected]
            assert len({tuple(sample["actualRGB"]) for sample in state["intersectionSamples"]}) >= 2
        for identity in ["treemap", "circle-pack", "task-overlap-dense", "mirrored-beeswarm", "streamgraph", "flowchart-dag"]:
            page.locator(f"svg#{identity}").screenshot(path=str(artifacts / f"{identity}-cs1.png"))
        dense_card = page.locator('article[data-example-id="task-overlap-dense"]')
        expand = dense_card.locator("[data-expand]")
        expand.click()
        detail = dense_card.evaluate(r'''card=>{
          const frame=card.querySelector('.viz-frame'),svg=frame.querySelector('svg');
          const labelSizes=[...svg.querySelectorAll('.task-label')].map(t=>parseFloat(getComputedStyle(t).fontSize)*svg.getScreenCTM().a);
          return {expanded:frame.classList.contains('is-expanded'),focusable:frame.tabIndex===0,accessibleName:frame.getAttribute('aria-label'),frameWidth:frame.clientWidth,frameHeight:frame.clientHeight,scrollWidth:frame.scrollWidth,scrollHeight:frame.scrollHeight,minimumLabelPixels:Math.min(...labelSizes),labelCount:labelSizes.length,buttonPressed:card.querySelector('[data-expand]').getAttribute('aria-pressed')};
        }''')
        assert detail["expanded"] and detail["focusable"] and detail["buttonPressed"] == "true", detail
        assert detail["labelCount"] == 100 and detail["minimumLabelPixels"] >= 14, detail
        assert detail["scrollWidth"] > detail["frameWidth"] and detail["scrollHeight"] > detail["frameHeight"], detail
        frame = dense_card.locator(".viz-frame")
        detail["labelReachability"] = frame.evaluate(r'''frame=>{
          const labels=[...frame.querySelectorAll('.task-label')],unreachable=[];
          for(const label of labels){
            const box=frame.getBoundingClientRect(),r=label.getBoundingClientRect();
            frame.scrollLeft+=r.x+r.width/2-box.x-frame.clientWidth/2;
            frame.scrollTop+=r.y+r.height/2-box.y-frame.clientHeight/2;
            const shown=label.getBoundingClientRect(),visible=frame.getBoundingClientRect();
            if(shown.x<visible.x-.5||shown.right>visible.x+frame.clientWidth+.5||shown.y<visible.y-.5||shown.bottom>visible.y+frame.clientHeight+.5)unreachable.push(label.dataset.taskId||label.textContent);
          }
          return {checked:labels.length,unreachable};
        }''')
        assert detail["labelReachability"] == {"checked": 100, "unreachable": []}, detail
        detail["captionReachability"] = frame.evaluate(r'''frame=>{
          const captions=[...frame.querySelectorAll('.caption')],unreachable=[];let checked=0,minimumPixels=Infinity;
          for(const text of captions){
            minimumPixels=Math.min(minimumPixels,parseFloat(getComputedStyle(text).fontSize)*text.getScreenCTM().a);
            for(let i=0;i<text.getNumberOfChars();i++){
              const extent=text.getExtentOfChar(i),center=new DOMPoint(extent.x+extent.width/2,extent.y+extent.height/2).matrixTransform(text.getScreenCTM()),box=frame.getBoundingClientRect();
              frame.scrollLeft+=center.x-box.x-frame.clientWidth/2;
              frame.scrollTop+=center.y-box.y-frame.clientHeight/2;
              const matrix=text.getScreenCTM(),a=new DOMPoint(extent.x,extent.y).matrixTransform(matrix),b=new DOMPoint(extent.x+extent.width,extent.y+extent.height).matrixTransform(matrix),visible=frame.getBoundingClientRect();
              if(a.x<visible.x-.5||b.x>visible.x+frame.clientWidth+.5||a.y<visible.y-.5||b.y>visible.y+frame.clientHeight+.5)unreachable.push({text:text.textContent,index:i});
              checked++;
            }
          }
          return {captions:captions.length,checkedGlyphs:checked,minimumPixels,unreachable};
        }''')
        assert detail["captionReachability"]["checkedGlyphs"] > 0 and detail["captionReachability"]["unreachable"] == [] and detail["captionReachability"]["minimumPixels"] >= 14, detail
        frame.evaluate("frame=>{frame.scrollLeft=frame.scrollWidth;frame.scrollTop=frame.scrollHeight;}")
        detail["pan"] = frame.evaluate(r'''frame=>{
          const svg=frame.querySelector('svg'),box=frame.getBoundingClientRect(),captions=[...svg.querySelectorAll('.caption')].map(t=>({text:t.textContent,box:t.getBoundingClientRect()}));
          return {scrollLeft:frame.scrollLeft,scrollTop:frame.scrollTop,rightReachable:Math.abs(frame.scrollWidth-frame.clientWidth-frame.scrollLeft)<=1,bottomReachable:Math.abs(frame.scrollHeight-frame.clientHeight-frame.scrollTop)<=1,captionVisible:captions.some(t=>t.box.x>=box.x-.5&&t.box.right<=box.right+.5&&t.box.y>=box.y-.5&&t.box.bottom<=box.bottom+.5)};
        }''')
        assert detail["pan"]["rightReachable"] and detail["pan"]["bottomReachable"], detail
        frame.screenshot(path=str(artifacts / "dense-readable-detail-cs1.png"))
        expand.click()
        fit = dense_card.evaluate("card=>({expanded:card.querySelector('.viz-frame').classList.contains('is-expanded'),pressed:card.querySelector('[data-expand]').getAttribute('aria-pressed')})")
        assert not fit["expanded"] and fit["pressed"] == "false", fit
        fitted = page.evaluate(INSPECT, {"ids": IDS, "layout": layout, "solids": solids, "venn": VENN})
        assert fitted["findings"] == [] and fitted["states"] == resting_states, fitted["findings"]
        browser.close()
    report = {"passed": True, "url": url, "viewport": viewport, "expectedPriority": EXPECTED, "states": states, "containment": result["containment"], "denseDetail": detail, "browserErrors": errors}
    (artifacts / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "ids": IDS, "report": str(artifacts / "report.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
