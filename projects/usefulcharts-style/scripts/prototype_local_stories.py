#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare local vertical compaction against preserved packed forward outputs."""

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/usefulcharts-style/scripts'))
import editorial_poster
from render_chart import viewer
from story_layout import pack_stories, solve_axis
from cohort_layout import place_cohorts


def local_pack(data, measure, top=190, cycles=0):
    initial = pack_stories(data, measure, top)
    nodes = copy.deepcopy(data['nodes'])
    widths = {n['id']: n['width'] for n in nodes}
    heights = {n['id']: measure(n, n['width'])[2] for n in nodes}
    xs = {n['id']: n['x'] - 65 for n in initial['nodes']}
    width = initial['width']
    structural = [e for e in data.get('edges', []) if e['kind'] != 'influence']
    ordered = sorted(nodes, key=lambda n: (n['y'], n['id']))
    by_id = {n['id']: n for n in nodes}
    for iteration in range(cycles + 1):
        incoming = {n['id']: {} for n in nodes}
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                first, second = a['id'], b['id']
                if abs(xs[first] - xs[second]) < (widths[first] + widths[second]) / 2 + 28 - .01:
                    incoming[second][first] = (heights[first] + heights[second]) / 2 + 34
        for edge in structural:
            a, b = edge['source'], edge['target']
            incoming[b][a] = max(incoming[b].get(a, 0), (heights[a] + heights[b]) / 2 + 42)
        ys = {}
        for node in ordered:
            nid = node['id']
            ys[nid] = max([heights[nid] / 2] + [ys[p] + gap for p, gap in incoming[nid].items()])
        if iteration == cycles:
            break
        constraints = []
        xorder = sorted(nodes, key=lambda n: (n['x'], n['id']))
        constraints.extend((a['id'], b['id'], 0) for a, b in zip(xorder, xorder[1:]))
        for i, a in enumerate(xorder):
            for b in xorder[i + 1:]:
                first, second = a['id'], b['id']
                if abs(ys[first] - ys[second]) < (heights[first] + heights[second]) / 2 + 34 - .01:
                    constraints.append((first, second, (widths[first] + widths[second]) / 2 + 28))
        xs, extent = solve_axis(nodes, widths, constraints, 'x')
        width = data.get('width', max(1000, extent + 130))
        xs, _ = solve_axis(nodes, widths, constraints, 'x', width - 130)
    height = data.get('height', max(720, max(ys[n['id']] + heights[n['id']] / 2 for n in nodes) + top + 100))
    result = copy.deepcopy(data)
    for node in result['nodes']:
        nid = node['id']
        node.update(x=65 + xs[nid], y=top + ys[nid])
    result.update(width=width, height=height, layout='packed')
    return result


def layered_pack(data, measure, top=190):
    result = copy.deepcopy(data)
    by_id = {n['id']: n for n in result['nodes']}
    parents = {nid: [] for nid in by_id}
    for edge in result['edges']:
        if edge['kind'] != 'influence':
            parents[edge['target']].append(edge['source'])
    pending = set(by_id)
    ranks = {}
    while pending:
        ready = sorted(nid for nid in pending if all(p in ranks for p in parents[nid]))
        if not ready:
            raise ValueError('Structural cycle.')
        for nid in ready:
            ranks[nid] = max((ranks[p] + 1 for p in parents[nid]), default=0)
            by_id[nid]['row'] = ranks[nid]
            pending.remove(nid)
    rows = {}
    for node in result['nodes']:
        rows.setdefault(node['row'], []).append(node)
    widths = [sum(n['width'] for n in row) + 28 * (len(row) - 1) for row in rows.values()]
    result['width'] = data.get('width', max(1000, max(widths) + 130))
    heights = {r: max(measure(n, n['width'])[2] for n in row) for r, row in rows.items()}
    levels = sorted(rows)
    gaps = [(heights[a] + heights[b]) / 2 + 36 for a, b in zip(levels, levels[1:])]
    first_y = top + heights[levels[0]] / 2
    last_y = first_y + sum(gaps)
    result['height'] = data.get('height', max(720, last_y + heights[levels[-1]] / 2 + 100))
    result['cohort_weights'] = {str(row): gap for row, gap in zip(levels[1:], gaps)}
    result['cohort_gap'] = 28
    result['nodes'] = place_cohorts(result, measure, 65, result['width'] - 65, first_y, last_y)
    result['layout'] = 'packed'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cycles', type=int, default=0)
    parser.add_argument('--method', choices=['local', 'layered'], default='local')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    data = json.loads(args.source.read_text(encoding='utf-8-sig'))
    (args.output / 'source.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    editorial_poster.pack_stories = layered_pack if args.method == 'layered' else lambda data, measure, top=190: local_pack(data, measure, top, args.cycles)
    poster = editorial_poster.EditorialPoster(data)
    svg, report = poster.render()
    (args.output / 'poster.svg').write_text(svg, encoding='utf-8')
    (args.output / 'poster.html').write_text(viewer(svg, data['title']), encoding='utf-8')
    (args.output / 'layout.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (args.output / 'driver.py').write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    print(json.dumps(dict(canvas=[poster.w, poster.h], nodes=len(poster.nodes), edges=len(poster.routes), cycles=args.cycles)))


if __name__ == '__main__':
    main()
