#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Compose the space edition with dated luminous wakes and generated ship art."""
from pathlib import Path
from html import escape
import base64
import hashlib
import json
import math
import shutil
from PIL import Image, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
OUT = PROJECT / "artifacts/space-edition"
ART = PROJECT / "artifacts/images/space-edition"
DATA = json.loads((PROJECT / "data/ships.json").read_text(encoding="utf-8"))
BY = {s["id"]:s for s in DATA["ships"]}
FONT = ROOT / "skills/usefulcharts-style/assets/fonts/BarlowCondensed-Bold.ttf"
W,M,GAP = 3600,90,100
CW = (W-2*M-GAP)/2
INK,MUTED,CYAN,PAPER,RULE = "#EFF7FF","#A6BCD2","#68DBFF","#050B17","#283A53"
COLORS = {"Earth":"#7CB9FF","Federation":"#70DCFF","Vulcan":"#FFBF82","Andorian":"#8BE8E5",
          "Klingon":"#FF967E","Romulan":"#B2EA9A","Reman":"#CBC4F1","Cardassian":"#FFD77D",
          "Dominion":"#C5A3FF","Borg":"#BDD97A","Ferengi":"#FFC795"}
ASSETS = {"enterprise-nx":"enterprise-nx.png","voyager":"voyager.png","defiant-first":"defiant.png",
          "discovery":"discovery.png","protostar":"protostar.png","bounty":"klingon-bird.png"}
parts=[]; boxes=[]; regions=[]; anchors=[]; placed_art=[]; drawn=[]
fonts={}; source_numbers={k:i+1 for i,k in enumerate(DATA["sources"])}


def esc(s):return escape(str(s),quote=True)
def font(size,kind):
    key=(size,kind)
    if key not in fonts:
        f=FONT if kind=="display" else Path("C:/Windows/Fonts/arialbd.ttf" if kind=="bold" else "C:/Windows/Fonts/arial.ttf")
        fonts[key]=ImageFont.truetype(str(f),round(size*4))
    return fonts[key]
def measure(s,size=19,kind="body"):return font(size,kind).getlength(str(s))/4
def wrap(s,w,size=19,kind="body"):
    result=[];current=""
    for word in str(s).split():
        test=(current+" "+word).strip()
        if current and measure(test,size,kind)>w:result.append(current);current=word
        else:current=test
    if current:result.append(current)
    return result
def text(s,x,y,size=19,kind="body",fill=INK,anchor="start",role="body"):
    fam="Barlow" if kind=="display" else "Arial"
    parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-family="{fam},sans-serif" font-weight="{700 if kind in {"display","bold"} else 400}" fill="{fill}" text-anchor="{anchor}" data-role="{role}">{esc(s)}</text>')
def para(s,x,y,w,size=19,kind="body",fill=INK,leading=None,role="body"):
    leading=leading or size*1.25
    lines=wrap(s,w,size,kind)
    for i,line in enumerate(lines):text(line,x,y+i*leading,size,kind,fill,role=role)
    return y+len(lines)*leading

def note_runs(note,credit,w):
    lines=[[]];used=0
    for value,size,color,role in [(note,19,'#CFDEEE','body'),(credit,15,MUTED,'source-credit')]:
        for word in value.split():
            gap=(20 if lines[-1] and lines[-1][-1]['role']!=role else measure(' ',size)) if used else 0
            length=measure(word,size)
            if used+gap+length>w:lines.append([]);used=0;gap=0
            if lines[-1] and lines[-1][-1]['role']==role:
                lines[-1][-1]['text']+=' '+word
            else:lines[-1].append(dict(text=word,x=used+gap,size=size,color=color,role=role))
            used+=gap+length
    return lines
def rect(x,y,w,h,fill,extra="",rx=0):
    parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" {extra}/>')
def path(d,color=CYAN,sw=1,extra="",fill="none"):
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')
def circle(x,y,r,color=CYAN,extra=""):
    parts.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{color}" {extra}/>')
def art(id,x,y,w,h,ship=None,year=None):
    parts.append(f'<use class="ship-art" href="#art-{id}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" style="mix-blend-mode:screen" data-ship="{ship or id}"'+(f' data-end-year="{year}"' if year is not None else '')+'/>')
    placed_art.append(dict(id=id,ship=ship or id,x=x,y=y,w=w,h=h,year=year))


