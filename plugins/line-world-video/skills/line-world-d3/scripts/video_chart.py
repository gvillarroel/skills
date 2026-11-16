#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Build and verify a bounded D3 table/comparison asset for a parent video clock."""
import argparse
import functools
import http.server
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

SKILL=Path(__file__).resolve().parent.parent
HTML=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Video data asset</title><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#ffffff}svg{display:block;width:100%;height:100%;font-family:Arial,sans-serif;font-variant-numeric:tabular-nums}text{fill:#333e48}line,path,circle{vector-effect:non-scaling-stroke}
</style></head><body><svg id="stage" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" role="img" aria-labelledby="asset-title asset-desc" data-colorset="colorset1"><title id="asset-title">Linked entity values</title><desc id="asset-desc">The table and zero-based comparison share the same records, units and selected entity. The parent video owns playback.</desc></svg><script src="d3.min.js"></script><script>
(() => {
const DATA=__DATA__,svg=d3.select('#stage'),C={ink:'#333e48',red:'#9e1b32',quiet:'#cfcfcf',white:'#ffffff'};
svg.append('rect').attr('width',1920).attr('height',1080).attr('fill',C.white);
svg.append('line').attr('x1',960).attr('x2',960).attr('y1',0).attr('y2',1080).attr('stroke',C.quiet).attr('stroke-width',1.5);
const gap=Math.min(200,600/(DATA.records.length-1)),top=(1080-gap*(DATA.records.length-1))/2,axisY=top+gap*(DATA.records.length-1)+110,x=d3.scaleLinear([0,d3.max(DATA.records,d=>d.value)*1.12||1],[1140,1740]);
const text=(g,xx,yy,value,size=30)=>g.append('text').attr('x',xx).attr('y',yy).attr('font-size',size).attr('fill',C.ink).text(value);
text(svg,130,top-105,'Entity',25);text(svg,830,top-105,'Value',25).attr('text-anchor','end');text(svg,1140,top-105,DATA.unit,25);
svg.append('line').attr('x1',115).attr('x2',855).attr('y1',top-70).attr('y2',top-70).attr('stroke',C.quiet);
const table=svg.append('g').attr('id','source-table').selectAll('g.record').data(DATA.records,d=>d.id).join('g').attr('class','record').attr('data-entity-id',d=>d.id).attr('transform',(d,i)=>`translate(0 ${top+i*gap})`);
table.each(function(d){const g=d3.select(this);text(g,130,10,d.label);text(g,830,10,d.value).attr('class','source-value').attr('text-anchor','end')});
const bars=svg.append('g').attr('id','comparison').selectAll('g.mark').data(DATA.records,d=>d.id).join('g').attr('class','mark').attr('data-entity-id',d=>d.id).attr('transform',(d,i)=>`translate(0 ${top+i*gap})`);
bars.append('line').attr('class','value-mark').attr('x1',x(0)).attr('x2',d=>x(d.value)).attr('y1',0).attr('y2',0).attr('stroke',C.ink).attr('stroke-width',2);
bars.append('circle').attr('cx',d=>x(d.value)).attr('cy',0).attr('r',8).attr('fill',C.quiet).attr('stroke','none');
bars.each(function(d){text(d3.select(this),x(d.value)+25,10,d.value,28)});
const axis=svg.append('g').attr('transform',`translate(0 ${axisY})`).call(d3.axisBottom(x).ticks(4).tickSize(6));axis.selectAll('text').attr('font-size',24).attr('fill',C.ink);axis.selectAll('line,path').attr('stroke',C.quiet);
const dot=svg.append('circle').attr('r',8).attr('fill',C.red).attr('stroke',C.white).attr('stroke-width',3);let state;
window.renderAt=(seconds)=>{const t=Math.max(0,Math.min(DATA.duration,+seconds||0)),position=Math.min(DATA.records.length-1e-8,t/DATA.duration*DATA.records.length),index=Math.floor(position),selected=DATA.records[index],u=Math.min(1,(position-index)/.5),q=u*u*(3-2*u),y=top+index*gap;
table.selectAll('text').attr('fill',function(){return this.parentNode.dataset.entityId===selected.id?C.red:C.ink});bars.selectAll('line').attr('stroke',function(){return this.parentNode.dataset.entityId===selected.id?C.red:C.ink});bars.selectAll('circle').attr('fill',function(){return this.parentNode.dataset.entityId===selected.id?C.red:C.quiet}).attr('stroke','none');bars.selectAll('text').attr('fill',function(){return this.parentNode.dataset.entityId===selected.id?C.red:C.ink});
const pulse=1-Math.min(1,(position-index)/.3),guideRadius=9+13*pulse*pulse*(3-2*pulse);dot.attr('r',guideRadius).attr('cx',78+(x(selected.value)-78)*q).attr('cy',y-62-Math.sin(q*Math.PI)*28);state={seconds:t,selectedId:selected.id,value:selected.value,unit:DATA.unit,duration:DATA.duration,palette:'colorset1',d3Version:d3.version,guideColor:C.red,guideRadius};return state;};
window.snapshot=()=>structuredClone(state);window.VIDEO_DATA=DATA;renderAt(0);
})();
</script></body></html>'''


def check_data(raw):
    records=raw.get('records',[])
    if not isinstance(records,list) or not 2<=len(records)<=8:raise ValueError('Provide 2–8 records.')
    ids=set()
    for r in records:
        if not isinstance(r,dict) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}',r.get('id','')) or r['id'] in ids:raise ValueError('Use unique lowercase entity IDs.')
        ids.add(r['id'])
        if not isinstance(r.get('label'),str) or not 1<=len(r['label'])<=22:raise ValueError('Labels must contain 1–22 characters.')
        v=r.get('value')
        if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not 0<=v<=1e9:raise ValueError('Values must be finite, nonnegative and <=1e9.')
    if not isinstance(raw.get('unit'),str) or not 1<=len(raw['unit'])<=24:raise ValueError('Provide a unit of 1–24 characters.')
    duration=raw.setdefault('duration',8)
    if isinstance(duration,bool) or not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration<2:raise ValueError('Duration must be finite and at least two seconds.')
    return raw


def browser_path():
    cache=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.cache')))/'ms-playwright'
    cached=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),key=lambda p:int(p.parts[-3].split('-')[-1]),reverse=True)
    options=[os.environ.get('LINE_WORLD_BROWSER'),*map(str,cached),'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','/usr/bin/chromium','/usr/bin/google-chrome']
    return next((p for p in options if p and Path(p).is_file()),None)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('build','export'));p.add_argument('--project',type=Path,required=True);p.add_argument('--data',type=Path);p.add_argument('--svg',type=Path);p.add_argument('--screenshot',type=Path);p.add_argument('--receipt',type=Path)
    a=p.parse_args();project=a.project.resolve()
    if project.is_relative_to(SKILL):raise ValueError('Keep generated files outside the copied skill.')
    if a.command=='build':
        if not a.data:p.error('--data is required for build.')
        data=check_data(json.loads(a.data.read_text(encoding='utf-8-sig')))
        project.mkdir(parents=True,exist_ok=True)
        if (project/'scene.html').exists():raise ValueError('Refusing to overwrite an existing scene.')
        shutil.copyfile(SKILL/'assets/vendor/d3.v7.9.0.min.js',project/'d3.min.js')
        shutil.copyfile(SKILL/'assets/vendor/D3-LICENSE.txt',project/'D3-LICENSE.txt')
        (project/'data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        (project/'scene.html').write_text(HTML.replace('__DATA__',json.dumps(data).replace('</','<\\/')),encoding='utf-8')
        print(json.dumps({'ok':True,'project':str(project),'duration':data['duration'],'palette':'colorset1'}));return 0
    if not all((a.svg,a.screenshot,a.receipt)):p.error('export requires --svg, --screenshot and --receipt.')
    if importlib.util.find_spec('playwright') is None:
        runner=shutil.which('uv')
        if not runner:raise RuntimeError('Install uv or run this dependency-declaring script with uv run --script.')
        return subprocess.call([runner,'run','--script',str(Path(__file__).resolve()),*sys.argv[1:]])
    from playwright.sync_api import sync_playwright
    for output in (a.svg,a.screenshot,a.receipt):output.resolve().parent.mkdir(parents=True,exist_ok=True)
    data=check_data(json.loads((project/'data.json').read_text(encoding='utf-8')))
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(project)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=browser_path(),headless=True,args=['--disable-gpu'])
            page=browser.new_page(viewport={'width':1920,'height':1080})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/scene.html',wait_until='networkidle')
            samples=[]
            for t in (0,data['duration']/4,data['duration']/2,data['duration']):
                samples.append(page.evaluate('t=>renderAt(t)',t))
            page.evaluate('t=>renderAt(t)',data['duration']/2)
            original=page.locator('#stage').evaluate('e=>e.outerHTML')
            page.evaluate('renderAt(0)');page.evaluate('t=>renderAt(t)',data['duration']/2)
            repeat=page.locator('#stage').evaluate('e=>e.outerHTML')==original
            result=page.evaluate('''() => {const boxes=[...document.querySelectorAll('#stage text')].map(e=>({text:e.textContent,b:e.getBoundingClientRect()}));const outside=boxes.filter(e=>e.b.left<0||e.b.top<0||e.b.right>1920||e.b.bottom>1080).map(e=>e.text),overlaps=[];for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j],area=Math.max(0,Math.min(a.b.right,b.b.right)-Math.max(a.b.left,b.b.left))*Math.max(0,Math.min(a.b.bottom,b.b.bottom)-Math.max(a.b.top,b.b.top));if(area>5)overlaps.push([a.text,b.text])}const ratios=[...document.querySelectorAll('.value-mark')].map((e,i)=>(+e.getAttribute('x2')-+e.getAttribute('x1'))/VIDEO_DATA.records[i].value).filter(Number.isFinite);return {outside,overlaps,sameScale:!ratios.length||Math.max(...ratios)-Math.min(...ratios)<1e-6,values:[...document.querySelectorAll('.source-value')].map(e=>+e.textContent)};}''')
            page.evaluate('t=>renderAt(t)',data['duration'])
            page.screenshot(path=str(a.screenshot.resolve()))
            svg=page.locator('#stage').evaluate('''e=>{const c=e.cloneNode(true);c.setAttribute('width',1920);c.setAttribute('height',1080);c.style.width='1920px';c.style.height='1080px';c.style.fontFamily='Arial, sans-serif';return new XMLSerializer().serializeToString(c)}''')
            a.svg.write_text(svg,encoding='utf-8')
            checks={'labelsWithinFrame':not result['outside'],'pairwiseLabelClearance':not result['overlaps'],'sameZeroBasedScale':result['sameScale'],'sourceValues':result['values']==[r['value'] for r in data['records']],'repeatSeek':repeat,'noBrowserErrors':not errors,'realD3':page.evaluate('d3.version')=='7.9.0'}
            report={'ok':all(checks.values()),'checks':checks,'sourceValues':data['records'],'unit':data['unit'],'palette':'colorset1','d3Version':page.evaluate('d3.version'),'samples':samples,'details':result,'errors':errors}
            a.receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');browser.close()
    finally:server.shutdown();server.server_close()
    print(json.dumps({'ok':report['ok'],'checks':checks}));return 0 if report['ok'] else 2


if __name__=='__main__':
    raise SystemExit(main())
