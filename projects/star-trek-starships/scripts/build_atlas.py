#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Compose the spacecraft atlas, portable viewer, and source catalogue."""
from pathlib import Path
from html import escape
from collections import Counter
import base64
import csv
import hashlib
import json
import math
from PIL import ImageFont

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
OUT=PROJECT/"artifacts"
DATA=json.loads((PROJECT/"data/ships.json").read_text(encoding="utf-8"))
BY_ID={s['id']:s for s in DATA['ships']}
BARLOW=ROOT/"skills/usefulcharts-style/assets/fonts/BarlowCondensed-Bold.ttf"
OFL=BARLOW.with_name("OFL.txt")
FONTS={"body":"C:/Windows/Fonts/arial.ttf","bold":"C:/Windows/Fonts/arialbd.ttf","display":str(BARLOW)}
FC={}
W,M,GAP=3600,76,76
CW=(W-2*M-GAP)/2
PAPER,INK,MUTED,RULE="#F4F0E5","#263B46","#536064","#CBCDC1"
COLORS={"Earth":"#77BDDD","Federation":"#7FB9D0","Vulcan":"#E8AE79","Andorian":"#8BBFC5",
    "Klingon":"#EA8B77","Romulan":"#A1BD93","Reman":"#C0B8A0","Cardassian":"#E7C65D",
    "Dominion":"#B89CCA","Borg":"#9FAF8B","Ferengi":"#EBA75C"}
parts=[];boxes=[];regions=[];anchors=[];ships_drawn=[];illustrations=[]
sn={k:i+1 for i,k in enumerate(DATA['sources'])}


def esc(s):return escape(str(s),quote=True)
def font(size,family="body"):
    k=(size,family)
    if k not in FC:FC[k]=ImageFont.truetype(FONTS[family],round(size*4))
    return FC[k]
def measure(s,size=18,family="body"):return font(size,family).getlength(s)/4
def wrap(s,w,size=18,family="body"):
    lines=[];cur=""
    for word in str(s).split():
        test=(cur+" "+word).strip()
        if cur and measure(test,size,family)>w:lines.append(cur);cur=word
        else:cur=test
    if cur:lines.append(cur)
    return lines
def rect(x,y,w,h,fill,stroke=None,sw=1,rx=0,cls=""):
    parts.append(f'<rect class="{cls}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" rx="{rx}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def path(d,stroke=INK,sw=1,fill="none",dash=None,extra=""):
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+extra+'/>')
def line(x,y,xx,yy,color=RULE,sw=1,dash=None):path(f'M{x:.2f} {y:.2f}L{xx:.2f} {yy:.2f}',color,sw,dash=dash)
def circle(x,y,r,fill,stroke=INK,sw=1):
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def text(s,x,y,size=18,family="body",color=INK,anchor="start",role="body"):
    fam="Barlow" if family=="display" else "Arial"
    weight=700 if family in ("display","bold") else 400
    parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam},sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" data-role="{role}">{esc(s)}</text>')
def para(s,x,y,w,size=18,family="body",color=INK,leading=None,role="body"):
    leading=leading or size*1.24
    lines=wrap(s,w,size,family)
    for i,v in enumerate(lines):text(v,x,y+i*leading,size,family,color,role=role)
    return y+len(lines)*leading
def pale(color,a=.8):
    vals=[round(int(color[i:i+2],16)*(1-a)+int(PAPER[i:i+2],16)*a) for i in (1,3,5)]
    return '#'+''.join(f'{v:02x}' for v in vals)


