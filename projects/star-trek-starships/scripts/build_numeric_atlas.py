#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Build a dense fleet chronology with a shared, piecewise-linear calendar x axis."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import math
import shutil
from PIL import Image
import build_space_atlas as draw
from build_lineages_atlas import GROUPS,ASSET_IDS

PROJECT=Path(__file__).resolve().parents[1];ROOT=PROJECT.parents[1];OUT=PROJECT/'artifacts/numeric-edition'
DATA=draw.DATA;BY=draw.BY;W,M=5200,70
INK,MUTED,CYAN,PAPER,RULE=draw.INK,draw.MUTED,draw.CYAN,draw.PAPER,draw.RULE
parts=draw.parts
text,para,rect,path,circle,symbol,wake=draw.text,draw.para,draw.rect,draw.path,draw.circle,draw.symbol,draw.wake
SEGMENTS=[
 dict(id='early',start=2060,end=2165,x=300,width=800,label='EARTH’S FIRST WARP AGE',ticks=[2060,2080,2100,2120,2140,2160]),
 dict(id='classic',start=2240,end=2300,x=1170,width=1020,label='THE EXPLORATION AGE',ticks=list(range(2240,2301,10))),
 dict(id='pre-tng',start=2320,end=2360,x=2260,width=320,label='THE NEXT GENERATION',ticks=[2320,2340]),
 dict(id='dense-modern',start=2360,end=2385,x=2580,width=1750,label='2360–2385 · EXPANDED DETAIL',ticks=list(range(2360,2385,5))),
 dict(id='late-modern',start=2385,end=2405,x=4330,width=450,label='LATER VOYAGES',ticks=[2385,2395,2405]),
 dict(id='future',start=3188,end=3200,x=4850,width=280,label='32ND C.',ticks=[3188,3200])]
cards={};artwork=[];marks=[];drawn=[];fragments=[]


def px(year):
    for s in SEGMENTS:
        if s['start']<=year<=s['end']:return s['x']+(year-s['start'])/(s['end']-s['start'])*s['width']
    raise ValueError(f'Year outside the declared calendar windows: {year}')


def short_design(s):
    return s['design'].replace('-class','').replace('32nd-century','32nd-c.').replace(' battle cruiser','').replace(' explorer','').replace(' starship','').replace('Klingon Bird-of-Prey','Bird-of-Prey')


