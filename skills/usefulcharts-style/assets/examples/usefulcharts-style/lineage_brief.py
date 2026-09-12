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
oral|Seasonal calendars|860|799.2,175.6,81|plain||Oral tradition|
craft|Artisan knowledge|940|687.6,212.5,90|plain|oral|Workshops and guilds|
record|Written reckonings|962|934.2,226.0,98|plain|oral|Tables and chronicles|
instruments|Measures and instruments|1018|673.2,291.70000000000005,101|plain|craft||
tables|Calendar tables|1041|909.0,305.20000000000005,88|plain|record||
natural|Schools of natural study|1082|792.0,375.40000000000003,146|pill|instruments,tables|Shared methods|
chroniclers|Court chroniclers|1096|1004.4,388.90000000000003,80|plain|record|No institutional successors|
inquiry|THE HOUSE OF INQUIRY|1134|787.5,468.1,201|hero|natural|Teachers, makers and observers|book
archive|The common archive|1161|787.5,544.6,142|plain|inquiry|A shared scholarly record|
"""

MECHANICS = """
makers|GUILD OF INSTRUMENT MAKERS|1193|371,670,208|hero|archive|A charter for independent workshops|wheel
brass|Brassworkers of Lorn|1228|227,779,112|card|makers|Balances and measures|
water|Water-engine fraternity|1246|370,779,126|plain|makers|Mills and pumps|
glass|Corven glass furnaces|1281|507,779,100|plain|makers|An independent craft|
scales|Public assay office|1267|121,878,88|plain|brass|Municipal standards|
dials|Alder dial-makers|1275|242,874,106|emblem|brass|Portable instruments|astrolabe
millwrights|Fellowship of millwrights|1308|370,866,102|card|water||
pumps|Mine-drainage company|1322|432,949,102|plain|water|Closed after the floods|
clear-glass|Clear-glass workshop|1314|552,873,90|card|glass|Optical blanks|
balance|College of Weights|1340|130,977,106|card|scales|Public teaching begins|
clockmakers|Brotherhood of Clockmakers|1351|282,984,149|hero|dials|The escapement dispute|gear
hydraulic|School of Hydraulic Arts|1386|443,1038,124|card|millwrights|A teaching successor|
glass-union|Union of Glassworkers|1392|582,972,106|plain|clear-glass|Furnaces join a common guild|
testing|Bureau of Testing|1420|130,1064,89|plain|balance||
standards|Lorn Standards Office|1446|134,1147,97|card|balance|Civic charter renewed|
pendulum|The Pendulum Circle|1427|282,1098,106|plain|clockmakers|An informal research society|
horology|Royal College of Horology|1458|184,1237,149|emblem|clockmakers|Teaching and instrument repair|crown
canals|Canal engineers|1462|329,1192,92|plain|hydraulic|Regional survey teams|
pump-school|Alder Pump School|1498|447,1132,95|plain|hydraulic|Disbanded in 1531|
mechanical|ACADEMY OF MECHANICAL ARTS|1544|187,1347,202|hero|horology,canals|The colleges unite|gear
metrology|National Metrology Bureau|1571|134,1451,114|card|testing,standards|Two civic offices combined|
engines|Institute of Engines|1610|282,1479,133|card|mechanical|A separate technical college|
precision|Precision Instrument Society|1628|289,1562,120|plain|mechanical,~meridian|Makers and observers collaborate|
engines-west|Western Engine Works|1691|147,1572,115|plain|engines|Transferred to the city in 1730|
rail|College of Rail Engineering|1786|273,1671,119|card|engines-west|New transport faculty|
machine|Machine Research Bureau|1842|229,1771,111|card|rail|A public laboratory|
calibration|Central Calibration Service|1904|133,1674,112|emblem|metrology|National measurement standards|wheel
"""

ASTRONOMY = """
sky|COLLEGE OF THE NIGHT SKY|1187|831,672,198|hero|archive|The first observatory charter|star
calendar|Office of the Calendar|1216|666,772,119|card|sky|A civic appointment|
meridian|Meridian Observatory|1239|830,773,159|emblem|sky|Daily positional records|observatory
watchers|The Hill Watchers|1257|1023,777,98|plain|sky|A lay observing circle|
almanac|Almanac printers|1294|665,866,87|plain|calendar|Commercial tables|
equinox|Equinox Commission|1310|786,871,105|card|calendar|An intermittent public body|
sunroom|The Sun Room|1288|907,867,88|plain|meridian|Transit observations|
summit|Summit Station|1336|1022,875,93|plain|watchers|Mountain observations|
nightbooks|Night-book society|1362|1027,958,101|plain|watchers|Records end in 1403|
newcalendar|Institute of Calendar Reform|1384|738,971,155|emblem|equinox,almanac|The two traditions reconcile|sun
transits|Transit Table Office|1411|897,965,104|card|sunroom|A permanent observing service|
star-census|The Star Census|1435|897,1048,104|plain|summit|A shared catalogue|
southern|Southern Observatory|1470|1026,1042,106|card|summit|A new latitude station|
ephemerides|Bureau of Ephemerides|1489|607,1071,112|card|newcalendar|Published prediction tables|
computers|The Human Computers|1517|738,1071,101|plain|newcalendar|Independent calculation teams|
observatories|THE UNITED OBSERVATORIES|1552|932,1158,199|hero|transits,star-census|The transit offices merge|observatory
reformers|Calendar reformers of Mere|1586|725,1175,112|plain|ephemerides|A short-lived dissenting school|
longitude|Longitude Prize Board|1594|997,1280,126|card|observatories,~pilotage|Navigation problem, public reward|
meridian-net|The Meridian Network|1618|847,1274,125|pill|observatories|Coordinated measurements|
north-station|North Cape Station|1641|887,1363,98|plain|meridian-net||
valley|Valley Observatory|1656|878,1441,113|card|meridian-net|A local foundation|
island-station|Island Transit House|1682|760,1361,107|plain|meridian-net||
southern-survey|Southern Sky Survey|1713|1015,1379,110|plain|southern,~longitude|Reuses the southern station|
variable|Variable-star observers|1729|1055,1579,100|plain|north-station|A correspondence network|
public-sky|Public Observatory of Lorn|1765|879,1625,171|emblem|valley|The university opens its instruments|orbit
comet|Comet correspondence|1774|875,1525,108|plain|island-station|A voluntary network|
southern-tables|Southern Tables Office|1809|700,1665,105|card|southern-survey|A national catalogue|
photometry|Photometry Section|1837|995,1730,99|card|variable,~silver-image|New methods of measurement|
instruments-lab|Observatory instrument shop|1851|859,1740,123|plain|public-sky,~precision|Makers return to the observatory|
stellar|Stellar Physics Society|1879|715,1754,115|card|comet,~spectrum|A change in research program|
astronomical|ASTRONOMICAL UNION|1908|894,1835,189|hero|photometry,public-sky|Observatories and observers unite|star
radial|Radial-velocity programme|1919|716,1853,118|plain|stellar|A specialist working group|
southern-union|Southern Astronomical Council|1933|704,1948,118|plain|southern-tables|Regional observatories cooperate|
radio-sky|Radio Sky Station|1947|970,1939,109|card|astronomical|An independent receiver array|
night-archive|Night-sky archive|1956|839,1942,103|plain|astronomical|Preserves the earlier ledgers|
space-science|Institute of Space Science|1964|947,2033,155|emblem|radio-sky|Space-borne instruments|orbit
stellar-centre|Centre for Stellar Physics|1969|554,2041,125|card|radial|A permanent institute|
sky-data|Open Sky Data Service|1983|554,2135,124|plain|night-archive,stellar-centre|Catalogues are combined|
southern-array|Southern Telescope Array|1988|704,2053,126|card|southern-union|Three sites, one programme|
orbital|Orbital Observatory Consortium|1997|947,2133,148|card|space-science|Continuing international cooperation|
open-sky|Open Sky Commons|2012|703,2235,161|hero|sky-data,southern-array|A shared public observing archive|star
"""

NAVIGATION = """
seafarers|FELLOWSHIP OF SEAFARERS|1224|1331,668,207|hero|archive|A charter shared by coastal guilds|ship
pilots|Lorn harbour pilots|1261|1160,771,113|card|seafarers|A municipal licence|
open-sea|Open-sea masters|1286|1330,776,101|plain|seafarers|Independent navigators|
boatmen|River boatmen of Mere|1307|1494,771,92|plain|seafarers|An inland tradition|
port-school|The Port School|1338|1160,864,105|card|pilots|Apprentices begin formal study|
tide|Tide recorders|1319|1156,934,98|plain|pilots||
pilotage|COLLEGE OF PILOTAGE|1371|1330,888,160|emblem|open-sea|The masters establish a school|compass
river-law|River Navigation Board|1389|1494,871,93|plain|boatmen|Civic regulation|
charts|Chamber of Sea Charts|1417|1292,990,125|card|port-school,~transits|Charts and astronomical tables|
coast-watch|Coast-watch stations|1436|1154,1020,101|plain|tide|A chain of local stations|
ocean|Oceanic Academy|1463|1339,1080,148|emblem|pilotage|A public teaching foundation|ship
river-merger|Inland Navigation Service|1502|1490,990,106|card|river-law|A regional public service|
soundings|The Soundings Office|1521|1184,1109,114|plain|charts|Hydrographic records|
beacons|Lighthouse Commissioners|1534|1358,1170,109|card|coast-watch|Beacons become a public duty|
pilot-union|Union of Licensed Pilots|1583|1462,1280,162|hero|ocean,river-merger|Coastal and inland licences converge|anchor
ocean-voyage|Ocean-voyage School|1608|1301,1365,111|plain|ocean|Closed after the port fire|
channel|Channel Pilot Service|1657|1488,1395,110|card|pilot-union|A specialist service|
beacon-college|College of Beacon Engineering|1684|1338,1459,125|plain|beacons,~precision|Lenses and signalling equipment|
harbour-board|Lorn Harbour Board|1728|1488,1494,109|plain|channel|Municipal reorganisation|
seamanship|National School of Seamanship|1761|1462,1584,162|emblem|pilot-union|Civil and naval instruction|ship
lifeboat|Voluntary Lifeboat Society|1792|1492,1680,91|plain|harbour-board|An independent rescue service|
signals|Maritime Signals Office|1826|1306,1579,101|card|beacon-college|Standard signals adopted|
merchant|Merchant Marine College|1858|1361,1685,121|card|seamanship|Civil instruction separates|
naval|Naval Navigation School|1865|1488,1792,90|plain|seamanship|Military instruction separates|
radio-sea|Marine Radio Service|1902|1361,1779,115|card|signals|A new communication network|
port-lab|Port Safety Laboratory|1921|1221,1851,115|plain|merchant,~machine|Research on navigation hazards|
rescue|Sea Rescue Federation|1934|1368,1873,101|card|lifeboat,~radio-sea|Volunteer stations federate|
maritime|MARITIME INSTITUTE|1951|1322,1968,173|hero|port-lab,radio-sea|Research and communications unite|anchor
hydro-school|Naval Hydrography School|1968|1488,1968,110|plain|naval,~hydrography|A specialist successor|
sea-college|College of Marine Systems|1986|1214,2073,119|card|maritime|Teaching becomes autonomous|
ocean-safety|Ocean Safety Authority|2001|1368,2074,139|emblem|maritime,rescue|A unified rescue and safety service|ship
naval-survey|Naval Survey Unit|2009|1501,2070,78|plain|hydro-school||
"""

OPTICS = """
lenses|The Lens Grinders|1405|582,1154,125|pill|glass-union|A distinct trade|
light|COLLEGE OF LIGHT|1491|489,1295,179|hero|lenses|An independent school of optical craft|lens
mirror|Mirror makers of Tarn|1548|359,1401,94|plain|light|Workshop tradition|
refraction|Circle of Refraction|1577|489,1401,118|card|light|An experimental society|
telescope|Long-tube workshop|1612|627,1406,110|plain|light,~observatories|Optical instruments for observers|
glassworks|Tarn Glassworks|1626|429,1489,111|card|mirror|Commercial production|
camera|Camera-obscura school|1641|561,1495,103|plain|refraction|A teaching circle|
spectrum|The Spectrum Society|1679|717,1496,159|emblem|refraction|Light studied as a physical problem|prism
opticians|Guild of Practical Opticians|1706|627,1581,130|card|telescope|An instrument trade|
glass-research|Glass Research House|1750|427,1577,108|plain|glassworks|Materials research|
silver-image|Silver-image experimenters|1793|433,1666,108|plain|camera|A voluntary correspondence group|
wave|Wave Theory Seminar|1822|566,1665,110|plain|spectrum|A university circle|
instrument-firm|Fenn Optical Instruments|1836|568,1755,129|card|opticians|A commercial successor|
photographic|Photographic Society|1854|394,1771,170|emblem|silver-image,glass-research|Experimenters and manufacturers unite|lens
optical-physics|Institute of Optical Physics|1888|420,1867,177|hero|wave|A permanent research institute|prism
medical-lenses|Medical lens makers|1896|583,1849,99|plain|instrument-firm|Specialist production|
cinema|Moving-image Circle|1906|130,1876,94|plain|photographic|An independent association|
color|Colour Laboratory|1923|254,1876,106|card|photographic,~optical-physics|Materials and perception|
laser|Coherent Light Laboratory|1959|405,1972,122|card|optical-physics|A new experimental programme|
microscopy|Centre for Microscopy|1964|553,1957,125|card|medical-lenses|Biomedical imaging|
moving-image|Institute of Moving Images|1978|157,1980,138|card|cinema,color|Teaching and colour research merge|
photonics|Photonics Research Council|1993|395,2072,143|emblem|laser|A research partnership|prism
imaging|Imaging Sciences Institute|2004|223,2084,152|hero|microscopy,color|A multidisciplinary institute|lens
"""

CARTOGRAPHY = """
surveyors|FELLOWSHIP OF SURVEYORS|1566|1182,1254,179|hero|soundings|The chart office gains a land-survey branch|globe
fieldbooks|Field-book exchange|1604|1145,1375,102|plain|surveyors|A professional correspondence|
triangulation|Triangulation Office|1643|1191,1464,119|card|surveyors,~meridian-net|A state surveying service|
atlas-room|The Atlas Room|1676|1040,1482,114|emblem|fieldbooks|Collectors become publishers|book
land-register|Land Registry Survey|1709|1182,1563,98|plain|triangulation|Cadastral administration|
hydrography|Hydrographic Bureau|1732|1209,1667,134|card|triangulation,~charts|Marine charts separate from land records|
geography|GEOGRAPHICAL SOCIETY|1775|1164,1756,190|hero|atlas-room|Public lectures and expeditions|globe
mapping|National Mapping Service|1829|1083,1851,112|card|land-register|Centralised public cartography|
earth-data|Earth Information Office|1972|1146,1978,129|card|mapping,geography,~hydrography|Maps become a shared data service|
"""


def build_lineage(base):
    labels = ['Astronomy', 'Navigation', 'Mechanics', 'Optics', 'Cartography', 'Common origins']
    data = base('atlas-of-inquiry', 'AN ATLAS OF SHARED INQUIRY', 'lineage', labels)
    data['groups'][-1]['color'] = '#A6A18B'
    data.update(width=1620,height=2430,pattern_id='usefulcharts-branching-lineage',
        subtitle='Individually authored fictional histories of institutions, unions and research traditions',
        reading_note='Solid paths: descent or stated merger. Dotted arrows: influence. Positions are schematic. Dates: founding or reorganisation. Map assignments are fictional.')
    for group, records in [('g5', ORIGINS), ('g2', MECHANICS), ('g0', ASTRONOMY), ('g1', NAVIGATION), ('g3', OPTICS), ('g4', CARTOGRAPHY)]:
        for line in records.strip().splitlines():
            nid, label, year, position, style, parents, note, icon = line.split('|')
            x, y, width = map(float, position.split(','))
            width=int(width)
            emphasis = style == 'hero'
            node = dict(id=nid, label=label, founded=int(year), group=group, x=x, y=y, width=width,
                style=style, size=15 if emphasis else 11.5 if style=='emblem' else 10.5,
                detail_size=9 if emphasis else 8.2,
                detail_position='outside',date_label=year,detail=note)
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
    records['observatories'].update(icon='illustration-astrolabe-observation',icon_width=70,width=238)
    records['pilotage'].update(icon='illustration-sextant-1904',icon_width=53,width=185)
    records['public-sky'].update(icon='illustration-telescope-observer',icon_width=59,width=204)
    records['mechanical'].update(icon='illustration-cogwheel-psf',icon_width=43)
    records['seafarers'].update(icon='illustration-compass-card-psf',icon_width=43)
    records['surveyors'].update(icon='illustration-theodolite-psf',icon_width=58,width=194)
    records['atlas-room'].update(icon='illustration-printing-press-bookman',icon_width=42,width=133)
    data['source_note']='Original synthetic history · All institutions, dates and relationships are invented. Source illustrations: Pearson Scott Foresman, Nordisk familjebok and American Type Founders; provenance embedded.'
    # Insets explain this particular source. The map explicitly repeats its key.
    data['insets'] = [dict(kind='isotype', title='Institutions represented in this study', box=[70.2,172,358.2,368.1],groups=[f'g{i}' for i in range(5)]),
        dict(kind='map', title='Illustrative regional traditions', box=[1123.2,172,414,356.4],
             countries={}, legend=True, note='Fictional assignments · Outlines: Natural Earth')]
    continents={'Europe':'g4','Asia':'g0','Africa':'g3','North America':'g2','South America':'g1','Oceania':'g1'}
    countries=json.loads((Path(__file__).resolve().parents[2]/'maps/world-countries.json').read_text(encoding='utf-8'))['countries']
    data['insets'][1]['countries']={c['id']:continents[c['continent']] for c in countries if c['continent'] in continents}
    for nid, label, width, dy in [('makers','MECHANICAL ARTS',180,-76),('sky','ASTRONOMICAL TRADITIONS',209,-78),
        ('seafarers','SEAFARING SCHOOLS',185,-74),('light','THE OPTICAL TRADITION',180,-81),
        ('surveyors','LAND AND SEA SURVEYS',185,-79)]:
        data['annotations'].append(dict(node=nid,dy=dy,width=width,label=label,kind='pill',group=records[nid]['group'],size=12))
    # The complete reviewed routes are acceptance geometry, not inferred history.
    corridors=json.loads((Path(__file__).with_name('lineage-corridors.json')).read_text(encoding='utf-8'))
    assert set(corridors)=={edge['id'] for edge in data['edges']}
    for edge in data['edges']:edge.update(corridors[edge['id']])
    return data
