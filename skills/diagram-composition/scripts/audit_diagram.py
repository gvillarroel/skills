#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect a composition at display size or materialize trusted static SVG CSS."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
from compose_diagram import parse_svg, require, tag, write_target
from visual_quality import MEASURE, QUALITY
from playwright.sync_api import Error as PlaywrightError, sync_playwright


PREPARE = r"""() => {
 const props = ['fill','fill-opacity','fill-rule','stroke','stroke-width','stroke-opacity',
 'stroke-linecap','stroke-linejoin','stroke-dasharray','stroke-dashoffset','opacity',
 'font-family','font-size','font-weight','font-style','text-anchor','dominant-baseline',
 'visibility','display','paint-order','color','clip-path','mask','filter',
 'marker-start','marker-mid','marker-end','vector-effect','letter-spacing',
 'stop-color','stop-opacity','flood-color','flood-opacity','text-decoration',
 'writing-mode','transform','transform-origin','overflow'];
 const root=document.querySelector('svg');
 const rows=[root,...root.querySelectorAll('*')].map(e=>[e,getComputedStyle(e)]);
 const geometry={rect:['x','y','width','height','rx','ry'],circle:['cx','cy','r'],
   ellipse:['cx','cy','rx','ry'],path:['d'],use:['x','y','width','height']};
 const values=rows.map(([e,s])=>[e,props.map(p=>[p,s.getPropertyValue(p)]),
   (geometry[e.tagName]||[]).map(p=>[p,s.getPropertyValue(p)])]);
 for (const [e, vals, geom] of values) {
   e.removeAttribute('class');e.removeAttribute('style');
   for (const [p,v0] of vals) {
     const v=v0.replace(/url\(["']?[^)#]*#([^)'"\s]+)["']?\)/g,'url(#$1)');
     if(v && !(p==='transform' && v==='none')) e.setAttribute(p,v);
   }
   for(const [p,v] of geom)if(v&&v!=='auto'&&v!=='none')e.style.setProperty(p,v);
 }
 root.querySelectorAll('style').forEach(e=>e.remove());
 return new XMLSerializer().serializeToString(root);
}"""


def launch_browser(pw):
    """Use a normal installed Chromium channel if the bundled binary is absent."""
    try:
        return pw.chromium.launch(headless=True)
    except PlaywrightError as exc:
        if "Executable doesn't exist" not in str(exc):
            raise
        original = exc
    for channel in ("chrome", "msedge"):
        try:
            return pw.chromium.launch(headless=True, channel=channel)
        except PlaywrightError as exc:
            if "not found" not in str(exc) and "doesn't exist" not in str(exc):
                raise
    raise original

