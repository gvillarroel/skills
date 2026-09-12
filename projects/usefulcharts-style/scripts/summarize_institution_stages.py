#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain v26 composition attempts, source preservation and all isolated outcomes."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'projects/usefulcharts-style/artifacts'
BASELINE='2b9f6595dd51f0f7324b84523545fafb294b3c65'


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))


def facts():
    name='skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json'
    before=json.loads(subprocess.check_output(['git','show',f'{BASELINE}:{name}'],cwd=ROOT))
    after=load(ROOT/name)
    nodes=lambda data:[{k:v for k,v in n.items() if k not in ('x','y')} for n in data['nodes']]
    edges=lambda data:[{k:v for k,v in e.items() if k not in ('via','corridor_y','source_port','target_port')} for e in data['edges']]
    insets=lambda data:[{k:v for k,v in inset.items() if k!='box'} for inset in data['insets']]
    excluded={'nodes','edges','insets','width','height'}
    checks=dict(all_node_facts_and_typography=nodes(before)==nodes(after),all_typed_relationships=edges(before)==edges(after),
        inset_data=insets(before)==insets(after),other_source_fields={k:v for k,v in before.items() if k not in excluded}==
        {k:v for k,v in after.items() if k not in excluded})
    canonical=ART/'images/stages-final-atlas-of-inquiry.png'
    reviewed=ART/'reviews/institution-stages-v26/compact-canonical/poster.png'
    checks['canonical_png_equals_reviewed']=canonical.read_bytes()==reviewed.read_bytes()
    return dict(status='pass' if all(checks.values()) else 'fail',checks=checks,
        node_count=len(after['nodes']),edge_count=len(after['edges']),influence_count=sum(e['kind']=='influence' for e in after['edges']),
        lateral_influences=sum(e.get('source_port','bottom')!='bottom' or e.get('target_port','top')!='top' for e in after['edges']),
        before_canvas=[before['width'],before['height']],after_canvas=[after['width'],after['height']],
        source_sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),png_sha256=hashlib.sha256(canonical.read_bytes()).hexdigest())


def inspect_runs():
    spec=importlib.util.spec_from_file_location('institution_contract',ROOT/'evaluations/contracts/verify-usefulcharts-institutions.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    reviews=load(ROOT/'evaluations/usefulcharts-style/institution-stages-visual-reviews-20260912.json')['runs']
    results=[]
    for folder in sorted((ROOT/'evaluations/runs').glob('usefulcharts-v26*-20260912-*')):
        manifest=load(folder/'run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            results.append(dict(id=folder.name,status='running',payload=manifest['skill']));continue
        process=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=ROOT,capture_output=True)
        surface=load(folder/'read-surface.json');naturalistic='-institutions-' in folder.name
        commands=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_start' and 'command' in event.get('args',{}):commands.append(event['args']['command'])
        paths=folder/'workspace/result'
        if (paths/'source.json').exists():
            audit=subprocess.run(['uv','run','--script','skills/usefulcharts-style/scripts/audit_chart.py',str(paths/'poster.svg'),
                '--source',str(paths/'source.json'),'--report',str(folder/'independent-browser.json')],cwd=ROOT,capture_output=True)
            if naturalistic:artifact=contract.inspect(folder)
            else:
                before=load(folder/'workspace/draft.json');after=load(paths/'source.json')
                strip=lambda data:[{k:v for k,v in e.items() if k not in ('via','source_port','target_port')} for e in data['edges']]
                same=strip(before)==strip(after) and {k:v for k,v in before.items() if k!='edges'}=={k:v for k,v in after.items() if k!='edges'}
                artifact=dict(status='pass' if same and audit.returncode==0 else 'fail',all_facts_and_coordinates_preserved=same,
                    routing=load(paths/'routing.json'),scope='Command contract only; no aesthetic acceptance.')
            artifact['independent_browser_pass']=audit.returncode==0
            if audit.returncode:artifact['status']='fail'
        else:artifact=dict(status='fail',missing=['result/source.json'])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        results.append(dict(id=folder.name,case='naturalistic-forward' if naturalistic else 'contract-smoke',model=model,
            payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],strict=load(folder/'evaluation-result.json'),
            independent_artifact=artifact,read_surface_pass=process.returncode==0,read_paths=[p['path'] for p in surface['readPaths']],
            used_influence_helper=any('route_influences.py' in command for command in commands),
            explicit_side_attachments=sum(edge.get('source_port','bottom')!='bottom' or edge.get('target_port','top')!='top'
                for edge in load(paths/'source.json').get('edges',[])) if (paths/'source.json').exists() else 0,
            visual_review=reviews.get(folder.name,'Command contract only.')))
    return results


def main():
    attempts=[]
    for path in sorted((ART/'reviews/institution-stages-v26').glob('*/prototype.json')):
        value=load(path);attempts.append(dict(id=path.parent.name,report=value,
            browser=({k:v for k,v in load(path.parent/'browser.json').items() if k in ('status','findings','node_count','edge_count')})
            if (path.parent/'browser.json').exists() else None))
    murals=[]
    for name in ('aurelian-families','atlas-of-inquiry','five-regional-histories'):
        svg=f'skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}.svg'
        old=subprocess.check_output(['git','show',f'{BASELINE}:{svg}'],cwd=ROOT);current=(ROOT/svg).read_bytes()
        audit=load(ART/f'reviews/stages-final-{name}-browser.json');mutations=load(ART/f'reviews/stages-final-mutations/{name}/mutation-audit.json')
        murals.append(dict(id=name,svg_sha256=hashlib.sha256(current).hexdigest(),
            unchanged_from_baseline=old.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n'),
            browser_status=audit['status'],findings=audit['findings'],canvas=audit['canvas'],crossings=len(audit['metadata']['crossings']),
            mutations_detected=sum(m['detected'] for m in mutations['mutations'])))
    report=dict(status='validating',baseline=BASELINE,all_development_attempts=attempts,runs=inspect_runs(),
        final_facts=facts(),final_murals=murals,route_metrics=load(ART/'reviews/stages-final-route-metrics.json'),
        limits=['Unblinded author critique, not a human discrimination study.',
            'Placement proxy objectives and shorter routes do not prove better composition.',
            'All failed and budget-limited attempts are retained; early drivers evolved without per-run snapshots.',
            'The compact institutions case is reused development data, not sealed holdout evidence.',
            'Genealogy, institutional histories and chronology remain in the quality-and-composition objective.'])
    output=ROOT/'evaluations/usefulcharts-style/institution-stages-summary-20260912.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(attempts=len(attempts),runs=len(report['runs']),running=sum(r.get('status')=='running' for r in report['runs']),
        strict_passes=sum(r.get('strict',{}).get('passed',False) for r in report['runs']),facts=report['final_facts']['status'])))


if __name__=='__main__':main()
