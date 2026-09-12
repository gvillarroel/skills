#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Authored fictional chronology: unequal political branches and distinct events."""


def build_timeline(base):
    labels=['Riverlands','Highlands','Coastlands','Islands','Northlands']
    d=base('five-regional-histories','FIVE REGIONS THROUGH TIME','timeline',labels)
    for key in ('nodes','edges','unions','insets'):d.pop(key)
    d.update(pattern_id='usefulcharts-parallel-history',subtitle='Divisions, unions, and changing societies in five fictional regions, 1000–2000',frame_color='#665D48',height=2400,
        time=dict(start=1000,end=2000,step=25),lanes=[dict(id=f'l{i}',label=v) for i,v in enumerate(labels)],periods=[],transitions=[],events=[],map_texture='milner-1850',
        eras=[dict(start=a,end=b,label=label) for a,b,label in [(1000,1200,'Early city states'),(1200,1450,'Maritime kingdoms'),(1450,1650,'Age of exchange'),(1650,1850,'Federations'),(1850,2000,'Modern age')]],
        source_note='Synthetic history · All periods, events and relationships are invented. Contextual art: Pearson Scott Foresman, Library of Congress and Nordisk familjebok; provenance embedded.',
        reading_note='One year scale. Bridges: succession, division or union; dots: uncertain continuity. Width is compositional. Objects illustrate subjects, not these fictional events. Decorative map: Milner, 1850.')
    # id, name, first year, last year, lane-relative x, width. The differing
    # number of simultaneous polities is part of the source, not a decoration.
    records=[[
        ('reed','Reed city states',1000,1190,18,25),('willow','Willow principalities',1000,1260,247,30),
        ('delta','Delta kingdom',1200,1380,24,63),('canal','Canal duchies',1280,1380,237,33),
        ('river','Kingdom of the Rivers',1400,1580,92,98),
        ('east','Eastern march',1600,1730,225,33),('west','Western estates',1600,1720,18,30),('court','Saffron court',1600,1740,122,39),
        ('lower','Lower river league',1750,1850,18,55),('upper','Upper river union',1760,1860,222,62),
        ('civic','River commonwealth',1870,2000,93,99)],
      [
        ('clans','Mountain clans',1000,1210,37,28),('pass','Pass confederacy',1220,1370,91,83),
        ('ridge','Ridge kingdom',1390,1550,12,38),('cairn','Cairn councils',1390,1610,140,24),('stone','Stone duchy',1390,1540,271,25),
        ('silver','Silver crown',1560,1770,12,75),('east','Eastern canton',1560,1760,234,61),
        ('union','Highland union',1790,1900,112,72),('charter','Charter era',1910,2000,80,109)],
      [
        ('coral','Coral ports',1000,1280,16,27),('amber','Amber towns',1000,1150,260,26),('pearl','Pearl league',1170,1390,216,59),
        ('harbor','Harbor republic',1300,1390,16,59),('maritime','Maritime empire',1410,1630,74,143),
        ('north','Northern coast',1650,1780,13,31),('free','Free ports',1650,1810,139,31),('south','Southern coast',1650,1790,268,27),
        ('amber2','Amber federation',1800,1900,14,66),('coral2','Coral union',1830,1920,116,64),('pearl2','Pearl republic',1810,1910,248,52),
        ('coast','Coastal union',1940,2000,62,178)],
      [
        ('palm','Palm settlements',1000,1250,98,26),('reef','Reef chiefdoms',1270,1450,15,32),('cove','Cove league',1270,1450,262,30),
        ('voyage','Voyaging alliance',1470,1680,93,86),('lagoon','Lagoon kingdom',1700,1840,16,65),('isles','Outer isles',1700,1880,251,36),
        ('assembly','Island assembly',1900,2000,104,91)],
      [
        ('forest','Forest peoples',1000,1220,15,25),('lake','Lake towns',1000,1220,273,23),('birch','Birch federation',1240,1460,100,85),
        ('taiga','Taiga estates',1480,1610,12,28),('fir','Fir councils',1480,1670,139,24),('glacial','Glacial march',1480,1640,264,33),
        ('western','Western kingdom',1630,1810,12,61),('northern','Northern league',1690,1810,132,41),('frontier','Frontier duchy',1660,1810,258,41),
        ('congress','Northern congress',1830,1910,96,105),('civic','Civic era',1930,2000,78,139)]]
    # Preserve each stream's center but reclaim excessive colored area for the
    # adjacent narrative. Ribbon width is an explicit compositional property.
    records=[[(key,label,a,b,x+(w-min(w,78))/2,min(w,78)) for key,label,a,b,x,w in rows] for rows in records]
    links=[[
        ('reed','delta','succession'),('willow','canal','succession'),('delta','river','union'),('canal','river','union'),
        ('river','west','division'),('river','court','division'),('river','east','division'),
        ('west','lower','succession'),('court','upper','union'),('east','upper','union'),('lower','civic','union'),('upper','civic','union')],
      [('clans','pass','succession'),('pass','ridge','division'),('pass','cairn','division'),('pass','stone','division'),
       ('ridge','silver','succession'),('stone','east','succession'),('cairn','union','uncertain'),('silver','union','union'),('east','union','union'),('union','charter','succession')],
      [('amber','pearl','succession'),('coral','harbor','succession'),('harbor','maritime','union'),('pearl','maritime','union'),
       ('maritime','north','division'),('maritime','free','division'),('maritime','south','division'),
       ('north','amber2','succession'),('free','coral2','succession'),('south','pearl2','succession'),('amber2','coast','union'),('coral2','coast','union'),('pearl2','coast','union')],
      [('palm','reef','division'),('palm','cove','division'),('reef','voyage','union'),('cove','voyage','union'),
       ('voyage','lagoon','division'),('voyage','isles','division'),('lagoon','assembly','union'),('isles','assembly','union')],
      [('forest','birch','union'),('lake','birch','union'),('birch','taiga','division'),('birch','fir','division'),('birch','glacial','division'),
       ('taiga','western','succession'),('fir','northern','succession'),('glacial','frontier','succession'),
       ('western','congress','union'),('northern','congress','union'),('frontier','congress','union'),('congress','civic','succession')]]
    events=[[
        (1025,'The first embankments','Villages pool labor to contain the spring floods.'),
        (1112,'A canal survey','Surveyors record the river slope on fired clay.'),
        (1226,'The Saffron market','A permanent grain exchange links delta towns.'),
        (1325,'Water courts','Judges set common rules for irrigation disputes.'),
        (1431,'One river toll','The new crown abolishes internal customs barriers.'),
        (1504,'A regional granary','Emergency stores protect towns after crop failure.'),
        (1618,'Three rival courts','A disputed inheritance separates the kingdom.'),
        (1692,'Canal locks','Canal boats reach the upper valley.'),
        (1768,'The towpath accord','Two leagues share a continuous transport route.'),
        (1830,'Steam on the rivers','Scheduled packets link inland manufacturing towns.'),
        (1892,'An elected council','Districts send delegates to a common assembly.'),
        (1951,'The basin authority','A joint agency coordinates reservoirs and power.')],
      [
        (1015,'Salt over the passes','Pack routes connect isolated upland communities.'),
        (1104,'The Cairn archive','Monasteries preserve land grants and family records.'),
        (1242,'A common road levy','Pass councils fund bridges and mountain shelters.'),
        (1316,'The summit hospice','Travelers gain a refuge on the winter route.'),
        (1413,'Three jurisdictions','Ridge, Cairn, and Stone issue separate charters.'),
        (1505,'Silver workings','Deep mines transform the ridge settlements.'),
        (1582,'The mint ordinance','A new coin standard unites the western markets.'),
        (1650,'The clockmakers','Small workshops specialize in precision escapements.'),
        (1732,'A winter post','Relay stations maintain a year-round mail service.'),
        (1816,'The union compact','Cantons retain local courts under a shared council.'),
        (1880,'The summit railway','An engineered pass opens to freight traffic.'),
        (1940,'The civic charter','Universal local representation replaces estate seats.')],
      [
        (1034,'Harbor soundings','Pilots publish the first list of safe anchorages.'),
        (1131,'Seasonal convoys','Merchants coordinate voyages through the straits.'),
        (1210,'The pilots\' guild','Experienced crews certify new harbor navigators.'),
        (1330,'The sea register','Ships carry standardized papers across the coast.'),
        (1434,'The maritime court','A single tribunal hears disputes between ports.'),
        (1516,'An ocean atlas','Chartmakers compare observations from distant voyages.'),
        (1573,'Pearl observatory','New tables guide offshore voyages.'),
        (1674,'Independent ports','Three administrations inherit the imperial docks.'),
        (1741,'Offshore survey','Crews chart the outer banks.'),
        (1840,'Ocean steam routes','Regular services replace seasonal sail crossings.'),
        (1900,'Dockworkers organize','Port unions negotiate shared working conditions.'),
        (1955,'The coastal compact','Member ports adopt a joint commercial code.')],
      [
        (1030,'Reading the swells','Navigators teach the routes between inhabited reefs.'),
        (1117,'The reef calendar','Seasonal gatherings follow tides and migrating birds.'),
        (1201,'Deep-water canoes','Longer hulls carry families beyond the inner islands.'),
        (1307,'Two island leagues','Chiefs divide responsibility for the western sea roads.'),
        (1382,'The shell exchange','Ceremonial gifts sustain relations across the archipelago.'),
        (1497,'A voyaging compact','Crews receive sanctuary in every allied harbor.'),
        (1565,'Schools of navigation','Experienced navigators formalize route instruction.'),
        (1630,'The island chronicle','Scribes collect oral accounts of early migrations.'),
        (1723,'The lagoon court','A royal council governs the populous inner islands.'),
        (1793,'Outer-island assemblies','Local councils negotiate their own trading agreements.'),
        (1912,'An archipelago assembly','Delegates agree a shared public revenue system.'),
        (1960,'The inter-island service','Regular ferries connect hospitals and schools.')],
      [
        (1020,'Markets on the ice','Winter roads connect forest settlements and lake towns.'),
        (1102,'The birch record','Traders keep account marks on thin bark sheets.'),
        (1263,'The northern compact','Lake and forest councils create a mutual-defense union.'),
        (1350,'A navigable frontier','Canals connect two major lake systems.'),
        (1430,'The survey lodges','Teams record boundaries before new farms are granted.'),
        (1512,'Three regional estates','Fir councils and frontier lords gain separate powers.'),
        (1600,'A winter observatory','Long observations improve the northern calendar.'),
        (1703,'The timber code','New limits protect forests close to navigable rivers.'),
        (1765,'The postal corridor','Relay stations link widely scattered northern towns.'),
        (1850,'A continental congress','Representatives agree common border and trade rules.'),
        (1900,'Electrifying the lakes','Hydroelectric schemes supply the industrial towns.'),
        (1950,'The public university','Regional colleges unite under a common charter.')]]
    # An object is used once, where its subject supports the fictional event.
    # Its real identity and date remain in the SVG's embedded provenance.
    art={(0,1):'illustration-cuneiform-tablet',(2,6):'illustration-astrolabe-observation',
         (2,8):'illustration-sextant-1904',(4,6):'illustration-telescope-observer'}
    landmarks={(0,4),(1,2),(1,7),(2,4),(3,4),(3,5),(4,2),(4,9)}
    major_periods={(0,'river'),(1,'silver'),(2,'maritime'),(3,'voyage'),(4,'birch')}
    for g,rows in enumerate(records):
        lookup={r[0]:r for r in rows}
        for key,label,a,b,x,w in rows:
            size=20 if (g,key) in major_periods else 10.5 if w<45 else 13 if w<90 else 16
            d['periods'].append(dict(id=f'p{g}-{key}',label=label,start=a,end=b,lane=f'l{g}',group=f'g{g}',offset=x,bar_width=w,size=size))
        for source,target,kind in links[g]:
            a,b=lookup[source],lookup[target]
            siblings=sorted([t for s,t,k in links[g] if s==source],key=lambda t:lookup[t][4])
            parents=sorted([s for s,t,k in links[g] if t==target],key=lambda s:lookup[s][4])
            sp=(siblings.index(target)+1)/(len(siblings)+1);tp=(parents.index(source)+1)/(len(parents)+1)
            d['transitions'].append(dict(id=f't{g}-{source}-{target}',source=f'p{g}-{source}',target=f'p{g}-{target}',kind=kind,
                style='dotted' if kind=='uncertain' else 'ribbon',source_port=sp,target_port=tp,ribbon_width=10 if kind in ('division','union') else 0))
        for i,(year,label,detail) in enumerate(events[g]):
            # Find the widest quiet interval through the complete event height,
            # including its optional artwork, rather than assigning two tracks.
            image_id=art.get((g,i));height=150 if image_id else 84
            stop=year+height/((d['height']-302)/1000)
            occupied=sorted((x-8,x+w+8) for _,_,a,b,x,w in rows if a<stop and b>year)
            merged=[]
            for a,b in occupied:
                if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
                else:merged.append((a,b))
            gaps=[];cursor=3
            for a,b in merged:
                if a>cursor:gaps.append((cursor,a))
                cursor=max(cursor,b)
            if cursor<318:gaps.append((cursor,318))
            left,right=max(gaps,key=lambda p:p[1]-p[0])
            width=min(148,right-left);x=(left+right-width)/2
            e=dict(id=f'event-{g}-{i}',lane=f'l{g}',year=year,label=f'{year} · {label}',detail=detail,offset=x,width=width,size=10.6,detail_size=9.5,group=f'g{g}')
            if (g,i) in landmarks:e.update(size=13.2,detail_size=10.2)
            if (g,i)==(2,10):e.update(label='1900 · Dock unions',detail='Workers agree common pay and work hours.',offset=1,width=62)
            if (g,i)==(0,9):e.update(offset=87,width=130)
            if (g,i)==(0,7):e.update(offset=168,width=52)
            if image_id and width>=65:e.update(icon=image_id,art_size=min(120 if image_id.startswith('illustration-') else 70,width))
            if (g,i)==(2,8):e['art_size']=65
            if (g,i)==(2,6):e.update(art_width=108,art_height=74.38)
            if (g,i)==(0,1):e.update(art_width=62,art_height=103.61)
            if (g,i)==(4,6):e.update(art_width=64,art_height=91.65)
            d['events'].append(e)
    # Reserve note space before reducing type. Two Highland periods move left
    # to leave a continuous corridor for the uncertain Cairn succession.
    for period in d['periods']:
        old=period['bar_width'];width=max(20,min(50,old*.58))
        major=period['size']==20
        if major:width=50
        period.update(offset=period['offset']+(old-width)/2,bar_width=width,
            size=18 if major else 12 if old>=55 else 11)
        if period['id'] in ('p1-cairn','p1-union'):period['offset']-=50
    illustrations={
        'event-2-6':('illustration-astrolabe-observation',95,65.43),
        'event-1-7':('illustration-clock-escapement',67,86.71),
        'event-3-6':('illustration-sextant-1904',65,62.32),
    }
    for event in d['events']:
        if event['id'] in illustrations:
            event['icon'],event['art_width'],event['art_height']=illustrations[event['id']]
        landmark=event['size']>12
        event.update(size=14.5 if landmark else 12.2,detail_size=11 if landmark else 10.7)
    d['source_note']='Synthetic history · All periods, events and relationships are invented. Contextual art: PSF, Library of Congress, Nordisk familjebok and The New Student\'s Reference Work; provenance embedded.'
    from pack_timeline_events import pack_events
    d,_=pack_events(d)
    # Allocate more room to concurrent coastal histories and retain generous
    # names while narrowing the page. Only selected quiet continuities use stems.
    from timeline_geometry import lane_geometry
    d['width']=1680
    for lane,weight in zip(d['lanes'],[1.02,1.04,1.12,.78,1.04]):lane['weight']=weight
    lanes=lane_geometry(d['lanes'],d['width']);stems=set()
    for period in d['periods']:
        period['offset']=(period['offset']+period['bar_width']/2)/325*lanes[period['lane']][1]-period['bar_width']/2
        if period['size']<18 and (period['end']-period['start']>=175 or period['id'] in ('p0-lower','p0-upper')):
            period.update(treatment='stem',stem_width=5);stems.add(period['id'])
        if period['size']==18:
            period['offset']+=(period['bar_width']-42)/2;period['bar_width']=42
    for edge in d['transitions']:
        if edge['source'] in stems:edge['source_port']=.5
        if edge['target'] in stems:edge['target_port']=.5
    for event in d['events']:event['offset']=event['offset']/325*lanes[event['lane']][1]
    d['reading_note']='One year scale. Thin stems and full bands show exact durations; wider stem labels name periods. Bridges show succession, division or union; dots show uncertainty. Width is compositional. Contextual objects and map do not depict these fictional regions.'
    d,_=pack_events(d)
    return d
