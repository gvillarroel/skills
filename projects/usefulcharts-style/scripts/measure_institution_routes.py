#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Measure actual SVG relationship lengths without treating them as aesthetic scores."""

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright


def collinear_overlaps(path):
    root=ET.parse(path).getroot();metadata=json.loads(root.find('{http://www.w3.org/2000/svg}metadata[@id="chart-data"]').text)
    def straights(route):
        points=route['points'];lengths=[abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(points,points[1:])]
        answer=[]
        for k,(a,b) in enumerate(zip(points,points[1:])):
            length=lengths[k]
            if not length:continue
            first=min(8,lengths[k-1]/2,length/2) if k else 0
            last=min(8,lengths[k+1]/2,length/2) if k<len(lengths)-1 else 0
            answer.append(([round(a[i]+(b[i]-a[i])*first/length,2) for i in (0,1)],
                [round(b[i]+(a[i]-b[i])*last/length,2) for i in (0,1)]))
        return answer
    routes=metadata['routes'];found=[]
    for i,a in enumerate(routes):
        for b in routes[i+1:]:
            shared=bool({a['source'],a['target']} & {b['source'],b['target']})
            if shared and a['kind']==b['kind']:continue
            for p,q in straights(a):
                for r,s in straights(b):
                    for axis in (0,1):
                        other=1-axis
                        if max(p[axis],q[axis],r[axis],s[axis])-min(p[axis],q[axis],r[axis],s[axis])>.02:continue
                        overlap=min(max(p[other],q[other]),max(r[other],s[other]))-max(min(p[other],q[other]),min(r[other],s[other]))
                        if overlap>4:found.append(dict(first=a['id'],second=b['id'],length=round(overlap,2),shared_endpoint=shared,
                            segment=[p,q],other_segment=[r,s]));break
    return found


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',nargs=2,action='append',required=True,metavar=('NAME','SVG'))
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page()
        for name,filename in args.candidate:
            path=Path(filename).resolve();page.goto(path.as_uri());page.evaluate('document.fonts.ready')
            data=page.evaluate("""()=>{const svg=document.documentElement;return {canvas:[svg.viewBox.baseVal.width,svg.viewBox.baseVal.height],edges:[...document.querySelectorAll('path[data-edge-id]')].map(el=>({id:el.dataset.edgeId,kind:el.dataset.kind||el.getAttribute('data-edge-kind'),length:el.getTotalLength(),bends:(el.getAttribute('d').match(/ Q /g)||[]).length}))};}""")
            lengths=sorted(data['edges'],key=lambda e:e['length'],reverse=True)
            overlaps=collinear_overlaps(path)
            results.append(dict(id=name,canvas=data['canvas'],edge_count=len(lengths),total_length=sum(e['length'] for e in lengths),
                total_bends=sum(e['bends'] for e in lengths),longest=lengths[:12],edges=lengths,
                unrelated_collinear_overlaps=sum(not item['shared_endpoint'] for item in overlaps),
                mixed_kind_endpoint_overlaps=sum(item['shared_endpoint'] for item in overlaps),overlaps=overlaps))
        browser.close()
    report=dict(candidates=results,scope='Full rendered relationships, including influence. These geometric measures require whole-page and reading-scale visual interpretation.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('edges','longest','overlaps')} for r in results]))


if __name__=='__main__':main()
