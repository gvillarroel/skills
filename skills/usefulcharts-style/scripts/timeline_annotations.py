#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure dated prose and contextual illustrations without moving their year."""

from render_chart import number, require, text_width, wrap


def event_content(event, width):
    """Return text lines and a full art viewport relative to the event's date."""
    size=number(event.get('size',10.5),'event.size')
    small=number(event.get('detail_size',size*.88),'event.detail_size')
    require(size>0 and small>0,'Event type sizes must be positive.')
    has_art=bool(event.get('icon'));position=event.get('art_position','below')
    require(position in ('above','below','left','right'),'Event art_position must be above, below, left or right.')
    require(has_art or 'art_position' not in event,'art_position requires an event illustration.')
    aw=number(event.get('art_width',event.get('art_size',56)),'event.art_width') if has_art else 0
    ah=number(event.get('art_height',event.get('art_size',56)),'event.art_height') if has_art else 0
    require(not has_art or (0<aw<=width and ah>0),'Event artwork must fit its declared width and have positive dimensions.')
    side=has_art and position in ('left','right');gap=8 if side else 5
    text_width_available=width-aw-gap if side else width
    require(text_width_available>0,'An illustration beside the note must leave positive text width.')
    names=wrap(event['label'],text_width_available,size,True)
    details=wrap(event.get('detail',''),text_width_available,small)
    tx=aw+gap if has_art and position=='left' else 0
    lines=[];y=0
    for values,fs,bold,role in ((names,size,True,'heading'),(details,small,False,'detail')):
        for value in values:
            lines.append(dict(text=value,x=tx,y=y,font=fs,bold=bold,role=role,box=(tx,y,text_width(value,fs,bold),fs*1.18)))
            y+=fs*1.18
    art=None
    if has_art:
        if position=='below':art=((width-aw)/2,y+gap,aw,ah)
        elif position=='above':art=((width-aw)/2,-ah-gap,aw,ah)
        elif position=='left':art=(0,0,aw,ah)
        else:art=(width-aw,0,aw,ah)
    boxes=[line['box'] for line in lines]+([art] if art else [])
    require(boxes,'Every event needs visible content.')
    return dict(lines=lines,art=art,boxes=boxes,top=min(b[1] for b in boxes),bottom=max(b[1]+b[3] for b in boxes),line_count=len(lines))
