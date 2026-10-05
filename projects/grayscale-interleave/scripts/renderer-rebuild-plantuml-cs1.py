#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0", "resvg-py>=0.5,<0.6"]
# ///
"""Refresh only the three affected CS1 native fixtures and retain all CS2 bytes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/plantuml-colorset-renderer'
GALLERY = SKILL / 'assets/examples/plantuml-colorset-renderer-cs1'
CS2 = SKILL / 'assets/examples/plantuml-colorset-renderer'
STAGE = ROOT / 'projects/grayscale-interleave/artifacts/renderer-plantuml-cs1-stage'
JAR = ROOT / 'projects/plantuml-colorset-renderer/artifacts/tools/plantuml-1.2026.6.jar'
COMMAND = ROOT / 'projects/visual-asset-composition/artifacts/tools/plantuml.cmd'
FIXTURES = {'archimate': 'svg', 'chart': 'svg', 'ditaa': 'png'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(directory):
    return {path.relative_to(directory).as_posix(): digest(path)
            for path in sorted(directory.rglob('*')) if path.is_file()}


def geometry(path):
    if path.suffix == '.png':
        with Image.open(path) as image:
            return image.size
    names = {'x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'rx', 'ry', 'r',
             'width', 'height', 'viewBox', 'd', 'points', 'transform', 'font-size',
             'font-family', 'font-weight', 'textLength', 'lengthAdjust', 'text-anchor'}
    return [(node.tag.rsplit('}', 1)[-1], {key: value for key, value in node.attrib.items()
                                        if key in names}, node.text if node.tag.endswith('text') else None)
            for node in ET.parse(path).getroot().iter()]


def main():
    if not JAR.is_file() or not COMMAND.is_file():
        raise FileNotFoundError(f'Local frozen PlantUML renderer not found: {JAR}')
    cs2_before = snapshot(CS2)
    gallery_before = snapshot(GALLERY)
    old = json.loads((GALLERY / 'render-report.json').read_text(encoding='utf-8'))
    before_geometry = {name: geometry(GALLERY / fmt / f'{name}.{fmt}')
                       for name, fmt in FIXTURES.items()}
    (STAGE / 'input').mkdir(parents=True, exist_ok=True)
    for name in FIXTURES:
        shutil.copyfile(SKILL / 'assets/examples/base' / f'{name}.puml', STAGE / 'input' / f'{name}.puml')
    report = STAGE / 'render-report.json'
    command = [sys.executable, str(SKILL / 'scripts/render_plantuml_directory.py'),
               str(STAGE / 'input'), '--output', str(STAGE / 'rendered'),
               '--colorset', 'colorset1', '--engine', 'cli',
               '--plantuml-command', str(COMMAND),
               '--coverage-manifest', str(SKILL / 'references/diagram-types.json'),
               '--publication-only', '--report', str(report)]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    (STAGE / 'command.json').write_text(json.dumps({'argv': command, 'exitCode': result.returncode,
                                                  'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n', encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    new = json.loads(report.read_text(encoding='utf-8'))
    records = {entry['source']: entry for entry in new['results']}
    if set(records) != {name + '.puml' for name in FIXTURES}:
        raise ValueError('The narrow build did not return exactly the requested fixtures.')
    for name, fmt in FIXTURES.items():
        source = STAGE / 'rendered' / fmt / f'{name}.{fmt}'
        if geometry(source) != before_geometry[name]:
            raise ValueError(f'Category-only refresh changed native geometry: {name}')
    old['results'] = [records.get(entry['source'], entry) for entry in old['results']]
    old['categoryOrderRefresh'] = {'scope': sorted(FIXTURES), 'nativeGeometryUnchanged': True,
                                   'otherResultsRetained': True}
    for name, fmt in FIXTURES.items():
        shutil.copyfile(STAGE / 'rendered' / fmt / f'{name}.{fmt}', GALLERY / fmt / f'{name}.{fmt}')
    (GALLERY / 'render-report.json').write_text(json.dumps(old, indent=2) + '\n', encoding='utf-8')
    cs2_after = snapshot(CS2)
    assert cs2_before == cs2_after, 'CS2 fixture bytes changed.'
    changed = [path for path, digest_after in snapshot(GALLERY).items()
               if gallery_before.get(path) != digest_after]
    expected_changes = {'render-report.json', *(f'{fmt}/{name}.{fmt}' for name, fmt in FIXTURES.items())}
    assert set(changed) <= expected_changes, changed
    proof = {'ok': True, 'rebuiltCs1Fixtures': list(FIXTURES), 'changedPaths': changed,
             'nativeGeometryUnchanged': True, 'preservedCs2Resources': len(cs2_before),
             'cs2Sha256Before': cs2_before, 'cs2Sha256After': cs2_after,
             'renderCommand': command}
    (STAGE / 'rebuild-proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in proof.items() if not key.startswith('cs2Sha')}, indent=2))


if __name__ == '__main__':
    main()
