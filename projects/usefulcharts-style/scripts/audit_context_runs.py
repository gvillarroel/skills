#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently replay every completed context-refinement trial, including failures."""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def execute(args, log):
    result=subprocess.run(['uv','run','--script',*map(str,args)],cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True)
    log.write_text(result.stdout+result.stderr,encoding='utf-8')
    return result.returncode


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',nargs='+')
    args=parser.parse_args()
    for name in args.runs:
        run=ROOT/'evaluations/runs'/name
        completion=json.loads((run/'evaluation-result.json').read_text(encoding='utf-8'))
        model=json.loads((run/'run-manifest.json').read_text(encoding='utf-8'))['pi']['model'].split('/')[-1]
        folder=run/'workspace/result'
        browser_exit=execute([ROOT/'skills/usefulcharts-style/scripts/audit_chart.py',folder/'poster.svg','--source',folder/'source.json',
                              '--report',run/'independent-browser.json'],run/'independent-browser.log')
        trace_exit=execute([ROOT/'scripts/summarize-pi-json-events.py',run/'events.jsonl','--output',run/'trace-summary.json',
                            '--require-model',model,'--require-tool-call','--fail-on-invalid-json','--fail-on-tool-error',
                            '--require-read','../prompt.md','--forbid-read-regex',r'(?i)(^|[\\/])assets[\\/]examples([\\/]|$)',
                            '--forbid-read-regex',r'(?i)^skills[\\/](?!usefulcharts-style([\\/]|$))'],run/'trace-summary.log')
        if 'spark' in name:
            expected=json.loads(re.search(r'```json\s*(.*?)\s*```',(run/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
            supplied=json.loads((run/'workspace/draft.json').read_text(encoding='utf-8'))
            output=json.loads((folder/'source.json').read_text(encoding='utf-8'))
            browser=json.loads((run/'independent-browser.json').read_text(encoding='utf-8'))
            passed=expected==supplied and output['nodes']==expected['nodes'] and output['insets']==expected['insets'] and not browser['findings'] and not browser['composition_warnings']
            contract=dict(status='pass' if passed else 'fail',exact_prompt_source=expected==supplied,
                          scope='Command control with 14 distinct symbols and two insets. No visual-parity or agent image-review claim.')
            (run/'independent-artifact.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
            artifact_exit=not passed
        else:
            artifact_exit=execute([ROOT/'evaluations/contracts/verify-usefulcharts-context-insets.py',run,'--output',run/'independent-artifact.json'],run/'independent-artifact.log')
        print(json.dumps(dict(run=name,strict_pass=completion['passed'],browser_exit=browser_exit,trace_exit=trace_exit,artifact_exit=artifact_exit)))


if __name__=='__main__':main()
