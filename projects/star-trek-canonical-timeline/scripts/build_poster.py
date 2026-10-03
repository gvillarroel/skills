#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Compose an editable, source-attributed schematic history poster and viewer."""
from pathlib import Path
from collections import defaultdict
from html import escape
import base64
import hashlib
import json
import math
import re
from PIL import ImageFont

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
DATA_PATH = PROJECT / "data/timeline.json"
DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))
TOTAL = sum(len(DATA[k]) for k in ['events','origins','future','branches'])
OUT = PROJECT / "artifacts"
W, M = 3600, 66
PAPER, INK, MUTED, RULE = "#F5F0E4", "#222C2B", "#4F5651", "#B9B7A9"
DARK = "#41483F"
COLORS = {
    "Federation":"#77BDDD", "Vulcan":"#E7A879", "Andorian":"#94C7D8",
    "Romulan":"#98BD92", "Reman":"#98BD92", "Klingon":"#F17B66",
    "Cardassian":"#F2C84B", "Bajoran":"#E7A786", "Dominion":"#B69AC8",
    "Breen":"#C1B1D7", "Borg":"#A2B49B", "8472":"#DBB98E",
    "Ferengi":"#EFAD56", "Gorn":"#AACCA3", "Kelpien":"#A5C6C4",
    "Metron":"#D5CFB3", "Tholian":"#DCA46F", "Talaxian":"#D7BA95",
    "Douwd":"#C4B5CC", "Talarian":"#DAC29C", "Kazon":"#CFBFA8",
    "Vidiian":"#C7B1A3", "Q":"#D1ABD0", "Hirogen":"#AEBAB2",
    "Vaadwaur":"#BAB8A3", "Xindi":"#E9B76D", "Pakled":"#BFAF90",
    "Vau N'Akat":"#CFABD5", "Ba'ku":"#D8BFA0", "Suliban":"#B6C797",
    "Kzinti":"#CAA673", "Tzenkethi":"#CFB58D", "Other":"#D4CCB8"
}
BARLOW = ROOT / "skills/usefulcharts-style/assets/fonts/BarlowCondensed-Bold.ttf"
FONT = {"body":Path("C:/Windows/Fonts/arial.ttf"),
        "bold":Path("C:/Windows/Fonts/arialbd.ttf"), "display":BARLOW}
FONTS = {}
parts, boxes, regions, links = [], [], [], []
source_numbers = {key:i for i,key in enumerate(DATA["sources"],1)}
placed = set()

def esc(s): return escape(str(s), quote=True)
def font(size, family="body"):
    key=(size,family)
    if key not in FONTS: FONTS[key]=ImageFont.truetype(str(FONT[family]),size*4)
    return FONTS[key]
def width(s,size,family="body"): return font(size,family).getlength(s)/4
def wrap(s,max_width,size=21,family="body"):
    lines=[]; line=""
    for word in str(s).split():
        test=(line+" "+word).strip()
        if line and width(test,size,family)>max_width:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines
