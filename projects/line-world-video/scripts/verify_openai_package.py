#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Verify actual archive inclusion, native OpenAI/Codex installation and skill discovery."""
import hashlib,json,os,queue,re,shutil,subprocess,tempfile,threading,zipfile
from pathlib import Path,PurePosixPath
from jsonschema import Draft202012Validator

PROJECT=Path(__file__).resolve().parent.parent
REPO=PROJECT.parent.parent
SKIP={'node_modules','__pycache__','.venv','.cache','dist','output'}
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_files(root):
 return {p.relative_to(root).as_posix():digest(p) for p in root.rglob('*') if p.is_file() and not any(x in SKIP for x in p.relative_to(root).parts) and p.relative_to(root).parts[:2]!=('assets','examples') and p.suffix not in ['.pyc','.pyo']}
def check_content(plugin,spec,schema):
 portable=read(plugin/'plugin.json');Draft202012Validator(schema).validate(portable)
 codex=read(plugin/'.codex-plugin/plugin.json')
 if any(portable[k]!=spec[k] or codex[k]!=spec[k] for k in ['name','version']):raise ValueError('Package identity differs from the release specification.')
 if codex.get('skills')!='./skills/':raise ValueError('Codex skill root must resolve to the packaged skills directory.')
 names=sorted(p.parent.name for p in (plugin/'skills').glob('*/SKILL.md'))
 if names!=sorted(spec['skills']):raise ValueError('Packaged skill set differs from the six-skill release.')
 for name in names:
  source=(plugin/'skills'/name/'SKILL.md').read_text(encoding='utf-8')
  if not re.search(r'^name:\s*'+re.escape(name)+r'\s*$',source,re.M):raise ValueError('Skill frontmatter does not match '+name)
 parity=[]
 for name in ['line-world-video','line-world-google-vids']:
  a=runtime_files(REPO/'skills'/name);b=runtime_files(plugin/'skills'/name)
  if a!=b:raise ValueError('Bundled skill is stale or incomplete: '+name)
  parity.append({'skill':name,'files':len(a),'canonicalHashesMatch':True})
 required=['skills/line-world-video/scripts/paper_video.py','skills/line-world-video/references/paper-tours.md','skills/line-world-video/assets/paper-video/paper.js','skills/line-world-video/assets/paper-video/index.html','skills/line-world-video/scripts/inspect_focus.py','skills/line-world-video/scripts/video_edit.py','skills/line-world-video/scripts/content_scan.py','skills/line-world-video/scripts/review_video.py','skills/line-world-google-vids/scripts/narration_cues.py','skills/line-world-google-vids/scripts/vids_batch.py','skills/line-world-google-vids/scripts/vids_inventory.py','skills/line-world-google-vids/scripts/vids_delivery.py','skills/line-world-google-vids/references/delivery.md','skills/line-world-google-vids/assets/runtime/vids-ui.js']
 required.append('skills/line-world-video/assets/paper-video/paper-motion.js')
 required.extend(['skills/line-world-video/scripts/people_context.py','skills/line-world-video/scripts/test_people_context.py'])
 required.extend(['skills/line-world-video/scripts/narration_review.py','skills/line-world-video/scripts/test_narration_review.py','skills/line-world-video/references/narration.md'])
 required.extend(['skills/line-world-video/scripts/documentary_assets.py','skills/line-world-video/scripts/test_documentary_assets.py','skills/line-world-video/references/documentary-images.md','skills/line-world-video/assets/vendor/photo-onebit/stylize_svg.py','skills/line-world-video/assets/vendor/photo-onebit/colorset_contract.py','skills/line-world-video/assets/vendor/photo-onebit/provenance.json'])
 required.extend(['skills/line-world-video/scripts/project_delivery.py','skills/line-world-video/scripts/test_project_delivery.py','skills/line-world-video/references/project-delivery.md'])
 required.extend(['skills/line-world-video/assets/runtime/focus-motion.js','skills/line-world-video/scripts/inspect_focus_motion.py','skills/line-world-video/scripts/test_focus_motion.py','skills/line-world-video/references/focus-motion.md'])
 required.extend(['skills/line-world-video/scripts/website_video.py','skills/line-world-video/scripts/test_website_video.py','skills/line-world-video/references/website-tours.md','skills/line-world-video/assets/runtime/website-tour.js'])
 required.extend(['skills/line-world-video/scripts/photo_focus.py','skills/line-world-video/scripts/test_photo_focus.py','skills/line-world-video/references/photo-focus.md'])
 required.extend(['skills/line-world-video/assets/runtime/gentle-motion.js','skills/line-world-video/scripts/test_gentle_motion.py','skills/line-world-video/scripts/inspect_gentle_motion.py','skills/line-world-video/references/gentle-motion.md'])
 required.extend(['skills/line-world-video/scripts/inspect_items.py','skills/line-world-video/scripts/test_item_contrast.py','skills/line-world-video/references/icons-and-alignment.md'])
 for name in ['line-world-video','line-world-d3','line-world-mermaid','line-world-icons','line-world-hyperframes']:
  rel='skills/'+name+'/assets/palettes/video-color-direction.json';required.append(rel)
  if digest(plugin/rel)!=digest(REPO/'skills/line-world-video/assets/palettes/video-color-direction.json'):raise ValueError('A producer has outdated composition color guidance.')
  required.append('skills/'+name+'/assets/runtime/focus.js')
  if digest(plugin/required[-1])!=digest(REPO/'skills/line-world-video/assets/runtime/focus.js'):raise ValueError('A video producer has an outdated focus runtime.')
  for resource in ['theme.css','theme.js','focus-motion.js','photo-focus.js','gentle-motion.js']:
   rel='skills/'+name+'/assets/runtime/'+resource;required.append(rel)
   if digest(plugin/rel)!=digest(REPO/'skills/line-world-video/assets/runtime'/resource):raise ValueError('A producer theme differs from the canonical runtime.')
 for rel in ['scripts/color_balance.py','scripts/test_color_balance.py','assets/palettes/video-balance.json']:
  if (plugin/'skills/line-world-video'/rel).exists():raise ValueError('The retired pixel-quota implementation must not ship.')
 for name in required:
  if not (plugin/name).is_file():raise ValueError('Required utility is missing: '+name)
 return {'skills':names,'canonicalParity':parity,'requiredUtilities':required,'portableSchemaValid':True,'codexManifestValid':True}
