#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Copy only Line World sources into a clean repository-owned publication worktree."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHARED = ['package-spec.json', 'plugin.json', *['scripts/' + s for s in ['package_plugin.py', 'verify_plugin.py', 'verify_openai_package.py', 'sync_local.py', 'prepare_publication.py', 'make_focus_motion_demo.py']]]


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--worktree', type=Path, required=True); args = parser.parse_args()
    target = args.worktree.resolve()
    if target == ROOT or not target.is_relative_to(ROOT) or not (target / '.git').is_file(): raise ValueError('Choose a separate git worktree inside this repository workspace.')
    inventory = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    selected = []
    for name in inventory:
        keep = name.startswith(('skills/line-world-video/', 'skills/line-world-google-vids/', 'evaluations/line-world-video/', 'evaluations/line-world-google-vids/'))
        keep |= name.startswith('evaluations/pi-prompts/line-world-') or name.startswith('evaluations/contracts/verify-line-world-')
        keep |= name in ['docs/line-world-video.md', '.github/workflows/line-world-plugin.yml', *['projects/line-world-video/' + s for s in SHARED]]
        for project in ['cuda-alexnet-vids', 'ml-overfitting-vids', 'seal-paper-vids']:
            prefix = 'projects/' + project + '/'
            if name.startswith(prefix):
                relative = Path(name[len(prefix):])
                keep |= relative.parts[0] in {'scripts', 'templates'} or len(relative.parts) == 1 and relative.suffix in {'.md', '.json', '.css'}
        if not keep or any(p in {'.line-world', '__pycache__', 'artifacts', 'node_modules', '.cache'} for p in Path(name).parts): continue
        source, destination = ROOT / name, target / name
        if not source.is_file(): continue
        destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, destination); selected.append(name)
    source_backlog = (ROOT / 'SKILLS.md').read_text(encoding='utf-8')
    rows = [l for l in source_backlog.splitlines() if l.startswith(('| line-world-video |', '| line-world-google-vids |'))]
    backlog = (target / 'SKILLS.md').read_text(encoding='utf-8')
    lines = [l for l in backlog.splitlines() if not l.startswith(('| line-world-video |', '| line-world-google-vids |'))]
    insert = next(i for i, l in enumerate(lines) if l.startswith('| ---')) + 1
    lines[insert:insert] = rows
    backlog = '\n'.join(lines) + '\n'
    version = json.loads((ROOT / 'projects/line-world-video/package-spec.json').read_text(encoding='utf-8'))['version']
    candidates = [line for line in source_backlog.splitlines() if line.startswith('### ') and line.endswith('plugin ' + version)]
    if len(candidates) != 1: raise ValueError('Record one recent validation heading for the release version.')
    marker = candidates[0]
    note = source_backlog.split(marker, 1)[1].split('\n### ', 1)[0]
    if marker not in backlog: backlog = backlog.replace('## Recent Validation Notes\n', '## Recent Validation Notes\n\n' + marker + note + '\n', 1)
    (target / 'SKILLS.md').write_text(backlog, encoding='utf-8'); selected.append('SKILLS.md')
    index = target / 'docs/README.md'; text = index.read_text(encoding='utf-8')
    link = '- [Line World Video plugin, reusable production and verified delivery](line-world-video.md)\n'
    if '(line-world-video.md)' not in text:
        anchor = '- [Original HyperFrames plugin with colorset1 and colorset2](hyperframes-colorsets.md)\n'
        if anchor not in text: raise ValueError('Review the documentation index insertion point.')
        index.write_text(text.replace(anchor, anchor + link), encoding='utf-8')
    selected.append('docs/README.md')
    coverage_path = 'evaluations/colorset-audit/coverage.json'
    source_coverage = json.loads((ROOT / coverage_path).read_text(encoding='utf-8'))
    coverage = json.loads(subprocess.check_output(['git', 'show', 'HEAD:' + coverage_path], cwd=target, text=True))
    names = {'line-world-video', 'line-world-google-vids'}
    coverage['skills'] = [r for r in coverage['skills'] if r['skill'] not in names] + [r for r in source_coverage['skills'] if r['skill'] in names]
    (target / coverage_path).write_text(json.dumps(coverage, indent=2) + '\n', encoding='utf-8'); selected.append(coverage_path)
    attributes = subprocess.check_output(['git', 'show', 'HEAD:.gitattributes'], cwd=target, text=True)
    if '/skills/line-world-video/** -text' not in attributes:
        attributes += '\n# Preserve evaluated Line World runtime bytes and source-digest receipts.\n/skills/line-world-video/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n/skills/line-world-google-vids/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'
    (target / '.gitattributes').write_text(attributes, encoding='utf-8'); selected.append('.gitattributes')
    report = {'worktree': str(target), 'files': [{'path': name, 'sha256': hashlib.sha256((target / name).read_bytes()).hexdigest()} for name in sorted(set(selected))]}
    output = ROOT / 'projects/line-world-video/artifacts/reviews/publication-inputs.json'; output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    output.with_suffix('.paths').write_bytes(b'\0'.join(r['path'].encode() for r in report['files']) + b'\0')
    print(json.dumps({'ok': True, 'files': len(report['files']), 'manifest': str(output)}))


if __name__ == '__main__': main()
