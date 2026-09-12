#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3"]
# ///
"""Fit source-bound landmarks in local pockets without changing the graph."""

import argparse
import copy
import json
import math
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from shapely.geometry import LineString, box
from shapely.ops import unary_union
from shapely.prepared import prep

from editorial_landmarks import landmark_content
from editorial_poster import EditorialPoster
from render_chart import number, require


MEASURE = r"""() => {
  const svg=document.querySelector('svg');
  const bounds=el=>{
    const b=el.getBBox(),m=svg.getScreenCTM().inverse().multiply(el.getScreenCTM());
    const p=[[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
    const xs=p.map(v=>v.x),ys=p.map(v=>v.y);
    return [Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];
  };
  const rectangles=[...svg.querySelectorAll('[data-node-box], [data-annotation-id], text, [data-artwork]')].map(bounds);
  const paths=[...svg.querySelectorAll('[data-edge-id], [data-union-id]')].map(el=>{
    const length=el.getTotalLength();
    return Array.from({length:Math.ceil(length/2)+1},(_,i)=>{
      const p=el.getPointAtLength(Math.min(length,i*2));return [p.x,p.y];
    });
  });
  return {rectangles,paths};
}"""


def fit_landmarks(source, geometry, nodes, width, height, radius=240, step=4):
    """Change landmark offsets only; keep a bounded association with its anchor."""
    require(40<=radius<=360 and 1<=step<=12,'Use a local search radius of 40–360 and a step of 1–12 units.')
    data=copy.deepcopy(source)
    obstacles=[box(*b).buffer(5) for b in geometry['rectangles'] if b[2]>b[0] and b[3]>b[1]]
    obstacles += [LineString(points).buffer(5) for points in geometry['paths'] if len(points)>1]
    decisions=[]
    for index,a in enumerate(data.get('annotations',[])):
        if a.get('kind')!='landmark':continue
        require(a.get('node') in nodes,'A landmark requires a known source node.')
        node=nodes[a['node']];content=landmark_content(a,node)
        require(a.get('group',node['group'])==node['group'],'A landmark must retain its source category.')
        w,h=content['width'],content['height'];x,y=node['x'],node['y']
        dx=number(a.get('dx',0),'landmark.dx');dy=number(a.get('dy',0),'landmark.dy')
        vertical=number(a.get('vertical_radius',max(90,h)),'landmark.vertical_radius')
        require(0<vertical<=radius,'A landmark vertical radius must remain within its local search radius.')
        preferred=(x+dx,y+dy);blocked=unary_union(obstacles);prepared=prep(blocked)
        candidates=[]
        for oy in range(-int(radius),int(radius)+1,step):
            for ox in range(-int(radius),int(radius)+1,step):
                distance=math.hypot(ox,oy)
                if distance>radius:continue
                xx,yy=x+ox,y+oy
                if xx-w/2<48 or xx+w/2>width-48 or yy-h/2<130 or yy+h/2>height-85:continue
                # A local caption must not occupy an unrelated generation.
                if abs(oy)>vertical:continue
                envelope=box(xx-w/2,yy-h/2,xx+w/2,yy+h/2)
                if prepared.intersects(envelope):continue
                distances=[(math.hypot(xx-other['x'],yy-other['y']),other['group']) for other in nodes.values()]
                same=min(d for d,g in distances if g==node['group'])
                other=min((d for d,g in distances if g!=node['group']),default=math.inf)
                if same>other+12:continue
                score=math.hypot(xx-preferred[0],(yy-preferred[1])*1.4)+distance*.15
                candidates.append((score,xx,yy,envelope))
        require(candidates,f'No local pocket for {a["node"]}.{content["field"]}; author the surrounding region or omit this optional repeated landmark, preserving its source field.')
        _,xx,yy,envelope=min(candidates,key=lambda v:(v[0],v[2],v[1]))
        a.update(dx=round(xx-x,3),dy=round(yy-y,3));obstacles.append(envelope.buffer(8))
        decisions.append(dict(annotation=index,node=a['node'],field=content['field'],label=content['label'],
            dx=a['dx'],dy=a['dy'],width=w,height=h,candidate_count=len(candidates)))
    return data,dict(status='pass',placements=decisions,changed_fields=['annotations[].dx','annotations[].dy'],
        obstacle_rectangles=len(geometry['rectangles']),obstacle_paths=len(geometry['paths']))


def measure_graph(source, workdir, browser_executable=None):
    require(source.get('design')=='editorial' and source.get('mode') in ('genealogy','lineage'),
        'Landmarks require an editorial genealogy or institutional graph.')
    require(source.get('layout') in ('authored','resolved') and all('x' in n and 'y' in n for n in source['nodes']),
        'Resolve the graph before placing local landmarks.')
    require(not source.get('insets'),'Compose inset-bearing pages explicitly before fitting local landmarks.')
    base=copy.deepcopy(source);base['annotations']=[a for a in base.get('annotations',[]) if a.get('kind')!='landmark']
    poster=EditorialPoster(base);svg,_=poster.render()
    with tempfile.TemporaryDirectory(prefix='landmark-measure-',dir=workdir) as scratch:
        file=Path(scratch)/'base.svg';file.write_text(svg,encoding='utf-8')
        with sync_playwright() as p:
            browser=None
            attempts=[{'executable_path':str(browser_executable)}] if browser_executable else [{},{'channel':'chrome'},{'channel':'msedge'}]
            for options in attempts:
                try:browser=p.chromium.launch(headless=True,**options);break
                except Exception:continue
            require(browser is not None,'No Chromium browser is available; provision it or use --browser-executable.')
            page=browser.new_page();page.goto(file.resolve().as_uri());page.evaluate('document.fonts.ready')
            geometry=page.evaluate(MEASURE);browser.close()
    return geometry,poster.w,poster.h


def place_landmarks(source, workdir, radius=240, browser_executable=None):
    geometry,width,height=measure_graph(source,workdir,browser_executable)
    nodes={n['id']:n for n in source['nodes']}
    return fit_landmarks(source,geometry,nodes,width,height,radius)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True);parser.add_argument('--radius',type=float,default=240)
    parser.add_argument('--browser-executable',type=Path)
    args=parser.parse_args()
    try:
        require(len({p.resolve() for p in (args.input,args.output,args.report)})==3,'Input, output and report must be distinct.')
        data=json.loads(args.input.read_text(encoding='utf-8-sig'));args.output.parent.mkdir(parents=True,exist_ok=True)
        resolved,report=place_landmarks(data,args.output.parent,args.radius,args.browser_executable)
        # The renderer also checks the final composition before either artifact is written.
        EditorialPoster(resolved).render()
        args.output.write_text(json.dumps(resolved,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report));return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(f'Landmarks could not be placed: {error}');return 2


if __name__=='__main__':raise SystemExit(main())
