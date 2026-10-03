#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Build native panels, compose the figure, and audit exact outputs in one run."""

import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode=True
from build_panels import build
from compose_diagram import compose, require, write_target
from audit_diagram import run as audit


def render(brief,output,overwrite=False):
    spec=json.loads(brief.read_text(encoding='utf-8-sig'))
    paths={name:output/name for name in ('plan.json','figure.svg','report.json','audit.json','preview.png')}
    require(brief.resolve() not in {p.resolve() for p in paths.values()},'Keep the authored brief separate from generated outputs')
    generated,assets,_=build(spec,brief.parent)
    measurements={p['id']:output/('geometry-'+p['id']+'.json') for p in generated['panels']}
    for panel in generated['panels']:
        source=(brief.parent/panel['source']).resolve()
        require(source not in {p.resolve() for p in [*paths.values(),*measurements.values()]},'Panel path collides with a generated output')
        panel['source']=os.path.relpath(source,output.resolve()).replace('\\','/')
    destinations=[*paths.values(),*measurements.values(),*[p for p,_ in assets]]
    require(len({p.resolve() for p in destinations})==len(destinations),'Generated paths must be distinct')
    require(brief.resolve() not in {p.resolve() for p in destinations},'Generated panel cannot replace its authored brief')
    for path in destinations:write_target(path,overwrite)
    for path,content in assets:path.write_text(content,encoding='utf-8')
    for panel in generated['panels']:
        source=(output/panel['source']).resolve()
        geometry=audit(SimpleNamespace(command='measure',input=source,output=None,
                                       report=measurements[panel['id']],overwrite=overwrite))
        panel['objects']=geometry['objects']
        panel['routingObstacles']=geometry['routingObstacles']
        panel['ports']={**geometry['ports'],**panel.get('ports',{})}
    paths['plan.json'].write_text(json.dumps(generated,indent=2)+'\n',encoding='utf-8')
    svg,report=compose(generated,paths['plan.json'])
    paths['figure.svg'].write_text(svg,encoding='utf-8')
    paths['report.json'].write_text(json.dumps({**report,'ok':True},indent=2)+'\n',encoding='utf-8')
    result=audit(SimpleNamespace(command='audit',input=paths['figure.svg'],report=paths['audit.json'],
                               screenshot=paths['preview.png'],output=None,overwrite=overwrite))
    return {'ok':result['ok'],'issues':result['issues'],'semanticColors':result['semanticColors']['status'],
            'minimumObservedPx':result['minimumObservedPx'],'outputs':{k:str(v) for k,v in paths.items()}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--brief',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--overwrite',action='store_true')
    ap.add_argument('--inspect',action='store_true')
    args=ap.parse_args()
    status=args.output_dir/'render-status.json'
    status_safe=False
    try:
        spec=json.loads(args.brief.read_text(encoding='utf-8-sig'))
        protected={args.brief.resolve(),*((args.brief.parent/p['source']).resolve() for p in spec['panels'])}
        require(status.resolve() not in protected,'Status path cannot replace an authored input or panel')
        write_target(status,args.overwrite)
        status_safe=True
        result=render(args.brief,args.output_dir,args.overwrite)
    except Exception as exc:
        result={'ok':False,'error':str(exc)}
    # A failed draft never claims that an older figure/audit is a new success.
    if status_safe:
        status.parent.mkdir(parents=True,exist_ok=True)
        status.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
    return 0 if result['ok'] or args.inspect else 1


if __name__=='__main__':raise SystemExit(main())
