#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare the caption request with the retained, verified v32 runtime."""

import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'
FROZEN = ROOT/'evaluations/runs/usefulcharts-v32b-context-1-20260912/workspace/skills/usefulcharts-style'


def execute(source, bundle, out):
    out.mkdir(parents=True, exist_ok=False)
    (out/'draft.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    commands = [
        [sys.executable,str(bundle/'scripts/compose_branching_history.py'),str(out/'draft.json'),'--output',str(out/'source.json'),'--report',str(out/'composition.json')],
        [sys.executable,str(bundle/'scripts/render_chart.py'),str(out/'source.json'),'--svg',str(out/'poster.svg'),'--html',str(out/'poster.html'),'--report',str(out/'layout.json')],
        ['uv','run','--script',str(bundle/'scripts/audit_chart.py'),str(out/'poster.svg'),'--source',str(out/'source.json'),'--report',str(out/'browser.json'),'--png',str(out/'poster.png')],
    ]
    records = []
    for index, command in enumerate(commands):
        completed = subprocess.run(command,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
                                   capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=900)
        output = completed.stdout+completed.stderr
        (out/f'step-{index}.log').write_text(output,encoding='utf-8')
        records.append(dict(step=index,exit_code=completed.returncode,tail=output[-1200:]))
        if completed.returncode:
            break
    (out/'execution.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(case=out.name,steps=[dict(step=r['step'],exit_code=r['exit_code']) for r in records])),flush=True)
    return records


def main():
    harness = runpy.run_path(str(ROOT/'scripts/run-pi-skill-eval.py'))
    snapshot = harness['snapshot_tree'](FROZEN)
    digest = harness['snapshot_digest'](snapshot)
    assert len(snapshot)==104 and digest=='85f1eb0bf430e1b20692642d419d0c508ec75fba72bbcf0f8a3b7624997cdba4'
    source = json.loads((ART/'caption-case.json').read_text(encoding='utf-8'))
    old = execute(source,FROZEN,ART/'baseline-caption-request')
    source.pop('annotations')
    before = execute(source,FROZEN,ART/'publishing-without-captions')
    assert harness['snapshot_tree'](FROZEN)==snapshot
    result = dict(frozen_bundle_sha256=digest,frozen_bundle_files=len(snapshot),bundle_unchanged=True,
                  caption_request=old,without_captions=before,
                  scope='Deterministic counterfactual replay on the retained runtime, not another model trial.')
    (ART/'baseline-replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