def symbol(kind,x,y,col,r=5,extra=""):
    parts.append(f'<g class="date-mark" {extra}>')
    if kind in {"launch","commission","built"}:
        path(f'M{x} {y-r}L{x+r} {y}L{x} {y+r}L{x-r} {y}Z',INK,1.2,fill=col)
    elif kind in {"destroyed","wrecked"}:
        path(f'M{x-r} {y-r}L{x+r} {y+r}M{x-r} {y+r}L{x+r} {y-r}',"#FF9F96",2.2)
    elif kind in {"retired","dismantled","abandoned"}:
        rect(x-r,y-r,r*2,r*2,PAPER,f'stroke="{col}" stroke-width="1.8"')
    elif kind=="time-jump":
        path(f'M{x-r} {y-r}L{x+r} {y}L{x-r} {y+r}',col,2.2)
    elif kind=="reactivated":
        circle(x,y,r,PAPER,f'stroke="{col}" stroke-width="2"');circle(x,y,2,col)
    else:circle(x,y,r,col,f'stroke="{INK}" stroke-width=".8"')
    parts.append('</g>')


def wake(x1,x2,y,col,solid=False,ship=None,start=None,end=None):
    if x1==x2:return
    kind="service" if solid else "observations"
    parts.append(f'<g class="wake {kind}-span" data-start="{start}" data-end="{end}" data-ship="{ship}">')
    dash='' if solid else 'stroke-dasharray="9 9"'
    if solid:
        spread=min(14,(x2-x1)*.12)
        path(f'M{x1:.3f} {y-1:.3f}Q{(x1+x2)/2:.3f} {y-spread*.35:.3f} {x2:.3f} {y-spread:.3f}V{y+spread:.3f}Q{(x1+x2)/2:.3f} {y+spread*.35:.3f} {x1:.3f} {y+1:.3f}Z',col,0,'opacity=".2"',fill=col)
    path(f'M{x1:.3f} {y:.3f}H{x2:.3f}',col,15,f'opacity=".12" filter="url(#glow)" {dash} class="wake-halo"')
    path(f'M{x1:.3f} {y:.3f}H{x2:.3f}',col,5 if solid else 2.2,f'opacity="{.88 if solid else .7}" {dash} class="wake-core"')
    if solid:path(f'M{x1:.3f} {y:.3f}H{x2:.3f}',"#E3F9FF",1.2,'opacity=".75"')
    parts.append('</g>')


def header():
    text('STAR TREK',M,191,174,'display')
    text('STARSHIPS IN MOTION',M,341,104,'display',CYAN)
    para('When they were built. When they flew.\nWhat became of them.',M,406,1240,33,fill="#BDCEE3",leading=43)
    text('79 SPACECRAFT',M,551,47,'display')
    text('11 groups  /  5 eras  /  Prime continuity',M+350,551,28,fill=MUTED)
    # A dated hero wake doubles as the opening reading example.
    x1,x2,y=1810,2500,317
    path(f'M{x1} {y-13}H{x2}',CYAN,3,'opacity=".28" filter="url(#glow)"')
    path(f'M{x1} {y+13}H{x2}',CYAN,3,'opacity=".28" filter="url(#glow)"')
    wake(x1,x2,y,CYAN,True,'voyager',2371,2378)
    symbol('launch',x1,y,CYAN,8);symbol('active',x2,y,CYAN,8)
    text('2371',x1,365,31,'bold',CYAN,'middle')
    text('2378',x2,365,31,'bold',CYAN,'middle')
    art('voyager',2545,100,920,540)
    text('USS VOYAGER',1870,467,45,'display')
    text('Seven years across the Delta Quadrant',1870,506,27,fill=MUTED)
    text('The wake measures years — not distance or speed.',1870,552,23,fill=MUTED)
    path(f'M{M} 625H{W-M}',RULE,1.4)
    text('READ THE WAKE',M,678,35,'display',CYAN)
    symbol('launch',M+8,727,CYAN,6);text('Known launch / commission / build',M+32,734,22)
    wake(M+750,M+900,727,CYAN,True);text('Supported service or mission',M+920,734,22)
    wake(M+1490,M+1640,727,CYAN);text('Selected sightings; gaps unverified',M+1660,734,22)
    text('TIME RUNS TO THE RIGHT',W-M,679,25,'bold',CYAN,'end')
    symbol('destroyed',M+8,772,CYAN,6);text('Loss',M+32,779,22)
    symbol('retired',M+250,772,CYAN,6);text('Retired / abandoned / dismantled',M+275,779,22)
    symbol('time-jump',M+750,772,CYAN,6);text('Time displacement',M+775,779,22)
    text('—  Launch year unstated',M+1490,779,22)
    text('Each chapter has its own linear year scale. A ship illustration extends beyond its marked date.',M,833,23,fill=MUTED)
    xx=M
    for op,col in COLORS.items():
        circle(xx+6,885,5,col);text(op,xx+24,892,21,fill=MUTED);xx+=measure(op,21)+67
    return 958


