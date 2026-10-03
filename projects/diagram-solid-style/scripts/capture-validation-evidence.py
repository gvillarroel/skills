#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seal current standalone style trials and retain all prior trial failures."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'evaluations/diagram-solid-style'
RUNS = ROOT / 'evaluations/runs'
SELECTED = {
    'mermaid': 12,
    'plantuml-colorset-renderer': 4,
    'echarts-animated-svg': 9,
    'slidev-echarts': 12,
    'slidev-animejs': 4,
    'slidev-quality-audit': 3,
}
spec = importlib.util.spec_from_file_location('pi_harness', ROOT / 'scripts/run-pi-skill-eval.py')
harness = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = harness
spec.loader.exec_module(harness)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_snapshot(source):
    result = {}
    for current, directories, files in os.walk(source):
        current = Path(current)
        directories[:] = [name for name in directories if name not in harness.COPY_IGNORE and (current / name).relative_to(source) not in harness.RUNTIME_EXCLUDED_DIRS]
        for name in files:
            path = current / name
            if name in harness.COPY_IGNORE or path.suffix.lower() in harness.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            result[path.relative_to(source).as_posix()] = {'sizeBytes': path.stat().st_size, 'sha256': digest(path)}
    return result


selected = []
for skill, attempt in SELECTED.items():
    folder = RUNS / f'20261003-diagram-solid-{skill}-luna-{attempt}'
    manifest = read(folder / 'run-manifest.json')
    result = read(folder / 'evaluation-result.json')
    events = read(folder / 'event-check.json')
    integrity = read(folder / 'skill-integrity-check.json')
    assert result['passed'] and events['passed'] and integrity['passed'], folder
    original = runtime_snapshot(ROOT / 'skills' / skill)
    current_digest = harness.snapshot_digest(original)
    assert current_digest == manifest['skill']['payloadSha256'], (skill, 'current source differs from validated payload')
    assert all(model['model'] == 'gpt-5.6-luna' for model in events['observedModels'])
    assert not any('git status' in (call.get('command') or '') or 'git diff' in (call.get('command') or '') for call in events['calls']), (skill, 'ancestor repository discovery')
    selected.append({
        'skill': skill, 'runId': folder.name, 'passed': True,
        'model': manifest['pi']['model'], 'profile': manifest['skill']['profile'],
        'startedAtUtc': result['startedAtUtc'], 'finishedAtUtc': result['finishedAtUtc'],
        'payloadSha256': current_digest, 'promptSha256': manifest['prompt']['sha256'],
        'expectedOutputs': manifest['expectedOutputs'],
        'outputHashes': {item['path']: item['sha256'] for item in read(folder / 'artifact-check.json')['outputs']},
        'toolCallCount': events['callCount'],
        'readPaths': sorted({call['path'] for call in events['calls'] if call['tool'] == 'read'}),
    })

failed = []
for folder in sorted(RUNS.glob('20261003-diagram-solid-*-luna-*')):
    if not (folder / 'evaluation-result.json').exists():
        continue
    result = read(folder / 'evaluation-result.json')
    if not result['passed']:
        failed.append({'runId': folder.name, 'gates': result['gates'], 'findings': read(folder / 'event-check.json').get('findings', [])})
failed.append({'runId': '20261003-diagram-solid-slidev-animejs-luna-3', 'manualRejection': 'Strict harness passed, but ancestor git status/diff exposed repository context; replaced by a clean standalone trial.'})

gallery = ROOT / 'skills/mermaid/assets/examples/mermaid-max-complexity'
manifest = read(gallery / 'gallery.json')
for item in manifest['patterns']:
    for field, hash_key in [('staticSvg', 'staticSha256'), ('animatedSvg', 'animatedSha256')]:
        path = gallery / item[field]
        assert b'\r' not in path.read_bytes(), path
        assert digest(path) == item[hash_key], path

report = {
    'date': '2026-10-03', 'scope': list(SELECTED), 'selectedTrials': selected,
    'retainedFailedTrials': failed,
    'mermaidFixture': {'families': 31, 'pairs': 62, 'svgCount': 124, 'alreadyLF': True, 'hashesMatch': True, 'manifestSha256': digest(gallery / 'gallery.json')},
    'echartsFixture': {'cards': 43, 'browserVerified': True},
    'plantumlFixture': {'reports': 2, 'resultCountPerPalette': 29, 'renderedCountPerPalette': 28, 'svgCount': 54, 'pngCount': 2, 'expectedUnavailableFamily': 'chronology'},
    'slidevEchartsAudit': {key: read(ROOT / 'projects/diagram-solid-style/artifacts/slidev-echarts-quality-final-4/quality-report.json')[key] for key in ['slideCount', 'stateCount', 'findingCount', 'severityCounts', 'ruleCounts']},
    'slidevAnimejsAudit': {key: read(ROOT / 'projects/diagram-solid-style/artifacts/slidev-animejs-quality-3/quality-report.json')[key] for key in ['slideCount', 'stateCount', 'findingCount', 'severityCounts', 'ruleCounts']},
    'actualEchartsSsr': read(ROOT / 'projects/diagram-solid-style/artifacts/ssr/results.json'),
    'markedAuditRegression': {key: read(ROOT / 'projects/diagram-solid-style/artifacts/audit-style-regression-3/quality-report.json')[key] for key in ['slideCount', 'stateCount', 'findingCount', 'severityCounts', 'ruleCounts']},
    'nativeMermaidPortableRegressions': {'testCount': 17, 'passed': True, 'script': 'skills/mermaid/scripts/test_native_solid.py'},
    'nativeMermaidComputedPaintAudit': {key: read(ROOT / 'projects/diagram-solid-style/artifacts/native-scan/native-style-summary.json')[key] for key in ['passed','staticFixtures','animatedFixtures','states','statesCovered','contrastPolicy','revealPolicy','zeroAreaAndCanvasPolicy']},
    'nativeMermaidIndependentReview': {key: read(ROOT / 'projects/solid-colorset-style/artifacts/composition-native-label-review-meta.json')[key] for key in ['checkedAtUtc','staticCount','stable','changedPaths','contrastFindings','outsideActorFindings','unexplainedRims','classifiedRims','method']},
    'nativeBrowserReview': read(ROOT / 'projects/diagram-solid-style/artifacts/review/browser-review.json'),
}
native_path = ROOT / 'projects/diagram-solid-style/artifacts/native-scan/native-style-summary.json'
native_rows = read(native_path)['rows']
report['nativeMermaidComputedPaintAudit'].update({
    'summarySha256': digest(native_path),
    'unexplainedRimCount': sum(len(row['unexplainedRims']) for row in native_rows),
    'contrastFindingCount': sum(len(row['contrastFindings']) for row in native_rows),
    'revealTargetCountsAcrossStates': {key: sum(row['animationState'][key] for row in native_rows) for key in ['opacityRevealTargets', 'hiddenRevealTargets', 'partialRevealTargets']},
})
report['nativeMermaidIndependentReview']['metadataSha256'] = digest(ROOT / 'projects/solid-colorset-style/artifacts/composition-native-label-review-meta.json')
(EVIDENCE / 'validation-20261003.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'selectedTrials': len(selected), 'allCurrentPayloadsMatch': True, 'retainedFailedTrials': len(failed), 'mermaidSvgCount': 124}))
