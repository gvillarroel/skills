#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently inspect published treemap paint and geometry in Chromium."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


INSPECT = r"""() => {
  const findings = [];
  const card = document.querySelector('[data-example="treemap"]');
  const svg = card?.querySelector('svg');
  if (!svg) return { clean: false, findings: ['The treemap SVG is missing.'] };
  const colorset = svg.dataset.colorset || svg.dataset.colorSet || document.body.dataset.colorSet;
  const allowed = new Set(window.D3_SOLID_PALETTES?.[colorset]?.allowed || []);
  const rgb = value => {
    if (/^#[0-9a-f]{6}$/i.test(value)) return [1,3,5].map(i => parseInt(value.slice(i,i+2),16));
    const values = value?.match(/^rgba?\(([^)]+)\)$/)?.[1].split(/[ ,/]+/).map(Number);
    return values?.length >= 3 ? values.slice(0,3) : null;
  };
  const hex = value => { const channels = rgb(value); return channels && '#' + channels.map(v => Math.round(v).toString(16).padStart(2,'0')).join(''); };
  const luminance = value => rgb(value).map(v => v / 255).map(v => v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4)
    .reduce((sum,v,i) => sum + v*[.2126,.7152,.0722][i],0);
  const contrast = (a,b) => (Math.max(luminance(a),luminance(b))+.05)/(Math.min(luminance(a),luminance(b))+.05);
  const textOn = fill => contrast('#000000',fill) >= contrast('#ffffff',fill) ? '#000000' : '#ffffff';
  const alpha = element => {
    let result = 1;
    for (let node=element; node && node !== svg.parentElement; node=node.parentElement) result *= Number(getComputedStyle(node).opacity);
    return result * Number(getComputedStyle(element).fillOpacity);
  };
  const rects = [...svg.querySelectorAll('rect')].filter(rect => !rect.closest('defs,clipPath,mask'));
  const pointIn = (element, point) => {
    try { return element.isPointInFill(point.matrixTransform(element.getScreenCTM().inverse())); }
    catch { return false; }
  };
  const backingAt = point => {
    const covering = rects.filter(rect => {
      const style = getComputedStyle(rect);
      return style.display !== 'none' && style.visibility !== 'hidden' && alpha(rect) > .99 && hex(style.fill) && pointIn(rect,point);
    });
    return covering.length ? hex(getComputedStyle(covering.at(-1)).fill) : '#ffffff';
  };
  const allNodes = [...svg.querySelectorAll('g')].filter(node => node.__data__?.depth && Number.isFinite(node.__data__.x0));
  const nodes = allNodes.map(group => {
    const datum = group.__data__, rect = group.querySelector(':scope > rect');
    if (!rect) { findings.push(`${datum.data.name}: node rectangle is missing.`); return null; }
    const style = getComputedStyle(rect), fill = hex(style.fill), box = rect.getBBox();
    const expectedWidth = datum.x1-datum.x0, expectedHeight = datum.y1-datum.y0;
    const mainTransform = group.transform.baseVal.consolidate()?.matrix;
    if (Math.abs(box.width-expectedWidth)>.01 || Math.abs(box.height-expectedHeight)>.01 ||
        Math.abs((mainTransform?.e ?? NaN)-datum.x0)>.01 || Math.abs((mainTransform?.f ?? NaN)-datum.y0)>.01)
      findings.push(`${datum.data.name}: the data rectangle geometry changed.`);
    for (const face of group.querySelectorAll(':scope > rect')) {
      const paint = getComputedStyle(face), faceFill=hex(paint.fill);
      if (paint.stroke !== 'none' && Number(paint.strokeOpacity) > 0 && Number.parseFloat(paint.strokeWidth) > 0)
        findings.push(`${datum.data.name}: a decorative outline is visible.`);
      if (alpha(face) < .999) findings.push(`${datum.data.name}: a readable face is translucent (${alpha(face)}).`);
      if (!allowed.has(faceFill)) findings.push(`${datum.data.name}: ${faceFill} is outside ${colorset}.`);
    }
    const labels = [...group.querySelectorAll(':scope > text')].map(label => {
      const bounds = label.getBBox(), visual = label.getBoundingClientRect();
      const point = new DOMPoint(visual.x+visual.width/2, visual.y+visual.height/2);
      const backing = backingAt(point), paint = hex(getComputedStyle(label).fill), level = contrast(paint,backing);
      if (!['#000000','#ffffff'].includes(paint) || paint !== textOn(backing)) findings.push(`${datum.data.name}: label is not maximum-contrast black/white on ${backing}.`);
      if (level < 4.5) findings.push(`${datum.data.name}: label contrast is ${level.toFixed(3)}:1.`);
      if (bounds.x < -.5 || bounds.y < -.5 || bounds.x+bounds.width > box.width+.5 || bounds.y+bounds.height > box.height+.5)
        findings.push(`${datum.data.name}: label exceeds its cell.`);
      return { text:label.textContent, fill:paint, backing, contrast:level, bounds:{x:bounds.x,y:bounds.y,width:bounds.width,height:bounds.height}, renderedFontSize:Number.parseFloat(getComputedStyle(label).fontSize)*svg.getBoundingClientRect().width/svg.viewBox.baseVal.width };
    });
    if (labels.length !== 1 || labels[0]?.text !== datum.data.name) findings.push(`${datum.data.name}: exactly one matching direct label is required.`);
    return { name:datum.data.name, branch:datum.depth===1 ? datum.data.name : datum.parent.data.name, depth:datum.depth,
      value:datum.value, fill, luminance:luminance(fill), stroke:style.stroke, alpha:alpha(rect),
      geometry:{x0:datum.x0,y0:datum.y0,x1:datum.x1,y1:datum.y1,width:box.width,height:box.height}, labels };
  }).filter(Boolean);
  const expected = {Create:{Prompt:4,Draft:7,Review:5},Serve:{Cache:5,Route:4,Observe:7},Learn:{Eval:6,Trace:5,Tune:8}};
  const branches=nodes.filter(node => node.depth===1), leaves=nodes.filter(node => node.depth===2);
  if (branches.length!==3 || leaves.length!==9 || nodes.length!==12) findings.push(`Expected 3 branches and 9 leaves; found ${branches.length} and ${leaves.length}.`);
  for (const [branch,children] of Object.entries(expected)) {
    for (const [name,value] of Object.entries(children)) {
      const matching = leaves.filter(node => node.branch===branch && node.name===name && node.value===value);
      if (matching.length!==1) findings.push(`${branch}/${name}: data/relationship/value is missing or altered.`);
    }
  }
  const ramps=[];
  const gutters=[];
  for (const group of allNodes.filter(node => node.__data__.depth===1)) {
    const data = group.__data__, children=data.children.map(child => leaves.find(leaf => leaf.name===child.data.name && leaf.branch===data.data.name));
    if (children.some(child => !child)) continue;
    const fills=children.map(child => child.fill), levels=children.map(child => child.luminance), steps=levels.slice(1).map((level,index)=>level-levels[index]);
    const increasing=steps.every(step=>step>.015), decreasing=steps.every(step=>step<-.015);
    if (new Set(fills).size!==children.length) findings.push(`${data.data.name}: sibling cells share paint.`);
    if (!increasing && !decreasing) findings.push(`${data.data.name}: sibling luminance does not form distinct ordered steps.`);
    ramps.push({ branch:data.data.name, order:children.map(child=>child.name), fills, luminances:levels, steps });
    for (let i=0;i<children.length;i++) for (let j=i+1;j<children.length;j++) {
      const a=children[i].geometry,b=children[j].geometry;
      const overlapX=Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0), overlapY=Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0);
      let local=null,gap=null;
      if (overlapX>1) {
        const first=a.y0<b.y0?a:b, second=first===a?b:a; gap=second.y0-first.y1;
        if (gap>0 && gap<=8) local=new DOMPoint((Math.max(a.x0,b.x0)+Math.min(a.x1,b.x1))/2,(first.y1+second.y0)/2);
      }
      if (!local && overlapY>1) {
        const first=a.x0<b.x0?a:b, second=first===a?b:a; gap=second.x0-first.x1;
        if (gap>0 && gap<=8) local=new DOMPoint((first.x1+second.x0)/2,(Math.max(a.y0,b.y0)+Math.min(a.y1,b.y1))/2);
      }
      if (!local) continue;
      const rootGroup=group.parentElement, point=local.matrixTransform(rootGroup.getScreenCTM()), fill=backingAt(point);
      if (fill===children[i].fill || fill===children[j].fill) findings.push(`${data.data.name}: the ${children[i].name}/${children[j].name} gutter merges with a leaf.`);
      gutters.push({branch:data.data.name,between:[children[i].name,children[j].name],width:gap,fill});
    }
  }
  if (gutters.length<6) findings.push(`Expected at least 6 sibling gutters, found ${gutters.length}.`);
  return {clean:findings.length===0,findings,colorset,patternId:card.dataset.patternId,viewBox:svg.getAttribute('viewBox'),nodes,ramps,gutters};
}"""


