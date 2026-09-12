#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure dated prose and contextual illustrations without moving their year."""

from render_chart import number, require, text_width, wrap


def paragraph_lines(event,width,size,small):
    """Wrap a bold lead-in and explanatory text as a single readable paragraph."""
    label=str(event['label']).strip()
    if label and label[-1] not in '.?!:':label+='.'
    tokens=[(word,size,True,'heading') for word in label.split()]
    tokens.extend((word,small,False,'detail') for word in str(event.get('detail','')).split())
    lines=[];runs=[];used=0
    def flush():
        if not runs:return
        font=max(run['font'] for run in runs)
        lines.append(dict(text=''.join(run['text'] for run in runs),font=font,bold=False,role='paragraph',runs=[dict(run) for run in runs],width=used))
    for word,font,bold,role in tokens:
        require(text_width(word,font,bold)<=width,f'Word {word!r} exceeds the paragraph width.')
        text=(' ' if runs else '')+word;advance=text_width(text,font,bold)
        if runs and used+advance>width:
            flush();runs=[];used=0;text=word;advance=text_width(text,font,bold)
        if runs and runs[-1]['role']==role:runs[-1]['text']+=text
        else:runs.append(dict(text=text,font=font,bold=bold,role=role))
        used+=advance
    flush()
    return lines


def event_content(event, width):
    """Return text lines and a full art viewport relative to the event's date."""
    size=number(event.get('size',10.5),'event.size')
    small=number(event.get('detail_size',size*.88),'event.detail_size')
    require(size>0 and small>0,'Event type sizes must be positive.')
    has_art=bool(event.get('icon'));position=event.get('art_position','below')
    require(position!='auto','Resolve art_position auto with pack_timeline_events.py before rendering.')
    require(position in ('above','below','left','right'),'Event art_position must be above, below, left or right.')
    require(has_art or 'art_position' not in event,'art_position requires an event illustration.')
    aw=number(event.get('art_width',event.get('art_size',56)),'event.art_width') if has_art else 0
    ah=number(event.get('art_height',event.get('art_size',56)),'event.art_height') if has_art else 0
    require(not has_art or (0<aw<=width and ah>0),'Event artwork must fit its declared width and have positive dimensions.')
    side=has_art and position in ('left','right');gap=8 if side else 5
    text_width_available=width-aw-gap if side else width
    require(text_width_available>0,'An illustration beside the note must leave positive text width.')
    tx=aw+gap if has_art and position=='left' else 0
    lines=[];y=0
    layout=event.get('text_layout','stacked')
    require(layout in ('stacked','paragraph'),'Event text_layout must be stacked or paragraph.')
    if layout=='paragraph':
        for line in paragraph_lines(event,text_width_available,size,small):
            line.update(x=tx,y=y,box=(tx,y,line.pop('width'),line['font']*1.18));lines.append(line)
            y+=line['font']*1.18
    else:
        names=wrap(event['label'],text_width_available,size,True)
        details=wrap(event.get('detail',''),text_width_available,small)
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
