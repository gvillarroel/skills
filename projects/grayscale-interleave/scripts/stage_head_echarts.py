#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Materialize committed gallery sources with current runtime palette templates."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = 'daaee75353c63ed6dde204d57cfdbae6b9936586'  # Qualified baseline HEAD before grayscale changes.
REL = 'skills/echarts-animated-svg/assets/examples/echarts-animated-svg'
CANONICAL = ROOT / REL
STAGE = ROOT / 'projects/grayscale-interleave/artifacts/staged-blobs/echarts-head-native'
GALLERY = STAGE / 'assets/examples/echarts-animated-svg'
BUILDER = 'scripts/build-gallery.mjs'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dirty_before = {name: digest(CANONICAL / name) for name in ['index.html', BUILDER]}
    tree = subprocess.run(['git', 'ls-tree', '-r', '--name-only', BASE, REL], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.splitlines()
    written = []
    for path in tree:
        relative = Path(path).relative_to(Path(REL))
        if relative.name == 'index.html' or relative.suffix in {'.svg', '.png', '.gif', '.mp4'}:
            continue
        content = subprocess.run(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout
        destination = GALLERY / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        written.append(relative.as_posix())
    # The committed builder imports ../../.. templates; copy only its runtime siblings.
    for folder in ['templates', 'palettes']:
        source = ROOT / 'skills/echarts-animated-svg/assets' / folder
        shutil.copytree(source, STAGE / 'assets' / folder, dirs_exist_ok=True)
    baseline_builder = subprocess.run(['git', 'show', f'{BASE}:{REL}/{BUILDER}'], cwd=ROOT,
                                      capture_output=True, check=True).stdout
    assert (GALLERY / BUILDER).read_bytes() == baseline_builder
    assert dirty_before == {name: digest(CANONICAL / name) for name in dirty_before}
    proof = {'ok': True, 'headRef': subprocess.run(['git', 'rev-parse', BASE], cwd=ROOT,
                                                  capture_output=True, text=True, check=True).stdout.strip(),
             'baselineBuilderSha256': hashlib.sha256(baseline_builder).hexdigest(),
             'writtenBaselineSources': written, 'dirtyWorkingSha256Before': dirty_before,
             'dirtyWorkingSha256After': {name: digest(CANONICAL / name) for name in dirty_before},
             'runtimeTemplateSource': 'skills/echarts-animated-svg/assets/templates',
             'runtimePaletteSource': 'skills/echarts-animated-svg/assets/palettes'}
    (STAGE / 'staging-proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