def launch_browser(playwright):
    try:
        return playwright.chromium.launch()
    except Error as original:
        for channel, executable in (
            ("msedge", Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")),
            ("chrome", Path("C:/Program Files/Google/Chrome/Application/chrome.exe")),
        ):
            if executable.exists():
                return playwright.chromium.launch(channel=channel)
        raise original


def check_negative_controls(page):
    """Mutate native paint/geometry immediately before the independent scan."""
    mutations = {
        "same-sibling-fill": """
          const leaves=groups.filter(group=>!group.__data__.children);
          for (const branch of ['Learn','Create','Serve']) {
            const siblings=leaves.filter(group=>group.__data__.parent.data.name===branch);
            const fill=getComputedStyle(siblings[0].querySelector(':scope > rect')).fill;
            siblings.forEach(group=>{const rect=group.querySelector(':scope > rect');remember(rect);rect.style.fill=fill;rect.setAttribute('fill',fill);});
          }
        """,
        "wrong-label-contrast": """
          const text=groups.find(group=>!group.__data__.children).querySelector(':scope > text');
          remember(text);text.style.fill='#e8002a';text.setAttribute('fill','#e8002a');
        """,
        "decorative-border": """
          const rect=groups.find(group=>!group.__data__.children).querySelector(':scope > rect');
          remember(rect);rect.style.stroke='#000000';rect.style.strokeWidth='2px';
        """,
        "changed-cell-geometry": """
          const rect=groups.find(group=>!group.__data__.children).querySelector(':scope > rect');
          remember(rect);rect.setAttribute('width',String(rect.width.baseVal.value-20));
        """,
    }
    controls=[]
    for name, mutation in mutations.items():
        code = """() => {
          const saved=[];
          const remember=element=>saved.push({element,attributes:[...element.attributes].map(attribute=>[attribute.name,attribute.value])});
          const groups=[...document.querySelector('[data-example="treemap"] svg').querySelectorAll('g')].filter(group=>group.__data__?.depth);
        """ + mutation + "\nconst result=(" + INSPECT + " )();\n" + """
          saved.forEach(({element,attributes})=>{
            [...element.attributes].forEach(attribute=>element.removeAttribute(attribute.name));
            attributes.forEach(([name,value])=>element.setAttribute(name,value));
          });
          return result;
        }"""
        result=page.evaluate(code)
        controls.append({"name":name,"rejected":not result["clean"],"findings":result["findings"]})
    return controls


def compare_geometry(report, reference):
    findings=[]
    known={(state["viewportWidth"],state["reducedMotion"],state["replay"]):state for state in reference["states"]}
    for state in report["states"]:
        key=(state["viewportWidth"],state["reducedMotion"],state["replay"])
        previous=known.get(key)
        if previous is None:
            findings.append(f"Missing reference state {key}.")
            continue
        prior={node["name"]:node for node in previous["nodes"]}
        for node in state["nodes"]:
            old=prior.get(node["name"])
            if old is None or any(node[field]!=old[field] for field in ("depth","value","branch","geometry")):
                findings.append(f"{key}: {node['name']} geometry/data/relationship changed.")
    return {"clean":not findings,"states":len(report["states"]),"findings":findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Source HTML path or HTTP(S) URL")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--baseline", action="store_true", help="Retain findings without requiring visual acceptance.")
    parser.add_argument("--negative-controls-only", action="store_true", help="Verify that the scanner rejects four native DOM regressions.")
    parser.add_argument("--compare-reference", type=Path, help="Compare native node geometry/data against a retained verification report.")
    args = parser.parse_args()
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    remote = args.source.startswith(("https://", "http://"))
    source = args.source if remote else Path(args.source).resolve().as_uri()
    report = {"source":args.source,"baseline":args.baseline,"states":[],"negativeControls":[],"errors":[],"clean":False}
    if not remote:
        report["htmlSha256"] = hashlib.sha256(Path(args.source).read_bytes()).hexdigest()
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        for width in ((1440,) if args.negative_controls_only else (1440,390)):
            for reduced in ((False,) if args.negative_controls_only else (False,True)):
                context = browser.new_context(viewport={"width":width,"height":1100}, reduced_motion="reduce" if reduced else "no-preference")
                page = context.new_page()
                page.on("pageerror", lambda error: report["errors"].append(str(error)))
                page.goto(source,wait_until="load",timeout=120000)
                card=page.locator('[data-example="treemap"]')
                card.scroll_into_view_if_needed()
                for replay in range(1 if args.negative_controls_only else 3):
                    if replay:
                        card.locator('[data-replay]').click()
                    page.wait_for_timeout(1600)
                    page.evaluate("document.querySelector('[data-example=treemap] svg').pauseAnimations(); document.querySelector('[data-example=treemap] svg').setCurrentTime(5)")
                    page.wait_for_timeout(100)
                    state = page.evaluate(INSPECT)
                    state.update({"viewportWidth":width,"reducedMotion":reduced,"replay":replay})
                    report["states"].append(state)
                    if replay==0 and not args.negative_controls_only:
                        stem=f"treemap-{width}-{'reduced' if reduced else 'normal'}"
                        card.screenshot(path=str(output/f"{stem}-card.png"))
                        card.locator('svg').screenshot(path=str(output/f"{stem}-svg.png"))
                        (output/f"{stem}.svg").write_text(card.locator('svg').evaluate("node=>node.outerHTML"),encoding="utf-8")
                if width==1440 and not reduced and not args.baseline:
                    report["negativeControls"] = check_negative_controls(page)
                context.close()
        browser.close()
    if args.compare_reference:
        report["geometryComparison"] = compare_geometry(report,json.loads(args.compare_reference.read_text(encoding="utf-8")))
    report["clean"] = not report["errors"] and all(state["clean"] for state in report["states"]) and \
        all(control["rejected"] for control in report["negativeControls"]) and report.get("geometryComparison",{}).get("clean",True)
    (output/"verification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    summary = {"clean":report["clean"],"baseline":args.baseline,"states":len(report["states"]),"findings":sum(len(state["findings"]) for state in report["states"]),"errors":report["errors"],"report":str(output/"verification.json")}
    print(json.dumps(summary,indent=2))
    return 0 if report["clean"] or (args.baseline and not report["errors"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
