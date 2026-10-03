#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Author a complete fictional chronology with independently varying regional histories."""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'projects/usefulcharts-style/artifacts/reviews/varied-chronology-v34'
SKILL = ROOT/'skills/usefulcharts-style'
sys.path.insert(0,str(SKILL/'scripts'))
from editorial_poster import EditorialPoster
from pack_timeline_events import pack_events, event_candidates, obstacles_for
from render_chart import viewer, wrap
from timeline_geometry import lane_geometry

# Local identity | complete name | start | end | center fraction | width | type | predecessors.
# A stem records the complete quiet continuity. A horizontal name remains
# inside a short dated ribbon; no date is lengthened to make a label fit.
# Prefix a predecessor with ? only when the fictional source states uncertainty.
HISTORIES = [r'''
reed|Reed settlements|400|645|.08|23|stem|
willow|Willow chiefdoms|460|805|.78|23|stem|
delta|Delta towns|670|950|.09|27|ribbon|reed
canal|Canal lords|600|1010|.47|23|stem|
saffron|Saffron kingdom|830|1130|.78|37|ribbon|willow
river|Empire of the Rivers|1040|1320|.25|57|major|delta,canal
marsh|Marsh republics|1145|1530|.79|23|stem|saffron
upper|Upper River court|1340|1535|.11|30|ribbon|river
lower|Lower River league|1340|1660|.39|29|ribbon|river
reedcourt|Reed restoration|1560|1725|.08|34|ribbon|upper
granary|Granary compact|1555|1590|.77|104|horizontal|marsh
eastmarch|Eastern marches|1610|1800|.75|24|ribbon|granary
saffron2|Saffron assembly|1690|1720|.29|110|horizontal|lower
canal2|Canal commonwealth|1740|1865|.37|47|major|saffron2
reedrepublic|Reed republic|1755|1880|.08|29|ribbon|reedcourt
eastrepublic|Eastern republic|1825|1960|.78|28|ribbon|eastmarch
convention|River convention|1890|1920|.29|111|horizontal|reedrepublic,canal2
federation|River federation|1930|2000|.28|48|ribbon|convention
estuary|Estuary free cities|1885|2000|.08|23|ribbon|
basin|Basin union|1970|2000|.78|100|horizontal|eastrepublic
''',r'''
clans|Mountain clans|400|755|.13|23|stem|
cairn|Cairn sanctuary|535|960|.89|25|stem|
pass|Pass confederacy|790|1070|.13|38|ribbon|clans
cairncourt|Court of Cairn|985|1250|.89|31|ribbon|cairn
ridge|Ridge duchies|1100|1370|.09|25|ribbon|pass
stone|Stone valley|1100|1435|.41|24|stem|pass
abbeys|Mountain abbeys|1280|1590|.89|22|stem|cairncourt
silver|Silver crown|1395|1660|.12|52|major|ridge
cantons|Free cantons|1460|1830|.43|27|ribbon|stone
prelates|Prelates' league|1620|1740|.89|26|ribbon|abbeys
regency|Silver regency|1680|1710|.12|106|horizontal|silver
westcrown|Western crown|1730|1830|.13|33|ribbon|regency
eastcantons|Eastern cantons|1760|1880|.89|29|ribbon|prelates
compact|Summit compact|1850|1875|.25|112|horizontal|westcrown,cantons
highunion|Highland union|1890|2000|.26|51|major|compact
eastcharter|Eastern charter|1910|2000|.89|31|ribbon|eastcantons
''',r'''
amber|Amber coast towns|410|685|.09|24|stem|
coral|Coral harbors|510|880|.46|26|stem|
pilots|Strait pilots|550|1020|.84|22|stem|
ambercourt|Amber court|710|970|.10|32|ribbon|amber
coralrepublic|Coral republic|910|1140|.47|34|ribbon|coral
pearl|Pearl sea league|995|1210|.10|37|ribbon|ambercourt
strait|Strait protectorate|1045|1260|.84|27|ribbon|pilots
maritime|Maritime Empire|1235|1480|.33|58|major|pearl,coralrepublic
outer|Outer coast ports|1290|1735|.93|22|stem|strait
north|Northern sea crown|1505|1760|.09|32|ribbon|maritime
free|Free port league|1505|1600|.30|32|ribbon|maritime
south|Southern coast|1505|1865|.53|27|ribbon|maritime
merchant|Merchant council|1620|1650|.30|109|horizontal|free
harbor|Harbor federation|1670|1825|.30|37|ribbon|merchant
outercouncil|Outer coast council|1760|1835|.93|31|ribbon|outer
amber2|Amber republic|1780|1900|.10|29|ribbon|north
coral2|Coral federation|1850|2000|.31|47|major|harbor
pearldom|Pearl dominion|1860|1935|.93|27|ribbon|outercouncil
southernrep|Southern republic|1890|2000|.44|27|ribbon|south
amberunion|Amber union|1920|2000|.10|35|ribbon|amber2
freeports|Free outer ports|1960|2000|.93|100|horizontal|pearldom
''',r'''
palm|Palm settlements|620|1030|.15|23|stem|
western|Western island routes|745|1190|.78|22|stem|
reef|Reef chiefdoms|1055|1370|.12|29|ribbon|palm
cove|Cove communities|1065|1290|.45|22|stem|palm
leagues|Western leagues|1220|1470|.78|32|ribbon|western
voyage|Voyaging alliance|1395|1660|.28|55|major|reef,cove
outer|Outer-island councils|1500|1780|.79|24|stem|leagues
lagoon|Lagoon kingdom|1690|1890|.06|36|ribbon|voyage
central|Central island league|1690|1830|.47|29|ribbon|voyage
westerncouncil|Western island council|1805|1880|.80|31|ribbon|outer
assembly|Island assembly|1855|1900|.30|106|horizontal|central
charter|Lagoon charter|1910|2000|.12|37|ribbon|lagoon
federation|Voyaging federation|1925|2000|.60|55|major|assembly,westerncouncil
''',r'''
forest|Forest communities|400|920|.10|24|stem|
lakes|Lake traders|480|1150|.70|25|stem|
birch|Birch federation|950|1285|.10|42|ribbon|forest
taiga|Taiga clans|1190|1470|.76|26|stem|lakes
west|Western forest estates|1310|1560|.09|29|ribbon|birch
east|Eastern forest estates|1310|1480|.39|27|ribbon|birch
north|Northern court|1500|1680|.50|36|ribbon|taiga
frontier|Frontier settlements|1530|1860|.90|23|stem|?east
winter|Winter convention|1585|1615|.09|107|horizontal|west
western|Western kingdom|1640|1800|.11|46|major|winter
taigarep|Taiga republic|1710|1890|.50|31|ribbon|north
congress|Northern congress|1820|1880|.11|37|ribbon|western
frontierrep|Frontier republic|1890|2000|.90|31|ribbon|frontier
federal|Northern federation|1920|2000|.13|51|major|congress,taigarep
taigaunion|Taiga union|1930|2000|.78|28|ribbon|
''']

