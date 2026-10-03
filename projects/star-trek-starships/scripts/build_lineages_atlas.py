#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Compose the complete fleet as compact horizontal lines of related ship records."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import math
import shutil
from PIL import Image
import build_space_atlas as draw

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
OUT=PROJECT/'artifacts/lineages-edition'
DATA=draw.DATA;BY=draw.BY
W,M,RAIL,GAP,UNIT=4800,80,0,18,8
INK,MUTED,CYAN,PAPER,RULE=draw.INK,draw.MUTED,draw.CYAN,draw.PAPER,draw.RULE
parts=draw.parts
text,para,rect,path,circle,symbol,wake=draw.text,draw.para,draw.rect,draw.path,draw.circle,draw.symbol,draw.wake
ASSET_IDS={**{k:k for k in draw.ASSETS},'columbia':'enterprise-nx','glenn':'discovery','valiant':'defiant-first','defiant-second':'defiant-first','prodigy':'protostar','rotarran':'bounty'}
GROUPS=[
 ('enterprise','THE ENTERPRISE LINE','Name succession','2151 → 2402',['enterprise-nx','enterprise-1701','enterprise-a','enterprise-b','enterprise-c','enterprise-d','enterprise-e','enterprise-f','titan-a-g']),
 ('earth','EARTH’S FIRST FLEET','Pioneers, tests & civil ships','2063 → 2154',['phoenix','friendship-1','conestoga','horizon','nx-alpha','nx-beta','nx-delta','fortunate','columbia']),
 ('neighbors-early','FIRST NEIGHBORS','Contact-era comparison','2063 → 2154',['t-plana-hath','kumari','vahklas','d-kyr']),
 ('classic-fleet','EARLY STARFLEET','Exploration-era comparison','2245 → 2268',['constellation','shenzhou','discovery','glenn','farragut','archer','intrepid','defiant-1764']),
 ('workhorses','REFITS & WORKHORSES','Fleet comparison','2278 → 2367',['bozeman','reliant','grissom','excelsior','saratoga']),
 ('explorers','EXPLORERS & FLAGSHIPS','Selected designs; reused names','2326 → 2401',['stargazer-old','phoenix-nebula','yamato','odyssey','prometheus','stargazer-new']),
 ('escorts','THE DEFIANT ERA','Runabout & escort comparison','2369 → 2384',['rio-grande','defiant-first','valiant','defiant-second']),
 ('voyager-line','VOYAGER & DELTA CRAFT','Names, expedition & replacements','2370 → 3191',['equinox','voyager','delta-flyer-1','delta-flyer-2','voyager-a','voyager-j']),
 ('new-generation','A NEW GENERATION','Explorers, workboats & prototypes','2379 → 2385',['titan','cerritos','solvang','aledo','protostar','dauntless','prodigy']),
 ('klingon','KLINGON SHIPLINES','Design comparison','2268 → 2375',['groth','bounty','kronos-one','bortas','negh-var','rotarran']),
 ('other-powers','RIVALS & ALLIES','Cross-fleet comparison','2266 → 2379',['romulan-bop','krayton','trager','khazara','koranak','captured-jemhadar','valdore','scimitar']),
 ('borg','THE BORG ENCOUNTERS','Distinct cubes; no hull succession','2366 → 2399',['wolf-cube','sector-cube','artifact']),
 ('future-fleet','AFTER THE BURN','32nd-century fleet comparison','3189 → 3190s',['nog','tikhov','credence','athena'])]
SHORT_KIND={'name-succession':'name successor','test-program':'test program','development':'development','sister-ship':'sister ship','replacement-hull':'replacement hull','later-name-bearer':'later name bearer','prototype-to-production':'production design','rename':'same hull renamed'}
OUTGOING={id:[r for r in DATA['relations'] if r['source']==id] for id in BY}
group_for={id:g[0] for g in GROUPS for id in g[4]}
source_num=draw.source_numbers
drawn=[];artwork=[];anchors=[];placed_relations=[]


