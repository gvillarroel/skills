#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13", "resvg-py==0.5.0", "numpy>=2,<3"]
# ///
"""Inspect and render the full-frame atlas using the shared capture implementation."""
import functools
import http.server
import json
import math
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from atlas_story import partition_check, coverage, validate_atlas
from color_audit import BROWSER_CHECK as COLOR_CHECK
from content_scan import source_presence, scan as scan_content

CHECKS = r"""() => {
 const state=snapshot(),issues=[],warnings=[],stage=document.querySelector('#stage');
 const normal=s=>{const m=s.match(/^rgb\((\d+), (\d+), (\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):s};
 const ids=[...document.querySelectorAll('[id]')].map(e=>e.id),duplicates=ids.filter((id,i)=>ids.indexOf(id)!==i);
 if(duplicates.length)issues.push('Duplicate SVG IDs: '+[...new Set(duplicates)].join(', '));
 if(document.querySelector('.world-headline,#conclusion'))issues.push('Automatic visible heading.');
 const guide=document.querySelector('#guide-dot'),config=STORY.attention;
 if(normal(getComputedStyle(guide).fill)!=='#9e1b32'||state.guideColor!=='#9e1b32')issues.push('Guide differs from primary red.');
 if(!Number.isFinite(state.guideRadius)||Math.abs(+guide.getAttribute('r')-state.guideRadius)>1e-8||state.guideRadius<config.travelRadius-1e-8||state.guideRadius>config.emitRadius+1e-8)issues.push('Guide radius violates its attention contract.');
 if(document.querySelector('#context-label').textContent!==(STORY.presentation.contextLabels[state.beat]||''))issues.push('Unrequested context label.');
 const paints=new Set();for(const e of stage.querySelectorAll('*')){const cs=getComputedStyle(e);for(const p of ['fill','stroke']){const v=normal(cs[p]);if(v&&v!=='none'&&v!=='rgba(0, 0, 0, 0)'&&!v.startsWith('url('))paints.add(v)}}
 const cell=[...document.querySelectorAll('.atlas-cell')].find(e=>e.dataset.sceneId===state.beat),panels=[];
 if(cell){for(const p of cell.querySelectorAll('.atlas-panel')){
   const surface=p.querySelector('.panel-surface').getBoundingClientRect(),text=[...p.querySelectorAll('text')],short=[];
   const outside=[],labels=[];
   for(const e of text){const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;const b=e.getBoundingClientRect();if(!b.width||!b.height)continue;
     const glyphs=[e,...e.querySelectorAll('tspan')].filter(n=>[...n.childNodes].some(t=>t.nodeType===3&&t.textContent.trim()));
     const size=Math.min(...glyphs.map(n=>parseFloat(getComputedStyle(n).fontSize)*Math.hypot(n.getCTM().a,n.getCTM().b)));
     if(size<18)short.push({text:e.textContent.trim(),size});
     if(e.textContent.trim())labels.push({text:e.textContent.trim(),b});
     if(b.x<surface.x-3||b.y<surface.y-3||b.right>surface.right+3||b.bottom>surface.bottom+3)outside.push(e.textContent.trim());
   }
   const content=p.querySelector('.panel-content'),b=content.getBoundingClientRect();
   panels.push({id:p.dataset.panelId,kind:p.dataset.kind,producer:p.dataset.producer,rect:{x:surface.x,y:surface.y,width:surface.width,height:surface.height},textCount:text.length,shortLabels:short,outside,contentBounds:{x:b.x,y:b.y,width:b.width,height:b.height},markCount:p.querySelectorAll('path,line,circle,polygon,rect').length});
   if(outside.length)issues.push('Panel overflow '+p.dataset.panelId+': '+outside.join(', '));
   for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
     const a=labels[i],b=labels[j],overlap=Math.max(0,Math.min(a.b.right,b.b.right)-Math.max(a.b.left,b.b.left))*Math.max(0,Math.min(a.b.bottom,b.b.bottom)-Math.max(a.b.top,b.b.top)),area=Math.min(a.b.width*a.b.height,b.b.width*b.b.height);
     if(area&&overlap/area>.16)issues.push('Overlapping labels '+p.dataset.panelId+': '+a.text+' / '+b.text);
   }
   if(short.length)warnings.push({panel:p.dataset.panelId,smallLabels:short});
 }}
 const references=[];for(const e of stage.querySelectorAll('[aria-labelledby],[aria-describedby]'))for(const attr of ['aria-labelledby','aria-describedby'])for(const id of(e.getAttribute(attr)||'').split(/\s+/).filter(Boolean))if(!document.getElementById(id))references.push(id);
 if(references.length)issues.push('Missing accessible metadata targets: '+references.join(', '));
 const natives=[...document.querySelectorAll('.atlas-panel[data-producer="mermaid"] > .panel-content > svg')];
 if(natives.some(e=>!e.querySelector(':scope > title')||!e.querySelector(':scope > desc')))issues.push('Native diagram lacks invisible title or description.');
 const ratios=[];for(const r of STORY.rows)for(const phase of ['before','after']){
   const v=document.querySelector('.atlas-'+phase+'-value[data-entity-id="'+r.id+'"]'),mark=document.querySelector('.atlas-'+phase+'-mark[data-entity-id="'+r.id+'"]');
   if(v&&mark){if(+v.textContent!==r[phase])issues.push('Table value differs from the source: '+r.id+'.'+phase);const length=+mark.getAttribute('x2')-+mark.getAttribute('x1');ratios.push(length/r[phase]);}
 }
 if(ratios.length&&Math.max(...ratios)-Math.min(...ratios)>1e-6)issues.push('Paired marks do not use the same zero-based scale.');
 const currentGroup=document.querySelector('.quantity-points[data-scene-id="'+state.beat+'"]'),quantities=[];
 // Quantity flights are part of the explanation, so protect the actual reading
 // labels as well as the primary guide. Preserve every encoded quantity.
 if(cell&&currentGroup&&+getComputedStyle(currentGroup).opacity>.05){
   const labels=[...cell.querySelectorAll('text')].filter(e=>e.textContent.trim()).map(e=>({text:e.textContent.trim(),box:e.getBoundingClientRect()}));
   for(const e of currentGroup.querySelectorAll('circle'))if(+e.getAttribute('opacity')>.05&&+e.getAttribute('r')>0){const b=e.getBoundingClientRect(),x=(b.left+b.right)/2,y=(b.top+b.bottom)/2,r=b.width/2+2;
     for(const label of labels){const q=label.box;if(Math.hypot(x-Math.max(q.left,Math.min(x,q.right)),y-Math.max(q.top,Math.min(y,q.bottom)))<r)issues.push('Quantity point overlaps label: '+label.text);}
   }
 }
 if(currentGroup){for(const row of STORY.rows){const nodes=[...currentGroup.querySelectorAll('circle')].filter(e=>e.dataset.entityId===row.id),points=state.points.filter(p=>p.view===currentGroup.dataset.view&&p.rowId===row.id);
   const quantity=points.reduce((n,p)=>n+p.quantity,0);quantities.push({rowId:row.id,quantity,landed:points.every(p=>p.landed)});
   if(Math.abs(quantity-row.after)>1e-8)issues.push('Point quantities differ from source: '+row.id);
   for(const node of nodes)if(normal(getComputedStyle(node).fill)!==(config.categoryColors[row.id]||'#333e48'))issues.push('Point category color changed: '+row.id);
 }}
 return{state,panels,issues,warnings,quantities,paints:[...paints],nativeCount:natives.length,d3Version:d3.version};
}"""


