#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Grade independently captured, rendered treemap task contracts."""

import argparse
import hashlib
import json
from pathlib import Path
import re


DATA = {
    'naturalistic': {
        'Delivery': {'Parcel': 41, 'Routing': 23, 'Intake': 13},
        'Experience': {'Support': 31, 'Learning': 19, 'Discovery': 11},
        'Platform': {'Runtime': 29, 'Storage': 17, 'Network': 9},
    },
    'contract': {
        'Research': {'Models': 38, 'Findings': 21, 'Studies': 12},
        'Services': {'Search': 34, 'Delivery': 20, 'Identity': 10},
        'Operations': {'Compute': 30, 'Storage': 18, 'Recovery': 8},
    },
}


def rgb(paint):
    if re.fullmatch(r'#[0-9a-fA-F]{6}', paint):
        return tuple(int(paint[i:i+2], 16) for i in (1, 3, 5))
    match = re.fullmatch(r'rgba?\(([^)]+)\)', paint)
    if not match:
        raise ValueError(f'Unsupported solid paint: {paint}')
    values = [float(part.strip()) for part in match.group(1).split(',')]
    if len(values) == 4 and values[3] != 1:
        raise ValueError(f'Nonopaque paint: {paint}')
    return tuple(values[:3])


def luminance(paint):
    channels = [channel / 255 for channel in rgb(paint)]
    linear = [channel / 12.92 if channel <= .04045 else ((channel + .055) / 1.055) ** 2.4 for channel in channels]
    return sum(weight * channel for weight, channel in zip((.2126, .7152, .0722), linear))


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + .05) / (low + .05)


def contains(outer, inner, tolerance=1.0):
    return (inner['x'] >= outer['x'] - tolerance and inner['y'] >= outer['y'] - tolerance
            and inner['x'] + inner['width'] <= outer['x'] + outer['width'] + tolerance
            and inner['y'] + inner['height'] <= outer['y'] + outer['height'] + tolerance)


def area(item):
    return item['box']['width'] * item['box']['height']


