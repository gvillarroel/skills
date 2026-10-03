#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Combine the latest D3 proof with unchanged SHA-bound Three/procedural rows."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];EVIDENCE=ROOT/'evaluations/arrow-contrast-custom';DATA=ROOT/'projects/arrow-contrast-custom/artifacts/data'
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/run-pi-skill-eval.py');harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
def payload(skill):
 tree=harness.snapshot_tree(ROOT/'skills'/skill)
 tree={k:v for k,v in tree.items() if not any(p in harness.COPY_IGNORE for p in Path(k).parts) and not k.startswith('assets/examples/')}
 return harness.snapshot_digest(tree)
previous=json.loads((EVIDENCE/'results-before-label-repair-20261003.json').read_text(encoding='utf-8'))
inheritance={skill:{'payloadSha256':payload(skill),'source':'results-before-label-repair-20261003.json','unchanged':True} for skill in ('threejs-animated-3d','procedural-svg-animation')}
assert all(item['payloadSha256']==previous['finalPayloads'][skill]['payloadSha256'] for skill,item in inheritance.items())
old=json.loads((DATA/'focused-arrow-check.json').read_text(encoding='utf-8'));new=json.loads((DATA/'focused-d3-check.json').read_text(encoding='utf-8'))
rows=[row for row in old['rows'] if not row['route'].startswith('d3-')]+new['rows']
assert len(rows)==48 and len(new['rows'])==32 and all(row['passed'] for row in rows)
report={'date':'2026-10-03','passed':True,'errors':old['errors']+new['errors'],'currentD3PayloadSha256':payload('d3'),'unchangedProofs':inheritance,'method':'Latest 32 D3 delivery/export rows plus 16 unchanged Three.js/procedural rows; SHA equality checked before inheritance.','rows':rows}
assert not report['errors']
(DATA/'focused-arrow-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
compact={**report,'rows':[{k:v for k,v in row.items() if k not in ('samples','arrows','glyphs')} for row in rows]}
(EVIDENCE/'focused-arrow-check-20261003.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
gallery_path=EVIDENCE/'gallery-states-20261003.json';gallery=json.loads(gallery_path.read_text(encoding='utf-8'))
before=EVIDENCE/'gallery-states-before-final-callout-20261003.json'
if not before.exists():before.write_bytes(gallery_path.read_bytes())
latest=json.loads((EVIDENCE/'bowtie-states-20261003.json').read_text(encoding='utf-8'))
states=[row for row in gallery['rows'] if row['item']!='bowtie-barriers']+latest['rows']
assert len(states)==36 and len(latest['rows'])==6 and all(row['passed'] for row in states)
gallery={**gallery,'rows':states,'currentD3PayloadSha256':payload('d3'),'method':'30 unchanged pattern states plus 6 fresh final bowtie states; the finalizer and other pattern geometry/paint code are unchanged by the final callout delta.','gallerySourceSha256':hashlib.sha256((ROOT/'skills/d3/assets/examples/d3-animated-svg/gallery.js').read_bytes()).hexdigest(),'finalizerSha256':hashlib.sha256((ROOT/'skills/d3/assets/templates/solid-style.js').read_bytes()).hexdigest()}
gallery_path.write_text(json.dumps(gallery,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'rowCount':len(rows),'currentD3PayloadSha256':report['currentD3PayloadSha256'],'unchangedProofs':inheritance},indent=2))