AUDIT = r"""({minimum}) => {
 const root=document.querySelector('svg');
 const rootBox=root.getBoundingClientRect();
 const issues=[], clippedMarks=[];
 function box(e) {
   const b=e.getBBox(), m=e.getScreenCTM();
   const p=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]
       .map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
   return {x:Math.min(...p.map(x=>x.x)),y:Math.min(...p.map(x=>x.y)),
     right:Math.max(...p.map(x=>x.x)),bottom:Math.max(...p.map(x=>x.y))};
 }
 function inside(b, c, slack=1.5) {
   return b.x>=c.x-slack&&b.y>=c.y-slack&&b.right<=c.right+slack&&b.bottom<=c.bottom+slack;
 }
 const texts=[];
 for(const e of root.querySelectorAll('text')) {
   if(e.closest('defs,clipPath,mask,marker,pattern,symbol'))continue;
   const style=getComputedStyle(e);
   if(style.display==='none'||style.visibility==='hidden'||+style.opacity===0)continue;
   const label=e.textContent.trim();if(!label)continue;
   const b=box(e),m=e.getScreenCTM();
   const size=Math.min(...[e,...e.querySelectorAll('tspan')].map(t=>{
     const tm=t.getScreenCTM();return parseFloat(getComputedStyle(t).fontSize)*Math.hypot(tm.c,tm.d);
   }));
   if(size+0.2<minimum)issues.push({kind:'small-text',label,size});
   if(!inside(b,rootBox))issues.push({kind:'canvas-overflow',label});
   const panel=e.closest('[data-panel-id]');
   if(panel) {
     const key=e.hasAttribute('data-panel-title')?'data-panel-box':'data-body';
     const [x,y,w,h]=JSON.parse(panel.getAttribute(key));
     const m=root.getScreenCTM(),a=new DOMPoint(x,y).matrixTransform(m),z=new DOMPoint(x+w,y+h).matrixTransform(m);
     if(!inside(b,{x:a.x,y:a.y,right:z.x,bottom:z.y}))issues.push({kind:'panel-overflow',panel:panel.dataset.panelId,label});
   }
   texts.push({label,box:b,size});
 }
 for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
   const a=texts[i],b=texts[j];
   if(Math.min(a.box.right,b.box.right)-Math.max(a.box.x,b.box.x)>2 &&
      Math.min(a.box.bottom,b.box.bottom)-Math.max(a.box.y,b.box.y)>2)
     issues.push({kind:'text-collision',labels:[a.label,b.label]});
 }
 for(const path of root.querySelectorAll('[data-relation-id] path')){
   const length=path.getTotalLength(),steps=Math.max(1,Math.ceil(length/3)),m=path.getScreenCTM();
   const hits=new Set();
   for(let i=0;i<=steps;i++){
     const p=path.getPointAtLength(length*i/steps),q=new DOMPoint(p.x,p.y).matrixTransform(m);
     for(const t of texts){const b=t.box;
       if(q.x>b.x+2&&q.x<b.right-2&&q.y>b.y+2&&q.y<b.bottom-2)hits.add(t.label);
     }
   }
   for(const label of hits)issues.push({kind:'connector-text-collision',relation:path.closest('[data-relation-id]').dataset.relationId,label});
 }
 for(const e of root.querySelectorAll('[data-source] path,[data-source] rect,[data-source] circle,[data-source] ellipse,[data-source] polygon,[data-source] polyline,[data-source] line')){
   if(e.closest('defs,clipPath,mask,marker,pattern,symbol'))continue;
   const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden')continue;
   const panel=e.closest('[data-panel-id]');if(!panel)continue;
   const [x,y,w,h]=JSON.parse(panel.dataset.body),m=root.getScreenCTM();
   const a=new DOMPoint(x,y).matrixTransform(m),z=new DOMPoint(x+w,y+h).matrixTransform(m);
   if(!inside(box(e),{x:a.x,y:a.y,right:z.x,bottom:z.y},2)){
     const source=e.closest('[data-source]');
     const finding={kind:'mark-overflow',panel:panel.dataset.panelId,element:e.tagName};
     if(source&&['hidden','clip'].includes(getComputedStyle(source).overflow))clippedMarks.push(finding);
     else issues.push(finding);
   }
 }
 return {issues,clippedMarks,textCount:texts.length,minimumObservedPx:texts.length?Math.min(...texts.map(x=>x.size)):null,
   panelCount:root.querySelectorAll('[data-panel-id]').length,labels:texts.map(x=>x.label)};
}"""


COLOR_AUDIT = r"""({colors,panels}) => {
 const root=document.querySelector('svg'), issues=[], occurrences=[], coverage={};
 const paintable=new Set(['path','rect','circle','ellipse','polygon','polyline','line','text']);
 const rgb=hex=>'rgb('+[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)).join(', ')+')';
 const declared=new Map(panels.map(p=>[p.id,new Set(p.concepts||[])]));
 for(const p of panels)coverage[p.id]=[];
 for(const e of root.querySelectorAll('[data-color-concept],[data-color-channel]')) {
   const concept=e.getAttribute('data-color-concept'), channel=e.getAttribute('data-color-channel');
   const panel=e.closest('[data-panel-id]')?.dataset.panelId||null;
   const finding={concept,channel,panel};
   if(!colors[concept]||!['fill','stroke'].includes(channel)||!paintable.has(e.tagName)||
      (panel&&!declared.get(panel)?.has(concept))) {
     issues.push({kind:'semantic-color-invalid-binding',...finding});continue;
   }
   const s=getComputedStyle(e), b=e.getBoundingClientRect(), r=root.getBoundingClientRect();
   let visible=!e.closest('defs,clipPath,mask,marker,pattern,symbol')&&
     (b.width>0||b.height>0)&&b.right>r.left&&b.left<r.right&&b.bottom>r.top&&b.top<r.bottom&&
     +s.getPropertyValue(channel+'-opacity')===1 && (channel!=='stroke'||parseFloat(s.strokeWidth)>0);
   for(let a=e;a&&a instanceof SVGElement;a=a.parentElement) {
     const t=getComputedStyle(a);
     if(t.display==='none'||t.visibility!=='visible'||+t.opacity!==1||
        t.filter!=='none'||t.maskImage!=='none'||t.mixBlendMode!=='normal')visible=false;
     if(a.tagName==='svg') {
       const v=a.getBoundingClientRect();
       if(b.right<=v.left||b.left>=v.right||b.bottom<=v.top||b.top>=v.bottom)visible=false;
     }
   }
   const actual=s.getPropertyValue(channel), expected=rgb(colors[concept]);
   occurrences.push({...finding,actual,expected,visible});
   if(!visible)issues.push({kind:'semantic-color-invisible-or-altered',...finding});
   if(actual!==expected)issues.push({kind:'semantic-color-mismatch',...finding,actual,expected});
   if(visible&&actual===expected&&panel&&!coverage[panel].includes(concept))coverage[panel].push(concept);
 }
 for(const p of panels)for(const concept of p.concepts||[]) {
   if(colors[concept]&&!coverage[p.id].includes(concept))
     issues.push({kind:'semantic-color-missing',panel:p.id,concept});
 }
 return {status:Object.keys(colors).length?'checked':'not-declared',colors,occurrences,coverage,issues};
}"""


