#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Place dated narrative notes around authored timeline periods and bridges."""

import argparse
import copy
import json
from pathlib import Path

from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
from shapely.prepared import prep

from render_chart import number,require
from timeline_geometry import lane_geometry,transition_geometry,period_parts
from timeline_annotations import event_content


def obstacles_for(data,scale,lanes):
    rectangles={};obstacles=[]
    periods={period['id']:period for period in data['periods']}
    for period in data['periods']:
        require(period['id'] not in rectangles,'Timeline period IDs must be distinct.')
        require(period['lane'] in lanes,'Timeline periods require known lanes.')
        x=lanes[period['lane']][0]+period.get('offset',18)
        y=scale(period['start']);width=number(period.get('bar_width',32),'bar_width')
        height=scale(period['end'])-y
        require(width>0 and height>0,'Timeline intervals need positive width and duration.')
        rectangles[period['id']]=(x,y,width,height)
        for px,py,pw,ph in period_parts(period,(x,y,width,height)):
            obstacles.append(box(px,py,px+pw,py+ph))
    for edge in data.get('transitions',[]):
        require(edge['source'] in rectangles and edge['target'] in rectangles,'Timeline transitions require known periods.')
        a,b=rectangles[edge['source']],rectangles[edge['target']]
        (sx,sy),(tx,ty),spans=transition_geometry(edge,periods[edge['source']],periods[edge['target']],a,b)
        style=edge.get('style','dotted')
        require(style in ('dotted','ribbon'),'Unknown timeline transition style.')
        if style=='ribbon':
            (sa,sb),(ta,tb)=spans
            obstacles.append(Polygon([(sa,sy),(sb,sy),(tb,ty),(ta,ty)]))
        else:
            mid=(sy+ty)/2
            obstacles.append(LineString([(sx,sy),(sx,mid),(tx,mid),(tx,ty)]).buffer(1))
    return obstacles


def pack_events(source,max_width=None,clearance=2.5):
    """Change only event widths and offsets; preserve all semantic inputs."""
    data=copy.deepcopy(source)
    require(data.get('design')=='editorial' and data.get('mode')=='timeline' and data.get('layout')!='compact',
        'Pack narrative events in an editorial timeline with authored period ribbons.')
    width=number(data.get('width',1800),'width');height=number(data.get('height',2700),'height')
    start,end=number(data['time']['start'],'time.start'),number(data['time']['end'],'time.end')
    require(width>400 and height>500 and end>start,'The timeline needs a positive year scale and a usable page.')
    require((max_width is None or max_width>=54) and clearance>=0,'Use a maximum note width of at least 54 and nonnegative clearance.')
    lanes=lane_geometry(data['lanes'],width)
    scale=lambda year:190+(year-start)/(end-start)*(height-302)
    obstacles=obstacles_for(data,scale,lanes);envelopes=[];decisions=[];ids=set()
    for event in sorted(data.get('events',[]),key=lambda item:item['year']):
        require(event['id'] not in ids and event['lane'] in lanes,'Events require distinct IDs and known lanes.');ids.add(event['id'])
        require(start<=event['year']<=end,'Event dates must be inside the year scale.')
        size=number(event.get('size',10.5),'event.size');small=number(event.get('detail_size',size*.88),'event.detail_size')
        require(size>0 and small>0,'Event type sizes must be positive.')
        year_y=scale(event['year']);lane_x,pitch=lanes[event['lane']]
        aw=number(event.get('art_width',event.get('art_size',56)),'art_width') if event.get('icon') else 0
        ah=number(event.get('art_height',event.get('art_size',56)),'art_height') if event.get('icon') else 0
        require(not event.get('icon') or (aw>0 and ah>0),'Event illustrations need positive dimensions.')
        require(event.get('art_position','below') in ('above','below','left','right'),'Event art_position must be above, below, left or right.')
        require(event.get('icon') or 'art_position' not in event,'art_position requires an event illustration.')
        # Notes start below their date. Padding must not extend the exact
        # endpoint of a preceding interval into later text.
        above=event.get('icon') and event.get('art_position')=='above'
        top=year_y-ah-5 if above else year_y
        active=[o for o in obstacles if o.bounds[3]>top+.001]+envelopes
        blocked=unary_union(active);prepared=prep(blocked);candidates=[]
        # Preserve a prose budget when an image is beside the note. An explicit
        # maximum remains a hard cap on the complete image-and-text group.
        side=bool(event.get('icon')) and event.get('art_position') in ('left','right')
        limit=max_width if max_width is not None else min(pitch-3,170+(aw+8 if side else 0))
        widths={float(w) for w in range(int(limit),53,-12)}|{54.,min(limit,float(event.get('width',limit)))}
        for note_width in sorted(widths,reverse=True):
            if note_width<aw or note_width>pitch-3:continue
            try:content=event_content(event,note_width)
            except ValueError:continue
            note_height=content['bottom']-content['top']
            if year_y+content['bottom']>height-82 or year_y+content['top']<190:continue
            preferred=event.get('offset',64)
            positions={0.,1.,3.,5.,pitch-note_width-5,preferred,*range(5,int(pitch-note_width-4),5)}
            for obstacle in active:
                x1,y1,x2,y2=obstacle.bounds
                if y1<year_y+content['bottom']+7 and y2>year_y+content['top']-7:
                    positions.update((x2-lane_x+8,x1-lane_x-note_width-8))
            for offset in sorted(positions):
                if offset<0 or offset+note_width>pitch-3:continue
                x=lane_x+offset;pieces=[]
                for bx,by,bw,bh in content['boxes']:
                    pieces.append(box(x+bx,year_y+by,x+bx+bw,year_y+by+bh))
                require(pieces,'Every event needs visible content.')
                envelope=unary_union(pieces)
                if prepared.intersects(envelope.buffer(clearance)):continue
                score=(content['line_count'],-note_width,abs(offset-preferred),offset)
                candidates.append((score,offset,note_width,note_height,envelope))
        require(candidates,f'No readable placement for event {event["id"]}. Recompose nearby periods, enlarge the page, or explicitly revise the event treatment; text and dates were not changed.')
        _,offset,note_width,note_height,envelope=min(candidates,key=lambda item:item[0])
        event.update(offset=round(offset,3),width=note_width)
        envelopes.append(envelope)
        decisions.append(dict(id=event['id'],offset=event['offset'],width=note_width,height=note_height))
    return data,dict(status='pass',event_count=len(decisions),decisions=decisions,
        limitation='This is a placement preflight. Render, run the source-backed browser audit, and inspect the final image.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--report',type=Path);parser.add_argument('--max-width',type=float,help='Cap the complete note group. By default, side images add their footprint to a 170-unit prose budget.')
    args=parser.parse_args()
    try:data,report=pack_events(json.loads(args.input.read_text(encoding='utf-8')),args.max_width)
    except (ValueError,KeyError) as error:
        print(json.dumps(dict(status='needs-layout',message=str(error))));raise SystemExit(1)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',events=report['event_count'],output=str(args.output))))


if __name__=='__main__':main()
