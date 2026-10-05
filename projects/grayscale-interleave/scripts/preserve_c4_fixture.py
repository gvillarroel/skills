#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain source-bound C4 fixture when unchanged named roles outlive a bad rebuild."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = 'daaee75353c63ed6dde204d57cfdbae6b9936586'  # Qualified baseline HEAD before grayscale changes.
REL = 'skills/mermaid/assets/examples/mermaid-max-complexity'
GALLERY = ROOT / REL
OUT = ROOT / 'projects/grayscale-interleave/artifacts/reviews/c4-preserved'
PATHS = ['source/colorset1/c4.mmd', 'svg/colorset1/c4.static.svg',
         'svg/colorset1/c4.animated.svg']


def head(path):
    return subprocess.run(['git', 'show', f'{BASE}:{REL}/{path}'], cwd=ROOT,
                          capture_output=True, check=True).stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_now = (GALLERY / PATHS[0]).read_text(encoding='utf-8')
    source_before = head(PATHS[0]).decode('utf-8')
    body_now = source_now.split('\nC4Context\n', 1)[1]
    body_before = source_before.split('\nC4Context\n', 1)[1]
    assert body_now == body_before, 'Cannot preserve a fixture with changed C4 facts or named roles.'
    records = []
    for path in PATHS:
        current = (GALLERY / path).read_bytes()
        old = head(path)
        rejected = OUT / 'rejected-native-rebuild' / path
        rejected.parent.mkdir(parents=True, exist_ok=True)
        if not rejected.exists():
            rejected.write_bytes(current)
        current = rejected.read_bytes()
        (GALLERY / path).write_bytes(old)
        records.append({'path': f'{REL}/{path}', 'rejectedSha256': hashlib.sha256(current).hexdigest(),
                        'preservedHeadSha256': hashlib.sha256(old).hexdigest()})
    manifest = json.loads((GALLERY / 'gallery.json').read_text(encoding='utf-8'))
    baseline = json.loads(head('gallery.json'))
    prior = next(record for record in baseline['patterns'] if record['id'] == 'mermaid-c4-cs1')
    manifest['patterns'] = [prior if record['id'] == prior['id'] else record for record in manifest['patterns']]
    payload = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    (GALLERY / 'gallery.json').write_bytes(payload)
    report = json.loads((GALLERY / 'reports/build-report.json').read_text(encoding='utf-8'))
    report['manifestSha256'] = hashlib.sha256(payload).hexdigest()
    (GALLERY / 'reports/build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    proof = {'ok': True, 'c4FactsAndNamedRoleSourceBodyUnchanged': True,
             'preservedSourceStaticAndAnimatedExactlyFromHEAD': records,
             'rejectedNativeRegeneration': 'Overlapping native relationship captions and insufficient medium-gray label contrast.',
             'indexedCategoryFixture': False, 'manifestPatternRestoredExactly': prior}
    (OUT / 'preservation-proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