def measure_card(s,w):
    content=w-24; name=draw.wrap(s['name'],content,30,'display')
    cls=draw.wrap(s['registry']+' · '+s['design'],content,16)
    launch=('Built ' if s['launch_kind']=='built' else 'Commissioned ' if s['launch_kind']=='commission' else 'Launch ')+(str(s['launch']) if s['launch'] is not None else '—')
    if s['construction'] and s['launch_kind']!='built':launch+=' · building '+', '.join(map(str,s['construction']))
    if s['shipyard'] and not s['construction']:launch+=' · '+s['shipyard']
    launch_lines=draw.wrap(launch,content,15,'bold')
    years=sorted(set(s['observations']+([s['launch']] if s['launch'] is not None else [])))
    uncertain=s.get('uncertain_range')
    date_label=('c. 2144–2145' if s['id']=='nx-delta' else '3190s · dating disputed') if uncertain else ' · '.join(map(str,years))
    date_lines=draw.wrap(date_label,content,17,'bold')
    py=32+(len(name)-1)*33+23+len(cls)*19+len(launch_lines)*18+7
    use_y=py
    bar_y=use_y+(len(date_lines)-1)*21+26
    end=uncertain[1] if uncertain else years[-1]
    start=uncertain[0] if uncertain else years[0]
    has_art=s['id'] in ASSET_IDS
    end_x=12+(end-start)*UNIT
    if has_art and end_x+14+146>w-8:raise ValueError('Artwork needs a wider record: '+s['id'])
    extra=draw.wrap(' · '.join(q['label'] for q in s['special']),content,15)
    note_y=bar_y+(66 if has_art else 33)+(len(extra)*18 if extra else 0)
    note=draw.note_runs(s['note'],f'[{source_num[s["source"]]}]',content)
    credit=[];credit_y=note_y+len(note)*23
    rels=[];rel_y=credit_y+6
    for r in OUTGOING[s['id']]:
        if r['kind']=='name-succession' and s['id'] in GROUPS[0][4] and r['target'] in GROUPS[0][4]:continue
        target=BY[r['target']]['name'].replace('USS ','')
        label=(f'↳ Renamed {r["year"]} · same hull' if r['kind']=='rename' else '→ '+target+' · '+SHORT_KIND[r['kind']])
        lines=draw.wrap(label,content,15)
        rels.append(dict(relation=r,lines=lines,y=rel_y));rel_y+=len(lines)*18
    return dict(id=s['id'],width=w,height=math.ceil(rel_y+13),name=name,cls=cls,launch=launch_lines,dates=date_lines,use_y=use_y,bar_y=bar_y,years=years,start=start,end=end,has_art=has_art,extra=extra,note_y=note_y,note=note,credit_y=credit_y,credit=credit,rels=rels)


def header():
    text('STAR TREK',M,131,128,'display')
    text('SHIPLINES',M+660,131,128,'display',CYAN)
    text('79 ships. 13 shared lines. A fleet history read from left to right.',M,185,30,fill=INK)
    text('NAMES • DESIGNS • CONSTRUCTION • VOYAGES • FATES',W-M,105,28,'display',CYAN,'end')
    text('Prime continuity · selected vessels · 2063–3190s',W-M,151,22,'body',MUTED,'end')
    text('READ EACH LINE →',M,259,26,'display',CYAN)
    text('Sequence spacing is schematic; years are stated within each ship. Sharing a row does not imply ancestry.',M+255,257,22,fill=MUTED)
    wake(2240,2370,250,CYAN,True);text('Supported service',2390,257,21)
    wake(2665,2795,250,CYAN);text('Selected sightings',2815,257,21)
    symbol('launch',3130,250,CYAN,6);text('Launch / build',3150,257,21)
    symbol('destroyed',3375,250,CYAN,6);text('Loss',3395,257,21)
    symbol('retired',3510,250,CYAN,6);text('Retired / abandoned',3535,257,21)
    text('Equal strip lengths = equal elapsed years; every strip starts at its vessel’s first shown date.',M,298,21,fill=MUTED)
    text('Images identify design families; hull markings and physical sizes are illustrative.',W-M,298,21,'body',MUTED,'end')
    return 342


