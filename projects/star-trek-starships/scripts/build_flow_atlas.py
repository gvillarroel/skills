#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Prototype full-context calendar cards in globally reusable chronological tracks."""
from pathlib import Path
import base64
import hashlib
import json
import math
import shutil
import heapq
from PIL import Image
import build_space_atlas as draw
from build_lineages_atlas import GROUPS,ASSET_IDS

PROJECT=Path(__file__).resolve().parents[1];ROOT=PROJECT.parents[1]
OUT=PROJECT/'artifacts/flow-edition';DATA=draw.DATA;BY=draw.BY
W=6400;M=65;TOP=460;LABEL_W=430
SEGMENTS=[
 dict(id='early',start=2060,end=2165,x=150,width=960,label='EARTH’S FIRST WARP AGE',ticks=[2060,2080,2100,2120,2140,2160]),
 dict(id='classic',start=2240,end=2300,x=1170,width=1170,label='THE EXPLORATION AGE',ticks=list(range(2240,2301,10))),
 dict(id='pre-tng',start=2320,end=2360,x=2400,width=460,label='A NEW GENERATION',ticks=[2320,2340]),
 dict(id='dense-modern',start=2360,end=2385,x=2860,width=1530,label='2360–2385 · EXPANDED DETAIL',ticks=list(range(2360,2385,5))),
 dict(id='late-modern',start=2385,end=2405,x=4390,width=1160,label='LATER VOYAGES',ticks=[2385,2390,2395,2400,2405]),
 dict(id='future',start=3188,end=3200,x=5610,width=590,label='32ND CENTURY',ticks=[3188,3190,3195,3200])]


def px(year):
    for s in SEGMENTS:
        if s['start']<=year<=s['end']:return s['x']+(year-s['start'])/(s['end']-s['start'])*s['width']
    raise ValueError(f'Year outside calendar windows: {year}')
parts=draw.parts
text,rect,path,circle,symbol,wake=draw.text,draw.rect,draw.path,draw.circle,draw.symbol,draw.wake
INK,MUTED,CYAN,PAPER=draw.INK,draw.MUTED,draw.CYAN,draw.PAPER
FAMILY={sid:g[0] for g in GROUPS for sid in g[4]}
FAMILY_NAME={g[0]:g[1] for g in GROUPS}
FAMILY_COLORS=dict(zip((g[0] for g in GROUPS),['#E9D394','#93C7F0','#E8BE8C','#82D0DC','#B8ADD8','#9ABBDD','#E9A98C','#93D5B8','#C7CB90','#EA947E','#B8CE8C','#D0D16E','#BCA9DF']))
FAMILY_CODES={g[0]:f'{i:02}' for i,g in enumerate(GROUPS,1)}
cards=[];marks=[];artwork=[];fragments=[]


def lines(value,size=22,kind='body'):return draw.wrap(value,LABEL_W-20,size,kind)


def card(s,secondary=None,suffix=''):
    special=secondary is not None
    years=sorted(set(p['year'] for p in secondary)) if special else sorted(set(s['observations']+(s['construction'] or [])+([s['launch']] if s['launch'] is not None else [])))
    uncertain=s.get('uncertain_range') if not special else None
    if uncertain:years=uncertain
    first,last=years[0],years[-1];start,end=px(first),px(last)
    tx=max(M+5,start+8 if end-start>LABEL_W+35 else end-LABEL_W-16)
    name=lines(s['name'],32,'display')
    meta=[] if special else lines('['+FAMILY_CODES[FAMILY[s['id']]]+'] '+s['design']+' · '+s['registry'],19)
    launch=('B' if s['launch_kind']=='built' else 'C' if s['launch_kind']=='commission' else 'L')+' '+(str(s['launch']) if s['launch'] is not None else '—')
    if s['construction'] and s['launch_kind']!='built':launch+=' · building '+', '.join(map(str,s['construction']))
    dates=lines(' · '.join(p['label'] for p in secondary) if special else launch+' | Seen '+('c. '+str(first)+'–'+str(last) if uncertain else ', '.join(map(str,s['observations']))),19,'bold')
    note=[] if special else lines(s['note'],21)
    credit=lines('Same physical hull.' if special else s['credit']+f' [{draw.source_numbers[s["source"]]}]',16)
    title_h=len(name)*37+9
    meta_y=28+title_h+22;date_y=meta_y+len(meta)*23+2
    note_y=date_y+len(dates)*23+12
    credit_y=note_y+len(note)*25+9
    height=math.ceil(credit_y+len(credit)*20+8)
    has_art=not special and s['id'] in ASSET_IDS
    family_label=('OTHER STATE · ' if special else '')+FAMILY_NAME[FAMILY[s['id']]]
    pieces=[dict(x=start-10,y=-6,w=end-start+20,h=28),
            dict(x=tx-5,y=23,w=LABEL_W+10,h=height-23)]
    if has_art:pieces.append(dict(x=end+10,y=-130,w=184,h=122))
    return dict(id=s['id']+suffix,owner=s['id'],family=FAMILY[s['id']],secondary=special,pieces=pieces,
                years=years,points=secondary or [],uncertain=uncertain,first=first,last=last,
                start=start,end=end,tx=tx,name=name,meta=meta,dates=dates,note=note,credit=credit,
                title_h=title_h,meta_y=meta_y,date_y=date_y,note_y=note_y,credit_y=credit_y,
                height=height,x0=min(start-9,tx-5),x1=max(end+9,tx+LABEL_W+4,end+194 if has_art else 0),has_art=has_art)