def matching_text(items, token):
    return [item for item in items if item['tag'] == 'text'
            and re.search(rf'\b{re.escape(str(token))}\b', item['text'])
            and area(item) > 0 and item['effectiveOpacity'] > .999]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    parser.add_argument('--case', choices=DATA, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    review = json.loads(args.review.read_text(encoding='utf-8'))
    data = DATA[args.case]
    states = []
    findings = []
    for state in review['states']:
        suffix = f"-normal-{state.get('replay',0)}" if not state.get('reducedMotion',True) else ''
        state_id = f"{state['format']}-{state['width']}{suffix}"
        checked = {'state': state_id, 'branches': {}, 'findings': []}
        local = checked['findings']
        if state['pageErrors'] or state['networkRequests']:
            local.append('Browser errors or external network requests occurred.')
        if not state.get('title') or not state.get('description'):
            local.append('Accessible SVG title or description is missing.')
        if state['format'] == 'html' and state['documentWidth'] > state['viewportWidth'] + 2:
            local.append('The document overflows the viewport horizontally.')
        items = state['items']
        rects = [item for item in items if item['tag'] == 'rect' and area(item) > 0]
        for branch, values in data.items():
            parent_labels = matching_text(items, branch)
            if not parent_labels:
                local.append(f'{branch}: visible parent label is missing.')
            else:
                parent_label = parent_labels[0]
                headers = [rect for rect in rects if contains(rect['box'], parent_label['box'])]
                if not headers:
                    local.append(f'{branch}: parent label is outside its header.')
                else:
                    header = min(headers, key=area)
                    try:
                        black = contrast('#000000', header['fill'])
                        white = contrast('#ffffff', header['fill'])
                        expected = (0,0,0) if black > white else (255,255,255)
                        if rgb(parent_label['fill']) != expected:
                            local.append(f'{branch}: parent label is not maximum-contrast black or white.')
                    except ValueError as error:
                        local.append(f'{branch}: {error}')
            leaves = []
            for name, value in values.items():
                labels = matching_text(items, name)
                if not labels:
                    local.append(f'{name}: visible leaf label is missing.')
                    continue
                label = labels[0]
                candidates = [rect for rect in rects if contains(rect['box'], label['box'])]
                if not candidates:
                    local.append(f'{name}: label is not inside a visible rectangle.')
                    continue
                cell = min(candidates, key=area)
                if not contains(state['svgBox'], cell['box']) or not contains(state['svgBox'], label['box']):
                    local.append(f'{name}: geometry or label extends beyond the SVG.')
                if cell['stroke'] != 'none' and float(cell['strokeWidth'].removesuffix('px')) > 0:
                    local.append(f'{name}: cell has a decorative border.')
                if cell['effectiveOpacity'] < .999 or float(cell['fillOpacity']) < .999:
                    local.append(f'{name}: cell is translucent.')
                value_labels = [text for text in matching_text(items, value) if contains(cell['box'], text['box'])]
                if not value_labels:
                    local.append(f'{name}: exact numeric value {value} is not visible in its cell.')
                try:
                    black, white = contrast('#000000', cell['fill']), contrast('#ffffff', cell['fill'])
                    expected = (0, 0, 0) if black > white else (255, 255, 255)
                    for text in [label, *value_labels]:
                        if rgb(text['fill']) != expected:
                            local.append(f'{name}: label is not maximum-contrast black or white.')
                    leaves.append({'name':name, 'value':value, 'fill':cell['fill'],
                                   'luminance':luminance(cell['fill']), 'textContrast':max(black,white),
                                   'area':area(cell), 'box':cell['box']})
                except ValueError as error:
                    local.append(f'{name}: {error}')
            if len(leaves) == len(values):
                if len({leaf['fill'] for leaf in leaves}) != len(values):
                    local.append(f'{branch}: sibling fills are not all distinct.')
                ordered = sorted(leaves, key=lambda leaf:leaf['luminance'])
                minimum_step = min(contrast(a['fill'], b['fill']) for a, b in zip(ordered, ordered[1:]))
                if minimum_step < 1.15:
                    local.append(f'{branch}: neighboring tonal steps are visually too close ({minimum_step:.3f}:1).')
                branch_area = sum(leaf['area'] for leaf in leaves)
                branch_value = sum(values.values())
                largest_error = max(abs(leaf['area']/branch_area - leaf['value']/branch_value) for leaf in leaves)
                if largest_error > .06:
                    local.append(f'{branch}: leaf area proportions diverge materially from values ({largest_error:.4f}).')
                checked['branches'][branch] = {'leaves':leaves, 'minimumTonalStep':minimum_step,
                                              'largestAreaFractionError':largest_error}
        if len(checked['branches']) == len(data):
            total_area = sum(leaf['area'] for branch in checked['branches'].values() for leaf in branch['leaves'])
            total_value = sum(value for branch in data.values() for value in branch.values())
            branch_errors = {name:abs(sum(leaf['area'] for leaf in branch['leaves'])/total_area
                                     - sum(data[name].values())/total_value)
                             for name,branch in checked['branches'].items()}
            checked['branchAreaFractionErrors'] = branch_errors
            if max(branch_errors.values()) > .06:
                local.append('Parent branch allocation diverges materially from its aggregate values.')
        findings.extend(f'{state_id}: {message}' for message in local)
        states.append(checked)
    for width in (960, 420):
        pair = [state for state in states if state['state'].endswith(f'-{width}')]
        if len(pair) == 2:
            for branch in data:
                left = pair[0]['branches'].get(branch, {}).get('leaves', [])
                right = pair[1]['branches'].get(branch, {}).get('leaves', [])
                if [(leaf['name'],leaf['fill']) for leaf in left] != [(leaf['name'],leaf['fill']) for leaf in right]:
                    findings.append(f'{width}: {branch} HTML/SVG name and paint parity failed.')
    for branch in data:
        sequences = [[(leaf['name'],leaf['fill']) for leaf in state['branches'].get(branch,{}).get('leaves',[])] for state in states]
        if sequences and any(sequence != sequences[0] for sequence in sequences[1:]):
            findings.append(f'{branch}: colors or names changed across native, Replay, responsive or export states.')
    result = {'schemaVersion':1, 'case':args.case, 'passed':not findings,
              'captureSha256':hashlib.sha256(args.review.read_bytes()).hexdigest(),
              'renderedStates':len(states), 'states':states, 'findings':findings,
              'acceptanceNotes':['The 1.15 sibling tonal-step threshold is a local distinguishability check, not a WCAG requirement.',
                                 'Portable SVG retains its intrinsic export width; responsive viewport overflow is checked on the HTML.',
                                 'Direct screenshot inspection remains necessary to confirm compact readability and grouping.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed':result['passed'], 'renderedStates':len(states), 'findings':findings}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
