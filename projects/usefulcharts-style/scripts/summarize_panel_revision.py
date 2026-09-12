#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain every panel/packing attempt, model gate, source contract and failure."""

import importlib.util
import json
import re
import subprocess
from pathlib import Path


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    root=Path(__file__).resolve().parents[3];runs=[]
    libraries=load_module('library_contract',root/'evaluations/contracts/verify-usefulcharts-libraries.py')
    controls=load_module('prior_controls',Path(__file__).with_name('summarize_cross_family_revision.py'))
    folders=sorted(folder for folder in (root/'evaluations/runs').glob('usefulcharts-v*-20260912-*') if re.match(r'usefulcharts-v(?:14|15)-',folder.name))
    for folder in folders:
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=read('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            runs.append(dict(id=folder.name,status='in-progress',payload=manifest['skill']));continue
        result=read('evaluation-result.json')
        summary=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True,check=False)
        surface=read('read-surface.json');artifact=dict(status='not-evaluated')
        classification=None
        if folder.name=='usefulcharts-v14-libraries-20260912-1':
            classification='evaluation-setup: invalid supplied ID/table formatting; cancelled with original evidence retained'
        elif 'libraries' in folder.name and (folder/'workspace/result/poster.png').exists():artifact=libraries.inspect(folder)
        elif 'boundary' in folder.name:artifact=controls.boundary_contract(folder)
        elif 'separated' in folder.name:
            source=json.loads((folder/'workspace/deliverables/source.json').read_text(encoding='utf-8'))
            expected=json.loads(re.search(r'```json\n(.*?)\n```',(folder/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
            artifact=dict(status='pass' if source==expected else 'fail',exact_input_preserved=source==expected)
        if folder.name=='usefulcharts-v14-separated-20260912-spark-1':classification='harness: mixed JSON/shell fence parsing rejected the correctly executed command'
        elif folder.name=='usefulcharts-v14-libraries-20260912-2':classification='skill and agent: oversized authored page, uniform panels, temporary-path and layout/audit errors'
        elif 'boundary' in folder.name and not result['passed']:classification='agent: unnecessary directory/existence probes returned errors before creating the requested review files; source and diagnostic semantics are checked separately'
        errors=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.extend(c['text'] for c in event.get('result',{}).get('content',[]) if c.get('type')=='text')
        runs.append(dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],
            expected_outputs=manifest['expectedOutputs'],strict=result,independent_artifact=artifact,failure_classification=classification,
            read_surface_passed=summary.returncode==0,read_paths=[p['path'] for p in surface['readPaths']],read_bytes=surface['totalReadResultBytes'],tool_errors=errors))
    output=root/'evaluations/usefulcharts-style/panel-and-packed-revision-summary-20260912.json'
    report=dict(status='validating',runs=runs,visual_parity='Not established. Read the separate visual review; exact data and clean geometry do not prove resemblance.')
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(summary=str(output),runs=len(runs),strict_passes=sum(r.get('strict',{}).get('passed',False) for r in runs),in_progress=sum(r.get('status')=='in-progress' for r in runs))))


if __name__=='__main__':main()
