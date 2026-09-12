#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reserve complete anchored headings while composing institutional branches."""

from editorial_landmarks import landmark_content
from render_chart import number, overlaps, require, wrap


def caption_size(annotation, node):
    kind = annotation.get('kind')
    require(kind in ('pill', 'heading', 'landmark'),
            'Branch composition reserves anchored pills, headings and source-bound landmarks.')
    if kind == 'landmark':
        content = landmark_content(annotation, node)
        return content['width'], content['height'], 0
    width = number(annotation.get('width', 130), 'annotation.width')
    size = number(annotation.get('size', 13), 'annotation.size')
    require(width >= 40 and size >= 8, 'Use readable branch captions at least forty units wide.')
    height = len(wrap(annotation['label'], width - 10, size, True)) * size * 1.12 + 7
    above = 57 if kind == 'heading' and annotation.get('icon') else 0
    return max(width, 44 if above else 0), height, above


def caption_box(annotation, node, anchor):
    width, height, above = caption_size(annotation, node)
    x = anchor[0] + anchor[2] / 2 + number(annotation.get('dx', 0), 'annotation.dx')
    y = anchor[1] + anchor[3] / 2 + number(annotation.get('dy', 0), 'annotation.dy')
    return x - width / 2, y - height / 2 - above, width, height + above


def branch_envelopes(data, measure):
    """Return asymmetric local bounds without replacing the actual name width."""
    nodes = {node['id']: node for node in data['nodes']}
    bounds = {}
    parts = {}
    for nid, node in nodes.items():
        width = number(node['width'], f'{nid}.width')
        height = measure(node, width)[2]
        parts[nid] = [(-width / 2, -height / 2, width, height)]
    for annotation in data.get('annotations', []):
        nid = annotation.get('node')
        require(nid in nodes, 'Branch annotation references an unknown institution.')
        _, height, _ = caption_size(annotation, nodes[nid])
        # A missing offset requests a local heading. Explicit offsets retain
        # their source geometry and must clear the named institution.
        annotation.setdefault('dy', -(parts[nid][0][3] / 2 + height / 2 + 24))
        box = caption_box(annotation, nodes[nid], parts[nid][0])
        require(not any(overlaps(box, other, 5) for other in parts[nid]),
                f'Anchored branch captions overlap their own content at {nid}; adjust dx/dy.')
        parts[nid].append(box)
    for nid, boxes in parts.items():
        left = min(box[0] for box in boxes)
        top = min(box[1] for box in boxes)
        right = max(box[0] + box[2] for box in boxes)
        bottom = max(box[1] + box[3] for box in boxes)
        bounds[nid] = dict(width=right - left, height=bottom - top,
                           dx=(left + right) / 2, dy=(top + bottom) / 2)
    return bounds


if __name__ == '__main__':
    print('Use compose_branching_history.py to reserve anchored branch captions.')