# Each note belongs to a stated year and region. Uneven dates are authored
# history, not a random jitter applied after layout. Technologies are fictional
# contextual subjects; real source drawings are not evidence for these dates.
NOTES = [r'''
430|The first embankments|River villages share the work of containing spring floods.
555|A clay register|Scribes record grain owed to the common store.|illustration-cuneiform-tablet
725|Markets in the delta|A permanent exchange connects the lower river towns.
870|The saffron road|Merchants establish a protected route to the inland court.
990|A common measure|Market wardens adopt one standard for grain and cloth.
1090|The river charter|Two courts surrender their separate tolls to the new empire.
1180|The flood survey|Surveyors map embankments beyond the old city limits.|illustration-theodolite-psf
1270|Water courts|Judges divide irrigation rights between farms and towns.
1380|Two successor courts|The imperial provinces retain rival systems of revenue.
1455|Letters of passage|Carriers gain access to every market of the lower league.
1580|The granary compact|Marsh councils pool emergency food reserves.
1665|Printed river tables|Pilots compare seasonal soundings and safe passages.|illustration-printing-press-bookman
1765|Canal schools|Engineers train apprentices in surveying and lock construction.
1835|Steam packets|Scheduled boats connect inland manufacturing towns.
1900|The river convention|Delegates negotiate a shared customs administration.
1950|The basin authority|A joint agency coordinates reservoirs and power.
''',r'''
465|Salt over the passes|Seasonal pack routes connect isolated upland communities.
650|The Cairn archive|Monasteries preserve land grants and family records.
840|The bridge levy|Pass councils collect money for crossings and mountain shelters.|illustration-suspension-bridge
1030|Winter refuges|The court protects travelers on the high road.
1140|Three jurisdictions|Ridge, Stone and Cairn maintain separate courts.
1320|The abbey schools|Teachers circulate calendars and copied manuscripts.
1450|Silver workings|Deep mines transform the ridge settlements.
1530|The coin ordinance|A common standard links the western markets.
1640|Precision workshops|Craftsmen specialize in clock escapements.|illustration-clock-escapement
1725|The relay post|Fresh horses keep the winter mail road open.|illustration-stagecoach
1790|A joint survey|Cantons commission a map of their common boundaries.
1860|The summit compact|Local courts survive under a shared council.
1935|The mountain railway|A new pass carries freight across the union.
1970|Regional colleges|Technical schools form a shared university council.
''',r'''
445|Harbor soundings|Pilots keep a list of sheltered anchorages.
615|The strait passages|Navigators record seasonal winds and coastal currents.
760|Seasonal convoys|Merchants coordinate voyages beyond the inner sea.|illustration-square-rigged-ship
945|The pilots' guild|Experienced crews certify new harbor navigators.
1100|The sea register|Ships carry common papers between the league's ports.
1295|A maritime court|One tribunal hears disputes between imperial harbors.
1390|An ocean atlas|Chartmakers compare observations from distant voyages.
1550|Three coastal states|Separate administrations inherit the imperial docks.
1640|The merchant council|A temporary chamber settles the free ports' debts.
1720|The offshore survey|Crews chart the outer banks and tidal channels.|illustration-sextant-1904
1805|The public observatory|New tables guide regular crossings of the straits.|illustration-astrolabe-observation
1880|Ocean steam routes|Scheduled services replace seasonal sail crossings.
1940|Dockworkers organize|Port unions negotiate shared working conditions.
1980|The commercial code|Four coastal states agree common shipping rules.
''',r'''
490|Reading the swells|Navigators teach the routes between inhabited reefs.
710|A reef calendar|Seasonal gatherings follow tides and migrating birds.
890|Deep-water canoes|Longer hulls carry families beyond the inner islands.
1130|The shell exchange|Ceremonial gifts sustain relations across the archipelago.
1280|Two voyaging traditions|Western crews and reef navigators preserve distinct routes.
1450|Harbor sanctuary|Allied islands offer shelter to visiting crews.
1585|Schools of navigation|Experienced navigators formalize route instruction.
1735|The island chronicle|Scribes collect oral accounts of early migrations.
1820|Outer-island assemblies|Local councils negotiate their own trading agreements.
1880|A common revenue|Delegates agree how to fund inter-island services.
1960|Regular ferries|Scheduled crossings connect hospitals and schools.
''',r'''
450|Markets on the ice|Winter roads connect forest settlements and lake towns.
700|The birch record|Traders keep account marks on thin bark sheets.
1020|A northern compact|Forest councils guarantee safe passage through their lands.
1225|The lake road|Portages connect two major navigable watersheds.
1400|Survey lodges|Teams record boundaries before new farms are granted.
1560|A navigable frontier|Settlers extend the canal road beyond the old estates.
1650|A winter observatory|Long observations improve the northern calendar.|illustration-telescope-observer
1755|The timber code|New limits protect forests beside the principal waterways.
1850|A continental congress|Representatives agree common trade and border rules.
1940|Electrifying the lakes|Hydroelectric schemes supply the industrial towns.
1980|The public university|Regional colleges adopt a common charter.
''']