def years_label(years):
    if len(years)<2:return str(years[0])
    if all(t//100==years[0]//100 for t in years):return str(years[0])+' · '+' · '.join(f'{t%100:02}' for t in years[1:])
    return ' · '.join(map(str,years))


def measure_card(s,points=None,suffix=''):
    secondary=points is not None
    id=s['id']+suffix
    points=points or []
    years=sorted(set(q['year'] for q in points)) if secondary else sorted(set(s['observations']+(s['construction'] or [])+([s['launch']] if s['launch'] is not None else [])))
    uncertain=s.get('uncertain_range') if not secondary else None
    if uncertain:years=list(uncertain)
    # A future/earlier state is an independent footprint, never a centuries-long filled interval.
    first,last=min(years),max(years)
    a,z=px(first),px(last)
    if secondary and not any(seg['start']<=first<=last<=seg['end'] for seg in SEGMENTS):
        raise ValueError('Split cross-window secondary evidence before placement: '+id)
    has_art=not secondary and s['id'] in ASSET_IDS
    tw=236 if not secondary else 224
    tx=max(M+2, a+8 if z-a>=tw+35 else z-tw-12)
    name=s['name']
    names=draw.wrap(name,tw,25,'display')
    meta=draw.wrap((s['registry']+' · '+short_design(s)) if not secondary else ' · '.join(q['label'] for q in points),tw,15)
    launch=('B' if s['launch_kind']=='built' else 'C' if s['launch_kind']=='commission' else 'L')+' '+(str(s['launch']) if s['launch'] is not None else '—')
    if s['construction'] and s['launch_kind']!='built':launch+=' · building '+', '.join(map(str,s['construction']))
    if secondary:date='[Same hull]'
    elif uncertain:date=launch+' | '+('c. 2144–45' if s['id']=='nx-delta' else '3190s · disputed')
    else:date=launch+' | '+years_label(years)
    dates=draw.wrap(date,tw,16,'bold')
    meta_y=51+(len(names)-1)*32+21
    date_y=meta_y+(len(meta)-1)*18+22
    height=math.ceil(date_y+(len(dates)-1)*19+12)
    x0=min(a-8,tx-4);x1=max(z+8,tx+tw+4,z+118 if has_art else z+8)
    return dict(id=id,owner=s['id'],secondary=secondary,years=years,points=points,uncertain=uncertain,first=first,last=last,a=a,z=z,tx=tx,tw=tw,names=names,meta=meta,dates=dates,meta_y=meta_y,date_y=date_y,height=height,x0=x0,x1=x1,has_art=has_art)


def paint(s,c,b):
    y=b['y'];col=draw.COLORS[s['operator']];id=c['id'];cls='continuation' if c['secondary'] else 'record'
    parts.append(f'<g id="{cls}-{id}" class="{cls}" data-id="{s["id"]}" data-fragment="{id}" data-source="{draw.esc(DATA["sources"][s["source"]]["url"])}" data-operator="{s["operator"]}" tabindex="0" role="button" aria-label="{draw.esc(s["name"]+". "+s["note"])}">')
    rect(b['x'],y,b['w'],b['h'],'transparent','class="hit-area"',4)
    yy=y+10
    if c['uncertain']:
        a,z=c['uncertain'];parts.append(f'<g class="uncertain-span" data-start="{a}" data-end="{z}">')
        rect(px(a),yy-6,px(z)-px(a),12,'url(#uncertain)',f'stroke="{col}" stroke-width="1"');parts.append('</g>')
    elif not c['secondary']:
        if s['service']:wake(px(s['service'][0]),px(s['service'][1]),yy,col,True,s['id'],*s['service'])
        elif len(c['years'])>1:wake(c['a'],c['z'],yy,col,False,s['id'],c['first'],c['last'])
    if c['has_art']:
        ax,ay,aw,ah=c['z']+12,y-7,100,62;asset=ASSET_IDS[s['id']]
        parts.append(f'<use class="ship-art" href="#art-{asset}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" style="mix-blend-mode:screen" data-ship="{s["id"]}" data-end-year="{c["last"]}"/>')
        artwork.append(dict(id=asset,ship=s['id'],x=ax,y=ay,w=aw,h=ah,year=c['last']))
    if not c['uncertain']:
        pairs=[(q['year'],q['kind']) for q in c['points']] if c['secondary'] else []
        if not c['secondary']:
            for t in c['years']:
                kind=s['launch_kind'] if t==s['launch'] else s['endpoint'] if t==s['observations'][-1] and s['endpoint'] else 'built' if t in (s['construction'] or []) else 'active'
                if t==s['launch'] and s['endpoint'] and t==s['observations'][-1]:kind='launch'
                pairs.append((t,kind))
            if s['endpoint'] and s['launch']==s['observations'][-1]:pairs.append((c['last'],s['endpoint']))
        for i,(t,kind) in enumerate(pairs):
            offset=17 if i and t==pairs[i-1][0] else 0
            symbol(kind,px(t),yy+offset,col,4.2,extra=f'data-year="{t}" data-kind="{kind}"')
            marks.append(dict(owner=s['id'],fragment=id,year=t,kind=kind,x=px(t)))
    for k,line in enumerate(c['names']):text(line,c['tx'],y+51+k*32,25,'display',col if s['important'] else INK,role='ship-name')
    for k,line in enumerate(c['meta']):text(line,c['tx'],y+c['meta_y']+k*18,15,fill=MUTED,role='class-detail' if not c['secondary'] else 'other-date')
    for k,line in enumerate(c['dates']):text(line,c['tx'],y+c['date_y']+k*19,16,'bold',col,role='use-label')
    parts.append('</g>')
    fragments.append(dict(id=id,owner=s['id'],secondary=c['secondary'],x=b['x'],y=y,w=b['w'],h=b['h']))
    if not c['secondary']:drawn.append(s['id'])


def header():
    text('STAR TREK',M,114,108,'display')
    text('FLEET LINES THROUGH TIME',M+610,114,88,'display',CYAN)
    text('79 spacecraft • shared family rows • one calendar axis',M,174,31)
    lx=1750
    for operator,col in draw.COLORS.items():
        circle(lx,166,5,col);text(operator,lx+14,173,19,fill=col)
        lx+=draw.measure(operator,19)+46
    text('X = YEAR',W-M,97,54,'display',CYAN,'end')
    text('Every year aligns vertically across all families.',W-M,142,24,'body',MUTED,'end')
    text('Calendar windows are linear. The 2360–2385 window is expanded; // marks omitted years.',M,235,24,fill=MUTED)
    text('L = launch   C = commissioned   B = built   — = unstated   •   Later states retain the same ship identity.',M,275,23,fill=MUTED)
    wake(2600,2750,224,CYAN,True);text('Supported service',2770,231,22)
    wake(3070,3220,224,CYAN);text('Dated evidence',3240,231,22)
    symbol('launch',3580,224,CYAN,6);text('Launch / build',3600,231,22)
    symbol('destroyed',3840,224,CYAN,6);text('Loss',3860,231,22)
    symbol('retired',4000,224,CYAN,6);text('Retired / abandoned',4020,231,22)
    text('Names, registry, class and dates on the chart. Full context and sources in the viewer.',W-M,275,23,'body',MUTED,'end')
    return 402


def paint_axis(y,bottom):
    for seg in SEGMENTS:
        x=seg['x'];ww=seg['width']
        rect(x,y-64,ww,45,'#17344A','opacity=".8"',3)
        text(seg['label'],x+12,y-33,23 if ww>300 else 21,'display',CYAN)
        path(f'M{x} {y}H{x+ww}',MUTED,1)
        for t in seg['ticks']:
            xx=px(t);text(t,xx,y-7,18,'bold',MUTED,'middle',role='axis-year')
            path(f'M{xx} {y+6}V{bottom}',RULE,.7,'opacity=".55" class="calendar-grid"')
    for a,b in zip(SEGMENTS,SEGMENTS[1:]):
        if b['start']>a['end']:
            xx=(a['x']+a['width']+b['x'])/2
            text('//',xx,y-6,26,'bold','#F6C78C','middle',role='axis-break')
            text(f'{a["end"]}–{b["start"]}',xx,y-33,13,'body',MUTED,'middle')


def main():
    for folder in ['svgs','images','documents','viewer','data','reviews','archives']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    top=header();groups=[];state_groups=[]
    for id,title,kind,years,ids in GROUPS:
        members=[]
        for rid in ids:
            c=measure_card(BY[rid]);cards[c['id']]=c;members.append(c['id'])
            # Each separate calendar window gets an independent same-hull fragment.
            # This preserves the empty time between sightings for other vessels.
            for i,seg in enumerate(SEGMENTS):
                points=[p for p in BY[rid]['special'] if seg['start']<=p['year']<=seg['end']]
                if points:
                    c=measure_card(BY[rid],points,f'-state-{i}');cards[c['id']]=c
                    state_groups.append(dict(id=c['id'],title='OTHER STATES',kind='Same physical hull',members=[c['id']],header_height=80,label_width=240,title_lines=['OTHER STATES'],kind_lines=['Same physical hull']))
        title_lines=draw.wrap(title,440,30,'display');kind_lines=draw.wrap(kind,440,17)
        header_height=45+len(title_lines)*37+len(kind_lines)*20
        groups.append(dict(id=id,title=title,kind=kind,members=members,header_height=header_height,label_width=440,title_lines=title_lines,kind_lines=kind_lines))
    groups+=state_groups
    brief=dict(mode='numeric',compact_groups=True,width=W,top=top,gap=18,row_gap=22,track_gap=10,groups=groups,records=[{k:c[k] for k in ['id','owner','x0','x1','height']} for c in cards.values()])
    spec=importlib.util.spec_from_file_location('shared_rows',ROOT/'skills/usefulcharts-style/scripts/pack_shared_rows.py');packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    packed=packer.pack(brief);layout=packed['layout'];boxes={b['id']:b for b in layout['boxes']}
    (OUT/'data/shared-row-brief.json').write_text(json.dumps(brief,indent=2)+'\n',encoding='utf-8')
    (OUT/'reviews/shared-row-layout.json').write_text(json.dumps(packed,indent=2)+'\n',encoding='utf-8')
    axis_start=len(parts);paint_axis(top-20,layout['height']+8)
    regions=[]
    for index,(g,gl) in enumerate(zip(groups,layout['groups'])):
        y=gl['y'];hh=gl['h'];gx=gl['x'];gw=gl['w'];regions.append(dict(id=g['id'],title=g['title'].title(),x=gx,y=y,w=gw,h=hh))
        rect(gx-7,y-10,gw+14,hh+20,'#081527',f'opacity="{.36 if index%2==0 else .18}"',7)
        path(f'M{gx} {y}H{gx+gw}',CYAN,1,'opacity=".35"')
        for k,line in enumerate(g['title_lines']):text(line,gx,y+35+k*37,30,'display',CYAN)
        py=y+35+len(g['title_lines'])*37
        for k,line in enumerate(g['kind_lines']):text(line,gx,py+k*20,17,fill=MUTED)
        for id in g['members']:paint(BY[cards[id]['owner']],cards[id],boxes[id])
    # An explicitly non-temporal inset reuses an empty pocket without relocating
    # a single dated mark. Every profile quotes the retained source record.
    inset_y=max(g['y']+g['h'] for g in layout['groups'] if g['x']<1300)+48
    rect(M-12,inset_y-18,1244,1980,'#09182A','stroke="#28506B" stroke-width="1"',8)
    text('DESIGN FILES & IDENTITY LINKS',M+18,inset_y+30,36,'display',CYAN)
    text('Reference inset · positions in this panel do not encode years.',M+18,inset_y+67,20,fill=MUTED)
    py=inset_y+115
    for sid in draw.ASSETS:
        s=BY[sid];asset=ASSET_IDS[sid];col=draw.COLORS[s['operator']]
        ax,ay,aw,ah=M+20,py-26,270,167
        parts.append(f'<g class="design-profile" data-owner="{sid}">')
        parts.append(f'<use class="ship-art" href="#art-{asset}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" style="mix-blend-mode:screen" data-ship="{sid}"/>')
        artwork.append(dict(id=asset,ship=sid,x=ax,y=ay,w=aw,h=ah,year=None,role='reference profile'))
        text(s['name'],M+312,py,30,'display',col)
        text(s['design']+' · '+s['registry'],M+312,py+28,17,fill=MUTED)
        last=para(s['note'],M+312,py+60,872,19,fill=INK,leading=24,role='context-note')
        text(s['credit']+f' [{draw.source_numbers[s["source"]]}]',M+312,last+7,16,fill=MUTED,role='source-credit')
        parts.append('</g>');py+=190
    text('SUCCESSION, REPLACEMENT & RENAMING',M+18,py+12,30,'display',CYAN)
    text('Typed links; these captions do not show service duration.',M+18,py+44,18,fill=MUTED)
    for i,r in enumerate(DATA['relations']):
        x=M+18;y=py+83+i*27
        label=BY[r['source']]['name']+' → '+BY[r['target']]['name']+' · '+r['kind'].replace('-',' ')
        if r['source']==r['target']:label=BY[r['source']]['name']+f' · same hull renamed {r["year"]}'
        parts.append(f'<g class="typed-relation" data-source="{r["source"]}" data-target="{r["target"]}" data-kind="{r["kind"]}">')
        text(label,x,y,18,fill=MUTED,role='relation-caption');parts.append('</g>')
    inset_bottom=max(inset_y+1962,py+83+21*27+20)
    footer=max(layout['height'],inset_bottom)+70
    text('Independent educational fan atlas · 12 September 2026 · Full notes and citations in the companion viewer · Illustrations identify design families, not physical size.',M,footer,19,fill=MUTED)
    H=math.ceil(footer+48)
    regions.append(dict(id='design-files',title='Design profiles and identity links',x=M-12,y=inset_y-18,w=1244,h=inset_bottom-inset_y+18))
    defs=[f'<style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{base64.b64encode(draw.FONT.read_bytes()).decode()});font-weight:700}}.record,.continuation{{cursor:pointer}}text{{font-kerning:normal}}</style>', '<filter id="glow" x="-60%" y="-400%" width="220%" height="900%"><feGaussianBlur stdDeviation="4"/></filter>', '<pattern id="uncertain" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M-1 1L6 8M2-3L9 4" stroke="#ADC8E3" stroke-width="1.2"/></pattern>']
    for id,file in draw.ASSETS.items():
        im=Image.open(draw.ART/file);iw,ih=im.size
        defs.append(f'<symbol id="art-{id}" viewBox="0 0 {iw} {ih}"><image width="{iw}" height="{ih}" href="data:image/png;base64,{base64.b64encode((draw.ART/file).read_bytes()).decode()}"/></symbol>')
    bg=base64.b64encode((draw.ART/'nebula-background.png').read_bytes()).decode()
    background=f'<rect width="{W}" height="{H}" fill="{PAPER}"/><image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{bg}" opacity=".6"/><rect width="{W}" height="{H}" fill="#030A18" opacity=".74"/>'
    meta=dict(edition='numeric shared rows',calendar=SEGMENTS,source='ships.json',display_policy='All identities, registry/class labels and primary date anchors are shown; full narrative notes and source credits remain in the companion evidence ledger. Secondary states are separate same-hull fragments, not continuous service across gaps.')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="poster-title poster-desc"><title id="poster-title">Star Trek: Fleet Lines Through Time</title><desc id="poster-desc">79 spacecraft on one shared calendar x axis. Linear calendar windows use visibly different scales; 2360–2385 is expanded. Family rows reuse space for multiple vessels and later states.</desc><metadata>{draw.esc(json.dumps(meta))}</metadata><defs>{"".join(defs)}</defs>{background}{"".join(parts)}</svg>'
    target=OUT/'svgs/star-trek-starships.svg';target.write_text(svg,encoding='utf-8')
    final=dict(width=W,height=H,boxes=[b for b in layout['boxes'] if not cards[b['id']]['secondary']],fragments=fragments,regions=regions,anchors=marks,illustrations=artwork,segments=SEGMENTS,edition='numeric',record_count=len(drawn),row_count=13,track_count=layout['row_count'],multi_record_tracks=layout['multi_record_rows'],source_sha256=hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (OUT/'reviews/layout.json').write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
    for rel in ['data/ships.json','data/ships.csv','documents/sources.html','documents/font-license.txt']:shutil.copyfile(PROJECT/'artifacts'/rel,OUT/rel)
    shutil.copyfile(PROJECT/'design/image-generation.json',OUT/'data/image-generation.json')
    template=(PROJECT/'scripts/viewer.html').read_text(encoding='utf-8')
    template=template.replace('</head>','<style>'+(PROJECT/'scripts/space-viewer.css').read_text()+'.continuation.dim{opacity:.19}.continuation.selected .hit-area{fill:#235b8733;stroke:#74dcff;stroke-width:2}.continuation:focus .hit-area{stroke:#74dcff;stroke-width:2}</style></head>')
    template=template.replace('Starships Through Time','Fleet Lines Through Time').replace('Starships<br>through time','Fleet lines<br>through time')
    template=template.replace('Construction, launch and documented use across the Prime timeline.','79 spacecraft share 13 family rows. The horizontal axis is calendar time; the same year aligns in every row.')
    template=template.replace('Click a fleet lane for its evidence. Each chapter has its own linear year scale. Dashed spans connect selected sightings; they do not confirm uninterrupted service.','The 2360–2385 window is expanded. Axis cuts mark omitted years. Dashed wakes connect sightings without confirming continuous service. Select a ship or a later-state fragment for the full record.')
    template=template.replace("querySelectorAll('.record')","querySelectorAll('.record,.continuation')")
    template=template.replace('setScale(.72)','setScale(.9)').replace('setScale(.62)','setScale(.55)').replace('Math.max(.12,','Math.max(.07,')
    template=template.replace('Jump to a chapter','Jump to a family / inset').replace('Choose a chapter','Choose a family / inset')
    template=template.replace("s.observations.join(' '),s.qualifier","s.observations.join(' '),s.special.map(p=>p.year+' '+p.label).join(' '),s.qualifier")
    template=template.replace('@@SVG@@',svg).replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')).replace('@@LAYOUT@@',json.dumps(final))
    (OUT/'viewer/index.html').write_text(template,encoding='utf-8')
    assert sorted(drawn)==sorted(BY) and len(drawn)==79
    print(json.dumps(dict(records=79,family_rows=13,state_pockets=len(state_groups),tracks=layout['row_count'],multi_record_tracks=layout['multi_record_rows'],state_fragments=len(cards),size=[W,H],area_ratio_previous=3600*7760/(W*H))))


if __name__=='__main__':main()