def rpc_discovery(binary,home,cwd,installed,logs):
 env={**os.environ,'CODEX_HOME':str(home)}
 with (logs/'app-server.stderr.txt').open('w',encoding='utf-8') as stderr:
  proc=subprocess.Popen([binary,'app-server'],cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,encoding='utf-8');messages=queue.Queue();events=[]
  def reader():
   for line in proc.stdout:messages.put(line)
  threading.Thread(target=reader,daemon=True).start()
  def send(value):proc.stdin.write(json.dumps(value)+'\n');proc.stdin.flush()
  def request(number,method,params):
   send({'id':number,'method':method,'params':params})
   while True:
    value=json.loads(messages.get(timeout=40));events.append(value)
    if value.get('id')==number:
     if 'error' in value:raise ValueError('Native '+method+' failed: '+str(value['error']))
     return value['result']
  try:
   request(1,'initialize',{'clientInfo':{'name':'line_world_package_check','version':read(installed/'plugin.json')['version']},'capabilities':{'experimentalApi':True}});send({'method':'initialized'})
   result=request(2,'skills/list',{'cwds':[str(cwd)],'forceReload':True});found=[]
   for group in result.get('data',[]):
    for skill in group.get('skills',[]):
     path=Path(skill.get('path','')).resolve()
     if path.is_relative_to(installed):found.append({'name':skill['name'],'path':str(path),'enabled':skill.get('enabled',True)})
   return {'pluginSkills':found,'modelTurns':0,'raw':result}
  finally:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
   (logs/'app-server-events.json').write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