def chapter(key,x,y,num,title,subtitle,lo,hi,ticks):
    start=y
    text(num,x,y+47,51,'display',CYAN)
    text(title,x+80,y+42,40,'display')
    text(f'{lo}–{hi}',x+CW,y+43,29,'display',MUTED,'end')
    text(subtitle,x+80,y+78,20,fill=MUTED)
    plotx=x+590;plotw=795
    def px(t):return plotx+(t-lo)/(hi-lo)*plotw
    axis_y=y+124
    path(f'M{plotx} {axis_y}H{px(hi)}',RULE,1)
    for t in ticks:
        xx=px(t);text(t,xx,axis_y-13,16,'bold',MUTED,'middle',role='axis-year');path(f'M{xx} {axis_y-3}V{axis_y+5}',MUTED,1)
    rows=[s for s in DATA['ships'] if s['chapter']==key]
    yy=y+148
    for i,s in enumerate(rows):
        rid=s['id'];col=COLORS[s['operator']];has_art=rid in ASSETS
        sz=34 if s['important'] else 30
        name_lines=wrap(s['name'],520,sz,'display')
        class_lines=wrap(s['registry']+' · '+s['design'],520,16)
        launch=('Built ' if s['launch_kind']=='built' else 'Commissioned ' if s['launch_kind']=='commission' else 'Launch ')+(str(s['launch']) if s['launch'] is not None else '—')
        if s['construction'] and s['launch_kind']!='built':launch+=' · building '+', '.join(map(str,s['construction']))
        if s['shipyard'] and not s['construction']:launch+=' · '+s['shipyard']
        launch_lines=wrap(launch,520,15,'bold')
        lab_end=yy+36+(len(name_lines)-1)*35+23+len(class_lines)*19+(len(launch_lines)-1)*18+4
        early_years=sorted(set(s['observations']+([s['launch']] if s['launch'] is not None else [])))
        extra_labels=[q['label'] for q in s['special'] if not(q['kind'] in {'active','reactivated','time-arrival'} and lo<=q['year']<=hi)]
        extra_width=max(150,min(720,px(early_years[-1])-plotx-16)) if has_art else 720
        extra_lines=wrap(' · '.join(extra_labels),extra_width,15)
        note_y=max(yy+109,lab_end+23,yy+187 if has_art else 0,yy+87+(len(extra_lines)-1)*18+25 if extra_lines else 0)
        credit=s['credit']+f' [{source_numbers[s["source"]]}]'
        notes=note_runs(s['note'],credit,CW-34)
        ht=math.ceil(max(128,note_y-yy+(len(notes)-1)*24+17))
        src=DATA['sources'][s['source']]['url']
        parts.append(f'<g id="record-{rid}" class="record" data-id="{rid}" data-operator="{s["operator"]}" data-source="{esc(src)}" tabindex="0" role="button" aria-label="{esc(s["name"]+". "+s["note"])}">')
        parts.append(f'<title>{esc(s["name"]+" — "+s["note"])}</title>')
        rect(x,yy,CW,ht,'transparent','class="hit-area"',9)
        if s['important']:
            rect(x-8,yy+6,5,38,col,rx=2)
        for k,line in enumerate(name_lines):text(line,x+14,yy+36+k*35,sz,'display',col if s['important'] else INK,role='ship-name')
        py=yy+36+(len(name_lines)-1)*35+23
        for line in class_lines:text(line,x+14,py,16,fill=MUTED,role='class-detail');py+=19
        for line in launch_lines:text(line,x+14,py,15,'bold',MUTED,role='launch-detail');py+=18
        obs=s['observations'];years=sorted(set(obs+([s['launch']] if s['launch'] is not None else [])))
        special=[q for q in s['special'] if q['kind'] in {'active','reactivated','time-arrival'} and lo<=q['year']<=hi]
        uncertain=s.get('uncertain_range')
        if uncertain:label='c. 2144–2145' if rid=='nx-delta' else '3190s · dating disputed'
        elif s['service']:label=f'{s["service"][0]}–{s["service"][1]}' + ('; '+', '.join(str(q['year']) for q in special) if special else '')
        else:label=' · '.join(map(str,years))
        text(label,plotx,yy+25,20,'bold',col,role='use-label')
        bar_y=yy+59
        if uncertain:
            a,b=uncertain;parts.append(f'<g class="uncertain-span" data-start="{a}" data-end="{b}">')
            rect(px(a),bar_y-7,px(b)-px(a),14,'url(#uncertain)',f'stroke="{col}" stroke-width=".7"');parts.append('</g>')
            anchors.append(dict(ship=rid,kind='uncertain-range',start=a,end=b,x1=px(a),x2=px(b),scale=[lo,hi,plotx,plotw]))
        else:
            if s['service']:a,b=s['service'];wake(px(a),px(b),bar_y,col,True,rid,a,b)
            elif len(years)>1:wake(px(years[0]),px(years[-1]),bar_y,col,False,rid,years[0],years[-1])
            for t in years:
                kind=s['launch_kind'] if t==s['launch'] else (s['endpoint'] if t==obs[-1] and s['endpoint'] else 'active')
                if t==s['launch'] and s['endpoint'] and t==obs[-1]:kind='launch'
                symbol(kind,px(t),bar_y,col,5,extra=f'data-year="{t}" data-kind="{kind}"')
                anchors.append(dict(ship=rid,kind=kind,year=t,x=px(t),scale=[lo,hi,plotx,plotw]))
            if s['endpoint'] and s['launch']==obs[-1]:symbol(s['endpoint'],px(obs[-1]),bar_y+22,col,5,extra=f'data-year="{obs[-1]}" data-kind="{s["endpoint"]}"')
            for q in special:
                symbol(q['kind'],px(q['year']),bar_y,col,5,extra=f'data-year="{q["year"]}" data-kind="{q["kind"]}"')
                anchors.append(dict(ship=rid,kind=q['kind'],year=q['year'],x=px(q['year']),scale=[lo,hi,plotx,plotw]))
            end=years[-1]
            circle(px(end),bar_y,13,col,'opacity=".12" class="engine-beacon" filter="url(#glow)"')
            if has_art:art(rid,px(end)+13,yy+8,254,157,ship=rid,year=end)
        for k,line in enumerate(extra_lines):text(line,plotx,yy+87+k*18,15,fill=MUTED,role='other-date')
        for k,runs in enumerate(notes):
            for run in runs:text(run['text'],x+14+run['x'],note_y+k*24,run['size'],fill=run['color'],role=run['role'])
        if i%3==2:path(f'M{x+14} {yy+ht-5}H{x+CW-15}',RULE,.6,'opacity=".35"')
        parts.append('</g>')
        boxes.append(dict(id=rid,x=x,y=yy,w=CW,h=ht));drawn.append(rid);yy+=ht
    regions.append(dict(id=key,title=title,x=x,y=start,w=CW,h=yy-start,scale=[lo,hi,plotx,plotw]))
    return yy+82