def pack_shapes(records,order):
    """Pack actual occupied pieces in y; preserve every fixed x and semantic owner."""
    placed=[];boxes=[];selected=[];gap=18;quantum=8
    group_order={g[0]:i for i,g in enumerate(GROUPS)};family_ys={}
    ordering=sorted(records,key=(lambda c:(group_order[c['family']],c['secondary'],c['first'],c['id'])) if order=='families' else (lambda c:(c['first'],-c['height'],c['id'])) if order=='time' else (lambda c:(-c['height'],c['first'],c['id'])) if order=='height' else (lambda c:(-sum(p['w']*p['h'] for p in c['pieces']),c['first'])))
    for original in ordering:
        options=[]
        positions={original['tx'],original['end']+24,max(M+5,original['start']-LABEL_W-16),original['start']+24}
        if original['end']-original['start']>LABEL_W:positions.add((original['end']+original['start']-LABEL_W)/2)
        for tx in sorted(positions):
            if tx+original['pieces'][1]['w']>W-M:continue
            c=dict(original,tx=tx,pieces=[dict(p) for p in original['pieces']])
            c['pieces'][1]['x']=tx-5
            # The short leader belongs to the occupied footprint, not to the time wake.
            anchor=c['end'];port=max(tx+12,min(tx+LABEL_W-12,anchor))
            c['pieces'].append(dict(x=min(anchor,port)-3,y=9,w=max(6,abs(anchor-port)+6),h=19))
            c['x0']=min(p['x'] for p in c['pieces']);c['x1']=max(p['x']+p['w'] for p in c['pieces'])
            minimum=TOP+16-min(p['y'] for p in c['pieces'])
            checks=[];candidates={math.ceil(minimum/quantum)*quantum}
            for p in c['pieces']:
                for previous in placed:
                    if p['x']<previous['x']+previous['w']+gap and p['x']+p['w']+gap>previous['x']:
                        checks.append((p,previous))
                        candidates.add(math.ceil((previous['y']+previous['h']+gap-p['y'])/quantum)*quantum)
            chosen=None;preferred=family_ys.get(c['family'],[]) if order=='families' else []
            candidates.update(preferred)
            for y in sorted((v for v in candidates if v>=minimum),key=lambda v:(v+(0 if v in preferred else 70),v)):
                if all(y+p['y']>=prev['y']+prev['h']+gap or y+p['y']+p['h']+gap<=prev['y'] for p,prev in checks):chosen=y;break
            if chosen is not None:options.append((chosen+c['height']+(0 if chosen in preferred else 70),abs(tx-original['tx']),chosen,c))
        assert options,original['id']
        _,_,chosen,c=min(options,key=lambda o:o[:3]);selected.append(c)
        boxes.append(dict(id=c['id'],group=c['family'],x=c['x0'],y=chosen,w=c['x1']-c['x0'],h=c['height']))
        placed.extend(dict(x=p['x'],y=chosen+p['y'],w=p['w'],h=p['h'],owner=c['id']) for p in c['pieces'])
        family_ys.setdefault(c['family'],[]).append(chosen)
    ys=sorted(set(b['y'] for b in boxes));rows=[dict(id=str(y),y=y,h=max(b['h'] for b in boxes if b['y']==y),members=[b['id'] for b in boxes if b['y']==y]) for y in ys]
    return dict(strategy=order,boxes=boxes,rows=rows,pieces=placed,selected=selected,height=max(p['y']+p['h'] for p in placed),row_count=len(rows),multi_record_rows=sum(len(r['members'])>1 for r in rows))


