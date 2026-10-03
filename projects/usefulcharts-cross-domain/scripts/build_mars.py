#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Render historical launch campaigns with a uniform calendar x axis."""
from pathlib import Path
import base64
import html
import json
import sys
import re
import copy
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT.parents[1]/'skills/usefulcharts-style/scripts'
sys.path.insert(0,str(SCRIPTS))
from render_chart import wrap, viewer
from pack_shared_rows import pack
from audit_panel_poster import audit

BG='#0B1B2A';INK='#F1F4F3';MUTED='#BBCBD1'
NASA='https://mars.nasa.gov/system/downloadable_items/45585_mars_2020_landing_press_kit.pdf'

def inventory():
    # Unit: one named launch campaign, including explicitly described payloads.
    # Years are deliberately coarser than conflicting day-level table entries.
    rows=[
      ('marsnik1','Marsnik 1','ussr',1960,None,'Flyby','Failed to reach Earth orbit'),
      ('marsnik2','Marsnik 2','ussr',1960,None,'Flyby','Failed to reach Earth orbit'),
      ('sputnik22','Sputnik 22','ussr',1962,None,'Flyby','Reached Earth orbit only'),
      ('mars1','Mars 1','ussr',1962,None,'Flyby','Radio failed en route; end year not plotted'),
      ('sputnik24','Sputnik 24','ussr',1962,None,'Flyby','Reached Earth orbit only'),
      ('mariner3','Mariner 3','us',1964,None,'Flyby','Launch shroud failed to separate'),
      ('mariner4','Mariner 4','us',1964,1965,'Flyby','1965: first successful Mars flyby; 21 photos'),
      ('zond2','Zond 2','ussr',1964,None,'Flyby','Radio failed; end year not plotted'),
      ('mariner6','Mariner 6','us',1969,1969,'Flyby','1969: Mars flyby; 75 photos'),
      ('mariner7','Mariner 7','us',1969,1969,'Flyby','1969: Mars flyby; 126 photos'),
      ('mars69a','Mars 1969A','ussr',1969,None,'Orbiter','Failed to reach Earth orbit'),
      ('mars69b','Mars 1969B','ussr',1969,None,'Orbiter','Launch failed'),
      ('mariner8','Mariner 8','us',1971,None,'Orbiter','Launch failed'),
      ('kosmos419','Kosmos 419','ussr',1971,None,'Mars mission','Reached Earth orbit only'),
      ('mars2','Mars 2','ussr',1971,1971,'Orbiter + lander','1971: reached Mars; lander crashed'),
      ('mars3','Mars 3','ussr',1971,1971,'Orbiter + lander','1971: landed; signal ceased after seconds'),
      ('mariner9','Mariner 9','us',1971,1971,'Orbiter','1971–72: orbital operations; 7,329 photos'),
      ('mars4','Mars 4','ussr',1973,1974,'Orbiter','1974: flew past Mars; orbit insertion failed'),
      ('mars5','Mars 5','ussr',1973,1974,'Orbiter','1974: reached orbit; operated briefly'),
      ('mars6','Mars 6','ussr',1973,1974,'Flyby + lander','1974: lander crashed on arrival'),
      ('mars7','Mars 7','ussr',1973,1974,'Flyby + lander','1974: lander missed Mars'),
      ('viking1','Viking 1','us',1975,1976,'Orbiter + lander','1976: orbit insertion and landing'),
      ('viking2','Viking 2','us',1975,1976,'Orbiter + lander','1976: orbit insertion and landing'),
      ('phobos1','Phobos 1','ussr',1988,None,'Orbiter + Phobos lander','1988: lost en route to Mars'),
      ('phobos2','Phobos 2','ussr',1988,1989,'Orbiter + Phobos lander','1989: contact lost near Phobos'),
      ('observer','Mars Observer','us',1992,None,'Orbiter','1993: contact lost before orbit insertion'),
      ('mgs','Mars Global Surveyor','us',1996,1997,'Orbiter','1997: arrived; last contact in 2006'),
      ('mars96','Mars 96','russia',1996,None,'Orbiter + surface probes','Launch failed; one campaign, five probes'),
      ('pathfinder','Mars Pathfinder','us',1996,1997,'Lander + Sojourner rover','1997: landed; last contact that year'),
      ('nozomi','Nozomi','japan',1998,None,'Orbiter','2003: failed to enter Mars orbit'),
      ('climate','Mars Climate Orbiter','us',1998,None,'Orbiter','1999: lost on arrival'),
      ('polar','Mars Polar Lander / DS2','us',1999,None,'Lander + two penetrators','1999: all three lost on arrival'),
    ]
    nodes=[]
    for i,label,g,launch,arrival,role,detail in rows:
        country={'us':'USA','ussr':'USSR','russia':'RUSSIA','japan':'JAPAN'}[g]
        n=dict(id=i,label=label,group=g,launch=launch,arrival=arrival,role=role,detail=detail,
               date_label=f'{launch} · {country} · {role}',source_url=NASA+'#page='+str(69 if launch<=1971 and i not in ['mars3','mariner9'] else 70),spans=[])
        nodes.append(n)
        found=re.match(r'(\d{4}):',detail)
        n['outcome']=int(found[1]) if arrival is None and found else None
    by={n['id']:n for n in nodes}
    by['mariner9']['spans']=[dict(label='Orbit',start=1971,end=1972)]
    by['viking1']['spans']=[dict(label='Orbiter',start=1976,end=1980),dict(label='Lander',start=1976,end=1982)]
    by['viking2']['spans']=[dict(label='Orbiter',start=1976,end=1978),dict(label='Lander',start=1976,end=1980)]
    by['mgs']['spans']=[dict(label='Operations',start=1997,end=2006)]
    return dict(id='mars-launches-1960-1999',title='THE LONG ROAD TO MARS',nodes=nodes,edges=[],
        groups=[dict(id='us',label='USA',color='#7AD7EE'),dict(id='ussr',label='USSR',color='#FFA893'),dict(id='russia',label='Russia',color='#D7BCFA'),dict(id='japan',label='Japan',color='#F8D381')],
        source_note='NASA, Mars 2020 Landing Press Kit (2021), pp. 69–70. Years are used because some day-level entries conflict with mission histories. This is a selected historical launch-campaign view, not a current mission-status catalog.',
        reading_note='One record is one launch campaign, which may carry several spacecraft. Circles mark launches, diamonds Mars encounters and crosses dated final losses on a uniform year scale. Dashed lines join dated events; only labeled solid bars indicate supported operations. Missing end dates remain unplotted.',
        scale=dict(start=1960,end=2007,left=105,pixels_per_year=58),width=2990)