def vessel(shape,x,y,w,h,owner="Federation"):
    """Original simplified dorsal identifiers, not engineering or scale drawings."""
    if not shape:return
    illustrations.append(dict(shape=shape,x=x,y=y,w=w,h=h))
    parts.append(f'<g class="vessel-art" data-shape="{shape}" transform="translate({x:.2f},{y:.2f}) scale({w/220:.4f},{h/140:.4f})" stroke="#46575B" stroke-width="1.3" fill="#DCE2DE" stroke-linejoin="round">')
    def p(d,fill="#DCE2DE",stroke="#46575B",sw=1.3):
        parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def el(cx,cy,rx,ry,fill="#DCE2DE",stroke="#46575B",sw=1.3):
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    # Bespoke principal hulls: pylons terminate on the visible nacelles, and the
    # proportions distinguish round, broad, elongated, and split-neck designs.
    hero_shapes={"nx","constitution","constitution-refit","excelsior","ambassador","galaxy","sovereign","odyssey","constitution-iii"}
    if shape in hero_shapes:
        params={
            "nx":(56,46,48,129,208,8,11),
            "constitution":(49,40,42,100,209,10,10),
            "constitution-refit":(49,40,42,91,211,7,13),
            "excelsior":(50,43,43,82,213,20,10),
            "ambassador":(53,44,49,111,207,13,13),
            "galaxy":(60,53,65,148,209,30,15),
            "sovereign":(74,67,37,130,215,13,12),
            "odyssey":(59,52,51,128,216,6,16),
            "constitution-iii":(49,41,43,113,216,13,14),
        }
        cx,rx,ry,ns,ne,ny,nh=params[shape]
        if shape=='nx':
            p('M75 25L125 29L147 13L153 19L138 43L82 56Z')
            p('M75 115L125 111L147 127L153 121L138 97L82 84Z')
            p('M78 49L127 55L128 64L87 65M78 91L127 85L128 76L87 75',"#BACAC7")
        elif shape=='galaxy':
            p('M91 56Q128 44 151 54L182 69L151 86Q128 96 91 84Z',"#BCCDC9")
            p('M127 58L164 35L180 40L149 65M127 82L164 105L180 100L149 75')
        elif shape=='sovereign':
            p('M96 44L151 51Q185 47 206 68Q185 93 151 89L96 96Z',"#C1CECA")
            p('M151 53L174 19L189 23L178 58M151 87L174 121L189 117L178 82')
        elif shape=='odyssey':
            p('M91 47L151 44L173 34L188 16L196 21L179 53L128 64M91 93L151 96L173 106L188 124L196 119L179 87L128 76')
            p('M117 61Q165 50 204 70Q165 90 117 79Z',"#B9C9C8")
        else:
            p('M68 61L116 56Q145 48 171 68L176 72Q145 91 116 84L68 79Z',"#C1CFCA")
            attach=169 if shape=='excelsior' else 150
            p(f'M117 58L{attach} {ny+nh-2}L{attach+13} {ny+nh-2}L138 65Z')
            p(f'M117 82L{attach} {140-ny-nh+2}L{attach+13} {140-ny-nh+2}L138 75Z')
        for yy in [ny,140-ny-nh]:
            if shape in {'constitution-refit','excelsior','constitution-iii','sovereign','odyssey'}:
                p(f'M{ns} {yy}L{ne-9} {yy}L{ne} {yy+nh*.45}L{ne-9} {yy+nh}L{ns+3} {yy+nh}L{ns-5} {yy+nh*.6}Z',"#D0DBD7")
            else:
                el((ns+ne)/2,yy+nh/2,(ne-ns)/2,nh/2,"#D0DBD7")
            p(f'M{ns+14} {yy+nh*.52}H{ne-15}','none',"#699CAF",2.7)
            el(ns+4,yy+nh/2,5,nh*.32,"#B7745F",sw=.6)
            for k in range(ns+23,ne-10,10):p(f'M{k} {yy+1.3}v{nh-2.6}','none',"#A3B6B1",.55)
        el(cx,70,rx,ry,"#D9E0D8")
        el(cx,70,rx-4,ry-4,"none","#829795",1)
        el(cx,70,rx-12,ry-12,"none","#8FA29C",.6)
        for ang in range(0,360,15):
            a=math.radians(ang)
            p(f'M{cx+math.cos(a)*(rx-4):.2f} {70+math.sin(a)*(ry-4):.2f}L{cx+math.cos(a)*(rx-12):.2f} {70+math.sin(a)*(ry-12):.2f}','none',"#94A69F",.65)
        if shape in {'nx','sovereign','odyssey'}:
            p(f'M{cx} 57Q{cx+25} 44 {cx+rx-3} 56L{cx+rx+19} 64L{cx+rx+19} 76L{cx+rx-3} 84Q{cx+25} 96 {cx} 83Z',"#C0CECA")
        else:el(cx+11,70,20,12,"#BFCFC7","#7F958C",.8)
        el(cx+4,70,8,5,"#ACC1B8","#6E847B",.7)
        el(cx+2,70,3,2,"#E8ECE2","#6E847B",.6)
        p(f'M{cx-rx+3} 66V74','none',"#577D8D",1.7)
        p(f'M{cx+rx-7} 57v7M{cx+rx-7} 76v7','none',"#B87862",2)
        parts.append('</g>');return
    if shape in {"bird-of-prey","d7","vorcha","neghvar","valdore","scimitar","romulan-bop","andorian","dderidex","jemhadar","ferengi","galor","keldon"}:
        c=pale(COLORS[owner],.3)
        if shape in {"galor","keldon"}:
            p('M18 58L52 40L70 48L91 18L115 10L106 57L206 61L211 78L105 83L115 130L91 122L69 92L52 100L18 82Z',c)
            p('M41 61L193 64L193 75L41 80Z',pale(c,.4));el(52,70,14,16,pale(c,.2))
            if shape=="keldon":p('M116 53L181 53L190 62L120 62Z',c)
        elif shape=="dderidex":
            p('M14 65Q56 10 176 9L210 31Q142 31 88 62L200 61L208 79L88 78Q143 109 210 109L176 131Q56 130 14 75Z',c)
            p('M42 66Q104 43 169 32L184 38Q124 56 98 69Q128 84 184 102L169 108Q104 97 42 75Z',PAPER)
            el(28,70,22,13,c)
        elif shape in {"d7","vorcha","neghvar"}:
            p('M15 62L97 60L128 40L170 23L177 32L155 58L214 58L214 82L155 82L177 108L170 117L128 100L97 80L15 78Z',c)
            el(21,70,17,19,c);p('M95 58L139 45L163 60L163 80L139 95L95 82Z',c)
            p('M163 18L216 18L216 32L163 32Z',c);p('M163 108L216 108L216 122L163 122Z',c)
        else:
            p('M8 65L58 49L94 48L150 8L191 13L143 57L208 59L215 70L208 81L143 83L191 127L150 132L94 92L58 91L8 75Z',c)
            p('M20 67L111 60L153 69L111 80L20 73Z',pale(c,.15));el(29,70,18,12,c)
            p('M151 12L178 20M151 128L178 120M102 51L125 61M102 89L125 79','none',"#69715D",1)
    elif shape=="cube":
        p('M56 24L132 6L192 41L192 117L116 135L56 100Z',"#ACB7A2")
        p('M56 24L116 58L192 41M116 58L116 135','none')
        for i in range(7):
            u=i*9;p(f'M{60+u} {29+u*.52}L{60+u} {96+u*.52}','none',"#62715F",.8)
            p(f'M{122+u} {61-u*.22}L{122+u} {127-u*.22}','none',"#62715F",.8)
        for i in range(7):
            u=i*9;p(f'M58 {34+u}L114 {65+u}M120 {68+u}L189 {52+u}','none',"#62715F",.8)
    else:
        typ=shape
        long=typ in {"sovereign","odyssey","constitution-iii","lamarr","intrepid","protostar","nova","luna"}
        cy=70;cx=57
        rx,ry=(46,54) if typ=="galaxy" else ((57,32) if long else (43,43))
        if typ=="ambassador":rx,ry=47,49
        if typ=="nx":rx,ry=48,48
        nstart=91 if not long else 116
        nend=205
        ny=18 if not long else 33
        if typ=="nx":nstart,ny=128,8
        if typ=="crossfield":
            p('M55 68L177 15L209 20L209 120L177 125L55 72Z')
            nstart,ny=82,5
        elif typ in {"defiant","flyer","runabout","texas","dauntless"}:
            p('M12 61L43 37L108 39L155 53L185 52L205 64L205 76L185 88L155 87L108 101L43 103L12 79Z')
            p('M37 60L64 49L139 56L165 70L139 84L64 91L37 80Z',"#C2CDC9")
            el(62,70,14,9,"#E8ECE6");p('M42 47L91 45M42 93L91 95','none',"#78949C",2.6)
            parts.append('</g>');return
        elif typ in {"freighter","probe","phoenix","nx-test"}:
            p('M9 65L28 56L196 56L216 70L196 84L28 84L9 75Z')
            if typ in {"phoenix","nx-test"}:
                p('M83 59L110 19L184 15L194 27L124 30L110 60M83 81L110 121L184 125L194 113L124 110L110 80')
                el(182,21,21,6,"#B0C1C4");el(182,119,21,6,"#B0C1C4")
            else:
                for i in range(5):p(f'M{43+i*27} 42h23v56h-23Z',"#CDD6CE")
            parts.append('</g>');return
        elif typ in {"vulcan-ring","vulcan-lander"}:
            el(121,70,83,59,"none","#937251",8);p('M9 64L159 58L207 70L159 82L9 76Z',"#CFB39B")
            el(27,70,17,9,"#D6C2A4");parts.append('</g>');return
        elif typ in {"future-oval","academy","future-intrepid"}:
            el(78,70,66,42,"#D7DDD8");el(78,70,42,25,"none","#83969B",1.5)
            p('M137 56L200 33L214 37L201 53L143 65M137 84L200 107L214 103L201 87L143 75',"#CBD6D5")
            el(64,70,12,6,"#ADBCC0");parts.append('</g>');return
        else:
            p('M63 59L126 55L169 38L187 41L152 65L152 75L187 99L169 102L126 85L63 81Z')
        # Secondary hull and nacelle pylons remain separate from the saucer.
        if typ not in {"nx","crossfield","miranda","soyuz","california","walker"}:
            p('M66 62Q119 41 163 60L183 70L163 80Q119 99 66 78Z',"#C7D2D0")
        for yy in [ny,140-ny-11]:
            p(f'M{nstart} {yy}L{nend-12} {yy}Q{nend+6} {yy+5.5} {nend-12} {yy+11}L{nstart} {yy+11}Q{nstart-10} {yy+5.5} {nstart} {yy}Z',"#D6DEDA")
            p(f'M{nstart+15} {yy+5}L{nend-14} {yy+5}','none',"#73AFC6",2.6)
            el(nstart,yy+5.5,6,4,"#C88168",sw=.6)
        if typ in {"constellation","sagan","prometheus"}:
            for yy in [38,95]:p(f'M97 {yy}h103v8H97Z',"#CDD7D6")
        el(cx,cy,rx,ry)
        el(cx,cy,rx-6,ry-6,"none","#8EA1A3",.8)
        if typ=="crossfield":el(cx,cy,rx-15,ry-15,PAPER,sw=1)
        else:
            for ang in range(0,360,30):
                a=math.radians(ang)
                p(f'M{cx+math.cos(a)*(rx-7):.2f} {cy+math.sin(a)*(ry-7):.2f}L{cx+math.cos(a)*(rx-17):.2f} {cy+math.sin(a)*(ry-17):.2f}','none',"#91A1A0",.6)
        el(cx+6,cy,19,12,"#C6D2CE","#72888A",.7);el(cx+5,cy,6,4,"#A9BFC3",sw=.7)
        p(f'M{cx-rx+4} 66V74','none',"#617C87",1.8)
    parts.append('</g>')