def route_relation(a,b,obstacles):
    """Route through actual free corridors, with bends penalized independently."""
    margin=11
    def free(p,q):
        if abs(p[0]-q[0])<.01:
            return all(not(r['x']-.5<p[0]<r['x']+r['w']+.5 and min(p[1],q[1])<r['y']+r['h']+.5 and max(p[1],q[1])>r['y']-.5) for r in obstacles)
        return all(not(r['y']-.5<p[1]<r['y']+r['h']+.5 and min(p[0],q[0])<r['x']+r['w']+.5 and max(p[0],q[0])>r['x']-.5) for r in obstacles)
    xs=sorted({a[0],b[0],M-20,W-M+20,*[max(20,min(W-20,q)) for r in obstacles for q in (r['x']-margin,r['x']+r['w']+margin)]})
    ys=sorted({a[1],b[1],TOP+2,*[max(TOP+2,q) for r in obstacles for q in (r['y']-margin,r['y']+r['h']+margin)]})
    start=(xs.index(a[0]),ys.index(a[1]),2);goal=(xs.index(b[0]),ys.index(b[1]))
    queue=[(0,0,start)];dist={start:0};came={};last=None;cache={}
    while queue:
        _,cost,state=heapq.heappop(queue)
        if cost!=dist.get(state):continue
        x,y,direction=state
        if (x,y)==goal:last=state;break
        for dx,dy,d in [(1,0,0),(-1,0,0),(0,1,1),(0,-1,1)]:
            xx,yy=x+dx,y+dy
            if not(0<=xx<len(xs) and 0<=yy<len(ys)):continue
            p,q=(xs[x],ys[y]),(xs[xx],ys[yy]);key=tuple(sorted((p,q)))
            if key not in cache:cache[key]=free(p,q)
            if not cache[key]:continue
            added=abs(p[0]-q[0])+abs(p[1]-q[1])+(45 if direction not in (2,d) else 0)
            nxt=(xx,yy,d);nd=cost+added
            if nd<dist.get(nxt,float('inf')):
                dist[nxt]=nd;came[nxt]=state
                heapq.heappush(queue,(nd+abs(q[0]-b[0])+abs(q[1]-b[1]),nd,nxt))
    if last is None:raise ValueError('No relationship corridor')
    points=[]
    while True:
        points.append((xs[last[0]],ys[last[1]]))
        if last==start:break
        last=came[last]
    points.reverse();simple=[points[0]]
    for i,p in enumerate(points[1:-1],1):
        a0,a1=points[i-1],points[i+1]
        if not(a0[0]==p[0]==a1[0] or a0[1]==p[1]==a1[1]):simple.append(p)
    simple.append(points[-1]);return simple