def relationships(y):
    path(f'M{M} {y}H{W-M}',CYAN,1,'opacity=".5"')
    text('ONE NAME. MANY VOYAGES.',M,y+59,44,'display',CYAN)
    text('Enterprise name succession · schematic spacing',M+649,y+57,24,fill=MUTED)
    ids=['enterprise-nx','enterprise-1701','enterprise-a','enterprise-b','enterprise-c','enterprise-d','enterprise-e','enterprise-f','titan-a-g']
    labels=['NX-01','1701','1701-A','1701-B','1701-C','1701-D','1701-E','1701-F','1701-G']
    dates=['2151','2245','2286','2293','2344 · seen','2363','2372','2401 · seen','2402 · renamed']
    cell=(W-2*M)/9
    for i,(id,label,date) in enumerate(zip(ids,labels,dates)):
        xx=M+i*cell;ww=cell-43
        rect(xx,y+92,ww,52,'#123047',f'stroke="{CYAN}" stroke-opacity=".5" stroke-width="1"',6)
        text(label,xx+ww/2,y+129,33,'display',INK,'middle')
        text(date,xx+ww/2,y+179,20,'body',MUTED,'middle')
        if i<8:path(f'M{xx+ww+7} {y+117}H{xx+cell-8}',CYAN,1.4,'marker-end="url(#arrow)"')
    stories=[
      ('NX test program','NX-Alpha → NX-Beta → NX-Delta','2143 / 2143 / c. 2144–2145','The prototypes lead toward Enterprise NX-01.'),
      ('A new Defiant','Original Defiant → Sao Paulo','Lost 2375 / renamed 2375','A replacement hull carries the familiar name.'),
      ('Sister NX explorers','Enterprise ↔ Columbia','Launch 2151 / launch 2154','Different physical vessels in one class.'),
      ('Two Delta Flyers','First hull → second hull','Built 2375 / built 2377','Voyager constructs a replacement after the loss.'),
      ('Spore-drive sisters','Discovery ↔ Glenn','Attested 2256 / lost 2256','Parallel experiments in Crossfield-class ships.'),
      ('Prototype to production','Protostar → Prodigy','Launch 2382 / launch 2385','A design becomes a production class.'),
      ('The Voyager name','Voyager → A ⇢ J','2371 / 2384 / seen 3189','Selected name bearers; intermediate ships omitted.'),
      ('Same hull, new name','Titan-A → Enterprise-G','Renamed 2402','The name and registry change; the hull continues.')]
    colw=(W-2*M-3*56)/4
    for i,(title,line,dates,note) in enumerate(stories):
        xx=M+(i%4)*(colw+56);yy=y+233+(i//4)*155
        parts.append('<g class="identity-story">')
        text(title,xx,yy,29,'display',CYAN)
        text(line,xx,yy+37,23,'bold')
        text(dates,xx,yy+68,19,fill=MUTED)
        para(note,xx,yy+100,colw,18,fill=MUTED)
        parts.append('</g>')
    regions.append(dict(id='identities',title='Ship identities and relationships',x=M,y=y,w=W-2*M,h=551))
    return y+582


def export(height):
    for folder in ['svgs','images','documents','viewer','data','reviews','archives']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    defs=[f'<style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{base64.b64encode(FONT.read_bytes()).decode()});font-weight:700}}.record{{cursor:pointer}}text{{font-kerning:normal}}.engine-beacon{{animation:beacon 3s ease-in-out infinite}}@keyframes beacon{{50%{{opacity:.35}}}}@media(prefers-reduced-motion:reduce){{.engine-beacon{{animation:none}}}}@media print{{.engine-beacon{{animation:none}}}}</style>',
          '<filter id="glow" x="-60%" y="-400%" width="220%" height="900%"><feGaussianBlur stdDeviation="4"/></filter>',
          '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#68DBFF" stroke-width="1.3"/></marker>',
          '<pattern id="uncertain" width="7" height="7" patternUnits="userSpaceOnUse"><path d="M-1 1L6 8M3-3L10 4" stroke="#ADC8E3" stroke-width="1.2"/></pattern>']
    assets=ASSETS
    for key,file in assets.items():
        im=Image.open(ART/file);width,hh=im.size
        defs.append(f'<symbol id="art-{key}" viewBox="0 0 {width} {hh}" preserveAspectRatio="xMidYMid meet"><image width="{width}" height="{hh}" href="data:image/png;base64,{base64.b64encode((ART/file).read_bytes()).decode()}"/></symbol>')
    meta=dict(continuity='Prime',edition='Space edition',data='ships.json',
              artwork='Six reference-guided generated spacecraft illustrations and one generated nebula backdrop; appearance is illustrative and not physical scale.',
              art_provenance='image-generation.json',time_policy=DATA['date_policy'])
    bg=base64.b64encode((ART/'nebula-background.png').read_bytes()).decode()
    background=f'<rect width="{W}" height="{height}" fill="{PAPER}"/><image width="{W}" height="{height}" preserveAspectRatio="xMaxYMid slice" href="data:image/png;base64,{bg}" opacity=".83"/><rect width="{W}" height="{height}" fill="#030A18" opacity=".66"/>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-labelledby="poster-title poster-desc"><title id="poster-title">Star Trek: Starships in Motion</title><desc id="poster-desc">79 selected spacecraft, dated wakes, known launches and final fates. Each chapter uses its own linear calendar scale. Glow does not encode distance or speed.</desc><metadata>{esc(json.dumps(meta))}</metadata><defs>{"".join(defs)}</defs>{background}{"".join(parts)}</svg>'
    target=OUT/'svgs/star-trek-starships.svg';target.write_text(svg,encoding='utf-8')
    layout=dict(width=W,height=height,boxes=boxes,regions=regions,anchors=anchors,illustrations=placed_art,
                edition='space',record_count=len(drawn),plot_offset=590,plot_width=795,
                source_sha256=hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (OUT/'reviews/layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
    for rel in ['data/ships.json','data/ships.csv','documents/sources.html','documents/font-license.txt']:
        shutil.copyfile(PROJECT/'artifacts'/rel,OUT/rel)
    shutil.copyfile(PROJECT/'design/image-generation.json',OUT/'data/image-generation.json')
    template=(PROJECT/'scripts/viewer.html').read_text(encoding='utf-8')
    css=(PROJECT/'scripts/space-viewer.css').read_text(encoding='utf-8')
    template=template.replace('</head>','<style>'+css+'</style></head>')
    template=template.replace('Starships Through Time','Starships in Motion').replace('Starships<br>through time','Starships<br>in motion')
    template=template.replace('Construction, launch and documented use across the Prime timeline.','A journey through construction, launch and documented use. The wakes measure years.')
    template=template.replace('@@SVG@@',svg).replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')).replace('@@LAYOUT@@',json.dumps(layout))
    (OUT/'viewer/index.html').write_text(template,encoding='utf-8')
    print(json.dumps(dict(edition='space',records=len(drawn),size=[W,height],ship_art=len(placed_art),output=str(target))))


def main():
    top=header();lx=M;rx=M+CW+GAP
    ly=chapter('early',lx,top,'01','THE FIRST WARP TRAILS','Earth pioneers, prototypes and neighboring fleets.',2060,2170,[2060,2080,2100,2120,2140,2160,2170])
    ly=chapter('classic',lx,ly,'02','THE EXPLORATION AGE','The Constitution era, spore drive and film voyages.',2240,2300,list(range(2240,2301,10)))
    ly=chapter('future',lx,ly,'05','BEYOND THE BURN','The Federation reaches into the 32nd century.',3188,3200,[3188,3190,3192,3194,3196,3198,3200])
    ry=chapter('modern',rx,top,'03','FLAGSHIPS & FRONTIERS','Explorers, escorts and the next generation.',2320,2405,[2320,2340,2360,2380,2400])
    ry=chapter('neighbors',rx,ry,'04','OTHER POWERS IN FLIGHT','Rivals, allies, captives and reclaimed vessels.',2360,2405,[2360,2370,2380,2390,2400])
    y=relationships(max(ly,ry)+20)
    path(f'M{M} {y}H{W-M}',RULE,1)
    text('DATES ARE EVIDENCE. THE SPACE IS A METAPHOR.',M,y+49,34,'display',CYAN)
    para('Launch, construction, selected sightings and preservation remain distinct. Unknown dates stay unknown; uncertain years are hatched. These are individual ships, not the manufacturing spans of their classes.',M,y+87,1630,21,fill=MUTED)
    para('Artwork is a reference-guided interpretation; ship size is illustrative. Read every vessel’s source and dating notes in the companion viewer. Prime chronology remains the main frame; time-travel exceptions are labeled.',rx,y+87,CW,21,fill=MUTED)
    text('Independent educational fan atlas · 12 September 2026 · Star Trek properties belong to their respective rights holders.',M,y+214,18,fill=MUTED)
    assert sorted(drawn)==sorted(BY)
    export(math.ceil(y+261))


if __name__=='__main__':main()
