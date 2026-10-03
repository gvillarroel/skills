#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Place measured chronological sequences into shared family rows without changing data."""
from pathlib import Path
import argparse
import copy
import json
import math


def positive(value,name,allow_zero=False):
    if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value < 0 or (value==0 and not allow_zero):
        raise ValueError(f'{name} must be a finite positive number')
    return value


def pack(source):
    """Keep author-defined membership/order; reuse horizontal space within each group."""
    if source.get('mode')=='numeric':return pack_numeric(source)
    data=copy.deepcopy(source)
    width=positive(data.get('width'), 'width')
    margin=positive(data.get('margin',40),'margin',True)
    rail=positive(data.get('label_rail',180),'label_rail',True)
    gap=positive(data.get('gap',16),'gap',True)
    row_gap=positive(data.get('row_gap',24),'row_gap',True)
    top=positive(data.get('top',0),'top',True)
    inner=width-2*margin
    if inner-rail<=0:raise ValueError('The width leaves no record space')
    column_gap=positive(data.get('column_gap',gap*2),'column_gap',True)
    records=data.get('records',[]);groups=data.get('groups',[])
    by={r['id']:r for r in records}
    if not records or len(by)!=len(records):raise ValueError('Record IDs must be unique and non-empty')
    if any(not isinstance(k,str) or not k for k in by):raise ValueError('Record IDs must be non-empty strings')
    seen=[];group_ids=set();boxes=[];rows=[];group_layout=[];y=top;shelf_used=0;shelf_height=0;band=0
    for g in groups:
        if not isinstance(g.get('id'),str) or not g['id'] or g['id'] in group_ids:raise ValueError('Group IDs must be unique and non-empty')
        group_ids.add(g['id']);members=g.get('members',[])
        if not members or any(i not in by for i in members):raise ValueError('Each group needs known members')
        seen.extend(members)
        group_width=positive(g.get('width',inner),f'{g["id"]}.width')
        if group_width>inner:raise ValueError('A group is wider than the canvas interior')
        available=group_width-rail
        if available<=0:raise ValueError('A group has no room after its label rail')
        if shelf_used and shelf_used+column_gap+group_width>inner+1e-6:
            y+=shelf_height+row_gap;shelf_used=0;shelf_height=0;band+=1
        gx=margin+shelf_used+(column_gap if shelf_used else 0)
        header=positive(g.get('header_height',0),f'{g["id"]}.header_height',True)
        start_y=y;local_y=y+header;chunks=[];current=[];used=0
        for id in members:
            r=by[id];w=positive(r.get('width'),f'{id}.width');positive(r.get('height'),f'{id}.height')
            if w>available:raise ValueError(f'{id} is wider than the available row; remeasure or enlarge the canvas')
            if current and used+gap+w>available+1e-6:chunks.append(current);current=[];used=0
            current.append(id);used+=w+(gap if len(current)>1 else 0)
        if current:chunks.append(current)
        for n,ids in enumerate(chunks):
            h=max(by[id]['height'] for id in ids)
            if n==0:h=max(h,positive(g.get('label_height',0),f'{g["id"]}.label_height',True))
            x=gx+rail;rid=f'{g["id"]}-{n+1}'
            for id in ids:
                r=by[id];boxes.append(dict(id=id,group=g['id'],row=rid,x=x,y=local_y,w=r['width'],h=r['height']))
                x+=r['width']+gap
            rows.append(dict(id=rid,group=g['id'],members=ids,x=gx+rail,y=local_y,h=h,used_width=x-(gx+rail)-gap,capacity=available))
            local_y+=h+row_gap
        gh=local_y-start_y-row_gap
        group_layout.append(dict(id=g['id'],x=gx,y=start_y,w=group_width,h=gh,band=band,rows=len(chunks),members=members))
        shelf_used=gx-margin+group_width;shelf_height=max(shelf_height,gh)
    if len(seen)!=len(set(seen)) or set(seen)!=set(by):raise ValueError('Groups must partition the complete record inventory exactly once')
    result=dict(version=1,mode='schematic-sequence',width=width,height=y+shelf_height+margin,boxes=boxes,rows=rows,groups=group_layout,record_count=len(records),group_count=len(groups),row_count=len(rows),band_count=band+1,multi_record_rows=sum(len(r['members'])>1 for r in rows))
    return dict(source=data,layout=result)


