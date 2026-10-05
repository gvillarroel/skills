#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Reject missing/hidden captions using preserved delivered DOM snapshots."""
import copy
import json
from pathlib import Path

from review_native_deck import attribute_caption_roles, caption_presence_findings

ROOT = Path(__file__).resolve().parents[3]
source = ROOT / 'projects/diagram-compactness/artifacts/reviews/caption-placement-regression-final/natural-2/new/native.json'
delivered = json.loads(source.read_text(encoding='utf-8'))
checks = []
for state in delivered['states']:
    graph = {'labels': copy.deepcopy(state['labels']), 'nodes': [{'quad': body['quad']} for body in state['bodies'] if not body['d'].startswith('M0 0L')], 'shafts': state['shafts']}
    for label in graph['labels']:
        label['opacity'] = 1
    attribute_caption_roles(graph)
    labels = graph['labels']
    assert not caption_presence_findings(labels), state['state']
    for required in ['Retest', 'Failed sample']:
        omitted = [label for label in labels if label['text'] != required]
        assert caption_presence_findings(omitted)
        hidden = copy.deepcopy(labels)
        next(label for label in hidden if label['text'] == required)['opacity'] = 0
        assert caption_presence_findings(hidden)
        tiny = copy.deepcopy(labels)
        next(label for label in tiny if label['text'] == required)['fontSize'] = 13
        assert caption_presence_findings(tiny)
        legend = copy.deepcopy(graph)
        legend['labels'] = [label for label in legend['labels'] if label['text'] != required]
        legend['labels'].append({'text': required, 'fontSize': 14, 'opacity': 1, 'quad': [[20, 20], [120, 20], [120, 34], [20, 34]]})
        attribute_caption_roles(legend)
        assert caption_presence_findings(legend['labels']), (state['state'], required, 'Legend must not substitute for a relationship caption')
        checks.append({'state': state['state'], 'caption': required, 'omissionHiddenTinyAndLegendReplacementRejected': True})
assert len(caption_presence_findings([])) == 2
report = {'ok': True, 'source': source.relative_to(ROOT).as_posix(), 'actualSettledStates': len(delivered['states']), 'checks': checks, 'emptyCaptionsCannotPass': True, 'opaqueDuplicateLegendCannotSubstitute': True, 'geometricRelationshipRoles': {'Retest': 'Review→Analyze', 'Failed sample': 'Analyze→Quarantine'}, 'limitation': 'Conservative emitted geometry association for this known six-node natural prompt; actual full native screenshots still require independent manual inspection.'}
output = ROOT / 'projects/diagram-compactness/artifacts/reviews/native-deck-caption-presence-regression.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'ok': True, 'states': len(delivered['states']), 'checks': len(checks), 'report': str(output)}))
