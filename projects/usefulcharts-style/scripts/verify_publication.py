#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify a successful Pages deployment and exact public poster source bytes."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import urllib.request
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--workflow',required=True)
    parser.add_argument('--report',required=True,type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[3]
    run=json.loads(subprocess.check_output(['gh','run','view',args.workflow,'--json','status,conclusion,headSha,url'],cwd=root))
    commit=subprocess.check_output(['git','rev-parse',args.commit],cwd=root).decode().strip()
    assert run['status']=='completed' and run['conclusion']=='success' and run['headSha']==commit,run
    spec=importlib.util.spec_from_file_location('pages_builder',root/'scripts/build-pages.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    base='https://gvillarroel.github.io/skills/examples/usefulcharts-style/'
    names=['index.html','manifest.json']+[f'{name}.{ext}' for name in ('aurelian-families','atlas-of-inquiry','five-regional-histories') for ext in ('json','svg','html')]
    checked=[]
    for name in names:
        expected=subprocess.check_output(['git','show',f'{commit}:skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}'],cwd=root)
        text=expected.decode('utf-8')
        if name=='index.html':
            text=builder.ensure_html_favicon(builder.ensure_html_head_meta(text,'usefulcharts-style'))
            for key,value in {'data-example-id':'usefulcharts-style','data-pattern-id':'usefulcharts-style','data-pattern-page':'true'}.items():
                text=builder.ensure_body_attribute(text,key,value)
        lines=[line.rstrip(' \t') for line in text.splitlines()]
        while lines and not lines[-1]:lines.pop()
        expected=('\n'.join(lines)+'\n').encode('utf-8')
        request=urllib.request.Request(base+name,headers={'User-Agent':'Codex-UsefulCharts-Publication-Verification/1.0'})
        with urllib.request.urlopen(request,timeout=45) as response:
            actual=response.read();status=response.status
        assert status==200 and actual==expected,f'Published bytes differ for {name}'
        checked.append(dict(file=name,status=status,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest()))
    with urllib.request.urlopen('https://gvillarroel.github.io/skills/',timeout=45) as response:catalog=response.read().decode('utf-8')
    assert 'examples/usefulcharts-style/' in catalog,'The main catalog is missing the example set.'
    report=dict(status='pass',commit=commit,workflow=run,url=base,files=checked,main_catalog_link=True,
        transformations='The standard Pages build adds gallery metadata/favicon and normalizes trailing whitespace and line endings. Compare the complete expected published bytes after those documented transforms.')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',commit=commit,files=len(checked),url=base,report=str(args.report))))


if __name__=='__main__':main()
