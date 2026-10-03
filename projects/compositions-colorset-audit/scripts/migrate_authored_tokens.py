#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Migrate authored composition paint tokens; never touch imported media."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ['compose-synchronized-svg', 'diagram-composition', 'hierarchy-lens', 'usefulcharts-style', 'video', 'manim-svg-video']
PALETTES = json.loads((ROOT / 'skills/hyperframes-explainer/assets/palettes/colorsets.json').read_text())
ALLOWED = PALETTES['colorsets']['colorset2']['allowed']
HEX = re.compile(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])')

def rgb(token):
    return [int(token[i:i + 2], 16) for i in (1, 3, 5)]

def closest(token):
    original = rgb(token)
    return min(ALLOWED, key=lambda c: sum((a - b) ** 2 for a, b in zip(original, rgb(c))))

changes = []
for skill in SKILLS:
    bundle = ROOT / 'skills' / skill
    target = bundle / 'assets/palettes/colorsets.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(PALETTES, indent=2) + '\n', encoding='utf-8')
    for path in sorted(bundle.rglob('*')):
        if not path.is_file() or path.suffix not in {'.py', '.ts', '.js', '.json', '.html', '.svg', '.css', '.md'}:
            continue
        relative = path.relative_to(bundle).as_posix()
        if relative.startswith(('assets/maps/', 'assets/portraits/', 'assets/objects/', 'assets/vendor/')):
            continue
        if '/assets/earth-globe-wikimedia.svg' in relative or 'provenance.json' in relative or path.name.startswith('test_'):
            continue
        content = path.read_text(encoding='utf-8')
        mappings = {m.group(): closest(m.group()) for m in HEX.finditer(content) if m.group().lower() not in ALLOWED}
        if mappings:
            replacement = path.with_name(path.name + '.colorset-tmp')
            replacement.write_text(HEX.sub(lambda m: mappings.get(m.group(), m.group()), content), encoding='utf-8')
            replacement.replace(path)
            changes.append({'path': path.relative_to(ROOT).as_posix(), 'mappedTokens': mappings})
out = ROOT / 'projects/compositions-colorset-audit/artifacts/manifests/token-migration.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(changes, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'changedFiles': len(changes), 'manifest': str(out)}))
