#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Rebuild owned published examples from unchanged source semantics."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/arrow-contrast-composition/artifacts/regeneration';OUT.mkdir(parents=True,exist_ok=True)
commands=[]
def run(cmd):
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    commands.append({'command':cmd,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (OUT/'commands.json').write_text(json.dumps(commands,indent=2),encoding='utf-8')
    if result.returncode:raise SystemExit(result.stdout+result.stderr)

base=Path('skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg')
for stem,source in [('inference-pulse','composition-brief.json'),('heatwave-tree','heatwave-tree-brief.json')]:
    plan=OUT/f'{stem}-plan.json'
    run(['uv','run','--script','skills/compose-synchronized-svg/scripts/compile_synchronized_svg_plan.py','--brief',str(base/source),'--output',str(plan),'--force','--json'])
    run(['uv','run','--script','skills/compose-synchronized-svg/scripts/compose_synchronized_svg.py','--spec',str(plan),'--output',str(base/f'{stem}.svg'),'--report',str(OUT/f'{stem}-composition.json'),'--force','--json'])

base=Path('skills/usefulcharts-style/assets/examples/usefulcharts-style')
for stem in ['aurelian-families','atlas-of-inquiry','five-regional-histories']:
    run(['uv','run','--script','skills/usefulcharts-style/scripts/render_chart.py',str(base/f'{stem}.json'),'--svg',str(base/f'{stem}.svg'),'--html',str(base/f'{stem}.html'),'--report',str(OUT/f'{stem}.json')])
print(f'Regenerated examples with {len(commands)} successful commands.')