def paint_card(s,c,b):
    id=s['id'];x,y,w=b['x'],b['y'],b['w'];col=draw.COLORS[s['operator']]
    parts.append(f'<g id="record-{id}" class="record" data-id="{id}" data-group="{group_for[id]}" data-operator="{s["operator"]}" data-source="{draw.esc(DATA["sources"][s["source"]]["url"])}" tabindex="0" role="button" aria-label="{draw.esc(s["name"]+". "+s["note"])}">')
    rect(x,y,w,b['h'],'transparent','class="hit-area"',5)
    path(f'M{x+12} {y+5}H{x+w-12}',col,2,'opacity=".65"')
    for k,line in enumerate(c['name']):text(line,x+12,y+32+k*33,30,'display',col if s['important'] else INK,role='ship-name')
    py=y+32+(len(c['name'])-1)*33+23
    for line in c['cls']:text(line,x+12,py,16,fill=MUTED,role='class-detail');py+=19
    for line in c['launch']:text(line,x+12,py,15,'bold',MUTED,role='launch-detail');py+=18
    for k,line in enumerate(c['dates']):text(line,x+12,y+c['use_y']+k*21,17,'bold',col,role='use-label')
    py=y+c['bar_y'];origin=c['start'];px=lambda t:x+12+(t-origin)*UNIT
    uncertain=s.get('uncertain_range')
    if uncertain:
        a,z=uncertain;parts.append(f'<g class="uncertain-span" data-start="{a}" data-end="{z}">')
        rect(px(a),py-6,px(z)-px(a),12,'url(#uncertain)',f'stroke="{col}" stroke-width="1"');parts.append('</g>')
    else:
        if s['service']:wake(px(s['service'][0]),px(s['service'][1]),py,col,True,id,*s['service'])
        elif len(c['years'])>1:wake(px(origin),px(c['end']),py,col,False,id,origin,c['end'])
        for t in c['years']:
            kind=s['launch_kind'] if t==s['launch'] else s['endpoint'] if t==s['observations'][-1] and s['endpoint'] else 'active'
            if t==s['launch'] and s['endpoint'] and t==s['observations'][-1]:kind='launch'
            symbol(kind,px(t),py,col,4,extra=f'data-year="{t}" data-kind="{kind}"')
            anchors.append(dict(ship=id,year=t,kind=kind,x=px(t),origin=origin,unit=UNIT))
        if s['endpoint'] and s['launch']==s['observations'][-1]:symbol(s['endpoint'],px(c['end']),py+18,col,4,extra=f'data-year="{c["end"]}" data-kind="{s["endpoint"]}"')
        for q in s['special']:
            if q['kind']=='reactivated' and 0<=q['year']-origin<=60:
                symbol('reactivated',px(q['year']),py,col,4,extra=f'data-year="{q["year"]}" data-kind="reactivated"')
                anchors.append(dict(ship=id,year=q['year'],kind='reactivated',x=px(q['year']),origin=origin,unit=UNIT))
    if c['has_art']:
        ax,ay,aw,ah=px(c['end'])+14,py-42,146,90
        asset=ASSET_IDS[id]
        parts.append(f'<use class="ship-art" href="#art-{asset}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" style="mix-blend-mode:screen" data-ship="{id}" data-end-year="{c["end"]}"/>')
        artwork.append(dict(id=asset,ship=id,x=ax,y=ay,w=aw,h=ah,year=c['end']))
    extra_y=y+c['note_y']-len(c['extra'])*18-6
    for k,line in enumerate(c['extra']):text(line,x+12,extra_y+k*18,15,fill=MUTED,role='other-date')
    for k,runs in enumerate(c['note']):
        for run in runs:text(run['text'],x+12+run['x'],y+c['note_y']+k*23,run['size'],fill=run['color'],role=run['role'])
    for k,line in enumerate(c['credit']):text(line,x+12,y+c['credit_y']+k*18,15,fill=MUTED,role='source-credit')
    for r in c['rels']:
        rr=r['relation'];parts.append(f'<g class="typed-relation" data-source="{rr["source"]}" data-target="{rr["target"]}" data-kind="{rr["kind"]}">')
        for k,line in enumerate(r['lines']):text(line,x+12,y+r['y']+k*18,15,fill=CYAN,role='relation-caption')
        parts.append('</g>');placed_relations.append(rr)
    parts.append('</g>');drawn.append(id)


