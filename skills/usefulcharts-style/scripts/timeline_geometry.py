#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Shared lane widths and visible attachments for narrative chronology."""

import math
from render_chart import number, require, text_width, wrap


def lane_geometry(lanes, page_width):
    """Return lane origins and widths without changing the shared year scale."""
    require(lanes and len({lane['id'] for lane in lanes}) == len(lanes),
            'Timeline lane IDs must be distinct.')
    weights = [number(lane.get('weight', 1), 'lane.weight') for lane in lanes]
    require(all(weight > 0 for weight in weights), 'Lane weights must be positive.')
    available = page_width - 175
    require(available > 0, 'The page must have room for timeline lanes.')
    total = sum(weights)
    if all(weight == weights[0] for weight in weights):
        pitch = available / len(lanes)
        return {lane['id']: (110 + index * pitch, pitch) for index, lane in enumerate(lanes)}
    result = {}; cursor = 110.
    for lane, weight in zip(lanes, weights):
        width = available * weight / total
        result[lane['id']] = (cursor, width)
        cursor += width
    return result


def duration_width(period, envelope_width):
    """A stem encodes the full interval; its wider capsule only contains a name."""
    treatment = period.get('treatment', 'ribbon')
    require(treatment in ('ribbon', 'stem'), 'Period treatment must be ribbon or stem.')
    if treatment == 'ribbon':
        require('stem_width' not in period and 'label_position' not in period,
                'stem_width and label_position require treatment: stem.')
        return envelope_width
    width = number(period.get('stem_width', 5), 'period.stem_width')
    require(2 <= width <= envelope_width, 'A duration stem must be 2 units or wider and fit its label envelope.')
    position = number(period.get('label_position', .5), 'period.label_position')
    require(0 <= position <= 1, 'Period label_position must be between zero and one.')
    return width


def period_parts(period, envelope):
    """Return exact visible rectangles, including the complete name capsule."""
    x, y, width, height = envelope
    stem = duration_width(period, width)
    if period.get('treatment') != 'stem':
        return [envelope]
    size = number(period.get('size', 13), 'period.size')
    names = wrap(period['label'], height-14, size, True)
    require(len(names)*size*1.1 <= width-4, 'The period name needs a wider capsule.')
    label_height = min(height, math.ceil(max(text_width(line, size, True) for line in names)+14))
    label_y = y+(height-label_height)*period.get('label_position', .5)
    return [(x+(width-stem)/2, y, stem, height), (x, label_y, width, label_height)]


def transition_geometry(edge, source, target, source_box, target_box):
    """Join visible interval endpoints; taper bridges to a thin stem when needed."""
    a, b = source_box, target_box
    sp = number(edge.get('source_port', .5), 'source_port')
    tp = number(edge.get('target_port', .5), 'target_port')
    require(5 <= a[2]*sp <= a[2]-5 and 5 <= b[2]*tp <= b[2]-5,
            'Timeline ports must remain five units inside each ribbon.')
    widths = [duration_width(period, rect[2]) for period, rect in ((source, a), (target, b))]
    for period, port in ((source, sp), (target, tp)):
        require(period.get('treatment') != 'stem' or port == .5,
                'Duration stems require centered transition ports.')
    start, end = (a[0]+a[2]*sp, a[1]+a[3]), (b[0]+b[2]*tp, b[1])
    require(end[1] >= start[1]-.01, 'Timeline transitions must not go backward.')
    style = edge.get('style', 'dotted')
    require(style in ('dotted', 'ribbon'), 'Unknown timeline transition style.')
    flow = number(edge.get('ribbon_width', 0), 'ribbon_width')
    require(flow >= 0, 'Transition width must be nonnegative.')
    spans = []
    for period, rect, point, port, width in zip((source, target), (a, b), (start, end), (sp, tp), widths):
        if flow:
            require(flow/2 <= min(rect[2]*port, rect[2]*(1-port)), 'Transition width exceeds its attachment ports.')
            actual = min(flow, width) if period.get('treatment') == 'stem' else flow
            spans.append((point[0]-actual/2, point[0]+actual/2))
        elif period.get('treatment') == 'stem':
            spans.append((point[0]-width/2, point[0]+width/2))
        else:
            spans.append((rect[0], rect[0]+rect[2]))
    return start, end, spans
