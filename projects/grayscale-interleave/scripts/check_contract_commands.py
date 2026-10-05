#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the existing exact-command event gate to every retained contract trace."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('pi_harness', ROOT / 'scripts/run-pi-skill-eval.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
rows = []
for run in sorted((ROOT / 'evaluations/runs').glob('gray-20261005-*-contract-1')):
    if not (run / 'evaluation-result.json').exists():
        continue
    manifest = json.loads((run / 'run-manifest.json').read_bytes())
    report = helper.event_check_report(events_path=run/'events.jsonl', prompt=(run/'prompt.md').read_text(encoding='utf-8'),
        require_prompt_read_first=True, require_exact_command_from_prompt=True, require_observed_model=True,
        requested_model=manifest['pi']['model'], fail_on_invalid_json=True, fail_on_tool_error=True,
        forbid_read_regex=manifest['eventPolicy']['forbidReadRegex'], forbid_command_regex=[])
    rows.append({'runId':run.name,'passed':report['passed'],'findings':report['findings'],
                 'evidenceSha256':{name:hashlib.sha256((run/name).read_bytes()).hexdigest()
                                  for name in ('prompt.md','events.jsonl','run-manifest.json')}})
out = ROOT / 'projects/grayscale-interleave/artifacts/reviews/contract-command-check.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(rows),'passed':sum(r['passed'] for r in rows),'failures':[r for r in rows if not r['passed']]},indent=2))
