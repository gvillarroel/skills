#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Arrange a data-first institutional history and choose its influence corridors."""

import argparse
import copy
import json
from pathlib import Path

from editorial_poster import EditorialPoster
from render_chart import require
from route_influences import compose_influences


def compose_history(source):
    require(source.get('design') == 'editorial' and source.get('mode') == 'lineage',
            'Branch composition requires an editorial institutional lineage.')
    require(source.get('layout', 'branches') == 'branches',
            'Use layout: branches for data-first composition; preserve authored or packed positions separately.')
    draft = copy.deepcopy(source)
    draft['layout'] = 'branches'
    poster = EditorialPoster(draft)
    resolved = copy.deepcopy(poster.data)
    resolved.update(layout='authored', font_size=poster.font)
    # All semantic fields, readable measurements and the measured key survive
    # resolution. The second pass can choose lateral influence attachments
    # without first forcing every influence through a bottom-to-top corridor.
    result, routing = compose_influences(resolved, local_first=True)
    if not routing['selected']:
        _, layout = EditorialPoster(result).render()
    else:
        layout = routing['layout']
    report = dict(status='pass', canvas=layout['canvas'], node_count=layout['node_count'],
                  edge_count=layout['edge_count'], crossing_count=layout['crossing_count'],
                  order=poster.data['branch_order'],
                  influence_choices=routing['choices'],
                  visual_review='Required. Stage allocation and route length do not measure aesthetic quality.')
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    paths = [p.resolve() for p in (args.source, args.output, args.report)]
    require(len(set(paths)) == 3, 'Input, output and report paths must all be distinct.')
    result, report = compose_history(json.loads(args.source.read_text(encoding='utf-8-sig')))
    for path, value in ((args.output, result), (args.report, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'influence_choices'}))


if __name__ == '__main__':
    main()