def main():
    for folder in ['svgs','images','documents','viewer','data','reviews','archives']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    top=header();available=W-2*M
    by_group={g[0]:g for g in GROUPS}
    bands=[['enterprise'],['earth'],['classic-fleet'],['neighbors-early','borg'],['workhorses','escorts'],['explorers','future-fleet'],['voyager-line'],['new-generation'],['klingon','other-powers']]
    group_widths={}
    for band in bands:
        total=sum(len(by_group[id][4]) for id in band)
        for id in band:group_widths[id]=(available-64*(len(band)-1))*len(by_group[id][4])/total
    cards={};groups=[]
    for id in [id for band in bands for id in band]:
        id,title,kind,years,members=by_group[id]
        group_width=group_widths[id]
        w=(group_width-GAP*(len(members)-1))/len(members)
        for ship in members:cards[ship]=measure_card(BY[ship],w)
        groups.append(dict(id=id,title=title,kind=kind,years=years,members=members,width=group_width,header_height=57))
    brief=dict(width=W,margin=M,label_rail=RAIL,gap=GAP,column_gap=64,row_gap=24,top=top,groups=groups,records=[dict(id=id,width=c['width'],height=c['height']) for id,c in cards.items()])
    spec=importlib.util.spec_from_file_location('shared_rows',ROOT/'skills/usefulcharts-style/scripts/pack_shared_rows.py')
    packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    packed=packer.pack(brief);layout=packed['layout'];boxes={b['id']:b for b in layout['boxes']};regions=[]
    (OUT/'data/shared-row-brief.json').write_text(json.dumps(brief,indent=2)+'\n',encoding='utf-8')
    (OUT/'reviews/shared-row-layout.json').write_text(json.dumps(packed,indent=2)+'\n',encoding='utf-8')
    for i,(g,gl) in enumerate(zip(groups,layout['groups'])):
        x,y,h,gw=gl['x'],gl['y'],gl['h'],gl['w'];regions.append(dict(id=g['id'],title=g['title'].title(),x=x,y=y,w=gw,h=h))
        parts.append(f'<g class="shared-family" data-group="{g["id"]}" data-count="{len(g["members"])}">')
        rect(x-10,y-3,gw+20,h+10,'#081527',f'opacity="{.30 if i%2==0 else .08}"',7)
        text(f'{i+1:02}',x,y+33,32,'display',CYAN)
        text(g['title'],x+55,y+33,32,'display',INK)
        tx=x+75+draw.measure(g['title'],32,'display')
        text(g['kind'],tx,y+30,18,fill=MUTED)
        text(g['years']+f'  /  {len(g["members"])} ships',x+gw,y+31,20,'body',CYAN,'end')
        for id in g['members']:paint_card(BY[id],cards[id],boxes[id])
        if g['id']=='enterprise':
            for a,b in zip(g['members'],g['members'][1:]):
                aa,bb=boxes[a],boxes[b]
                rr=next(r for r in DATA['relations'] if r['source']==a and r['target']==b)
                parts.append(f'<g class="typed-relation" data-source="{a}" data-target="{b}" data-kind="name-succession">')
                path(f'M{aa["x"]+aa["w"]+3} {aa["y"]+28}H{bb["x"]-3}',CYAN,1.4,'marker-end="url(#arrow)"')
                parts.append('</g>');placed_relations.append(rr)
        parts.append('</g>')
    h=math.ceil(layout['height']+140)
    footer_y=layout['height']+12
    text('DIFFERENT HULLS. SHARED NAMES. DISTINCT EVIDENCE.',M,footer_y,32,'display',CYAN)
    text('Arrows name supported relationships. Comparison rows organize fleets without asserting descent. Unknown launches stay unknown; a jump is not a service interval.',M,footer_y+41,21,fill=MUTED)
    text('Independent educational fan atlas · 12 September 2026 · Full sources and qualifications in the companion viewer · Star Trek properties belong to their respective rights holders.',M,footer_y+80,18,fill=MUTED)
    font64=base64.b64encode(draw.FONT.read_bytes()).decode()
    defs=[f'<style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{font64});font-weight:700}}.record{{cursor:pointer}}text{{font-kerning:normal}}</style>', '<filter id="glow" x="-60%" y="-400%" width="220%" height="900%"><feGaussianBlur stdDeviation="4"/></filter>', '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#68DBFF" stroke-width="1.2"/></marker>', '<pattern id="uncertain" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M-1 1L5 7M2-3L8 3" stroke="#ADC8E3" stroke-width="1"/></pattern>']
    for id,file in draw.ASSETS.items():
        im=Image.open(draw.ART/file);iw,ih=im.size
        defs.append(f'<symbol id="art-{id}" viewBox="0 0 {iw} {ih}" preserveAspectRatio="xMidYMid meet"><image width="{iw}" height="{ih}" href="data:image/png;base64,{base64.b64encode((draw.ART/file).read_bytes()).decode()}"/></symbol>')
    bg=base64.b64encode((draw.ART/'nebula-background.png').read_bytes()).decode()
    background=f'<rect width="{W}" height="{h}" fill="{PAPER}"/><image width="{W}" height="{h}" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{bg}" opacity=".62"/><rect width="{W}" height="{h}" fill="#030A18" opacity=".72"/>'
    metadata=dict(edition='shared lineages',source_sha256=hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest(),sequence='Schematic within author-defined semantic rows; no global calendar x coordinate.',evidence_strips='Local origins, common eight SVG units per elapsed year; solid only for supported service. Off-scale events printed separately.',artwork='Six existing generated class illustrations, reused only for the same class/type; appearance is illustrative.')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="poster-title poster-desc"><title id="poster-title">Star Trek: Shiplines</title><desc id="poster-desc">79 individual ships share 13 horizontal thematic lines. Multiple facts and typed relationships stay with each vessel. Sequence spacing is schematic, and local evidence strips use a common duration scale.</desc><metadata>{draw.esc(json.dumps(metadata))}</metadata><defs>{"".join(defs)}</defs>{background}{"".join(parts)}</svg>'
    target=OUT/'svgs/star-trek-starships.svg';target.write_text(svg,encoding='utf-8')
    final_layout=dict(width=W,height=h,boxes=layout['boxes'],regions=regions,anchors=anchors,illustrations=artwork,edition='lineages',record_count=len(drawn),row_count=len(regions),band_count=layout['band_count'],source_sha256=metadata['source_sha256'],svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (OUT/'reviews/layout.json').write_text(json.dumps(final_layout,indent=2)+'\n',encoding='utf-8')
    for rel in ['data/ships.json','data/ships.csv','documents/sources.html','documents/font-license.txt']:shutil.copyfile(PROJECT/'artifacts'/rel,OUT/rel)
    shutil.copyfile(PROJECT/'design/image-generation.json',OUT/'data/image-generation.json')
    template=(PROJECT/'scripts/viewer.html').read_text(encoding='utf-8')
    template=template.replace('</head>','<style>'+(PROJECT/'scripts/space-viewer.css').read_text()+'</style></head>')
    template=template.replace('Starships Through Time','Star Trek Shiplines').replace('Starships<br>through time','Star Trek<br>shiplines')
    template=template.replace('Construction, launch and documented use across the Prime timeline.','79 vessels share 13 horizontal lines. Each block combines identity, dates, design, fate and relationships.')
    template=template.replace('Click a fleet lane for its evidence. Each chapter has its own linear year scale. Dashed spans connect selected sightings; they do not confirm uninterrupted service.','Read each line left to right. Sequence spacing is schematic. Within each ship, evidence strips use the same duration scale. Dashed spans connect sightings without confirming uninterrupted service.')
    template=template.replace('@@SVG@@',svg).replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')).replace('@@LAYOUT@@',json.dumps(final_layout))
    (OUT/'viewer/index.html').write_text(template,encoding='utf-8')
    assert sorted(drawn)==sorted(BY) and len(drawn)==79
    assert len(placed_relations)==len(DATA['relations'])==21
    print(json.dumps(dict(records=len(drawn),rows=len(regions),size=[W,h],placements=len(artwork),area_ratio_previous=3600*7760/(W*h))))


if __name__=='__main__':main()