def make(source,reuse):
    by={n['id']:n for n in source['nodes']};colors={g['id']:g['color'] for g in source['groups']}
    scale=source['scale'];date=lambda year:scale['left']+(year-scale['start'])*scale['pixels_per_year']
    measured=[];lines={}
    for n in by.values():
        labels=wrap(n['label'],275,22,True);kickers=wrap(n['date_label'],275,15);details=wrap(n['detail'],275,17)
        lines[n['id']]=[('label',t,22) for t in labels]+[('kicker',t,15) for t in kickers]+[('detail',t,17) for t in details]
        yy=sum(size*1.25 for _,_,size in lines[n['id']])+14
        end=max([n['launch'],n['arrival'] or n['launch'],n['outcome'] or n['launch']]+[s['end'] for s in n['spans']])
        measured.append(dict(id=n['id'],owner=n['id'],x0=date(n['launch'])-9,x1=max(date(n['launch'])+282,date(end)+85),height=yy+37+len(n['spans'])*31))
    model=dict(mode='numeric',width=source['width'],top=285,gap=18,track_gap=24,row_gap=24,
        reuse_tracks=reuse,labels_in_footprints=True,
        records=measured,groups=[dict(id=g['id'],members=[n['id'] for n in by.values() if n['group']==g['id']]) for g in source['groups']])
    packed=pack(model);layout=packed['layout'];height=layout['height']+180;pieces=[];esc=lambda t:html.escape(str(t),quote=True)
    font=base64.b64encode((SCRIPTS.parent/'assets/fonts/BarlowCondensed-Bold.ttf').read_bytes()).decode()
    pieces.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{source["width"]}" height="{height}" viewBox="0 0 {source["width"]} {height}" role="img" aria-labelledby="title desc"><title id="title">{source["title"]}</title><desc id="desc">{esc(source["reading_note"])}</desc><style>@font-face{{font-family:Poster;src:url(data:font/ttf;base64,{font})}}text{{font-family:Arial,sans-serif}}.display{{font-family:Poster,Arial,sans-serif}}</style><rect width="{source["width"]}" height="{height}" fill="{BG}"/>')
    def txt(x,y,t,size=17,color=INK,extra=''):
        pieces.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" data-background="{BG}" {extra}>{esc(t)}</text>')
    txt(72,55,'1960–1999 LAUNCH CAMPAIGNS / SELECTED OPERATIONS THROUGH 2006',18,'#F8D381','letter-spacing="2.6"')
    txt(68,144,source['title'],78,INK,'class="display"')
    txt(72,190,f'32 launch campaigns • 4 national programs • {layout["row_count"]} shared tracks',22)
    for j,g in enumerate(source['groups']):txt(1780+j*235,105,g['label'],23,g['color'],'font-weight="700"')
    txt(1780,145,'○ Launch     ◇ Mars encounter     × Final loss     ━ Operations',21,MUTED)
    txt(1780,185,'X = calendar year. Equal distances mean equal elapsed years.',19,MUTED)
    for yr in range(1960,2008):
        x=date(yr);major=yr%5==0
        pieces.append(f'<line x1="{x}" x2="{x}" y1="245" y2="{layout["height"]+15}" stroke="{MUTED}" stroke-opacity="{.22 if major else .07}"/>')
        if major:txt(x-22,250,str(yr),20,MUTED)
    for b in layout['boxes']:
        n=by[b['id']];x=date(n['launch']);y=b['y'];color=colors[n['group']]
        pieces.append(f'<g data-record-id="{n["id"]}" id="record-{n["id"]}"><rect data-record-box="true" x="{b["x"]}" y="{y}" width="{b["w"]}" height="{b["h"]}" fill="none"/>')
        yy=y
        for role,line,size in lines[n['id']]:
            yy+=size*1.25;txt(x,yy,line,size,color if role=='label' else MUTED,extra=f'data-role="{role}"'+(' font-weight="700"' if role=='label' else ''))
        yy+=22
        if n['arrival'] is not None:
            arrival=date(n['arrival']);pieces.append(f'<path d="M {x} {yy} H {arrival}" stroke="{color}" stroke-width="2" stroke-dasharray="4 4"/>')
            pieces.append(f'<path data-date-owner="{n["id"]}" data-date-type="encounter" data-year="{n["arrival"]}" data-calendar-x="{arrival}" d="M {arrival} {yy-6} l 6 6 l -6 6 l -6 -6 Z" fill="{BG}" stroke="{color}" stroke-width="1.8"/>')
        if n['outcome'] is not None:
            outcome=date(n['outcome']);pieces.append(f'<path d="M {x} {yy} H {outcome}" stroke="{color}" stroke-width="2" stroke-dasharray="4 4"/>')
            pieces.append(f'<path data-date-owner="{n["id"]}" data-date-type="outcome" data-year="{n["outcome"]}" data-calendar-x="{outcome}" d="M {outcome-5} {yy-5} l 10 10 M {outcome-5} {yy+5} l 10 -10" fill="none" stroke="{color}" stroke-width="2"/>')
        pieces.append(f'<circle data-date-owner="{n["id"]}" data-date-type="launch" data-year="{n["launch"]}" data-calendar-x="{x}" cx="{x}" cy="{yy}" r="3.5" fill="{color}"/>')
        for s in n['spans']:
            yy+=31;start=date(s['start']);end=date(s['end'])
            pieces.append(f'<path data-span-owner="{n["id"]}" data-start="{s["start"]}" data-end="{s["end"]}" d="M {start} {yy} H {end}" stroke="{color}" stroke-width="5"/>')
            txt(end+10,yy+5,f'{s["end"]}',15,color)
            # Component identity is printed in a separate band above its interval.
            txt(start,yy-8,s['label'],14,color)
        pieces.append('</g>')
    if reuse:
        # Place source-backed context in an independently checked empty pocket.
        left=date(1978);pw=date(1987)-left-30
        occupied=[b for b in layout['boxes'] if b['x']<left+pw+20 and b['x']+b['w']>left-20]
        counts=Counter(n['group'] for n in by.values())
        blocks=[('A COUNT OF CAMPAIGNS',f'{len(by)} launch campaigns: '+', '.join(f'{counts[g["id"]]} {g["label"]}' for g in source['groups'])+'. Each campaign appears once, regardless of its number of payloads.'),
          ('A GAP IN NEW LAUNCHES','No mission in this inventory launched from 1976 through 1987. Hardware launched with Viking in 1975 continued operating during part of that gap.'),
          ('TWO VIKINGS, FOUR VEHICLES','Viking 1 and Viking 2 are two campaigns. Each carried an orbiter and a lander. The component endpoints span 1978, 1980 and 1982.'),
          ('FIVE PROBES, ONE ATTEMPT','Mars 96 planned one orbiter, two landers and two penetrators. The launch failed before that architecture could be used at Mars.')]
        entries=[];dy=100
        for heading,body in blocks:
            entries.append((26,heading,28,'#F8D381','class="display"',dy));dy+=30
            for line in wrap(body,pw-52,20):entries.append((26,line,20,MUTED,'',dy));dy+=27
            dy+=27
        candidates=sorted({285,*[b['y']+b['h']+25 for b in occupied]})
        cy=next((y for y in candidates if y+dy<=layout['height']-10 and all(y+dy+20<=b['y'] or y>=b['y']+b['h']+20 for b in occupied)),None)
        if cy is not None:
            pieces.append(f'<rect data-context-pocket="true" x="{left}" y="{cy}" width="{pw}" height="{dy}" fill="{BG}" stroke="#496071"/>')
            txt(left+26,cy+35,'REFERENCE DESK / NOT A TIME INTERVAL',15,MUTED)
            for dx,value,size,color,extra,offset in entries:txt(left+dx,cy+offset,value,size,color,extra)
            layout['context_pocket']=dict(x=left,y=cy,w=pw,h=dy)
    yy=layout['height']+65
    for note in [source['reading_note'],source['source_note']]:
        for line in wrap(note,source['width']-145,17):txt(72,yy,line,17,MUTED);yy+=24
    pieces.append(f'<metadata id="poster-source">{esc(json.dumps(source,ensure_ascii=False))}</metadata></svg>')
    return '\n'.join(pieces),packed

def main():
    source=inventory();(ROOT/'data/mars.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    for name,reuse in [('baseline',False),('revision-2',True)]:
        source=inventory()
        if reuse:source['scale']['pixels_per_year']=85;source['width']=4285
        out=ROOT/'artifacts'/name/'mars';out.mkdir(parents=True,exist_ok=True)
        svg,layout=make(source,reuse)
        (out/'poster.svg').write_text(svg,encoding='utf-8');(out/'source.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
        (out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8');(out/'poster.html').write_text(viewer(svg,source['title']),encoding='utf-8')
        report=audit(out/'poster.svg',out/'source.json',out/'poster.png',out/'poster.pdf')
        (out/'browser.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(variant=name,status=report['status'],findings=report['findings'],canvas=report['canvas'],rows=layout['layout']['row_count'],reused=layout['layout']['cross_group_rows'])))

if __name__=='__main__':main()