def pack_numeric(source):
    """Assign only vertical tracks; keep every measured calendar footprint fixed in x."""
    data=copy.deepcopy(source)
    width=positive(data.get('width'),'width');top=positive(data.get('top',0),'top',True)
    gap=positive(data.get('gap',12),'gap',True);row_gap=positive(data.get('row_gap',20),'row_gap',True)
    track_gap=positive(data.get('track_gap',10),'track_gap',True)
    records=data.get('records',[]);by={r['id']:r for r in records}
    if not records or len(by)!=len(records):raise ValueError('Record IDs must be unique')
    if any(not isinstance(k,str) or not k for k in by):raise ValueError('Record IDs must be non-empty strings')
    groups=data.get('groups',[]);seen=[];group_ids=set();boxes=[];rows=[];layouts=[];y=top
    for g in groups:
        if not isinstance(g.get('id'),str) or not g['id'] or g['id'] in group_ids:raise ValueError('Group IDs must be unique and non-empty')
        group_ids.add(g['id']);ids=g.get('members',[])
        if not ids or any(id not in by for id in ids):raise ValueError('Each group needs known members')
        seen.extend(ids)
        for id in ids:
            r=by[id];left=positive(r.get('x0'),f'{id}.x0',True);right=positive(r.get('x1'),f'{id}.x1')
            positive(r.get('height'),f'{id}.height')
            if right<=left or right>width:raise ValueError(f'{id} has an invalid or outside fixed x footprint')
        tracks=[];ends=[]
        for id in sorted(ids,key=lambda id:(by[id]['x0'],by[id]['x1'],id)):
            r=by[id];options=[i for i,end in enumerate(ends) if end+gap<=r['x0']]
            track=min(options,key=lambda i:ends[i]) if options else len(tracks)
            if track==len(tracks):tracks.append([]);ends.append(0)
            tracks[track].append(id);ends[track]=r['x1']
        local=y+positive(g.get('header_height',0),'header_height',True)
        for i,ids_in_track in enumerate(tracks):
            hh=max(by[id]['height'] for id in ids_in_track);rid=f'{g["id"]}-{i+1}'
            for id in ids_in_track:
                r=by[id];boxes.append(dict(id=id,group=g['id'],row=rid,x=r['x0'],y=local,w=r['x1']-r['x0'],h=r['height']))
            rows.append(dict(id=rid,group=g['id'],members=ids_in_track,y=local,h=hh));local+=hh+track_gap
        gh=max(local-y-track_gap,positive(g.get('label_height',0),'label_height',True))
        layouts.append(dict(id=g['id'],y=y,h=gh,rows=len(tracks),members=ids));y+=gh+row_gap
    if len(seen)!=len(set(seen)) or set(seen)!=set(by):raise ValueError('Groups must partition the complete inventory exactly once')
    if data.get('reuse_tracks'):
        if data.get('labels_in_footprints') is not True:
            raise ValueError('Track reuse requires locally identified groups in measured footprints')
        if any(g.get(k,0) for g in groups for k in ('header_height','label_height','label_width')):
            raise ValueError('Track reuse uses local labels, not rectangular group headers')
        # Reclaim each terminated track, even while another track of its family continues.
        membership={id:g['id'] for g in groups for id in g['members']}
        tracks=[];ends=[];last_groups=[]
        for id in sorted(by,key=lambda id:(by[id]['x0'],by[id]['x1'],id)):
            available=[i for i,end in enumerate(ends) if end+gap<=by[id]['x0']]
            chosen=min(available,key=lambda i:(last_groups[i]!=membership[id],ends[i],i)) if available else len(tracks)
            if chosen==len(tracks):tracks.append([]);ends.append(0);last_groups.append(None)
            tracks[chosen].append(id);ends[chosen]=by[id]['x1'];last_groups[chosen]=membership[id]
        boxes=[];rows=[];y=top
        for i,ids in enumerate(tracks):
            h=max(by[id]['height'] for id in ids);rid=f'shared-{i+1}'
            for id in ids:
                r=by[id];boxes.append(dict(id=id,group=membership[id],row=rid,x=r['x0'],y=y,w=r['x1']-r['x0'],h=r['height']))
            rows.append(dict(id=rid,members=ids,groups=list(dict.fromkeys(membership[id] for id in ids)),y=y,h=h))
            y+=h+track_gap
        layouts=[]
        for g in groups:
            owned=[b for b in boxes if b['group']==g['id']]
            layouts.append(dict(id=g['id'],members=g['members'],fragments=[b['id'] for b in owned],rows=len({b['row'] for b in owned}),local_labels=True))
        y=y-track_gap+row_gap
    elif data.get('compact_groups'):
        # Keep fixed calendar footprints while reusing whole family pockets.
        # Titles are part of the declared group envelope, never added afterwards.
        placed=[]
        for g,gl in zip(groups,layouts):
            owned=[b for b in boxes if b['group']==g['id']]
            left=min(b['x'] for b in owned)
            right=max(max(b['x']+b['w'] for b in owned),left+positive(g.get('label_width',0),'label_width',True))
            if right>width:raise ValueError(f'{g["id"]} title envelope exceeds the canvas')
            candidates=sorted({top,*[p['y']+p['h']+row_gap for p in placed]})
            for candidate in candidates:
                if all(right+gap<=p['x'] or left>=p['x']+p['w']+gap or candidate+gl['h']+row_gap<=p['y'] or candidate>=p['y']+p['h']+row_gap for p in placed):
                    break
            delta=candidate-gl['y']
            for b in owned:b['y']+=delta
            for r in rows:
                if r['group']==g['id']:r['y']+=delta
            gl.update(x=left,y=candidate,w=right-left)
            placed.append(gl)
        y=max(g['y']+g['h'] for g in layouts)+row_gap
    layout=dict(version=1,mode='numeric',width=width,height=y-row_gap,boxes=boxes,rows=rows,groups=layouts,record_count=len(records),group_count=len(groups),row_count=len(rows),multi_record_rows=sum(len(r['members'])>1 for r in rows),cross_group_rows=sum(len({b['group'] for b in boxes if b['row']==r['id']})>1 for r in rows))
    return dict(source=data,layout=layout)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    try:result=pack(json.loads(args.input.read_text(encoding='utf-8-sig')))
    except (ValueError,KeyError,TypeError) as e:p.exit(2,f'Cannot pack shared rows: {e}\n')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:result['layout'][k] for k in ['record_count','group_count','row_count','multi_record_rows','width','height']}))


if __name__=='__main__':main()
