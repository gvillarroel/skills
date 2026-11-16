#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently review isolated outputs and clean runtime read surfaces."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'evaluations/line-world-google-vids'
rows=json.loads((folder/'offline-results-20261115.json').read_text())['results']
rows+=[{'case':'final-naturalistic','runId':'20261115-line-world-vids-final-naturalistic-1'},{'case':'orchestrator-routing','runId':'20261115-line-world-vids-routing-1'}]
results=[]
for row in rows:
    root=ROOT/'evaluations/runs'/row['runId'];ws=root/'workspace';gate=json.loads((root/'evaluation-result.json').read_text());trace=json.loads((root/'event-check.json').read_text())
    assert gate['passed'] and trace['passed'] and not trace['findings']
    reads=[c['path'] for c in trace['calls'] if c['tool']=='read']
    assert not any('assets/examples' in x.replace('\\','/') for x in reads)
    assert all((m['provider'],m['model'])==('openai-codex','gpt-6.1-sol') for m in trace['observedModels'])
    assert json.loads((root/'skill-integrity-check.json').read_text())['passed']
    if row['case']=='boundary':
        assert json.loads((ws/'boundary/check.json').read_text())['rejected'] is True
        assert all(s['observed'] is False for s in json.loads((ws/'draft/observed.json').read_text())['scenes'])
    elif row['case']=='orchestrator-routing':
        a=json.loads((ws/'release/route.json').read_text());assert a['companionSkill']=='line-world-google-vids' and a['guideColor']=='#9e1b32' and a['visibleTitles'] is False and a['nativeVoiceTimingRequired'] is True and a['localRenderCountsAsNativeExport'] is False
    else:
        a=json.loads((ws/'release/timing.json').read_text());source=json.loads((ws/'inputs/story.json').read_text());expected=306 if row['case']=='generalization' else 1908
        assert a['frames']==expected and a['status']=='measured-native-timing'
        assert [s['id'] for s in a['scenes']]==[s['id'] for s in source['scenes']]
        assert [s['script'] for s in a['scenes']]==[s['script'] for s in source['scenes']]
        end=0
        for s in a['scenes']:
            assert s['startFrame']==end and s['frames']>0;end=s['endFrame']
            assert s['voiceoverSeconds']+s.get('audioLeadSeconds',0)+s.get('tailSeconds',0)<=s['duration']+1/a['fps']
        assert end==a['frames']
        if row['case']!='generalization':assert all(s['observed'] is False for s in json.loads((ws/'handoff/observed.json').read_text())['scenes'])
    cmd=['uv','run','--script',str(ROOT/'scripts/summarize-pi-json-events.py'),str(root/'events.jsonl'),'--output',str(root/'reviewed-read-surface.json'),'--require-model','gpt-6.1-sol','--fail-on-invalid-json','--fail-on-tool-error']
    subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True)
    results.append({'case':row['case'],'runId':row['runId'],'passed':True,'readSurface':reads,'model':'openai-codex/gpt-6.1-sol','durationSeconds':gate['durationSeconds']})
(folder/'reviewed-evidence-20261115.json').write_text(json.dumps({'ok':True,'cases':results,'note':'Offline artifact/read-surface validation only. Native UI and downloaded media are separate evidence.'},indent=2)+'\n')
print(json.dumps({'ok':True,'isolatedRuns':len(results),'cases':[r['case'] for r in results]}))
