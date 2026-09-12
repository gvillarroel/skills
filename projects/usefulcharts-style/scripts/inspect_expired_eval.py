#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil>=7,<8"]
# ///
"""Inspect or terminate only an expired Pi process in an exact evaluation workspace."""

import argparse
import json
import time
from pathlib import Path

import psutil


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('run',type=Path);parser.add_argument('--pid',type=int,required=True);parser.add_argument('--terminate',action='store_true')
args=parser.parse_args();run=args.run.resolve();workspace=(run/'workspace').resolve()
manifest=json.loads((run/'run-manifest.json').read_text(encoding='utf-8'))
process=psutil.Process(args.pid);created=process.create_time();cwd=Path(process.cwd()).resolve();command=process.cmdline()
assert cwd==workspace,f'Process workspace does not match: {cwd}'
assert process.name().lower()=='node.exe' and any('pi-coding-agent' in p for p in command),command
age=time.time()-created;assert age>manifest['pi']['timeoutSeconds'],'The process has not exceeded its recorded deadline.'
report=dict(run=manifest['runId'],pid=process.pid,process_created=created,cwd=str(cwd),elapsed_seconds=age,
    recorded_timeout=manifest['pi']['timeoutSeconds'],action='inspect',children=[])
children=process.children(recursive=True)
if args.terminate:
    for child in reversed(children):
        try:
            report['children'].append(dict(pid=child.pid,name=child.name(),created=child.create_time()))
            child.kill()
        except psutil.NoSuchProcess:pass
    assert process.create_time()==created,'Process identity changed.'
    process.kill();process.wait(timeout=15);report['action']='terminated-after-recorded-timeout'
(run/'expired-process-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
