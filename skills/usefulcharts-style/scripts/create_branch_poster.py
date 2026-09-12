#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compose, export and audit one consistent branch-poster deliverable bundle."""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

from compose_branching_history import compose_history
from editorial_poster import EditorialPoster
from render_chart import require, viewer
from verify_branch_source import verify_fields

FILES = ('source.json', 'poster.svg', 'poster.html', 'layout.json', 'browser.json', 'poster.png')


def create_bundle(original, directory):
    draft = copy.deepcopy(original)
    draft.setdefault('design', 'editorial')
    draft.setdefault('mode', 'lineage')
    draft.setdefault('layout', 'branches')
    resolved, composition = compose_history(draft)
    fidelity = verify_fields(original, resolved)
    require(fidelity['status'] == 'pass', 'The composition changed a supplied field: ' + json.dumps(fidelity['findings']))
    svg, layout = EditorialPoster(resolved).render()
    layout.update(composition=composition, original_source_check=fidelity)
    directory.mkdir(parents=True, exist_ok=True)
    contents = {
        'source.json': json.dumps(resolved, indent=2)+'\n',
        'poster.svg': svg,
        'poster.html': viewer(svg, resolved['title']),
        'layout.json': json.dumps(layout, indent=2)+'\n',
    }
    for name, content in contents.items():
        (directory/name).write_text(content, encoding='utf-8')
    # Audit the actual final paths after serializing the composed source.
    # The original data-first draft is never substituted into the bundle.
    command = [sys.executable, str(Path(__file__).with_name('audit_chart.py')),
               str(directory/'poster.svg'), '--source', str(directory/'source.json'),
               '--report', str(directory/'browser.json'), '--png', str(directory/'poster.png')]
    audited = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    require(audited.returncode == 0, 'The exported poster failed its browser audit: ' + audited.stdout + audited.stderr)
    browser = json.loads((directory/'browser.json').read_text(encoding='utf-8'))
    return dict(status='pass', files=list(FILES), nodes=len(resolved['nodes']), edges=len(resolved['edges']),
                canvas=browser['canvas'], original_fields_preserved=True,
                composition_warnings=browser.get('composition_warnings', []),
                visual_review='Open poster.png and inspect the composition before writing the requested review.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        require(args.input.resolve() not in {(args.output_dir/name).resolve() for name in FILES},
                'Keep the original draft outside the generated bundle; input and output paths must be distinct.')
        original = json.loads(args.input.read_text(encoding='utf-8-sig'))
        result = create_bundle(original, args.output_dir)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Branch poster could not be completed: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
