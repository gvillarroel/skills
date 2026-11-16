#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare project-owned runtime assets and native Mermaid comparison lanes."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
PLUGIN=ROOT/'resources/plugin/skills'
if not PLUGIN.is_dir():PLUGIN=REPO/'projects/line-world-video/artifacts/packages/line-world-video-0.21.1/plugin/skills'
PRIMARY=REPO/'skills/line-world-video' if (REPO/'skills/line-world-video/SKILL.md').is_file() else PLUGIN/'line-world-video'
sys.path.insert(0,str(PRIMARY/'scripts'))
import video_edit as edit

def main():
 p=argparse.ArgumentParser();p.add_argument('--render-diagrams',action='store_true');a=p.parse_args()
 for name in ['composition','svgs','data','manifests','reviews','videos','screenshots','sources','tools']:(ROOT/'artifacts'/name).mkdir(parents=True,exist_ok=True)
 out=ROOT/'artifacts/composition'
 shutil.copyfile(ROOT/'templates/index.html',out/'index.html')
 for name in ['d3.min.js','gsap.min.js','D3-LICENSE.txt']:
  shutil.copyfile(PRIMARY/'assets/vendor'/name,out/name)
 for name in ['space-grotesk.ttf','OFL.txt']:shutil.copyfile(PRIMARY/'assets/fonts'/name,out/name)
 for name in ['focus.js','theme.js']:shutil.copyfile(PRIMARY/'assets/runtime'/name,out/name)
 if not (ROOT/edit.META).is_file():edit.setup(ROOT)
 # Recompile the owned theme so updated runtime rules replace stale generated CSS.
 (ROOT/'theme.css').write_text(edit.theme_css(edit.read(ROOT/'theme.json')),encoding='utf-8')
 shutil.copyfile(ROOT/'theme.css',out/'theme.css')
 diagrams=ROOT/'artifacts/svgs'
 sources={'engineered':'''flowchart LR
accTitle: Engineered visual descriptors
accDescr: Image processing extracts edges and designed descriptors before classification.
    image[Imagen] --> edges[Bordes] --> descriptors[Descriptores] --> classifier[Clasificador]
''','learned':'''flowchart LR
accTitle: Learned visual features
accDescr: A convolutional network learns features from images and predicts an object category.
    input[Imagen] --> learned[Características aprendidas] --> category[Categoría]
'''}
 for name,source in sources.items():(diagrams/(name+'.mmd')).write_text(source,encoding='utf-8')
 config={'theme':'base','htmlLabels':False,'fontFamily':'Arial','themeVariables':{'fontFamily':'Arial','fontSize':'40px','primaryColor':'#ffffff','primaryBorderColor':'#333e48','primaryTextColor':'#333e48','lineColor':'#cfcfcf'},'flowchart':{'htmlLabels':False,'curve':'linear','rankSpacing':100,'nodeSpacing':80,'padding':28,'wrappingWidth':420}}
 (diagrams/'config.json').write_bytes(edit.encode(config))
 cache=Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright';paths=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
 browser=str(paths[0]) if paths else 'C:/Program Files/Google/Chrome/Application/chrome.exe'
 (diagrams/'browser.json').write_bytes(edit.encode({'executablePath':browser,'args':['--no-sandbox']}))
 if a.render_diagrams:
  env={**os.environ,'NPM_CONFIG_CACHE':str(ROOT/'artifacts/tools/npm'),'PUPPETEER_SKIP_DOWNLOAD':'true'}
  for name in sources:
   command=['uv','run','--script',str(PLUGIN/'line-world-mermaid/scripts/animate_mermaid_svg.py'),str(diagrams/(name+'.mmd')),'-o',str(diagrams/(name+'.svg')),'--animation','none','--require-accessibility','--config-file',str(diagrams/'config.json'),'--mmdc-arg=--puppeteerConfigFile','--mmdc-arg='+str(diagrams/'browser.json')]
   subprocess.run(command,cwd=ROOT,env=env,check=True)
 if all((diagrams/(name+'.svg')).is_file() for name in sources):
  (out/'diagrams.js').write_text('window.NATIVE_DIAGRAMS='+json.dumps({k:(diagrams/(k+'.svg')).read_text(encoding='utf-8') for k in sources})+';\n',encoding='utf-8')
 story=edit.read(ROOT/'story.json');(out/'story.js').write_text('window.PRODUCTION='+json.dumps(story,ensure_ascii=False)+';\n',encoding='utf-8')
 cues=edit.read(ROOT/'artifacts/data/cues.json') if (ROOT/'artifacts/data/cues.json').is_file() else {'scenes':[]}
 (out/'cues.js').write_text('window.NARRATION_CUES='+json.dumps(cues,ensure_ascii=False)+';\n',encoding='utf-8')
 if (ROOT/'scripts/scene.js').is_file():shutil.copyfile(ROOT/'scripts/scene.js',out/'scene.js')
 media=edit.read(ROOT/'artifacts/media/manifest.json')['assets'];(out/'media').mkdir(exist_ok=True)
 for asset in media:shutil.copyfile(ROOT/'artifacts/media'/asset['svg'],out/'media'/asset['svg'])
 (out/'media.js').write_text('window.MEDIA_ASSETS='+json.dumps({a['id']:{'image':'media/'+a['svg'],'label':a['label'],'kind':a['kind']} for a in media},ensure_ascii=False)+';\n',encoding='utf-8')
 objects=edit.read(ROOT/'artifacts/media/objects/manifest.json')['assets'];(out/'objects').mkdir(exist_ok=True)
 for asset in objects:
  for variant in asset['variants']:shutil.copyfile(ROOT/'artifacts/media/objects'/variant['png'],out/'objects'/variant['png'])
 (out/'objects.js').write_text('window.DOCUMENTARY_ASSETS='+json.dumps({a['id']:{'variants':{v['id']:{'image':'objects/'+v['png'],'width':v['width'],'height':v['height']} for v in a['variants']}} for a in objects},ensure_ascii=False)+';\n',encoding='utf-8')
 html=(out/'index.html').read_text(encoding='utf-8')
 preview=html.replace('<svg id="stage"','<div id="viewer"><svg id="stage"').replace('</svg></div>','</svg></div></div>')
 preview=preview.replace('</style>','''#viewer{max-width:1280px;aspect-ratio:16/9;margin:auto}#stage{width:100%;height:100%}html,body{overflow:auto;background:#f7f7f7}#controls{max-width:1280px;margin:16px auto;display:flex;gap:12px;padding:12px;font:16px Arial}#seek{flex:1}</style>''')
 controls='''<div id="controls"><button id="play">Play</button><select id="pick"></select><input id="seek" type="range" min="0" step="0.01"><output id="clock"></output></div><script>ready.then(()=>{let i=0,t=0,playing=false,previous=0;const pick=document.querySelector('#pick'),seek=document.querySelector('#seek'),clock=document.querySelector('#clock'),play=document.querySelector('#play');PRODUCTION.scenes.forEach((s,k)=>{const o=document.createElement('option');o.value=k;o.textContent=(k+1)+' · '+s.id;pick.append(o)});function draw(){seek.max=PRODUCTION.scenes[i].clipSeconds;seek.value=t;clock.textContent=t.toFixed(2)+' / '+Number(seek.max).toFixed(2)+' s';renderClip(i,t)}pick.onchange=()=>{i=+pick.value;t=0;draw()};seek.oninput=()=>{t=+seek.value;draw()};play.onclick=()=>{playing=!playing;play.textContent=playing?'Pause':'Play'};function tick(now){if(playing&&previous){t+=Math.min(.1,(now-previous)/1000);if(t>=+seek.max){if(i<PRODUCTION.scenes.length-1){i++;pick.value=i;t=0}else{t=+seek.max;playing=false;play.textContent='Play'}}draw()}previous=now;requestAnimationFrame(tick)}draw();requestAnimationFrame(tick)});</script>'''
 preview=preview.replace('</body>',controls+'</body>');(out/'preview.html').write_text(preview,encoding='utf-8')
 c=edit.config(ROOT);c['sharedInputs']=['scripts/scene.js','theme.css','artifacts/composition/index.html','artifacts/composition/focus.js','artifacts/composition/theme.js','artifacts/composition/d3.min.js','artifacts/composition/space-grotesk.ttf','artifacts/svgs/engineered.svg','artifacts/svgs/learned.svg','artifacts/composition/media.js']+[('artifacts/composition/media/'+a['svg']) for a in media];variants={a['id']:{v['id']:v for v in a['variants']} for a in objects};c['sceneInputs']={s['id']:sorted({'artifacts/composition/objects/'+variants[o['asset']][o['variant']]['png'] for o in s.get('objects',[]) if o.get('asset')}) for s in story['scenes']};c['overviewIds']=[];c['files']['cues']='artifacts/data/cues.json';c['clock']='scene-local';edit.atomic(ROOT/edit.META,edit.encode(c))
 print(json.dumps({'ok':True,'composition':str(out),'diagramCount':sum((diagrams/(k+'.svg')).is_file() for k in sources),'pluginVersion':edit.read(PLUGIN.parent/'plugin.json')['version']}))
if __name__=='__main__':main()