def main():
 spec=read(PROJECT/'package-spec.json');version=spec['version'];base=PROJECT/'artifacts/host-checks'/('openai-'+version);base.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='clean-',dir=base));report={'ok':False,'version':version,'workdir':str(work),'checks':{}}
 try:
  archive=PROJECT/'artifacts/packages'/f'line-world-video-{version}-marketplace.zip';report['archive']=str(archive);report['archiveSha256']=digest(archive);extracted=work/'marketplace';extracted.mkdir()
  with zipfile.ZipFile(archive) as z:
   for name in z.namelist():
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:raise ValueError('Archive member is not a contained relative path.')
   z.extractall(extracted)
  plugin=extracted/'plugin';schema=read(PROJECT/'artifacts/host-checks'/('release-'+version)/'plugin.schema.json');report['checks']['contents']=check_content(plugin,spec,schema)
  portable_archive=PROJECT/'artifacts/packages'/f'line-world-video-{version}.zip'
  with zipfile.ZipFile(portable_archive) as z:
   for p in plugin.rglob('*'):
    if p.is_file() and hashlib.sha256(z.read(p.relative_to(plugin).as_posix())).hexdigest()!=digest(p):raise ValueError('Portable plugin and marketplace archives differ.')
  report['checks']['bothArchivesContainSamePlugin']=True
  # A removed required runtime must be rejected; preserve and restore exact bytes.
  target=plugin/'skills/line-world-video/assets/runtime/focus.js';saved=target.read_bytes();target.unlink()
  try:
   try:check_content(plugin,spec,schema)
   except (ValueError,OSError):report['checks']['missingRequiredRuntimeRejected']=True
   else:raise ValueError('Incomplete package was incorrectly accepted.')
  finally:target.write_bytes(saved)
  home=work/'codex-home';home.mkdir();temporary=work/'tmp';temporary.mkdir();env={**os.environ,'CODEX_HOME':str(home),'TMP':str(temporary),'TEMP':str(temporary),'UV_CACHE_DIR':str(work/'uv-cache')};binary=shutil.which('codex.cmd') or shutil.which('codex');results=[]
  commands=[['--version'],['plugin','marketplace','add',str(extracted),'--json'],['plugin','list','--available','--marketplace','line-world-local','--json'],['plugin','add','line-world-video@line-world-local','--json'],['plugin','list','--marketplace','line-world-local','--json']]
  for n,args in enumerate(commands):
   result=subprocess.run([binary,*args],cwd=extracted,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60);(work/f'command-{n}.stdout.txt').write_text(result.stdout,encoding='utf-8');(work/f'command-{n}.stderr.txt').write_text(result.stderr,encoding='utf-8');results.append({'args':args,'exitCode':result.returncode})
   if result.returncode:raise ValueError('Native Codex command failed: '+str(args))
   if n==3:installed=Path(json.loads(result.stdout)['installedPath']).resolve()
   if n==4:
    entry=next(v for v in json.loads(result.stdout)['installed'] if v['name']=='line-world-video')
    if not entry.get('enabled') or entry['version']!=version:raise ValueError('Installed plugin is not enabled at the expected version.')
  report['checks']['nativeCommands']=results
  for path in plugin.rglob('*'):
   if path.is_file() and digest(path)!=digest(installed/path.relative_to(plugin)):raise ValueError('Installed plugin differs from the shipped archive.')
  report['checks']['installedBytesMatchArchive']=True
  cwd=work/'project';cwd.mkdir();subprocess.run(['git','init','--quiet',str(cwd)],check=True,capture_output=True)
  discovery=rpc_discovery(binary,home,cwd,installed,work);report['checks']['nativeSkillDiscovery']=discovery
  # Native names are plugin-qualified; the actual installed path identifies each bundled skill.
  if sorted(Path(v['path']).parent.name for v in discovery['pluginSkills'])!=sorted(spec['skills']):raise ValueError('Native app-server did not discover every installed plugin skill.')
  tests=[]
  for name,script in [('line-world-video','test_focus.py'),('line-world-video','test_focus_motion.py'),('line-world-video','test_photo_focus.py'),('line-world-video','test_gentle_motion.py'),('line-world-video','test_scene_effects.py'),('line-world-video','test_website_video.py'),('line-world-video','test_theme.py'),('line-world-video','test_item_contrast.py'),('line-world-video','test_video_edit.py'),('line-world-video','test_review_video.py'),('line-world-video','test_content_scan.py'),('line-world-video','test_media_assets.py'),('line-world-video','test_documentary_assets.py'),('line-world-video','test_project_delivery.py'),('line-world-video','test_people_context.py'),('line-world-video','test_narration_review.py'),('line-world-video','test_paper_video.py'),('line-world-video','test_paper_motion.py'),('line-world-google-vids','test_narration_cues.py'),('line-world-google-vids','test_vids_plan.py'),('line-world-google-vids','test_vids_inventory.py'),('line-world-google-vids','test_vids_batch.py'),('line-world-google-vids','test_vids_ui.py'),('line-world-google-vids','test_vids_delivery.py')]:
   result=subprocess.run(['uv','run','--script',str(installed/'skills'/name/'scripts'/script)],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60);(work/(script+'.stdout.txt')).write_text(result.stdout,encoding='utf-8');(work/(script+'.stderr.txt')).write_text(result.stderr,encoding='utf-8');tests.append({'skill':name,'script':script,'exitCode':result.returncode})
   if result.returncode:raise ValueError('Installed utility test failed: '+script)
  report['checks']['installedRuntimeTests']=tests;report['ok']=True
 except Exception as e:report['error']=str(e)
 report['scope']='Actual ZIP extraction, task-local Codex install, native skills/list and installed utility tests. No global install, account publication or desktop activation is claimed.'
 (work/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(base/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'report':str(base/'verification.json'),'error':report.get('error'),'registeredSkills':[v['name'] for v in report['checks'].get('nativeSkillDiscovery',{}).get('pluginSkills',[])]}));return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
