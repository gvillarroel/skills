#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit public model identity, proof usage, failures and original-only payloads."""
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from seal_technique_evolution import REPO, read, sha
from inspect_technique_evolution import collect


def inspect(root):
    result = {}
    for arm in ['b','c']:
        directory = root / 'jobs' / arm
        rows = collect(directory)
        transcripts = []
        for path in directory.glob('*/agent/pi.txt'):
            events = []
            for line in path.read_text(encoding='utf-8').splitlines():
                try: events.append(json.loads(line))
                except ValueError: pass
            assistants = [e['message'] for e in events if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant']
            commands = [e for e in events if e.get('type')=='tool_execution_start']
            text = json.dumps(commands)
            proof_commands = [e for e in commands if e.get('toolName')=='bash' and 'scripts/proof_svg.py' in json.dumps(e.get('args',{}))]
            failures = [e for e in events if e.get('type')=='tool_execution_end' and e.get('isError')]
            transcripts.append({'trial':path.parent.parent.name,'models':sorted({e.get('model') for e in assistants}),
                'assistant_messages':len(assistants),'guide_read':'references/information-editing.md' in text,
                'proof_calls':len(proof_commands),
                'proof_image_reads':sum(e.get('toolName')=='read' and 'proof' in json.dumps(e.get('args',{})).lower() and '.png' in json.dumps(e.get('args',{})) for e in commands),
                'failures':[e.get('result',{}).get('content',[]) for e in failures],
                'transcript_sha256':sha(path)})
        result[arm]={'completed_trials':len(rows),'finished':(directory / 'result.json').exists() and bool(read(directory/'result.json').get('finished_at')),
            'agent_errors':sum(bool(r['exception']) for r in rows),
            'assistant_models':sorted({m for t in transcripts for m in t['models']}),
            'guide_read_trials':sum(t['guide_read'] for t in transcripts),
            'proof_used_trials':sum(t['proof_calls']>0 for t in transcripts),
            'proof_read_trials':sum(t['proof_image_reads']>0 for t in transcripts),
            'transcripts':transcripts}
    registry=read(root / 'evaluator/anchor-registry.json')
    paths=[]
    for task in (root / 'development').iterdir():
        if not task.is_dir(): continue
        source=root/'evaluator'/registry[task.name]['file']
        assert sha(source)==registry[task.name]['sha256']
        for element in ET.fromstring(source.read_bytes()).iter():
            path=re.sub(r'\s+',' ',element.get('d','')).strip()
            if len(path)>=80: paths.append(path)
    text=' '.join(p.read_text(encoding='utf-8') for p in (root/'inputs/c/svg-brief-design').rglob('*') if p.is_file())
    normalized=re.sub(r'\s+',' ',text)
    assert all(path not in normalized for path in paths)
    result['source_audit']={'passed':True,'public_sources':6,'long_paths_compared':len(set(paths)),
        'scope':'Exact long-path text only; no proof against arbitrary transformed copying. No private source inspected.'}
    return result


def main():
    root=REPO/'evaluations/runs/svt4'
    result=inspect(root)
    if len(sys.argv)>1 and sys.argv[1]=='seal':
        assert all(result[a]['finished'] and result[a]['completed_trials']==12 for a in ['b','c'])
        assert all(result[a]['assistant_models']==['gpt-6-luna'] for a in ['b','c'])
        with (root/'model-and-behavior-audit.json').open('x',encoding='utf-8') as handle:
            json.dump(result,handle,indent=2)
    compact={a:{k:v for k,v in result[a].items() if k!='transcripts'} for a in ['b','c']}
    compact['failures']=[{'arm':a,'trial':t['trial'],'failures':t['failures']} for a in ['b','c'] for t in result[a]['transcripts'] if t['failures']]
    compact['source_audit']=result['source_audit']
    print(json.dumps(compact,indent=2))


if __name__=='__main__':main()
