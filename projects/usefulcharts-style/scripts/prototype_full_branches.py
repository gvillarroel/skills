#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Probe a complete mural with causal and founded stage composition.

Retain every record, label, caption, treatment, type size and typed relationship.
Only positions, routes and the separately retained contextual opening are editable.
These are development probes, not aesthetic acceptance scores.
"""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/usefulcharts-style'
ART = ROOT / 'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--order', choices=('founded', 'causal'), required=True)
    parser.add_argument('--label', help='Use a fresh artifact directory for each changed candidate.')
    parser.add_argument('--placement-only', action='store_true', help='Inspect complete label placement before expensive routing; never a release artifact.')
    args = parser.parse_args()
    original = json.loads((SKILL / 'assets/examples/usefulcharts-style/atlas-of-inquiry.json').read_text(encoding='utf-8'))
    out = ART / (args.label or args.order)
    out.mkdir(parents=True, exist_ok=False)
    draft = copy.deepcopy(original)
    retained = {key: draft.pop(key, None) for key in ('insets', 'width', 'height')}
    draft.update(layout='branches', branch_order=args.order)
    for node in draft['nodes']:
        for key in ('x', 'y', 'row', 'col'):
            node.pop(key, None)
    for edge in draft['edges']:
        for key in ('via', 'corridor_y', 'source_port', 'target_port'):
            edge.pop(key, None)
    (out / 'original.json').write_text(json.dumps(original, indent=2) + '\n', encoding='utf-8')
    (out / 'retained-context.json').write_text(json.dumps(retained, indent=2) + '\n', encoding='utf-8')
    (out / 'draft.json').write_text(json.dumps(draft, indent=2) + '\n', encoding='utf-8')
    if args.placement_only:
        sys.path.insert(0, str(SKILL/'scripts'))
        from editorial_poster import EditorialPoster
        placed = EditorialPoster(draft).data
        placed.update(layout='authored', edges=[], source_note='Placement diagnostic only. All relationship paths and contextual insets are omitted from this diagnostic, not from the intended poster.')
        (out/'source.json').write_text(json.dumps(placed, indent=2)+'\n', encoding='utf-8')
    commands = [
        [sys.executable, str(SKILL/'scripts/compose_branching_history.py'), str(out/'draft.json'), '--output', str(out/'source.json'), '--report', str(out/'composition.json')],
        [sys.executable, str(SKILL/'scripts/render_chart.py'), str(out/'source.json'), '--svg', str(out/'poster.svg'), '--html', str(out/'poster.html'), '--report', str(out/'layout.json')],
        ['uv', 'run', '--script', str(SKILL/'scripts/audit_chart.py'), str(out/'poster.svg'), '--source', str(out/'source.json'), '--report', str(out/'browser.json'), '--png', str(out/'poster.png')],
    ]
    if args.placement_only:
        commands = commands[1:]
    results = []
    for index, command in enumerate(commands):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        (out / f'step-{index}.log').write_text(result.stdout + result.stderr, encoding='utf-8')
        results.append({'step': index, 'exit_code': result.returncode})
        print(json.dumps(results[-1]), flush=True)
        if result.returncode:
            break
    (out/'execution.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
    raise SystemExit(results[-1]['exit_code'])


if __name__ == '__main__':
    main()
