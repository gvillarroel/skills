#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the one-comparison correction against independent saved fixtures."""
from pathlib import Path
import json
import runpy
import shutil
import sys


def main():
    root = Path(__file__).resolve().parents[6]
    revision = Path(__file__).resolve().parent
    original_raw = (revision.parents[1] / 'validate_svg_cases.py').read_bytes()
    corrected_raw = (revision / 'validate_svg_cases.py').read_bytes()
    old = b'numeric(observed, target) if field == "font_size" else observed == target'
    new = b'numeric(observed, target) if field == "font_size" else color(observed, target) if field == "text_color" else observed == target'
    assert original_raw.count(old) == 1 and corrected_raw.replace(new, old) == original_raw
    grader = runpy.run_path(str(revision / 'validate_svg_cases.py'))
    design = root / 'evaluations/runs/benchmark-design-svg'
    output = root / 'evaluations/runs/benchmark-verifier-r1'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for case in ('geometry', 'relations', 'asset'):
        grader['validate'](case, design / ('expected-' + case))
        records.append(dict(test='original-positive-' + case, passed=True))
    previous = json.loads((design / 'smoke-results.json').read_text(encoding='utf-8'))
    for record in previous['mutation_results']:
        name = record['mutation']
        workspace = design / ('mutation-' + name)
        case = 'geometry' if (workspace / 'inputs/dispatch.svg').exists() else 'relations' if (workspace / 'source/release-route.svg').exists() else 'asset'
        rejected = False
        try:
            grader['validate'](case, workspace)
        except (ValueError, KeyError, TypeError):
            rejected = True
        expected_rejection = record.get('expected_rejection', False)
        assert rejected == expected_rejection, name
        records.append(dict(test=name, passed=True, expected_rejection=expected_rejection))
    for case in ('geometry', 'relations'):
        spec = grader['CASES'][case]
        for variant in ('uppercase', 'lowercase', 'mixedcase', 'wrong-rgb'):
            workspace = output / (case + '-' + variant)
            assert not workspace.exists(), workspace
            shutil.copytree(design / ('expected-' + case), workspace)
            graph_path = workspace / spec['base'] / 'graph.json'
            graph = json.loads(graph_path.read_text(encoding='utf-8'))
            for node in graph['nodes']:
                value = node['text_color']
                node['text_color'] = value.upper() if variant == 'uppercase' else value.lower() if variant == 'lowercase' else ''.join(char.upper() if index % 2 else char.lower() for index, char in enumerate(value)) if variant == 'mixedcase' else '#010203'
            graph_path.write_text(json.dumps(graph, indent=2) + '\n', encoding='utf-8', newline='\n')
            rejected = False
            try:
                grader['validate'](case, workspace)
            except ValueError:
                rejected = True
            assert rejected == (variant == 'wrong-rgb'), (case, variant)
            records.append(dict(test=case + '-' + variant, passed=True, expected_rejection=variant == 'wrong-rgb'))
    result = dict(passed=True, exact_single_comparison_change=True, tests=len(records), accepted=sum(not item.get('expected_rejection', False) for item in records), rejected=sum(item.get('expected_rejection', False) for item in records), results=records)
    (output / 'test-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'results'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
