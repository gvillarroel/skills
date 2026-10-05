#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a source-identical retained trial deck in evaluator-owned artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run_id')
args = parser.parse_args()
trial = ROOT / 'evaluations/runs' / args.run_id / 'workspace'
trial.resolve().relative_to(ROOT / 'evaluations/runs')
output = ROOT / 'projects/diagram-compactness/artifacts/reviews' / args.run_id / 'independent-retained-build'
workspace = output / 'workspace'
assert not output.exists(), 'Use a fresh evaluator-owned build; never overwrite prior evidence.'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
sources = {path.relative_to(trial).as_posix(): digest(path) for path in [trial / 'deck/slides.md', trial / 'deck/package.json', trial / 'deck/components/SampleWorkflow.vue']}
deliverables = {path.relative_to(trial).as_posix(): digest(path) for path in (trial / 'deliverables').rglob('*') if path.is_file()}
shutil.copytree(trial / 'deck', workspace / 'deck', ignore=shutil.ignore_patterns('node_modules', 'dist', '__pycache__'))
shutil.copytree(trial / 'skills/slidev-echarts', workspace / 'skills/slidev-echarts', ignore=shutil.ignore_patterns('node_modules', '__pycache__'))
commands = []
for command in [['npm.cmd', 'install', '--no-audit', '--no-fund'], ['npm.cmd', 'run', 'build']]:
    process = subprocess.run(command, cwd=workspace / 'deck', capture_output=True, text=True, encoding='utf-8')
    name = 'install' if 'install' in command else 'build'
    (output / f'{name}.log').write_text(process.stdout + process.stderr, encoding='utf-8')
    commands.append({'argv': command, 'returnCode': process.returncode})
    assert process.returncode == 0, output / f'{name}.log'
assert sources == {path: digest(trial / path) for path in sources}
assert sources == {path: digest(workspace / path) for path in sources}
assert deliverables == {path: digest(trial / path) for path in deliverables}
report = {'ok': True, 'run': args.run_id, 'originalSourcesAndDeliverablesUnchanged': True, 'sourceSha256': sources, 'originalDeliverableSha256': deliverables, 'copiedSkillResource': 'Retained read-only trial bundle, not canonical/sibling fixtures', 'commands': commands, 'deck': str(workspace / 'deck'), 'authoredCapturesRetained': any((trial / 'deliverables').rglob('*.png'))}
(output / 'build-proof.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'ok': True, 'deck': str(workspace / 'deck'), 'proof': str(output / 'build-proof.json')}))
