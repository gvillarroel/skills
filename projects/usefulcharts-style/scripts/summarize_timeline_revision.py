#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain all dated-note forward attempts, exact contracts and actual failures."""

import copy
import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('contract',root/'evaluations/contracts/verify-usefulcharts-regions.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v*-20260912-*')):
        if not folder.name.startswith(('usefulcharts-v16-','usefulcharts-v17-')):continue
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            results.append(dict(id=folder.name,status='running',payload=manifest['skill']));continue
        strict=load('evaluation-result.json')
        check=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True,check=False)
        surface=load('read-surface.json')
        if '-regions-' in folder.name:
            artifact=module.inspect(folder)
        else:
            source=load('workspace/draft.json');brief=load('workspace/deliverables/brief.json');normalized=copy.deepcopy(brief)
            for event in normalized['events']:event.pop('offset',None);event.pop('width',None)
            artifact=dict(status='pass' if source==normalized else 'fail',exact_source_preserved=source==normalized,
                placement_report=load('workspace/deliverables/placements.json')['status'],renderer_report=load('workspace/deliverables/layout.json')['status'])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        errors=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.extend(c['text'] for c in event.get('result',{}).get('content',[]) if c.get('type')=='text')
        if folder.name.startswith('usefulcharts-v16-regions'):
            visual='Rejected: excessive page size and tiny narrative text.'
        elif folder.name.startswith('usefulcharts-v17-regions'):
            visual=('Improved small-history legibility: 1300 by 1700, readable notes and an integrated clock illustration. '
                'Not accepted as parity: the three persistent lanes and evenly recurring notes remain schematic; '
                'one illustration does not demonstrate dense editorial variety.')
        else:
            visual='Command control only; no aesthetic acceptance claim.'
        results.append(dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],
            expected_outputs=manifest['expectedOutputs'],strict=strict,independent_artifact=artifact,
            read_surface_passed=check.returncode==0,read_paths=[p['path'] for p in surface['readPaths']],read_bytes=surface['totalReadResultBytes'],
            tool_errors=errors,visual_review=visual))
    report=dict(status='validating',runs=results,visual_parity='Not established. Technical checks and all failed attempts are retained separately from the visual critique.')
    output=root/'evaluations/usefulcharts-style/narrative-chronology-summary-20260912.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(results),strict_passes=sum(r.get('strict',{}).get('passed',False) for r in results),running=sum(r.get('status')=='running' for r in results))))


if __name__=='__main__':main()