def paint(s,c,b):
    y=b['y'];col=FAMILY_COLORS[c['family']];kind='continuation' if c['secondary'] else 'record'
    parts.append(f'<g id="{kind}-{c["id"]}" class="{kind}" data-id="{s["id"]}" data-fragment="{c["id"]}" data-family="{c["family"]}" data-operator="{s["operator"]}" data-source="{draw.esc(DATA["sources"][s["source"]]["url"])}" tabindex="0" role="button" aria-label="{draw.esc(s["name"])}">')
    hit=''.join(f'M{p["x"]} {y+p["y"]}h{p["w"]}v{p["h"]}h{-p["w"]}Z' for p in c['pieces'])
    parts.append(f'<path d="{hit}" fill="transparent" class="hit-area"/>')
    yy=y+12
    if c['uncertain']:
        parts.append(f'<g class="uncertain-span" data-start="{c["first"]}" data-end="{c["last"]}">')
        rect(c['start'],yy-6,c['end']-c['start'],12,'url(#uncertain)',f'stroke="{col}" stroke-width="1"');parts.append('</g>')
    elif not c['secondary']:
        if s['service']:wake(px(s['service'][0]),px(s['service'][1]),yy,col,True,s['id'],*s['service'])
        elif len(c['years'])>1:wake(c['start'],c['end'],yy,col,False,s['id'],c['first'],c['last'])
    if c['has_art']:
        asset=ASSET_IDS[s['id']];ax,ay,aw,ah=c['end']+14,y-126,174,108
        parts.append(f'<use class="ship-art" href="#art-{asset}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" style="mix-blend-mode:screen" data-ship="{s["id"]}" data-end-year="{c["last"]}"/>')
        artwork.append(dict(id=asset,ship=s['id'],x=ax,y=ay,w=aw,h=ah,year=c['last']))
    pairs=[]
    if not c['uncertain']:
        if c['secondary']:pairs=[(p['year'],p['kind']) for p in c['points']]
        else:
            for t in c['years']:
                event=s['launch_kind'] if t==s['launch'] else s['endpoint'] if t==s['observations'][-1] and s['endpoint'] else 'built' if t in (s['construction'] or []) else 'active'
                if t==s['launch']==s['observations'][-1] and s['endpoint']:event='launch'
                pairs.append((t,event))
            if s['endpoint'] and s['launch']==s['observations'][-1]:pairs.append((c['last'],s['endpoint']))
    for i,(year,event) in enumerate(pairs):
        symbol(event,px(year),yy+(18 if i and year==pairs[i-1][0] else 0),col,5,extra=f'data-year="{year}" data-kind="{event}"')
        marks.append(dict(owner=s['id'],fragment=c['id'],year=year,kind=event,x=px(year)))
    tx=c['tx'];port=max(tx+12,min(tx+LABEL_W-12,c['end']))
    path(f'M{c["end"]} {yy}V{y+20}H{port}V{y+27}',col,1.4,'opacity=".7" class="annotation-leader"')
    rect(tx,y+23,LABEL_W,b['h']-23,'#091525','',3)
    rect(tx,y+28,LABEL_W,c['title_h'],col,'opacity=".92"' if s['important'] and not c['secondary'] else 'opacity=".17"',3)
    for i,line in enumerate(c['name']):text(line,tx+10,y+61+i*37,32,'display','#08121F' if s['important'] and not c['secondary'] else col,role='ship-name')
    for key,base,size,leading,color,font in [('meta',c['meta_y'],19,23,MUTED,'body'),('dates',c['date_y'],19,23,col,'bold'),('note',c['note_y'],21,25,INK,'body'),('credit',c['credit_y'],16,20,MUTED,'body')]:
        for i,line in enumerate(c[key]):text(line,tx+10,y+base+i*leading,size,font,color,role=key)
    parts.append('</g>')
    fragments.append(dict(id=c['id'],owner=s['id'],secondary=c['secondary'],x=b['x'],y=y,w=b['w'],h=b['h']))


