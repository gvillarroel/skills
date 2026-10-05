#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record native-caption source freeze and retain superseded visual failures."""
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('integrity', Path(__file__).with_name('source_integrity.py'))
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


def files(skill):
    bundle = ROOT / 'skills' / skill
    result = {}
    for current, directories, filenames in os.walk(bundle):
        parent = Path(current)
        directories[:] = sorted(name for name in directories if name not in integrity.HARNESS.COPY_IGNORE and (parent / name).relative_to(bundle) not in integrity.HARNESS.RUNTIME_EXCLUDED_DIRS)
        for name in sorted(filenames):
            path = parent / name
            if name not in integrity.HARNESS.COPY_IGNORE and path.suffix.lower() not in integrity.HARNESS.SNAPSHOT_IGNORED_SUFFIXES:
                result[path.relative_to(bundle).as_posix()] = {'sizeBytes': path.stat().st_size, 'sha256': integrity.HARNESS.sha256_file(path)}
    return result


snapshot = {name: {'runtimeFiles': files(name), 'payloadSha256': integrity.runtime_digest(name)} for name in ['slidev-echarts', 'echarts-animated-svg']}
assert snapshot['echarts-animated-svg']['payloadSha256'] == 'b51f5e3e971863ccc196b8d13cf70f6b67ccddf593019d390c87293125eaa8e4'
for number in [2, 3]:
    name = f'compact-slidev-echarts-20261004-sol-first-probe-final-natural-{number}'
    path = ROOT / 'projects/diagram-compactness/artifacts/reviews' / name / 'independent-deck/manual-review.json'
    previous = json.loads(path.read_text(encoding='utf-8'))
    previous.update({'passed': False, 'pendingRawPixelConfirmation': False, 'rawPixelConfirmation': 'Default resized and reduced native PNGs both contain Analyze→Review shaft crossing the leading glyphs of Failed sample. Default authored/captured native pixels confirm the collision; animations-disabled resized capture was artificially more permissive. No reduced-only font/cache cause is claimed.', 'pixelProof': 'projects/diagram-compactness/artifacts/reviews/caption-default-diagnosis/comparison.json', 'regressionProof': 'projects/diagram-compactness/artifacts/reviews/caption-placement-regression-final/report.json'})
    path.write_text(json.dumps(previous, indent=2), encoding='utf-8')
report = {'frozen': True, 'skills': snapshot, 'focusedTests': 'evaluations/runs/20261005-compaction-renderers-manual/slidev-caption-search-native-final/test-report.json', 'actualDefaultNativeRegression': 'projects/diagram-compactness/artifacts/reviews/caption-placement-regression-final/report.json', 'authoringAudit': 'projects/diagram-compactness/artifacts/reviews/slidev-caption-placement-source-freeze.json', 'nextCohortRevision': 'sol-caption-placement-final'}
out = ROOT / 'projects/diagram-compactness/artifacts/reviews/slidev-caption-placement-source-snapshot.json'
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'frozen': True, 'skills': {name: {'files': len(value['runtimeFiles']), 'sha256': value['payloadSha256']} for name, value in snapshot.items()}, 'snapshot': str(out)}))
