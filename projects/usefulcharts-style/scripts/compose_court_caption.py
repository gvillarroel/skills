#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3"]
# ///
"""Compose one existing court capsule and verify its actual painted placement."""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import viewer
from playwright.sync_api import sync_playwright
from shapely.geometry import LineString, box


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--node',default='person-35-0');parser.add_argument('--width',type=float,default=74)
    parser.add_argument('--dx',type=float,default=-32);parser.add_argument('--dy',type=float,default=40)
    parser.add_argument('--detail',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=json.loads(args.source.read_text(encoding='utf-8'));nodes={n['id']:n for n in source['nodes']}
    matches=[(i,a) for i,a in enumerate(source['annotations']) if a.get('kind')=='pill' and a.get('node')==args.node]
    if len(matches)!=1:raise ValueError('Identify exactly one existing court capsule.')
    i,annotation=matches[0];annotation.update(width=args.width,dx=args.dx,dy=args.dy)
    (args.output/'source.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    try:
        svg,layout=EditorialPoster(source).render()
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,source['title']),encoding='utf-8')
        root=ET.fromstring(svg);ns={'s':'http://www.w3.org/2000/svg'}
        group=root.find(f'.//s:g[@data-annotation-id="annotation-{i}"]',ns);rect=group.find('s:rect',ns)
        x,y,w,h=[float(rect.attrib[k]) for k in ('x','y','width','height')]
        expected=[nodes[args.node]['x']+args.dx,nodes[args.node]['y']+args.dy]
        actual=[x+w/2,y+h/2]
        unchanged_preference=max(abs(a-b) for a,b in zip(expected,actual))<.01
        with sync_playwright() as p:
            browser=p.chromium.launch();page=browser.new_page()
            page.goto((args.output/'poster.svg').resolve().as_uri());page.evaluate('document.fonts.ready')
            paths=page.evaluate("""()=>[...document.querySelectorAll('[data-edge-id],[data-union-id]')].map(el=>{
              const length=el.getTotalLength();return {id:el.dataset.edgeId||el.dataset.unionId,points:Array.from({length:Math.ceil(length)+1},(_,i)=>{const p=el.getPointAtLength(Math.min(length,i));return [p.x,p.y]})};})""")
            if args.detail:
                page.set_viewport_size({'width':int(source['width']),'height':int(source['height'])})
                args.detail.parent.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(args.detail),clip={'x':max(24,nodes[args.node]['x']-280),
                    'y':nodes[args.node]['y']-230,'width':600,'height':400})
            browser.close()
        obstacle=box(x,y,x+w,y+h).buffer(2)
        crossings=[p['id'] for p in paths if len(p['points'])>1 and LineString(p['points']).intersects(obstacle)]
        status='pass' if unchanged_preference and not crossings else 'fail'
        report=dict(status=status,node=args.node,label=annotation['label'],requested_center=expected,painted_center=actual,
            painted_box=[x,y,w,h],printed_lines=[t.text for t in group.findall('s:text',ns)],
            silent_relocation=not unchanged_preference,paths_through_caption=crossings,layout=layout)
    except ValueError as error:report=dict(status='fail',error=str(error))
    (args.output/'composition.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='layout'}));return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())