def main():
    for folder in ['svgs','images','documents','viewer','data','reviews','archives']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    for s in DATA['ships']:
        cards.append(card(s))
        for i,seg in enumerate(SEGMENTS):
            points=[p for p in s['special'] if seg['start']<=p['year']<=seg['end']]
            if points:cards.append(card(s,points,f'-state-{i}'))
    brief=dict(mode='compound-calendar-prototype',width=W,top=TOP,gap=18,
               contract='Date anchors stay fixed; measured label variants may change sides. Compound shapes reserve all painted marks, labels, leaders and artwork.',
               records=[{k:c[k] for k in ['id','owner','family','first','last','start','end','height']} for c in cards])
    candidates=[pack_shapes(cards,order) for order in ['time','height','area','families']]
    layout=candidates[-1];packed=dict(source=brief,layout=layout)
    (OUT/'reviews/packing-candidates.json').write_text(json.dumps([{k:v for k,v in c.items() if k not in {'boxes','rows','pieces','selected'}} for c in candidates],indent=2)+'\n')
    boxes={b['id']:b for b in layout['boxes']}
    cards[:]=layout['selected']
    # Colored labels and source prose create density, while every dated mark stays fixed.
    text('STAR TREK',M,120,115,'display')
    text('THE FLEET THROUGH TIME',M+640,120,104,'display',CYAN)
    text('79 spacecraft · construction, voyages & fate · a shared horizontal calendar',M,180,32)
    text('Full source notes beside every vessel. Color and bracketed numbers identify ship families.',M,226,26,fill=MUTED)
    text('L = launched · C = commissioned · B = built · — = unstated · Seen = dated evidence',M,270,24,'body',MUTED)
    text('Each window is linear at its labeled scale. // = omitted years. Every year aligns across the page.',W-M,226,24,'body',MUTED,'end')
    text('Solid wakes = supported service · dashed wakes = dated evidence · thin elbows = label leaders',W-M,270,24,'body',MUTED,'end')
    for i,g in enumerate(GROUPS):
        x=M+(i%7)*885;y=323+(i//7)*38;col=FAMILY_COLORS[g[0]]
        text(FAMILY_CODES[g[0]]+'  '+g[1],x,y,23,'display',col,role='family-key')
    for seg in SEGMENTS:
        rect(seg['x'],TOP-46,seg['width'],36,'#1C3C54','',3)
        text(seg['label'],seg['x']+8,TOP-19,21,'display',CYAN)
        for t in seg['ticks']:
            text(t,px(t),TOP-56,22,'bold',MUTED,'middle',role='axis-year')
            path(f'M{px(t)} {TOP+2}V{layout["height"]+10}','#38526B',1,'opacity=".6"')
    for a,b in zip(SEGMENTS,SEGMENTS[1:]):
        if b['start']>a['end']:text('//',(a['x']+a['width']+b['x'])/2,TOP-20,26,'bold','#F6C78C','middle',role='axis-break')
    by_card={c['id']:c for c in cards};routed=[]
    for r in DATA['relations']:
        if r['source']==r['target']:continue
        c,d=by_card[r['source']],by_card[r['target']];a,b=boxes[c['id']],boxes[d['id']]
        start=(c['tx']+LABEL_W+3,a['y']+28+c['title_h']/2)
        end=(d['tx']-3,b['y']+28+d['title_h']/2)
        obstacles=[p for p in layout['pieces'] if p['owner'] not in (c['id'],d['id'])]
        points=route_relation(start,end,obstacles)
        color=FAMILY_COLORS[c['family']]
        command='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)
        parts.append(f'<g class="typed-link" data-source="{r["source"]}" data-target="{r["target"]}" data-kind="{r["kind"]}">')
        path(command,'#020711',7,'opacity=".9"')
        path(command,color,2.8,'opacity=".85"'+(' stroke-dasharray="5 6"' if r['kind']!='name-succession' else ''))
        circle(*end,4.5,color);parts.append('</g>')
        routed.append(dict(**r,points=points))
    for c in cards:paint(BY[c['owner']],c,boxes[c['id']])
    (OUT/'reviews/relationship-routes.json').write_text(json.dumps(routed,indent=2)+'\n')
    footer=layout['height']+84
    text('HOW THESE SHIPS ARE RELATED',M,footer,38,'display',CYAN)
    for i,r in enumerate(DATA['relations']):
        label=BY[r['source']]['name']+' → '+BY[r['target']]['name']+' · '+r['kind'].replace('-',' ')
        if r['source']==r['target']:label=BY[r['source']]['name']+f' · same hull renamed {r["year"]}'
        parts.append(f'<g class="typed-relation" data-source="{r["source"]}" data-target="{r["target"]}" data-kind="{r["kind"]}">')
        text(label,M+(i%3)*2100,footer+52+(i//3)*35,21,fill=MUTED,role='relation-caption');parts.append('</g>')
    text('Lines between nameplates show the relationships indexed above. Solid = name succession; dashed = the other typed links. Adjacency alone carries no relationship.',M,footer+333,22,fill=MUTED)
    text('Independent educational fan atlas · Prime continuity · 12 September 2026 · Illustrations identify design families; hull markings and physical sizes are illustrative.',M,footer+369,21,fill=MUTED)
    H=math.ceil(footer+411)
    defs=[f'<style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{base64.b64encode(draw.FONT.read_bytes()).decode()});font-weight:700}}.record,.continuation{{cursor:pointer}}</style>','<filter id="glow" x="-60%" y="-400%" width="220%" height="900%"><feGaussianBlur stdDeviation="4"/></filter>','<pattern id="uncertain" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M-1 1L6 8M2-3L9 4" stroke="#ADC8E3" stroke-width="1.2"/></pattern>']
    for id,file in draw.ASSETS.items():
        im=Image.open(draw.ART/file);iw,ih=im.size
        defs.append(f'<symbol id="art-{id}" viewBox="0 0 {iw} {ih}"><image width="{iw}" height="{ih}" href="data:image/png;base64,{base64.b64encode((draw.ART/file).read_bytes()).decode()}"/></symbol>')
    bg=base64.b64encode((draw.ART/'nebula-background.png').read_bytes()).decode()
    background=f'<rect width="{W}" height="{H}" fill="{PAPER}"/><image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{bg}" opacity=".55"/><rect width="{W}" height="{H}" fill="#030A18" opacity=".70"/>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>Star Trek: the fleet through time</title><desc>Full-context chronological prototype. One shared piecewise-linear calendar x axis; globally reused tracks and source-bound family labels.</desc><defs>{"".join(defs)}</defs>{background}{"".join(parts)}</svg>'
    target=OUT/'svgs/star-trek-starships.svg';target.write_text(svg,encoding='utf-8')
    label_boxes=[dict(id=c['id'],x=c['tx'],y=boxes[c['id']]['y']+23,w=LABEL_W,h=c['height']-23) for c in cards if not c['secondary']]
    regions=[]
    for g in GROUPS:
        own=[b for b in label_boxes if b['id'] in g[4]];x=min(b['x'] for b in own);y=min(b['y'] for b in own)
        regions.append(dict(id=g[0],title=g[1].title(),x=x,y=y,w=max(b['x']+b['w'] for b in own)-x,h=max(b['y']+b['h'] for b in own)-y))
    final=dict(width=W,height=H,boxes=label_boxes,fragments=fragments,regions=regions,anchors=marks,illustrations=artwork,segments=SEGMENTS,edition='flow',record_count=79,row_count=layout['row_count'],multi_record_tracks=layout['multi_record_rows'],source_sha256=hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (OUT/'reviews/layout.json').write_text(json.dumps(final,indent=2)+'\n')
    (OUT/'reviews/shared-row-layout.json').write_text(json.dumps(packed,indent=2)+'\n')
    for rel in ['data/ships.json','data/ships.csv','documents/sources.html','documents/font-license.txt']:shutil.copyfile(PROJECT/'artifacts'/rel,OUT/rel)
    template=(PROJECT/'scripts/viewer.html').read_text(encoding='utf-8').replace('</head>','<style>'+(PROJECT/'scripts/space-viewer.css').read_text()+'</style></head>')
    template=template.replace('</head>','<style>.continuation.dim{opacity:.17}.continuation.selected .hit-area{fill:#235b8733;stroke:#74dcff;stroke-width:2}.continuation:focus .hit-area{stroke:#74dcff;stroke-width:2}</style></head>')
    template=template.replace('Starships Through Time','The Fleet Through Time').replace('Starships<br>through time','The fleet<br>through time')
    template=template.replace("querySelectorAll('.record')","querySelectorAll('.record,.continuation')").replace('Each chapter has its own linear year scale.','Every year has the same x coordinate across the page; labeled axis windows have different scales. Color identifies ship families.')
    template=template.replace('Jump to a chapter','Jump to a ship family').replace('Choose a chapter','Choose a ship family').replace("s.observations.join(' '),s.qualifier","s.observations.join(' '),s.special.map(p=>p.year+' '+p.label).join(' '),s.qualifier")
    template=template.replace('Math.max(.12,','Math.max(.04,')
    shutil.copyfile(PROJECT/'design/image-generation.json',OUT/'data/image-generation.json')
    template=template.replace('@@SVG@@',svg).replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')).replace('@@LAYOUT@@',json.dumps(final))
    (OUT/'viewer/index.html').write_text(template,encoding='utf-8')
    print(json.dumps(dict(records=79,full_notes=79,strategy=layout['strategy'],baselines=layout['row_count'],shared_baselines=layout['multi_record_rows'],maximum_fragments_per_baseline=max(len(r['members']) for r in layout['rows']),size=[W,H])))


if __name__=='__main__':main()
