#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Use verified empty pockets for a Mars spacecraft field guide, preserving calendar geometry."""
import json
import xml.etree.ElementTree as ET
from artwork import ROOT,REPO,tag,rect,txt,art,save,render

def main():
    base=REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/mars';out=ROOT/'artifacts/revision-2/mars'
    root=ET.fromstring((base/'poster.svg').read_text(encoding='utf-8'));source=json.loads((base/'source.json').read_text());layout=json.loads((base/'layout.json').read_text())
    for e in list(root):
        if e.get('data-context-pocket') or (e.tag==tag('text') and 1635<=float(e.get('x','0'))<2370 and 285<=float(e.get('y','0'))<=856):root.remove(e)
    arts=[];sheet=ROOT/'artifacts/images/mars-sheet.png'
    rect(root,1600,280,810,700,'#0B1B2A','#496071',18)
    txt(root,1624,318,'EXPLORE THE HARDWARE',30,'#F8D381','700')
    txt(root,1624,348,'Field guide • picture positions do not encode dates',18,'#BBCBD1')
    examples=[(0,1630,374,'MARINER 9','mariner9','An orbiter maps the planet'),(1,2020,374,'VIKING IN CRUISE','viking1','Orbiter + protected lander'),(2,1630,667,'VIKING ON THE GROUND','viking2','A separate vehicle explores the surface'),(3,2020,667,'MARS PATHFINDER','pathfinder','Petals open after the airbag landing')]
    for cell,x,y,label,anchor,caption in examples:
        arts.append(art(root,sheet,(x,y,350,225),'mars-'+str(cell),[anchor],['us'],label+' — '+caption,crop=((cell%2)*627,(cell//2)*627,627,627)))
        if cell==0:
            # The generated sheet's neighboring antenna enters the nominal cell.
            # A specimen-shaped SVG viewport keeps the complete Mariner wingtip.
            definitions=root.find(tag('defs'));clip=ET.SubElement(definitions,tag('clipPath'),dict(id='mariner-specimen',clipPathUnits='userSpaceOnUse'))
            ET.SubElement(clip,tag('path'),dict(d='M0 0H610V370H627V627H0Z'))
            root[-1].find(tag('use')).set('clip-path','url(#mariner-specimen)')
        txt(root,x,y+245,label,21,'#7AD7EE','700');txt(root,x,y+273,caption,17,'#BBCBD1')
    # Reuse the vacant early-calendar lower area; all dates remain in the original tracks.
    rect(root,96,1340,825,485,'#0B1B2A','#496071',18)
    txt(root,122,1380,'SAME DESTINATION, DIFFERENT MACHINES',27,'#FFA893','700')
    arts.append(art(root,ROOT/'artifacts/references/soviet-43.jpg',(122,1410,425,265),'mars-soviet-museum',['mars2','mars3'],['ussr'],'Mars 2/3 spacecraft model photographed in a museum; NASA history reference'))
    txt(root,575,1453,'MARS 2 / MARS 3',24,'#FFA893','700')
    for j,line in enumerate(['USSR • launched 1971','Both carried a lander.','Mars 2 crashed; Mars 3','landed, then fell silent.','Follow their records →']):txt(root,575,1490+j*31,line,19,'#BBCBD1')
    counts={g['id']:sum(n['group']==g['id'] for n in source['nodes']) for g in source['groups']}
    txt(root,122,1732,f'32 campaigns: {counts["us"]} USA · {counts["ussr"]} USSR · 1 Russia · 1 Japan',21,'#F8D381','700')
    txt(root,122,1770,'Count launches, not individual payloads.',21)
    txt(root,122,1806,'Museum photograph: NASA history · model, not a flight scene',16,'#BBCBD1')
    rect(root,2485,295,650,515,'#0B1B2A','#496071',18)
    arts.append(art(root,ROOT/'artifacts/references/nozomi-39.jpg',(2510,350,340,280),'mars-nozomi',['nozomi'],['japan'],'ISAS/JAXA artist concept of Nozomi; the spacecraft failed to enter Mars orbit'))
    txt(root,2510,333,'FIND THE MISSION THAT NEVER ENTERED ORBIT',21,'#F8D381','700')
    txt(root,2510,670,'NOZOMI · JAPAN · LAUNCHED 1998',25,'#F8D381','700')
    for j,line in enumerate(['The pictured orbiter did not enter Mars orbit in 2003.','An artist concept shows the intended spacecraft,','not a successful arrival. Look for its final-loss cross.']):txt(root,2510,711+j*27,line,19,'#BBCBD1')
    # Two source-grounded comparison cards fill otherwise idle row space.
    rect(root,1635,1000,750,105,'#193341',None,14)
    txt(root,1655,1031,'NO NEW LAUNCHES IN THIS INVENTORY: 1976–1987',21,'#F8D381','700')
    txt(root,1655,1062,'Viking hardware launched in 1975 kept working during part of the gap.',18)
    rect(root,3550,1385,625,500,'#193341',None,18)
    txt(root,3575,1425,'HOW MANY VEHICLES?',30,'#D7BCFA','700')
    arts.append(art(root,ROOT/'artifacts/references/mars96-dlr.jpg',(3575,1440,575,180),'mars96-dlr',['mars96'],['russia'],'Mars 96 orbiter model by DLR Institute of Planetary Exploration; launch failed',crop=(0,345,1000,325)))
    txt(root,3575,1644,'MARS 96 · DLR COMPUTER MODEL',18,'#D7BCFA','700')
    for j,line in enumerate(['Two Viking campaigns carried four vehicles.','The orbiter and lander bars end in different years.','Mars 96 planned five probes in one campaign:', 'one orbiter, two landers, two penetrators.','Its launch failed before deployment at Mars.']):txt(root,3575,1679+j*29,line,20)
    txt(root,3575,1850,'Trace the component bars; do not add extra launches.',18,'#BBCBD1')
    save(root,out,arts,source);(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    # Calendar and record marks are copied byte-for-byte as XML attributes.
    original=ET.parse(base/'poster.svg').getroot()
    marks=lambda r:[dict(e.attrib) for e in r.iter() if e.get('data-date-owner') or e.get('data-span-owner')]
    assert marks(root)==marks(original)
    assert [e.get('data-record-id') for e in root.iter() if e.get('data-record-id')]==[n['id'] for n in layout['layout']['boxes']]
    render(out,(1560,270,1600,820))
if __name__=='__main__':main()
