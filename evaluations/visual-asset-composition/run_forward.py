#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run preregistered, isolated composition cases and retain every attempt."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARTIFACTS = ROOT / 'projects/visual-asset-composition/artifacts'


def run_case(task):
    skill, kind, case, repetition, cohort = task
    run_id = f'assets-{skill}-{kind}-20260927-{cohort}-{repetition}'
    command = ['uv', 'run', '--script', 'scripts/run-pi-skill-eval.py', skill,
               '--prompt-file', f'evaluations/pi-prompts/assets-{skill}-{kind}.md',
               '--model', 'openai-codex/gpt-5.6-luna', '--thinking', 'medium',
               '--mode', 'json', '--strict', '--timeout-seconds', '600', '--run-id', run_id]
    for artifact in case['outputs']:
        command.extend(['--expect-output', artifact])
    if kind == 'contract':
        command.append('--require-exact-command-from-prompt')
    environment = dict(os.environ)
    environment['PATH'] = str(ARTIFACTS / 'tools') + os.pathsep + environment['PATH']
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    log = ARTIFACTS / 'pi-logs' / f'{run_id}.txt'
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    row = {'runId': run_id, 'skill': skill, 'case': kind, 'repetition': repetition,
           'exitCode': result.returncode, 'command': command, 'outputs': case['outputs'],
           'log': log.relative_to(ROOT).as_posix()}
    print(json.dumps(row), flush=True)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cohort', required=True)
    parser.add_argument('--skills', nargs='+')
    parser.add_argument('--cases', nargs='+', default=['contract','naturalistic','boundary','generalization'])
    args = parser.parse_args()
    definitions = json.loads((HERE/'cases.json').read_text(encoding='utf-8'))
    tasks = [(skill,kind,case,repeat,args.cohort)
             for skill,cases in definitions.items() if not args.skills or skill in args.skills
             for kind,case in cases.items() if kind in args.cases
             for repeat in range(1, (3 if kind in {'naturalistic','generalization'} else 1)+1)]
    rows=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run_case,t) for t in tasks]):
            rows.append(future.result())
            label='-'.join(args.skills or ['all'])+'-'+'-'.join(args.cases)
            (ARTIFACTS/f'pi-{args.cohort}-{label}.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    return int(any(r['exitCode'] for r in rows))


if __name__=='__main__':
    raise SystemExit(main())
