#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Individually authored fictional institutional histories and their page placement.

Years and relationships are explicit story records, never inferred from coordinates.
Multiple parents denote the merger described in the record, not biological ancestry.
The diagram is schematic: a vertical distance does not encode elapsed time.
"""

import json
from pathlib import Path


# id | name | year | x,y,width | treatment | predecessors | historical note | emblem
# A predecessor prefixed with ~ is influence, not institutional descent.
ORIGINS = """
oral|Seasonal calendars|860|888,166,81|plain||Oral tradition|
craft|Artisan knowledge|940|764,223,90|plain|oral|Workshops and guilds|
record|Written reckonings|962|1038,238,98|plain|oral|Tables and chronicles|
instruments|Measures and instruments|1018|748,311,101|plain|craft||
tables|Calendar tables|1041|1010,326,88|plain|record||
natural|Schools of natural study|1082|880,404,146|pill|instruments,tables|Shared methods|
chroniclers|Court chroniclers|1096|1116,419,80|plain|record|No institutional successors|
inquiry|THE HOUSE OF INQUIRY|1134|875,507,201|hero|natural|Teachers, makers and observers|book
archive|The common archive|1161|875,592,142|plain|inquiry|A shared scholarly record|
"""

MECHANICS = """
makers|GUILD OF INSTRUMENT MAKERS|1193|289,694,208|hero|archive|A charter for independent workshops|wheel
brass|Brassworkers of Lorn|1228|132,828,112|card|makers|Balances and measures|
water|Water-engine fraternity|1246|336,805,126|plain|makers|Mills and pumps|
glass|Corven glass furnaces|1281|516,850,100|plain|makers|An independent craft|
scales|Public assay office|1267|100,941,88|plain|brass|Municipal standards|
dials|Alder dial-makers|1275|222,925,106|emblem|brass|Portable instruments|astrolabe
millwrights|Fellowship of millwrights|1308|345,914,102|card|water||
pumps|Mine-drainage company|1322|445,991,102|plain|water|Closed after the floods|
clear-glass|Clear-glass workshop|1314|539,1055,90|card|glass|Optical blanks|
balance|College of Weights|1340|106,1066,106|card|scales|Public teaching begins|
clockmakers|Brotherhood of Clockmakers|1351|264,1049,149|hero|dials|The escapement dispute|gear
hydraulic|School of Hydraulic Arts|1386|399,1137,124|card|millwrights|A teaching successor|
glass-union|Union of Glassworkers|1392|503,1220,106|plain|clear-glass|Furnaces join a common guild|
testing|Bureau of Testing|1420|98,1160,89|plain|balance||
standards|Lorn Standards Office|1446|185,1255,97|card|balance|Civic charter renewed|
pendulum|The Pendulum Circle|1427|370,1225,106|plain|clockmakers|An informal research society|
horology|Royal College of Horology|1458|301,1323,149|emblem|clockmakers|Teaching and instrument repair|crown
canals|Canal engineers|1462|435,1310,92|plain|hydraulic|Regional survey teams|
pump-school|Alder Pump School|1498|531,1400,95|plain|hydraulic|Disbanded in 1531|
mechanical|ACADEMY OF MECHANICAL ARTS|1544|272,1462,202|hero|horology,canals|The colleges unite|gear
metrology|National Metrology Bureau|1571|108,1404,114|card|testing,standards|Two civic offices combined|
engines|Institute of Engines|1610|326,1572,133|card|mechanical|A separate technical college|
precision|Precision Instrument Society|1628|525,1558,120|plain|mechanical,~meridian|Makers and observers collaborate|
engines-west|Western Engine Works|1691|338,1683,115|plain|engines|Transferred to the city in 1730|
rail|College of Rail Engineering|1786|429,1772,119|card|engines-west|New transport faculty|
machine|Machine Research Bureau|1842|523,1869,111|card|rail|A public laboratory|
calibration|Central Calibration Service|1904|110,1521,112|emblem|metrology|National measurement standards|wheel
"""

ASTRONOMY = """
sky|COLLEGE OF THE NIGHT SKY|1187|880,724,198|hero|archive|The first observatory charter|star
calendar|Office of the Calendar|1216|669,848,119|card|sky|A civic appointment|
meridian|Meridian Observatory|1239|880,848,159|emblem|sky|Daily positional records|observatory
watchers|The Hill Watchers|1257|1095,842,98|plain|sky|A lay observing circle|
almanac|Almanac printers|1294|615,962,87|plain|calendar|Commercial tables|
equinox|Equinox Commission|1310|745,1007,105|card|calendar|An intermittent public body|
sunroom|The Sun Room|1288|884,950,88|plain|meridian|Transit observations|
summit|Summit Station|1336|1032,973,93|plain|watchers|Mountain observations|
nightbooks|Night-book society|1362|1130,1065,101|plain|watchers|Records end in 1403|
newcalendar|Institute of Calendar Reform|1384|690,1125,155|emblem|equinox,almanac|The two traditions reconcile|sun
transits|Transit Table Office|1411|877,1110,104|card|sunroom|A permanent observing service|
star-census|The Star Census|1435|1044,1147,104|plain|summit|A shared catalogue|
southern|Southern Observatory|1470|1172,1222,106|card|summit|A new latitude station|
ephemerides|Bureau of Ephemerides|1489|621,1243,112|card|newcalendar|Published prediction tables|
computers|The Human Computers|1517|744,1314,101|plain|newcalendar|Independent calculation teams|
observatories|THE UNITED OBSERVATORIES|1552|935,1292,199|hero|transits,star-census|The transit offices merge|observatory
reformers|Calendar reformers of Mere|1586|651,1413,112|plain|ephemerides|A short-lived dissenting school|
longitude|Longitude Prize Board|1594|1101,1402,126|card|observatories,~pilotage|Navigation problem, public reward|
meridian-net|The Meridian Network|1618|884,1437,125|pill|observatories|Coordinated measurements|
north-station|North Cape Station|1641|720,1542,98|plain|meridian-net||
valley|Valley Observatory|1656|857,1552,113|card|meridian-net|A local foundation|
island-station|Island Transit House|1682|1009,1545,107|plain|meridian-net||
southern-survey|Southern Sky Survey|1713|1179,1517,110|plain|southern,~longitude|Reuses the southern station|
variable|Variable-star observers|1729|706,1680,100|plain|north-station|A correspondence network|
public-sky|Public Observatory of Lorn|1765|894,1670,171|emblem|valley|The university opens its instruments|orbit
comet|Comet correspondence|1774|1068,1666,108|plain|island-station|A voluntary network|
southern-tables|Southern Tables Office|1809|1180,1768,105|card|southern-survey|A national catalogue|
photometry|Photometry Section|1837|729,1818,99|card|variable,~silver-image|New methods of measurement|
instruments-lab|Observatory instrument shop|1851|900,1801,123|plain|public-sky,~precision|Makers return to the observatory|
stellar|Stellar Physics Society|1879|1054,1861,115|card|comet,~spectrum|A change in research program|
astronomical|ASTRONOMICAL UNION|1908|820,1951,189|hero|photometry,public-sky|Observatories and observers unite|star
radial|Radial-velocity programme|1919|1043,1998,118|plain|stellar|A specialist working group|
southern-union|Southern Astronomical Council|1933|1191,2085,118|plain|southern-tables|Regional observatories cooperate|
radio-sky|Radio Sky Station|1947|727,2107,109|card|astronomical|An independent receiver array|
night-archive|Night-sky archive|1956|900,2133,103|plain|astronomical|Preserves the earlier ledgers|
space-science|Institute of Space Science|1964|751,2251,155|emblem|radio-sky|Space-borne instruments|orbit
stellar-centre|Centre for Stellar Physics|1969|1041,2244,125|card|radial|A permanent institute|
sky-data|Open Sky Data Service|1983|898,2360,124|plain|night-archive,stellar-centre|Catalogues are combined|
southern-array|Southern Telescope Array|1988|1158,2410,126|card|southern-union|Three sites, one programme|
orbital|Orbital Observatory Consortium|1997|738,2503,148|card|space-science|Continuing international cooperation|
open-sky|Open Sky Commons|2012|1009,2503,161|hero|sky-data,southern-array|A shared public observing archive|star
"""

NAVIGATION = """
seafarers|FELLOWSHIP OF SEAFARERS|1224|1454,730,207|hero|archive|A charter shared by coastal guilds|ship
pilots|Lorn harbour pilots|1261|1310,858,113|card|seafarers|A municipal licence|
open-sea|Open-sea masters|1286|1520,852,101|plain|seafarers|Independent navigators|
boatmen|River boatmen of Mere|1307|1681,918,92|plain|seafarers|An inland tradition|
port-school|The Port School|1338|1240,1003,105|card|pilots|Apprentices begin formal study|
tide|Tide recorders|1319|1368,957,98|plain|pilots||
pilotage|COLLEGE OF PILOTAGE|1371|1535,1017,160|emblem|open-sea|The masters establish a school|compass
river-law|River Navigation Board|1389|1689,1088,93|plain|boatmen|Civic regulation|
charts|Chamber of Sea Charts|1417|1286,1128,125|card|port-school,~transits|Charts and astronomical tables|
coast-watch|Coast-watch stations|1436|1426,1169,101|plain|tide|A chain of local stations|
ocean|Oceanic Academy|1463|1557,1200,148|emblem|pilotage|A public teaching foundation|ship
river-merger|Inland Navigation Service|1502|1685,1287,106|card|river-law|A regional public service|
soundings|The Soundings Office|1521|1325,1296,114|plain|charts|Hydrographic records|
beacons|Lighthouse Commissioners|1534|1445,1370,109|card|coast-watch|Beacons become a public duty|
pilot-union|Union of Licensed Pilots|1583|1634,1447,162|hero|ocean,river-merger|Coastal and inland licences converge|anchor
ocean-voyage|Ocean-voyage School|1608|1513,1566,111|plain|ocean|Closed after the port fire|
channel|Channel Pilot Service|1657|1654,1592,110|card|pilot-union|A specialist service|
beacon-college|College of Beacon Engineering|1684|1445,1654,125|plain|beacons,~precision|Lenses and signalling equipment|
harbour-board|Lorn Harbour Board|1728|1653,1727,109|plain|channel|Municipal reorganisation|
seamanship|National School of Seamanship|1761|1545,1814,162|emblem|pilot-union|Civil and naval instruction|ship
lifeboat|Voluntary Lifeboat Society|1792|1696,1882,91|plain|harbour-board|An independent rescue service|
signals|Maritime Signals Office|1826|1437,1889,101|card|beacon-college|Standard signals adopted|
merchant|Merchant Marine College|1858|1555,2001,121|card|seamanship|Civil instruction separates|
naval|Naval Navigation School|1865|1691,2027,90|plain|seamanship|Military instruction separates|
radio-sea|Marine Radio Service|1902|1416,2062,115|card|signals|A new communication network|
port-lab|Port Safety Laboratory|1921|1550,2126,115|plain|merchant,~machine|Research on navigation hazards|
rescue|Sea Rescue Federation|1934|1691,2171,101|card|lifeboat,~radio-sea|Volunteer stations federate|
maritime|MARITIME INSTITUTE|1951|1513,2257,173|hero|port-lab,radio-sea|Research and communications unite|anchor
hydro-school|Naval Hydrography School|1968|1685,2355,110|plain|naval,~hydrography|A specialist successor|
sea-college|College of Marine Systems|1986|1423,2436,119|card|maritime|Teaching becomes autonomous|
ocean-safety|Ocean Safety Authority|2001|1568,2513,139|emblem|maritime,rescue|A unified rescue and safety service|ship
naval-survey|Naval Survey Unit|2009|1704,2511,78|plain|hydro-school||
"""

OPTICS = """
lenses|The Lens Grinders|1405|139,1635,125|pill|glass-union|A distinct trade|
light|COLLEGE OF LIGHT|1491|168,1763,179|hero|lenses|An independent school of optical craft|lens
mirror|Mirror makers of Tarn|1548|100,1885,94|plain|light|Workshop tradition|
refraction|Circle of Refraction|1577|263,1883,118|card|light|An experimental society|
telescope|Long-tube workshop|1612|411,1959,110|plain|light,~observatories|Optical instruments for observers|
glassworks|Tarn Glassworks|1626|110,2010,111|card|mirror|Commercial production|
camera|Camera-obscura school|1641|224,2010,103|plain|refraction|A teaching circle|
spectrum|The Spectrum Society|1679|364,2092,159|emblem|refraction|Light studied as a physical problem|prism
opticians|Guild of Practical Opticians|1706|540,2060,130|card|telescope|An instrument trade|
glass-research|Glass Research House|1750|110,2131,108|plain|glassworks|Materials research|
silver-image|Silver-image experimenters|1793|234,2194,108|plain|camera|A voluntary correspondence group|
wave|Wave Theory Seminar|1822|355,2207,110|plain|spectrum|A university circle|
instrument-firm|Fenn Optical Instruments|1836|535,2172,129|card|opticians|A commercial successor|
photographic|Photographic Society|1854|149,2296,170|emblem|silver-image,glass-research|Experimenters and manufacturers unite|lens
optical-physics|Institute of Optical Physics|1888|370,2325,177|hero|wave|A permanent research institute|prism
medical-lenses|Medical lens makers|1896|555,2287,99|plain|instrument-firm|Specialist production|
cinema|Moving-image Circle|1906|100,2417,94|plain|photographic|An independent association|
color|Colour Laboratory|1923|211,2425,106|card|photographic,~optical-physics|Materials and perception|
laser|Coherent Light Laboratory|1959|374,2431,122|card|optical-physics|A new experimental programme|
microscopy|Centre for Microscopy|1964|543,2418,125|card|medical-lenses|Biomedical imaging|
moving-image|Institute of Moving Images|1978|125,2525,138|card|cinema,color|Teaching and colour research merge|
photonics|Photonics Research Council|1993|332,2525,143|emblem|laser|A research partnership|prism
imaging|Imaging Sciences Institute|2004|548,2530,152|hero|microscopy,color|A multidisciplinary institute|lens
"""

CARTOGRAPHY = """
surveyors|FELLOWSHIP OF SURVEYORS|1566|1352,1499,179|hero|soundings|The chart office gains a land-survey branch|globe
fieldbooks|Field-book exchange|1604|1266,1604,102|plain|surveyors|A professional correspondence|
triangulation|Triangulation Office|1643|1361,1741,119|card|surveyors,~meridian-net|A state surveying service|
atlas-room|The Atlas Room|1676|1250,1863,114|emblem|fieldbooks|Collectors become publishers|book
land-register|Land Registry Survey|1709|1350,1981,98|plain|triangulation|Cadastral administration|
hydrography|Hydrographic Bureau|1732|1297,2168,134|card|triangulation,~charts|Marine charts separate from land records|
geography|GEOGRAPHICAL SOCIETY|1775|1237,2290,190|hero|atlas-room|Public lectures and expeditions|globe
mapping|National Mapping Service|1829|1290,2413,112|card|land-register|Centralised public cartography|
earth-data|Earth Information Office|1972|1256,2534,129|card|mapping,geography,~hydrography|Maps become a shared data service|
"""


def build_lineage(base):
    labels = ['Astronomy', 'Navigation', 'Mechanics', 'Optics', 'Cartography', 'Common origins']
    data = base('atlas-of-inquiry', 'AN ATLAS OF SHARED INQUIRY', 'lineage', labels)
    data['groups'][-1]['color'] = '#A6A18B'
    data.update(pattern_id='usefulcharts-branching-lineage',
        subtitle='Individually authored fictional histories of institutions, unions and research traditions',
        reading_note='Solid paths: descent or stated merger. Dotted arrows: influence. Positions are schematic. Dates: founding or reorganisation. Map assignments are fictional.')
    for group, records in [('g5', ORIGINS), ('g2', MECHANICS), ('g0', ASTRONOMY), ('g1', NAVIGATION), ('g3', OPTICS), ('g4', CARTOGRAPHY)]:
        for line in records.strip().splitlines():
            nid, label, year, position, style, parents, note, icon = line.split('|')
            x, y, width = map(int, position.split(','))
            emphasis = style == 'hero'
            node = dict(id=nid, label=label, founded=int(year), group=group, x=x, y=y, width=width,
                style=style, size=15 if emphasis else 11.5 if style=='emblem' else 10.5,
                detail_size=9 if emphasis else 8.2,
                detail=year + (' · '+note if note else ''))
            if icon:
                node.update(icon=icon, icon_width=37 if emphasis else 29)
            data['nodes'].append(node)
            for source in filter(None, parents.split(',')):
                influence=source.startswith('~'); source=source.lstrip('~')
                data['edges'].append(dict(id=f'{source}-to-{nid}', source=source, target=nid,
                    kind='influence' if influence else 'branch', weight=1.5 if influence else 2.5))
    records={n['id']:n for n in data['nodes']}
    for edge in data['edges']:
        assert edge['source'] in records, edge
        assert records[edge['source']]['founded'] < records[edge['target']]['founded'], edge
    corridors={'clockmakers-to-pendulum':1180,'horology-to-mechanical':1388,'canals-to-mechanical':1388}
    for edge in data['edges']:
        if edge['id'] in corridors:edge['corridor_y']=corridors[edge['id']]
        if edge['id']=='glass-union-to-lenses':
            edge['via']=[[503,1357.24],[436,1357.24],[436,1608],[139,1608]]
    records['observatories'].update(icon='illustration-astrolabe-observation',icon_width=70,width=238)
    records['pilotage'].update(icon='illustration-sextant-1904',icon_width=53,width=185)
    records['public-sky'].update(icon='illustration-telescope-observer',icon_width=59,width=204)
    data['source_note']='Original synthetic history · All institutions, dates and relationships are invented. Source illustrations: Pearson Scott Foresman and Nordisk familjebok; provenance embedded.'
    # Insets explain this particular source. The map explicitly repeats its key.
    data['insets'] = [dict(kind='isotype', title='Institutions represented in this study', box=[78,178,398,409],groups=[f'g{i}' for i in range(5)]),
        dict(kind='map', title='Illustrative regional traditions', box=[1248,178,460,396],
             countries={}, legend=True, note='Fictional assignments · Outlines: Natural Earth')]
    continents={'Europe':'g4','Asia':'g0','Africa':'g3','North America':'g2','South America':'g1','Oceania':'g1'}
    countries=json.loads((Path(__file__).resolve().parents[2]/'maps/world-countries.json').read_text(encoding='utf-8'))['countries']
    data['insets'][1]['countries']={c['id']:continents[c['continent']] for c in countries if c['continent'] in continents}
    for nid, label, width, dy in [('makers','MECHANICAL ARTS',180,-76),('sky','ASTRONOMICAL TRADITIONS',209,-78),
        ('seafarers','SEAFARING SCHOOLS',185,-74),('light','THE OPTICAL TRADITION',180,-81),
        ('surveyors','LAND AND SEA SURVEYS',185,-79)]:
        data['annotations'].append(dict(node=nid,dy=dy,width=width,label=label,kind='pill',group=records[nid]['group'],size=12))
    return data
