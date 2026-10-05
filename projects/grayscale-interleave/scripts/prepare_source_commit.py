#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Review and stage explicit revision paths while preserving unrelated drafts."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXCLUDED = {'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html',
            'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs'}


def paths(*arguments):
    result = subprocess.run(['git',*arguments],cwd=ROOT,capture_output=True,check=True)
    return [p for p in result.stdout.decode('utf-8').split('\0') if p]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',action='store_true')
    args=parser.parse_args()
    owners=set(json.loads((ROOT/'evaluations/grayscale-interleave/cases.json').read_bytes()))
    existing=paths('diff','--cached','--name-only','-z')
    changed=set(paths('diff','--name-only','-z')) | set(existing) | set(paths('ls-files','--others','--exclude-standard','-z'))
    selected,preserved=[],[]
    for relative in sorted(changed):
        parts=Path(relative).parts
        include=(relative in {'SKILLS.md','docs/colorsets.json','docs/colorsets.md','scripts/validate-colorsets.py','scripts/test-colorsets.py'}
                 or (len(parts)>2 and parts[0]=='skills' and parts[1] in owners)
                 or relative.startswith('evaluations/grayscale-interleave/')
                 or relative.startswith('projects/grayscale-interleave/')
                 or relative.startswith('evaluations/pi-prompts/colorset1-gray-order-d3-logo-'))
        if not include or relative in EXCLUDED:
            preserved.append(relative)
            continue
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or any(p in {'node_modules','artifacts','runs','__pycache__'} for p in parts):
            raise ValueError(f'Unsafe or generated source candidate: {relative}')
        selected.append({'path':relative,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    names=[row['path'] for row in selected]
    if args.stage:
        if any(name not in names for name in existing):
            raise ValueError('Existing staged source includes unrelated work')
        # Keep argv below the Windows command-line limit without broad git add.
        for start in range(0,len(names),35):
            subprocess.run(['git','add','--',*names[start:start+35]],cwd=ROOT,check=True,capture_output=True)
        if sorted(paths('diff','--cached','--name-only','-z'))!=names:
            raise ValueError('Staged paths differ from the reviewed candidate inventory')
        subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    report={'staged':args.stage,'candidateCount':len(selected),'candidates':selected,'preserved':preserved,
            'echartsPublicationDecision':'Preserve HEAD index/builder. Isolated current-module CS2 regeneration changes only a non-rendering timestamp; native structure is identical.'}
    out=ROOT/'projects/grayscale-interleave/artifacts/manifests/source-staging.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'staged':args.stage,'candidateCount':len(selected),'preserved':preserved},indent=2))


if __name__=='__main__':
    main()