def symbol(kind,x,y,color=INK,r=6,extra=""):
    parts.append(f'<g class="date-mark" {extra}>')
    if kind in {"launch","commission","built"}:path(f'M{x} {y-r}L{x+r} {y}L{x} {y+r}L{x-r} {y}Z',INK,1.4,color)
    elif kind in {"destroyed","wrecked"}:
        line(x-r,y-r,x+r,y+r,"#9B493C",2.3);line(x-r,y+r,x+r,y-r,"#9B493C",2.3)
    elif kind in {"retired","dismantled","abandoned"}:rect(x-r,y-r,r*2,r*2,PAPER,INK,1.6)
    elif kind=="time-jump":path(f'M{x-r} {y-r}L{x+r} {y}L{x-r} {y+r}',INK,2)
    elif kind=="reactivated":circle(x,y,r,PAPER,INK,2);circle(x,y,2,color,color,0)
    else:circle(x,y,r,color,INK,1)
    parts.append('</g>')


def hero():
    rect(0,0,W,271,INK)
    text('STAR TREK / STARSHIPS',M,182,172,"display",PAPER)
    text('THROUGH TIME     •     WHEN THEY WERE BUILT, WHEN THEY FLEW, WHAT BECAME OF THEM',M,251,25,"body",PAPER)
    count=len(DATA['ships']);operators=len({s['operator'] for s in DATA['ships']})
    text(f'{count} SPACECRAFT',W-M,115,46,"display",PAPER,"end")
    text(f'{operators} groups · Prime continuity',W-M,161,25,"body","#D2DEE0","end")
    text('Launch • documented use • final fate',W-M,204,25,"body","#D2DEE0","end")
    text('A NAME PASSED FROM SHIP TO SHIP',M,326,33,"display")
    text('Succession of the Enterprise name; spacing below is schematic, not elapsed time.',M+563,325,21,color=MUTED)
    lineage=[("enterprise-nx","NX-01","2151","Earth's warp 5 pioneer"),
        ("enterprise-1701","1701","2245","Constitution → refit"),
        ("enterprise-a","1701-A","2286","Commissioned for Kirk"),
        ("enterprise-b","1701-B","2293","Launch / Nexus rescue"),
        ("enterprise-c","1701-C","2344 · seen","Lost at Narendra III"),
        ("enterprise-d","1701-D","2363","Galaxy-class flagship"),
        ("enterprise-e","1701-E","2372","Sovereign-class explorer"),
        ("enterprise-f","1701-F","2401 · seen","Launch year unstated"),
        ("titan-a-g","1701-G","2402 · renamed","Former USS Titan-A")]
    cell=(W-2*M)/9
    for i,(id,label,date,caption) in enumerate(lineage):
        s=BY_ID[id];x=M+i*cell;cx=x+cell/2
        if i<8:path(f'M{x+cell-21} 571H{x+cell+15}',MUTED,2,extra=' marker-end="url(#arrow)"')
        vessel(s['shape'],cx-145,357,290,169)
        rect(x+23,540,cell-46,63,COLORS[s['operator']],INK,.8,4)
        text(label,cx,585,45,"display",anchor="middle",role="lineage-name")
        text(date,cx,635,24,"bold",anchor="middle",role="lineage-date")
        text(caption,cx,669,21,anchor="middle")
    text('Dorsal identifiers are original simplified drawings. They do not compare physical size or assert engineering specifications.',M,713,18,color=MUTED)
    # Compact, example-driven reading key.
    line(M,740,W-M,740,INK,2)
    text('HOW TO READ THE FLEET LANES',M,785,31,"display")
    symbol('launch',M+14,824,COLORS['Federation']);text('Diamond: known launch / commissioning / build',M+35,831,20)
    line(M+715,824,M+820,824,COLORS['Federation'],13);text('Solid: supported service or mission interval',M+838,831,20)
    line(M+1512,824,M+1612,824,MUTED,2,'6 5');symbol('active',M+1512,824,COLORS['Federation'],4);symbol('active',M+1612,824,COLORS['Federation'],4)
    text('Dots + dashes: selected attested years; gaps unverified',M+1630,831,20)
    symbol('destroyed',M+14,865);text('Cross: destroyed / wrecked',M+35,872,20)
    symbol('retired',M+715,865);text('Square: retired / dismantled / abandoned',M+738,872,20)
    symbol('time-jump',M+1512,865);text('Chevron: time displacement',M+1535,872,20)
    text('— in a launch field means unstated. A first or last sighting is not a factory production date.',M,918,22,'bold')
    x=M
    for op,c in COLORS.items():
        rect(x,946,18,18,c,INK,.5);text(op,x+26,962,20);x+=measure(op,20)+65
    return 1014


