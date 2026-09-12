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

from render_chart import number,require,text_width,wrap


def obstacles_for(data,scale,pitch,lanes):
    rectangles={};obstacles=[]
    for period in data['periods']:
        require(period['id'] not in rectangles,'Timeline period IDs must be distinct.')
        require(period['lane'] in lanes,'Timeline periods require known lanes.')
        x=110+lanes[period['lane']]*pitch+period.get('offset',18)
        y=scale(period['start']);width=number(period.get('bar_width',32),'bar_width')
        height=scale(period['end'])-y
        require(width>0 and height>0,'Timeline intervals need positive width and duration.')
        rectangles[period['id']]=(x,y,width,height)
        obstacles.append(box(x,y,x+width,y+height))
    for edge in data.get('transitions',[]):
        require(edge['source'] in rectangles and edge['target'] in rectangles,'Timeline transitions require known periods.')
        a,b=rectangles[edge['source']],rectangles[edge['target']]
        sp,tp=number(edge.get('source_port',.5),'source_port'),number(edge.get('target_port',.5),'target_port')
        require(5<=a[2]*sp<=a[2]-5 and 5<=b[2]*tp<=b[2]-5,'Timeline ports must remain five units inside each ribbon.')
        sx,tx=a[0]+a[2]*sp,b[0]+b[2]*tp;sy,ty=a[1]+a[3],b[1]
        require(ty>=sy,'Timeline transitions must not go backward.')
        style=edge.get('style','dotted')
        require(style in ('dotted','ribbon'),'Unknown timeline transition style.')
        if style=='ribbon':
            flow=number(edge.get('ribbon_width',0),'ribbon_width')
            require(flow>=0 and flow/2<=min(a[2]*sp,a[2]*(1-sp),b[2]*tp,b[2]*(1-tp)),'Transition width exceeds its attachment ports.')
            sa,sb=(sx-flow/2,sx+flow/2) if flow else (a[0],a[0]+a[2])
            ta,tb=(tx-flow/2,tx+flow/2) if flow else (b[0],b[0]+b[2])
            obstacles.append(Polygon([(sa,sy),(sb,sy),(tb,ty),(ta,ty)]))
        else:
            mid=(sy+ty)/2
            obstacles.append(LineString([(sx,sy),(sx,mid),(tx,mid),(tx,ty)]).buffer(1))
    return obstacles


def pack_events(source,max_width=170,clearance=2.5):
    """Change only event widths and offsets; preserve all semantic inputs."""
    data=copy.deepcopy(source)
    require(data.get('design')=='editorial' and data.get('mode')=='timeline' and data.get('layout')!='compact',
        'Pack narrative events in an editorial timeline with authored period ribbons.')
    width=number(data.get('width',1800),'width');height=number(data.get('height',2700),'height')
    start,end=number(data['time']['start'],'time.start'),number(data['time']['end'],'time.end')
    require(width>400 and height>500 and end>start,'The timeline needs a positive year scale and a usable page.')
    require(max_width>=54 and clearance>=0,'Use a maximum note width of at least 54 and nonnegative clearance.')
    lanes={lane['id']:i for i,lane in enumerate(data['lanes'])}
    require(lanes and len(lanes)==len(data['lanes']),'Timeline lane IDs must be distinct.')
    pitch=(width-175)/len(lanes);scale=lambda year:190+(year-start)/(end-start)*(height-302)
    obstacles=obstacles_for(data,scale,pitch,lanes);envelopes=[];decisions=[];ids=set()
    for event in sorted(data.get('events',[]),key=lambda item:item['year']):
        require(event['id'] not in ids and event['lane'] in lanes,'Events require distinct IDs and known lanes.');ids.add(event['id'])
        require(start<=event['year']<=end,'Event dates must be inside the year scale.')
        size=number(event.get('size',10.5),'event.size');small=number(event.get('detail_size',size*.88),'event.detail_size')
        require(size>0 and small>0,'Event type sizes must be positive.')
        year_y=scale(event['year']);lane_x=110+lanes[event['lane']]*pitch
        aw=number(event.get('art_width',event.get('art_size',56)),'art_width') if event.get('icon') else 0
        ah=number(event.get('art_height',event.get('art_size',56)),'art_height') if event.get('icon') else 0
        require(not event.get('icon') or (aw>0 and ah>0),'Event illustrations need positive dimensions.')
        # Notes start below their date. Padding must not extend the exact
        # endpoint of a preceding interval into later text.
        active=[o for o in obstacles if o.bounds[3]>year_y+.001]+envelopes
        blocked=unary_union(active);prepared=prep(blocked);candidates=[]
        widths={float(w) for w in range(int(max_width),53,-12)}|{54.,min(max_width,float(event.get('width',max_width)))}
        for note_width in sorted(widths,reverse=True):
            if note_width<aw or note_width>pitch-3:continue
            try:names=wrap(event['label'],note_width,size,True);details=wrap(event.get('detail',''),note_width,small)
            except ValueError:continue
            note_height=len(names)*size*1.18+len(details)*small*1.18+(ah+5 if aw else 0)
            if year_y+note_height>height-82:continue
            preferred=event.get('offset',64)
            positions={0.,1.,3.,5.,pitch-note_width-5,preferred,*range(5,int(pitch-note_width-4),5)}
            for obstacle in active:
                x1,y1,x2,y2=obstacle.bounds
                if y1<year_y+note_height+7 and y2>year_y-7:
                    positions.update((x2-lane_x+8,x1-lane_x-note_width-8))
            for offset in sorted(positions):
                if offset<0 or offset+note_width>pitch-3:continue
                x=lane_x+offset;y=year_y;pieces=[]
                for lines,fs,bold in ((names,size,True),(details,small,False)):
                    for line in lines:
                        pieces.append(box(x,y,x+text_width(line,fs,bold),y+fs*1.18));y+=fs*1.18
                if aw:
                    ix=x+(note_width-aw)/2;iy=y+5;pieces.append(box(ix,iy,ix+aw,iy+ah))
                require(pieces,'Every event needs visible content.')
                envelope=unary_union(pieces)
                if prepared.intersects(envelope.buffer(clearance)):continue
                score=(len(names)+len(details),-note_width,abs(offset-preferred),offset)
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
    parser.add_argument('--report',type=Path);parser.add_argument('--max-width',default=170,type=float)
    args=parser.parse_args()
    try:data,report=pack_events(json.loads(args.input.read_text(encoding='utf-8')),args.max_width)
    except (ValueError,KeyError) as error:
        print(json.dumps(dict(status='needs-layout',message=str(error))));raise SystemExit(1)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',events=report['event_count'],output=str(args.output))))


if __name__=='__main__':main()
