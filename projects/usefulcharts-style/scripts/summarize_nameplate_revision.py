#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain every v25 nameplate run and independently inspect its complete output."""

import importlib.util
import hashlib
import json
import subprocess
from pathlib import Path


def command_contract(folder, root):
    load=lambda name:json.loads((folder/name).read_text(encoding='utf-8-sig'))
    original=load('workspace/draft.json');resolved=load('workspace/result/source.json')
    by_id={n['id']:n for n in resolved['nodes']}
    same=set(by_id)=={n['id'] for n in original['nodes']} and all(
        all(by_id[n['id']].get(k)==v for k,v in n.items()) for n in original['nodes'])
    same=same and all(resolved.get(k)==v for k,v in original.items() if k not in ('layout','nodes','annotations'))
    annotations=lambda data:[{k:v for k,v in a.items() if k not in ('dx','dy')} for a in data['annotations']]
    same=same and annotations(original)==annotations(resolved)
    audited=subprocess.run(['uv','run','--script',str(root/'skills/usefulcharts-style/scripts/audit_chart.py'),
        str(folder/'workspace/result/poster.svg'),'--source',str(folder/'workspace/result/source.json'),
        '--report',str(folder/'independent-browser.json')],cwd=root,capture_output=True)
    return dict(status='pass' if same and audited.returncode==0 else 'fail',all_facts_preserved=same,
        placement=load('workspace/result/placement.json')['status'],independent_browser=load('independent-browser.json')['status'])


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('emphasis_contract',root/'evaluations/contracts/verify-usefulcharts-nameplate-composition.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    runs=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v25-*-20260912-*')):
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            runs.append(dict(id=folder.name,status='running',payload=manifest['skill']));continue
        result=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json');errors=[];images=[];invalid_lines=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            try:event=json.loads(line)
            except json.JSONDecodeError:
                invalid_lines.append(line[:200]);continue
            if event.get('type')!='tool_execution_end':continue
            blocks=event.get('result',{}).get('content',[])
            if event.get('isError'):errors.extend(c['text'] for c in blocks if c.get('type')=='text')
            images.extend(dict(mime=c.get('mimeType'),encoded_bytes=len(c.get('data',''))) for c in blocks if c.get('type')=='image')
        family='-family-' in folder.name
        if family:artifact=contract.inspect(folder,root)
        elif (folder/'workspace/result/source.json').exists():artifact=command_contract(folder,root)
        else:artifact=dict(status='fail',missing=['result/source.json'])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        review=load('visual-review.json') if (folder/'visual-review.json').exists() else 'Awaiting direct image review.' if family else 'Command control only.'
        runs.append(dict(id=folder.name,case='naturalistic-forward' if family else 'contract-smoke',model=model,
            payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],expected_outputs=manifest['expectedOutputs'],
            strict=load('evaluation-result.json'),independent_artifact=artifact,read_surface_passed=result.returncode==0,
            read_paths=[p['path'] for p in surface['readPaths']],tool_errors=errors,invalid_event_lines=invalid_lines,
            supported_image_results=images,visual_review=review))
    prototypes=[]
    for path in sorted((root/'projects/usefulcharts-style/artifacts/reviews/nameplate-composition-v25').glob('*/prototype.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        prototypes.append(dict(id=path.parent.name,changed_people=len(data.get('changed_nodes',[])),
            **{key:data.get(key) for key in ('status','before','include_portraits','reflow','compact_captions',
                'landmark_preferences','error','all_source_facts_preserved')}))
    facts=json.loads((root/'projects/usefulcharts-style/artifacts/reviews/nameplates-final-facts.json').read_text(encoding='utf-8'))
    murals=[]
    for name in ('aurelian-families','atlas-of-inquiry','five-regional-histories'):
        path=root/f'skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}.svg'
        previous=subprocess.check_output(['git','show',f'5720173d:skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}.svg'],cwd=root)
        current=path.read_bytes()
        normalize=lambda value:value.replace(b'\r\n',b'\n')
        audit=json.loads((root/f'projects/usefulcharts-style/artifacts/reviews/nameplates-final-{name}-browser.json').read_text(encoding='utf-8'))
        mutations=json.loads((root/f'projects/usefulcharts-style/artifacts/reviews/nameplates-final-mutations/{name}/mutation-audit.json').read_text(encoding='utf-8'))
        murals.append(dict(id=name,svg_sha256=hashlib.sha256(current).hexdigest(),
            unchanged_from_before=normalize(previous)==normalize(current),canvas=audit['canvas'],
            browser_status=audit['status'],browser_findings=audit['findings'],
            mutations_detected=sum(m['detected'] for m in mutations['mutations'])))
    court=json.loads((root/'projects/usefulcharts-style/artifacts/reviews/nameplate-composition-v25/solid-principals-local-court/composition.json').read_text(encoding='utf-8'))
    trial_root=root/'projects/usefulcharts-style/artifacts/reviews/nameplate-composition-v25'
    ineffective_move=dict(id='solid-principals-realm-gap',geometry_status='pass',visual_intent_achieved=False,
        requested_offset=[-180,-60],actual_offset=[-212,108],
        png_unchanged=(trial_root/'solid-principals-reflow/poster.png').read_bytes()==(trial_root/'solid-principals-realm-gap/poster.png').read_bytes(),
        finding='The pocket search returned the previous realm location. A changed JSON preference was not a visible caption separation. The final local court treatment is independently checked below.')
    canonical=root/'projects/usefulcharts-style/artifacts/images/nameplates-final-aurelian-families.png'
    reviewed=root/'projects/usefulcharts-style/artifacts/reviews/nameplate-composition-v25/solid-principals-local-court/poster.png'
    visual_reviews=[r['visual_review'] for r in runs if r.get('case')=='naturalistic-forward']
    report=dict(status='validating',runs=runs,local_development_attempts=prototypes,final_facts=facts,final_murals=murals,
        naturalistic_visual_acceptance=dict(passed=sum(isinstance(r,dict) and r.get('status')=='pass' for r in visual_reviews),
            total=len(visual_reviews),scope='Compact development output only. Strict execution and visual acceptance are separate gates.'),
        ineffective_context_move=ineffective_move,
        court_composition={k:v for k,v in court.items() if k!='layout'},
        canonical_png_matches_reviewed=canonical.read_bytes()==reviewed.read_bytes(),
        prototype_retention='These exploratory attempts used an evolving project driver with the unchanged v24 router. Preserve their outcomes, not a claim of frozen per-attempt reproducibility. Composition-stage files omit required captions and never count as final passes.',
        evaluation_scope='Development reuse of the full Silver Vale family, with compact name/date groups, three focal people and a light palette. Not a sealed holdout or a substitute for the dense three-family target.',
        visual_parity='Not established. Preserve dense genealogy, institutional lineage and chronology requirements and previous unresolved findings.')
    output=root/'evaluations/usefulcharts-style/nameplate-composition-summary-20260912.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(runs),strict_passes=sum(r.get('strict',{}).get('passed',False) for r in runs),
        independent_passes=sum(r.get('independent_artifact',{}).get('status')=='pass' for r in runs),
        running=sum(r.get('status')=='running' for r in runs))))


if __name__=='__main__':main()