def chapter(key,x,y,num,title,sub,lo,hi,ticks):
    rows=[s for s in DATA['ships'] if s['chapter']==key]
    start=y
    rect(x,y,53,57,INK);text(num,x+26.5,y+42,38,"display",PAPER,"middle")
    text(title,x+72,y+43,41,"display")
    text(f'{lo}–{hi}',x+CW,y+42,31,"display",MUTED,"end")
    para(sub,x+72,y+81,CW-72,19,color=MUTED)
    y+=134
    # Column locations leave readable prose, exact time, and identities separate.
    labx=x+14; plotx=x+525; plotw=555; notex=x+1120; notew=CW-1134
    text('SHIP · CLASS · LAUNCH EVIDENCE',labx,y,17,"bold",MUTED)
    text('LAUNCH & KNOWN USE',plotx,y,17,"bold",MUTED)
    text('HISTORY & FATE',notex,y,17,"bold",MUTED)
    yy=y+44
    heights=[]
    for s in rows:
        ht=max(100,26+len(wrap(s['note'],notew,18))*22.3+len(wrap(s['credit']+f' [{sn[s["source"]]}]',notew,14))*17.2+13)
        heights.append(math.ceil(ht))
    bottom=yy+sum(heights)
    def px(t):return plotx+(t-lo)/(hi-lo)*plotw
    for t in ticks:
        xx=px(t);text(t,xx,y+31,16,'bold',MUTED,'middle',role='axis-year');line(xx,y+39,xx,bottom,RULE,.75)
    for idx,(s,ht) in enumerate(zip(rows,heights)):
        rid=s['id'];col=COLORS[s['operator']]
        parts.append(f'<g id="record-{rid}" class="record" data-id="{rid}" data-operator="{s["operator"]}" data-source="{esc(DATA["sources"][s["source"]]["url"])}" tabindex="0" role="button" aria-label="{esc(s["name"]+". "+s["note"])}">')
        parts.append(f'<title>{esc(s["name"]+" — "+s["note"])}</title>')
        rect(x,yy,CW,ht,'transparent',cls='hit-area')
        line(x,yy+ht,x+CW,yy+ht,RULE,.8)
        if s['important']:rect(labx-5,yy+10,482,37,pale(col,.26))
        else:rect(labx-5,yy+14,4,29,col)
        names=wrap(s['name'],467,27,'display')
        if len(names)>1:
            # Expand this identity's name area without changing the numeric timeline.
            size=25;names=wrap(s['name'],467,size,'display')
        else:size=27
        for j,n in enumerate(names):text(n,labx+6,yy+37+j*29,size,'display',role='ship-name')
        assert len(names)==1,(rid,names)
        text(s['registry']+' · '+s['design'],labx+6,yy+62,15,color=MUTED,role='identity-detail')
        lword={'launch':'Launch','commission':'Commissioned','built':'Built'}[s['launch_kind']]
        launch=f'{lword} {s["launch"]}' if s['launch'] is not None else 'Launch —'
        if s['construction'] and s['launch_kind']!='built':launch+=' · building '+', '.join(map(str,s['construction']))
        if s['shipyard'] and not s['construction']:launch+=' · '+s['shipyard']
        for j,v in enumerate(wrap(launch,468,15)):text(v,labx+6,yy+84+j*18,15,'bold',MUTED,role='launch-detail')
        obs=s['observations']; special=[q for q in s['special'] if q['kind'] in {'reactivated','active','time-arrival'} and lo<=q['year']<=hi]
        all_years=sorted(set(obs+([s['launch']] if s['launch'] is not None else [])))
        uncertain=s.get('uncertain_range')
        if uncertain:
            label='c. 2144–2145' if rid=='nx-delta' else '3190s · calendar dating disputed'
        elif s['service']:
            label=f'{s["service"][0]}–{s["service"][1]}'
            if special:label+='; '+', '.join(str(q['year']) for q in special)
        elif len(all_years)>2:
            label=' · '.join(str(v) for v in all_years)
        elif len(all_years)==2:label=f'{all_years[0]} … {all_years[1]}'
        else:label=str(all_years[0])
        text(label,plotx,yy+28,19,'bold',role='use-label')
        bar_y=yy+55
        if uncertain:
            a,b=uncertain
            parts.append(f'<g class="uncertain-span" data-start="{a}" data-end="{b}">')
            rect(px(a),bar_y-6,px(b)-px(a),12,'url(#uncertain)',MUTED,.8)
            parts.append('</g>')
            anchors.append(dict(ship=rid,kind='uncertain-range',start=a,end=b,x1=px(a),x2=px(b),scale=[lo,hi,plotx,plotw]))
        else:
            if s['service']:
                a,b=s['service']
                parts.append(f'<g class="service-span" data-start="{a}" data-end="{b}">')
                rect(px(a),bar_y-7,px(b)-px(a),14,col,INK,.5,2)
                parts.append('</g>')
                anchors.append(dict(ship=rid,kind='service',start=a,end=b,x1=px(a),x2=px(b),scale=[lo,hi,plotx,plotw]))
            elif len(all_years)>1:line(px(all_years[0]),bar_y,px(all_years[-1]),bar_y,MUTED,1.8,'6 5')
            for t in all_years:
                k=s['launch_kind'] if t==s['launch'] else ('active' if t!=obs[-1] or not s['endpoint'] else s['endpoint'])
                if t==s['launch'] and s['endpoint'] and t==obs[-1]:k='launch'
                symbol(k,px(t),bar_y,col,4.8,extra=f'data-year="{t}" data-kind="{k}"')
                anchors.append(dict(ship=rid,kind=k,year=t,x=px(t),scale=[lo,hi,plotx,plotw]))
            if s['endpoint'] and s['launch']==obs[-1]:
                symbol(s['endpoint'],px(obs[-1]),bar_y+20,col,4.8,extra=f'data-year="{obs[-1]}" data-kind="{s["endpoint"]}"')
            for q in special:
                symbol(q['kind'],px(q['year']),bar_y,col,5,extra=f'data-year="{q["year"]}" data-kind="{q["kind"]}"')
                anchors.append(dict(ship=rid,kind=q['kind'],year=q['year'],x=px(q['year']),scale=[lo,hi,plotx,plotw]))
        extras=[]
        for q in s['special']:
            if q not in special:extras.append(q['label'])
        if extras:para(' · '.join(extras),plotx,yy+88,plotw,15,color=MUTED,role='other-date')
        ty=para(s['note'],notex,yy+26,notew,18,leading=22.3)
        para(s['credit']+f' [{sn[s["source"]]}]',notex,ty+1,notew,14,color=MUTED,leading=17.2,role='source-credit')
        parts.append('</g>')
        boxes.append(dict(id=rid,x=x,y=yy,w=CW,h=ht));ships_drawn.append(rid)
        yy+=ht
    regions.append(dict(id=key,title=title,x=x,y=start,w=CW,h=yy-start))
    return yy+70