def main_atlas(args):
    from render_line_world import QuietHandler, browser_path, capture
    project,report_path=args.project.resolve(),args.report.resolve()
    report_path.parent.mkdir(parents=True,exist_ok=True)
    images=report_path.parent/(report_path.stem+"-frames");images.mkdir(exist_ok=True)
    story=validate_atlas(json.loads((project/"story.json").read_text(encoding="utf-8-sig")))
    palette=json.loads((project/"assets/palettes/colorsets.json").read_text())["colorsets"][story["palette"]]
    report={"ok":False,"nativeHyperFrames":False,"mode":"atlas","findings":[],"warnings":[],"samples":[],"coverage":coverage(story),"partitions":[{"id":s["id"],**partition_check(s["panels"])} for s in story["scenePlan"]]}
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(QuietHandler,directory=str(project)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=browser_path(),headless=True,args=["--disable-gpu"])
            page=browser.new_page(viewport={"width":story["width"],"height":story["height"]},device_scale_factor=1)
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/index.html",wait_until="networkidle")
            page.evaluate("document.fonts.ready");page.wait_for_function("typeof renderAt==='function'")
            report['contentSource']=source_presence(page,story['duration'],story['fps'])
            if not report['contentSource']['ok']:report['findings'].append({'issue':'No explanatory object is visible.','intervals':report['contentSource']['emptyIntervals']})
            for beat in story["beats"]:
                times=[beat["start"]+beat["duration"]*.55,beat["end"]-.12]
                scene=next((s for s in story['scenePlan'] if s['id']==beat['id']),None)
                if scene and any(p['kind'] in story['attention']['emissionViews'] and p['producer']=='d3' for p in scene['panels']):
                    hold=(beat['duration']-story['camera']['transitionSeconds'])/4
                    start=.38/len(scene['panels'])+.035
                    span=min(story['attention']['emissionSeconds'],hold*max(.04,1/len(scene['panels'])-start-.025))
                    times += [beat['start']+story['camera']['transitionSeconds']*.25]
                    times += [beat['start']+story['camera']['transitionSeconds']+row*hold+start*hold+span/2+story['attention']['flightSeconds']*.5 for row in range(len(story['rows']))]
                for seconds in times:
                    page.evaluate("t=>renderAt(t)",seconds)
                    data=page.evaluate(CHECKS)
                    color=page.evaluate(COLOR_CHECK)
                    data['colorPriority']=color
                    if not color['ok']:report['findings'].append({'time':seconds,'issue':'Large dark neutral blocks violate the red/gray-first style.','marks':color['darkBlocks']})
                    if seconds>=beat['end']-.121 and any(not q['landed'] for q in data['quantities']):
                        report['findings'].append({'time':seconds,'issue':'A quantity point did not reach its receiver before the scene ended.'})
                    report["findings"].extend({"time":seconds,"issue":v} for v in data["issues"])
                    bad=set(data["paints"])-set(palette["allowed"])
                    if bad:report["findings"].append({"time":seconds,"unsupportedPaint":sorted(bad)})
                    report["warnings"].extend({"time":seconds,**v} for v in data["warnings"])
                    html=page.locator('#stage').evaluate('e=>e.outerHTML')
                    page.evaluate('renderAt(0)');page.evaluate('t=>renderAt(t)',seconds)
                    if page.locator('#stage').evaluate('e=>e.outerHTML')!=html:
                        report["findings"].append({"time":seconds,"issue":"Repeated seek changes the frame."})
                    frame=images/f"{beat['id']}-{seconds:07.2f}.png";frame.write_bytes(capture(page,project,args.capture))
                    report["samples"].append({"time":seconds,"path":str(frame),**data})
            report["findings"].extend({"browserError":v} for v in errors)
            if not args.audit_only and not report["findings"]:
                if not args.output:raise ValueError("--output is required for rendering.")
                output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
                command=["ffmpeg","-y","-v","error","-f","image2pipe","-vcodec","png","-framerate",str(story["fps"]),"-i","pipe:0","-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(output)]
                process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                try:
                    count=round(story["duration"]*story["fps"])
                    for i in range(count):
                        page.evaluate("t=>renderAt(t)",i/story["fps"]);process.stdin.write(capture(page,project,args.capture))
                        if i%(story["fps"]*5)==0:print(f"Captured {i}/{count} frames",flush=True)
                    process.stdin.close();stderr=process.stderr.read().decode(errors="replace")
                    if process.wait():raise RuntimeError(stderr)
                finally:
                    if process.poll() is None:process.kill();process.wait()
                report["media"]={"path":str(output),"expectedFrames":count,"expectedDuration":story["duration"]}
                report['contentEncoded']=scan_content(output,cache=report_path.with_name(report_path.stem+'-content.json'))
                if not report['contentEncoded']['ok']:report['findings'].append({'issue':'Encoded movie has insufficient-content frames.','intervals':report['contentEncoded']['intervals']})
            browser.close()
        sheet=Image.new('RGB',(1440,304*math.ceil(len(report["samples"])/3)),"white");draw=ImageDraw.Draw(sheet)
        for i,s in enumerate(report["samples"]):
            x,y=i%3*480,i//3*304
            with Image.open(s["path"]) as im:sheet.paste(im.resize((480,270)),(x,y))
            draw.text((x+10,y+281),f"{s['time']:.2f}s | {s['state']['beat']}",fill="#333e48")
        contact=report_path.parent/(report_path.stem+"-contact-sheet.jpg");sheet.save(contact,quality=94)
        report.update(contactSheet=str(contact),ok=not report["findings"])
        radii=[s['state']['guideRadius'] for s in report['samples'] if s['state']['beat']!='overview']
        report['attention']={'guideColor':'#9e1b32','minimumSampleRadius':min(radii),'maximumSampleRadius':max(radii),'quantityViews':sorted({p['view'] for s in report['samples'] for p in s['state']['points']}),'categoryColors':story['attention']['categoryColors']}
    except Exception as exc:
        report["findings"].append({"error":str(exc)})
    finally:
        server.shutdown();server.server_close()
        report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ok":report["ok"],"report":str(report_path),"findings":len(report["findings"]),"warnings":len(report["warnings"])}))
    return 0 if report["ok"] else 2
