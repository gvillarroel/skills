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
SHARED = ['package-spec.json', 'plugin.json', *['scripts/' + s for s in ['package_plugin.py', 'verify_plugin.py', 'verify_openai_package.py', 'sync_local.py', 'prepare_publication.py', 'make_focus_motion_demo.py', 'make_photo_focus_demo.py', 'register_local.py']]]


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--worktree', type=Path, required=True); args = parser.parse_args()
    target = args.worktree.resolve()
    if target == ROOT or not target.is_relative_to(ROOT) or not (target / '.git').is_file(): raise ValueError('Choose a separate git worktree inside this repository workspace.')
    inventory = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    selected = []
    for name in inventory:
        keep = name.startswith(('skills/line-world-video/', 'skills/line-world-google-vids/', 'evaluations/line-world-video/', 'evaluations/line-world-google-vids/'))
        keep |= name.startswith('evaluations/pi-prompts/line-world-') or name.startswith('evaluations/contracts/verify-line-world-')
        keep |= name in ['docs/line-world-video.md', 'docs/plugins-marketplace.md', '.github/workflows/line-world-plugin.yml', '.github/workflows/skills-marketplace.yml', *['projects/line-world-video/' + s for s in SHARED]]
        keep |= name.startswith('projects/skills-marketplace/')
        keep |= name.startswith('evaluations/plugin-marketplace/')
        for project in ['cuda-alexnet-vids', 'ml-overfitting-vids', 'seal-paper-vids', 'reddit-navigation-video', 'line-world-quality-review']:
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
    backlog = subprocess.check_output(['git', 'show', 'HEAD:SKILLS.md'], cwd=target, text=True, encoding='utf-8')
    lines = [l for l in backlog.splitlines() if not l.startswith(('| line-world-video |', '| line-world-google-vids |'))]
    insert = next(i for i, l in enumerate(lines) if l.startswith('| ---')) + 1
    lines[insert:insert] = rows
    backlog = '\n'.join(lines) + '\n'
    version = json.loads((ROOT / 'projects/line-world-video/package-spec.json').read_text(encoding='utf-8'))['version']
    candidates = [line for line in source_backlog.splitlines() if line.startswith('### ') and line.endswith('plugin ' + version)]
    if len(candidates) != 1: raise ValueError('Record one recent validation heading for the release version.')
    marker = candidates[0]
    note = source_backlog.split(marker, 1)[1].split('\n### ', 1)[0]
    if marker in backlog:
        start = backlog.index(marker); end = backlog.find('\n### ', start + len(marker))
        backlog = backlog[:start] + marker + note.rstrip() + '\n' + (backlog[end:] if end >= 0 else '')
    else: backlog = backlog.replace('## Recent Validation Notes\n', '## Recent Validation Notes\n\n' + marker + note + '\n', 1)
    (target / 'SKILLS.md').write_text(backlog, encoding='utf-8'); selected.append('SKILLS.md')
    index = target / 'docs/README.md'; text = index.read_text(encoding='utf-8')
    link = '- [Line World Video plugin, reusable production and verified delivery](line-world-video.md)\n'
    if '(line-world-video.md)' not in text:
        anchor = '- [Original HyperFrames plugin with colorset1 and colorset2](hyperframes-colorsets.md)\n'
        if anchor not in text: raise ValueError('Review the documentation index insertion point.')
        index.write_text(text.replace(anchor, anchor + link), encoding='utf-8')
    selected.append('docs/README.md')
    marketplace_link = '- [Skills Marketplace: install plugins and publish new ones](plugins-marketplace.md)\n'
    index_text = index.read_text(encoding='utf-8')
    if '(plugins-marketplace.md)' not in index_text:
        index.write_text(index_text.replace('- [Usage and setup](getting-started.md)\n', '- [Usage and setup](getting-started.md)\n' + marketplace_link), encoding='utf-8')
    overview = subprocess.check_output(['git', 'show', 'HEAD:README.md'], cwd=target, text=True, encoding='utf-8')
    source_overview = (ROOT / 'README.md').read_text(encoding='utf-8')
    install = source_overview.split('Install complete plugins from **Skills Marketplace**:', 1)[1].split('\n## ', 1)[0]
    if '(docs/plugins-marketplace.md)' not in overview:
        anchor = 'A skill must work as an independent bundle. Repository documentation and example galleries support maintenance but must not become hidden runtime dependencies.\n'
        if anchor not in overview: raise ValueError('Review the README marketplace insertion point.')
        (target / 'README.md').write_text(overview.replace(anchor, anchor + '\nInstall complete plugins from **Skills Marketplace**:' + install + '\n'), encoding='utf-8')
    else:
        start = overview.index('Install complete plugins from **Skills Marketplace**:')
        end = overview.find('\n## ', start)
        if end < 0: raise ValueError('Review the README marketplace block boundary.')
        (target / 'README.md').write_text(overview[:start] + 'Install complete plugins from **Skills Marketplace**:' + install.rstrip() + '\n' + overview[end:], encoding='utf-8')
    selected.append('README.md')
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