def connections(x,y,w):
    """Typed relationships supplement, rather than replace, the dated ship lanes."""
    text('SAME NAME, NEW HULL — OR THE SAME SHIP?',x,y+35,34,'display')
    stories=[('Defiant', 'Prototype destroyed 2375', 'Sao Paulo renamed 2375', 'A replacement vessel, not a repaired original.'),
        ('Delta Flyer', 'First hull built 2375', 'Second hull built 2377', 'Two separate craft assembled aboard Voyager.'),
        ('Protostar → Prodigy', 'Prototype launched 2382', 'Production ship 2385', 'A prototype design becomes a production class.'),
        ('Titan-A → Enterprise-G', 'Titan-A under Shaw', 'Enterprise-G in 2402', 'A new name and registry for the same hull.')]
    yy=y+69
    for title,a,b,note in stories:
        text(title,x+12,yy+28,28,'display')
        text(a,x+12,yy+57,19,color=MUTED)
        path(f'M{x+478} {yy+48}H{x+566}',MUTED,2,extra=' marker-end="url(#arrow)"')
        text(b,x+596,yy+57,19,'bold')
        text(note,x+12,yy+86,18)
        line(x,yy+107,x+w,yy+107,RULE,1)
        yy+=128
    regions.append(dict(id='identities',title='Ship identity and succession',x=x,y=y,w=w,h=yy-y))
    return yy+30


