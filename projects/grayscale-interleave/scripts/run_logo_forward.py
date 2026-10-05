#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the changed D3 logo builder through one contract and three forwards."""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--revision', default='r2')
parser.add_argument('--timeout', type=int, default=600)
args = parser.parse_args()
out = ROOT / 'projects/grayscale-interleave/artifacts/reviews/logo-forward'
out.mkdir(parents=True,exist_ok=True)
rows = []
for family, count, prompt in [('contract',1,'contract'),('naturalistic',3,'natural')]:
    for repeat in range(1,count+1):
        run_id = f'gray-20261005-logo-{args.revision}-d3-{family}-{repeat}'
        command = ['uv','run','--script','scripts/run-pi-skill-eval.py','d3','--prompt-file',
                   f'evaluations/pi-prompts/colorset1-gray-order-d3-logo-{prompt}-20261005.md',
                   '--model','openai-codex/gpt-5.6-luna','--thinking','medium','--mode','json','--strict',
                   '--run-id',run_id,'--timeout-seconds',str(args.timeout)]
        if family=='contract':
            command.append('--require-exact-command-from-prompt')
        for path in ['deliverables/logo.html','deliverables/validation.json','deliverables/native.json','deliverables/small-logo.png']:
            command.extend(['--expect-output',path])
        result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (out/f'{run_id}.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        rows.append({'runId':run_id,'family':family,'returnCode':result.returncode,'command':command})
        (out/f'{args.revision}-dispatches.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:rows[-1][k] for k in ('runId','returnCode')}),flush=True)
