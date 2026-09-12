#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compose institutional branches from a DAG without permanent leaf columns."""

import copy
import math
from collections import defaultdict

from cohort_layout import place_cohorts
from render_chart import number, require


def arrange_branches(data, measure, top=190):
    """Measure the widest active stage, then compact overlapping local stories."""
    result = copy.deepcopy(data)
    nodes = result['nodes']
    by_id = {n['id']: n for n in nodes}
    require(nodes and len(by_id) == len(nodes), 'Branching stories require distinct named records.')
    require(result.get('mode') == 'lineage' and not result.get('unions'),
            'Branching stories support institutional lineages; use cohorts for partnerships.')
    require(not result.get('insets'), 'Place insets in an authored copy of the resolved branch layout.')
    require(all(a.get('node') for a in result.get('annotations', [])),
            'Branch annotations must be anchored to a node; fixed captions need authored placement.')
    require(not any(any(key in n for key in ('x', 'y', 'row', 'col', 'row_offset')) for n in nodes),
            'Branching stories infer positions. Use packed for relative hints or authored for prescribed coordinates.')
    parents = {nid: [] for nid in by_id}
    for edge in result.get('edges', []):
        a, b = edge['source'], edge['target']
        require(a in by_id and b in by_id, f'Unresolved branching relationship {edge["id"]}.')
        require(not edge.get('via') and 'corridor_y' not in edge,
                'Omit absolute routes while arranging branches; compose them after inspecting the resolved layout.')
        if edge['kind'] != 'influence':
            parents[b].append(a)
    pending = set(by_id)
    ranks = {}
    dated = all(type(n.get('founded')) in (int, float) and math.isfinite(n['founded']) for n in nodes)
    order_mode = result.get('branch_order', 'founded' if dated else 'causal')
    require(order_mode in ('causal', 'founded'), 'Branch order must be causal or founded.')
    require(order_mode != 'founded' or dated, 'Founded branch order requires a finite numeric founded year on every record.')
    bands = {nid: 0 for nid in by_id}
    if order_mode == 'founded':
        chronological = sorted(nodes, key=lambda n: (n['founded'], n['id']))
        for index, node in enumerate(chronological):
            bands[node['id']] = index // 6
    while pending:
        ready = sorted(nid for nid in pending if all(p in ranks for p in parents[nid]))
        require(ready, 'Structural relations contain a cycle. Correct the source graph.')
        for nid in ready:
            ranks[nid] = max([bands[nid]] + [ranks[p] + 1 for p in parents[nid]])
            by_id[nid]['row'] = ranks[nid]
            pending.remove(nid)
    widths = {n['id']: number(n['width'], f'{n["id"]}.width') for n in nodes}
    heights = {n['id']: measure(n, widths[n['id']])[2] for n in nodes}
    rows = defaultdict(list)
    for node in nodes:
        rows[node['row']].append(node)
    minimum_width = max(sum(widths[n['id']] for n in row) + 28 * (len(row) - 1) for row in rows.values())
    width = number(data.get('width', max(1000, minimum_width + 130)), 'width')
    require(width >= minimum_width + 130 - .01,
            f'The widest branching stage needs at least {minimum_width + 130:.1f} units; omit the fixed width or enlarge it.')
    # The unit packer measures adjacent records and relaxes their centers toward
    # actual relatives. It has no partnership units here and invents no edges.
    result['cohort_gap'] = 28
    result.pop('cohort_weights', None)
    result.pop('cohort_spread', None)
    placed = place_cohorts(result, measure, 65, width - 65, 0, 1)
    xs = {n['id']: n['x'] for n in placed}
    ordered = sorted(nodes, key=lambda n: (ranks[n['id']], xs[n['id']], n['id']))
    incoming = {nid: {} for nid in by_id}
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            first, second = a['id'], b['id']
            if abs(xs[first] - xs[second]) < (widths[first] + widths[second]) / 2 + 28 - .01:
                incoming[second][first] = (heights[first] + heights[second]) / 2 + 28
    for nid, predecessors in parents.items():
        for predecessor in predecessors:
            incoming[nid][predecessor] = max(incoming[nid].get(predecessor, 0),
                                           (heights[nid] + heights[predecessor]) / 2 + 32)
    ys = {}
    for node in ordered:
        nid = node['id']
        ys[nid] = max([heights[nid] / 2] + [ys[p] + gap for p, gap in incoming[nid].items()])
    extent = max(ys[nid] + heights[nid] / 2 for nid in by_id)
    if order_mode == 'founded':
        outgoing = {nid: {} for nid in by_id}
        for target, predecessors in incoming.items():
            for source, gap in predecessors.items():
                outgoing[source][target] = gap
        upper = {}
        for node in reversed(ordered):
            nid = node['id']
            upper[nid] = min([extent - heights[nid] / 2] + [upper[t] - gap for t, gap in outgoing[nid].items()])
        ordinal = {n['id']: i / max(1, len(nodes) - 1) for i, n in enumerate(chronological)}
        for node in ordered:
            nid = node['id']
            lower = max([ys[nid]] + [ys[p] + gap for p, gap in incoming[nid].items()])
            preferred = heights[nid] / 2 + (extent - heights[nid]) * ordinal[nid]
            ys[nid] = max(lower, min(upper[nid], preferred))
    minimum_height = extent + top + 100
    height = number(data.get('height', max(720, minimum_height)), 'height')
    require(height >= minimum_height - .01,
            f'The branching stories need at least {minimum_height:.1f} units; omit the fixed height or enlarge it.')
    for node in nodes:
        nid = node['id']
        node.update(x=xs[nid], y=top + ys[nid])
        node.pop('row', None)
    result.pop('cohort_gap', None)
    result.update(width=width, height=height, layout='branches', branch_order=order_mode)
    return result


if __name__ == '__main__':
    print('Use render_chart.py with design: editorial, mode: lineage and layout: branches.')
