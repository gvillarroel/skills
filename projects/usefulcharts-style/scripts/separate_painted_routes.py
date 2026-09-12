#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Propose local eight-unit shifts for overlapping authored institutional strokes."""

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import collinear_overlap, compress, segment_hits, viewer


def painted_segments(points):
    lengths = [abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(points, points[1:])]
    answer = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        length = lengths[i]
        if not length:
            continue
        first = min(8, lengths[i - 1] / 2, length / 2) if i else 0
        last = min(8, lengths[i + 1] / 2, length / 2) if i < len(lengths) - 1 else 0
        answer.append((i, tuple(a[k] + (b[k] - a[k]) * first / length for k in (0, 1)),
                       tuple(b[k] + (a[k] - b[k]) * last / length for k in (0, 1))))
    return answer


def conflicts(routes):
    found = []
    prepared = [(edge, painted_segments(edge['points'])) for edge in routes]
    for i, (a, first) in enumerate(prepared):
        for b, second in prepared[i + 1:]:
            if {a['source'], a['target']} & {b['source'], b['target']}:
                continue
            width_a = a.get('weight', 2.8 if a['kind'] in ('branch', 'descent') else 1.8)
            width_b = b.get('weight', 2.8 if b['kind'] in ('branch', 'descent') else 1.8)
            tolerance = (width_a + width_b) / 2 + .03
            for ia, p, q in first:
                for ib, r, s in second:
                    overlap = collinear_overlap(p, q, r, s, tolerance=tolerance)
                    if overlap > 4:
                        found.append(dict(first=a['id'], second=b['id'], a=ia, b=ib, length=overlap))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = json.loads(args.source.read_text(encoding='utf-8-sig'))
    poster = EditorialPoster(source)
    poster.render()
    routes = copy.deepcopy(poster.routes)
    original = conflicts(routes)
    history = []
    for iteration in range(40):
        current = conflicts(routes)
        if not current:
            break
        candidates = []
        choices = set((item[key], item[index]) for item in current for key, index in (('first', 'a'), ('second', 'b')))
        for eid, index in sorted(choices):
            edge = next(e for e in routes if e['id'] == eid)
            points = edge['points']
            if index == 0 or index >= len(points) - 2:
                continue
            axis = 1 if points[index][1] == points[index + 1][1] else 0
            for delta in (-8, 8, -16, 16, -24, 24):
                path = [list(point) for point in points]
                for position in (index, index + 1):
                    path[position][axis] += delta
                path = compress([tuple(point) for point in path])
                if any(segment_hits(a, b, box, 0) for a, b in zip(path, path[1:]) for box in poster.boxes.values()):
                    continue
                if any(segment_hits(a, b, box, 4) for a, b in zip(path, path[1:]) for box in poster.annotation_boxes):
                    continue
                if any(not (48 <= x <= poster.w - 48 and 130 <= y <= poster.h - 70) for x, y in path):
                    continue
                trial = [dict(e, points=path) if e['id'] == eid else e for e in routes]
                remaining = conflicts(trial)
                if len(remaining) >= len(current):
                    continue
                before_length = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(points, points[1:]))
                after_length = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(path, path[1:]))
                candidates.append((len(remaining), abs(delta), after_length - before_length, eid, index, delta, trial))
        if not candidates:
            break
        best = min(candidates, key=lambda item: item[:-1])
        history.append(dict(before=len(current), after=best[0], edge=best[3], segment=best[4], delta=best[5]))
        routes = best[-1]
        print(json.dumps(history[-1]), flush=True)
    remaining = conflicts(routes)
    result = copy.deepcopy(source)
    by_id = {e['id']: e for e in routes}
    for edge in result['edges']:
        edge['via'] = [list(point) for point in by_id[edge['id']]['points'][1:-1]]
    svg, layout = EditorialPoster(result).render()
    for name, value in [('source.json', result), ('layout.json', layout),
                        ('separation.json', dict(before=original, after=remaining, iterations=history,
                                                 status='pass' if not remaining else 'needs-composition'))]:
        (args.output / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    (args.output / 'poster.svg').write_text(svg, encoding='utf-8')
    (args.output / 'poster.html').write_text(viewer(svg, source['title']), encoding='utf-8')
    print(json.dumps(dict(before=len(original), after=len(remaining), iterations=len(history))))


if __name__ == '__main__':
    main()
