#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "resvg-py==0.5.0", "pillow>=11,<13"]
# ///
"""Compose original-speed archive panels natively and overlay the shared pure SVG clock."""
import argparse
import concurrent.futures
import functools
import hashlib
import http.server
import io
import json
import math
import re
import subprocess
import sys
import threading
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import resvg_py

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[1]
FONT=ROOT/'composition/space-grotesk.ttf'
sys.path.insert(0,str(REPO/'skills/line-world-video/scripts'))
from inspect_focus import browser_path


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def identity(data):return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def run(command,log):
    with log.open('wb') as out:subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,check=True)


def panel_jobs(story):
    jobs=[]
    for scene in story['scenes']:
        if scene['kind']=='overview':
            for i,item in enumerate(scene['overview']):jobs.append({'id':scene['id']+'-'+str(i),'size':story['layout']['overview'][i],'scene':scene,'segments':[{**item,'start':0,'end':scene['duration'],'duration':scene['duration']}]})
        else:
            jobs.append({'id':scene['id']+'-main','size':story['layout']['main'],'scene':scene,'segments':scene['primary']})
            if scene.get('secondary'):jobs.append({'id':scene['id']+'-tv','size':story['layout']['television'],'scene':scene,'segments':[{'asset':scene['secondary'],'offset':.03,'start':0,'end':scene['duration'],'duration':scene['duration']}]})
    return jobs


def prepare_panel(job,story):
    folder=ROOT/'artifacts/panels';folder.mkdir(parents=True,exist_ok=True)
    output=folder/(job['id']+'.mp4');receipt=output.with_suffix('.json')
    source_ids={s['asset'] for s in job['segments']}
    key=identity({'recipe':2,'segments':job['segments'],'size':job['size'],'fps':story['fps'],'crops':{s:story['crops'][s] for s in source_ids},'source':{s:sha(ROOT/story['media'][s]['file']) for s in source_ids}})
    if receipt.is_file() and output.is_file():
        old=read(receipt)
        if old['key']==key and old['sha256']==sha(output):return old
    clips=[]
    for i,segment in enumerate(job['segments']):
        row=story['media'][segment['asset']];crop=story['crops'][segment['asset']];size=job['size'];frames=round(segment['duration']*story['fps'])
        segment_output=folder/(job['id']+'-'+str(i)+'.mp4')
        vf=f"crop={crop['width']}:{crop['height']}:{crop['x']}:{crop['y']},scale={size['w']}:{size['h']}:force_original_aspect_ratio=decrease:flags=lanczos,pad={size['w']}:{size['h']}:(ow-iw)/2:(oh-ih)/2:white,setsar=1,fps={story['fps']},tpad=stop_mode=clone:stop_duration={segment['duration']},trim=end_frame={frames},setpts=N/({story['fps']}*TB)"
        command=['ffmpeg','-y','-v','error','-threads','2','-filter_threads','2','-ss',str(segment['offset']),'-i',str(ROOT/row['file']),'-an','-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-threads','2',str(segment_output)]
        run(command,folder/(job['id']+'-'+str(i)+'.log'));clips.append(segment_output)
    listing=folder/(job['id']+'.concat.txt');listing.write_text(''.join("file '"+p.name+"'\n" for p in clips),encoding='utf-8')
    temporary=output.with_name(output.stem+'.pending.mp4')
    run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-an','-movflags','+faststart',str(temporary)],folder/(job['id']+'-concat.log'))
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,nb_read_frames','-of','json',str(temporary)],text=True))['streams'][0]
    if int(probe['nb_read_frames'])!=job['scene']['frames']:raise ValueError('Panel frame budget differs: '+job['id'])
    temporary.replace(output);result={'id':job['id'],'key':key,'sha256':sha(output),'file':str(output.relative_to(ROOT)),'frames':job['scene']['frames'],'segments':job['segments'],'size':job['size'],'sourcePolicy':'Original playback speed; native frame-rate conversion, conservative matte crop, aspect-preserving fit and declared end-frame holds. No loops, reversal, interpolation or synthesized footage.'}
    save(receipt,result);print(json.dumps({'panel':job['id'],'frames':result['frames']}),flush=True);return result


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def send_head(self):
        path=Path(self.translate_path(self.path));self.remaining=None
        if path.is_file() and path.suffix.lower() in {'.mp4','.wav'}:
            size=path.stat().st_size;match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
            start=int(match[1]) if match else 0;end=min(size-1,int(match[2])) if match and match[2] else size-1
            if start> end or start>=size:self.send_error(416);return None
            self.send_response(206 if match else 200);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
            if match:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers();source=path.open('rb');source.seek(start);self.remaining=end-start+1;return source
        return super().send_head()
    def copyfile(self,source,out):
        try:
            if self.remaining is None:return super().copyfile(source,out)
            while self.remaining:
                block=source.read(min(65536,self.remaining))
                if not block:break
                out.write(block);self.remaining-=len(block)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass


