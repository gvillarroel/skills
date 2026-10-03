#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Integrate an illustrated field guide into all six schematic historical branches."""
import json
import sys
import xml.etree.ElementTree as ET
from artwork import ROOT,REPO,tag,art,save,render

sys.path.insert(0,str(REPO/'projects/star-trek-canonical-timeline/scripts'))
import build_poster as p
import build_dense_poster as dense

def main():
    out=ROOT/'artifacts/revision-2/civilizations';p.OUT=out/'native'
    for name in ['svgs','reviews','viewer','documents','images']:(p.OUT/name).mkdir(parents=True,exist_ok=True)
    p.DARK='#142B3D';arts=[];artroot=ET.Element(tag('svg'))
    species={
      'st-001':(0,'HUMAN','Federation','Follow Earth into the Federation.'),
      'st-origin-05':(1,'VULCAN','Vulcan','Follow the paths to Romulus and Ni’Var.'),
      'st-origin-06':(2,'KLINGON','Klingon','Trace war, diplomacy and diaspora.'),
      'st-076':(3,'CARDASSIAN','Cardassian','Watch an alliance form, then fracture.'),
      'st-056':(4,'BORG','Borg','Find the two distinct stories in 2401.'),
      'st-051':(5,'FERENGI','Ferengi','Follow contact and political change.'),
    }
    shipbase=REPO/'projects/star-trek-starships/artifacts/images/space-edition'
    ships={
       'st-002':('enterprise-nx.png','ENTERPRISE NX-01','Federation','Exploration brings contact, cooperation and conflict.'),
       'st-024':('discovery.png','DISCOVERY','Federation','The ship leaves its century after the Control crisis.'),
       'st-070':('voyager.png','VOYAGER','Borg','Follow one crew through many different societies.'),
       'st-103':('voyager.png','HOME THROUGH A TRANSWARP HUB','Borg','Compare this return with the separate 2401 Borg stories.'),
    }
    original=p.event
    def event(e,x,y,w,actor=None,compact=False):
        item=species.get(e['id']) or ships.get(e['id'])
        if item:
            cell,label,group,hook=item;is_species=e['id'] in species
            height=242;ix=x+19;iy=y+5
            p.rect(ix,iy,w-22,height,'#08121F',rx=14)
            if is_species:
                asset=ROOT/'artifacts/images/species-sheet.png';crop=((cell%3)*512,(cell//3)*512,512,512)
            else:asset=shipbase/cell;crop=None
            box=(ix+6,iy+15,200,height-30)
            a=art(artroot,asset,box,'civilization-'+e['id'],[e['id']],[group],('Illustrative representative: ' if is_species else 'Reference-guided ship illustration: ')+label,crop)
            arts.append(a);p.parts.append(ET.tostring(artroot[-1],encoding='unicode'))
            tx=ix+215;tw=w-257
            yy=p.paragraph('FIELD GUIDE' if is_species else 'FOLLOW THE SHIP',tx,iy+34,tw,15,'bold',fill='#A5D1E4')
            yy=p.paragraph(label,tx,yy+14,tw,25,'display',fill='#F8D381')
            yy=p.paragraph(hook,tx,yy+13,tw,17,fill='#EFF4F5')
            p.paragraph('Illustrative person; not a dated portrait.' if is_species else 'Illustration; dimensions are not to scale.',tx,yy+14,tw,14,fill='#B9C9D1')
            y+=height+18
        return original(e,x,y,w,actor,compact)
    p.event=event;dense.main()
    original_svg=(p.OUT/'svgs/star-trek-timeline.svg').read_text(encoding='utf-8')
    root=ET.fromstring(original_svg);root.append(artroot.find(tag('defs')))
    save(root,out,arts,p.DATA)
    layout=json.loads((p.OUT/'reviews/layout.json').read_text());(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    # Replace the native viewer's inline poster while retaining full source inspection.
    viewer=(p.OUT/'viewer/index.html').read_text(encoding='utf-8')
    viewer=viewer.replace(original_svg,(out/'poster.svg').read_text(encoding='utf-8')).replace('#paper svg{','#paper > svg{').replace('../svgs/star-trek-timeline.svg','poster.svg').replace('../documents/star-trek-timeline.pdf','poster.pdf')
    (out/'poster.html').write_text(viewer,encoding='utf-8')
    render(out,(55,740,1430,1050))
if __name__=='__main__':main()
