#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise all named D3 builder and procedural catalog palette output paths."""
from pathlib import Path
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'projects/colorset-audit/artifacts'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'skills/d3/scripts'))
from check_palette_contract import validate_artifact

results = []
def command(argv):
    result = subprocess.run(argv, cwd=ROOT, text=True, encoding='utf-8', capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{argv}: {result.stderr[-2500:]} {result.stdout[-2500:]}')
    return result

for builder in sorted((ROOT / 'skills/d3/scripts').glob('build*.py')):
    if 'colorset_output' not in builder.read_text():
        continue
    for active in ('colorset1', 'colorset2'):
        output = OUT / 'html' / f'{builder.stem}-{active}.html'
        flags = [] if active == 'colorset1' else ['--colorset', active]
        if builder.stem == 'build_agent_loop_overlay': flags += ['--force']
        command([sys.executable, str(builder), str(output), *flags])
        check = validate_artifact(output, colorset=active)
        if not check['ok']:
            raise RuntimeError(f'{builder.name}/{active}: {check}')
        results.append({'kind':'d3-named-builder', 'builder':builder.relative_to(ROOT).as_posix(), 'colorset':active, 'output':output.relative_to(ROOT).as_posix(), 'palettePass':True})

for active in ('colorset1', 'colorset2'):
    for motion in ('full', 'reduced'):
        folder = OUT / 'svgs' / f'procedural-{active}-{motion}'
        command(['uv','run','--script','skills/procedural-svg-animation/scripts/build_procedural_svg.py','--all',str(folder),'--palette',active,'--motion',motion,'--seed','827','--force','--json'])
        paths = sorted(folder.glob('*.svg'))
        report = OUT / 'data' / f'procedural-{active}-{motion}-validation.json'
        command(['uv','run','--script','skills/procedural-svg-animation/scripts/validate_procedural_svg.py',*map(str,paths),'--expected-palette',active,'--expect-motion',motion,'--require-standalone','--report',str(report)])
        for path in paths:
            root = ET.fromstring(path.read_text(encoding='utf-8'))
            results.append({'kind':'procedural-pattern', 'patternId':root.get('data-pattern-id'), 'colorset':active, 'motion':motion, 'output':path.relative_to(ROOT).as_posix(), 'palettePass':True})

# Negative regression: metadata cannot conceal arbitrary animated paint.
sample = OUT / 'svgs/procedural-colorset1-full/procedural-svg-gradient-cycle.svg'
root = ET.fromstring(sample.read_text(encoding='utf-8'))
element = next(e for e in root.iter() if e.tag.endswith('stop'))
element.set('stop-color','#123456')
tampered = OUT / 'svgs/off-palette-stop.svg'
tampered.write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8')
negative = subprocess.run(['uv','run','--script','skills/procedural-svg-animation/scripts/validate_procedural_svg.py',str(tampered)],cwd=ROOT,capture_output=True,text=True)
if negative.returncode == 0:
    raise RuntimeError('Off-palette gradient stop was accepted')
results.append({'kind':'negative-paint-mutation','mutation':'gradient-stop-#123456','rejected':True})
record = OUT / 'data/custom-generated-coverage.json'
record.parent.mkdir(parents=True,exist_ok=True)
record.write_text(json.dumps({'ok':True,'caseCount':len(results),'results':results},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'caseCount':len(results),'record':str(record)}))
