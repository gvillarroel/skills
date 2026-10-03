#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect independent browser, semantic, and trace evidence after one Pi run."""

import argparse
import json
import subprocess
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run',type=Path)
    ap.add_argument('--case',choices=['contract','naturalistic','boundary','generalization'],required=True)
    ap.add_argument('--stem',required=True)
    args=ap.parse_args()
    result_path=args.run/'evaluation-result.json'
    if not result_path.is_file():raise SystemExit('The runtime has not finished; retain its current session.')
    evidence=Path('evaluations/diagram-composition')
    artifacts=Path('projects/diagram-composition/artifacts')
    audit=artifacts/'reviews'/(args.stem+'.json')
    trace=evidence/(args.stem+'-trace.json')
    artifact=evidence/(args.stem+'-artifact.json')
    svg=args.run/'workspace/out/figure.svg'
    commands=[
        ['uv','run','--script','scripts/summarize-pi-json-events.py',str(args.run/'events.jsonl'),
         '--require-model','gpt-5.6-luna','--fail-on-invalid-json','--fail-on-tool-error','--output',str(trace)],
        ['uv','run','--script','skills/diagram-composition/scripts/audit_diagram.py','audit',
         '--input',str(svg),'--report',str(audit),'--screenshot',str(artifacts/'images'/(args.stem+'.png')),'--overwrite'],
        ['uv','run','--script','evaluations/contracts/check-diagram-polish.py',str(args.run),'--case',args.case,
         '--audit',str(audit),'--output',str(artifact)]]
    exits=[]
    for command in commands:
        process=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        exits.append(process.returncode)
        if process.returncode and not process.stdout.strip():print(process.stderr[:1200])
    record={'runId':args.run.name,'case':args.case,'commandExitCodes':exits,
            'payload':json.loads((args.run/'run-manifest.json').read_text())['skill'],
            'runtime':json.loads(result_path.read_text()),
            'artifact':json.loads(artifact.read_text()) if artifact.is_file() else None,
            'tracePassed':json.loads(trace.read_text())['passed'] if trace.is_file() else None}
    (evidence/(args.stem+'-collected.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'runId':record['runId'],'exits':exits,'payload':record['payload'],
                      'runtime':record['runtime'],'artifact':record['artifact']}))
    return 0 if not any(exits) else 1


if __name__=='__main__':raise SystemExit(main())
