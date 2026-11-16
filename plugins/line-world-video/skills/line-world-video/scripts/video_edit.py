#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect, patch and cache project-owned video data with compact deterministic reports."""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,re,tempfile
from pathlib import Path

SKILL=Path(__file__).resolve().parent.parent
THEME={'schemaVersion':1,'palette':'colorset1','colors':{'background':'#ffffff','surface':'#ffffff','primary':'#9e1b32','secondaryHighlight':'#696969','ink':'#333e48','muted':'#696969','line':'#828282','quiet':'#e7e7e7'},'fontScale':1,'lineWidth':2}
META='.line-world/editing.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def encode(v):return (json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def signature(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(root,value):
 p=(root/value).resolve()
 if not p.is_relative_to(root) or p==root:raise ValueError('Use a file inside the project.')
 return p
def input_path(root,value):
 path=Path(value);current=path.resolve()
 if path.is_absolute():return current
 project=inside(root,path)
 matches=list(dict.fromkeys(p for p in [current,project] if p.is_file()))
 if len(matches)>1:raise ValueError('Ambiguous input file; use an explicit path to the intended patch or receipts.')
 if not matches:raise ValueError('Input file was not found in the working directory or project: '+str(path))
 return matches[0]
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(prefix='.edit-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as stream:stream.write(data)
  os.replace(name,path)
 finally:
  if Path(name).exists():Path(name).unlink()
def transaction(writes):
 saved={p:p.read_bytes() if p.exists() else None for p in writes}
 try:
  for p,data in writes.items():
   if data is None:
    if p.exists():p.unlink()
   elif saved[p]!=data:atomic(p,data)
 except Exception:
  for p,data in saved.items():
   if data is None:
    if p.exists():p.unlink()
   else:atomic(p,data)
  raise
 return saved
def finite(v):return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
def validate_theme(raw):
 t=copy.deepcopy(THEME)
 if not isinstance(raw,dict) or set(raw)-set(t):raise ValueError('Unsupported theme field.')
 for k,v in raw.items():
  if k=='colors':
   if not isinstance(v,dict) or set(v)-set(t['colors']):raise ValueError('Use the declared semantic color roles.')
   t[k].update(v)
  else:t[k]=v
 if t['schemaVersion']!=1 or t['palette'] not in ['colorset1','colorset2']:raise ValueError('Theme schemaVersion/palette is invalid.')
 palette=read(SKILL/'assets/palettes/video-colors.json')['colorsets'][t['palette']]['allowed']
 if any(v not in palette for v in t['colors'].values()):raise ValueError('Use exact bundled palette tokens.')
 if t['colors']['primary']!='#9e1b32':raise ValueError('Keep the primary guide red #9e1b32.')
 if not finite(t['fontScale']) or not .75<=t['fontScale']<=1.5:raise ValueError('fontScale must be between 0.75 and 1.5; recheck label clearance.')
 if not finite(t['lineWidth']) or not .5<=t['lineWidth']<=4:raise ValueError('lineWidth must be between 0.5 and 4.')
 return t
def theme_css(raw):
 t=validate_theme(raw);variables={**t['colors'],'fontScale':t['fontScale'],'lineWidth':str(t['lineWidth'])+'px'}
 key=lambda k:re.sub(r'[A-Z]',lambda m:'-'+m[0].lower(),k)
 return (SKILL/'assets/runtime/theme.css').read_text(encoding='utf-8')+'\n:root{'+''.join('--lw-'+key(k)+':'+str(v)+';' for k,v in variables.items())+'}\n'
def validate_document(value,kind):
 if not isinstance(value,dict):raise ValueError('Editable JSON documents must be objects.')
 if kind=='theme':return validate_theme(value)
 if kind=='story' and 'rows' in value and ('timing' in value or value.get('mode')=='atlas'):
  import importlib
  module=importlib.import_module('line_world' if (Path(__file__).parent/'line_world.py').is_file() else 'story');module.validate(value)
 scenes=value.get('scenes',[])
 if not isinstance(scenes,list):raise ValueError('scenes must be a list.')
 if any(not isinstance(s,dict) for s in scenes):raise ValueError('Each scene must be an object.')
 ids=[s.get('id') for s in scenes]
 if any(not isinstance(v,str) or not v for v in ids) or len(ids)!=len(set(ids)):raise ValueError('Scenes need unique nonempty stable IDs.')
 for scene in scenes:
  duration=scene.get('clipSeconds',scene.get('duration'))
  if duration is not None and (not finite(duration) or duration<=0):raise ValueError('Scene duration must be finite and positive.')
  essential=scene.get('essentialAnimationSeconds')
  if essential is not None and (not finite(essential) or essential<0 or duration is not None and essential>duration):raise ValueError('Essential animation must fit within the scene budget.')
  if 'script' in scene and (not isinstance(scene['script'],str) or not scene['script'].strip()):raise ValueError('Narration must be nonempty text.')
  cues=scene.get('cues',[])
  if not isinstance(cues,list):raise ValueError('cues must be a list.')
  last=-1
  for c in cues:
   if not isinstance(c,dict):raise ValueError('Each cue must be an object.')
   if not isinstance(c.get('target'),str) or not c['target']:raise ValueError('Each cue needs a target.')
   if 'at' in c:
    if not finite(c['at']) or c['at']<last or c['at']<0 or duration is not None and c['at']>duration:raise ValueError('Cue arrivals must follow scene-local time within its duration.')
    last=c['at']
   if 'travelSeconds' in c and (not finite(c['travelSeconds']) or not .1<=c['travelSeconds']<=.45):raise ValueError('Cue travelSeconds must be between 0.1 and 0.45.')
 return value
def segments(path):
 if not isinstance(path,str) or not path:raise ValueError('Provide a nonempty semantic path.')
 parts=[];start=0;depth=0
 for i,char in enumerate(path):
  if char=='[':depth+=1
  if char==']':depth-=1
  if char=='.' and depth==0:parts.append(path[start:i]);start=i+1
 parts.append(path[start:]);result=[]
 for part in parts:
  match=re.fullmatch(r'([A-Za-z_][A-Za-z0-9_-]*)(?:\[([A-Za-z_][A-Za-z0-9_-]*)=([^\]]+)\])?',part)
  if not match:raise ValueError('Use paths such as scenes[id=split].cues[id=test].travelSeconds.')
  name,key,expected=match.groups()
  if expected is not None:
   try:expected=json.loads(expected)
   except json.JSONDecodeError:pass
  result.append((name,key,expected))
 return result
def locate(document,path,parent=False):
 parts=segments(path);node=document
 for n,(name,key,expected) in enumerate(parts):
  if parent and n==len(parts)-1:
   if key:raise ValueError('Set a field of the selected object rather than replacing a selected list item.')
   if not isinstance(node,dict):raise ValueError('The parent is not an object.')
   if name not in node:raise ValueError('Unknown path field '+name+'; inspect the object first.')
   return node,name
  if not isinstance(node,dict) or name not in node:raise ValueError('Unknown path field '+name+'; available: '+', '.join(list(node)[:12]) if isinstance(node,dict) else 'Path does not select an object.')
  node=node[name]
  if key:
   if not isinstance(node,list):raise ValueError('Selectors require a list.')
   matches=[v for v in node if isinstance(v,dict) and v.get(key)==expected]
   if len(matches)!=1:raise ValueError('Selector '+name+'['+key+'='+str(expected)+'] matched '+str(len(matches))+' objects; use a unique ID or phrase.')
   node=matches[0]
 return node
def config(root):
 p=inside(root,META)
 if not p.is_file():raise ValueError('Run setup once to register editable project files.')
 c=read(p)
 if c.get('schemaVersion')!=1 or not isinstance(c.get('files'),dict) or not {'story','theme'}<=set(c['files']) or set(c['files'])-{'story','theme','cues'}:raise ValueError('Invalid editing file registry.')
 if len(set(c['files'].values()))!=len(c['files']):raise ValueError('Editable files must be distinct.')
 if c.get('clock') not in ['global','scene-local'] or not isinstance(c.get('continuous'),bool):raise ValueError('Invalid cache clock or continuity mode.')
 if any(str(v).replace('\\','/').startswith('.line-world/') for v in c['files'].values()):raise ValueError('Editable data cannot replace editing metadata.')
 for rel in [*c['files'].values(),*c.get('sharedInputs',[]),*sum(c.get('sceneInputs',{}).values(),[])]:inside(root,rel)
 return c
def documents(root,c):return {k:validate_document(read(inside(root,v)),k) for k,v in c['files'].items()}
def setup(root,story='story.json',cues=None):
 if (SKILL/'SKILL.md').is_file() and root.is_relative_to(SKILL):raise ValueError('Keep the skill read-only.')
 root.mkdir(parents=True,exist_ok=True)
 if inside(root,META).exists():raise ValueError('Editing configuration already exists.')
 if not inside(root,story).is_file():raise ValueError('Provide an existing story.json.')
 files={'story':story,'theme':'theme.json'}
 if cues:files['cues']=cues
 if len(set(files.values()))!=len(files):raise ValueError('Editable aliases must reference different files.')
 source=read(inside(root,story));theme=copy.deepcopy(THEME)
 if source.get('palette') in ['colorset1','colorset2']:theme['palette']=source['palette']
 docs={k:validate_document(read(inside(root,p)) if inside(root,p).exists() else theme if k=='theme' else read(inside(root,p)),k) for k,p in files.items()}
 # Track the known local renderer and its static resources; declare extra inputs explicitly.
 shared=[p for p in ['scene.js','index.html'] if inside(root,p).is_file()]
 shared+=sorted(p.relative_to(root).as_posix() for p in (root/'assets').rglob('*') if p.is_file() and 'node_modules' not in p.parts)
 c={'schemaVersion':1,'files':files,'sharedInputs':shared,'sceneInputs':{},'overviewIds':['overview'],'clock':'global' if 'timing' in source or source.get('mode')=='atlas' else 'scene-local','continuous':True}
 css=theme_css(docs['theme']).encode();css_path=inside(root,'theme.css')
 if css_path.exists() and css_path.read_bytes()!=css:raise ValueError('Preserve existing authored theme.css; move it before setup or integrate the generated theme explicitly.')
 writes={css_path:css,inside(root,META):encode(c)}
 if not inside(root,'theme.json').exists():writes[inside(root,'theme.json')]=encode(docs['theme'])
 transaction(writes);return {'ok':True,'files':files,'clock':c['clock'],'trackedSharedInputs':len(shared),'next':'inspect, plan/apply, status and record'}
def compact(value,budget=2400):
 full=json.dumps(value,ensure_ascii=False,separators=(',',':'))
 if len(full)<=budget:return value
 if isinstance(value,list):return {'count':len(value),'ids':[v.get('id',v.get('target')) for v in value[:24] if isinstance(v,dict)],'truncated':True}
 if isinstance(value,dict):return {'keys':list(value),'lists':{k:len(v) for k,v in value.items() if isinstance(v,list)},'truncated':True}
 return {'preview':full[:budget],'truncated':True}
def inspect(root,alias,path=None):
 c=config(root)
 if alias not in c['files']:raise ValueError('Unknown file alias.')
 p=inside(root,c['files'][alias]);data=read(p);value=locate(data,path) if path else data
 return {'ok':True,'file':alias,'sha256':sha(p),'path':path,'value':compact(value)}
def changed_plan(root,patch):
 c=config(root);before=documents(root,c);after=copy.deepcopy(before);changes=[]
 if not isinstance(patch,dict) or set(patch)-{'changes','expectedSha256'}:raise ValueError('Patch supports changes and expectedSha256.')
 if not isinstance(patch.get('changes'),list) or not patch['changes']:raise ValueError('Provide a nonempty changes array.')
 for alias,expected in patch.get('expectedSha256',{}).items():
  if alias not in c['files'] or sha(inside(root,c['files'][alias]))!=expected:raise ValueError('Stale input fingerprint for '+alias)
 for op in patch['changes']:
  if not isinstance(op,dict) or set(op)-{'file','path','value','expect'} or 'value' not in op:raise ValueError('Each change needs file, path and value; expect is optional.')
  alias=op.get('file','story')
  if alias not in after:raise ValueError('Unknown or missing editable file alias '+str(alias))
  parent,key=locate(after[alias],op['path'],True);old=parent.get(key)
  if key=='id':raise ValueError('Stable IDs are immutable in field patches; author a deliberate structural revision instead.')
  if 'expect' in op and old!=op['expect']:raise ValueError('Expected prior value differs at '+op['path'])
  if old!=op['value']:parent[key]=copy.deepcopy(op['value']);changes.append({'file':alias,'path':op['path'],'before':old,'after':op['value']})
 for kind,value in after.items():validate_document(value,kind)
 # Existing aligned cues cannot extend beyond a revised scene budget.
 by_id={s['id']:s for s in after['story'].get('scenes',[])}
 for scene in after.get('cues',{}).get('scenes',[]):
  if by_id and scene['id'] not in by_id:raise ValueError('Cue references an unknown story scene.')
  budget=by_id.get(scene['id'],{});duration=budget.get('clipSeconds',budget.get('duration'))
  if duration and any(cue.get('at',0)>duration for cue in scene.get('cues',[])):raise ValueError('A cue exceeds its story scene budget.')
 return c,before,after,changes
def apply(root,patch,dry=False):
 c,before,after,changes=changed_plan(root,patch);changed=any(signature(before[k])!=signature(after[k]) for k in before)
 report={'ok':True,'changed':changed,'dryRun':dry,'changes':compact(changes),'changedFiles':[k for k in before if signature(before[k])!=signature(after[k])],'narrationReview':any(op['file']=='story' and any(w in op['path'].split('.')[-1] for w in ['script','voice','language']) for op in changes),'localOnly':True}
 if dry or not changed:return report
 writes={inside(root,c['files'][k]):encode(v) for k,v in after.items() if signature(before[k])!=signature(v)}
 if 'theme' in report['changedFiles']:writes[inside(root,'theme.css')]=theme_css(after['theme']).encode()
 revision=signature({'before':before,'after':after});history=inside(root,'.line-world/history/'+revision+'.json')
 saved={p:p.read_bytes() if p.exists() else None for p in writes}
 record={'revision':revision,'before':{str(p.relative_to(root)):data.decode('utf-8') if data is not None else None for p,data in saved.items()},'afterSha256':{str(p.relative_to(root)):hashlib.sha256(data).hexdigest() for p,data in writes.items()}}
 transaction({**writes,history:encode(record)})
 report.update(revision=revision,history=str(history.relative_to(root)),next='Rebuild the producer, then use status to select local render work.');return report
def restore(root,revision):
 if not re.fullmatch('[a-f0-9]{64}',revision):raise ValueError('Use a recorded revision ID.')
 record=read(inside(root,'.line-world/history/'+revision+'.json'))
 for rel,expected in record['afterSha256'].items():
  if not inside(root,rel).is_file() or sha(inside(root,rel))!=expected:raise ValueError('Project changed after this revision; refusing a stale restore.')
 transaction({inside(root,rel):data.encode('utf-8') if data is not None else None for rel,data in record['before'].items()})
 return {'ok':True,'restoredRevision':revision,'files':list(record['before'])}
def scene_inputs(root,c,docs):
 story=docs['story'];scenes=story.get('scenes')
 if not scenes:scenes=[{'id':k,'duration':v} for k,v in story.get('timing',{}).items()]
 if not scenes:raise ValueError('Cache planning needs story scenes or named timing beats.')
 cue_map={s['id']:s for s in docs.get('cues',{}).get('scenes',[])}
 shared={p:sha(inside(root,p)) for p in c.get('sharedInputs',[])}
 global_story={k:v for k,v in story.items() if k not in ['scenes','timing','script','projectTitle','googleVidsUrl','voice','language']}
 world=[{k:v for k,v in s.items() if k not in ['script','clip','sourceClip']} for s in scenes];result=[];start=0
 for scene in scenes:
  sid=scene['id'];sources={p:sha(inside(root,p)) for p in c.get('sceneInputs',{}).get(sid,[])};duration=scene.get('clipSeconds',scene.get('duration',scene.get('seconds',0)))
  payload={'scene':scene,'cues':cue_map.get(sid),'theme':docs.get('theme'),'global':global_story,'shared':shared,'sources':sources}
  if c.get('clock')=='global':payload['globalStart']=start
  if sid in c.get('overviewIds',[]):payload['world']=world
  result.append({'id':sid,'inputsSha256':signature(payload),'narrationSha256':signature({'script':scene.get('script'),'voice':story.get('voice'),'language':story.get('language')})});start+=duration
 return result
def receipt_current(root,scene,old,prior=None,continuous=True):
 if not old or old.get('inputsSha256')!=scene['inputsSha256']:return False
 path=inside(root,old['artifact'])
 if not path.is_file() or sha(path)!=old['artifactSha256']:return False
 return not continuous or prior is None or old.get('upstreamPoseSha256')==signature(prior.get('lastPose'))
def status(root,details=False):
 c=config(root);docs=documents(root,c);scenes=scene_inputs(root,c,docs);p=inside(root,'.line-world/render-state.json');state=read(p) if p.is_file() else {'scenes':{}};items=[];previous=None
 for s in scenes:
  old=state['scenes'].get(s['id']);reasons=[];waiting=[]
  if not old:reasons.append('no-render-receipt')
  else:
   if old['inputsSha256']!=s['inputsSha256']:reasons.append('inputs-changed')
   path=inside(root,old['artifact'])
   if not path.is_file() or sha(path)!=old['artifactSha256']:reasons.append('artifact-missing-or-changed')
   if c.get('continuous',True) and previous:
    prior=state['scenes'].get(previous['id'])
    if items[-1]['action']!='reuse':waiting.append(previous['id'])
    elif old.get('upstreamPoseSha256')!=signature(prior.get('lastPose')):reasons.append('incoming-pose-changed')
  item={**s,'action':'render' if reasons else 'check-join' if waiting else 'reuse','reasons':reasons,'waitingOn':waiting}
  if old and old.get('narrationSha256')!=s['narrationSha256']:item['narrationReview']=True
  items.append(item);previous=s
 result={'ok':True,'render':[i['id'] for i in items if i['action']=='render'],'checkJoin':[i['id'] for i in items if i['action']=='check-join'],'reuse':[i['id'] for i in items if i['action']=='reuse'],'narrationReview':[i['id'] for i in items if i.get('narrationReview')],'scope':'Local render cache; this never confirms native uploads, voice measurement or export.'}
 if details:result['scenes']=items
 return result
def record(root,receipts):
 if not isinstance(receipts,list) or not receipts:raise ValueError('Provide local render receipts as a nonempty array.')
 c=config(root);docs=documents(root,c);scenes=scene_inputs(root,c,docs);by_id={s['id']:s for s in scenes};state_path=inside(root,'.line-world/render-state.json');state=read(state_path) if state_path.is_file() else {'schemaVersion':1,'scenes':{}};seen=set()
 for receipt in receipts:
  sid=receipt.get('id')
  if sid not in by_id or sid in seen or receipt.get('inputsSha256')!=by_id[sid]['inputsSha256']:raise ValueError('Render receipt has an unknown, duplicate or stale scene fingerprint.')
  seen.add(sid);artifact=inside(root,receipt['artifact'])
  if not artifact.is_file():raise ValueError('Render artifact does not exist.')
  i=next(i for i,s in enumerate(scenes) if s['id']==sid);previous=scenes[i-1] if i else None;prior=state['scenes'].get(previous['id']) if previous else None
  if c.get('continuous',True):
   for j in range(i):
    previous_scene=scenes[j];previous_receipt=state['scenes'].get(previous_scene['id']);incoming=state['scenes'].get(scenes[j-1]['id']) if j else None
    if not receipt_current(root,previous_scene,previous_receipt,incoming):raise ValueError('Record the current predecessor endpoints first.')
   if any(not isinstance(receipt.get(k),dict) or not receipt[k] for k in ['firstPose','lastPose']):raise ValueError('Continuous scenes need actual nonempty firstPose and lastPose objects.')
   signature([receipt['firstPose'],receipt['lastPose']])
  if c.get('continuous',True) and prior and receipt['firstPose']!=prior['lastPose']:raise ValueError('The rendered join poses differ.')
  baseline=state['scenes'].get(sid,{}).get('narrationSha256',by_id[sid]['narrationSha256'])
  state['scenes'][sid]={**by_id[sid],'narrationSha256':baseline,'artifact':str(artifact.relative_to(root)),'artifactSha256':sha(artifact),'firstPose':receipt.get('firstPose'),'lastPose':receipt.get('lastPose'),'upstreamPoseSha256':signature(prior.get('lastPose')) if prior else None}
 transaction({state_path:encode(state)});return {'ok':True,'recorded':len(receipts),**status(root)}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['setup','inspect','plan','apply','restore','status','record','theme']);parser.add_argument('--project',type=Path,required=True);parser.add_argument('--story',default='story.json');parser.add_argument('--cues');parser.add_argument('--file',default='story');parser.add_argument('--path');parser.add_argument('--patch',type=Path);parser.add_argument('--revision');parser.add_argument('--receipts',type=Path);parser.add_argument('--details',action='store_true');parser.add_argument('--report',type=Path);args=parser.parse_args();root=args.project.resolve()
 try:
  if (SKILL/'SKILL.md').is_file() and root.is_relative_to(SKILL):raise ValueError('Keep the skill bundle read-only.')
  report_path=inside(root,args.report.resolve()) if args.report else None
  protected=[inside(root,v) for v in ['story.json','theme.json','theme.css',META]]
  if inside(root,META).is_file():protected.extend(inside(root,v) for v in config(root)['files'].values())
  if report_path and (report_path in protected or report_path.is_relative_to(inside(root,'.line-world'))):raise ValueError('A report cannot replace editable inputs or metadata.')
  if args.command=='setup':result=setup(root,args.story,args.cues)
  elif args.command=='inspect':result=inspect(root,args.file,args.path)
  elif args.command in ['plan','apply']:
   if not args.patch:raise ValueError('Provide --patch changes.json.')
   result=apply(root,read(input_path(root,args.patch)),args.command=='plan')
  elif args.command=='restore':result=restore(root,args.revision or '')
  elif args.command=='status':result=status(root,args.details)
  elif args.command=='record':
   if not args.receipts:raise ValueError('Provide --receipts render-receipts.json.')
   result=record(root,read(input_path(root,args.receipts)))
  else:
   c=config(root);transaction({inside(root,'theme.css'):theme_css(read(inside(root,c['files']['theme']))).encode()});result={'ok':True,'css':'theme.css'}
  if args.report:
   atomic(report_path,encode(result))
  print(json.dumps(result,ensure_ascii=False,allow_nan=False));return 0
 except (ValueError,OSError,KeyError,TypeError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
