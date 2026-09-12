#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Original synthetic acceptance data for dense editorial poster compositions."""

import json
import math
from pathlib import Path

COLORS=['#F56550','#77BDDD','#F2C529','#98BD92','#B88BC6','#F49A2C','#EBA1BA','#B7B3A1']


def base(identifier,title,mode,labels):
    return dict(id=identifier,title=title,mode=mode,design='editorial',width=1800,height=2700,font_size=12.2,
        imprint=['ORIGINAL STUDY','Synthetic source data','2026 · Editable SVG'],
        groups=[dict(id=f'g{i}',label=label,color=COLORS[i]) for i,label in enumerate(labels)],
        source_note='Original synthetic study · All people, institutions, events, dates, and relationships are invented. Vector illustrations are fictional.',
        nodes=[],edges=[],unions=[],annotations=[],insets=[])


def genealogy():
    from genealogy_brief import build_genealogy
    return build_genealogy(base)


def lineage():
    labels=['Astronomy','Navigation','Mechanics','Optics','Cartography','Common origins']
    d=base('atlas-of-inquiry','AN ATLAS OF SHARED INQUIRY','lineage',labels)
    d['groups'][-1]['color']='#A6A18B'
    d.update(pattern_id='usefulcharts-branching-lineage',subtitle='The fictional schools and societies of five scholarly traditions',
        reading_note='Solid lines: institutional branching. Dotted arrows: influence. Vertical placement is schematic. Map colors are invented illustrative assignments.')
    origin=[('oral','Oral calendars',900,166,80),('craft','Artisan traditions',776,220,84),('record','Written records',1012,222,82),('measure','Early measurement',896,293,106),('study','Schools of natural study',899,370,128),('inquiry','COMMON INQUIRY',899,461,160),('archive','The shared archive',899,557,136)]
    for i,(nid,label,x,y,w) in enumerate(origin):
        d['nodes'].append(dict(id=nid,label=label,detail='' if i<3 else ['','', '', 'c. 1080','c. 1160','Five branches of study','A common scholarly record'][i],x=x,y=y,width=w,group='g5',style='plain' if i<3 else 'pill' if i<5 else 'emblem',icon='book' if i>=5 else None,icon_width=32,size=14 if i>=5 else 12))
    for i,(s,t) in enumerate([('oral','craft'),('oral','record'),('craft','measure'),('record','measure'),('measure','study'),('study','inquiry'),('inquiry','archive')]):d['edges'].append(dict(id=f'origin-{i}',source=s,target=t,kind='branch',weight=3.6))
    d['insets']=[dict(kind='isotype',title='Institutions in the five traditions',box=[84,180,400,423]),dict(kind='map',title='Illustrative regional presence',box=[1225,181,470,365],countries={},note='Synthetic assignments · Geographic outlines: Natural Earth')]
    continents={'Europe':'g4','Asia':'g0','Africa':'g3','North America':'g2','South America':'g1','Oceania':'g1'}
    for c in json.loads((Path(__file__).resolve().parents[2]/'maps/world-countries.json').read_text(encoding='utf-8'))['countries']:
        d['insets'][1]['countries'][c['id']]=continents.get(c['continent'],'g2')
    roots=['Celestial Observatories','Maritime Academies','Schools of Mechanical Arts','Colleges of Light','Geographical Societies']
    symbols=['star','ship','wheel','lens','globe']
    places=['Lorn','Alder','Bayeux','Corven','Dale','Everen','Falken','Rosene','Varda','Mere','Tarn','Linden','Iona','Keld','Oris','Brune','Edda','Haven','Sorn','Fenn','Luma','Neris','Oriel','Rook','Silva','Thorn','Vey','Wren','Yarrow','Aster','Cairn','Elvan','Glen','Isen','Leven','Mora','Nacre']
    institution_types=[
        ['Sky Office','Sun College','Star House','Sky Survey','Transit House','Deep Sky Lab'],
        ['Pilot Guild','Tide School','Chart Office','Sea College','Harbor Board','Ocean School','Pilot Union','Tide Institute','Sea Survey','Mariners Guild','Port Academy','Route Service'],
        ['Tool Guild','Water School','Clock House','Engine Works','Power College','Design Office'],
        ['Glass Guild','Lens School','Light College','Imaging Lab'],
        ['Field Office','Survey Corps','Atlas House','Mapping Agency']]
    founding_notes=['Calendars become systematic observations','Pilot guilds formalize sea knowledge','Instrument makers organize workshops','Glassmakers develop optical methods','Navigation gives rise to public surveys']
    movement_labels=['MERIDIAN NETWORKS','OPEN-OCEAN PILOTAGE','PRECISION WORKSHOPS','SCHOOLS OF REFRACTION','PUBLIC SURVEY OFFICES']
    # Families occupy unequal historical regions of the page. Later traditions
    # branch from earlier institutions instead of restarting five equal columns.
    profiles=[
        (65,1160,728,1360,[3,6,9,11,10,9]),
        (1280,420,800,1930,[2,3,3,2,3,3,3,2,3,3,2,3]),
        (65,1160,1510,2010,[4,6,8,10,11,10]),
        (65,595,2140,2550,[3,5,6,6]),
        (755,945,2160,2550,[4,7,9,10])]
    branch_origins=['archive','archive','school-0-5-6','school-2-5-1','school-1-11-2']
    for g in range(5):
        left,family_width,root_y,last_y,row_counts=profiles[g];root=f'root-{g}'
        d['annotations'].append(dict(x=left+family_width/2,y=root_y-62,width=178,label=labels[g].upper(),kind='pill',group=f'g{g}',size=13))
        d['nodes'].append(dict(id=root,label=roots[g],detail=founding_notes[g],x=left+family_width/2,y=root_y,width=193,group=f'g{g}',style='hero',icon=symbols[g],icon_width=41,size=16,detail_size=9.5))
        d['edges'].append(dict(id=f'first-branch-{g}',source=branch_origins[g],target=root,kind='branch',corridor_y=620+g*9 if g<2 else root_y-102,weight=4.2))
        previous={}
        for r,count in enumerate(row_counts):
            slots=list(range(count))
            row={}
            for c in slots:
                nid=f'school-{g}-{r}-{c}'
                spread=.72 if r==0 else .9 if r<3 else 1
                if count==max(row_counts):spread=1
                offset=(family_width-88)*(c/(count-1)-.5)*spread
                x=left+family_width/2+offset
                y=root_y+110+r*(last_y-root_y-110)/(len(row_counts)-1)+8*math.sin(r*1.5+c*2+g)
                label=f'{places[(r*7+c+g*5)%len(places)]} {institution_types[g][r]}'
                style='plain' if (r*3+c+g)%5 in (1,2) else 'emblem' if (r+c+g)%3==0 else 'card'
                if style=='emblem' and any(len(word)>7 for word in label.split()):style='card'
                n=dict(id=nid,label=label,detail=f'est. {round(1200+(y-700)*.42)}',x=x,y=y,width=85,group=f'g{g}',style=style,size=10.0)
                if style=='emblem':n.update(icon=symbols[g],icon_width=18,width=89,size=10)
                d['nodes'].append(n);row[c]=nid
                if r==0:source=root
                else:source=min(previous.values(),key=lambda v:abs(next(n['x'] for n in d['nodes'] if n['id']==v)-x))
                d['edges'].append(dict(id=f'branch-{nid}',source=source,target=nid,kind='branch'))
                if r in (5,11) and c==2 and 1 in previous:d['edges'].append(dict(id=f'merge-{nid}',source=previous[1],target=nid,kind='influence'))
            if r in (2,8) and r<len(row_counts)-1:
                d['annotations'].append(dict(x=left+family_width/2,y=root_y+110+r*(last_y-root_y-110)/(len(row_counts)-1)-45,width=176,label=movement_labels[g] if r<7 else 'STEAM ROUTE SERVICES',kind='pill',size=10.5,group=f'g{g}'))
            previous=row
    for i,(source,target) in enumerate([('school-0-2-7','school-1-4-0'),('school-1-6-0','school-2-2-7'),('school-2-4-6','root-4'),('school-3-1-4','school-4-2-0')]):
        d['edges'].append(dict(id=f'exchange-{i}',source=source,target=target,kind='influence'))
    return d


def timeline():
    from timeline_brief import build_timeline
    return build_timeline(base)


if __name__=='__main__':
    print('Import the three fixture functions from build_examples.py.')
