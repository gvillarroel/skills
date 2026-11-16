#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26,<2", "playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Check paper table values, original-source guide poses and actual encoded frames."""
import argparse,functools,hashlib,http.server,json,math,os,re,subprocess,threading
from pathlib import Path
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright
import pymupdf
ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--native',action='store_true');args=parser.parse_args()
 story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'));project=ROOT/'artifacts/composition';out=ROOT/'artifacts/reviews'/('encoded-native' if args.native else 'encoded');out.mkdir(exist_ok=True)
 report={'ok':False,'nativeGoogleVids':args.native,'tableChecks':[],'guideChecks':[],'reviewFrames':[],'errors':[]};video=ROOT/'artifacts/videos'/('seal-google-vids-final.mp4' if args.native else 'seal-paper-final.mp4')
 with pymupdf.open(project/'source.pdf') as pdf:
  t1=[float(w[4]) for w in pdf[6].get_text('words') if w[0]>350 and 80<w[1]<130 and re.fullmatch(r'\d+(?:\.\d+)?',w[4])]
  actual=[r['values'][0] for r in story['scenes'][3]['chart']['rows']]
  report['tableChecks'].append({'source':'Table 1, PDF page 7','original':t1,'chart':actual,'ok':t1==actual})
  numbers=[float(w[4]) for w in pdf[7].get_text('words') if 68<w[1]<156 and re.fullmatch(r'\d+\.\d+',w[4])]
  original=[numbers[i:i+3] for i in range(0,len(numbers),3)];actual=[r['values'] for r in story['scenes'][4]['chart']['rows']]
  report['tableChecks'].append({'source':'Table 2, PDF page 8','original':original,'chart':actual,'ok':original==actual})
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(project)));threading.Thread(target=server.serve_forever,daemon=True).start()
 wanted={};cue_samples=[];offset=0
 cache=Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright';paths=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),key=lambda p:int(p.parts[-3].split('-')[-1]),reverse=True)
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True);page=browser.new_page(viewport={'width':1920,'height':1080});page.goto(f'http://127.0.0.1:{server.server_port}/index.html?capture=1');page.evaluate('async()=>await ready')
   for i,s in enumerate(story['scenes']):
    frames=round(s['duration']*30)
    for t in [0,.4,.8,*[v for c in s['cues'] for v in [c['at'],min(c['at']+.9,s['duration']-1/30)]]]:
     n=round(t*30);state=page.evaluate('([i,t])=>renderClip(i,t)',[i,n/30]);global_n=offset+n;wanted[global_n]={'scene':s['id'],'localSeconds':n/30,'state':state}
    for c in s['cues']:cue_samples.append((offset+round(c['at']*30),s['id'],c['target']))
    offset+=frames
   browser.close()
 finally:server.shutdown();server.server_close()
 ordered=sorted(wanted);expr='+'.join(f'eq(n\\,{n})' for n in ordered)
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-an','-sn','-vf','select='+expr,'-vsync','0',str(out/'frame-%03d.png')],check=True)
 files=sorted(out.glob('frame-*.png'))
 if len(files)!=len(ordered):raise ValueError('Encoded frame extraction count differs from the planned review.')
 by_n=dict(zip(ordered,files))
 for n,sid,target in cue_samples:
  state=wanted[n]['state'];g=state['guide'];x,y=round(g['x']),round(g['y']);r=max(2,round(g['r']/3))
  with Image.open(by_n[n]) as im:rgb=[round(v,2) for v in ImageStat.Stat(im.convert('RGB').crop((x-r,y-r,x+r+1,y+r+1))).median]
  delta=max(abs(a-b) for a,b in zip(rgb,[158,27,50]));report['guideChecks'].append({'scene':sid,'target':target,'frame':n,'seconds':n/30,'rgb':rgb,'maximumChannelDelta':delta,'ok':delta<=30})
 for k in range(0,len(files),12):
  batch=files[k:k+12];sheet=Image.new('RGB',(1920,math.ceil(len(batch)/3)*360),'white')
  for j,p in enumerate(batch):
   with Image.open(p) as im:sheet.paste(im.resize((640,360)),((j%3)*640,(j//3)*360))
  sheet.save(out/f'sheet-{k//12+1:02}.jpg',quality=93)
 report.update(videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),reviewFrames=[{'frame':n,'seconds':n/30,'file':str(by_n[n]),**wanted[n]} for n in ordered])
 report['ok']=all(v['ok'] for v in report['tableChecks']+report['guideChecks']) and not any(v['state']['issues'] for v in report['reviewFrames'])
 report['scope']='Original PDF numeric extraction versus every derived table value; encoded primary-red guide arrivals and sampled zooms/joins. Full source trajectories and all-frame presence are separate receipts. Raster diagram typography requires manual visual review.'
 (ROOT/'artifacts/reviews'/('native-encoded-review.json' if args.native else 'encoded-review.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'ok':report['ok'],'tableValues':len(t1)+len(numbers),'guideArrivals':len(cue_samples),'frames':len(files),'failures':[v for v in report['tableChecks']+report['guideChecks'] if not v['ok']]}))
 return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