def identity_diagrams(y):
    """Explain the different relationships between named physical vessels."""
    line(M,y,W-M,y,INK,2)
    text('HOW ONE SHIP LEADS TO ANOTHER',M,y+52,39,'display')
    text('Relationships are schematic; a shared name or technology does not imply the same hull.',M+753,y+50,21,color=MUTED)
    stories=[
        ('NX test program', [('NX-Alpha','2143'),('NX-Beta','2143'),('NX-Delta','c. 2144–2145')],
         'Successive test vehicles. The warp 3 trials lead toward Enterprise NX-01 in 2151.', 'program'),
        ('Defiant: a replacement hull', [('Original Defiant','Launched 2370 · lost 2375'),('Sao Paulo → Defiant','Renamed 2375')],
         'The second vessel carries the name and registry after the first is destroyed.', 'replacement'),
        ('Sister ships in the NX class', [('Enterprise NX-01','Launched 2151'),('Columbia NX-02','Launched 2154')],
         'Different hulls in one class; construction of Columbia is attested in 2153.', 'sister'),
        ('Two Delta Flyers', [('First Delta Flyer','Built 2375 · lost 2377'),('Second Delta Flyer','Built 2377')],
         'Voyager builds the replacement after the first craft is lost to the Borg.', 'replacement'),
        ('Spore-drive sister ships', [('Discovery','Attested 2256'),('Glenn','Lost 2256')],
         'Parallel Crossfield-class experiments; Discovery survives the program.', 'sister'),
        ('Prototype to production ship', [('Protostar','Launched 2382'),('Prodigy','Launched 2385')],
         'A prototype design becomes a production class, with a new named vessel.', 'development'),
        ('The Voyager name across centuries', [('Voyager','Launched 2371'),('Voyager-A','Commissioned 2384'),('Voyager-J','Attested 3189')],
         'Selected bearers of the name. The leap to J omits intermediate ships.', 'name'),
        ('Titan-A becomes Enterprise-G', [('Titan-A','Attested 2396 · 2401'),('Enterprise-G','Renamed 2402')],
         'One physical vessel receives a new name and registry after Frontier Day.', 'rename'),
    ]
    for i,(title,nodes,note,kind) in enumerate(stories):
        x=M+(i%2)*(CW+GAP);yy=y+93+(i//2)*153
        parts.append(f'<g class="identity-story" data-relationship="{kind}">')
        text(title,x+12,yy+23,27,'display')
        cell=CW/len(nodes)
        for j,(name,date) in enumerate(nodes):
            xx=x+j*cell;ww=cell-65
            rect(xx+12,yy+38,ww,37,pale(COLORS['Federation'],.42),INK,.65,3)
            text(name,xx+12+ww/2,yy+64,23,'bold',anchor='middle')
            text(date,xx+12+ww/2,yy+98,18,anchor='middle',color=MUTED)
            if j<len(nodes)-1:
                if kind=='sister':
                    text('↔',xx+cell-20,yy+66,28,anchor='middle')
                else:
                    path(f'M{xx+cell-44:.2f} {yy+57}H{xx+cell+1:.2f}',MUTED,1.7,dash='4 4' if kind=='name' and j==1 else None,extra=' marker-end="url(#arrow)"')
        text(note,x+12,yy+132,19,color=MUTED)
        parts.append('</g>')
    regions.append(dict(id='identities',title='Ship relationships and identity',x=M,y=y,w=W-2*M,h=710))
    return y+739


def export(height):
    for folder in ['svgs','images','documents','viewer','data','reviews']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    b64=base64.b64encode(BARLOW.read_bytes()).decode()
    meta=dict(subject=DATA['title'],continuity=DATA['continuity'],source_file='ships.json',
        creation='Original educational composition using usefulcharts-style guidance; not an official Star Trek or UsefulCharts publication.',
        illustrations='Original simplified dorsal identifiers; not to scale or engineering-accurate.',font_license=OFL.read_text(encoding='utf-8'))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-labelledby="poster-title poster-desc">
<title id="poster-title">Star Trek: Starships Through Time</title>
<desc id="poster-desc">79 selected individual spacecraft. Separate linear chapter scales plot known launch, commissioning, active years and loss. Dashed observation envelopes do not assert continuous service. Construction dates not established are left unstated.</desc>
<metadata>{esc(json.dumps(meta,ensure_ascii=False))}</metadata>
<defs><style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{b64});font-weight:700}}text{{font-kerning:normal}}.record{{cursor:pointer}}.record:hover .hit-area{{fill:#A2BAC414}}</style>
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="{MUTED}" stroke-width="1.4"/></marker>
<pattern id="uncertain" width="7" height="7" patternUnits="userSpaceOnUse"><path d="M-1 1L6 8M3-3L10 4" stroke="#869894" stroke-width="1.4"/></pattern></defs>
<rect width="{W}" height="{height}" fill="{PAPER}"/>{''.join(parts)}</svg>'''
    (OUT/'svgs/star-trek-starships.svg').write_text(svg,encoding='utf-8')
    layout=dict(width=W,height=height,boxes=boxes,regions=regions,anchors=anchors,illustrations=illustrations,
        record_count=len(ships_drawn),source_sha256=hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest(),svg_sha256=hashlib.sha256((OUT/'svgs/star-trek-starships.svg').read_bytes()).hexdigest())
    (OUT/'reviews/layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
    (OUT/'data/ships.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'documents/font-license.txt').write_text(OFL.read_text(encoding='utf-8'),encoding='utf-8')
    with (OUT/'data/ships.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['id','name','class_or_design','registry','operator','construction_observed','launch_or_commission_year','date_type','shipyard','selected_active_years','supported_service_interval','fate','note','date_qualification','source'])
        for s in DATA['ships']:writer.writerow([s['id'],s['name'],s['design'],s['registry'],s['operator'],s['construction'],s['launch'],s['launch_kind'],s['shipyard'],s['observations'],s['service'],s['endpoint'],s['note'],s['qualifier'],DATA['sources'][s['source']]['url']])
    template=(PROJECT/'scripts/viewer.html').read_text(encoding='utf-8')
    template=template.replace('@@SVG@@',svg).replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')).replace('@@LAYOUT@@',json.dumps(layout).replace('</','<\\/'))
    (OUT/'viewer/index.html').write_text(template,encoding='utf-8')
    source_html=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Starship source ledger</title><style>body{font:17px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:0 24px;background:#f4f0e5;color:#263b46}a{color:#24618b}article{border-top:1px solid #b9c2bd;padding:16px 0}h2{margin-bottom:8px}p{margin:8px 0}small{color:#536064}</style><h1>Starship evidence ledger</h1><p>Prime continuity · Selected individual spacecraft · Research checked 12 September 2026.</p><p>Screen events and plaques take priority over games, novels and promotional timelines. Calendar conversions and disputed dates are qualified below. Unknown dates remain unknown. Source articles sometimes include apocrypha, which is not automatically part of this dataset.</p><p><a href="../viewer/index.html">Open the atlas</a> · <a href="../data/ships.json">Editable JSON</a> · <a href="../data/ships.csv">CSV</a></p>']
    for s in DATA['ships']:
        src=DATA['sources'][s['source']]
        source_html.append(f'<article id="{s["id"]}"><h2>[{sn[s["source"]]}] {esc(s["name"])}</h2><p><b>{esc(s["design"])}</b> · {esc(s["registry"])} · {esc(s["operator"])}</p><p>Construction observations: {esc(s["construction"] or "not established")}. {esc(s["launch_kind"].title())}: {esc(s["launch"] or "not established")}. Shipyard: {esc(s["shipyard"] or "not established")}.</p><p>Selected active years: {esc(s["observations"])}. Supported service/mission interval: {esc(s["service"] or "not asserted")}.</p><p>{esc(s["note"])}</p><p>{esc(s["qualifier"] or "No additional dating qualification.")}</p><p><b>Screen trail:</b> {esc(s["credit"])}</p><p><a href="{src["url"]}">{esc(src["title"])}</a> <small>— Memory Alpha; checked {src["accessed"]}</small></p></article>')
    source_html.append('<p>Additional cross-checks: <a href="https://www.startrek.com/news/enterprise-starfleets-finest-flagships">StarTrek.com: Enterprise flagships</a> · <a href="https://www.startrek.com/news/sector-001-federation-starships-of-first-contact">StarTrek.com: Sector 001 starships</a></p></html>')
    (OUT/'documents/sources.html').write_text(''.join(source_html),encoding='utf-8')
    print(json.dumps(dict(ships=len(ships_drawn),size=[W,height],anchors=len(anchors),output=str(OUT/'svgs/star-trek-starships.svg'))))


def main():
    top=hero()
    lx=M;rx=M+CW+GAP
    ly=chapter('early',lx,top,'01','FIRST WARP & EARLY FLEETS','Earth prototypes, cargo ships and neighboring civilizations.',2060,2170,[2060,2080,2100,2120,2140,2160,2170])
    ly=chapter('classic',lx,ly,'02','THE AGE OF THE CONSTITUTION','Different hulls can share a name; time jumps interrupt chronology.',2240,2300,list(range(2240,2301,10)))
    ly=chapter('future',lx,ly,'05','THE DISTANT FEDERATION','Scale jumps to the 32nd century. Discovery also reappears in 3189.',3188,3200,[3188,3190,3192,3194,3196,3198,3200])
    ry=chapter('modern',rx,top,'03','EXPLORERS, ESCORTS & SUCCESSORS','Federation ships from Picard’s first command to Enterprise-G.',2320,2405,[2320,2340,2360,2380,2400])
    ry=chapter('neighbors',rx,ry,'04','RIVALS, ALLIES & CAPTURED SHIPS','Selected individual craft. Color follows the stated origin/operator group.',2360,2405,[2360,2370,2380,2390,2400])
    y=identity_diagrams(max(ly,ry)+10)
    line(M,y,W-M,y,INK,2)
    text('BUILT IS NOT THE SAME AS FIRST SEEN',M,y+53,34,'display')
    para('Most stories identify a mission year more clearly than a construction period. Launch dates, shipyard records, selected sightings and final dispositions remain separate. The bars describe individual ships, never a factory production run for an entire class.',M,y+92,1600,21)
    text('CANON & CHRONOLOGY',M+CW+GAP,y+53,34,'display')
    para('Prime continuity is the main frame. Mirror and alternate-future visits appear only as qualified context. NX-Delta and Academy-era calendar dates are visibly uncertain. Sources and dating notes are available for every ship in the companion viewer and ledger.',M+CW+GAP,y+92,CW,21)
    y+=221
    text('Original educational atlas · 12 September 2026 · Screen titles abbreviated: ENT, TOS, TAS, TNG, DS9, VOY, DIS, LD, PRO, PIC and SA.',M,y,18,color=MUTED)
    text('Star Trek spacecraft belong to their respective rights holders. This is an independent fan reference, with original layout and schematic illustrations.',M,y+32,18,color=MUTED)
    assert sorted(ships_drawn)==sorted(BY_ID)
    export(math.ceil(y+77))


if __name__=='__main__':main()