def brief():
    labels=['Riverlands','Highlands','Coastlands','Islands','Northlands']
    d=dict(id='five-regional-histories',pattern_id='usefulcharts-parallel-history',
           title='FIVE REGIONS THROUGH TIME',subtitle='Independent histories, shifting states and shared inventions in a fictional world, 400–2000',
           design='editorial',mode='timeline',width=2100,height=3150,frame_color='#665D48',
           imprint=['ORIGINAL STUDY','Fictional world history','Editable SVG'],font_size=12.2,
           groups=[dict(id=f'g{i}',label=label,color=color) for i,(label,color) in enumerate(zip(labels,['#F56550','#77BDDD','#F2C529','#98BD92','#B88BC6']))],
           lanes=[dict(id=f'l{i}',label=label,weight=weight) for i,(label,weight) in enumerate(zip(labels,[1.05,1,1.17,.86,.92]))],
           periods=[],transitions=[],events=[],annotations=[],map_texture='milner-1850',
           time=dict(start=400,end=2000,step=50),
           eras=[dict(start=a,end=b,label=label) for a,b,label in [(400,800,'Early communities'),(800,1200,'Courts and sea leagues'),(1200,1500,'Regional empires'),(1500,1800,'Successor states'),(1800,2000,'Constitutions and unions')]],
           source_note='Original fictional study. All polities, events, years and relations are invented. Public-domain contextual drawings retain their real provenance in the SVG.',
           reading_note='One numeric year scale. Width denotes emphasis, not territory. Thin stems and full bands show exact durations. Bridges show explicit succession, division or union; dots mark uncertain continuity. Images and the historical map illustrate subjects, not these fictional regions.')
    lanes=lane_geometry(d['lanes'],d['width'])
    for i,block in enumerate(HISTORIES):
        records=[]
        for row in block.strip().splitlines():
            key,name,start,end,cx,width,style,parents=row.split('|')
            period=dict(id=f'p{i}-{key}',label=name,start=int(start),end=int(end),lane=f'l{i}',group=f'g{i}',
                        offset=float(cx)*lanes[f'l{i}'][1]-float(width)/2,bar_width=float(width),size=18 if style=='major' else 12.4)
            if style=='stem':period.update(treatment='stem',stem_width=4)
            if style=='horizontal':period.update(label_orientation='horizontal',size=12.4)
            else:
                height=(period['end']-period['start'])*(d['height']-302)/1600
                lines=wrap(name,height-14,period['size'],True)
                period['bar_width']=max(period['bar_width'],math.ceil(len(lines)*period['size']*1.1+6))
            period['offset']=max(5,min(lanes[f'l{i}'][1]-period['bar_width']-5,float(cx)*lanes[f'l{i}'][1]-period['bar_width']/2))
            d['periods'].append(period);records.append((key,parents.split(',') if parents else []))
        incoming={key:parents for key,parents in records}
        outgoing={key:[] for key,_ in records}
        for target,parents in records:
            for parent in parents:outgoing[parent.lstrip('?')].append(target)
        for target,parents in records:
            for parent in parents:
                uncertain=parent.startswith('?');source=parent.lstrip('?')
                kind='uncertain' if uncertain else 'union' if len(parents)>1 else 'division' if len(outgoing[source])>1 else 'succession'
                d['transitions'].append(dict(id=f't{i}-{source}-{target}',source=f'p{i}-{source}',target=f'p{i}-{target}',kind=kind,
                    style='dotted' if uncertain else 'ribbon',source_port=.5,target_port=.5,ribbon_width=7 if kind in ('division','union') else 0))
        for number,row in enumerate(NOTES[i].strip().splitlines()):
            fields=row.split('|');year,name,detail=fields[:3]
            event=dict(id=f'e{i}-{number}',lane=f'l{i}',year=int(year),group=f'g{i}',label=f'{year} · {name}',detail=detail,
                       size=12.7,detail_size=11.3,text_layout='paragraph',offset=lanes[f'l{i}'][1]*.40,width=170)
            if len(fields)>3:
                event.update(icon=fields[3],art_position='auto',art_width=88,art_height=70,placement_priority=1)
                ratios={'illustration-cuneiform-tablet':.5984,'illustration-suspension-bridge':273/168,'illustration-clock-escapement':.7727,
                        'illustration-stagecoach':359/149,'illustration-square-rigged-ship':213/208,'illustration-sextant-1904':1.043,
                        'illustration-astrolabe-observation':1.452,'illustration-telescope-observer':.6983}
                event['art_height']=round(88/ratios.get(fields[3],1),2)
            d['events'].append(event)
    return d


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',required=True)
    parser.add_argument('--periods-only',action='store_true')
    parser.add_argument('--diagnose',action='store_true')
    args=parser.parse_args();folder=ART/args.label;folder.mkdir(parents=True,exist_ok=False)
    data=brief();(folder/'draft.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    if args.diagnose:
        lanes=lane_geometry(data['lanes'],data['width']);scale=lambda year:190+(year-400)/1600*(data['height']-302)
        obstacles=obstacles_for(data,scale,lanes);results=[]
        for event in data['events']:
            x,pitch=lanes[event['lane']]
            candidates=event_candidates(event,x,pitch,scale(event['year']),data['height'],obstacles,[],190,2.5,data['events'],scale)
            results.append(dict(id=event['id'],year=event['year'],candidates=len(candidates)))
        (folder/'diagnosis.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(scope='Individual note feasibility, without previously placed notes; not a complete poster.',failures=[row for row in results if not row['candidates']])));return
    if args.periods_only:data['events']=[]
    else:
        data,placement=pack_events(data,max_width=190)
        (folder/'placement.json').write_text(json.dumps(placement,indent=2)+'\n',encoding='utf-8')
    svg,layout=EditorialPoster(data).render()
    for name,content in [('source.json',json.dumps(data,indent=2)+'\n'),('poster.svg',svg),('poster.html',viewer(svg,data['title'])),('layout.json',json.dumps(layout,indent=2)+'\n')]:
        (folder/name).write_text(content,encoding='utf-8')
    subprocess.run(['uv','run','--script',str(SKILL/'scripts/audit_chart.py'),str(folder/'poster.svg'),'--source',str(folder/'source.json'),
                    '--report',str(folder/'browser.json'),'--png',str(folder/'poster.png')],check=True)
    print(json.dumps(dict(folder=str(folder),periods=len(data['periods']),transitions=len(data['transitions']),events=len(data['events']),diagnostic=args.periods_only)))


if __name__ == '__main__':
    main()