def rect(x,y,w,h,fill,stroke=None,sw=1,rx=0,cls=""):
    parts.append(f'<rect class="{cls}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def line(x1,y1,x2,y2,color=RULE,sw=1.2,dash=None):
    parts.append(f'<path d="M{x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f}" fill="none" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def circle(x,y,r,fill,stroke=None,sw=1):
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def text(s,x,y,size=21,family="body",fill=INK,anchor="start",role="body"):
    cssfamily="Barlow" if family=="display" else "Arial"
    weight="700" if family in ("display","bold") else "400"
    parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{cssfamily},sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" data-role="{role}">{esc(s)}</text>')
def paragraph(s,x,y,w,size=21,family="body",fill=INK,leading=None,role="body"):
    leading=leading or size*1.27
    for i,v in enumerate(wrap(s,w,size,family)): text(v,x,y+i*leading,size,family,fill,role=role)
    return y+len(wrap(s,w,size,family))*leading
def section(y,num,title,dates,note=""):
    line(M,y,W-M,y,INK,2)
    rect(M,y,58,58,DARK)
    text(num,M+29,y+41,36,"display",PAPER,"middle")
    text(title,M+77,y+44,43,"display")
    text(dates,W-M,y+43,37,"display",MUTED,"end")
    if note: text(note,M+79,y+76,19,"body",MUTED)
    return y+101
def event_height(e,w,compact=False):
    title_size=26 if e.get("kind") in {"war","milestone","battle","catastrophe"} else 24
    h=20+len(wrap(e["label"],w-39,title_size,"display"))*27
    h+=len(wrap(e["detail"],w-40,18))*22.7
    h+=len(wrap(e["credit"]+f' [{source_numbers[e["source"]]}]',w-40,14))*17
    return h+23
def event(e,x,y,w,actor=None,compact=False):
    assert e["id"] not in placed,e["id"]
    placed.add(e["id"])
    color=COLORS.get(actor or e.get("actor"),COLORS["Other"])
    h=event_height(e,w,compact)
    important=e.get("kind") in {"war","milestone","battle","catastrophe"}
    title_size=26 if important else 24
    parts.append(f'<g id="{e["id"]}" class="record" data-source="{e["source"]}" data-actor="{esc(e.get("actor",actor or "context"))}" data-year="{esc(e["date"])}" tabindex="0" role="button" aria-label="{esc(e["date"]+": "+e["label"])}">')
    parts.append(f'<title>{esc(e["date"]+" — "+e["label"]+". "+e["detail"]+" Source: "+e["credit"])}</title>')
    rect(x,y,w,h,"transparent",cls="hit-area")
    rect(x,y+22,6,h-35,color)
    circle(x+3,y+9,4.8,color,INK,0.8)
    # The date belongs to this event, never to an entire horizontal row.
    text(e["date"],x+18,y+14,16,"bold",MUTED,role="date")
    ty=y+44
    title_lines=wrap(e["label"],w-39,title_size,"display")
    if important: rect(x+16,y+23,w-20,len(title_lines)*27+6,color)
    for i,v in enumerate(title_lines): text(v,x+22,ty+i*27,title_size,"display",role="event-title")
    ty=y+23+len(title_lines)*27+23
    ty=paragraph(e["detail"],x+19,ty,w-40,18,leading=22.7)
    paragraph(e["credit"]+f' [{source_numbers[e["source"]]}]',x+19,ty+1,w-40,14,fill=MUTED,leading=17,role="credit")
    parts.append('</g>')
    boxes.append(dict(id=e["id"],x=x,y=y,w=w,h=h,label=e["label"]))
    return y+h
def columns(y,groups,weights=None):
    """Pack subjects independently; dates, not baselines, establish chronology."""
    weights=weights or [1]*len(groups); gap=35
    unit=(W-2*M-gap*(len(groups)-1))/sum(weights)
    ends=[]; x=M
    for i,(title,actor,items) in enumerate(groups):
        w=unit*weights[i]
        color=COLORS.get(actor,COLORS["Other"])
        rect(x,y,w,46,color,INK,1)
        text(title,x+14,y+33,30,"display")
        py=y+69
        previous=None
        for e in sorted(items,key=lambda z:z.get("year",0)):
            if previous:
                line(x+3,previous,x+3,py+4,color,3)
                links.append(dict(type="reading-sequence",source=previous_id,target=e["id"]))
            py=event(e,x,py,w)+13
            previous=py-26
            previous_id=e["id"]
        ends.append(py); x+=w+gap
    return max(ends)
def compact_cards(y,records,cols=6,actors=None):
    gap=33; w=(W-2*M-gap*(cols-1))/cols; py=y
    for start in range(0,len(records),cols):
        end=[]
        for i,e in enumerate(records[start:start+cols]):
            end.append(event(e,M+i*(w+gap),py,w,actor=actors[start+i] if actors else None))
        py=max(end)+23
    return py
def pill(label,x,y,w,color,subtitle=None):
    rect(x,y,w,48,color,INK,1.4,3)
    text(label,x+w/2,y+33,28,"display",anchor="middle")
    if subtitle: text(subtitle,x+w/2,y+75,19,"body",MUTED,"middle")
def arrow(points,label,tx,ty,color=INK,dashed=False,source=None,target=None,kind="political"):
    d="M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in points)
    parts.append(f'<path class="relationship" data-relation="{kind}" d="{d}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" marker-end="url(#arrow)"'+(' marker-start="url(#arrow)"' if kind=='war' else '')+(' stroke-dasharray="9 6"' if dashed else '')+'/>')
    lw=width(label,18,"bold")
    rect(tx-lw/2-8,ty-19,lw+16,26,PAPER)
    text(label,tx,ty,18,"bold",color,"middle",role="relationship-label")
    links.append(dict(type=kind,source=source,target=target,label=label))
def foundation(y,ufp):
    # Four founding members enter one federal polity; this does not erase their identity.
    by=y+12
    worlds=[("EARTH",M+35,260,"Federation"),("VULCAN",M+505,270,"Vulcan"),
            ("ANDORIA",W-M-805,285,"Andorian"),("TELLAR",W-M-340,270,"Other")]
    targetx=W/2-445
    h=event_height(ufp,890)
    for label,x,w,actor in worlds:
        pill(label,x,by,w,COLORS[actor])
        cx=x+w/2
        arrow([(cx,by+48),(cx,by+105),(W/2,by+105),(W/2,by+143)],
              "founding member",cx,by+94,COLORS[actor],source=label,target=ufp["id"],kind="founding-member")
    event(ufp,targetx,by+150,890)
    # An original schematic of interstellar polity, without borrowed logos or ship art.
    paragraph("The Federation is a political union. Species, planets and governments are different kinds of entity; a species can span more than one polity.",M+35,by+172,840,22,fill=MUTED)
    paragraph("The Romulan war is fought before the Federation exists. Later Federation-Romulan encounters should not be projected backward onto the 2156-2160 conflict.",W-M-875,by+172,820,22,fill=MUTED)
    return by+150+h+18
def war_network(y):
    x=M; inner=W-2*M
    rect(x,y,inner,362,"#ECE7DA",INK,1.2,5)
    text("WHO FIGHTS WITH WHOM?",x+24,y+42,34,"display")
    text("Dominion War • 2373-2375 • alliances change during the war",x+478,y+40,21,"body",MUTED)
    # Coalition membership is explicit; the antagonistic relation is between coalitions.
    pill("FEDERATION",x+50,y+80,380,COLORS["Federation"])
    pill("KLINGON EMPIRE",x+510,y+80,370,COLORS["Klingon"])
    pill("ROMULAN STAR EMPIRE",x+960,y+80,445,COLORS["Romulan"])
    pill("DOMINION",x+1810,y+80,390,COLORS["Dominion"])
    pill("CARDASSIAN UNION",x+2280,y+80,445,COLORS["Cardassian"])
    pill("BREEN",x+2870,y+80,340,COLORS["Breen"])
    ally_y=y+207
    line(x+240,y+128,x+240,ally_y,COLORS["Federation"],5)
    line(x+695,y+128,x+695,ally_y,COLORS["Klingon"],5)
    line(x+1182,y+128,x+1182,ally_y,COLORS["Romulan"],5)
    line(x+240,ally_y,x+1182,ally_y,"#547C81",5)
    for cx,label in [(x+695,'restored 2373'),(x+1182,'joins 2374')]:
        rect(cx-width(label,18,'bold')/2-7,y+142,width(label,18,'bold')+14,25,'#ECE7DA')
        text(label,cx,y+161,18,'bold',anchor='middle')
    line(x+2005,y+128,x+2005,ally_y,COLORS["Dominion"],5)
    line(x+2502,y+128,x+2502,ally_y,COLORS["Cardassian"],5)
    line(x+3040,y+128,x+3040,ally_y,COLORS["Breen"],5)
    line(x+2005,ally_y,x+3040,ally_y,"#8F76A4",5)
    for cx,label in [(x+2502,'joins 2373'),(x+3040,'joins 2375')]:
        rect(cx-width(label,18,'bold')/2-7,y+142,width(label,18,'bold')+14,25,'#ECE7DA')
        text(label,cx,y+161,18,'bold',anchor='middle')
    arrow([(x+1182,ally_y),(x+2005,ally_y)],"WAR 2373-2375",x+1590,ally_y-4,"#A64334",source="Federation-led alliance",target="Dominion-led coalition",kind="war")
    # The switch uses its own lower corridor and terminates on the allied coalition.
    arrow([(x+2502,ally_y+3),(x+2502,y+271),(x+690,y+271),(x+690,ally_y+4)],
          "Cardassian fleet switches sides at the final battle • 2375",x+1600,y+266,"#73570F",source="Cardassian Union",target="Federation-led alliance",kind="side-change")
    text("BAJOR",x+2780,y+286,27,"display")
    paragraph("2373 nonaggression pact: neutrality, not Dominion membership.",x+2780,y+313,590,19,fill=MUTED)
    text("SON'A",x+35,y+303,24,"display")
    text("Supply ketracel-white to the Dominion. [20]",x+143,y+303,18,"body",MUTED)
    text("A coalition is not a merger: each government retains its own interests.",x+35,y+333,20,"body",MUTED)
    for s,t,date in [("Klingon Empire","Federation-led alliance","2373"),("Romulan Star Empire","Federation-led alliance","2374"),("Cardassian Union","Dominion-led coalition","2373"),("Breen","Dominion-led coalition","2375")]:
        links.append(dict(type="coalition-membership",source=s,target=t,date=date))
    links.append(dict(type="nonaggression",source="Bajor",target="Dominion",date="2373"))
    return y+390

def export(y):
    H=math.ceil(y+20)
    expected={e["id"] for k in ("events","origins","future","branches") for e in DATA[k]}
    assert placed==expected, {"missing":list(expected-placed),"extra":list(placed-expected)}
    font64=base64.b64encode(BARLOW.read_bytes()).decode()
    defs=f'<defs><style>@font-face{{font-family:Barlow;src:url(data:font/ttf;base64,{font64}) format("truetype");font-weight:700}} .record:focus{{outline:none}} .record:focus .hit-area{{stroke:#24344d;stroke-width:3}} text{{font-kerning:normal}}</style><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="poster-title poster-description"><title id="poster-title">Star Trek: Civilizations, Wars and the Prime Timeline</title><desc id="poster-description">A dense schematic chronology with 152 attributed entries, political coalition diagrams, ancient context, the 32nd century, and eight separately identified alternative histories. Dates are explicit; spacing is not a uniform elapsed-time scale.</desc>{defs}<rect width="{W}" height="{H}" fill="{PAPER}"/>'+''.join(parts)+'</svg>'
    svg=svg.replace('152 attributed entries',f'{TOTAL} attributed entries')
    license_text=(BARLOW.parent/'OFL.txt').read_text(encoding='utf-8')
    svg=svg.replace('</desc>','</desc><metadata id="font-license">'+esc(license_text)+'</metadata>',1)
    target=OUT/"svgs/star-trek-timeline.svg"; target.write_text(svg,encoding="utf-8")
    manifest=dict(width=W,height=H,records=len(placed),record_ids=sorted(placed),regions=regions,boxes=boxes,
                  links=links,data_sha256=hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  design="Schematic chronological columns within eras; chronological links do not assert descent or a duration.",
                  typography=dict(body_px=18,credit_px=14,min_date_px=16),color_by_actor=COLORS)
    (OUT/"reviews/layout.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    write_viewer(svg,manifest)
    print(json.dumps({"svg":str(target),"width":W,"height":H,"records":len(placed),"relationships":len(links)}))

def write_viewer(svg,manifest):
    entries=[e for key in ("events","origins","future","branches") for e in DATA[key]]
    payload=json.dumps(dict(entries=entries,sources=DATA["sources"],regions=regions,colors=COLORS),ensure_ascii=False).replace("</","<\\/")
    # This viewer is an artifact, not a published website. All content is local.
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Star Trek — Civilizations & Wars</title><style>
    *{box-sizing:border-box}body{margin:0;background:#d5d5cb;color:#202b2a;font:15px Arial,sans-serif}header{height:72px;background:#27352f;color:#f7f1e6;display:flex;align-items:center;gap:16px;padding:12px 22px;position:fixed;inset:0 0 auto;z-index:5;box-shadow:0 1px 6px #0004}header strong{font-size:19px;white-space:nowrap}button,select,input,.download{font:inherit;border:1px solid #b1b5aa;border-radius:5px;background:#faf7ef;color:#24382f;padding:9px 11px}button,.download{cursor:pointer}button:hover,.download:hover{background:#e0eee3}input{min-width:130px;width:230px}.download{text-decoration:none;font-size:13px}#viewport{position:absolute;inset:72px 340px 0 0;overflow:auto;padding:25px;cursor:grab;touch-action:pan-x pan-y}#paper{margin:0 auto;box-shadow:0 4px 25px #0003;width:900px}#paper svg{width:100%;height:auto;display:block}aside{position:fixed;top:72px;right:0;bottom:0;width:340px;padding:24px;background:#fbf8f0;border-left:1px solid #b7b9ae;overflow:auto}aside h1{font-size:25px;margin:0 0 10px}aside h2{font-size:18px;margin:24px 0 10px}aside p{line-height:1.5}aside a{color:#225e82;overflow-wrap:anywhere}.muted{font-size:13px;color:#667064}.small{font-size:12px;line-height:1.5}.record{cursor:pointer}.record:hover .hit-area{stroke:#617558;stroke-width:2;fill:#fff1}.record.selected .hit-area{stroke:#245b7e;stroke-width:5;fill:#9bc8e31a}.record.match .hit-area{stroke:#9c6220;stroke-width:4;fill:#f1c36e33}#results button{display:block;text-align:left;width:100%;margin:6px 0;font-size:13px}#zoomvalue{min-width:44px;font-size:13px}#reset{margin-top:15px}details{margin:16px 0}summary{cursor:pointer}#legend div{margin:8px 0;font-size:13px}#legend span{display:inline-block;width:13px;height:13px;margin-right:8px;border:1px solid #2223;vertical-align:middle}@media(max-width:1000px){aside{width:270px;padding:18px}#viewport{right:270px}header{gap:7px;padding:8px}header strong{display:none}input{width:145px}.download{padding:9px 7px}select{max-width:145px}}@media(max-width:700px){aside{display:none}#viewport{right:0}select{display:none}.download{display:none}header{flex-wrap:wrap;height:104px}#viewport{top:104px}}
    </style><header><strong>STAR TREK / ATLAS</strong><button id="fit" title="Fit the whole poster">Fit</button><button id="minus" aria-label="Zoom out">−</button><span id="zoomvalue"></span><button id="plus" aria-label="Zoom in">+</button><button id="read">Read</button><select id="jump" aria-label="Jump to era"><option value="">Jump to era…</option></select><input id="search" type="search" placeholder="Find a civilization, war, year…" aria-label="Search the poster"><a class="download" href="../svgs/star-trek-timeline.svg" download>SVG</a><a class="download" href="../documents/star-trek-timeline.pdf" download>PDF</a></header><main id="viewport"><div id="paper">'''+svg+'''</div></main><aside><h1>Civilizations,<br>wars & continuity</h1><p class="muted">152 entries · Ancient history to the 32nd century · 8 alternative histories</p><div id="selection"><p>Choose an entry on the poster for its episode credit and source. Use <b>Read</b> for comfortable type, or jump to an era.</p><p class="small">Read down within each branch. Dates are authoritative; horizontal alignment and spacing do not express equal elapsed time.</p></div><div id="results"></div><details><summary>Color key</summary><div id="legend"></div></details><details><summary>Scope and dating</summary><p class="small">Selected major on-screen events, with Prime continuity as the main story. Books, games and speculative continuations are excluded. Kelvin, Mirror, erased and conditional histories are separated. Approximate or conflicting dates are visible. A contact, raid or catastrophe is not automatically a declared war.</p><p class="small">Compiled 12 September 2026. An original fan reference; independent of UsefulCharts and the Star Trek rights holders.</p></details></aside><script id="data" type="application/json">'''+payload+'''</script><script>
    const data=JSON.parse(document.getElementById('data').textContent), viewport=document.getElementById('viewport'),paper=document.getElementById('paper'),records=new Map(data.entries.map(e=>[e.id,e]));
    let scale=0.25,drag=null;const baseWidth='''+str(W)+''',baseHeight='''+str(manifest['height'])+''';
    function setScale(next,cx=viewport.clientWidth/2,cy=viewport.clientHeight/2){next=Math.max(.07,Math.min(1.8,next));const ratio=next/scale;const sx=(viewport.scrollLeft+cx)*ratio-cx,sy=(viewport.scrollTop+cy)*ratio-cy;scale=next;paper.style.width=baseWidth*scale+'px';document.getElementById('zoomvalue').textContent=Math.round(scale*100)+'%';viewport.scrollLeft=sx;viewport.scrollTop=sy;}
    function fit(){setScale(Math.min((viewport.clientWidth-50)/baseWidth,(viewport.clientHeight-50)/baseHeight));viewport.scrollLeft=0;viewport.scrollTop=0;}
    function focusRecord(id){const el=document.getElementById(id),e=records.get(id);if(!el||!e)return;document.querySelectorAll('.record.selected').forEach(e=>e.classList.remove('selected'));el.classList.add('selected');const box=el.getBBox();if(scale<.62)setScale(.72);viewport.scrollTop=Math.max(0,box.y*scale-150);viewport.scrollLeft=Math.max(0,box.x*scale-70);const panel=document.getElementById('selection');panel.replaceChildren();const title=document.createElement('h2');title.textContent=e.date+' · '+e.label;panel.append(title);const p=document.createElement('p');p.textContent=e.detail;panel.append(p);const credit=document.createElement('p');credit.className='small';credit.textContent='On-screen anchor: '+e.credit;panel.append(credit);const a=document.createElement('a');a.href=data.sources[e.source].url;a.target='_blank';a.rel='noopener';a.textContent=data.sources[e.source].title+' ↗';panel.append(a);history.replaceState(null,'','#'+id);}
    document.getElementById('fit').onclick=fit;document.getElementById('read').onclick=()=>setScale(.72);document.getElementById('plus').onclick=()=>setScale(scale*1.35);document.getElementById('minus').onclick=()=>setScale(scale/1.35);
    document.querySelectorAll('.record').forEach(el=>{el.onclick=()=>{if(!drag?.moved)focusRecord(el.id)};el.onkeydown=e=>{if(e.key==='Enter')focusRecord(el.id)}});
    data.regions.forEach(r=>{const o=document.createElement('option');o.value=r.id;o.textContent=r.id.replaceAll('-',' ');document.getElementById('jump').append(o)});document.getElementById('jump').onchange=e=>{const r=data.regions.find(r=>r.id===e.target.value);if(r){setScale(.40);viewport.scrollTop=r.y*scale;viewport.scrollLeft=0;}};
    document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();document.querySelectorAll('.record.match').forEach(el=>el.classList.remove('match'));const results=document.getElementById('results');results.replaceChildren();if(q.length<2)return;const matches=data.entries.filter(r=>[r.label,r.detail,r.date,r.actor,r.credit].join(' ').toLowerCase().includes(q));const p=document.createElement('p');p.className='muted';p.textContent=matches.length+' matching entries';results.append(p);matches.forEach(r=>{document.getElementById(r.id).classList.add('match');const b=document.createElement('button');b.textContent=r.date+' · '+r.label;b.onclick=()=>focusRecord(r.id);results.append(b)});});
    Object.entries(data.colors).filter(([k])=>!['Other','Reman','Metron','Douwd','Talarian','Vidiian','Talaxian',"Ba'ku",'Vaadwaur','Kazon','Pakled'].includes(k)).forEach(([name,color])=>{const d=document.createElement('div'),s=document.createElement('span');s.style.background=color;d.append(s,document.createTextNode(name));document.getElementById('legend').append(d)});
    viewport.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,sx:viewport.scrollLeft,sy:viewport.scrollTop,moved:false};});viewport.addEventListener('pointermove',e=>{if(!drag||!e.buttons)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>6)drag.moved=true;if(drag.moved){viewport.scrollLeft=drag.sx-dx;viewport.scrollTop=drag.sy-dy;}});window.addEventListener('pointerup',()=>setTimeout(()=>drag=null,10));viewport.addEventListener('wheel',e=>{if(e.ctrlKey){e.preventDefault();const r=viewport.getBoundingClientRect();setScale(scale*Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top)}},{passive:false});document.fonts.ready.then(()=>{fit();if(location.hash)focusRecord(location.hash.slice(1));});
    </script></html>'''
    html=html.replace('152 entries',f'{TOTAL} entries').replace('152 historical entries',f'{TOTAL} historical entries')
    (OUT/"viewer/index.html").write_text(html,encoding="utf-8")

if __name__=="__main__":
    from build_dense_poster import main
    main()
