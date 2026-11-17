#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Inspect authored float/detail previews with one clock and actual browser pixels."""
import argparse
import hashlib
import io
import json
import math
import os
import tempfile
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright


def inspect(page, times, floats, detail=None, viewport=None, fixed=()):
    """Return evidence; require explicit selectors instead of inferring artistic intent."""
    if not times or any(not math.isfinite(t) or t < 0 for t in times):
        raise ValueError('Supply finite nonnegative parent-clock times.')
    if bool(detail) != bool(viewport) or not floats and not detail:
        raise ValueError('Select float groups and/or a detail wrapper with its fixed viewport.')
    selectors = list(dict.fromkeys([*floats, *fixed, *([detail, viewport] if detail else [])]))
    for selector in selectors:
        if page.locator(selector).count() != 1:
            raise ValueError('Select exactly one element: ' + selector)
    dimensions = page.viewport_size
    def seek(t):
        page.evaluate('async t=>{await window.renderAt(t);await document.fonts.ready}', t)
        return page.evaluate('''({selectors,viewport})=>({elements:Object.fromEntries(selectors.map(s=>{
          const e=document.querySelector(s);let b=e.getBoundingClientRect();
          if(s===viewport&&e instanceof SVGSVGElement){
            const v=e.viewBox.baseVal,w=v.width||e.width.baseVal.value,h=v.height||e.height.baseVal.value;
            const x=v.width?v.x:0,y=v.height?v.y:0,m=e.getScreenCTM();
            const p=[[x,y],[x+w,y],[x,y+h],[x+w,y+h]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
            const xs=p.map(p=>p.x),ys=p.map(p=>p.y);
            b={x:Math.min(...xs),y:Math.min(...ys),width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys)};
          }
          if(s===viewport&&e instanceof SVGGElement)throw Error('Select the fixed viewport rect or nested svg, not its content group.');
          return[s,{x:b.x,y:b.y,width:b.width,height:b.height,transform:e.getAttribute('transform'),text:e.textContent}]
        })),sources:[...document.querySelectorAll('image')].map(e=>e.getAttribute('href')||e.getAttribute('xlink:href'))})''', {'selectors':selectors,'viewport':viewport})
    def digest(data): return hashlib.sha256(data).hexdigest()
    def covers(a,b):
        return a['x']<=b['x']+.02 and a['y']<=b['y']+.02 and a['x']+a['width']>=b['x']+b['width']-.02 and a['y']+a['height']>=b['y']+b['height']-.02
    def box_equal(a,b): return all(abs(a[k]-b[k])<.02 for k in ['x','y','width','height'])
    def region_hash(pixels, box):
        image=Image.open(io.BytesIO(pixels))
        rect=(math.floor(box['x']),math.floor(box['y']),math.ceil(box['x']+box['width']),math.ceil(box['y']+box['height']))
        return digest(image.crop(rect).tobytes())
    records=[]; findings=[]; fixed_initial=None; original_sources=None
    for t in times:
        state=seek(t); pixels=page.screenshot(animations='disabled')
        if fixed_initial is None:
            fixed_initial=state['elements']; original_sources=state['sources']
        if state['sources']!=original_sources: findings.append({'seconds':t,'kind':'source-image-changed'})
        for selector in [*floats,*fixed,*([viewport] if viewport else [])]:
            b=state['elements'][selector]
            if b['x']<-.02 or b['y']<-.02 or b['x']+b['width']>dimensions['width']+.02 or b['y']+b['height']>dimensions['height']+.02:
                findings.append({'seconds':t,'kind':'outside-frame','target':selector})
        for selector in [*fixed,*([viewport] if viewport else [])]:
            if not box_equal(state['elements'][selector],fixed_initial[selector]): findings.append({'seconds':t,'kind':'fixed-element-moved','target':selector})
        if detail and not covers(state['elements'][detail],state['elements'][viewport]):
            findings.append({'seconds':t,'kind':'empty-detail-viewport'})
        records.append({'seconds':t,'state':state,'frameSha256':digest(pixels),'detailPixelsSha256':region_hash(pixels,state['elements'][viewport]) if viewport else None})
    movements={}
    for selector in floats:
        boxes=[r['state']['elements'][selector] for r in records]
        span={k:max(b[k] for b in boxes)-min(b[k] for b in boxes) for k in ['x','y']}
        movements[selector]=span
        if max(span.values())<.05: findings.append({'kind':'float-not-visible','target':selector})
        if any(abs(b['width']-boxes[0]['width'])>.02 or abs(b['height']-boxes[0]['height'])>.02 for b in boxes):
            findings.append({'kind':'float-group-resized','target':selector})
    # Revisit the middle after both extremes; compare the actual complete frame.
    selected=records[len(records)//2]; seek(times[-1]); seek(times[0]); repeated=seek(selected['seconds'])
    repeat={'stateEqual':repeated==selected['state'],'pixelsEqual':digest(page.screenshot(animations='disabled'))==selected['frameSha256']}
    if not all(repeat.values()): findings.append({'kind':'repeat-seek-differs'})
    if detail and len({r['detailPixelsSha256'] for r in records})<2: findings.append({'kind':'detail-not-visible'})
    return {'ok':not findings,'samples':records,'floatTravel':movements,'repeatSeek':repeat,'findings':findings,'scope':'Sampled actual browser geometry and pixels. Source href identity, selected fixed elements and viewport coverage. No automatic speech alignment, cycle timing, comfort certification or encoded-video approval.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',type=Path,required=True); parser.add_argument('--times',required=True)
    parser.add_argument('--width',type=int,required=True); parser.add_argument('--height',type=int,required=True)
    parser.add_argument('--float-target',action='append',default=[]); parser.add_argument('--detail-target'); parser.add_argument('--viewport')
    parser.add_argument('--fixed-target',action='append',default=[])
    parser.add_argument('--output',type=Path,required=True); parser.add_argument('--screenshot',type=Path,required=True); parser.add_argument('--screenshot-time',type=float)
    args=parser.parse_args(); args.output.parent.mkdir(parents=True,exist_ok=True); args.screenshot.parent.mkdir(parents=True,exist_ok=True)
    errors=[]; report={'ok':False}
    temporary=args.output.parent/'browser-temp'; temporary.mkdir(exist_ok=True)
    os.environ['TMP']=str(temporary.resolve()); os.environ['TEMP']=str(temporary.resolve()); tempfile.tempdir=str(temporary.resolve())
    try:
        with sync_playwright() as pw:
            chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
            browser=pw.chromium.launch(headless=True,**({'executable_path':str(chrome)} if chrome.is_file() else {}))
            page=browser.new_page(viewport={'width':args.width,'height':args.height}); page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(args.html.resolve().as_uri()); page.evaluate('async()=>{await window.ready;await document.fonts.ready}')
            times=[float(x) for x in args.times.split(',')]
            report=inspect(page,times,args.float_target,args.detail_target,args.viewport,args.fixed_target)
            page.evaluate('t=>window.renderAt(t)',args.screenshot_time if args.screenshot_time is not None else times[len(times)//2])
            page.screenshot(path=str(args.screenshot.resolve()),animations='disabled'); browser.close()
    except Exception as error: errors.append(str(error))
    report['browserErrors']=errors; report['ok']=report['ok'] and not errors
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':report['ok'],'samples':len(report.get('samples',[])),'findings':report.get('findings',[]),'output':str(args.output)}))
    return 0 if report['ok'] else 2


if __name__=='__main__': raise SystemExit(main())
