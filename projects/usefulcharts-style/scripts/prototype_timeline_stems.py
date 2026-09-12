#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Render source-preserving chronology studies from the preceding publication."""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'skills/usefulcharts-style/scripts'))
from pack_timeline_events import pack_events
from timeline_geometry import lane_geometry
from editorial_poster import EditorialPoster
from render_chart import viewer

SOURCE = 'skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', default='e35d36c3')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--variants', nargs='+')
    args = parser.parse_args()
    if args.output.exists():parser.error('Choose a new output directory to preserve earlier exploration evidence.')
    base = json.loads(subprocess.check_output(['git', 'show', f'{args.before}:{SOURCE}'], cwd=ROOT))
    choices = {
        'stems': (1800, 2400, [1]*5),
        'weighted-stems': (1800, 2400, [1.08,1.08,1.14,.8,.9]),
        'compact-stems': (1680, 2200, [1]*5),
        'compact-weighted': (1680, 2200, [1.08,1.08,1.14,.8,.9]),
        'portrait-weighted': (1680, 2400, [1.02,1.04,1.12,.78,1.04]),
        'portrait-selective': (1680, 2400, [1.02,1.04,1.12,.78,1.04]),
        'full-selective': (1800, 2400, [1.02,1.04,1.12,.78,1.04]),
        'portrait-balanced': (1680, 2400, [1.02,1.04,1.12,.78,1.04]),
    }
    results = []
    for name, (width, height, weights) in choices.items():
        if args.variants and name not in args.variants: continue
        folder = args.output/name; folder.mkdir(parents=True, exist_ok=True)
        data = copy.deepcopy(base); data.update(width=width, height=height)
        for lane, weight in zip(data['lanes'], weights):
            if weight != 1: lane['weight'] = weight
        lanes = lane_geometry(data['lanes'], width)
        stems = set()
        for period in data['periods']:
            period['offset'] = (period['offset']+period['bar_width']/2)/325*lanes[period['lane']][1]-period['bar_width']/2
            selective='selective' in name or name=='portrait-balanced'
            if period['size'] < 18 and (not selective or period['end']-period['start']>=175 or (name=='portrait-balanced' and period['id'] in ('p0-lower','p0-upper'))):
                period.update(treatment='stem', stem_width=5)
                stems.add(period['id'])
            if name=='portrait-balanced' and period['size']==18:
                period['offset']+=(period['bar_width']-42)/2
                period['bar_width']=42
        for edge in data['transitions']:
            if edge['source'] in stems: edge['source_port'] = .5
            if edge['target'] in stems: edge['target_port'] = .5
        for event in data['events']:
            event['offset'] = event['offset']/325*lanes[event['lane']][1]
        data['reading_note'] = 'One year scale. Thin stems and full bands show exact durations; wider stem labels name periods. Bridges show succession, division or union; dots show uncertainty. Width is compositional. Contextual objects and map do not depict these fictional regions.'
        (folder/'input.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        try:
            data, placements = pack_events(data)
            svg, report = EditorialPoster(data).render()
            (folder/'brief.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
            (folder/'poster.svg').write_text(svg, encoding='utf-8')
            (folder/'poster.html').write_text(viewer(svg, data['title']), encoding='utf-8')
            (folder/'layout.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
            (folder/'placements.json').write_text(json.dumps(placements, indent=2)+'\n', encoding='utf-8')
            results.append(dict(variant=name, status='rendered', stems=len(stems), canvas=[width,height]))
        except ValueError as error:
            (folder/'rejected.json').write_text(json.dumps(dict(error=str(error)), indent=2)+'\n', encoding='utf-8')
            results.append(dict(variant=name, status='needs-layout', reason=str(error)))
        print(json.dumps(results[-1]), flush=True)
    (args.output/'attempts.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__': main()