def png(svg):return resvg_py.svg_to_bytes(svg_string=svg,font_files=[str(FONT)],skip_system_fonts=True)


def panel_frame(file,frame_index):
    # Select the decoded frame identity: timestamp seeking can round beyond the
    # final sample in a concatenated MP4 even when its frame budget is correct.
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-vf',rf'select=eq(n\,{frame_index})','-fps_mode','passthrough','-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    if not data:raise ValueError('No source panel frame: '+str(file))
    return Image.open(io.BytesIO(data)).convert('RGBA')


def normalize_scene(output,record):
    prior=record.get('rangeNormalization')
    if prior and prior.get('version')==2:
        return record
    # A JPEG outgoing plate can propagate its full-range flag through an overlay.
    # Convert actual decoded colors once, then tag every scene consistently.
    original=ROOT/prior['input'] if prior else ROOT/'artifacts/videos/range-sources'/(record['id']+'-'+record['sha256'][:12]+'.mp4')
    original_sha=prior['inputSha256'] if prior else record['sha256']
    original.parent.mkdir(parents=True,exist_ok=True)
    if not original.is_file():
        import shutil
        shutil.copyfile(output,original)
    if sha(original)!=original_sha:raise ValueError('The pre-normalization source changed.')
    pending=output.with_name(output.stem+'.range.pending.mp4')
    run(['ffmpeg','-y','-v','error','-threads','2','-filter_threads','2','-i',str(original),'-an','-vf','format=rgb24,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:colorspace=bt709,setsar=1','-frames:v',str(record['frames']),'-c:v','libx264','-crf','17','-preset','fast','-threads','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(pending)],output.with_suffix('.range.log'))
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-count_frames','-of','json',str(pending)],text=True))['streams'][0]
    if probe['pix_fmt']!='yuv420p' or probe.get('color_range')!='tv' or int(probe['nb_read_frames'])!=record['frames']:raise ValueError('Scene color/frame normalization failed.')
    pending.replace(output)
    record['rangeNormalization']={'version':2,'input':original.relative_to(ROOT).as_posix(),'inputSha256':original_sha,'policy':'Decode the actual input to RGB before conversion to consistently tagged limited-range BT.709. Preserve authored colors, frame identities and duration; never retag existing YUV samples as a substitute for conversion.'}
    record['sha256']=sha(output);save(output.with_suffix('.json'),record)
    return record


def outgoing(page,scene,story):
    # The guide-free transition plate is composed from actual prepared panel pixels,
    # plus exactly the same final SVG state. It never repaints source footage.
    image=Image.new('RGBA',(1920,1080),'white');placements=page.evaluate('(id)=>layoutFor(STORY.scenes.find(s=>s.id===id))',scene['id'])
    for p in placements:
        source=ROOT/'artifacts/panels'/Path(p['file']).name
        frame=panel_frame(source,scene['frames']-1)
        image.alpha_composite(frame,(p['x'],p['y']))
    svg=page.evaluate('([t])=>overlaySvg(t,{guide:false})',[scene['end']-1/story['fps']])
    image.alpha_composite(Image.open(io.BytesIO(png(svg))).convert('RGBA'))
    output=ROOT/'artifacts/stills'/(scene['id']+'-outgoing.jpg');output.parent.mkdir(parents=True,exist_ok=True);image.convert('RGB').save(output,quality=96)
    return output


def audit(page,story):
    return page.evaluate('''()=>{
      const findings=[],samples=[],coverage=[];
      for(const scene of STORY.scenes){
        const plan=scenePlan(scene);let visited=0;
        for(let frame=0;frame<scene.frames;frame++){
          const t=frame/STORY.fps,state=renderAt(scene.start+t),p=state.focus,r=p.radius+4;
          if(p.x-r<0||p.x+r>1920||p.y-r<0||p.y+r>1080)findings.push({scene:scene.id,t,kind:'guide-outside-stage'});
          if(t>=scene.panSeconds)for(const box of plan.obstacles){
            if(p.x+r>box.x0&&p.x-r<box.x1&&p.y+r>box.y0&&p.y-r<box.y1){findings.push({scene:scene.id,t,kind:'guide-over-content',target:p.target});break;}
          }
          visited++;
        }
        for(const cue of scene.cues){
          const state=renderAt(scene.start+cue.at),reading=LineWorldFocus.audit(document.querySelector('#stage'));
          if(!reading.ok)findings.push({scene:scene.id,t:cue.at,kind:'svg-reading',issues:reading.issues});
          samples.push({scene:scene.id,time:scene.start+cue.at,target:cue.target,observedTarget:state.focus.target,reading});
          if(state.focus.target!==cue.target)findings.push({scene:scene.id,t:cue.at,kind:'cue-target-mismatch'});
        }
        coverage.push({scene:scene.id,frames:visited});
      }
      const t=STORY.scenes[2].start+8;
      renderAt(t);const first=overlaySvg(t);renderAt(1);const again=overlaySvg(t);
      if(first!==again)findings.push({kind:'repeat-seek-state'});
      return{ok:!findings.length,findings,samples,coverage,repeatSeekIdentical:first===again};
    }''')


def render_scene(page,scene,index,story,receipts):
    folder=ROOT/'artifacts/videos/clips';folder.mkdir(parents=True,exist_ok=True)
    output=folder/(f'{index+1:02}-'+scene['id']+'.mp4');receipt=output.with_suffix('.json')
    previous=ROOT/'artifacts/stills'/(story['scenes'][index-1]['id']+'-outgoing.jpg') if index else None
    key=identity({'recipe':3,'scene':scene,'story':sha(ROOT/'composition/story.js'),'graphics':sha(ROOT/'composition/scene.js'),'focus':sha(ROOT/'composition/focus.js'),'gentle':sha(ROOT/'composition/gentle-motion.js'),'font':sha(FONT),'panels':{p['id']:p['sha256'] for p in receipts if p['id'].startswith(scene['id']+'-')},'previous':sha(previous) if previous else None})
    if output.is_file() and receipt.is_file():
        old=read(receipt)
        if old['key']==key and old['sha256']==sha(output):
            old=normalize_scene(output,old);outgoing(page,scene,story);return old
    placements=page.evaluate('(id)=>layoutFor(STORY.scenes.find(s=>s.id===id))',scene['id'])
    command=['ffmpeg','-y','-v','error','-threads','2','-filter_complex_threads','2']
    for p in placements:command+=['-i',str(ROOT/'artifacts/panels'/Path(p['file']).name)]
    graphics_index=len(placements);command+=['-f','image2pipe','-framerate',str(story['fps']),'-vcodec','png','-i','pipe:0']
    if previous:previous_index=graphics_index+1;command+=['-loop','1','-i',str(previous)]
    pan=scene['panSeconds']
    u=f'min(t/{pan},1)' if pan else '1'
    easing=f'(3*pow({u},2)-2*pow({u},3))'
    shift=f'1920*(1-{easing})' if pan else '0'
    filters=[f"color=c=white:s=1920x1080:r={story['fps']}:d={scene['duration']}[base]"]
    current='base'
    if previous:
        filters.append(f"[{current}][{previous_index}:v]overlay=x='-1920*{easing}':y=0:enable='lt(t,{pan})':eof_action=pass[prior]");current='prior'
    for i,p in enumerate(placements):
        source=f'{i}:v'
        if p.get('camera'):
            c=p['camera'];at=f'(on/{story["fps"]})'
            enter=f'max(0,min(1,({at}-{c["start"]})/{c["inSeconds"]}))';leave=f'max(0,min(1,({at}-{c["start"]+c["inSeconds"]+c["holdSeconds"]})/{c["outSeconds"]}))'
            smooth=lambda u:f'(3*pow({u},2)-2*pow({u},3))'
            zoom=f'1+{c["zoom"]-1}*{smooth(enter)}*(1-{smooth(leave)})';cx=(c['focus'][0]+c['focus'][2])/2;cy=(c['focus'][1]+c['focus'][3])/2
            source='camera'+str(i)
            filters.append(f"[{i}:v]scale=iw*3:ih*3:flags=lanczos,zoompan=z='{zoom}':x='max(0,min(iw-iw/zoom,{cx}*iw-iw/(2*zoom)))':y='max(0,min(ih-ih/zoom,{cy}*ih-ih/(2*zoom)))':d=1:s={p['w']}x{p['h']}:fps={story['fps']}[{source}]")
        label='panel'+str(i);filters.append(f"[{current}][{source}]overlay=x='{p['x']}+{shift}':y={p['y']}:eof_action=repeat[{label}]");current=label
    filters.append(f'[{current}][{graphics_index}:v]overlay=0:0:shortest=1,format=yuv420p[final]')
    temporary=output.with_name(output.stem+'.pending.mp4')
    command+=['-filter_complex',';'.join(filters),'-map','[final]','-an','-frames:v',str(scene['frames']),'-r',str(story['fps']),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(temporary)]
    with (folder/(scene['id']+'-render.log')).open('wb') as log:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
        try:
            # Batch browser IPC and bound raster work while preserving frame order.
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as rasters:
                for first in range(0,scene['frames'],30):
                    times=[scene['start']+frame/story['fps'] for frame in range(first,min(scene['frames'],first+30))]
                    svgs=page.evaluate('times=>times.map(t=>overlaySvg(t))',times)
                    for data in rasters.map(png,svgs):process.stdin.write(data)
                    if first%300==0:print(json.dumps({'scene':scene['id'],'frame':first,'total':scene['frames']}),flush=True)
            process.stdin.close();code=process.wait(timeout=90)
            if code:raise ValueError('FFmpeg composition failed; inspect '+scene['id']+'-render.log')
        except BaseException:
            if process.poll() is None:process.kill();process.wait()
            raise
    temporary.replace(output);record={'key':key,'id':scene['id'],'sha256':sha(output),'frames':scene['frames'],'seconds':scene['duration'],'file':output.relative_to(ROOT).as_posix(),'nativeHyperFrames':False,'renderer':'Original archive panels composed natively with FFmpeg; shared pure SVG clock via Playwright/resvg.'}
    save(receipt,record);record=normalize_scene(output,record);outgoing(page,scene,story);return record


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--panels-only',action='store_true');parser.add_argument('--audit-only',action='store_true');args=parser.parse_args()
    story=read(ROOT/'story.json');jobs=panel_jobs(story)
    if args.audit_only:
        receipts=[read(ROOT/'artifacts/panels'/(job['id']+'.json')) for job in jobs]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:receipts=list(pool.map(lambda job:prepare_panel(job,story),jobs))
    save(ROOT/'artifacts/manifests/panels.json',receipts)
    if args.panels_only:return
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            chrome=browser_path();browser=pw.chromium.launch(executable_path=chrome,headless=True)
            page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            page.goto(f'http://127.0.0.1:{server.server_port}/composition/index.html?graphics=1')
            page.evaluate('async()=>{await window.ready;}')
            report=audit(page,story);save(ROOT/'artifacts/reviews/source-audit.json',report)
            print(json.dumps({'sourceAudit':report['ok'],'findings':len(report['findings']),'frames':sum(r['frames'] for r in report['coverage'])}),flush=True)
            if not report['ok']:raise ValueError('Fix the source audit before rendering.')
            if args.audit_only:
                preview_reports=[]
                for scene in story['scenes']:
                    t=scene['start']+scene['cues'][1]['at']+.1
                    page.evaluate('async t=>await seekMedia(t)',t)
                    preview_reports.append(page.evaluate('''()=>({viewport:[innerWidth,innerHeight],scroll:[scrollX,scrollY],stage:document.querySelector('#stage').getBoundingClientRect().toJSON(),media:[...document.querySelectorAll('video')].map(e=>({id:e.dataset.id,display:getComputedStyle(e).display,rect:e.getBoundingClientRect().toJSON(),src:e.src,time:e.currentTime,width:e.videoWidth,height:e.videoHeight,ready:e.readyState}))})'''))
                    page.screenshot(path=str(ROOT/'artifacts/images'/(scene['id']+'-preview.png')))
                save(ROOT/'artifacts/reviews/preview.json',preview_reports)
            else:
                records=[render_scene(page,scene,i,story,receipts) for i,scene in enumerate(story['scenes'])]
                save(ROOT/'artifacts/manifests/render.json',{'ok':True,'scenes':records,'frames':story['frames'],'seconds':story['duration'],'nativeGoogleVidsExport':False,'nativeHyperFrames':False})
            browser.close()
    finally:server.shutdown();server.server_close()
    if not args.audit_only:
        request={'fps':story['fps'],'voice':{'file':'artifacts/audio/voice.wav','provenance':'Microsoft Edge speech via edge-tts, es-CL-CatalinaNeural; actual decoded audio and word boundaries. Local narration, not Google Vids.'},'scenes':[{'id':scene['id'],'clip':f'artifacts/videos/clips/{i+1:02}-{scene["id"]}.mp4','voiceSeconds':scene['duration']} for i,scene in enumerate(story['scenes'])]}
        save(ROOT/'assembly.json',request)
        subprocess.run(['uv','run','--script',str(REPO/'skills/line-world-video/scripts/project_delivery.py'),'assemble','--request',str(ROOT/'assembly.json'),'--output',str(ROOT/'artifacts/videos/sixties-lifestyle.mp4'),'--report',str(ROOT/'artifacts/reviews/assembly.json'),'--replace'],check=True)


if __name__=='__main__':main()
