#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run every bundled skill test and retain compact results plus local logs."""

import concurrent.futures
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'


def run(script):
    folder = ART/'tests'
    folder.mkdir(parents=True, exist_ok=True)
    temp = ART/'temporary'
    temp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    result = subprocess.run(['uv', 'run', '--script', str(script)], cwd=ROOT, env=env,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    text = result.stdout + result.stderr
    (folder/(script.stem+'.log')).write_text(text, encoding='utf-8')
    match = re.search(r'Ran (\d+) tests?', text)
    record = dict(script=script.relative_to(ROOT).as_posix(), exit_code=result.returncode,
                  tests=int(match.group(1)) if match else 0)
    print(json.dumps(record), flush=True)
    return record


def main():
    scripts = sorted((ROOT/'skills/usefulcharts-style/scripts').glob('test_*.py'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(run, scripts))
    (ART/'tests/summary.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    assert all(record['exit_code'] == 0 and record['tests'] for record in records)
    print(json.dumps(dict(status='pass', tests=sum(record['tests'] for record in records), suites=len(records))))


if __name__ == '__main__':
    main()