def run(args):
    prepare = args.command == "prepare"
    measure = args.command == "measure"
    root, vb, digest = parse_svg(args.input, allow_style=prepare or measure)
    destinations = [args.output] if prepare else [args.report] if measure else [args.report, args.screenshot]
    require(all(p is not None for p in destinations), "prepare needs --output; measure needs --report; audit needs --report and --screenshot")
    require(len({p.resolve() for p in destinations}) == len(destinations), "Output paths must be distinct")
    for path in destinations:
        require(path.resolve() != args.input.resolve(), "Preserve the original SVG input")
        write_target(path, args.overwrite)
    data = root.find(tag("metadata") + "[@id='composition-report']")
    if not prepare and not measure:
        require(data is not None and data.text, "Expected a composition-report metadata element")
        report = json.loads(data.text)
        width = report["canvas"]["displayWidth"]
        minimum = report["canvas"]["minTextPx"]
    else:
        width, minimum = vb[2], 0
    require(width > 0 and width <= 16000, "Display width must be between 1 and 16000 pixels")
    requests = []
    with sync_playwright() as pw:
        browser = launch_browser(pw)
        try:
            page = browser.new_page(viewport={"width": math.ceil(width), "height": math.ceil(width * vb[3] / vb[2])},
                                    device_scale_factor=1, java_script_enabled=False)
            page.route("**/*", lambda route: (requests.append(route.request.url), route.abort()))
            page.set_content(root_to_text(root), wait_until="load", timeout=30000)
            page.evaluate("([w,h])=>{document.body.style.margin='0';const s=document.querySelector('svg');s.style.width=w+'px';s.style.height=h+'px';s.style.display='block'}", [width, width * vb[3] / vb[2]])
            page.evaluate("document.fonts.ready")
            if prepare or measure:
                active = page.evaluate("() => [...document.querySelectorAll('svg,svg *')].some(e=>{const s=getComputedStyle(e);return s.animationName!=='none'&&s.animationDuration.split(',').some(d=>parseFloat(d)>0)})")
                require(not active, "Active CSS animation found; export a meaningful static frame first")
            if measure:
                result={"ok":True, **page.evaluate(MEASURE), "sourceSha256":digest}
                require(not requests, "External resources requested during measurement")
                args.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
                return result
            if prepare:
                output = page.evaluate(PREPARE)
                require(not requests, "External resources were requested during normalization")
                args.output.write_text(output, encoding="utf-8")
                parse_svg(args.output)
                return {"ok": True, "output": str(args.output), "sourceSha256": digest}
            audit = page.evaluate(AUDIT, {"minimum": minimum})
            color_audit = page.evaluate(COLOR_AUDIT, {"colors": report.get("semanticColors", {}), "panels": report["panels"]})
            audit["issues"].extend(color_audit.pop("issues"))
            audit["semanticColors"] = color_audit
            quality = page.evaluate(QUALITY, {"report": report})
            audit["issues"].extend(quality.pop("issues"))
            audit["visualQuality"] = quality
            audit["externalRequests"] = requests
            audit["sourceSha256"] = digest
            audit["displayWidth"] = width
            audit["ok"] = not audit["issues"] and not requests and audit["textCount"] > 0
            page.screenshot(path=str(args.screenshot), full_page=True)
            args.report.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return audit
        finally:
            browser.close()


def root_to_text(root):
    return "<!doctype html><html><head><meta charset='utf-8'></head><body>" + ET.tostring(root, encoding="unicode") + "</body></html>"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "measure", "audit"])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="Report draft findings without failing the command; final audit must omit this flag")
    args = parser.parse_args()
    try:
        result = run(args)
        print(json.dumps({k: v for k, v in result.items() if k != "labels"}, ensure_ascii=True))
        return 0 if result["ok"] or (args.command == "audit" and args.inspect) else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
