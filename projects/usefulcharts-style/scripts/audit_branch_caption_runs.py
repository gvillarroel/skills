#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replay caption outputs and inspect every completed model trace."""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def execute(args, log):
    result = subprocess.run(['uv','run','--script',*map(str,args)], cwd=ROOT, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    log.write_text(result.stdout+result.stderr, encoding='utf-8')
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+')
    args = parser.parse_args()
    for name in args.runs:
        run = ROOT/'evaluations/runs'/name
        model = json.loads((run/'run-manifest.json').read_text(encoding='utf-8'))['pi']['model'].split('/')[-1]
        completion = json.loads((run/'evaluation-result.json').read_text(encoding='utf-8'))
        folder = run/'workspace/result'
        browser = execute([ROOT/'skills/usefulcharts-style/scripts/audit_chart.py',folder/'poster.svg','--source',folder/'source.json',
                           '--report',run/'independent-browser-v2.json'],run/'independent-browser-v2.log')
        trace = execute([ROOT/'scripts/summarize-pi-json-events.py',run/'events.jsonl','--output',run/'trace-summary.json',
                         '--require-model',model,'--require-tool-call','--fail-on-invalid-json','--fail-on-tool-error',
                         '--require-read','../prompt.md','--forbid-read-regex',r'(?i)(^|[\\/])assets[\\/]examples([\\/]|$)',
                         '--forbid-read-regex',r'(?i)^skills[\\/](?!usefulcharts-style([\\/]|$))'],run/'trace-summary.log')
        if 'spark' in name:
            expected = json.loads(re.search(r'```json\s*(.*?)\s*```',(run/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
            source = json.loads((folder/'source.json').read_text(encoding='utf-8'))
            actual = {node['id']:node for node in source['nodes']}
            passed = json.loads((run/'workspace/draft.json').read_text(encoding='utf-8')) == expected
            passed = passed and all(all(actual[node['id']][key] == value for key,value in node.items()) for node in expected['nodes'])
            result = dict(status='pass' if passed and not browser else 'fail', scope='Exact-command control, not an aesthetic review.')
            result['version'] = 2
            (run/'independent-artifact-v2.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
            artifact = result['status'] != 'pass'
        else:
            artifact = execute([ROOT/'evaluations/contracts/verify-usefulcharts-branch-captions.py',run,
                                '--browser-report',run/'independent-browser-v2.json',
                                '--output',run/'independent-artifact-v2.json'],run/'independent-artifact-v2.log')
        print(json.dumps(dict(run=name,strict_pass=completion['passed'],browser_exit=browser,trace_exit=trace,artifact_exit=artifact)))


if __name__ == '__main__':
    main()
