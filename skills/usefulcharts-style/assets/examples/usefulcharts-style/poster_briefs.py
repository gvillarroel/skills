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
    houses=['Alder','Bayeux','Corven','Daleshire','Everen','Falken','Rosene']
    d=base('aurelian-families','DYNASTIES OF THE AURELIAN COAST','genealogy',[f'House {h}' for h in houses])
    d.update(pattern_id='usefulcharts-dynastic-genealogy',subtitle='Seven courts, cadet branches, and recorded family alliances',
             reading_note='Double lines: partners. Children descend from the union. Dotted descent: uncertain. Vertical spacing is schematic, not a time scale.')
    kings=['Adrian','Edmund','Hugh','Robert','Philip','Louis','Henri','Conrad','Otto','Frederick','Alaric','Baldwin','Roland','Victor','Charles','Leo','Martin','Richard','Stephen','William','Edward','Francis','George','Albert','Julian','Henry','Arthur','Felix']
    queens=['Adele','Beatrice','Eleanor','Matilda','Isabel','Margaret','Alice','Joanna','Agnes','Emma','Sofia','Cecilia','Anne','Helena','Louise','Mary','Clara','Elise','Irene','Diana','Vera','Rose','Ada','Eve']
    d['nodes']=[dict(id='progenitor',label='Aurelian I',detail='The coastal founder · 842–889',group='g3',x=890,y=190,width=157,style='hero',icon='portrait',icon_width=38,size=16,variant=1),
        dict(id='western-heir',label='Berengar',detail='King of the western marches',group='g0',x=570,y=280,width=121,style='card'),
        dict(id='eastern-heir',label='Adalheid',detail='Queen of the eastern ports',group='g2',x=1150,y=280,width=121,style='card')]
    d['edges']=[dict(id='anc-west',source='progenitor',target='western-heir',kind='descent'),dict(id='anc-east',source='progenitor',target='eastern-heir',kind='descent')]
    crowns=['Alder','Bayeux','Corven','Daleshire','Everen','Falken','Rosene']
    by_union={}
    male_art=[862,15708,24684,864,111317,95998,89043,16367]
    female_art=[87760,78591,11390,866,105945,75374,105600,31233]
    d['nodes'][0]['icon']='museum-864'
    d['source_note']='Original synthetic genealogy · Names, dates, and relationships are invented. Public-domain museum portraits are decorative art samples, not likenesses of these fictional people.'
    counts=[24,28,22,26,21,25,23]
    ystarts=[395,447,384,438,410,478,398]
    yends=[2555,2540,2550,2565,2510,2555,2550]
    for g,house in enumerate(houses):
        origin_x=127+g*237
        d['annotations'].append(dict(x=origin_x+81,y=342,width=137,label=f'Kingdom of {crowns[g]}',kind='heading',size=21,icon='shield',group=f'g{g}',variant=g))
        previous=None
        weights=[1+.1*math.sin(r*1.7+g) for r in range(counts[g]-1)]
        levels=[ystarts[g]+sum(weights[:r])/sum(weights)*(yends[g]-ystarts[g]) for r in range(counts[g])]
        for r in range(counts[g]):
            x=origin_x+int(13*math.sin(r*.58+g));y=round(levels[r],2)
            female=(r+g*2)%7==3
            name=(queens if female else kings)[(r+g*4)%len(queens if female else kings)]
            numeral=['I','II','III','IV'][r//7]
            main=f'royal-{g}-{r}'
            feature=(r+g*3)%5==0 or r==counts[g]-1
            year=round(930+(y-384)/2176*825)
            n=dict(id=main,label=f'{name} {numeral}',detail=f'{year}–{year+28}',group=f'g{g}',x=x,y=y,width=92 if feature else 77,style='emblem' if feature else 'card',size=12.2)
            if feature:n.update(icon=f'museum-{(female_art if female else male_art)[(r+g)%8]}',icon_width=32,variant=r+g,width=112,size=12)
            if (r+g)%11==5:
                n.update(style='plain',width=73);n.pop('icon',None)
            d['nodes'].append(n)
            if previous:
                uid=by_union.get(previous)
                if uid:
                    if (r+g)%13==8:d['edges'].append(dict(id=f'uncertain-{g}-{r}',source=uid,target=main,kind='uncertain'))
                    else:next(u for u in d['unions'] if u['id']==uid)['children'].append(main)
                else:d['edges'].append(dict(id=f'parent-{g}-{r}',source=previous,target=main,kind='descent'))
            else:d['edges'].append(dict(id=f'founding-{g}',source='western-heir' if g<3 else 'eastern-heir',target=main,kind='descent',corridor_y=365+g*4))
            if (r+g)%5!=2:
                spouse=f'partner-{g}-{r}'
                partner_name=(kings if female else queens)[(r*3+g)%len(kings if female else queens)]
                d['nodes'].append(dict(id=spouse,label=partner_name,detail=f'b. {year-21}',group=f'g{g-1}' if r in (8,17,23) and g>0 else f'g{g}',x=x+107,y=y,width=70,style='plain',size=10.5))
                uid=f'union-{g}-{r}';d['unions'].append(dict(id=uid,partners=[main,spouse],children=[]));by_union[main]=uid
                if r in (8,17,23) and g>0:
                    candidates=[n for n in d['nodes'] if n['id'].startswith(f'royal-{g-1}-') and n['id'] in by_union and n['y']<y-72]
                    prior=by_union[max(candidates,key=lambda n:n['y'])['id']] if candidates else None
                    if prior:next(u for u in d['unions'] if u['id']==prior)['children'].append(spouse)
            next_gap=levels[r+1]-y if r+1<len(levels) else 90
            if r>0 and (r*3+g)%4==0 and next_gap>=87:
                child=f'cadet-{g}-{r}'
                short=['Hugh','Eve','Anna','Otto','Leo','Mary','Adele','Rose'][(r+g)%8]
                d['nodes'].append(dict(id=child,label=short,detail=f'b. {year-16}',group=f'g{g}',x=x+151,y=y+next_gap/2,width=46,style='plain' if r%3 else 'card',size=10.5))
                prior=by_union.get(previous)
                if prior:next(u for u in d['unions'] if u['id']==prior)['children'].append(child)
                else:d['edges'].append(dict(id=f'cadet-parent-{g}-{r}',source=previous,target=child,kind='descent'))
            if r in (5,12,20):
                d['annotations'].append(dict(x=x,y=y-48,width=106,label=house.upper() if r==5 else ['JUNIOR LINE','RESTORED LINE'][r==20],kind='pill',size=10.7,group=f'g{g}'))
            previous=main
    return d


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
    vocabulary=[
        ['Solar','Stellar','Lunar','Meridian','Orbital','Sidereal','Polar','Celestial','Astral','Equatorial','Deep Sky','Comet'],
        ['Coastal','Pelagic','Tidal','Harbor','Oceanic','Maritime','Compass','Estuary','Bluewater','Current','Pilot','Voyage'],
        ['Clockwork','Hydraulic','Kinetic','Engine','Precision','Steam','Applied','Workshop','Mechanical','Lever','Power','Dynamic'],
        ['Spectral','Prism','Wave','Mirror','Lens','Optical','Imaging','Glass','Luminous','Photon','Refraction','Visible'],
        ['Geodetic','Regional','Terrain','Relief','Survey','Continental','Coastline','Atlas','Spatial','Topographic','Longitude','Field']]
    endings=['Society','School','Institute','Academy','College','Union','Circle','Laboratory','Observatory','Guild','Foundation','Commons']
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
        d['nodes'].append(dict(id=root,label=roots[g],detail='The founding tradition',x=left+family_width/2,y=root_y,width=193,group=f'g{g}',style='hero',icon=symbols[g],icon_width=41,size=16))
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
                label=f'{vocabulary[g][(r*3+c)%12]} {endings[(r+c*2+g)%12]}'
                if r>=12:label='New '+label
                style='plain' if (r*3+c+g)%5 in (1,2) else 'emblem' if (r+c+g)%3==0 else 'card'
                if style=='emblem' and any(len(word)>7 for word in label.split()):style='card'
                n=dict(id=nid,label=label,detail=f'est. {round(1200+(y-700)*.42)}',x=x,y=y,width=76,group=f'g{g}',style=style,size=10.0)
                if style=='emblem':n.update(icon=symbols[(g+c)%5],icon_width=18,width=76,size=10.5)
                d['nodes'].append(n);row[c]=nid
                if r==0:source=root
                else:source=min(previous.values(),key=lambda v:abs(next(n['x'] for n in d['nodes'] if n['id']==v)-x))
                d['edges'].append(dict(id=f'branch-{nid}',source=source,target=nid,kind='branch'))
                if r in (5,11) and c==2 and 1 in previous:d['edges'].append(dict(id=f'merge-{nid}',source=previous[1],target=nid,kind='influence'))
            if r in (2,8) and r<len(row_counts)-1:
                d['annotations'].append(dict(x=left+family_width/2,y=root_y+110+r*(last_y-root_y-110)/(len(row_counts)-1)-45,width=150,label='THE REGIONAL SCHOOLS' if r<7 else 'THE OPEN SOCIETIES',kind='pill',size=10.5,group=f'g{g}'))
            previous=row
    for i,(source,target) in enumerate([('school-0-2-7','school-1-4-0'),('school-1-6-0','school-2-2-7'),('school-2-4-6','root-4'),('school-3-1-4','school-4-2-0')]):
        d['edges'].append(dict(id=f'exchange-{i}',source=source,target=target,kind='influence'))
    return d


def timeline():
    labels=['Riverlands','Highlands','Coastlands','Islands','Northlands']
    d=base('five-regional-histories','FIVE REGIONS THROUGH TIME','timeline',labels)
    for key in ('nodes','edges','unions','insets'):d.pop(key)
    d.update(pattern_id='usefulcharts-parallel-history',subtitle='A comparative chronicle of five fictional regions, 1000–2000',frame_color='#665D48',
             time=dict(start=1000,end=2000,step=25),lanes=[dict(id=f'l{i}',label=v) for i,v in enumerate(labels)],periods=[],events=[],map_texture=True,
             reading_note='Every ribbon and event uses the same linear year scale. Contemporaneous columns are comparable; adjacent phases do not imply ancestry.',
             eras=[dict(start=a,end=b,label=label) for a,b,label in [(1000,1200,'Early city states'),(1200,1450,'Maritime kingdoms'),(1450,1650,'Age of exchange'),(1650,1850,'Federations'),(1850,2000,'Modern age')]])
    local=[['Delta','Saffron','Canal','Willow','Reed','Vale','Estuary','River'],['Highland','Mountain','Ridge','Cairn','Stone','Pass','Summit','Plateau'],['Coral','Harbor','Maritime','Amber','Pearl','Coastal','Port','Bluewater'],['Island','Voyaging','Palm','Reef','Cove','Archipelago','Seafarer','Lagoon'],['Northern','Forest','Lake','Birch','Taiga','Fir','Glacial','Frontier']]
    regimes=['Settlements','Principalities','Kingdom','League','Commonwealth','Union','Federation','Republic']
    actions=['First permanent trading ports','A shared calendar is adopted','Founding of the great sky tower','New canals reshape farming','Guilds establish common weights','The first public library opens','Sea voyages link the regions','Printing brings a wider reading public','New tables guide sailors by the stars','Workshops use water power','Surveyors complete the regional atlas','The first elected assembly meets','A network of public colleges opens','Steam routes connect inland towns','Shared postal and telegraph networks','The charter of regional union']
    icons=['ship','obelisk','observatory','leaf','wheel','book','compass','press','astrolabe','machine','globe','tower','archive','ship','gear','book']
    d['transitions']=[]
    for g in range(5):
        for track in range(2):
            first=[[1000,1105],[1060,1000],[1000,1270],[1110,1040],[1000,1190]][g][track]
            last=2000 if track==0 else [1940,2000,1975,1920,2000][g]
            count=[[9,6],[7,10],[11,5],[6,9],[8,7]][g][track]
            weights=[.8+.6*math.sin(i*1.3+g+track)**2 for i in range(count)]
            years=[round(first+sum(weights[:i])/sum(weights)*(last-first),1) for i in range(count+1)]
            previous=None
            for i,(a,b) in enumerate(zip(years,years[1:])):
                if i:a+=4 if i%3 else 13
                term=local[g][(i+track*3)%8]
                regime=regimes[min(7,int(i/count*8))]
                offset=12+track*160+[0,9,-3,12,5][(i+g+track)%5]
                bar_width=[21,24,57,21,31,67,21][(i+g*2+track)%7]
                size=10.8 if bar_width<24 else 12.2 if bar_width<50 else 16
                # A short interval cannot carry a long rotated name in one line.
                if b-a<72 and len(f'{term} {regime}')>19:bar_width=max(35,bar_width);size=11.4
                nid=f'period-{g}-{track}-{i}'
                d['periods'].append(dict(id=nid,label=f'{term} {regime}',group=f'g{g}',lane=f'l{g}',start=a,end=b,offset=offset,bar_width=bar_width,size=size))
                if previous:d['transitions'].append(dict(id=f'continuation-{g}-{track}-{i}',source=previous,target=nid,kind='succession',style='ribbon' if i%4 in (1,2) else 'dotted'))
                previous=nid
                fractions=(.09,.6) if b-a>110 else (.15,)
                for k,fraction in enumerate(fractions):
                    phrase=actions[min(15,int((a-1000)/1000*16)+k)]
                    e=dict(lane=f'l{g}',year=a+(b-a)*fraction,label=phrase,offset=offset+bar_width+8,width=154-(offset-track*160+bar_width+8),group=f'g{g}',size=9.8)
                    if (i+g+track+k)%4==0 and (b-a>100 or len(fractions)==1):
                        artwork=[90589,57819,246,60878,191,50240,27881,15190][(i+g+track)%8]
                        e.update(icon=f'object-{artwork}',art_size=56)
                    d['events'].append(e)
    d['source_note']='Original synthetic history · Dates and events are invented. Public-domain museum objects are decorative collection samples, not evidence of these events.'
    d['reading_note']='One linear year scale. Filled and dotted bridges are declared continuations, not ancestry. Decorative map: Natural Earth. Artwork provenance is embedded in the SVG.'
    return d


if __name__=='__main__':
    print('Import the three fixture functions from build_examples.py.')
