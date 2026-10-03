#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record immutable vendor bytes, scene geometry and final fixture linkage."""
import hashlib,json,re,subprocess,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];EVIDENCE=ROOT/'evaluations/arrow-contrast-custom'
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/run-pi-skill-eval.py');HARNESS=importlib.util.module_from_spec(spec);spec.loader.exec_module(HARNESS)
tree=HARNESS.snapshot_tree(ROOT/'skills/d3');tree={k:v for k,v in tree.items() if not any(p in HARNESS.COPY_IGNORE for p in Path(k).parts) and not k.startswith('assets/examples/')}
def sha(data):return hashlib.sha256(data).hexdigest()
def head(path):return subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
vendors=[]
for skill in ('d3','threejs-animated-3d'):
 for path in (ROOT/'skills'/skill/'assets/vendor').rglob('*'):
  if not path.is_file():continue
  relative=path.relative_to(ROOT).as_posix();current=path.read_bytes();before=head(relative)
  vendors.append({'path':relative,'sha256':sha(current),'matchesBaseline':current==before})
scene_path='skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js'
def geometry(source):
 start=source.index('function setupVectorField');end=source.index('\nfunction ',start+10)
 body=source[start:end]
 return {'constructors':re.findall(r'new THREE\.(?:Cone|Cylinder|Plane|Box)Geometry\([^\n;]+',body),'positions':re.findall(r'\.position\.(?:set|[xyz]\s*=)[^\n;]+',body),'phases':re.findall(r'(?:const angle|const lift|rotation\.[xyz]|scale\.y)[^\n;]+',body)}
before_geometry=geometry(head(scene_path).decode('utf-8'));after_geometry=geometry((ROOT/scene_path).read_text(encoding='utf-8'))
runtime=ROOT/'skills/d3/assets/templates/solid-style.js';fixture=ROOT/'skills/d3/assets/examples/d3-animated-svg/solid-style.js'
result={'date':'2026-10-03','d3RuntimePayload':{'fileCount':len(tree),'payloadSha256':HARNESS.snapshot_digest(tree)},'baselineCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'vendors':vendors,'allVendorBytesPreserved':all(v['matchesBaseline'] for v in vendors),'publishedThreeGeometry':{'before':before_geometry,'after':after_geometry,'preserved':before_geometry==after_geometry},'d3FinalizerFixture':{'sha256':sha(runtime.read_bytes()),'matchesRuntime':runtime.read_bytes()==fixture.read_bytes()},'paletteChanges':subprocess.check_output(['git','diff','--name-only','--','skills/d3/assets/palettes/colorsets.json','skills/threejs-animated-3d/assets/palettes/colorsets.json','skills/procedural-svg-animation/assets/palettes/colorsets.json','skills/svg-brief-design/assets/palettes/colorsets.json','skills/vectorize-art-patterns/assets/palettes/colorsets.json'],cwd=ROOT,text=True).splitlines()}
(EVIDENCE/'integrity-20261003.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert result['allVendorBytesPreserved'] and result['publishedThreeGeometry']['preserved'] and result['d3FinalizerFixture']['matchesRuntime'] and not result['paletteChanges'],result
print(json.dumps({k:v for k,v in result.items() if k not in ('vendors','publishedThreeGeometry')},indent=2))
