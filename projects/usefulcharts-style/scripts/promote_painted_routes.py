#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Promote only the reviewed local corridor shifts, preserving all mural content."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    examples = ROOT / 'skills/usefulcharts-style/assets/examples/usefulcharts-style'
    review = ROOT / 'projects/usefulcharts-style/artifacts/reviews/local-stories-v31'
    candidate = json.loads((review / 'published-separated/source.json').read_text(encoding='utf-8'))
    before = json.loads((examples / 'atlas-of-inquiry.json').read_text(encoding='utf-8'))
    assert candidate['nodes'] == before['nodes']
    assert {key: value for key, value in candidate.items() if key != 'edges'} == {key: value for key, value in before.items() if key != 'edges'}
    for original, proposed in zip(before['edges'], candidate['edges']):
        assert {k: v for k, v in original.items() if k != 'via'} == {k: v for k, v in proposed.items() if k != 'via'}
    audit = json.loads((review / 'published-separated/browser.json').read_text(encoding='utf-8'))
    assert audit['status'] == 'pass' and not audit['findings'] and not audit['composition_warnings']
    baseline = review / 'baseline-institution'
    baseline.mkdir(exist_ok=False)
    for extension in ('json', 'svg', 'html'):
        shutil.copyfile(examples / ('atlas-of-inquiry.' + extension), baseline / ('poster.' + extension))
    path = examples / 'lineage-corridors.json'
    corridors = json.loads(path.read_text(encoding='utf-8'))
    history = json.loads((review / 'published-separated/separation.json').read_text(encoding='utf-8'))
    changed = {item['edge'] for item in history['iterations']}
    for edge in candidate['edges']:
        if edge['id'] in changed:
            corridors[edge['id']]['via'] = edge['via']
    path.write_text(json.dumps(corridors, indent=2) + '\n', encoding='utf-8')
    (review / 'promoted-corridors.json').write_text(json.dumps(dict(edges=sorted(changed), shifts=len(history['iterations']),
                                                                   preserved_nodes=141, preserved_edges=171), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(changed_edges=len(changed), local_shifts=len(history['iterations']), nodes_unchanged=True)))


if __name__ == '__main__':
    main()
