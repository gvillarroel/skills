#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Reclaim completed early and future lanes for recognizable ship comparisons."""
import json
import xml.etree.ElementTree as ET
from artwork import ROOT,REPO,tag,rect,txt,art,save,render

def main():
    base=REPO/'projects/star-trek-starships/artifacts/flow-edition';out=ROOT/'artifacts/revision-2/starships'
    original_svg=(base/'svgs/star-trek-starships.svg').read_text(encoding='utf-8');root=ET.fromstring(original_svg)
    source=json.loads((REPO/'projects/star-trek-starships/data/ships.json').read_text(encoding='utf-8'))
    layout=json.loads((base/'reviews/layout.json').read_text());packed=json.loads((base/'reviews/shared-row-layout.json').read_text())['layout']
    shipbase=REPO/'projects/star-trek-starships/artifacts/images/space-edition';refs=shipbase.parent/'reference';arts=[]
    # These are exact empty pockets after the early branches and future fleet end.
    start_new=len(root)
    pockets=[dict(x=75,y=3145,w=1070,h=1910),dict(x=5550,y=2210,w=750,h=2630)]
    def intersects(a,b):return a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']
    for pocket in pockets:
        assert not any(intersects(pocket,b) for b in packed['pieces']),pocket
        rect(root,**pocket,fill='#081520',stroke='#345261',rx=30)
    txt(root,110,3102,'READ THE SILHOUETTE',44,'#F7D38B','700')
    txt(root,110,3142,'Picture gallery in released lanes • image positions are not dates',22,'#B8CBD6')
    left=[
      ('enterprise-nx.png','enterprise-nx','enterprise',110,3190,'ENTERPRISE NX-01','Compact twin-nacelle profile','Follow its 2151 launch and early missions.'),
      ('enterprise-original.jpg','enterprise-1701','enterprise',630,3190,'ENTERPRISE NCC-1701','Saucer, neck and secondary hull','A later ship inherits the name.'),
      ('defiant.png','defiant-first','escorts',110,3690,'DEFIANT','A compact, integrated hull','Compare the two physical Defiant hulls.'),
      ('klingon-bird.png','bounty','klingon',630,3690,'KLINGON BIRD-OF-PREY','Wings and a forward command pod','Follow Bounty and Rotarran separately.'),
    ]
    for file,anchor,group,x,y,title,shape,hook in left:
        path=refs/file if file.endswith('.jpg') else shipbase/file
        crop=(0,295,1600,665) if file.endswith('.jpg') else None
        arts.append(art(root,path,(x,y,445,300),'ship-guide-'+anchor,[anchor],[group],title+' — '+shape,crop))
        txt(root,x,y+342,title,27,'#F7D38B','700');txt(root,x,y+378,shape,22)
        txt(root,x,y+415,hook,20,'#B8CBD6')
    txt(root,110,4304,'SAME NAME ≠ SAME HULL',35,'#F7D38B','700')
    for j,line in enumerate(['Name succession links a sequence of ships.','A refit or renaming can belong to one physical ship.','Read the relation label before following its arrow.','The original dates, gaps and qualified notes stay in the plot.']):txt(root,110,4352+j*39,line,25)
    txt(root,110,4570,'A SMALL EXPLORATION CHALLENGE',27,'#8BD8E8','700')
    for j,line in enumerate(['Find a ship with a known launch year.','Find one whose construction year remains unknown.','Trace an observed interval, then find an observation with no duration.']):txt(root,110,4620+j*41,line,23)
    txt(root,110,4805,'Illustrated ship types are examples, not a scale comparison.',22,'#B8CBD6')
    txt(root,110,4840,'Classic Enterprise: reference photograph. Other examples: reference-guided art.',19,'#B8CBD6')
    txt(root,5590,2270,'THREE EXPLORATION PROFILES',34,'#F7D38B','700')
    txt(root,5590,2311,'Field guide • follow the named records in the plot',23,'#B8CBD6')
    right=[('discovery.png','discovery','classic-fleet',2370,'DISCOVERY','A circular primary hull and long nacelles.','Follow its departure and future observations.'),
      ('voyager.png','voyager','voyager-line',3070,'VOYAGER','An elongated saucer and swept-back nacelles.','Find the interval ending with its return in 2378.'),
      ('protostar.png','protostar','new-generation',3770,'PROTOSTAR','A small, sharply tapered exploration ship.','Follow its own history and the later Prodigy.')]
    for file,anchor,group,y,title,shape,hook in right:
        arts.append(art(root,shipbase/file,(5590,y,665,395),'ship-guide-'+anchor,[anchor],[group],title+' — '+shape))
        txt(root,5590,y+445,title,34,'#F7D38B','700');txt(root,5590,y+492,shape,24)
        txt(root,5590,y+535,hook,23,'#B8CBD6')
    txt(root,5590,4658,'The small ships at trail ends remain in the timeline.',22,'#B8CBD6')
    txt(root,5590,4695,'Large views reveal shape without moving a year marker.',22,'#B8CBD6')
    txt(root,5590,4760,'Illustrations are not to scale. See the record sources.',20,'#B8CBD6')
    for e in list(root)[start_new:]:
        if e.tag in [tag('text'),tag('svg')] and float(e.get('x','6400'))<1200:e.set('y',str(float(e.get('y'))+100))
    for a in arts:
        if a['box']['x']<1200:a['box']['y']+=100
    # Retain the twelve original trail-end images and register their lineage anchors.
    for item in layout['illustrations']:
        path=shipbase/{'enterprise-nx':'enterprise-nx.png','discovery':'discovery.png','defiant-first':'defiant.png','voyager':'voyager.png','protostar':'protostar.png','bounty':'klingon-bird.png'}[item['id']]
        arts.append(dict(placement_id='trail-'+item['ship'],asset_id=path.stem,path=str(path),anchors=[item['ship']],groups=[next(b['group'] for b in packed['boxes'] if b['id']==item['ship'])],explanation='Small ship illustration at the existing observed trail end',box={k:item[k] for k in ['x','y','w','h']},recognized_at_placed_size=False))
    save(root,out,arts,source);layout['reclaimed_art_pockets']=pockets;(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    original=ET.fromstring(original_svg)
    marks=lambda r:[dict(e.attrib) for e in r.iter() if e.get('data-year') or e.get('data-kind')]
    assert marks(root)==marks(original)
    viewer=(base/'viewer/index.html').read_text(encoding='utf-8').replace(original_svg,(out/'poster.svg').read_text(encoding='utf-8'))
    viewer=viewer.replace('#paper svg{','#paper > svg{').replace('../svgs/star-trek-starships.svg','poster.svg').replace('../documents/star-trek-starships.pdf','poster.pdf')
    (out/'poster.html').write_text(viewer,encoding='utf-8');render(out,(70,3035,1090,1900))
if __name__=='__main__':main()
